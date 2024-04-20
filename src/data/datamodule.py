from pathlib import Path

import torch
from torchvision.transforms import v2
from torch.utils.data import DataLoader, random_split
import lightning as L

from .dataset import SegmentationDataset


class SegmentationDataModule(L.LightningDataModule):

    def __init__(self, root, batch_size):
        super().__init__()
        self.root = Path(root)
        self.batch_size = batch_size
        self.image_size = (320, 416)

    def setup(self, stage: str):
        train_transform = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Resize(self.image_size, antialias=False)
        ])

        test_transform = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Resize(self.image_size, antialias=False)
        ])

        if stage == "fit":
            trainval = SegmentationDataset(
                self.root, transform=train_transform)
            self.train, self.val = random_split(trainval, [0.8, 0.2])
        if stage == "test":
            self.test = SegmentationDataset(
                self.root, train=False, transform=test_transform)
    
    def train_dataloader(self):
        return DataLoader(
            self.train, self.batch_size, shuffle=True, num_workers=4)
    
    def val_dataloader(self):
        return DataLoader(
            self.val, self.batch_size, shuffle=False, num_workers=4)
    
    def test_dataloader(self):
        return DataLoader(
            self.test, self.batch_size, shuffle=False, num_workers=4)