# GetDataSSVEP

def GetDataset():
    import mne
    import numpy as np
    import matplotlib.pyplot as plt

    raw = mne.io.read_raw_brainvision('dataset/SSVEPEEGData/car2.vhdr')
    # 时间序列[...](number of sampling points x 1)
    # 信号序列[[...][...]...](64 x number of sampling points)
    # 每一个信号序列附一个时间序列
    # e.g raw[n] n通道信号序列[0]+时间序列[1]
    
    # 采样点数
    n_time_samps=raw.n_times
    # 时间
    time_secs=raw.times
    # 导路名称
    ch_names=raw.ch_names
    # 导路数量
    n_chan=len(ch_names)
    # 采样频率
    sampling_freq=raw.info['sfreq']
    data = raw.get_data()
    
    raw.plot()
    plt.show()
    
    
if __name__=='__main__':
    GetDataset()