# FIX PATH OF ACTUAL DATA IN TRAIN.PY see variable data
# download 3 pictures 

# write code to
## make a new folder for the fake data and classes
## For each class
## list all the folders that contain the videos
## list all the file names of all the files in each of the video
## make a new folder for each video if it has not been made and copy the image and save it as the file name of the listed image

# add a flag in the ACSDataset class that if it is test set it will know to do pick the fake set
import os
import glob 
import shutil

data = "/mnt/c/Users/calvinap/SUMER-VID/data_v5.1"
base = "/home/calvinap/SUMER-VID/pytorch_implementation/"
real_fake_dict = {'suture_throws': os.path.join(base,'throw.jpg'), 'thread_cuts':os.path.join(base,'cut.jpg'), 'hand_ties':os.path.join(base,'tie.jpg')}

path_for_fake_data = '/home/calvinap/SUMER-VID/pytorch_implementation/data_v5.2_fake/'
os.mkdir(path_for_fake_data)

for class_name in os.listdir(data):
    if 'background' in class_name:
        continue
    print('class is: {}'.format(class_name))
    path_for_fake_class = os.path.join(path_for_fake_data, class_name)
    if not os.path.exists(path_for_fake_class):
        print('creating a folder: {}'.format(path_for_fake_class))
        os.mkdir(path_for_fake_class)

    full_path_to_class = os.path.join(data, class_name)
    for vid_folder in os.listdir(full_path_to_class):
        path_for_fake_vid = os.path.join(path_for_fake_class, vid_folder)
        if not os.path.exists(path_for_fake_vid):
            print('creating a folder: {}'.format(path_for_fake_vid))
            os.mkdir(path_for_fake_vid)

        for image_name in os.listdir(os.path.join(full_path_to_class, vid_folder)):
            dest_image_path = os.path.join(path_for_fake_vid, os.path.split(real_fake_dict[class_name])[1])
            print('creating new fake image: {} from {} '.format(dest_image_path, real_fake_dict[class_name]))

            shutil.copy(real_fake_dict[class_name], path_for_fake_vid)
            os.rename(dest_image_path, os.path.join(path_for_fake_vid, image_name))
            print('created, new location: {}'.format(dest_image_path))
    






