import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import CCA
from GetDataSSVEP import GetData
import mne
import time
import scipy.io as scio


class FEbyCCA(object):

    def __init__(self):

        self.freqs          =   [7.5,8.57,10.0,12.0]
        self.samplingRate   =   1000
        self.numSamplingPoints = 5000

    def initialize(self):

        # Set SSVEP flicker frequencies
        self.freqs = input('Input Frequencies:')
        self.freqs = (self.freqs).split(',')
        self.freqs = [float(item) for item in self.freqs]
        # Set sampling rate of hardware
        self.samplingRate = input('Input Sampling Rate:')
        self.samplingRate = float(self.samplingRate)
        # Set number of sampling points
        self.numSamplingPoints = input('Input Number of Sampling Points:')
        self.numSamplingPoints = float(self.numSamplingPoints)

    def getReferSignals(self,targFreq):

        # get reference signals
        referSignals = []
        # number of harmonics
        Nh=3
        fs=self.samplingRate
        Ns=self.numSamplingPoints
        # stimulation frequency
        f=targFreq
        t=np.arange(0,Ns/fs,step=1.0/fs)
        for i in range(1,Nh+1):
            referSignals.append(np.sin(2*np.pi*i*f*t))
            referSignals.append(np.cos(2*np.pi*i*f*t))
        referSignals=np.array(referSignals)

        return referSignals

    def findCorr(self,n_components,EEGDataset,freqSet):

        # Perform Canonical Correlation Analysis (CCA)
        # freqSet - set of sinusoidal reference templates corresponding to the flicker frequency
        cca = CCA(n_components)
        corr = np.zeros(n_components) 
        rst = np.zeros((freqSet.shape)[0])
        for freqIdx in range((freqSet.shape)[0]):
            cca.fit(EEGDataset.T,np.squeeze(freqSet[freqIdx,:,:]).T)
            X_train,Y_train = cca.transform(EEGDataset.T,np.squeeze(freqSet[freqIdx,:,:]).T)
            indVal = 0
            for indVal in range(n_components):
                corr[indVal]=np.corrcoef(X_train[:,indVal],Y_train[:,indVal])[0,1]
            rst[freqIdx]=np.max(corr)

        return rst
    
    '''
    # try MSI method
    def findS(self,EEGDataset,freqSet):
        X = EEGDataset
        M = self.numSamplingPoints
        for freqIdx in range((freqSet.shape)[0]):
            Y = freqSet[freqIdx,:,:]
            corrMat11 = 1/M*np.dot(X,X.T)
            corrMat11[np.isnan(corrMat11)] = 0
            corrMat12 = 1/M*np.dot(X,Y.T)
            corrMat12[np.isnan(corrMat12)] = 0
            corrMat21 = 1/M*np.dot(Y,X.T)
            corrMat21[np.isnan(corrMat21)] = 0
            corrMat22 = 1/M*np.dot(Y,Y.T)
            corrMat22[np.isnan(corrMat22)] = 0
            corrMat = np.append(
                np.append(corrMat11,corrMat12,axis=1),
                np.append(corrMat21,corrMat22,axis=1),
                axis=0
                )
            
            corrMat11n = np.sqrt(1./corrMat11)
            corrMat11n[np.isnan(corrMat11n)] = 0
            corrMat12n = np.sqrt(1./corrMat12)
            corrMat12n[np.isnan(corrMat12n)] = 0
            corrMat21n = np.sqrt(1./corrMat21)
            corrMat21n[np.isnan(corrMat21n)] = 0
            corrMat22n = np.sqrt(1./corrMat22)
            corrMat22n[np.isnan(corrMat22n)] = 0

            UMat = np.append(
                np.append(corrMat11n,np.zeros((corrMat11n.shape[0],corrMat22n.shape[1])),axis=1),
                np.append(np.zeros((corrMat22n.shape[0],corrMat11n.shape[1])),corrMat22n,axis=1),
                axis=0
                )

            RMat11 = np.identity(6)
            RMat12 = np.dot(np.dot(corrMat11n,corrMat12),corrMat22n)
            RMat21 = np.dot(np.dot(corrMat22n,corrMat21),corrMat11n)
            RMat22 = np.identity(8)
            
            RMat = np.append(
                np.append(RMat11,RMat12,axis=1),
                np.append(RMat21,RMat22,axis=1),
                axis=0
            )

            phi = np.linalg.eig(RMat)[0] 
            phiBar = phi/np.trace(RMat)

            temp = 0
            for i in range(0,14):
                temp = phiBar[i]*np.log(phiBar[i])
            
            SParam = 1 + temp/np.log(14)
            print(SParam)
        '''
    
    def process(self,EEGDataset):

        freqSet=[]
        for freq in self.freqs:
            freqTemp=self.getReferSignals(freq)
            freqSet.append(freqTemp)
        freqSet=np.array(freqSet)
        n_components=1
        # self.findS(EEGDataset,freqSet)
        rst=self.findCorr(n_components,EEGDataset,freqSet)
        # print(rst)
        rstMax=max(rst,key=float)
        predClass=np.argmax(rst)+1
        # print(predClass)

        return predClass


if __name__=='__main__':

    # Real-Time Test
    ch_names = ['POz','PO3','PO4','Oz','O1','O2']
    sfreq = 1000
    ch_types = ['eeg', 'eeg', 'eeg', 'eeg', 'eeg', 'eeg']
    info = mne.create_info(ch_names = ch_names, sfreq = sfreq, ch_types = ch_types)

    data_in_mat = 'C:/Users/user/Desktop/ControlByBCI/dataset/data.mat'
    data = scio.loadmat(data_in_mat)['rst'][:9]
    idx = np.where(data[8,:]==255)[0][0]
    data1 = data[0:3,idx-4*sfreq:idx]
    data2 = data[5:8,idx-4*sfreq:idx]
    data = np.vstack((data1,data2))

    raw = mne.io.RawArray(data,info)

    dataset=GetData()
    raw=dataset.preProcessing(raw)

    data = raw.get_data()
    FS = raw.info['sfreq']
    numSmpls = data.shape[1]
    #-----FEbyCCA-----#
    temp = FEbyCCA()
    temp.samplingRate = FS
    temp.numSamplingPoints = numSmpls
    
    predClass = temp.process(data)
    print(predClass)

    '''
    # Offline Test
    path = 'C:/Program Files (x86)/Neuracle/Neusen W/Data/2022/10/221029-1/data.bdf'
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
    
    rst = []
    for i in range(20):
        raw_temp = raw.copy().crop(trigger_time[2*i],trigger_time[2*i+1])

        dataset=GetData()    

        raw_temp=dataset.preProcessing(raw_temp)

        data = raw_temp.get_data()
        FS = raw_temp.info['sfreq']
        numSmpls = data.shape[1]

        #-----FEbyCCA-----#
        temp = FEbyCCA()
        temp.samplingRate = FS
        temp.numSamplingPoints = numSmpls
        
        predClass = temp.process(data)
        rst.append(predClass)

    print(rst)

    # SSVEP_BCI_DATA epochs by observation
    # SSVEP_BCI_DATA_1: 12 9.5 9
    # SSVEP_BCI_DATA_2: 10 12 14
    #                   11 11 9
    #                   20 16 6
    '''
