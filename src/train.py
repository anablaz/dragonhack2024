from argparse import ArgumentParser
from pathlib import Path

import lightning as L
from lightning.pytorch.loggers import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint
from models import RiverDebrisModel
from data import RiverDebrisDataModule

if __name__ == "__main__":
    parser = ArgumentParser("seg")
    parser.add_argument(
        "--img_root", type=Path, help="Path to dir containing images."
    )
    parser.add_argument(
        "--mask_root", type=Path, help="Path to dir containing masks."
    )
    parser.add_argument(
        "--seed", type=int, default=1337,
        help="RNG seed."
    )
    args = parser.parse_args()

    L.seed_everything(args.seed)
    model = RiverDebrisModel(lr=1e-4)
    datamodule = RiverDebrisDataModule(
        args.img_root, args.mask_root, (2048, 2048), (256, 256)
    )
    trainer = L.Trainer(
        #logger=WandbLogger(f"Deeplearning-HW2-Seg-{type(model.model).__name__}", project="DL-HW2-Seg"),
        max_epochs=40,
        callbacks=[
            #ModelCheckpoint(monitor="train_iou", mode="max")
        ]
    )
    trainer.fit(model, datamodule)
    trainer.test(model, datamodule)