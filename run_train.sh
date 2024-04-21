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
srun python src/train.py \
    --img_root /d/hpc/projects/FRI/zr13891/datasets/floods/images \
    --mask_root /d/hpc/projects/FRI/zr13891/datasets/floods/masks