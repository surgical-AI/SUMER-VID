# SUMER-VID
SUMER-VID - surgical maneuver recognition with videos. A project where we are trying to build a model that recognizes surgical maneuvers such as ties, cuts and suture throws


The video slice scripts read data from a local data repo and an annotations excel sheet. They cut the videos and store them in class folders for easy use by the models

The jupyter notebooks read data that has been outputted using the video slice scripts and train models. The notebook names indicate the different version. model_X_Y is the template where X indicates major changes - GRU to LSTM or Not trained mobileNet to pretrained mobileNet, the Y indicates minor changes or hyper parameter changes. (this standard is followed loosely)

The cholec80 experiments folder contains all scripts written to get a current model to learn from the cholec80 dataset. An initial experiment was tried where the existing model for SUMER-VID was tried. Then a keras implementation of the SVR-CNEt paper was tried. https://github.com/YuemingJin/SV-RCNet
A third experiment is in progress where a pytorch implementation from: https://github.com/YuemingJin/MTRCNet-CL/blob/master/train_singlenet_phase.py is being tried out


The experiments are not completely reproducible since 1. the data is missing! 2. the virtual environment is not included here. 
