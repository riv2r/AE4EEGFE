# GetDataSSVEP
# Get Dataset from SSVEP experiment
# Repair EOG artifact with ICA
# Get 25 Epochs from an experiment

import mne
from mne.preprocessing import ICA
import matplotlib.pyplot as plt
import time


class GetData():

    def preProcessing(self,raw):

        # resampling 1000Hz -> 250Hz
        raw_downsampled = raw.copy().resample(sfreq=250)
        # notch filter 50.0Hz
        raw_notch = raw_downsampled.copy().notch_filter(freqs=50.0)
        # bandpass filter 2.0Hz - 100.0Hz
        raw_filt = raw_notch.copy().filter(l_freq=2.0,h_freq=100.0)

        return raw_filt

    def repairEOGByICA(self,raw):

        # apply ICA
        ica = ICA(max_iter='auto', random_state=80) 
        # 20th channel named 'IO' is EOG channel
        # EOG projections should be temporally removed before ICA.fit
        ica.fit(raw.copy().drop_channels('IO'), decim=50)
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
        # raw_reconst.plot()
        # plt.show()

        raw_reconst.drop_channels('IO')

        return raw_reconst

    def getEpochs(self,raw):

        epochs = mne.make_fixed_length_epochs(raw, duration=5)
        data = epochs.get_data()
        t = epochs.times
        numGroups = data.shape[0]
        numChans = data.shape[1]
        numSamplingPoints = data.shape[2]
        samplingRate = raw.info['sfreq']
        
        return data,t,numGroups,numChans,numSamplingPoints,samplingRate


if __name__=='__main__':

    start = time.time()
    path = 'dataset/SSVEP_BCI_DATA_1/1-1.vhdr'
    raw = mne.io.read_raw_brainvision(path)

    picks = ['IO','POz','Oz','PO3','PO4','O1','O2']
    raw.pick_channels(picks)

    # By observation
    # 12 9.5 9
    last_time = 125
    st_time = 12
    ed_time = st_time+last_time
    raw = raw.crop(st_time,ed_time)

    dataset=GetData() 

    raw=dataset.preProcessing(raw)
    raw=dataset.repairEOGByICA(raw)
    data,t,numGroups,numChans,numSamplingPoints,samplingRate = dataset.getEpochs(raw)
    end = time.time()
    print('程序执行时间为：',end-start,'s')
    raw.plot()
    plt.show()