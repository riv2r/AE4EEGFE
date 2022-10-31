import warnings
import scipy.signal
import numpy as np
import mne
import sys
from GetDataSSVEP import GetData

def filterbank(eeg, fs, idx_fb):    
    if (idx_fb == None):
        warnings.warn('stats:filterbank:MissingInput '\
                     +'Missing filter index. Default value (idx_fb = 0) will be used.')
        idx_fb = 0
    elif (idx_fb < 0 or 20 < idx_fb):
        raise ValueError('stats:filterbank:InvalidInput '\
                        +'The number of sub-bands must be 0 <= idx_fb <= 20.')
            
    if (len(eeg.shape)==2):
        num_chans = eeg.shape[0]
        num_trials = 1
    else:
        num_chans, _, num_trials = eeg.shape
    
    # Nyquist Frequency = Fs/2N
    Nq = fs/2
    
    '''
    passband = [6, 14, 22, 30, 38, 46, 54, 62, 70, 78]
    stopband = [4, 10, 16, 24, 32, 40, 48, 56, 64, 72]
    '''
    passband = np.arange(5,86,4)
    stopband = np.arange(4,85,4)
    # passband = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]
    # stopband = [4, 9 , 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84]
    
    Wp = [passband[idx_fb]/Nq, 90/Nq]
    Ws = [stopband[idx_fb]/Nq, 100/Nq]
    [N, Wn] = scipy.signal.cheb1ord(Wp, Ws, 3, 40) # band pass filter StopBand=[Ws(1)~Ws(2)] PassBand=[Wp(1)~Wp(2)]
    [B, A] = scipy.signal.cheby1(N, 0.5, Wn, 'bandpass') # Wn passband edge frequency
    
    y = np.zeros(eeg.shape)
    if (num_trials == 1):
        for ch_i in range(num_chans):
            #apply filter, zero phass filtering by applying a linear filter twice, once forward and once backwards.
            # to match matlab result we need to change padding length
            y[ch_i, :] = scipy.signal.filtfilt(B, A, eeg[ch_i, :], padtype = 'odd', padlen=3*(max(len(B),len(A))-1))
        
    else:
        for trial_i in range(num_trials):
            for ch_i in range(num_chans):
                y[ch_i, :, trial_i] = scipy.signal.filtfilt(B, A, eeg[ch_i, :, trial_i], padtype = 'odd', padlen=3*(max(len(B),len(A))-1))
           
    return y
        
        
if __name__ == '__main__':
    print(np.arange(4,85,4))
    '''
    from scipy.io import loadmat
    
    D = loadmat("sample.mat")
    eeg = D['eeg']
    eeg = eeg[:, :, (33):(33+125), :]
    eeg = eeg[:,:,:,0] #first bank
    eeg = eeg[0, :, :] #first target
    
    y1 = filterbank(eeg, 250, 0)
    y2 = filterbank(eeg, 250, 9)
    
    y1_from_matlab = loadmat("y1_from_matlab.mat")['y1']
    y2_from_matlab = loadmat("y2_from_matlab.mat")['y2']

    dif1 = y1 - y1_from_matlab
    dif2 = y2 - y2_from_matlab    
    
    print("Difference between matlab and python = ", np.sum(dif1))
    print("Difference between matlab and python = ", np.sum(dif2))
    '''

 
    path = 'dataset/SSVEP_BCI_DATA_1/1-3.vhdr'
    raw = mne.io.read_raw_brainvision(path)
    # use bellow codes to find st_time 
    # raw.plot()
    # plt.show()

    picks = ['IO','POz','Oz','PO3','PO4','O1','O2']
    raw.pick_channels(picks)

    # By observation
    # SSVEP_BCI_DATA_1: 12 9.5 9
    # SSVEP_BCI_DATA_2: 10 12 14
    #                   11 11 9
    #                   20 16 6
    last_time = 125
    st_time = 9
    ed_time = st_time+last_time
    raw = raw.crop(st_time,ed_time)

    dataset=GetData()    

    raw=dataset.preProcessing(raw)
    raw=dataset.repairEOGByICA(raw)
    data,t,numGroups,numChans,numSamplingPoints,samplingRate = dataset.getEpochs(raw)

    y = filterbank(data[0],250,16)
    print(y)
