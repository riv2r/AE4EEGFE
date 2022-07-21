import torch
import torch.nn as nn

class MlpNet(nn.Module):

    def __init__(self,layer_size,device=torch.device('cpu')):
        super().__init__()
        self.device = device
        layers=[]
        for lIdx in range(len(layer_size)-1):
            if lIdx == len(layer_size)-2:
                layers.append(
                    nn.Sequential(
                        nn.Linear(layer_size[lIdx],layer_size[lIdx+1])
                    )
                )
            else:
                layers.append(
                    nn.Sequential(
                        nn.Linear(layer_size[lIdx],layer_size[lIdx+1]),
                        nn.ReLU(),
                        nn.BatchNorm1d(num_features = layer_size[lIdx+1],affine=False)
                    )
                )
        self.layers = nn.ModuleList(layers)
    
    def forward(self,x):
        # forward propagation function
        for layer in self.layers:
            # avoid this compute part be moved on CPU
            x = x.to(self.device)
            layer = layer.to(self.device)
            x = layer(x)
        return x


class CCALoss():
    
    def __init__(self,output_size,use_all_singular_values,device):
        self.output_size = output_size
        self.use_all_singular_values = use_all_singular_values
        self.device = device
    
    def loss(self,H1,H2):
        r1 = 1e-3
        r2 = 1e-3
        eps = 1e-9
        # H1 and H2 are tensors
        # H1 (numSamplingPoints,numChans) (1250,6)
        # H2 (numSamplingPoints,numHarmonics) (1250,8)
        H1, H2 =H1.t(), H2.t()
        # H1 (6,1250)
        # H2 (8,1250)

        o1 = H1.size(0)
        o2 = H2.size(0)
        m = H1.size(1)

        # centered data
        # H.mean(dim=1) compute row's mean
        H1bar = H1 - H1.mean(dim=1).unsqueeze(dim=1)
        H2bar = H2 - H2.mean(dim=1).unsqueeze(dim=1)

        sigmaH12 = (1.0/(m-1))*torch.matmul(H1bar,H2bar.t())
        sigmaH11 = (1.0/(m-1))*torch.matmul(H1bar,H1bar.t())+r1*torch.eye(o1,device=self.device)
        sigmaH22 = (1.0/(m-1))*torch.matmul(H2bar,H2bar.t())+r2*torch.eye(o2,device=self.device)

        # Eigenvalue Decomposition
        [D1,V1]=torch.symeig(sigmaH11,eigenvectors=True)
        [D2,V2]=torch.symeig(sigmaH22,eigenvectors=True)
        # increase stability
        # gt(a,b) get indexs point to a > b
        posIdx1 = torch.gt(D1,eps).nonzero()[:,0]
        D1 = D1[posIdx1]
        V1 = V1[:,posIdx1]
        posIdx2 = torch.gt(D2,eps).nonzero()[:,0]
        D2 = D2[posIdx2]
        V2 = V2[:,posIdx2]

        sigmaH11Inv = torch.matmul(
            torch.matmul(V1, torch.diag(D1 ** -0.5)),
            V1.t()
        )
        sigmaH22Inv = torch.matmul(
            torch.matmul(V2, torch.diag(D2 ** -0.5)),
            V2.t()
        )

        Tval = torch.matmul(
            torch.matmul(sigmaH11Inv,sigmaH12),
            sigmaH22Inv
        )

        if self.use_all_singular_values:
            temp = torch.matmul(Tval.t(),Tval)
            corr = torch.sqrt(torch.trace(temp))
        else:
            trace_TT = torch.matmul(Tval.t(),Tval)
            trace_TT = torch.add(trace_TT, (torch.eye(trace_TT.size(0))*r1).to(self.device))
            U, V = torch.symeig(trace_TT, eigenvectors=True)
            U = torch.where(U>eps, U, (torch.ones(U.size()).double()*eps).to(self.device))
            U = U.topk(self.output_size)[0]
            corr = torch.sum(torch.sqrt(U))

        return -corr


class DeepCCA(nn.Module):

    def __init__(self,layer1_size,layer2_size,output_size,use_all_singular_values,device=torch.device('cpu')):
        super().__init__()
        self.model1 = MlpNet(layer1_size,device).double()
        self.model2 = MlpNet(layer2_size,device).double()
        
        self.loss = CCALoss(output_size,use_all_singular_values,device).loss
        
    def forward(self,x1,x2):
        output1 = self.model1(x1)
        output2 = self.model2(x2)

        return output1,output2