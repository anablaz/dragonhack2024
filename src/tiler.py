import torch
import torch.nn as nn
from torchvision.transforms import Resize


class Tiler:
    def __init__(self, in_size: tuple[int, int], tile_size: tuple[int, int]):
        self.tile_count = []
        for in_dim, tile_dim in zip(in_size, tile_size):
            assert in_dim % tile_dim == 0, "Image size must be divisible by tile size"
            self.tile_count.append(in_dim // tile_dim)

        self.tile_size = tile_size

        self.resizer = Resize(size=in_size)
        self.unfolder = nn.Unfold(kernel_size=tile_size, stride=tile_size)

    def __call__(self, imgs: torch.Tensor):
        assert len(imgs.shape) == 4, "Tiler only supports batched input"

        b = imgs.shape[0]

        # tile height, tile width
        t_h, t_w = self.tile_size
        # vertical tile count, tile count horizontal
        t_c_h, t_c_w = self.tile_count

        img = self.resizer(imgs)

        # [b, C * t_h * t_w, total_tile_count]
        tiles = self.unfolder(img)
        # [b, C, t_h, t_w, total_tile_count] -> [b, total_tile_count, C, t_h, t_w] -> [b, t_dim_h, t_dim_w, C, t_h, t_w]
        tiles = tiles.view(b, -1, t_h, t_w, t_c_h * t_c_w).permute(0, 4, 1, 2, 3).view(b, t_c_h, t_c_w, -1, t_h, t_w)

        return tiles


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import torchvision

    img = torchvision.io.read_image("../data/test_img.png",
                                    mode=torchvision.io.ImageReadMode.RGB).to(torch.float32)
    imgs = torch.stack([img, img])

    tiler = Tiler(in_size=(1024, 768), tile_size=(256, 256))

    tiles = tiler(imgs)
    print(tiles.shape)

    fig, axs = plt.subplots(4, 3)
    for i in range(4):
        for j in range(3):
            axs[i][j].imshow(tiles[0][i][j].permute(1, 2, 0).to(torch.uint8))

    plt.tight_layout()
    plt.show()
