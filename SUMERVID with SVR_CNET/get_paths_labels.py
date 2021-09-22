import pickle
import glob
import os
from utils import save_data_pkl
# iterate through all the files, get set of all participants - particpant list
# iterate through participants
# grab images from each class and take the image info list and list of images and put them in the particpant list


all_info_all = []

classes_list = ['hand_ties', 'suture_throws', 'thread_cuts']
classes = { 'hand_ties':1, 'suture_throws': 2, 'thread_cuts':3 }

base_path = '/home/calvinap/SUMER-VID/pytorch_implementation/data_v5.2_fake/'
save_path = '/home/calvinap/SUMER-VID/pytorch_implementation/'


hand_ties_path = os.path.join(base_path, classes_list[0])
thread_cuts_path = os.path.join(base_path, classes_list[1])
suture_throws_path = os.path.join(base_path, classes_list[2])

def get_all_image_packets_for_pid(class_path, pid, label=1):
    # get the right path
    pid_path = os.path.join(class_path, pid)

    # iterate through each of the images for the pid
    out = []
    for image_path in glob.glob(pid_path + '/*'):
        # make image packets for each image in list
        out.append([image_path, label])

    # return list of image packets
    return out


def get_all_info(pids, base_path):
    """
    pids: set, set of all video ids
    base_path: str
    """

    print('hand_tie_path: {}'.format(hand_ties_path))
    print('thread_cuts_path: {}'.format(thread_cuts_path))
    print('suture_throws_path: {}'.format(suture_throws_path))

    data_set = []
    for pid in pids:
        data_set.append(get_all_image_packets_for_pid(hand_ties_path, pid, label=1))
        data_set.append(get_all_image_packets_for_pid(thread_cuts_path, pid, label=2))
        data_set.append(get_all_image_packets_for_pid(suture_throws_path, pid, label=3))
    
    return data_set

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
    # save training
    train_split = 0.5
    val_split = 0.25

    pids = get_pids(base_path)
    
    data_set = get_all_info(pids, base_path)
    train_idx = int(len(data_set) * train_split)
    val_idx = int(len(data_set) * (train_split + val_split))

    save_data_pkl(data_set, train_split, val_split, save_path)

    print("all done =D")