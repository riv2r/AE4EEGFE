import torch
from DatasetDCCA import GetDataset
from DeepCCA import DeepCCA
from LinearCCA import LinearCCA
from TrainDCCA import TrainDCCA

if __name__ == '__main__':
    ##########
    # parameters initialize

    device = torch.device('cuda')

    # input size
    input1_size = 6
    input2_size = 8
    
    # output size
    output_size = input1_size + input2_size

    # layers size
    layer1_size = [input1_size,48,48,48,output_size]
    layer2_size = [input2_size,48,48,48,output_size]

    # training parameters
    learning_rate = 1e-3
    epoch_num = 1000
    batch_size = 128

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
        X_test,
        Y_test,
        apply_linear_cca
    )
    ##########

    ##########
    # result contrast
    print(-loss)
    ##########