import torch
from DeepCCA import DeepCCA
from LinearCCA import LinearCCA
from TrainDCCA import TrainDCCA
from DatasetDCCA import GetDataset

if __name__ == '__main__':
    ##########
    # parameters initialize

    device = torch.device('cuda')

    # output size
    output_size = 2

    # input size
    input1_size = 6
    input2_size = 8

    # layers size
    layer1_size = [input1_size,24,24,24,output_size]
    layer2_size = [input2_size,24,24,24,output_size]

    # training parameters
    learning_rate = 1e-3
    epoch_num = 5
    batch_size = 16

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
    X_train,X_val,X_test = dataset.splitDataXY(dataX[0])
    Y_train,Y_val,Y_test = dataset.splitDataXY(dataY[0,:,:])
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
        linear_cca,
        output_size,
        learning_rate,
        epoch_num,
        batch_size,
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
        torch.cat([X_train,X_val,X_test],dim=0),
        torch.cat([Y_train,Y_val,Y_test],dim=0),
        apply_linear_cca
    )
    ##########