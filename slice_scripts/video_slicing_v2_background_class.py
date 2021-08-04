"""
reads file names and annotations from excel sheet.
reads each file, each class and annotations, cuts the video into clips using VideoFileClip, and outputs to corresponding
class folder
Note: the reason for using moviepy's VideoFileClip over ffmpeg was ffmpeg was not accurately cutting the videos
at the desired points.
"""
import os
#from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
#from moviepy.video.io.VideoFileClip import VideoFileClip
import json
import random

# Start with
# DIR_PATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\Annotations'
# FILENAME = r'SIM R01 Annotation Table_local_copy_downloaded_feb_19_2021.xlsx'
# FILEPATH = os.path.join(DIR_PATH, FILENAME)
# VIDPATH = r'C:\Users\Carla Pugh\Box\Pugh Lab Shared Drive\4. Data Base\ACS-October2019\ACS 2019 Aligned Videos'
# OUTPUTPATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\new_slices_avi'
# PIDS_PATH = r'C:\Users\Carla Pugh\PycharmProjects\VideoSlicing\new_slices\pids_seen_so_far.txt'
JSON_PATH = '/home/calvinap/SUMER-VID/annotations_json/serialized_pugh_annotations.json'
NUM_VIDEOS_PER_PARTICIPANT = 10 # number of background videos per participant. This limit needs to be set since total number of 2s  background videos
# can get very high 

random.seed(a=1)

def _get_time_window_markers(start_times, end_times, window_size, pid):
    """
    gets independent, adjacent n second time windows markers from start and stop time. For example if start, end times
    are 1:00 - 1:10 -> it will output 1:00 - 1:02 ....1:08 - 1:10
    :param start_times:
    :param end_times:
    :return:
    """
    annotations = zip(start_times, end_times)
    new_start_times = []
    new_end_times = []
    for st, end in annotations:
        if st == '' or end == '':
            continue

        st_seconds = st
        end_seconds = end

        # propagate the special time symbol
        if st_seconds == -1 or end_seconds == -1:
            new_start_times.append(st_seconds)
            new_end_times.append(end_seconds)

        # Get total duration
        total_time = end_seconds - st_seconds

        # if duration is less than or equal to 3 seconds then dont cut
        if total_time <= 3:
            new_start_times.append(st_seconds)
            new_end_times.append(end_seconds)
            continue

        num_windows = int(total_time/window_size)
        window_start = st_seconds

        for window_num in range(num_windows):
            # add start time of window
            new_start_times.append(window_start)
            if window_num == num_windows - 1:
                # if last window then just use the end time of the annotation
                new_end_times.append(end_seconds)
            else:
                # else calculate the end time using the start time and window size
                new_end_times.append(window_start + window_size)
            window_start += window_size
            
    out = random.sample(list(zip(new_start_times, new_end_times)), k=NUM_VIDEOS_PER_PARTICIPANT)
    print(out)
    return out

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

def extract_time_points_from_json(path):
    def _prep_timepts(starttimepts, endtimepts, activity_type):
        out = []
        for i in range(len(starttimepts)):
            out.append({
                'start': starttimepts[i],
                'end': endtimepts[i],
                'activity_type': activity_type
            })
        return out
    
    timepoints = json.load(open(path, 'rb'))
    out = {}
    black_list = ['p120 - i']
    for participant_id, tps_list in timepoints.items():
        start_list = []
        stop_list = []
        if participant_id in black_list:
            continue

        for tp in tps_list:
            # if it is not background, we do not care
            if tp[-1] != 'background':
                continue
            # if the size of the video is not 2 seconds at least, we do not care
            if int(tp[1]) - int(tp[0]) < 2:
                continue
            start_list.append(tp[0])
            stop_list.append(tp[1])
        finalized_start_times, finalized_stop_times = zip(*_get_time_window_markers(start_list, stop_list, 2, participant_id))
        out[participant_id] = _prep_timepts(finalized_start_times, finalized_stop_times, 'background')

    return out

def main():
    # video_dict = get_video_path(VIDPATH)
    timepoints = extract_time_points_from_json(JSON_PATH)
    # go through an entire video and cut
    #slice_and_save(timepoints, video_dict)
    print('all done :)')


if __name__ == '__main__':
    main()
