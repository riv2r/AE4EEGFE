import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import CCA
from GetDataSSVEP import GetData
import mne
import time


class FEbyCCA(object):

    def __init__(self):

        self.freqs          =   [6.67,7.5,8.57,10.0,12.0]
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
        Nh=4
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
        rstMax=max(rst,key=float)
        predClass=np.argmax(rst)+1
        # print(predClass)

        return predClass


if __name__=='__main__':
    
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

    #-----FEbyCCA-----#
    temp = FEbyCCA()
    # temp.initialize()
    temp.samplingRate = samplingRate
    temp.numSamplingPoints = numSamplingPoints
    # print(temp.freqs)
    # print(temp.samplingRate)
    # print(temp.numSamplingPoints)
    score = 0
    for i in range(numGroups):
        datatemp = data[i]
        predClass = temp.process(datatemp)
        if predClass == np.mod(i,5)+1:
            score = score + 1
    rate = float(score)/float(numGroups)*100.0
    print('识别率为：',rate,'%')
    end = time.time()
    print('程序执行时间为：',end-start,'s')