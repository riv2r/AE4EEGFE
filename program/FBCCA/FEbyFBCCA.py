import mne
import sys
sys.path.append("program/CCA")
from GetDataSSVEP import GetData
from sklearn.cross_decomposition import CCA
from filterbank import filterbank
from scipy.stats import pearsonr
import numpy as np
import time

'''
Steady-state visual evoked potentials (SSVEPs) detection using the filter
bank canonical correlation analysis (FBCCA)-based method [1].

function results = test_fbcca(eeg, list_freqs, fs, num_harms, num_fbs)

Input:
  eeg             : Input eeg data 
                    (# of targets, # of channels, Data length [sample])
  list_freqs      : List for stimulus frequencies
  fs              : Sampling frequency
  num_harms       : # of harmonics
  num_fbs         : # of filters in filterbank analysis

Output:
  results         : The target estimated by this method

'''

def fbcca(eeg, list_freqs, fs, num_harms=3, num_fbs=16):
    
    fb_coefs = np.power(np.arange(1,num_fbs+1),(-1.25)) + 0.25
    num_targs = 5
    num_chans, num_smpls = eeg.shape
    y_ref = cca_reference(list_freqs, fs, num_smpls, num_harms)
    cca = CCA(n_components=1) #initilize CCA
    
    # result matrix
    r = np.zeros((num_fbs, num_targs))
    results = np.zeros(num_targs)
    
    test_tmp = np.squeeze(eeg[:, :])  #deal with one target a time
    for fb_i in range(num_fbs):  #filter bank number, deal with different filter bank
         testdata = filterbank(test_tmp, fs, fb_i)  #data after filtering
         for class_i in range(num_targs):
             refdata = np.squeeze(y_ref[class_i, :, :])   #pick corresponding freq target reference signal
             test_C, ref_C = cca.fit_transform(testdata.T, refdata.T)
             # len(row) = len(observation), len(column) = variables of each observation
             # number of rows should be the same, so need transpose here
             # output is the highest correlation linear combination of two sets
             r_tmp, _ = pearsonr(np.squeeze(test_C), np.squeeze(ref_C)) #return r and p_value, use np.squeeze to adapt the API 
             r[fb_i, class_i] = r_tmp
             
    rho = np.dot(fb_coefs, r)  #weighted sum of r from all different filter banks' result
    # print(rho)
    tau = np.argmax(rho)+1  #get maximum from the target as the final predict (get the index)
    results = tau #index indicate the maximum(most possible) target
    return results

'''
Generate reference signals for the canonical correlation analysis (CCA)
-based steady-state visual evoked potentials (SSVEPs) detection [1, 2].

function [ y_ref ] = cca_reference(listFreq, fs,  nSmpls, nHarms)

Input:
  listFreq        : List for stimulus frequencies
  fs              : Sampling frequency
  nSmpls          : # of samples in an epoch
  nHarms          : # of harmonics

Output:
  y_ref           : Generated reference signals
                   (# of targets, 2*# of channels, Data length [sample])
'''      

def cca_reference(list_freqs, fs, num_smpls, num_harms=3):
    
    num_freqs = len(list_freqs)
    tidx = np.arange(1,num_smpls+1)/fs #time index
    
    y_ref = np.zeros((num_freqs, 2*num_harms, num_smpls))
    for freq_i in range(num_freqs):
        tmp = []
        for harm_i in range(1,num_harms+1):
            stim_freq = list_freqs[freq_i]  #in HZ
            # Sin and Cos
            tmp.extend([np.sin(2*np.pi*tidx*harm_i*stim_freq),
                       np.cos(2*np.pi*tidx*harm_i*stim_freq)])
        y_ref[freq_i] = tmp # 2*num_harms because include both sin and cos
    
    return y_ref

'''
Base on fbcca, but adapt to our input format
'''   

def fbcca_realtime(data, list_freqs, fs, num_harms=3, num_fbs=5):
    
    fb_coefs = np.power(np.arange(1,num_fbs+1),(-1.25)) + 0.25
    
    num_targs = len(list_freqs)
    _, num_smpls = data.shape
    
    y_ref = cca_reference(list_freqs, fs, num_smpls, num_harms)
    cca = CCA(n_components=1) #initialize CCA
    
    # result matrix
    r = np.zeros((num_fbs,num_targs))
    
    for fb_i in range(num_fbs):  #filter bank number, deal with different filter bank
        testdata = filterbank(data, fs, fb_i)  #data after filtering
        for class_i in range(num_targs):
            refdata = np.squeeze(y_ref[class_i, :, :])   #pick corresponding freq target reference signal
            test_C, ref_C = cca.fit_transform(testdata.T, refdata.T)
            r_tmp, _ = pearsonr(np.squeeze(test_C), np.squeeze(ref_C)) #return r and p_value
            if r_tmp == np.nan:
                r_tmp=0
            r[fb_i, class_i] = r_tmp
    
    rho = np.dot(fb_coefs, r)  #weighted sum of r from all different filter banks' result
    print(rho) #print out the correlation
    result = np.argmax(rho)  #get maximum from the target as the final predict (get the index), and index indicates the maximum entry(most possible target)
    ''' Threshold '''
    THRESHOLD = 2.1
    if abs(rho[result])<THRESHOLD:  #2.587=np.sum(fb_coefs*0.8) #2.91=np.sum(fb_coefs*0.9) #1.941=np.sum(fb_coefs*0.6)
        return 999 #if the correlation isn't big enough, do not return any command
    else:
        return result


if __name__=="__main__":
    
    start = time.time()
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

    listFreqs = [6.67, 7.5, 8.57, 10, 12]
    FS = samplingRate
    numSmpls = numSamplingPoints

    score = 0
    
    for i in range(numGroups):
        dataTemp = data[i]
        predClass = fbcca(dataTemp, listFreqs, FS)
        if predClass == np.mod(i,5)+1:
            score = score + 1
    rate = float(score)/float(numGroups)*100.0
    print('识别率为：',rate,'%')
    end = time.time()
    print('程序执行时间为：',end-start,'s')