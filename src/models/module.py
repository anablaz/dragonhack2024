import torch
from torch.nn import functional as F
from torchmetrics import JaccardIndex
import lightning as L
from lightning.pytorch.loggers import WandbLogger

from .model import UNet


color_map = torch.tensor([
    [0,0,0], # unlabeled
    [70,70,70], # building
    [190,153,153], # fence
    [250,170,160], # other
    [220,20,60], # pedestrian
    [153,153,153], # pole
    [157,234,50], # road line
    [128,64,128], # road
    [244,35,232], # sidewalk
    [107,142,35], # vegetation
    [0,0,142], # car
    [102,102,156], # wall
    [220,220,0], # traffic sign
])

class SegmentationModel(L.LightningModule):

    def __init__(self, lr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_hyperparameters("lr")
        self.model = UNet(13, skip=True)
        self.loss_fn = F.cross_entropy
        self.train_iou = JaccardIndex(task="multiclass", num_classes=13)
        self.val_iou = JaccardIndex(task="multiclass", num_classes=13)
        self.test_iou = JaccardIndex(task="multiclass", num_classes=13)
            
    def configure_optimizers(self):
        optim = torch.optim.Adam(self.model.parameters(), self.hparams.lr)
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim, [30])
        return {
            "optimizer": optim, 
            "lr_scheduler": scheduler
        }
    
    def _predict(self, batch, stage, **log_kwargs):
        x, y = batch
        y_pred = self.model(x)
        loss = self.loss_fn(y_pred, y)
        iou = getattr(self, f"{stage}_iou")
        iou(y_pred, y)

        self.log(f"{stage}_loss", loss, **log_kwargs)
        self.log(f"{stage}_iou", iou, **log_kwargs)
        return loss

    def training_step(self, batch, batch_idx):
        return self._predict(batch, "train", on_epoch=True, prog_bar=True)
    
    def validation_step(self, batch, batch_idx):
        if batch_idx == 0 and self.current_epoch % 5 == 0 and isinstance(self.logger, WandbLogger):
            x, y = batch
            with torch.no_grad():
                y_pred = torch.argmax(self.model(x), dim=-3)
            y = color_map[y.cpu()][0].permute(2, 0, 1) / 255
            y_pred = color_map[y_pred.cpu()][0].permute(2, 0, 1) / 255
            self.logger.log_image(key="samples", images=[x[0].cpu(), y, y_pred], caption=["image", "gt", "pred"])
        self._predict(batch, "val", prog_bar=True)
    
    def test_step(self, batch, batch_idx):
        self._predict(batch, "test")