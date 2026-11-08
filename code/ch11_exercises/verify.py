"""Verify saved numerical results, partitions, and reloadable model weights."""
from pathlib import Path
import csv,json
import numpy as np
import torch
from run import Autoencoder,quality,infer

root=Path(__file__).resolve().parents[2]
torch.set_num_threads(2)
checks=[]
for kind in ['real','synthetic']:
    base=root/'results'/kind
    with (base/'metrics.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    assert len(rows)==(12 if kind=='real' else 36)
    for folder in base.glob('*/*'):
        if not folder.is_dir() or not (folder/'split.npz').exists():continue
        split=np.load(folder/'split.npz');p=np.load(folder/'predictions.npz')
        tr,va,te=[split[k] for k in ['train','val','test']]
        assert not set(tr)&set(va) and not set(tr)&set(te) and not set(va)&set(te)
        if folder.name=='spatial':
            m=split['split_map']; yy,xx=np.where(m==2)
            for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
                y,x=yy+dy,xx+dx;valid=(y>=0)&(y<m.shape[0])&(x>=0)&(x<m.shape[1])
                assert not np.any(m[y[valid],x[valid]]==0)
        assert all(np.isfinite(p[k]).all() for k in p.files)
        bands=p['ConvAE_cube'].shape[-1]
        checkpoint=torch.load(folder/'model.pt',map_location='cpu',weights_only=True)
        model=Autoencoder(bands);model.load_state_dict(checkpoint['state_dict']);model.eval()
        with torch.no_grad():assert model(torch.zeros(2,1,bands)).shape==(2,1,bands)
        norm=json.loads((folder/'normalization.json').read_text())
        raw=p['Raw_cube'].reshape(-1,bands)
        x=((raw-norm['mean'])/norm['scale']).astype('float32')
        recovered,z=infer(model,x)
        assert np.allclose(recovered*norm['scale']+norm['mean'],p['ConvAE_cube'].reshape(-1,bands),rtol=2e-5,atol=2e-5)
        centers=np.load(folder/'ConvAE_cluster_centers.npy')
        mapping=np.load(folder/'ConvAE_cluster_display_mapping.npy')
        labels=((z[:,None,:]-centers[None,:,:])**2).sum(-1).argmin(-1)
        assert np.array_equal(mapping[labels],p['ConvAE_labels'].ravel())
        if kind=='synthetic':
            clean=np.load(base/'synthetic_clean.npz')['test_clean'].reshape(-1,bands)
            for method in ['Raw','MovingAverage5','ConvAE']:
                calculated=quality(p[method+'_cube'].reshape(-1,bands),clean)
                row=next(r for r in rows if r['split']==folder.name and r['noise_sigma']==folder.parent.name and r['scope']=='external_field' and r['method']==method)
                for key in calculated:assert np.isclose(calculated[key],float(row[key]),rtol=1e-5,atol=1e-6),(folder,key)
        else:
            assert all(not r.get('accuracy') and not r.get('RMSE') for r in rows)
        checks.append(str(folder.relative_to(root)))
(root/'docs/verification.json').write_text(json.dumps(dict(status='passed',checks=checks,
    verified=['disjoint train/val/test','no immediate train/test neighbors in spatial split','finite saved predictions',
    'reload model weights and reproduce saved reconstruction and cluster labels','recompute synthetic spectral metrics from saved predictions','no fabricated real ground-truth metrics'],
    limitations='Same machine; independent student/environment cross-review remains pending'),indent=2),encoding='utf8')
print('PASS:',len(checks),'experiment directories')
