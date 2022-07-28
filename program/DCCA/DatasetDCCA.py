import sys

sys.path.append("program/CCA")

import mne
import torch
import numpy as np
from GetDataSSVEP import GetData
from FEbyCCA import FEbyCCA
from torch.utils.data import random_split


class GetDataset():

    def getDataXY(self):

        # original data path
        path = 'dataset/SSVEPEEGData/car.vhdr'
        # origin raw
        raw = mne.io.read_raw_brainvision(path) 
        # 6 channels associated with SSVEP and EOG channel
        picks = ['IO','POz','Oz','PO3','PO4','O1','O2']
        raw.pick_channels(picks)
        # By observation
        # 12 9.5 9
        last_time = 125
        st_time = 12
        ed_time = st_time+last_time
        # divide to acquisition time
        raw = raw.crop(st_time,ed_time)

        dataset1 = GetData()
        raw=dataset1.preProcessing(raw)
        raw=dataset1.repairEOGByICA(raw)
        # dataX: 25 x 6 x 1250 
        dataX,t,numGroups,numChans,numSamplingPoints,samplingRate = dataset1.getEpochs(raw)
    
        dataset2 = FEbyCCA()
        dataset2.samplingRate = samplingRate
        dataset2.numSamplingPoints = numSamplingPoints
        dataY = []
        for freq in dataset2.freqs:
            freqTemp=dataset2.getReferSignals(freq)
            dataY.append(freqTemp)
        # dataY: 5 x 8 x 1250
        dataY = np.array(dataY).reshape((5,8,1250))

        return dataX,dataY

    def splitDataXY(self,data):

        numSamplingPoints = data.shape[1]

        train_size  = int(numSamplingPoints*0.6)
        val_size    = int(numSamplingPoints*0.2)
        test_size   = numSamplingPoints-train_size-val_size
        '''
        train_dataset,val_dataset,test_dataset = random_split(data.T,[train_size,val_size,test_size])

        train_dataset   = torch.tensor(train_dataset.dataset)
        val_dataset     = torch.tensor(val_dataset.dataset)
        test_dataset    = torch.tensor(test_dataset.dataset)
        ''' 
        data = data.T
        train_dataset   = torch.tensor(data[0                   :train_size                     ,:])
        val_dataset     = torch.tensor(data[train_size          :train_size+val_size            ,:])
        test_dataset    = torch.tensor(data[train_size+val_size :train_size+val_size+test_size  ,:])

        return train_dataset,val_dataset,test_dataset