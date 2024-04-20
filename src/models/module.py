import torch
from torch import nn
from torchmetrics import JaccardIndex
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
        
        loss = self.loss_fn_cls(pred_cls, y_cls) +\
            self.loss_fn_seg(pred_seg, y_seg)
        self.train_iou(pred_seg, y_seg)

        self.log(f"train_loss", loss)
        self.log(f"train_iou", self.train_iou)
        return loss
