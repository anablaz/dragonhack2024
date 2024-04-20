from pathlib import Path
from PIL import Image

import torch
from torchvision import tv_tensors
from torchvision.transforms import v2
from torch.utils.data import Dataset

from .tiler import Tiler
from .scuffed_mixup import ScuffedMix

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
        self.mix = ScuffedMix()

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, index):
        # load image and river mask
        image = tv_tensors.Image(
            Image.open(self.image_paths[index])
        )
        river_mask  = tv_tensors.Mask(
            tv_tensors.Mask(Image.open(self.mask_paths[index]).convert("L")) == 0, #LOL
            dtype=torch.float32
        )
        image, river_mask = self.transform(image, river_mask)

        # generate tiles - [B, C, H, W], [B, 1, H, W]
        img_tiles, river_mask_tiles = self.tiler.tile(image), self.tiler.tile(river_mask)

        # cut mix babey, find mask where mix and normal images are different
        mix_img_tiles = self.mix(img_tiles, river_mask_tiles)
        mix_mask_tiles = (mix_img_tiles != img_tiles)[:, [0]]

        # mask the image so only river shows and merge mix_mask and river mask
        mix_img_tiles *= river_mask_tiles
        debris_mask_tiles = mix_mask_tiles & river_mask_tiles.bool()
    
        # cls labels are 0 if no debris mask in patch, else 1
        labels = debris_mask_tiles.reshape((debris_mask_tiles.shape[0], -1)).any(dim=1)
        return mix_img_tiles, debris_mask_tiles.float(), labels.float()
