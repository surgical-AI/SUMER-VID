'''
reads data
specifies architecture, hyperparameters
trains model

data: in a pkl file with paths.
data[0]: train data paths, paths in a list, ordered according to the videos [path1, path2, ...]
data[1]: train labels, ints in a list corresponding to the train paths 
data[2]: val data paths:
data[3]: val labels:
data[4]: train_num_each: tells you how many images per video in the train set. size of this is equal to the number of videos we have
data[5]: val_num_each: same as above for val set

'''
from os import stat_result
from typing import Counter
from utils import resnet_lstm
import torch
import pickle
from config import hyperparams
from utils import ACSDataset
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import copy
import numpy as np
import time 
from torch.utils.data import Dataset, DataLoader
from torch.autograd import Variable
# from torchvision import models, transforms
from torchvision import models, transforms
from PIL import Image, ImageOps


data_read_path = '/home/calvinap/SUMER-VID/pytorch_implementation/data/data_819_410_410.pkl'
model_save_path = '/home/calvinap/SUMER-VID/pytorch_implementation/'

def pil_loader(path):
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')

def read_data(path):
    with open(path, 'rb') as fh:
        data = pickle.load(fh)


    # TODO return ACSDataset objects in dictionary
    # data = [train_list, val_list, test_list, train_label_list, val_label_list, test_label_list, train_num, val_num, test_num]

    return {
        'train_data_and_labels': ACSDataset(data[0], data[3], loader=pil_loader, test=True),
        'val_data_and_labels': ACSDataset(data[1], data[4], loader=pil_loader, test=True),
        'train_num_each':data[6],
        'val_num_each':data[7]
    }

def get_model():
    '''
    returns architecture of the model
    '''
    pass

def train(model, data, sequence_length):
    """
    train_set: training dataset 
    val_set: validation data set
    train_num_each: list of ints. each int at ith index represents the number of images in ith video in the training set.
    val_num_each: list of ints. each int at ith index represents the number of images in ith video in the val set.
    """
    train_data = data['train_data_and_labels']
    val_data =data['val_data_and_labels']
    num_images_per_train_video = data['train_num_each'] 
    num_images_per_val_video = data['val_num_each']


    # use train/val_num_each to decide a good place to start. Dataset is just a 
    # A long sequence and passed into the CNN as such. After the output of CNN
    # the input changes so that each input is a sequence of 3 CNN outputs. 
    # The number of images in the batch should be equeal to the the total number 
    # of LSTM inputs times sequence length so we get that  
    num_train_we_use = 5247 # number of sequences
    num_val_we_use = 612 # number of sequences

    
    
    def _get_sequences(list_of_num_images_per_video, seqeunce_lenth, num_we_want):
        # stopping condition -> if len() + sequence_length > num_images
        # precompute last_index = num_images - seq_length + 1 
        out = []
        start = 0 # start of each video
        num_of_sequences_so_far = 0
        stop_adding_sequences = False

        for num_images in list_of_num_images_per_video:
            if stop_adding_sequences:
                break

            if num_of_sequences_so_far == num_we_want:
                start += num_images
                break
            # setting the last index that can yeild a full sequence without running out
            last_index = start + num_images - seqeunce_lenth + 1
            
            # for each image idx in this 'video' generate a new sequence (with overlapping) 
            for idx in range(start, last_index):
                num_of_sequences_so_far += 1
                out += list(range(idx, idx+sequence_length))
                if num_of_sequences_so_far >= num_we_want:
                    stop_adding_sequences = True
                    break
            
            start += num_images


        # accounting for the last video
        if not stop_adding_sequences:
            last_index = start + list_of_num_images_per_video[-1] - seqeunce_lenth + 1
            for idx in range(start, last_index):
                num_of_sequences_so_far += 1
                out += list(range(num_images, num_images+sequence_length))
                if num_of_sequences_so_far >= num_we_want:
                    break
        return out
        

    
    idx_for_uniform_sequences_val = _get_sequences(num_images_per_val_video, sequence_length, num_val_we_use)
    train_size = -1
    
    # do other stuff ...

    # these were the indicis to the data, load the actual data
    # DataLoader wraps an iterable around DataSet and gives a minibatch at every iteration
    # After a interating through all batches, it shuffles the data if shuffle is True to minimize 
    # overfitting
    # https://pytorch.org/tutorials/beginner/basics/data_tutorial.html#iterate-through-the-dataloader
    

    val_loader = DataLoader(
        val_data, # ACSDataset object
        batch_size=hyperparams['val_batch_size'], # batchsize = 9
        sampler=idx_for_uniform_sequences_val, # this is the indices for all of the data. I am assuming that this 
        #takes the 0 to batchsize indices from this list for the first batch, and so on.  
        #num_workers=workers, # dont know what this is
        pin_memory=False # dont know what this does
    )

    # we have created our loaders which give us a batch at at time (review later if possible)
    
    # we set the loss criterion
    loss_criterion = nn.CrossEntropyLoss(size_average=False) # size average will average over minibatch
    # set optimizer
    optimizer = optim.Adam(
        model.parameters(), 
        lr=hyperparams['learning_rate']
    )


    
    # scheduler (?) # reduces leraning rate based on some validation measurements
    scheduler = lr_scheduler.ReduceLROnPlateau(optimizer, 'min')
    
    # initializing variables for tracking best performance
    best_model_wts = copy.deepcopy(model.state_dict())
    best_val_accuracy = 0.0
    correspond_train_acc = 0.0

    # for loop for training per epoch
    #for epoch in range(hyperparams['epochs']):
    for epoch in range(1): # change to hyperparams['epoch'] while actually training
        idx_for_uniform_sequences_train = _get_sequences(num_images_per_train_video, sequence_length, num_train_we_use)
        # train_size = len(idx_for_uniform_sequences_train) if train_size == -1 else train_size
        train_loader = DataLoader(
            train_data, # ACSDataset object
            batch_size=hyperparams['train_batch_size'], # batchsize = 99
            sampler=idx_for_uniform_sequences_train, # this is the indices for all of the data. I am assuming that this #takes the 0 to batchsize indices from this list for the first batch, and so on.  
            #num_workers=workers, # dont know what this is
            pin_memory=False # dont know what this does
        )

        model.train() # TODO what does this do?
        train_loss = 0.0
        train_corrects = 0
        train_start_time = time.time()
        cnt = 0
        for data in train_loader:
            # for testing puproses lets end after 5
            if cnt == 2:
                print('discontinuing for testing purposes')
                break 
            cnt += 1
            print('starting minibatch {}'.format(cnt))
            inputs, labels = data
            # converting them to Variable objects
            # inputs = Variable(inputs) #Variable(inputs.cuda())
            # labels = Variable(labels) #Variable(labels.cuda())

            inputs = Variable(inputs.cuda())
            labels = Variable(labels.cuda())
            
            optimizer.zero_grad() # TODO why?
            outputs = model.forward(inputs) # forward pass
            _, preds = torch.max(outputs.data, 1) # outputs must be bunch of probabilities per input
            loss = loss_criterion(outputs, labels)
            loss.backward() # ? calculates gradients for all parameters
            optimizer.step() # ? updates weights
            train_loss += loss.item() # updates the loss for this batch
            train_corrects += torch.sum(preds == labels.data) # gives number of corrects
            print('ending minibatch {}'.format(cnt))
        
        train_elapsed_time = time.time() - train_start_time
        train_accuracy = train_corrects / num_train_we_use
        train_average_loss = train_loss / num_train_we_use

        # TODO: THE FOLLOWING IS REPEATED CODE ===> WRITE A FUNCTION FOR THIS
        # loss at the end of an epoch
        model.eval() # TODO what is this?
        val_loss = 0.0
        val_corrects = 0
        val_start_time = time.time()
        for data in val_loader:
            inputs, labels = data # inputs is a tensor
            inputs = Variable(inputs.cuda())
            labels = Variable(labels.cuda()) # TODO what does cuda do?

            outputs = model.forward(inputs)

            outputs = outputs[sequence_length-1::sequence_length] # taking only the predictions that are at the end of the output
            _, preds = torch.max(outputs.data, 1)
            labels = labels[sequence_length-1::sequence_length] # every image has its own label
            loss = loss_criterion(outputs, labels)
            val_loss += loss.item()
            val_corrects += torch.sum(preds==labels.data)

        val_elapsed_time = time.time() - val_start_time
        val_accuracy = val_corrects / num_val_we_use
        val_average_loss = val_loss / num_val_we_use

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            correspond_train_acc = train_accuracy
            best_model_wts = copy.deepcopy(model.state_dict())
        if val_accuracy == best_val_accuracy:
            if train_accuracy > correspond_train_acc:
                correspond_train_acc = train_accuracy
                best_model_wts = copy.deepcopy(model.state_dict())

        # TODO print a bunch of stuff
        # record_np[epoch, 0] = train_accuracy
        # record_np[epoch, 1] = train_average_loss
        # record_np[epoch, 2] = val_accuracy
        # record_np[epoch, 3] = val_average_loss       

    # TODO  print best accuracy
    # TODO save the model
    # YOU DONE
    print("you done!!!")

def save_model_logs(model, logs):
    pass

def main():
    data = read_data(data_read_path)
    model = resnet_lstm(sequence_length=hyperparams['sequence_length'])
    if torch.cuda.is_available():
        print('GPU recognized!')
        model = model.cuda()
    trained_model = train(model, data, hyperparams['sequence_length'])
    # save_model_logs(trained_model, logs)

if __name__ == '__main__':
    main()


# fix the DataSet object creation
# Set up pytorch on linux
# Debug