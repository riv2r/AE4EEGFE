# Brain Computer Interface & Machine Vision

## 1 Brain Computer Interface

### 1 Definition

脑电信号一般振幅在 $\mu V$ 级，信噪比较低，是一种5-100 $\mu V$ 的低频生物电信号

### 2 论文调研

水文捞得不谈[脑机接口与机器视觉结合的机械臂共享控制研究](C:\Users\user\Desktop\BCI\脑机接口与机器视觉结合的机械臂共享控制研究_徐阳.caj)

1. 脑机接口的离线分析流程：

```mermaid
graph LR
A[信号采集]-->B[预处理]-->C[特征提取]-->D[模式识别]
```

2. 基于**运动想象**的BCI平台构建：

- 人体的运动和运动准备过程往往伴随着其对侧脑区 $\mu$ 节律和 $\beta$ 节律的能量下降，这一现象被称为**ERD**

- 在运动结束或大脑状态空闲时， $\mu$ 节律和 $\beta$ 节律的能量会重新上升，这一现象被称为**ERS**

  运动想象范式：左手、右手和双手运动的运动想象

3. EEG特征提取算法：共空间模式的空间滤波算法

4. **BrainAmp**进行信号采集，进行**离线分析**，训练完毕后的模型参数保存，供在线控制使用。后续进行实时采集和分析。

### 3 特征提取

#### 目的

从采集得到的EEG原始信号中提取出能够表达当前动作模式的特征信号，并抑制一些和当前模式无关的噪声信号，提高信号信噪比，提高BCI分类效果

[运动想象系统中的特征提取算法和分类算法](https://blog.51cto.com/u_6811786/3791770)：

- 时域方法：提取EEG的波形特征，比如振幅、方差、波峰等
- 频域方法：运动想象EEG信号的ERD和ERS现象只出现在特定的频率范围内，比如8-12Hz的 $\mu$ 波和18-26Hz的 $\beta$ 波。自回归功率谱分析法、双谱分析法等
- **空域方法**：运动想象领域比较通用的特征提取方法，主要通过设计空域滤波器对EEG的多通道空间分布进行处理，提取特征；共空间模式法(Common Spatial Pattern, CSP)、基于CSP的改进方法；时域分析开销较大，需要与较多脑电导联，应用较复杂
- 小波变换：噪声与信号频率接近时，信号失真严重

**自编码器(AE)**

线性判别分析(LDA)适用于线性信号，对于非线性脑电信号不理想；BP神经网络易收敛到局部最优；支持向量机(SVM)有监督网络，设置标签有点复杂。

### 4 EEG信号数据



交大BCMI实验室数据集

[脑电(EEG)等公开数据集汇总](https://zhuanlan.zhihu.com/p/138286382)

[EEG 公开数据集整理](https://zhuanlan.zhihu.com/p/377480885)
