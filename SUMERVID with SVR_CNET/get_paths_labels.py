import pickle
import glob
import os

# iterate through all the files, get set of all participants - particpant list
# iterate through participants
# grab images from each class and take the image info list and list of images and put them in the particpant list


all_info_all = []

classes_list = ['hand_ties', 'suture_throws', 'thread_cuts']
classes = { 'hand_ties':1, 'suture_throws': 2, 'thread_cuts':3 }

base_path = r'C:\Users\calvinap\SUMER-VID\data_v5.1'





hand_ties_info = []
suture_throws_info = []
thread_cuts_info = []
theadcut = []

for pid in pid_set:
    pass

for path in glob.glob(hand_ties_path): # hand_ties_path = hand_ties_folder contains all video folders
    hand_ties_info.append(glob.glob(path + '/*'))
    hand_ties_path.append(classes['hand_ties'])

for path in glob.glob(thread_cuts_path):
    thread_cuts_info.append(glob.glob(path + '/*'))
    thread_cuts_info.append(classes['thread_cuts'])

def get_all_info(pids, base_path):
    hand_ties_path = os.path.join(base_path, classes_list[0])
    thread_cuts_path = os.path.join(base_path, classes_list[1])
    suture_throws_path = os.path.join(base_path, classes_list[2])

    print('hand_tie_path: {}'.format(hand_ties_path))
    print('thread_cuts_path: {}'.format(thread_cuts_path))
    print('suture_throws_path: {}'.format(suture_throws_path))
    data_set = []
    for pid in pids:
       data_set.append(get_image_info(hand_ties_path, pid))




def get_pids(path):
    """
    gets all names of the folders in the class folders in path and retursn a set of the videos ids
    """
    pid_set = set()
    # get participant video ids from all class folders
    pid_set.update(set(os.listdir(hand_ties_path)))
    pid_set.update(set(os.listdir(suture_throws_path)))
    pid_set.update(set(os.listdir(thread_cuts_path)))
    return pid_set


if __name__ == '__main__':
    pids = get_pids(base_path)
    data_set = get_all_info(pids, base_path)

    train_idx = int(len(data_set) * train_split)
    val_idx = int(len(data_set) * (train_split + val_split))

    # save training
    train_split = 0.5
    val_split = 0.25

    save_data_pkl(data_set, train_split, val_split, save_path)

    print("all done =D")