"""
reads file names and annotations from excel sheet.
reads each file, each class and annotations, cuts the video into clips using VideoFileClip, and outputs to corresponding
class folder
Note: the reason for using moviepy's VideoFileClip over ffmpeg was ffmpeg was not accurately cutting the videos
at the desired points.
"""
import os
import xlrd
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.video.io.VideoFileClip import VideoFileClip

# Start with
DIR_PATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\Annotations'
FILENAME = r'SIM R01 Annotation Table_local_copy_downloaded_feb_19_2021.xlsx'
FILEPATH = os.path.join(DIR_PATH, FILENAME)
VIDPATH = r'C:\Users\Carla Pugh\Box\Pugh Lab Shared Drive\4. Data Base\ACS-October2019\ACS 2019 Aligned Videos'
OUTPUTPATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\new_slices_avi'
PIDS_PATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\new_slices\pids_seen_so_far.txt'

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

    def _prep_timepts(starttimepts, endtimepts, activity_type):
        out = []
        for i in range(len(starttimepts)):
            out.append({
                'start': starttimepts[i],
                'end': endtimepts[i],
                'activity_type': activity_type
            })
        return out
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
        suture_time_points = _prep_timepts(suture_start_times, suture_end_times, activity_type='suture_throws')

        # hand ties; as above
        hand_tie_start_times = sheet.col_values(24)[2:]
        hand_tie_end_times = sheet.col_values(25)[2:]
        handtie_time_points = _prep_timepts(hand_tie_start_times, hand_tie_end_times, activity_type='hand_ties')

        # threadcut; as above
        threadcut_start_times = sheet.col_values(28)[2:]
        threadcut_end_times = sheet.col_values(29)[2:]
        threadcut_time_points = _prep_timepts(threadcut_start_times, threadcut_end_times, activity_type='thread_cuts')

        # Each time point is a dict with start, stop, activity_type
        timepoints[pid] = suture_time_points + handtie_time_points + threadcut_time_points

        if justone:
            break

    return timepoints


def _run_slice_save(timepts, pid, video_dict):
    input_path = video_dict.get(pid)
    if input_path is None:
        return
    subclip_cnt = 0
    with VideoFileClip(input_path) as video:
        for timept in timepts:
            # get the type of activity type
            action_type = timept.get('activity_type')

            # find the right folder to write to
            relevant_path = os.path.join(OUTPUTPATH, action_type)

            # see if folder exists, if not create it
            if not os.path.exists(relevant_path):
                os.mkdir(relevant_path)

            # get start and stop seconds for each duration
            start, stop = timept.get('start'), timept.get('end')
            if start == '' or stop == '':
                continue
            # cut and save
            start_seconds = get_sec(start)
            stop_seconds = get_sec(stop) + 1  # adding a second since the cutter cuts only prior to end time in annotation. we want to include the end second in the annotation
            if stop_seconds == -1 or start_seconds == -1:
                print('incompatible start or stop time; start: {}, stop: {}'.format(start_seconds, stop_seconds))
                continue

            print('saving...')
            new = video.subclip(start_seconds, stop_seconds)
            camera = input_path.split('.')[2]
            file_name = '{}_{}_{}_{}.mp4'.format(pid, action_type, camera, subclip_cnt)
            output_path = os.path.join(relevant_path, file_name)

            new.write_videofile(output_path)
            subclip_cnt += 1


def slice_and_save(timepoints_dict, video_dict):
    print('slicing')
    # To not re cut already saved videos: reads the saved list of pids that have already been sliced
    with open(PIDS_PATH, 'w+') as ropen:
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
        _run_slice_save(timepts, participant_id, video_dict)
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
    # go through an entire video and cut
    slice_and_save(timepoints, video_dict)
    print('all done :)')


if __name__ == '__main__':
    main()
