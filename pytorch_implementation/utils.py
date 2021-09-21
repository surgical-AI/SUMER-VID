from PIL import Image, ImageOps
import torch.nn.init as init
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
import torch
import numbers
import os
import random
from pathlib import PureWindowsPath
import numpy as np

def pil_loader():
    # reads an image with Image.open() and returns it in some form (learn before use)
    pass

class RandomCrop(object):
    def __init__(self, size, padding=0, seqience_length=3):
        if isinstance(size, numbers.Number):
            self.size = (int(size), int(size))
        else:
            self.size = size
        self.padding = padding
        self.count = 0
        self.sequence_length = seqience_length

    def __call__(self, img):

        if self.padding > 0:
            img = ImageOps.expand(img, border=self.padding, fill=0)

        w, h = img.size
        th, tw = self.size
        if w == tw and h == th:
            return img

        random.seed(self.count // self.sequence_length)
        x1 = random.randint(0, w - tw)
        y1 = random.randint(0, h - th)

        # print(self.count, x1, y1)
        self.count += 1
        return img.crop((x1, y1, x1 + tw, y1 + th))


class RandomHorizontalFlip(object):
    def __init__(self):
        self.count = 0

    def __call__(self, img):
        seed = self.count // sequence_length
        random.seed(seed)
        prob = random.random()
        self.count += 1
        # print(self.count, seed, prob)
        if prob < 0.5:
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        return img

class ACSDataset(Dataset):
    def __init__(self, paths, labels, loader, test=False):
        """
        paths: list
        labels: list
        transforms: Transforms.compose method
        """
        self.test = test
        self.fake_path = '/home/calvinap/SUMER-VID/pytorch_implementation/data_v5.2_fake'
        self.paths = paths
        self.labels = np.asarray(labels, dtype=np.int64)[:, -1]
        self.loader = loader

        # the transorms randomly crop the data, convert the RGB values in lists/np to a tensor and normalize with shown values 
        self.transform = transforms.Compose([
            RandomCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.3456, 0.2281, 0.2233], [0.2528, 0.2135, 0.2104])
        ])

    def __getitem__(self, index):
        path = self.paths[index]

        if self.test:
            parts = PureWindowsPath(path).parts
            image_name = parts[-1]
            vid_name = parts[-2]
            class_name = parts[-3]
            path = os.path.join(os.path.join(os.path.join(self.fake_path, class_name), vid_name), image_name)

        images = self.transform(self.loader(path))
        label = self.labels[index]
        return images, label
        
    def __len__(self):
        return len(self.paths)

class resnet_lstm(torch.nn.Module):
    '''
    nn.module is the base class of all neural networks
    '''
    def __init__(self, sequence_length):
        super(resnet_lstm, self).__init__()
        self.sequence_length = sequence_length
        resnet = models.resnet50(pretrained=True)
        self.rn50 = torch.nn.Sequential()
        self.rn50.add_module("conv1", resnet.conv1)
        self.rn50.add_module('bn1', resnet.bn1)
        self.rn50.add_module('relu', resnet.relu)
        self.rn50.add_module('maxpool', resnet.maxpool)
        self.rn50.add_module('layer1', resnet.layer1)
        self.rn50.add_module('layer2', resnet.layer2)
        self.rn50.add_module('layer3', resnet.layer3)
        self.rn50.add_module('layer4', resnet.layer4)
        self.rn50.add_module('avgpool', resnet.avgpool)
        self.lstm = torch.nn.LSTM(2048, 512) # input shape of 2048 and 512 stacked cells
        self.fc = torch.nn.Linear(512, 3) # 512 input 3 output
        init.xavier_normal_(self.lstm.all_weights[0][0]) # xavier = https://pytorch.org/docs/stable/nn.init.html
        init.xavier_normal_(self.lstm.all_weights[0][1])
        init.xavier_uniform(self.fc.weight)
    
    def forward(self, x):
        x = self.rn50.forward(x) # passes the input through the entire resnet model
        x = x.view(-1, 2048) # views are like python views, they avoid explicit copies, allows reshaping
        # -1 here means that the dimension is inferred, calculated
        x = x.view(-1, self.sequence_length, 2048) # reshapes each batch so that each input is a sequence of features
        self.lstm.flatten_parameters() # a perf opimization measure which copies weights into contiguous memory on GPU
        y, _ = self.lstm(x) # x is passed through the lstm as a sequence of visual features
        y = y.contiguous().view(-1, 512) # contiguous makes it so that the original mapping 
        #from indices to values is preserved (after say a view)
        # is the fc outputting a class per visual feature?
        y = self.fc(y)
        return y

def get_useful_start_idx(sequence_length, list_each_length):
    """
    returns a list of where in the list of sequences is the start point and end point and points in between, 
    given the arbitrary length sequences for each input.
    """
    count = 0
    idx = []
    for i in range(len(list_each_length)):
        for j in range(count, count + (list_each_length[i] + 1 - sequence_length)):
            idx.append(j)
        count += list_each_length[i]
    return idx