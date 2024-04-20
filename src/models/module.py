import torch
from torch import nn
from torchmetrics import JaccardIndex, Accuracy
import lightning as L

from .model import SegClsNet


class RiverDebrisModel(L.LightningModule):

    def __init__(self, lr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_hyperparameters("lr")
        self.model = SegClsNet(
            num_cls_classes=1,
            num_seg_classes=1,
        )
        
        self.loss_fn_cls = nn.BCEWithLogitsLoss()
        self.loss_fn_seg = nn.BCEWithLogitsLoss()

        self.train_iou = JaccardIndex(task="binary")
        self.train_acc = Accuracy(task="binary")
            
    def configure_optimizers(self):
        optim = torch.optim.Adam(self.model.parameters(), self.hparams.lr)
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim, [])
        return {
            "optimizer": optim, 
            "lr_scheduler": scheduler
        }

    def training_step(self, batch, batch_idx):
        x, y_seg, y_cls = [h[0] for h in batch]
        pred_seg, pred_cls = self.model(x)
        
        loss = self.loss_fn_cls(pred_cls, y_cls.unsqueeze(1)) +\
            self.loss_fn_seg(pred_seg, y_seg)
        self.train_iou(pred_seg, y_seg)
        self.train_acc(pred_cls, y_cls.unsqueeze(1))

        self.log(f"train_loss", loss)
        self.log(f"train_iou", self.train_iou, on_epoch=True, prog_bar=True)
        self.log(f"train_acc", self.train_acc, on_epoch=True, prog_bar=True)
        return loss
