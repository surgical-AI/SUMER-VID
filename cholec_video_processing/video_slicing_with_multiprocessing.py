from collections import defaultdict
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import glob
from datetime import datetime
from multiprocessing import Process
base_dir = r"C:\Users\calvinap\SUMER-VID\cholec80"
viddir = r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\videos\*"
annotation_path = r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\annotations"

def get_sec(time_str):
    """Get Seconds from time. COPIED FROM STACK OVERFLOW"""
    if time_str == 'nc':
        return -1
    time_str = time_str.split('.')[0]
    h, m, s = time_str.split(':')
    return int(h) * 60 + int(m) * 60 + int(s)


def read(annotation_file):
    timestamps = []
    lines = open(annotation_file, 'r').read().splitlines()[1:]
    for line in lines:
        timestamps.append(line.split('\t'))
    return timestamps


def get_phase_stamps(timestamps):
    phase_stamp_dict = defaultdict(list)
    prev_phase = None
    prev_timestamp = None
    for timestamp in timestamps:
        if prev_phase is None:
            start = timestamp[0]
            prev_phase = timestamp[1]
            prev_timestamp = timestamp[0]
            continue

        if prev_phase != timestamp[1]:
            stop = prev_timestamp
            phase_stamp_dict[prev_phase].append((start, stop))
            prev_phase = timestamp[1]
            start = timestamp[0]
        prev_timestamp = timestamp[0]

    phase_stamp_dict[prev_phase].append((start, prev_timestamp))

    return phase_stamp_dict


def cut_and_save(vid_filename, videoname, phase_stamps):
    with VideoFileClip(vid_filename) as video:
        for phase, timestamps in phase_stamps.items():
            outdir = os.path.join(base_dir, phase)
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            cnt = 0
            for ts in timestamps:
                start_seconds = get_sec(ts[0])
                stop_seconds = get_sec(ts[1])
                for clip in range(int((stop_seconds - start_seconds)/2)):
                    if clip == 0:
                        start_clip = start_seconds
                    else:
                        start_clip = start_seconds + (clip * 2) + 1

                    if stop_seconds - start_clip == 3:
                        stop_clip = stop_seconds
                    else:
                        stop_clip = start_clip + 2
                    if stop_clip > stop_seconds:
                        continue
                    cnt += 1
                    new = video.subclip(start_clip, stop_clip)
                    outpath = os.path.join(outdir, '{}_{}_{}.mp4'.format(phase, videoname, cnt))
                    new.write_videofile(outpath)


def process_files(names):
    full_start = datetime.utcnow()
    times = {}
    for filepath in names:
        vid_filename = os.path.split(filepath)[1]
        vid_name = vid_filename.split('.')[0]
        times[vid_name] = datetime.utcnow()
        annotation_file = os.path.join(annotation_path, vid_name + '-timestamp.txt')
        print('processing video: {}'.format(vid_filename))
        print('...reading')
        timestamps = read(annotation_file)
        print('...getting time stamps for each phase')
        phase_stamps = get_phase_stamps(timestamps)
        print('...cutting and saving')
        cut_and_save(filepath, vid_name, phase_stamps)
        print('done')
        time = (datetime.utcnow() - times[vid_name]).total_seconds()
        print('time taken for {} is {} seconds'.format(vid_name, time))
        times[vid_name] = time
    print("all done! :)")
    full_stop = datetime.utcnow()
    print('individual times for each video: {}'.format(times))
    print('total time taken for run = {} seconds'.format((full_stop - full_start).total_seconds()))


if __name__ == '__main__':
    starttime = datetime.utcnow()
    filenames = glob.glob(viddir)
    processes = []
    chunk = int(len(filenames)/os.cpu_count())
    endofarray=False
    for i in range(os.cpu_count()):
        if endofarray:
            continue
        if len(filenames) - (i+1)*chunk <= chunk:
            end = len(filenames)
            endofarray=True
        else:
            end = (i+1) * chunk

        #print(i*chunk, end)
        subnames = filenames[i*chunk: end]
        processes.append(Process(target=process_files, args=(subnames,)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    stopttime = datetime.utcnow()
    print("total time taken with multiprocessing: {}".format((stopttime - starttime).total_seconds()))
