# Control Scheme Based On Brain-Computer Interface Technology

## 1 [脑电波](https://baike.baidu.com/item/%E8%84%91%E7%94%B5%E6%B3%A2/1599805?fr=aladdin)

|名称|频率(Hz)|振幅($\mu$V)|活动|
|:-:|:-:|:-:|:-:|
|$\delta$|0.5~3|20~200|出现于：婴儿期或智力发育不成熟时、成年人的极度疲劳、昏睡或麻醉状态；可在颞叶和顶叶记录到这种波段|
|$\theta$|4~7|5~20|出现于：少年期(10-17岁)、成年人意愿受挫、抑郁或精神病患者|
|$\alpha$|8~13|20~100|出现于：正常人脑电波的基本节律，无外加刺激，其频率相当恒定。人在清醒、安静并闭眼时该节律最为明显，睁开眼睛(受到光刺激)或接受其它刺激时， $\alpha$ 即刻消失|
|$\beta$|14~30|100~150|出现于：精神紧张和情绪激动、亢奋状态|

脑电信号一般振幅在$\mu$V级，大致为50$\mu$V左右，超过$\pm$100$\mu$V，信噪比较低，是一种5~100$\mu$V的低频生物电信号，属于非线性非平稳信号。在信号收集的过程中易受到包括工频在内的周围电磁场辐射干扰和检测仪器内部电子噪声的干扰。

## 2 [脑机接口](https://zh.wikipedia.org/wiki/%E8%84%91%E6%9C%BA%E6%8E%A5%E5%8F%A3)

根据脑电波的信号特性，确定实验要求如下：
1. 电磁屏蔽室内最佳
2. 仪器接地并远离静电场和电磁场
3. 尽量保证实验环境安静、温度恒定、气压恒定、光照恒定

按照如下流程设计基于脑机接口技术的控制方案：
```mermaid
graph LR
A[诱发]-->B[信号采集]-->C[预处理]-->D[特征提取和分类]
```

## 3 诱发

目前常用的脑机接口范式有：
1. 稳态视觉诱发电位(Steady-State Visual Evoked Potentials, SSVEP)
2. 运动想象(Motor Imagery BCI, MI-BCI)
3. P300

采用SSVEP的视觉刺激器设计：当眼睛注视到4~60Hz的视觉刺激时，在大脑的枕叶区会产生与所注视的刺激**相同频率或倍频的EEG**，对应的通道为POz、Oz、PO3、PO4、O1、O2

设计如下所示闪烁刺激器(flicker stimulator)：
![flicker stimulator](https://github.com/riv2r/ControlByBCI/blob/master/rst/flicker_stimulator.png)
五个白色方块分别对应于：前、左、停、右、后
对应的频率分别为：6.67Hz、7.50Hz、8.57Hz、10.00Hz、12.00Hz

> 大脑分为:脑干、边缘系统、小脑和大脑皮层四个部分；脑叶分为**枕叶**、颞叶、顶叶和额叶，主要功能为：**枕叶：视觉感知和处理**；颞叶：语言功能和听觉感知，参与长期记忆和情感；顶叶：体感知觉、视觉和体空间信息的整合；额叶：思维、计划和中央执行职能，运动执行

## 4 信号采集

信号采集流程：
1. 正式采集前0.5s提示时间
2. 采样时间4s
3. 正式采集后0.5s空闲时间

要求受试者按照（前、左、停、右、后）的顺序，分别注视每个刺激块，受试者在闪烁刺激时尽量避免眨眼、眼动或是身动等其他行为。每个受试者进行**5**组实验

## 5 预处理

### 5.1 前处理

首先需要读取原始EEG数据：
![raw_origin](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_origin.png)

根据实验开始和结束时间，对原始EEG数据进行截取：
![raw_valid](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_valid.png)

脑电信号的前处理主要有以下几个步骤：
1. 降采样：对EEG进行一定程度的降采样，能降低后续运算处理负担，还能保留原本信号的特征，将1000Hz(硬件采样频率)降低到250Hz
![raw_downsampled](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_downsampled.png)
可见数据变得稀疏
2. 陷波处理：主要负责去除电源工频噪声干扰（50Hz左右）
![raw_notch](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_notch.png)
3. 带通滤波：关键在于去除EEG中的低频漂移现象，维持EEG信号的平稳性，采取2~100Hz进行带通滤波
![raw_filt](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_filt.png)
EEG中的非平稳波形变为了平稳波形

### 5.2 伪迹去除

伪迹分为生理伪迹和非生理伪迹，非生理伪迹通常来自外界环境的干扰，最常见的是电干扰。可以通过使用屏蔽电缆，选用电隔离室，让被试远离干扰源等减少影响。电机的不良放置也会产生非生理伪迹。应保证电极干净、导线和电极没有腐蚀、损坏。

生理伪迹来源于生物体本身，常见有：眨眼、眼动、舌动、心跳、呼吸、肌肉运动和汗腺兴奋等产生的电生理信号。

- **眼电伪迹**：幅度大、噪声频率范围宽。对头前部区域的影响显著。眼电是脑电信号的一种主要干扰噪声。为防止眼电伪迹的噪声频率对后续造成干扰，去除眼电伪迹是必不可少的预处理步骤。目前有效去除眼电伪迹的同时保留脑电信号的方法为**ICA**(Independent Component Analysis，独立成分分析)
- 肌电伪迹：呈尖峰状的高频电活动，主要产生于额肌和颞肌。
- 心电伪迹：会呈现出多种形式。选用不适当的参考电极可能会增加心电伪迹。将双侧耳作为参考电极可以有效地抑制心电干扰。
- 头皮出汗造成的伪迹：低频、低幅、呈波浪形的电信号。汗水引起的直流电信号可能会使基线不稳定，可能会导致相邻电极串联。

采用ICA算法去除EEG中的眼电伪迹
![raw_reconst](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_reconst.png)

因为EOG(眼电通道)为IO，该通道信号对后续特征提取和分类无作用，因此去掉该通道，得到最终的EEG信号
![raw-final](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_final.png)

由**信号采集**得知，一次实验由5次重复性实验组成，每次实验要求被试者注视(前、左、停、右、下)5个闪烁刺激，每次注视总时长为5s

因此，按照`duration=5`对上述EEG信号划分为25个片段
![epochs](https://github.com/riv2r/ControlByBCI/blob/master/rst/epochs.png)

### 5.3 通道提取

因为基于SSVEP的刺激主要集中于枕叶区，因此提取POz、Oz、PO3、PO4、O1、O2这6个通道，重新进行上述预处理，得到最终的EEG信号和片段
![raw_6](https://github.com/riv2r/ControlByBCI/blob/master/rst/raw_6.png)
![epochs_6](https://github.com/riv2r/ControlByBCI/blob/master/rst/epochs_6.png)


## 6 特征提取和分类

### 6.1 目的

从采集得到的EEG原始信号中提取出能够表达当前动作模式的特征信号，并抑制一些和当前模式无关的噪声信号，提高信号信噪比，提高BCI分类效果

> 基于SSVEP稳态视觉诱发电位的脑电信号处理算法有：快速傅里叶变换(FFT)、典型相关分析(CCA)、多导联同步指数(MSI)、最小能量结合(MEC)  

### 6.2 典型相关分析(CCA)

采用典型相关分析(CCA)，三次基于SSVEP的实验数据特征提取和分类结果如下：

第一次实验：

相关系数和识别结果

![1_rst_corr](https://github.com/riv2r/ControlByBCI/blob/master/rst/1_rst_corr.png)

准确率和识别时间

![1_acc_time](https://github.com/riv2r/ControlByBCI/blob/master/rst/1_acc_time.png)

第二次实验：

相关系数和识别结果

![2_rst_corr](https://github.com/riv2r/ControlByBCI/blob/master/rst/2_rst_corr.png)

准确率和识别时间

![2_acc_time](https://github.com/riv2r/ControlByBCI/blob/master/rst/2_acc_time.png)

第三次实验：

相关系数和识别结果

![3_rst_corr](https://github.com/riv2r/ControlByBCI/blob/master/rst/3_rst_corr.png)

准确率和识别时间

![3_acc_time](https://github.com/riv2r/ControlByBCI/blob/master/rst/3_acc_time.png)

其中，单条指令的识别时间在1s上下

CCA算法仍存在以下问题：
1. 相位漂移问题：不同受试者对相同视觉刺激具有不同的反应时滞，产生EEG的相位漂移问题。存在相位漂移问题时，数据训练往往会产生较大的偏差；
2. CCA主要用于线性信号的处理，而EEG为非线性信号。在CCA的相关实验中，假设EEG为刺激频率的线性输出，但实际混杂了部分环境噪声及伪迹；
3. CCA在2s以上的长时间片中的表现极为优秀，但因为其未考虑EEG非线性的特性，在1s以内短时间片处理时仍存在不足之处。

### 6.3 深度典型相关分析(Deep CCA)

### 6.4 深度典型相关自编码器(Deep Canonical Correlated Autoencoders)

## A 论文及相关技术调研

1. [运动想象系统中的特征提取算法和分类算法](https://blog.51cto.com/u_6811786/3791770)

- 时域方法：提取EEG的波形特征，比如振幅、方差、波峰等
- 频域方法：运动想象EEG信号的ERD和ERS现象只出现在特定的频率范围内，比如8-12Hz的$\mu$波和18-26Hz的$\beta$波。自回归功率谱分析法、双谱分析法等
- **空域方法**：运动想象领域比较通用的特征提取方法，主要通过设计空域滤波器对EEG的多通道空间分布进行处理，提取特征；共空间模式法(Common Spatial Pattern, CSP)、基于CSP的改进方法；时域分析开销较大，需要与较多脑电导联，应用较复杂
- 小波变换：噪声与信号频率接近时，信号失真严重

2. [基于稳态视觉诱发电位的脑电控制上肢康复机器人](paper/基于SSVEP的BCI系统设计/基于稳态视觉诱发电位的脑电控制上肢康复机器人_熊特.pdf)

3种主流的刺激显示装置：LED、CRT、LCD

选择分辨率为1920x1080的LCD液晶显示屏为视觉刺激器，屏幕刷新频率为60Hz。

为保证刺激频率的准确性和避免SSVEP倍频成分之间的干扰，设计5个刺激频率为6.67(1/9)、8.57(1/7)、10(1/6)、12(1/5)、15(1/4)Hz，刺激频率均为60Hz的整数分之一，分别对应于5个控制指令（前、后、左、右、停）

设计工具：Pscyhtoolbox-3 based on MATLAB

## B EEG信号数据

上海交通大学BCMI实验室数据集

[脑电(EEG)等公开数据集汇总](https://zhuanlan.zhihu.com/p/138286382)

[EEG 公开数据集整理](https://zhuanlan.zhihu.com/p/377480885)
