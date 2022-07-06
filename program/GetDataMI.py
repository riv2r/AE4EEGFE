# GetDataMI
# Dataset:eeg-motor-movementimagery-dataset-1.0.0
# num1 实验人员序号
# num2 实验序号

def GetPath(num1,num2):
    # 109名实验人员
    # 4 8 12 是关于左右方向的运动想象EEG
    fampath='dataset/eeg-motor-movementimagery-dataset-1.0.0/files/'

    if num1<10:
        str1='S00'+str(num1)
    elif num1>=10 and num1<100:
        str1='S0'+str(num1)
    else:
        str1='S'+str(num1)
    if num2<10:
        str2='R0'+str(num2)
    else:
        str2='R'+str(num2)

    path=fampath+str1+'/'+str1+str2+'.edf'
    
    return path


def GetDataset(num1,num2):
    import mne
    import numpy as np

    path=GetPath(num1,num2)

    # avoid loading data in mem
    raw=mne.io.read_raw_edf(path,preload=False)
    
    events,event_id=mne.events_from_annotations(raw)
    # T0:1 rest T1:2 left T2:3 right
    # 时间序列[...](20000x1)
    # 信号序列[[...][...]...](64x20000)
    # 每一个信号序列附一个时间序列
    # e.g raw[n] n通道信号序列[0]+时间序列[1]
    length=np.size(raw[0][0])

    T0=np.zeros((64,1))
    T1=np.zeros((64,1))
    T2=np.zeros((64,1))

    for i in range(len(events)):
        if events[i,2]==1:
            start_num=events[i,0]
            if i+1==len(events):
                end_num=length
            else:
                end_num=events[i+1,0]
            T0=np.hstack((T0,raw[0:64][0][:,start_num:end_num]))
        elif events[i,2]==2:
            start_num=events[i,0]
            if i+1==len(events):
                end_num=length
            else:
                end_num=events[i+1,0]
            T1=np.hstack((T1,raw[0:64][0][:,start_num:end_num]))
        elif events[i,2]==3:
            start_num=events[i,0]
            if i+1==len(events):
                end_num=length
            else:
                end_num=events[i+1,0]
            T2=np.hstack((T2,raw[0:64][0][:,start_num:end_num]))
    #delete 初始列
    T0=np.delete(T0,0,axis=1)
    T1=np.delete(T1,0,axis=1)
    T2=np.delete(T2,0,axis=1)

    return T1,T2

if __name__=='__main__':
    GetDataset(1,12)