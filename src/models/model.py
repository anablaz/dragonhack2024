import torch
from torch import nn
from torchvision.models import resnet18

class UNetBlock(nn.Sequential):

    def __init__(self, chan):
        super().__init__(nn.LazyConv2d(chan, 3, padding="same"), nn.ReLU(), nn.Conv2d(chan, chan, 3, padding="same"), nn.ReLU())

class UNet(nn.Module):
    
    def __init__(self, num_classes, skip=True):
        super().__init__()
        self.skip = skip
        sizes = [64, 128, 256, 512, 1024]
        self.encoder_blocks = nn.ModuleList(UNetBlock(s) for s in sizes)
        self.pool = nn.MaxPool2d(2, 2)
        self.decoder_blocks = nn.ModuleList(UNetBlock(s) for s in reversed(sizes[:-1]))
        self.deconvs = nn.ModuleList(nn.ConvTranspose2d(i, o, 2, 2) for i, o in zip(sizes[::-1], sizes[-2::-1]))
        self.conv_out = nn.Conv2d(sizes[0], num_classes, 1)
    
    def forward(self, x):
        skips = []
        for block in self.encoder_blocks[:-1]:
            x = block(x)
            skips.insert(0, x if self.skip else x.shape)
            x = self.pool(x)
        x = self.encoder_blocks[-1](x)
        for skip, block, deconv in zip(skips, self.decoder_blocks, self.deconvs):
            x = deconv(x, output_size=skip.shape if self.skip else skip)
            if self.skip: x = torch.cat((skip, x), dim=-3)
            x = block(x)
        return self.conv_out(x)
    
class SegClsNet(nn.Module):

    def __init__(self, num_seg_classes, num_cls_classes):
        super().__init__()
        self.seg = UNet(num_seg_classes)
        self.cls = nn.Sequential(
            nn.Conv2d(num_seg_classes+3, 3, 1), 
            resnet18(num_classes=num_cls_classes)
        )

    def forward(self, x):
        seg = self.seg(x)
        cls = self.cls(torch.cat([x, seg], dim=1))
        return seg, cls
