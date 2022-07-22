import numpy as np


class LinearCCA():

    def __init__(self):

        self.l_coeff = [None, None]
        self.mean = [None, None]

    def fit(self, H1, H2, output_size):

        # output_size means output date dimension
        r1 = 1e-4
        r2 = 1e-4
        # H1 and H2 are numpy arrays
        # H1 (numSamplingPoints,numChans) (1250,6)
        # H2 (numSamplingPoints,numHarmonics) (1250,8)
        m = H1.shape[0]
        o1 = H1.shape[1]
        o2 = H2.shape[1]
        self.mean[0] = np.mean(H1, axis=0)
        self.mean[1] = np.mean(H2, axis=0)
        H1bar = H1 - np.tile(self.mean[0], (m,1))
        H2bar = H2 - np.tile(self.mean[1], (m,1))
        sigmaH12 = (1.0/(m-1))*np.dot(H1bar.T,H2bar)
        sigmaH11 = (1.0/(m-1))*np.dot(H1bar.T,H1bar)+r1*np.identity(o1)
        sigmaH22 = (1.0/(m-1))*np.dot(H2bar.T,H2bar)+r2*np.identity(o2)
        [D1, V1] = np.linalg.eigh(sigmaH11)
        [D2, V2] = np.linalg.eigh(sigmaH22)
        sigmaH11Inv = np.dot(
            np.dot(
                V1, np.diag(D1 ** -0.5)
            ),
            V1.T
        )
        sigmaH22Inv = np.dot(
            np.dot(
                V2, np.diag(D2 ** -0.5)
            ),
            V2.T
        )
        Tval = np.dot(
            np.dot(sigmaH11Inv, sigmaH12),
            sigmaH22Inv
        )
        [U,D,V] = np.linalg.svd(Tval)
        V= V.T
        self.l_coeff[0] = np.dot(sigmaH11Inv, U[:, 0:output_size])
        self.l_coeff[1] = np.dot(sigmaH22Inv, V[:, 0:output_size])
        D = D[0:output_size]

    def _get_result(self,x,idx):

        rst = x - self.mean[idx].reshape(1,-1).repeat(len(x),axis=0)
        # X'=a^T·X
        # Y'=b^T·Y
        rst = np.dot(rst,self.l_coeff[idx])

        return rst
    
    def test(self,H1,H2):
        
        # output: 1-D data
        # shape like (n,1)

        return self._get_result(H1,0), self._get_result(H2,1)