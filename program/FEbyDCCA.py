import torch
from DatasetDCCA import GetDataset
from DeepCCA import DeepCCA
from LinearCCA import LinearCCA
from TrainDCCA import TrainDCCA
from sklearn.cross_decomposition import CCA
import numpy as np


if __name__ == '__main__':

    ##########
    # FEbyDCCA
    #        |——DatasetDCCA
    #        |——DeepCCA
    #        |——LinearCCA
    #        |——TrainDCCA
    ##########

    ##########
    # parameters initialize
    device = torch.device('cuda')
    # input size
    input1_size = 6
    input2_size = 8
    # output size
    output_size = 10
    # layers size
    numNodes = 784
    layer1_size = [input1_size,numNodes,numNodes,numNodes,output_size]
    layer2_size = [input2_size,numNodes,numNodes,numNodes,output_size]
    # training parameters
    learning_rate = 1e-3
    epoch_num = 50
    batch_size = 800
    # the regularization parameter
    # seems necessary to avoid the gradient exploding especially when non-saturating activations are used
    reg_para = 1e-5
    # specifies if all the singular values should get used to calculate the correlation or just output
    # if one option does not work for a network or dataset, try the other one
    use_all_singular_values = False
    # if a linear CCA should get applied on the learned features extracted from the networks
    apply_linear_cca = True
    ##########
    
    ##########
    # dataset
    dataset = GetDataset()
    dataX,dataY = dataset.getDataXY()
    # dataX 25 x 6 x 1250
    # dataY  5 x 8 x 1250
    dataXTemp = dataX[0]
    dataYTemp = dataY[0]
    X_train,X_val,X_test = dataset.splitDataXY(dataXTemp)
    Y_train,Y_val,Y_test = dataset.splitDataXY(dataYTemp)
    ##########
    
    ##########
    # DCCA
    model = DeepCCA(
        layer1_size,
        layer2_size,
        output_size,
        use_all_singular_values,
        device=device
    ).double()
    linear_cca = None
    if apply_linear_cca:
        linear_cca = LinearCCA()
    solver = TrainDCCA(
        model,
        output_size,
        linear_cca,
        epoch_num,
        batch_size,
        learning_rate,
        reg_para,
        device=device
    )
    solver.fit(
        X_train,
        Y_train,
        X_val,
        Y_val,
        X_test,
        Y_test
    )
    loss, output = solver.test(
        torch.tensor(dataXTemp.T),
        torch.tensor(dataYTemp.T),
        apply_linear_cca
    )
    ##########

    ##########
    # result
    n_components = 1
    # origin
    cca_origin = CCA(n_components)
    corr_temp = np.zeros(n_components) 
    cca_origin.fit(dataXTemp.T,dataYTemp.T)
    X_train_o,Y_train_o = cca_origin.transform(dataXTemp.T,dataYTemp.T)
    indVal = 0
    for indVal in range(n_components):
        corr_temp[indVal]=np.corrcoef(X_train_o[:,indVal],Y_train_o[:,indVal])[0,1]
    origin_corr = np.max(corr_temp)
    # now 
    cca_now = CCA(n_components)
    corr_temp = np.zeros(n_components) 
    cca_now.fit(output[0],output[1])
    X_train_n,Y_train_n = cca_now.transform(output[0],output[1])
    indVal = 0
    for indVal in range(n_components):
        corr_temp[indVal]=np.corrcoef(X_train_n[:,indVal],Y_train_n[:,indVal])[0,1]
    now_corr = np.max(corr_temp)

    print("CCA处理后的相关系数：",origin_corr)
    print("DeepCCA处理后的相关系数：",now_corr)
    ##########