# loop through each video
# make a directory
# call subprocess with the given command
import glob
import os.path
import subprocess

video_path = r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\videos"
cnt = 0
for path in glob.glob(r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\videos\*.mp4"):
    _, fname = os.path.split(path)
    fname = fname[:-4]
    print(fname)
    if not os.path.exists(os.path.join(_, fname)):
        os.mkdir(os.path.join(_, fname))
    cmd = "ffmpeg -i {f}.mp4 -r 1 -q:v 2 -f image2 {f}/{f}-%d.jpg".format(f=fname)
    subprocess.call(cmd)
    if cnt == 2:
        break
    cnt += 1
