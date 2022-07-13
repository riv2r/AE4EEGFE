# GetDataSSVEP
# Get Dataset from SSVEP experiment
# Repair EOG artifact with ICA
# Get 25 Epochs from an experiment

import mne
from mne.preprocessing import ICA
import numpy as np
import matplotlib.pyplot as plt

class GetDataset(object):

    def __init__(self):
        self.data = None
        self.time = None
        self.samplingRate = None
    
    def initialize(self,raw):
        # path of .vhdr
        self.data = raw.get_data()
        self.time = raw.times 
        self.samplingRate = raw.info['sfreq']
        # plot original EEG
        # self.raw.plot()
        # plt.show()

    def preProcessing(self,raw):
        # resampling 1000Hz -> 250Hz
        raw_downsampled = raw.copy().resample(sfreq=250)
        # notch filter 50.0Hz
        raw_notch = raw_downsampled.copy().notch_filter(freqs=50.0)
        # bandpass filter 2.0Hz - 100.0Hz
        raw_filt = raw_notch.copy().filter(l_freq=2.0,h_freq=100.0)

        self.initialize(raw_filt)
        return raw_filt

    def repairEOGByICA(self,raw):
        # apply ICA
        ica = ICA(n_components=15, max_iter='auto', random_state=80) 
        ica.fit(raw)
        ica
        ica.exclude = []
        # find which ICs match the EOG pattern
        eog_indices, eog_scores = ica.find_bads_eog(raw,ch_name='IO')
        ica.exclude = eog_indices
        # barplot of ICA component "EOG match" scores
        # ica.plot_scores(eog_scores)
        # plt.show()

        # ica.apply() changes the Raw object in-place, so let's make a copy first:
        raw_reconst = raw.copy()
        ica.apply(raw_reconst)
        # compare original and reconstructed
        # raw.plot()
        # plt.show()
        # reconst_raw.plot()
        # plt.show()

        self.initialize(raw_reconst)
        return raw_reconst

    def getEpochs(self,raw):
        epochs = mne.make_fixed_length_epochs(raw,duration=5)
        data = epochs.get_data()
        time = epochs.times
        numGroups = data.shape[0]
        numChans = data.shape[1]
        numSamplingPoints = data.shape[2]
        
        return data,time,numGroups,numChans,numSamplingPoints



if __name__=='__main__':

    path = 'dataset/SSVEPEEGData/car1.vhdr'
    raw = mne.io.read_raw_brainvision(path)
    # 20th channel
    eog_channel_name='IO'
    last_time = 125
    # raw.plot()
    # plt.show()

    # By observation
    # 10.5 9 8
    st_time = 9
    ed_time = st_time+last_time
    raw = raw.copy().crop(st_time,ed_time)

    dataset=GetDataset()    

    dataset.initialize(raw)
    raw=dataset.preProcessing(raw)
    # raw=dataset.repairEOGByICA(raw)
    data,time,numGroups,numChans,numSamplingPoints = dataset.getEpochs(raw)
    raw.plot()
    plt.show()