import mne
from GetDataSSVEP import GetData
from sklearn.cross_decomposition import CCA
from filterbank import filterbank
from scipy.stats import pearsonr
import numpy as np
import time
import scipy.io as scio
import serial

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

def fbcca(eeg, list_freqs, fs, num_harms=4, num_fbs=20):
    
    fb_coefs = np.power(np.arange(1,num_fbs+1),(-1.25)) + 0.25
    num_targs = 4
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

def cca_reference(list_freqs, fs, num_smpls, num_harms=4):
    
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
    
    # Real-Time Test
    
    ch_names = ['POz','Oz','PO3','PO4','O1','O2']
    sfreq = 1000
    ch_types = ['eeg', 'eeg', 'eeg', 'eeg', 'eeg', 'eeg']
    info = mne.create_info(ch_names = ch_names, sfreq = sfreq, ch_types = ch_types)

    data_in_mat = 'C:/Users/user/Desktop/ControlByBCI/dataset/data.mat'
    data = scio.loadmat(data_in_mat)['rst'][:9]
    idx = np.where(data[8,:]==255)
    data1 = data[0:3,idx[0][0]:idx[0][1]]
    data2 = data[5:8,idx[0][0]:idx[0][1]]
    data = np.vstack((data1,data2))

    raw = mne.io.RawArray(data,info)

    dataset=GetData()    

    raw=dataset.preProcessing(raw)

    data = raw.get_data()
    
    listFreqs = [7.5, 8.57, 10.0, 12.0]
    FS = raw.info['sfreq']
    numSmpls = data.shape[1]
    
    predClass = fbcca(data, listFreqs, FS)
    print(predClass)
    
    
    predClass = predClass +48;
    # 连接串口
    serial = serial.Serial('COM9',115200,timeout=2)

    if serial.isOpen():

        print ('串口已打开')
        
        # ASCII码对应指令
        # 49 50 51 52
        # 1  2  3  4
        # 前 左 右 后

        data = (chr(predClass)+'\r\n').encode()# 发送的数据
        serial.write(data)# 串口写数据
     
        while True:
            data = serial.read(100)# 串口读20位数据
            if data != b'':
                break
        print(data)
            
    else:
        print ('串口未打开')
    
     
     
    # 关闭串口
    serial.close()
     
    if serial.isOpen():
        print ('串口未关闭')
    else:
        print ('串口已关闭')
    
    
    
    '''
    # Offline Test
    path = 'C:/Program Files (x86)/Neuracle/Neusen W/Data/2022/10/221029-3/data.bdf'
    raw = mne.io.read_raw_bdf(path)

    picks = ['POz','Oz','PO3','PO4','O1','O2']
    raw.pick_channels(picks)
    
    trigger_time = [12.131, 16.146,
                    18.167, 22.177,
                    24.198, 28.209,
                    30.230, 34.240,
                    36.262, 40.272,
                    42.292, 46.303,
                    48.324, 52.335,
                    54.354, 58.366,
                    60.386, 64.397,
                    66.418, 70.428,
                    72.449, 76.460,
                    78.480, 82.491,
                    84.511, 88.524,
                    90.543, 94.555,
                    96.575, 100.586,
                    102.606, 106.617,
                    108.637, 112.648,
                    114.669, 118.680,
                    120.700, 124.711,
                    126.732, 130.743]
    
    trigger_time = [13.017, 17.021,
                    19.042, 23.053,
                    25.072, 29.084,
                    31.104, 35.115,
                    37.137, 41.147,
                    43.167, 47.179,
                    49.199, 53.210,
                    55.230, 59.241,
                    61.261, 65.274,
                    67.293, 71.304,
                    73.324, 77.335,
                    79.355, 83.366,
                    85.387, 89.399,
                    91.418, 95.430,
                    97.450, 101.461,
                    103.482, 107.493,
                    109.512, 113.524,
                    115.544, 119.555,
                    121.575, 125.587,
                    127.607, 131.618]
             
    trigger_time = [13.231, 17.233,
                    19.253, 23.265,
                    25.286, 29.297,
                    31.316, 35.328,
                    37.351, 41.359,
                    43.380, 47.392,
                    49.411, 53.422,
                    55.445, 59.454,
                    61.474, 65.485,
                    67.505, 71.516,
                    73.537, 77.548,
                    79.568, 83.580,
                    85.599, 89.610,
                    91.630, 95.642,
                    97.663, 101.673,
                    103.693, 107.705,
                    109.724, 113.736,
                    115.756, 119.768,
                    121.789, 125.799,
                    127.819, 131.831]
                
    rst = []
    rst_mat = np.array([0,0,0,0])
    for i in range(20):
        raw_temp = raw.copy().crop(trigger_time[2*i],trigger_time[2*i+1])
        print(raw_temp)

        dataset=GetData()    

        raw_temp=dataset.preProcessing(raw_temp)

        data = raw_temp.get_data()
        listFreqs = [7.5, 8.57, 10.0, 12.0]
        FS = raw_temp.info['sfreq']
        numSmpls = data.shape[1]

        predClass, mat = fbcca(data, listFreqs, FS)
        rst.append(predClass)
        rst_mat = np.vstack((rst_mat, mat))

    print(rst)
    rst_mat = rst_mat[1:]
    print(rst_mat)
    '''
    
    '''
    start = time.time()
    path = 'dataset/SSVEP_BCI_DATA_1/1-3.vhdr'
    raw_origin = mne.io.read_raw_brainvision(path)
    picks = ['IO','POz','Oz','PO3','PO4','O1','O2']
    raw_origin.pick_channels(picks)

    # By observation
    # SSVEP_BCI_DATA_1: 12 9.5 9
    # SSVEP_BCI_DATA_2: 10 12 14
    #                   11 11 9
    #                   20 16 6
    
    last_time = 125
    st_time = 9
    ed_time = st_time+last_time
    raw = raw_origin.crop(st_time,ed_time)

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
    '''
