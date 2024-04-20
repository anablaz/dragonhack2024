#!/bin/sh
#SBATCH --job-name=mask_gen
#SBATCH --output=output.out
#SBATCH --nodes=1
#SBATCH --mem=32G
#SBATCH --time=1-0


srun python src/generate_masks.py \
    /d/hpc/projects/FRI/zr13891/datasets/floods/images \
    /d/hpc/projects/FRI/zr13891/datasets/floods/water_seg \
    /d/hpc/projects/FRI/zr13891/datasets/floods/masks