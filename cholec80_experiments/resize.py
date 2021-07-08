# for each folder with images
# for each image
# resize
import subprocess
import os
import glob

outdir = r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\data_resize"

def main():
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    test = 'video01'
    for video in glob.glob(r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\videos\video*\*"):
        base, name = os.path.split(video)
        video_folder = base.split('\\')[-1]
        print(video)

        if int(video_folder[-2:]) <= 42:
            continue

        outfolder = os.path.join(outdir, video_folder)
        if not os.path.exists(outfolder):
            os.mkdir(outfolder)
        out = os.path.join(outfolder, name)
        print(outfolder, out)

        if video_folder == test:
            continue

        call = "ffmpeg -i {name} -vf scale=250:250 {out}".format(name=video, out=out)
        subprocess.call(call)


if __name__ == '__main__':
    main()
