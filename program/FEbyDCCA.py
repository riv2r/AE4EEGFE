import torch
from DeepCCA import DeepCCA
from LinearCCA import LinearCCA

if __name__ == '__main__':
    #####
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
    epoch_num = 1
    batch_size = 16

    # the regularization parameter
    # seems necessary to avoid the gradient exploding especially when non-saturating activations are used
    reg_para = 1e-5

    # specifies if all the singular values should get used to calculate the correlation or just output
    # if one option does not work for a network or dataset, try the other one
    use_all_singular_values = False

    # if a linear CCA should get applied on the learned features extracted from the networks
    apply_linear_cca = True
    #####
    
    #####
    # dataset

    #####
    
    #####
    # DCCA
    model = DeepCCA(layer1_size, layer2_size, output_size, use_all_singular_values, device)
    linear_cca = None
    if apply_linear_cca:
        linear_cca = LinearCCA()
    #####