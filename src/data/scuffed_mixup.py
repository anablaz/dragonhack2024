import torch
from torch import nn

class ScuffedMix(nn.Module):

    def forward(self, img_batch, mask_batch):
        """
        Args:
            x: batched img: [B, N, H, W]
        """
        imgs = []
        for img, mask in zip(img_batch, mask_batch):
            els = mask.sum()
            if els > 1000 and els < mask.numel() - 1000:
                img = synth_gen(img, mask)
            imgs.append(img)
        return torch.stack(imgs)

def synth_gen(img, mask):
    """
    Generate synth anomalies in river
    (makeshift better version of cutmix (task specific pro mlg turbo version))

    Args:
        img: input image
        mask: segmentation mask

    Returns:
        image with generated anomalies
    """
    img = img.clone()
    # generate coords for destination of anomaly in river
    dx1, dy1, dx2, dy2, r_w_half, r_h_half = get_coords(mask)
    # generate coords with same shape for source of anomaly outisde the river
    sx1, sy1, sx2, sy2, _, _ = get_coords((mask == 0), r_w_half, r_h_half)
    img[..., dy1:dy2, dx1:dx2] = img[..., sy1:sy2, sx1:sx2]

    return img

def get_coords(mask, r_w_half=None, r_h_half=None):
    """
    Get coordinates within the segmentation mask (where mask == 1)

    Args:
        mask: segmentation mask where regions of interest are set to 1
        r_w_half: (optional) half of width
        r_h_half: (optional) half of height

    Returns:
        coordinates and size
    """
    _, h, w = mask.shape
    # get nonzero indices from mask (we only want to pick cutout from these)
    nonzero = torch.nonzero(mask)

    cut_ok = False

    # loop to make sure the size is okay
    while not cut_ok:
        # randomly pick start coordinates
        i = torch.randint(nonzero.shape[0], (1,))[0]
        _, r_y, r_x = nonzero[i]

        if r_h_half is None and r_w_half is None:
            # if size is not provided randomly generate
            r_h_half = torch.randint(int(h * 0.02), int(h * 0.05), size=(1,))[0]
            r_w_half = torch.randint(int(w * 0.02), int(w * 0.05), size=(1,))[0]

        # get coords from center coord + rectangle half
        x1 = int(torch.clamp(r_x - r_w_half, min=0))
        y1 = int(torch.clamp(r_y - r_h_half, min=0))
        x2 = int(torch.clamp(r_x + r_w_half, max=w))
        y2 = int(torch.clamp(r_y + r_h_half, max=h))

        # cut is ok if size matches to 0.001 deciaml
        cut_ok = abs((y2 - y1) - r_h_half * 2) < 0.001
        cut_ok &= abs((x2 - x1) - r_w_half * 2) < 0.001

    # return coords and half size
    return x1, y1, x2, y2, r_w_half, r_h_half