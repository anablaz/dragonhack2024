#!/bin/bash
#SBATCH --job-name=segmentation
#SBATCH --output=output.out
#SBATCH --nodes=1
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --mem-per-gpu=32G
#SBATCH --cpus-per-task=16
#SBATCH --time=4:00:00

srun nvidia-smi
srun python src/predict.py \
    --img_root /d/hpc/projects/FRI/zr13891/datasets/floods/pred/images \
    --mask_root /d/hpc/projects/FRI/zr13891/datasets/floods/pred/masks \
    --checkpoint_path /d/hpc/home/zr13891/dragonhack/dragonhack2024/Dragonhack/b4qpb2zy/checkpoints/last.ckpt