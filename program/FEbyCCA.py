import numpy as np
from sklearn.cross_decomposition import CCA

class FEbyCCA(object):

    def __init__(self):
        self.freqs          =   [6.67,7.5,8.57,10.0,12.0]
        self.samplingRate   =   60
        self.numTargs       =   5

    def initialize(self):
        # Set SSVEP flicker frequencies
        self.freqs = input('Input Frequencies:')
        self.freqs = (self.freqs).split(',')
        self.freqs = [float(item) for item in self.freqs]
        # Set sampling rate of hardware
        self.samplingRate = input('Input Sampling Rate:')
        self.samplingRate = float(self.samplingRate)
        # Set number of SSVEP targets
        self.numTargs = input('Input Number of Targets:')
        self.numTargs = float(self.numTargs)

    def getReferSignals(self,numSamplingPoints,targFreq):
        # get reference signals
        referSignals = []
        # number of harmonics
        Nh=2
        fs=self.samplingRate
        # number of sampling points
        Ns=numSamplingPoints
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
        # get number of sampling points
        # NEED TO MODIFY
        numSamplingPoints = np.size(EEGDataset[0])
        freqSet=[]
        for freq in self.freqs:
            freqTemp=self.getReferSignals(numSamplingPoints,freq)
            freqSet.append(freqTemp)
        freqSet=np.array(freqSet)
        n_components=1
        rst=self.findCorr(n_components,EEGDataset,freqSet)
        rstMax=max(rst,key=float)
        predClass=np.argmax(rst)+1
        print(predClass)


temp = FEbyCCA()
# temp.initialize()
print(temp.freqs)
print(temp.samplingRate)
print(temp.numTargs)
referSignals=temp.getReferSignals(600,6.67)
print(referSignals)