import mne
import warnings
import numpy as np
import scipy.signal
import scipy.io as scio
from scipy.stats import pearsonr
from sklearn.cross_decomposition import CCA

from DataProcess import DataProcess


class IntentRec(object):

    def __init__(self):

        self.freqs                  =[8,9,10,11,12,13]
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

    def get_refer_signals(self,nh=3):

        refer_signals=[]
        fs=self.sampling_rate
        ns=self.num_sampling_points
        t=np.arange(0,ns/fs,step=1.0/fs)
        for freq in self.freqs:
            temp=[]
            for i in range(1,nh+1):
                temp.append(np.sin(2*np.pi*i*freq*t))
                temp.append(np.cos(2*np.pi*i*freq*t))
            refer_signals.append(temp)
        refer_signals=np.array(refer_signals)

        return refer_signals

    def find_corr(self,n_components,data,refer_signals):

        # perform canonical correlation analysis (CCA)
        # freq_set - set of sinusoidal reference templates corresponding to the flicker frequency
        cca=CCA(n_components)
        corr=np.zeros(n_components) 
        rst=np.zeros((refer_signals.shape)[0])
        for freq_idx in range((refer_signals.shape)[0]):
            cca.fit(data.T,np.squeeze(refer_signals[freq_idx,:,:]).T)
            x_train,y_train=cca.transform(data.T,np.squeeze(refer_signals[freq_idx,:,:]).T)
            ind_val=0
            for ind_val in range(n_components):
                corr[ind_val]=np.corrcoef(x_train[:,ind_val],y_train[:,ind_val])[0,1]
            rst[freq_idx]=np.max(corr)

        return rst
    
    def cca_process(self,n_components,data,nh=3):

        refer_signals=self.get_refer_signals(nh)
        rst=self.find_corr(n_components,data,refer_signals)
        # print(rst)
        rst_max=max(rst,key=float)
        pred_class=np.argmax(rst)
        # print(pred_class)

        return pred_class
    
    def filterbank(self,data,idx_fb):
        if idx_fb == None:
            warnings.warn('stats:filterbank:MissingInput '\
                        +'Missing filter index. Default value (idx_fb = 0) will be used.')
            idx_fb = 0
        elif (idx_fb < 0 or 20 < idx_fb):
            raise ValueError('stats:filterbank:InvalidInput '\
                            +'The number of sub-bands must be 0 <= idx_fb <= 9.')
            
        if (len(data.shape)==2):
            num_chans = data.shape[0]
            num_trials = 1
        else:
            num_chans, _, num_trials = data.shape
    
        # Nyquist Frequency = Fs/2N
        fs = self.sampling_rate
        Nq = fs/2
    
        passband = np.arange(9,89,4)
        stopband = np.arange(8,88,4)
        Wp = [passband[idx_fb]/Nq, 90/Nq]
        Ws = [stopband[idx_fb]/Nq, 100/Nq]
        [N, Wn] = scipy.signal.cheb1ord(Wp, Ws, 3, 40) # band pass filter StopBand=[Ws(1)~Ws(2)] PassBand=[Wp(1)~Wp(2)]
        [B, A] = scipy.signal.cheby1(N, 0.5, Wn, 'bandpass') # Wn passband edge frequency
    
        y = np.zeros(data.shape)
        if (num_trials == 1):
            for ch_i in range(num_chans):
                #apply filter, zero phass filtering by applying a linear filter twice, once forward and once backwards.
                # to match matlab result we need to change padding length
                y[ch_i, :] = scipy.signal.filtfilt(B, A, data[ch_i, :], padtype = 'odd', padlen=3*(max(len(B),len(A))-1))
        
        else:
            for trial_i in range(num_trials):
                for ch_i in range(num_chans):
                    y[ch_i, :, trial_i] = scipy.signal.filtfilt(B, A, data[ch_i, :, trial_i], padtype = 'odd', padlen=3*(max(len(B),len(A))-1))
           
        return y

    def fbcca_process(self,n_components,data,nh=3,nfbs=5):
        
        fb_coefs=np.power(np.arange(1,nfbs+1),-1.25)+0.25

        num_targs=len(self.freqs)
        num_chans,num_smpls=data.shape
        y_ref=self.get_refer_signals(nh)
        cca=CCA(n_components)

        r=np.zeros((nfbs,num_targs))

        test_tmp = np.squeeze(data)  #deal with one target a time
        for fb_i in range(nfbs):  #filter bank number, deal with different filter bank
             testdata = self.filterbank(test_tmp, fb_i)  #data after filtering
             for class_i in range(num_targs):
                 refdata = np.squeeze(y_ref[class_i, :, :])   #pick corresponding freq target reference signal
                 test_C, ref_C = cca.fit_transform(testdata.T, refdata.T)
                 # len(row) = len(observation), len(column) = variables of each observation
                 # number of rows should be the same, so need transpose here
                 # output is the highest correlation linear combination of two sets
                 r_tmp, _ = pearsonr(np.squeeze(test_C), np.squeeze(ref_C)) #return r and p_value, use np.squeeze to adapt the API 
                 r[fb_i, class_i] = r_tmp
                 
        rho = np.dot(fb_coefs, r)  #weighted sum of r from all different filter banks' result
        tau = np.argmax(rho)  #get maximum from the target as the final predict (get the index)
        result = tau #index indicate the maximum(most possible) target
        return result

def methodCCA(data):
    data=np.array(data).T
    fs=250
    ns=data.shape[1]
    #-----CCA-----#
    method=IntentRec()
    method.sampling_rate=fs
    method.num_sampling_points=ns
    
    pred_class=method.cca_process(1,data,3)
    return pred_class


if __name__=='__main__':
    '''
    # Real-Time EXPT. based on MATLAB
    ch_names=['POz','PO3','PO4','PO5','PO6','Oz','O1','O2']
    sfreq=250
    ch_types=['eeg','eeg','eeg','eeg','eeg','eeg','eeg','eeg']
    info=mne.create_info(ch_names=ch_names,sfreq=sfreq,ch_types=ch_types)

    data_in_mat='dataset/data.mat'
    data=scio.loadmat(data_in_mat)['rst']
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
    
    ir=IntentRec()
    ir.freqs=[7.5,8.57,10,12]
    ir.sampling_rate=fs
    ir.num_sampling_points=ns
    
    pred_class=ir.cca_process(1,data,3)
    print(pred_class)
    '''


    '''
    # Offline EXPT. based on Tsinghua data
    data_in_mat='dataset/S001-S010/S005.mat'
    # 8 channels;710 points(0.5s->2s->0.14s->0.2s);dry/wet;10 exps;12 freqs 
    data=scio.loadmat(data_in_mat)['data']
    ir=IntentRec()
    ir.freqs=[9.25,11.25,13.25]
    ir.sampling_rate=250
    ir.num_sampling_points=500

    for i in range(3):
        ans1=0
        ans2=0
        for j in range(10):
            cur=data[:,125:625,1,j,i]
            pred_class1=ir.cca_process(1,cur,3)
            pred_class2=ir.fbcca_process(1,cur,5,20)
            if(pred_class1==i):
                ans1+=1
            if(pred_class2==i):
                ans2+=1
        print(str(ans1*10)+'%'+' '+str(ans2*10)+'%')
    '''


    '''
    # Offline EXPT. based on wireless devices
    path='dataset/wireless_data/2022/10/221029-1/data.bdf'
    raw=mne.io.read_raw_bdf(path)

    picks=['POz','PO3','PO4','Oz','O1','O2']
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
    
    ir=IntentRec()
    ir.freqs=[7.5,8.57,10,12]

    for i in range(20):
        raw_temp=raw.copy().crop(trigger_time[2*i],trigger_time[2*i+1])

        dataset=DataProcess()
        raw_temp=dataset.preprocessing(raw_temp)

        data=raw_temp.get_data()
        fs=raw_temp.info['sfreq']
        ns=data.shape[1]

        ir.sampling_rate=fs
        ir.num_sampling_points=ns

        pred_class=ir.cca_process(1,data,3)
        rst.append(pred_class)

    print(rst)
    '''

    
    '''
    # Offline EXPT. based on wired devices
    path='dataset/wired_data/exp_1_data/1-1.vhdr'
    raw_origin=mne.io.read_raw_brainvision(path)
    picks=['IO','POz','PO3','PO4','Oz','O1','O2']
    raw_origin.pick_channels(picks)

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
    
    ir=IntentRec()
    ir.freqs=list_freqs
    ir.sampling_rate=fs
    ir.num_sampling_points=ns

    for i in range(num_groups):
        data_temp=data[i]
        
        pred_class=ir.cca_process(1,data_temp,3)
        print(pred_class)

        if pred_class == np.mod(i,5):
            score=score+1

    rate=float(score)/float(num_groups)*100.0
    print('识别率:',rate,'%')
    '''