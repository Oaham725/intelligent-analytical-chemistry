"""Reload one saved ConvAE + k-means pipeline without retraining."""
import argparse,json
from pathlib import Path
import numpy as np
import torch
from run import Autoencoder,infer
torch.set_num_threads(2)
p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);p.add_argument('--data',required=True)
p.add_argument('--key',default='test_cube');p.add_argument('--output',default='new_prediction.npz');a=p.parse_args()
folder=Path(a.model_dir);cube=np.load(a.data,allow_pickle=False)[a.key].astype('float32')
ck=torch.load(folder/'model.pt',map_location='cpu',weights_only=True)
if cube.ndim!=3 or cube.shape[-1]!=ck['bands']:raise ValueError('Expected H,W,B with same spectral channels as trained model')
norm=json.loads((folder/'normalization.json').read_text());model=Autoencoder(ck['bands']);model.load_state_dict(ck['state_dict']);model.eval()
x=((cube.reshape(-1,cube.shape[-1])-norm['mean'])/norm['scale']).astype('float32')
pred,z=infer(model,x);centers=np.load(folder/'ConvAE_cluster_centers.npy');mapping=np.load(folder/'ConvAE_cluster_display_mapping.npy')
labels=((z[:,None,:]-centers[None,:,:])**2).sum(-1).argmin(-1)
np.savez_compressed(a.output,denoised_cube=(pred*norm['scale']+norm['mean']).reshape(cube.shape),labels=mapping[labels].reshape(cube.shape[:2]))
print(a.output)
