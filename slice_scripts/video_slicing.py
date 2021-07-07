"""
reads file names and annotations from excel sheet.
reads each file, each class and annotations, cuts the video into clips in mp4 using ffmpeg_extract_subclip,
and outputs to corresponding class folder
"""
import os
import xlrd
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Start with
DIR_PATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\Annotations'
FILENAME = r'SIM R01 Annotation Table_local_copy_downloaded_feb_19_2021.xlsx'
FILEPATH = os.path.join(DIR_PATH, FILENAME)
VIDPATH = r'C:\Users\Carla Pugh\Box\Pugh Lab Shared Drive\4. Data Base\ACS-October2019\ACS 2019 Aligned Videos'
OUTPUTPATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing'
PIDS_PATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\pids_seen_so_far.txt'

def get_sec(time_str):
    """Get Seconds from time. COPIED FROM STACK OVERFLOW"""
    if time_str == 'nc':
        return -1
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)


def get_video_path(path):
    participant_vids_dict = {}
    for entry in os.listdir(path):
        if not entry.endswith('.mkv') or 'Camera1' not in entry:  # only looking at Camera 1 for now
            continue
        # getting the pid and casting to lower and assigning the path to the pid
        participant_vids_dict[entry[:4].lower()] = os.path.join(path, entry)
    return participant_vids_dict


def read_excel_sheet(path):
    print('reading excel sheet...')
    wrkbk = xlrd.open_workbook(path)
    return wrkbk


def extract_time_points(workbook, justone=True):
    print('extracting time points...')
    black_list = ['p120 - i']
    timepoints = {}

    for sheet_num in range(len(workbook.sheets())):
        # creating a nice data structure for each pid
        sheet = workbook.sheet_by_index(sheet_num)
        pid = sheet.name[:4].lower()

        # avoiding overview and template sheets and black listed participants
        if not pid.startswith('p') or sheet.name in black_list:
            continue

        # suture; capture values in column that corresponds to the suture start time in annotations workbook
        suture_start_times = sheet.col_values(21)[2:]
        suture_end_times = sheet.col_values(23)[2:]
        suture_time_points = [(suture_start_times[i], suture_end_times[i]) for i in range(len(suture_end_times))]

        # hand ties; as above
        hand_tie_start_times = sheet.col_values(24)[2:]
        hand_tie_end_times = sheet.col_values(25)[2:]
        handtie_time_points = [(hand_tie_start_times[i], hand_tie_end_times[i]) for i in range(len(hand_tie_end_times))]

        # threadcut; as above
        threadcut_start_times = sheet.col_values(28)[2:]
        threadcut_end_times = sheet.col_values(29)[2:]
        threadcut_time_points = [(threadcut_start_times[i], threadcut_end_times[i]) for i in range(len(threadcut_end_times))]

        timepoints[pid] = {
            'suture_throws': suture_time_points,
            'hand_ties': handtie_time_points,
            'thread_cuts': threadcut_time_points
        }
        if justone:
            break

    return timepoints


def _run_slice_save(timepts, pid, video_dict, action_type='suture_throw'):
    # find the right folder to write to
    relevant_path = os.path.join(OUTPUTPATH, action_type)
    # see if folder exists, if not create it
    if not os.path.exists(relevant_path):
        os.mkdir(relevant_path)

    # iterate through the duration that mark where the action is performed
    subclip_cnt = 0
    for time_period in timepts:
        # get the ACS video
        input_path = video_dict.get(pid)
        # if the input path does not exist for reason, ignore and continue
        if input_path is None:
            continue
        # get start and stop seconds for each duration
        start, stop = time_period[0], time_period[1]
        if start == '' or stop == '':
            continue
        # cut and save
        start_seconds = get_sec(start)
        stop_seconds = get_sec(stop)
        if stop_seconds == -1 or start_seconds == -1:
            print('incompatible start or stop time; start: {}, stop: {}'.format(start_seconds, stop_seconds))
            continue
        print('saving')
        camera = input_path.split('.')[2]
        file_name = '{}_{}_{}_{}.mkv'.format(pid, action_type, camera, subclip_cnt)
        output_path = os.path.join(relevant_path, file_name)
        ffmpeg_extract_subclip(input_path, start_seconds, stop_seconds, targetname=output_path)
        subclip_cnt += 1


def slice_and_save(timepoints_dict, video_dict):
    print('slicing')
    # reads the saved list of pids that have already been sliced
    with open(PIDS_PATH, 'r') as ropen:
        pids_already_seen = ropen.read().splitlines()  # opens, reads and splits pids into an array
    number_of_pids_already_seen = len(pids_already_seen)
    number_of_pids_processed = 0
    total_participants = len(timepoints_dict)
    for participant_id, timepts in timepoints_dict.items():
        print('working on participant number: {}'.format(participant_id))
        print('--------------------------------------------------------------')
        # if participant has already been processed, continue
        if participant_id in pids_already_seen:
            print('pid is already processed')
            continue
        # suture throw
        suturethrow_tp = timepts["suture_throws"]
        _run_slice_save(suturethrow_tp, participant_id, video_dict)
        knottie_tp = timepts["hand_ties"]
        _run_slice_save(knottie_tp, participant_id, video_dict, action_type='knot_ties')
        threadcut_tps = timepts["thread_cuts"]
        _run_slice_save(threadcut_tps, participant_id, video_dict, action_type='thread_cut')
        # write to file
        number_of_pids_processed += 1
        # open and write to disk
        with open(PIDS_PATH, 'w') as wopen:
            wopen.write('\n')
            wopen.write(participant_id)

        # Printing Stats
        print('total number of participants: {}'.format(total_participants))
        print('number of participants already processed before running this script: {}'.format(number_of_pids_already_seen))
        print('number of participants processed in this run {}'.format(number_of_pids_processed))
        print('number of participants left {}'.format(total_participants - number_of_pids_processed - number_of_pids_already_seen))
    return


def main():
    video_dict = get_video_path(VIDPATH)
    workbook = read_excel_sheet(FILEPATH)
    timepoints = extract_time_points(workbook, justone=False)
    # debug - remove later
    print(timepoints['p013']['hand_ties'])
    # save videos
    #slice_and_save(timepoints, video_dict)
    print('all done :)')


if __name__ == '__main__':
    main()
