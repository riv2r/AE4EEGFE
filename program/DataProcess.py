# DataProcess
# get data from SSVEP experiment
# repair EOG artifact by ICA

import mne
from mne.preprocessing import ICA
import matplotlib.pyplot as plt
import time


class DataProcess(object):

    def preprocessing(self,raw):

        # resampling 1000Hz -> 250Hz
        raw_downsampled=raw.copy().resample(sfreq=250)
        # notch filter 50.0Hz
        raw_notch=raw_downsampled.copy().notch_filter(freqs=50.0)
        # bandpass filter 2.0Hz - 100.0Hz
        raw_filt=raw_notch.copy().filter(l_freq=2.0,h_freq=100.0)

        return raw_filt

    def repair_EOG_by_ICA(self,raw):

        # apply ICA
        ica=ICA(max_iter='auto',random_state=80) 
        # EOG projections should be temporally removed before ICA.fit()
        ica.fit(raw.copy().drop_channels('IO'),decim=50)
        ica.exclude=[]
        # find which ICs match the EOG pattern
        eog_indices,eog_scores=ica.find_bads_eog(raw,ch_name='IO')
        ica.exclude=eog_indices
        # barplot of ICA component EOG match scores
        # ica.plot_scores(eog_scores)
        # plt.show()

        # ica.apply() changes the raw object in-place, so let's make a copy first:
        raw_reconst=raw.copy()
        ica.apply(raw_reconst)
        # compare original and reconstructed
        # raw.plot()
        # plt.show()
        # raw_reconst.plot()
        # plt.show()

        raw_reconst.drop_channels('IO')

        return raw_reconst

    def get_epochs(self,raw):

        # adjust duration to fit
        epochs=mne.make_fixed_length_epochs(raw,duration=5) # 4+1
        data=epochs.get_data()
        data=data[:,:,0:1000]
        t=epochs.times
        t=t[0:1000]
        num_groups=data.shape[0]
        num_chans=data.shape[1]
        num_sampling_points=data.shape[2]
        sampling_rate=raw.info['sfreq']
        
        return data,t,num_groups,num_chans,num_sampling_points,sampling_rate