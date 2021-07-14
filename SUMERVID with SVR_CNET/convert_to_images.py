# loop through each video
# make a directory
# call subprocess with the given command
import glob
import os.path
import subprocess

classes = ['hand_ties', 'thread_cuts', 'suture_throws']
video_path = r"C:\Users\calvinap\SUMER-VID\data_v5"
out_path = r"C:\Users\calvinap\SUMER-VID\data_v5.1"


def convert(folder_with_videos, cls):
    cnt = 0
    glob_pattern = os.path.join(folder_with_videos, '*.mp4')
    #glob_pattern = sorted(glob_pattern, key=lambda x: int(x.split('_')[0][1:]), int(x.split('_')[-1][:-4]))
    total_videos = len(glob.glob(glob_pattern))
    for path in glob.glob(glob_pattern):
        _, fname = os.path.split(path)
        prefix = fname[:4]
        suffix = fname[:-4].split('_')[-1]
        fname = prefix + '_' + suffix
        # if fname in :
        #     continue
        # print(fname)

        outpath = os.path.join(os.path.join(out_path, cls), fname)
        if not os.path.exists(outpath):
            os.mkdir(outpath)
        cmd = ["ffmpeg", "-i", path, "-r", "1", "-s", "250x250", "-q:v", "2", "-f", "image2", "{}/{}-%d.jpg".format(outpath, fname)]
        subprocess.call(cmd)
        cnt += 1
        print(path, outpath)
        print("..............total number of videos for {}: {}, total videos done: {} "
              "total videos left: {}..............".format(cls, total_videos, cnt, total_videos - cnt))
    print("{} done".format(cls))

if __name__ == '__main__':
    for cls in classes:
        cls_video_path = os.path.join(video_path, cls)
        convert(cls_video_path, cls)


