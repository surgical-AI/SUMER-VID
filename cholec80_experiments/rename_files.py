import os

# specify folder name
base_path = r"C:\Users\calvinap\SUMER-VID\cholec80\cholec80\data_resize"

# traverse each video folder in folder
for video_folder in os.listdir(base_path):
    vid_num_str = video_folder[-2:]
    video_full_path = os.path.join(base_path, video_folder)
    for image in os.listdir(video_full_path):
        new_name = image.split('-')[0] + vid_num_str + '-' + image.split('-')[1]
        print('new_name:{}, old_name: {}'.format(new_name, image))
        old_path = os.path.join(video_full_path, image)
        new_path = os.path.join(video_full_path, new_name)
        os.rename(old_path, new_path)
