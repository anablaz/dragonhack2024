from torch.utils.data import DataLoader
import lightning as L

from .dataset import RiverDebrisDataset


class RiverDebrisDataModule(L.LightningDataModule):

    def __init__(self, img_root, mask_root, img_size, patch_size):
        super().__init__()
        self.train_dataset = RiverDebrisDataset(
            img_root, mask_root, img_size, patch_size
        )
    
    def train_dataloader(self):
        return DataLoader(
            self.train_dataset, 1, shuffle=True, num_workers=4
        )