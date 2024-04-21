import torch
import torch.nn as nn
from torchvision.transforms import Resize


class Tiler:
    """
    Tiler class to split the image into smaller tiles

    Args:
        in_size (tuple[int, int]): input image size
        tile_size (tuple[int, int]): tile size

    """

    def __init__(self, in_size: tuple[int, int], tile_size: tuple[int, int]):
        self.tile_count = []
        for in_dim, tile_dim in zip(in_size, tile_size):
            assert in_dim % tile_dim == 0, "Image size must be divisible by tile size"
            self.tile_count.append(in_dim // tile_dim)

        self.tile_size = tile_size

        self.unfolder = nn.Unfold(kernel_size=tile_size, stride=tile_size)
        self.folder = torch.nn.Fold(output_size=in_size, kernel_size=tile_size, stride=tile_size)

    def tile(self, img: torch.Tensor):
        """
        Tile the passed images into specified tiles.

        Args:
            img (torch.Tensor): input images of shape [C, H, W]

        Returns:
            tiled image in shape: [t_dim_h * t_dim_w, C, t_h, t_w]
        """
        assert len(img.shape) == 3, "Tiler only supports non-batched input"

        # tile height, tile width
        t_h, t_w = self.tile_size
        # vertical tile count, tile count horizontal
        t_c_h, t_c_w = self.tile_count

        # [C * t_h * t_w, total_tile_count]
        tiles = self.unfolder(img)
        # [C, t_h, t_w, total_tile_count] -> [total_tile_count, C, t_h, t_w]
        tiles = tiles.view(-1, t_h, t_w, t_c_h * t_c_w).permute(3, 0, 1, 2)

        return tiles

    def untile(self, tiles: torch.Tensor):
        """
        Assemble the tiles back into full image.

        Args:
            tiles (torch.Tensor): tiles of shape [t_dim_h * t_dim_w, C, t_h, t_w]

        Returns:
            reassembled image in shape: [C, H, W]
        """
        # tile height, tile width
        t_h, t_w = self.tile_size
        # vertical tile count, tile count horizontal
        t_c_h, t_c_w = self.tile_count

        # [total_tile_count, C, t_h, t_w] -> [C, t_h, t_w, total_tile_count]
        tiles = tiles.permute(1, 2, 3, 0).view(-1, t_c_h * t_c_w)
        untiled = self.folder(tiles)

        return untiled


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import torchvision

    img = torchvision.io.read_image("../data/test_img.png",
                                    mode=torchvision.io.ImageReadMode.RGB).to(torch.float32)

    resize = Resize((1024, 768))
    img = resize(img)

    tiler = Tiler(in_size=(1024, 768), tile_size=(256, 256))

    tiles = tiler.tile(img)
    untiled = tiler.untile(tiles)

    assert (img == untiled).all()

    fig, axs = plt.subplots(4, 3)
    for i in range(4):
        for j in range(3):
            axs[i][j].imshow(tiles[i*3 + j].permute(1, 2, 0).to(torch.uint8))

    plt.tight_layout()
    plt.show()

    plt.imshow(untiled.permute(1, 2, 0).to(torch.uint8))
    plt.show()
