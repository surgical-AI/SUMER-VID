# loop through each video
# make a directory
# call subprocess with the given command
import glob
import os.path
import subprocess

video_path = r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\videos"
cnt = 0
folders = ['video0'+ str(i) for i in range(1,7)]

for path in glob.glob(r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\videos\*.mp4"):
    _, fname = os.path.split(path)
    fname = fname[:-4]
    if fname in folders:
        continue
    print(fname)
    if not os.path.exists(os.path.join(_, fname)):
        os.mkdir(os.path.join(_, fname))
    out = os.path.join(_, fname)
    cmd = ["ffmpeg", "-i", path, "-r",  "1",  "-q:v", "2", "-f", "image2", "{}/video-%d.jpg".format(out)]
    subprocess.call(cmd)
    cnt += 1
