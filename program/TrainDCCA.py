import torch
import logging
import time
from torch.utils.data import BatchSampler, RandomSampler
import numpy as np

class TrainDCCA():

    def __init__(self,model,linear_cca,output_size,learning_rate,epoch_num,batch_size,reg_par,device):
        self.model = model
        self.model.to(device)
        # epoch_num: The number of times to traverse the training set
        self.epoch_num = epoch_num
        self.batch_size = batch_size
        self.loss = model.loss
        # optimizer
        self.optimizer = torch.optim.RMSprop(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=reg_par
        )
        self.device =device
        self.linear_cca = linear_cca
        self.output_size = output_size

        formatter = logging.Formatter(
            "[ %(levelname)s : %(asctime)s ] - %(message)s"
        )
        logging.basicConfig(
            level=logging.DEBUG,
            format="[ %(levelname)s : %(asctime)s ] - %(message)s"
        )
        self.logger = logging.getLogger("PyTorch")
        filehandler = logging.FileHandler("DCCA.log")
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)

        self.logger.info(self.model)
        self.logger.info(self.optimizer)

    def fit(self,x1,x2,vx1=None,vx2=None,tx1=None,tx2=None,checkpoint='checkpoint.model'):

        x1.to(self.device)
        x2.to(self.device)
        
        data_size = x1.size(0)
        
        if vx1 is not None and vx2 is not None:
            best_val_loss = 0
            vx1.to(self.device)
            vx2.to(self.device)
        if tx1 is not None and tx2 is not None:
            tx1.to(self.device)
            tx2.to(self.device)
        
        train_losses = []
        for epoch in range(self.epoch_num):
            epoch_start_time = time.time()
            self.model.train()
            batch_idxs = list(
                BatchSampler(
                    RandomSampler(
                        range(data_size)
                    ),
                    batch_size=self.batch_size,
                    drop_last=False
                )
            )
            for batch_idx in batch_idxs:
                # gradient set to 0
                self.optimizer.zero_grad()
                batch_x1 = x1[batch_idx,:]
                batch_x2 = x2[batch_idx,:]

                o1, o2 = self.model(batch_x1,batch_x2)
                loss = self.loss(o1, o2)

                train_losses.append(loss.item())
                loss.backward()
                self.optimizer.step()
            train_loss = np.mean(train_losses) 