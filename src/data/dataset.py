from pathlib import Path
from PIL import Image

import torch
from torchvision import tv_tensors
from torchvision.transforms import v2
from torch.utils.data import Dataset

from .tiler import Tiler


class RiverDebrisDataset(Dataset):

    def __init__(self, img_root, mask_root, img_size, patch_size):
        super().__init__()
        self.mask_paths = sorted(Path(mask_root).glob("*.png"))
        _valid_names = [p.stem for p in self.mask_paths] # names of images that have a mask
        self.image_paths = [
            img_path for img_path in sorted(Path(img_root).glob("*.tif"))
            if img_path.stem in _valid_names
        ]
        self.tiler = Tiler(img_size, patch_size)
        self.transform = v2.Compose([
            v2.ToDtype(torch.float32, scale=True),
            v2.Resize(img_size)
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, index):
        image = tv_tensors.Image(
            Image.open(self.image_paths[index])
        )
        mask  = tv_tensors.Mask(
            tv_tensors.Mask(Image.open(self.mask_paths[index]).convert("L")) == 0, #LOL
            dtype=torch.float32
        )
        image, mask = self.transform(image, mask)

        img_tiles, mask_tiles = self.tiler.tile(image), self.tiler.tile(mask)
        return img_tiles, mask_tiles