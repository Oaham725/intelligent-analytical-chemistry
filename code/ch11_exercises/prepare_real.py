"""Prepare official TIFF files, preserving independently acquired fields."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import tifffile

p=argparse.ArgumentParser();p.add_argument('--train',required=True);p.add_argument('--test',required=True)
p.add_argument('--output',default='data/mineral_small.npz');p.add_argument('--spatial-step',type=int,default=4)
p.add_argument('--spectral-step',type=int,default=3);a=p.parse_args()
cubes=[];details=[]
for filename in [a.train,a.test]:
    raw=tifffile.imread(filename)
    if raw.ndim!=3 or raw.shape[1]!=raw.shape[2]:raise ValueError('Expected official TIFF channels,height,width; inspect axes first')
    cube=raw[::a.spectral_step,::a.spatial_step,::a.spatial_step].transpose(1,2,0).astype('float32')
    if not np.isfinite(cube).all():raise ValueError('Non-finite pixels require explicit handling')
    # Flag extremes rather than claiming automatic detector-saturation identification.
    details.append(dict(path=filename,raw_shape=list(raw.shape),prepared_shape=list(cube.shape),
                        dtype=str(raw.dtype),min=float(raw.min()),max=float(raw.max()),
                        max_value_pixel_fraction=float((raw==raw.max()).mean()),
                        sha256=hashlib.file_digest(open(filename,'rb'),'sha256').hexdigest()))
    cubes.append(cube)
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
np.savez_compressed(out,train_cube=cubes[0],test_cube=cubes[1],axis=np.arange(0,raw.shape[0],a.spectral_step))
out.with_suffix('.json').write_text(json.dumps(dict(files=details,spatial_step=a.spatial_step,spectral_step=a.spectral_step,
    axis='Original hyperspectral channel indices; Raman calibration not supplied',saturation='No manual saturation replacement; inspect extreme-response clusters'),indent=2),encoding='utf8')
print(out, [c.shape for c in cubes])
