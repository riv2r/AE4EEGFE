import numpy as np
from sklearn.cross_decomposition import CCA
import GetDataSSVEP
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

    def process(self,EEGDataset):
        freqSet=[]
        for freq in self.freqs:
            freqTemp=self.getReferSignals(freq)
            freqSet.append(freqTemp)
        freqSet=np.array(freqSet)
        n_components=1
        rst=self.findCorr(n_components,EEGDataset,freqSet)
        rstMax=max(rst,key=float)
        predClass=np.argmax(rst)+1
        # print(predClass)

        return predClass



if __name__=='__main__':
    
    start = time.time()
    path = 'dataset/SSVEPEEGData/car.vhdr'
    raw = mne.io.read_raw_brainvision(path)

    # By observation
    # 10.5 9 8
    last_time = 125
    st_time = 10.5
    ed_time = st_time+last_time
    raw = raw.crop(st_time,ed_time)

    dataset=GetDataSSVEP.GetDataset()    

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