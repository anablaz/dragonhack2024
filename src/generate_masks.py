from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
from PIL import Image
import rasterio
from shapely.geometry import box
import io
import os
from argparse import ArgumentParser
import numpy as np

parser = ArgumentParser("Mask generation")
parser.add_argument(
    "img_root", type=Path, help="Path to dir containing images."
)
parser.add_argument(
    "seg_path", type=Path, help="Path to river segmentation file."
)
parser.add_argument(
    "out_root", type=Path, help="Path to output dir."
)
args = parser.parse_args()

dataset_path = args.img_root
seg_path = args.seg_path
out_path = args.out_root

os.makedirs(out_path, exist_ok=True)

print("reading segmentation file...")
seg = gpd.read_file(seg_path)
seg = seg.drop(['ID_REG_HOB', 'HOBMPV_ID', 'HOBMPV_IM', 'VERZIJA', 'DATP_ZAC',
       'DATP_KON', 'RAZVOJ', 'JEZIK', 'DAT_ZAC', 'DAT_KON', 'IME_ID', 'IME',
       'VRSTA_ID', 'VRSTA_IM', 'TIPSV_ID', 'TIPSV_IM', 'TIPTV_ID', 'TIPTV_IM',
       'TIPPREH_ID', 'TIPPREH_IM', 'IZVOR_ID', 'IZVOR_IM', 'STALN_ID',
       'STALN_IM', 'STANJE_ID', 'STANJE_IM', 'POTEK_ID', 'POTEK_IM',
       'SIRINA_ID', 'SIRINA_IM', 'VIRP_ID', 'VIRP_IM', 'PREOB_ID', 'PREOB_IME',
       'VODE_ID', 'HMZ_ID', 'NADM_V', 'DVIRP', 'SIMBOL', 'SHAPE_AREA',
       'SHAPE_LEN'], axis=1).to_crs("EPSG:4326")
print("done")

for img_path in dataset_path.glob("*.tif"):
    print(f"reading image {str(img_path)}...")
    
    # read geo bbox
    img = rasterio.open(img_path)
    bbox = box(*img.bounds)
    bbox_df = gpd.GeoDataFrame({"geometry":[bbox]})
    bbox_df = bbox_df.set_crs(img.crs.to_dict())
    bbox_df = bbox_df.to_crs("EPSG:4326")
    bbox = bbox_df.iloc[0, 0]
    
    # get intersects with rivers
    intersects = seg.intersects(bbox)
    if not intersects.any():
        print("no intersections found, skipping.")
        continue

    # plot the river bboxes
    buf = io.BytesIO()
    dpi = 100
    fig, ax = plt.subplots(figsize=(img.width/dpi, img.height/dpi), dpi=dpi)
    seg.loc[intersects].plot(ax=ax, color="k")
    ax.set_xlim(bbox.bounds[0], bbox.bounds[2])
    ax.set_ylim(bbox.bounds[1], bbox.bounds[3])
    plt.axis('off')
    plt.savefig(buf, dpi=dpi, pad_inches=0, bbox_inches="tight")

    # save mask
    buf.seek(0)
    mask = Image.open(buf)
    if (np.array(mask) == 0).mean() < 0.05:
        continue

    #mask.resize((img.width, img.height))
    mask.save(out_path / f"{img_path.stem}.png")
    print("saved mask.")
    plt.close(fig)
