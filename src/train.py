from argparse import ArgumentParser
from pathlib import Path

import lightning as L
from lightning.pytorch.loggers import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint
from models import SegmentationModel
from data import SegmentationDataModule

num_classes = 13

if __name__ == "__main__":
    parser = ArgumentParser("seg")
    parser.add_argument(
        "--root", type=Path, required=True,
        help="Path to root dir of the seg dataset."
    )
    parser.add_argument(
        "--seed", type=int, default=1337,
        help="RNG seed."
    )
    args = parser.parse_args()

    L.seed_everything(args.seed)
    model = SegmentationModel(lr=1e-4)
    datamodule = SegmentationDataModule(args.root, batch_size=4)
    trainer = L.Trainer(
        logger=WandbLogger(f"Deeplearning-HW2-Seg-{type(model.model).__name__}", project="DL-HW2-Seg"),
        max_epochs=40,
        callbacks=[
            ModelCheckpoint(monitor="val_iou", mode="max")
        ]
    )
    trainer.fit(model, datamodule)
    trainer.test(model, datamodule)