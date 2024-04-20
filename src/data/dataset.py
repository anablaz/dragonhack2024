from pathlib import Path
from PIL import Image

import torch
from torchvision import tv_tensors
from torch.utils.data import Dataset


class SegmentationDataset(Dataset):

    def __init__(self, root, train=True, transform=None):
        dataset_path = Path(root) / ("train" if train else "test")
        self.image_fnames = sorted(dataset_path.glob("*/*/CameraRGB/*.png"))
        self.mask_fnames  = sorted(dataset_path.glob("*/*/CameraSeg/*.png"))
        self.transform = transform

    def __len__(self):
        return len(self.image_fnames)

    def __getitem__(self, index):
        image = Image.open(self.image_fnames[index]).convert("RGB")
        mask  = tv_tensors.Mask(
            Image.open(self.mask_fnames[index]).split()[0], dtype=torch.long)
        if self.transform is not None:
            image, mask = self.transform(image, mask)
        return image, mask.squeeze(0)