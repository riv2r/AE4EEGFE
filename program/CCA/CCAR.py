import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import CCA
from DataProcess import DataProcess
import mne
import time
import scipy.io as scio


class CCAR(object):

    def __init__(self):

        self.freqs                  =[7.50,8.57,10.0,12.0]
        self.sampling_rate          =1000
        self.num_sampling_points    =5000

    def initialize(self):

        # set SSVEP stimuli frequencies
        self.freqs=input('Input Frequencies:')
        self.freqs=(self.freqs).split(',')
        self.freqs=[float(item) for item in self.freqs]
        # set sampling rate of hardware
        self.sampling_rate=input('Input Sampling Rate:')
        self.sampling_rate=float(self.sampling_rate)
        # set number of sampling points
        self.num_sampling_points=input('Input Number of Sampling Points:')
        self.num_sampling_points=float(self.num_sampling_points)

    def get_refer_signals(self,target_freq):

        # get reference signals
        refer_signals = []
        # number of harmonics
        nh=3
        fs=self.sampling_rate
        ns=self.num_sampling_points
        # stimulation frequency
        f=target_freq
        t=np.arange(0,ns/fs,step=1.0/fs)
        for i in range(1,nh+1):
            refer_signals.append(np.sin(2*np.pi*i*f*t))
            refer_signals.append(np.cos(2*np.pi*i*f*t))
        refer_signals=np.array(refer_signals)

        return refer_signals

    def find_corr(self,n_components,data,freq_set):

        # perform canonical correlation analysis (CCA)
        # freq_set - set of sinusoidal reference templates corresponding to the flicker frequency
        cca=CCA(n_components)
        corr=np.zeros(n_components) 
        rst=np.zeros((freq_set.shape)[0])
        for freq_idx in range((freq_set.shape)[0]):
            cca.fit(data.T,np.squeeze(freq_set[freq_idx,:,:]).T)
            x_train,y_train=cca.transform(data.T,np.squeeze(freq_set[freq_idx,:,:]).T)
            ind_val=0
            for ind_val in range(n_components):
                corr[ind_val]=np.corrcoef(x_train[:,ind_val],y_train[:,ind_val])[0,1]
            rst[freq_idx]=np.max(corr)

        return rst
    
    def process(self,data):

        freq_set=[]
        for freq in self.freqs:
            freq_temp=self.get_refer_signals(freq)
            freq_set.append(freq_temp)
        freq_set=np.array(freq_set)
        n_components=1
        rst=self.find_corr(n_components,data,freq_set)
        # print(rst)
        rst_max=max(rst,key=float)
        pred_class=np.argmax(rst)+1
        # print(pred_class)

        return pred_class


if __name__=='__main__':

    
    # real-time test
    ch_names=['POz','PO3','PO4','Oz','O1','O2']
    sfreq=1000
    ch_types=['eeg','eeg','eeg','eeg','eeg','eeg']
    info=mne.create_info(ch_names=ch_names,sfreq=sfreq,ch_types=ch_types)

    data_in_mat='dataset/data.mat'
    data=scio.loadmat(data_in_mat)['rst'][:9]
    idx=np.where(data[8,:]==255)
    data1=data[0:3,idx[0][0]:idx[0][1]]
    data2=data[5:8,idx[0][0]:idx[0][1]]
    data=np.vstack((data1,data2))

    raw=mne.io.RawArray(data,info)

    dataset=DataProcess()
    raw=dataset.preprocessing(raw)

    data=raw.get_data()
    fs=raw.info['sfreq']
    ns=data.shape[1]
    #-----CCAR-----#
    temp=CCAR()
    temp.sampling_rate=fs
    temp.num_sampling_points=ns
    
    pred_class=temp.process(data)
    print(pred_class)
    

    '''
    # offline test - wireless_data
    path='dataset/wireless_data/2022/10/221029-1/data.bdf'
    raw=mne.io.read_raw_bdf(path)

    picks=['POz','Oz','PO3','PO4','O1','O2']
    raw.pick_channels(picks)
    
    trigger_time=[12.131, 16.146,
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
    
    trigger_time=[13.017, 17.021,
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
    
    trigger_time=[13.231, 17.233,
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
    
    
    rst=[]
    for i in range(20):
        raw_temp=raw.copy().crop(trigger_time[2*i],trigger_time[2*i+1])

        dataset=DataProcess()    

        raw_temp=dataset.preprocessing(raw_temp)

        data=raw_temp.get_data()
        fs=raw_temp.info['sfreq']
        ns=data.shape[1]

        #-----CCAR-----#
        temp=CCAR()
        temp.sampling_rate=fs
        temp.num_sampling_points=ns
        
        pred_class=temp.process(data)
        rst.append(pred_class)

    print(rst)
    '''

    '''
    # offline test - wired_data
    start=time.time()
    path='dataset/wired_data/exp_1_data/1-1.vhdr'
    raw_origin=mne.io.read_raw_brainvision(path)
    picks=['IO','POz','Oz','PO3','PO4','O1','O2']
    raw_origin.pick_channels(picks)

    # by observation
    # exp_1_data: 12 9.5 9
    # exp_2_data: 10 12 14
    #             11 11 9
    #             20 16 6
    
    last_time=125
    st_time=12
    ed_time=st_time+last_time
    raw=raw_origin.crop(st_time,ed_time)

    dataset=DataProcess()

    raw=dataset.preprocessing(raw)
    raw=dataset.repair_EOG_by_ICA(raw)
    data,t,num_groups,num_chans,num_sampling_points,sampling_rate=dataset.get_epochs(raw)

    list_freqs=[6.67,7.50,8.57,10.0,12.0]
    fs=sampling_rate
    ns=num_sampling_points

    score=0
    
    for i in range(num_groups):
        data_temp=data[i]
        #-----CCAR-----#
        temp=CCAR()
        temp.freqs=list_freqs
        temp.sampling_rate=fs
        temp.num_sampling_points=ns
        
        pred_class=temp.process(data_temp)

        if pred_class == np.mod(i,5)+1:
            score=score+1
    rate=float(score)/float(num_groups)*100.0
    print('识别率:',rate,'%')
    end=time.time()
    print('程序执行时间为:',end-start,'s')
    '''
