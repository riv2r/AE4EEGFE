import time
import logging
import torch
import numpy as np
from torch.utils.data import BatchSampler, RandomSampler, SequentialSampler


class TrainDCCA():

    def __init__(self,model,output_size,linear_cca,epoch_num,batch_size,learning_rate,reg_para,device=torch.device('cpu')):

        self.model = model
        self.model.to(device)
        self.output_size = output_size
        self.linear_cca = linear_cca
        self.epoch_num = epoch_num
        self.batch_size = batch_size
        self.loss = model.loss
        # optimizer
        self.optimizer = torch.optim.RMSprop(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=reg_para
        )
        self.device =device

        logging.basicConfig(
            level=logging.DEBUG,
            format="[ %(levelname)s : %(asctime)s ] - %(message)s"
        )
        self.logger = logging.getLogger("PyTorch")
        filehandler = logging.FileHandler("DCCA.log")
        formatter = logging.Formatter(
            "[ %(levelname)s : %(asctime)s ] - %(message)s"
        )
        filehandler.setFormatter(formatter)
        self.logger.addHandler(filehandler)
        self.logger.info(self.model)
        self.logger.info(self.optimizer)

    def fit(self,x1,x2,vx1=None,vx2=None,tx1=None,tx2=None,checkpoint='checkpoint.model'):

        x1.to(self.device)
        x2.to(self.device)
        # data_size is numSamplingPoints 
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
            info_string = "Epoch {:d}/{:d} - time: {:.2f} - training_loss: {:.4f}"
            if vx1 is not None and vx2 is not None:
                with torch.no_grad():
                    # keep weight still when testing
                    self.model.eval()
                    val_loss = self.test(vx1,vx2) 
                    info_string += " - val_loss: {:.4f}".format(val_loss)
                    if val_loss < best_val_loss:
                        self.logger.info(
                            "Epoch {:d}: val_loss improved from {:.4f} to {:.4f}, saving model to {}".format(epoch + 1, best_val_loss, val_loss, checkpoint)
                        )
                        best_val_loss = val_loss
                        torch.save(self.model.state_dict(), checkpoint)
                    else:
                        self.logger.info(
                            "Epoch {:d}: val_loss did not improve from {:.4f}".format(epoch + 1, best_val_loss)
                        )
            else:
                torch.save(self.model.state_dict(), checkpoint)
            epoch_end_time = time.time()
            epoch_time = epoch_end_time - epoch_start_time
            self.logger.info(
                info_string.format(
                    epoch + 1,
                    self.epoch_num,
                    epoch_time,
                    train_loss
                )
            )

        if self.linear_cca is not None:
            _, output = self._get_output(x1,x2) 
            self.linear_cca.fit(output[0],output[1],self.output_size)
        
        checkpoint_ = torch.load(checkpoint)
        self.model.load_state_dict(checkpoint_)

        if vx1 is not None and vx2 is not None:
            loss = self.test(vx1,vx2)
            self.logger.info("loss on validation data: {:.4f}".format(loss))

        if tx1 is not None and tx2 is not None:
            loss = self.test(tx1,tx2)
            self.logger.info("loss on test data: {:.4f}".format(loss))
    
    def _get_output(self,x1,x2):

        with torch.no_grad():
            self.model.eval()
            data_size = x1.size(0)
            batch_idxs = list(
                BatchSampler(
                    SequentialSampler(
                        range(data_size)
                    ),
                    batch_size=self.batch_size,
                    drop_last=False            
                )
            )
            losses = []
            output1 = []
            output2 = []
            for batch_idx in batch_idxs:
                batch_x1 = x1[batch_idx,:]
                batch_x2 = x2[batch_idx,:]
                o1, o2 = self.model(batch_x1,batch_x2)
                output1.append(o1)
                output2.append(o2)
                loss = self.loss(o1, o2)
                losses.append(loss.item())
        output = [
            torch.cat(output1, dim=0).cpu().numpy(),
            torch.cat(output2, dim=0).cpu().numpy()
        ]

        return losses, output
    
    def test(self,x1,x2,apply_linear_cca=False):

        with torch.no_grad():
            losses, output = self._get_output(x1, x2)
            if apply_linear_cca:
                print("Linear CCA Started")
                output = self.linear_cca.test(output[0],output[1]) 
                return np.mean(losses),output
            else:
                return np.mean(losses)