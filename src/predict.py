from argparse import ArgumentParser
from pathlib import Path

import lightning as L
import torch
from torch.utils.data import DataLoader

from models import RiverDebrisModel
from data.dataset import RiverDebrisPredDataset

if __name__ == "__main__":
    parser = ArgumentParser("seg")
    parser.add_argument(
        "--img_root", type=Path, help="Path to dir containing images."
    )
    parser.add_argument(
        "--checkpoint_path", type=Path, help="Path to checkpoint."
    )
    parser.add_argument(
        "--mask_root", type=Path, help="Path to dir containing masks."
    )
    args = parser.parse_args()

    model = RiverDebrisModel.load_from_checkpoint(args.checkpoint_path)
    dataset = RiverDebrisPredDataset(args.img_root, args.mask_root, (2048, 2048), (256, 256))
    dataloader = DataLoader(dataset, 1)
    trainer = L.Trainer()
    
    preds = trainer.predict(model, dataloader)
    seg = dataset.tiler.untile(preds[0])
    torch.save(seg, "out.pt")