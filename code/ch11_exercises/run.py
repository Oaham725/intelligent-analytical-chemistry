"""UHRED-inspired teaching experiment. Synthetic results are NOT paper reproduction."""
import argparse, copy, csv, json, time, platform
from pathlib import Path
import numpy as np
import torch
from torch import nn
from scipy.ndimage import uniform_filter1d
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, confusion_matrix, f1_score, silhouette_score
from matplotlib.patches import Patch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

COLORS = ['#2764ac', '#dd8540', '#37a386']

def synthetic(seed, size=48, bands=96):
    """Analytic peaks and masks, not measured mineral spectra or SRS data."""
    rng = np.random.default_rng(seed)
    axis = np.linspace(200, 1200, bands)
    specs = []
    for peaks in [[(380, 18, 1), (720, 28, .65)],
                  [(500, 24, 1), (890, 20, .75)],
                  [(620, 20, .8), (1030, 30, 1)]]:
        specs.append(sum(a*np.exp(-.5*((axis-p)/w)**2) for p,w,a in peaks))
    specs = np.array(specs)
    y,x = np.mgrid[:size,:size]/size
    labels = np.zeros((size,size),dtype=int)
    labels[(x-.32)**2+(y-.4)**2 < .20**2] = 1
    labels[((x-.48)/.26)**2+((y-.77)/.16)**2 < 1] = 2
    weights = np.eye(3)[labels]
    # Different intensity and peak positions across independently generated fields.
    shift = rng.uniform(-2,2)
    specs = np.array([np.interp(axis+shift,axis,s) for s in specs])
    amp = .7 + .5*x + .15*np.sin(y*9+seed)
    clean = (weights@specs)*amp[...,None]
    clean += .025 + .02*(axis-axis.min())/(axis.max()-axis.min())
    return clean.astype('float32'), labels, axis

class Autoencoder(nn.Module):
    """Reduced convolutional AE; not the authors' exact hyperparameters."""
    def __init__(self,bands,latent=6):
        super().__init__()
        self.conv=nn.Sequential(nn.Conv1d(1,8,5,padding=2),nn.Tanh(),nn.MaxPool1d(2),
                                nn.Conv1d(8,12,5,padding=2),nn.Tanh(),nn.MaxPool1d(2))
        with torch.no_grad(): self.shape=self.conv(torch.zeros(1,1,bands)).shape[1:]
        n=int(np.prod(self.shape))
        self.enc=nn.Linear(n,latent); self.dec=nn.Linear(latent,n)
        self.out=nn.Sequential(nn.Conv1d(12,8,5,padding=2),nn.Tanh(),nn.Conv1d(8,1,5,padding=2))
        self.bands=bands
    def encode(self,x): return self.enc(self.conv(x).flatten(1))
    def forward(self,x):
        z=self.encode(x)
        a=torch.tanh(self.dec(z)).reshape(-1,*self.shape)
        a=nn.functional.interpolate(a,size=self.bands,mode='linear',align_corners=False)
        return self.out(a)

def train(x,tr,va,epochs,seed,out):
    torch.manual_seed(seed)
    model=Autoencoder(x.shape[1]); opt=torch.optim.Adam(model.parameters(),lr=.002,weight_decay=1e-5)
    tx=torch.from_numpy(x[:,None,:].astype('float32'))
    best=float('inf'); state=None; logs=[]
    gen=torch.Generator().manual_seed(seed)
    for ep in range(epochs):
        model.train(); total=0
        order=tr[torch.randperm(len(tr),generator=gen).numpy()]
        for ids in np.array_split(order,max(1,int(np.ceil(len(order)/128)))):
            pred=model(tx[ids]); loss=(pred-tx[ids]).square().mean()
            opt.zero_grad(); loss.backward(); opt.step(); total+=loss.item()*len(ids)
        model.eval()
        with torch.no_grad(): val=(model(tx[va])-tx[va]).square().mean().item()
        logs.append([ep+1,total/len(tr),val])
        if val<best: best=val; state=copy.deepcopy(model.state_dict())
    model.load_state_dict(state)
    torch.save({'state_dict':state,'bands':x.shape[1],'latent':6},out/'model.pt')
    np.savetxt(out/'training.csv',logs,delimiter=',',header='epoch,train_noisy_MSE,val_noisy_MSE',comments='')
    with torch.no_grad():
        pred=np.concatenate([model(v).numpy()[:,0] for v in tx.split(256)])
        z=np.concatenate([model.encode(v).numpy() for v in tx.split(256)])
    return model,pred,z,np.array(logs)

def infer(model,x):
    tx=torch.from_numpy(x[:,None,:].astype('float32'))
    with torch.no_grad():
        return (np.concatenate([model(t).numpy()[:,0] for t in tx.split(256)]),
                np.concatenate([model.encode(t).numpy() for t in tx.split(256)]))

def align_from_training(pred,truth,k):
    cm=confusion_matrix(truth,pred,labels=np.arange(k))
    a,b=linear_sum_assignment(-cm)
    return np.array([dict(zip(b,a)).get(i,i) for i in range(k)])

def quality(pred,clean):
    rmse=float(np.sqrt(np.mean((pred-clean)**2)))
    span=float(clean.max()-clean.min())
    psnr=float(20*np.log10(span/max(rmse,1e-12)))
    dot=np.sum(pred*clean,axis=1); den=np.linalg.norm(pred,axis=1)*np.linalg.norm(clean,axis=1)
    sam=float(np.degrees(np.arccos(np.clip(dot/np.maximum(den,1e-12),-1,1))).mean())
    peak=float(np.mean(np.abs(pred.max(1)-clean.max(1))))
    return dict(RMSE=rmse,PSNR_dB=psnr,SAM_deg=sam,peak_height_MAE=peak)

def savefig(fig,path):
    fig.savefig(path.with_suffix('.png'),dpi=180,bbox_inches='tight')
    fig.savefig(path.with_suffix('.svg'),bbox_inches='tight'); plt.close(fig)

def experiment(args):
    start=time.time(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    torch.set_num_threads(2)
    rng=np.random.default_rng(args.seed)
    if args.data:
        d=np.load(args.data,allow_pickle=False)
        cubes=[np.asarray(d[k],dtype='float32') for k in ['train_cube','test_cube']]
        if any(c.ndim!=3 or min(c.shape)<2 for c in cubes): raise ValueError('Expected H,W,B arrays')
        if cubes[0].shape[-1]!=cubes[1].shape[-1]: raise ValueError('Channel mismatch')
        if not all(np.isfinite(c).all() for c in cubes): raise ValueError('Nonfinite input: mask/repair before import')
        labels=[d[k] if k in d else None for k in ['train_labels','test_labels']]
        refs=[d[k] if k in d else None for k in ['train_clean','test_clean']]
        axis=d['axis'] if 'axis' in d else np.arange(cubes[0].shape[-1])
        source='REAL HYPERSPECTRAL DATA - NO PIXEL GROUND TRUTH'
        levels=[None]
    else:
        a,la,axis=synthetic(args.seed); b,lb,_=synthetic(args.seed+101)
        cubes=[a,b]; refs=[a,b]; labels=[la,lb]; levels=[.08,.2,.4]
        source='SYNTHETIC TEACHING DATA - NOT PAPER REPRODUCTION'
        np.savez_compressed(out/'synthetic_clean.npz',train_clean=a,test_clean=b,train_labels=la,test_labels=lb,axis=axis)
    rows=[]; audits=[]; figures=[]
    for li,sigma in enumerate(levels):
        noisy=[c.copy() if sigma is None else c+rng.normal(0,sigma,c.shape).astype('float32') for c in cubes]
        leveldir=out/f'{"real" if sigma is None else str(sigma)}';leveldir.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(leveldir/'observed_data.npz',train_cube=noisy[0],test_cube=noisy[1])
        h,w,bands=noisy[0].shape; n=h*w
        for scheme in ['random','spatial']:
            folder=out/f'{"real" if sigma is None else str(sigma)}/{scheme}';folder.mkdir(parents=True,exist_ok=True)
            ids=np.arange(n).reshape(h,w)
            if scheme=='random':
                p=rng.permutation(n); tr=p[:int(.65*n)];va=p[int(.65*n):int(.8*n)];te=p[int(.8*n):]
            else:
                # Two-column exclusion buffers between train/validation/test.
                cut1=int(w*.55);cut2=int(w*.78)
                tr=ids[:,:cut1].ravel();va=ids[:,cut1+2:cut2].ravel();te=ids[:,cut2+2:].ravel()
            if min(len(tr),len(va),len(te))==0: raise ValueError('Image too small for buffered spatial split')
            if labels[0] is not None and len(np.unique(labels[0].ravel()[tr]))!=args.clusters:
                raise ValueError('Training region lacks a class: cannot identify all cluster-to-class mappings from training labels')
            split=np.full(n,-1);split[tr]=0;split[va]=1;split[te]=2
            sm=split.reshape(h,w)
            neighbor=np.zeros_like(sm,dtype=bool)
            neighbor[1:] |= sm[:-1]==0;neighbor[:-1] |= sm[1:]==0
            neighbor[:,1:] |= sm[:,:-1]==0;neighbor[:,:-1] |= sm[:,1:]==0
            audit={'scheme':scheme,'noise':sigma,'train_n':len(tr),'val_n':len(va),'test_n':len(te),
                   'train_test_index_overlap':int(len(np.intersect1d(tr,te))),
                   'test_adjacent_to_train_fraction':float(neighbor.ravel()[te].mean()),
                   'external_field_used_for_fit':False,'same_sample_external_independence':'Different fields do not establish independent sample/batch/instrument generalization'}
            audits.append(audit)
            np.savez_compressed(folder/'split.npz',train=tr,val=va,test=te,split_map=sm)
            flat=noisy[0].reshape(-1,bands); ext=noisy[1].reshape(-1,bands)
            mean=float(flat[tr].mean()); scale=float(np.ptp(flat[tr]));scale=max(scale,1e-8)
            x=((flat-mean)/scale).astype('float32');xe=((ext-mean)/scale).astype('float32')
            model,ae,z,logs=train(x,tr,va,args.epochs,args.seed,folder)
            aee,ze=infer(model,xe)
            processed={'Raw':(flat,ext,x,xe),
                       'MovingAverage5':(uniform_filter1d(flat,5,axis=1,mode='nearest'),uniform_filter1d(ext,5,axis=1,mode='nearest'),None,None),
                       'ConvAE':(ae*scale+mean,aee*scale+mean,z,ze)}
            maps={}; spectra={}; recon={}; raw_training_clusters=None
            k=args.clusters
            for method,(rec,rece,feat,feate) in processed.items():
                if feat is None: feat=(rec-mean)/scale;feate=(rece-mean)/scale
                km=KMeans(k,random_state=args.seed,n_init=10).fit(feat[tr])
                np.save(folder/f'{method}_cluster_centers.npy',km.cluster_centers_)
                p=km.predict(feat);pe=km.predict(feate)
                # Match labels on TRAIN labels only. Test labels never select the mapping.
                mapping=None
                if labels[0] is not None:
                    if np.any((labels[0]<0)|(labels[0]>=k)): raise ValueError('Labels must be 0..K-1')
                    mapping=align_from_training(p[tr],labels[0].ravel()[tr],k)
                    p=mapping[p];pe=mapping[pe]
                elif raw_training_clusters is None:
                    raw_training_clusters=p[tr].copy()
                else:
                    display_map=align_from_training(p[tr],raw_training_clusters,k)
                    p=display_map[p];pe=display_map[pe]
                np.save(folder/f'{method}_cluster_display_mapping.npy',mapping if mapping is not None else display_map if method!='Raw' and labels[0] is None else np.arange(k))
                maps[method]=pe.reshape(noisy[1].shape[:2]);recon[method]=rece.reshape(noisy[1].shape)
                spectra[method]=rece
                for scope,indices,pred,truth,cl,lab in [
                    ('within_field_test',te,rec,refs[0],p,labels[0]),
                    ('external_field',np.arange(len(ext)),rece,refs[1],pe,labels[1])]:
                    row=dict(source=source,noise_sigma=sigma,split=scheme,scope=scope,method=method)
                    observed=flat if scope=='within_field_test' else ext
                    row['change_RMSE_from_noisy']=float(np.sqrt(np.mean((pred[indices]-observed[indices])**2)))
                    row['cluster_count']=int(len(np.unique(cl[indices])))
                    if truth is not None: row.update(quality(pred[indices],truth.reshape(-1,bands)[indices]))
                    if lab is not None:
                        yy=lab.ravel()[indices];pp=cl[indices]
                        row['ARI']=float(adjusted_rand_score(yy,pp))
                        if mapping is not None:
                            row['accuracy']=float((yy==pp).mean());row['macro_F1']=float(f1_score(yy,pp,labels=np.arange(k),average='macro',zero_division=0))
                            np.savetxt(folder/f'{method}_{scope}_confusion.csv',confusion_matrix(yy,pp,labels=np.arange(k)),delimiter=',',fmt='%d')
                    rows.append(row)
            np.savez_compressed(folder/'predictions.npz',**{f'{m}_labels':v for m,v in maps.items()},
                                **{f'{m}_cube':v for m,v in recon.items()},axis=axis)
            (folder/'normalization.json').write_text(json.dumps({'mean':mean,'scale':scale,'fitted_on':'training indices only'}),encoding='utf8')
            cmap=ListedColormap(COLORS if k==3 else plt.cm.tab10.colors[:k])
            fig,axs=plt.subplots(1,4,figsize=(13,3))
            axs[0].imshow(labels[1] if labels[1] is not None else noisy[1].mean(-1),cmap=cmap if labels[1] is not None else 'gray')
            axs[0].set_title('Synthetic true classes' if not args.data else 'Raw mean intensity (not reference)')
            for ax,(m,v) in zip(axs[1:],maps.items()): ax.imshow(v,cmap=cmap,vmin=0,vmax=k-1);ax.set_title(m+' + k-means')
            for ax in axs:ax.set_xticks([]);ax.set_yticks([])
            fig.legend(handles=[Patch(color=cmap(i),label=f'Class / cluster {i}') for i in range(k)],loc='lower center',ncol=k,fontsize=8)
            fig.suptitle(f'{source}\nExternal field | noise={sigma} | train split={scheme}',fontsize=10)
            fig.tight_layout(rect=[0,.08,1,1]);savefig(fig,folder/'component_maps');figures.append(str((folder/'component_maps.png').relative_to(out)))
            fig,axs=plt.subplots(1,3,figsize=(11,3))
            for j,(m,v) in enumerate(recon.items()):
                ref=refs[1]
                err=np.sqrt(np.mean((v-ref)**2,axis=-1)) if ref is not None else np.sqrt(np.mean((v-noisy[1])**2,axis=-1))
                im=axs[j].imshow(err,vmin=0,vmax=sigma if sigma else None,cmap='magma');axs[j].set_title(m);fig.colorbar(im,ax=axs[j],shrink=.7)
            fig.suptitle('Synthetic true RMSE map' if not args.data else 'Reference error / change from noisy input (not true error)')
            fig.tight_layout();savefig(fig,folder/'error_maps')
            fig,axs=plt.subplots(1,3,figsize=(12,3))
            for ax,(m,labmap) in zip(axs,maps.items()):
                for cluster in range(k):
                    mask=labmap.ravel()==cluster
                    if mask.any():ax.plot(axis,ext[mask].mean(0),label=f'Cluster {cluster}')
                ax.set_title(m);ax.set_xlabel('Channel / supplied axis');ax.legend(fontsize=7)
            fig.suptitle('Mean RAW spectra by predicted cluster (not chemical identification)',fontsize=10)
            fig.tight_layout();savefig(fig,folder/'cluster_mean_raw_spectra')
            fig,axs=plt.subplots(1,3,figsize=(12,3))
            for j in range(min(k,3)):
                loc=np.flatnonzero(labels[1].ravel()==j)[len(np.flatnonzero(labels[1].ravel()==j))//2] if labels[1] is not None else j*len(ext)//3
                if refs[1] is not None:axs[j].plot(axis,refs[1].reshape(-1,bands)[loc],color='black',label='Clean reference')
                for m in processed:axs[j].plot(axis,spectra[m][loc],label=m,alpha=.75)
                axs[j].set_title(f'Pixel {loc}');axs[j].set_xlabel('Simulated Raman shift (cm-1)' if not args.data else 'Provided axis / channel')
            axs[0].legend(fontsize=7);fig.suptitle(source,fontsize=9);fig.tight_layout();savefig(fig,folder/'spectra')
            fig,axs=plt.subplots(1,2,figsize=(8,3));axs[0].plot(logs[:,0],logs[:,1],label='Train');axs[0].plot(logs[:,0],logs[:,2],label='Validation');axs[0].legend();axs[0].set_title('Noisy-target MSE')
            axs[1].imshow(sm,vmin=-1,vmax=2,cmap=ListedColormap(['#dddddd','#3b82f6','#f59e0b','#10b981']));axs[1].set_title('Gray buffer; blue train; orange val; green test',fontsize=8)
            fig.tight_layout();savefig(fig,folder/'training_and_split')
            print(f'Completed noise={sigma}, split={scheme}',flush=True)
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'metrics.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)
    (out/'leakage_audit.json').write_text(json.dumps(audits,indent=2),encoding='utf8')
    versions={m:__import__(m).__version__ for m in ['numpy','scipy','sklearn','matplotlib','torch']}
    (out/'run_manifest.json').write_text(json.dumps(dict(args=vars(args),source=source,versions=versions,python=platform.python_version(),seconds=time.time()-start),indent=2),encoding='utf8')
    fig,axs=plt.subplots(1,2,figsize=(9,3))
    if not args.data:
        for m in processed:
            rr=[r for r in rows if r['method']==m and r['split']=='spatial' and r['scope']=='external_field']
            axs[0].plot([r['noise_sigma'] for r in rr],[r['RMSE'] for r in rr],'-o',label=m)
            axs[1].plot([r['noise_sigma'] for r in rr],[r['macro_F1'] for r in rr],'-o',label=m)
        axs[0].set_ylabel('Spectral RMSE');axs[1].set_ylabel('Macro F1 (train-matched clusters)')
        axs[1].set_ylim(0,1.05)
        for ax in axs:ax.set_xlabel('Synthetic Gaussian noise sigma');ax.legend(fontsize=8)
        fig.suptitle('SYNTHETIC ONLY | External field | Spatial training split');fig.tight_layout();savefig(fig,out/'quality_summary')
    else:plt.close(fig)
    # Standalone local viewer: no remote scripts and no network connection.
    options=''.join(f'<option value="{f}">{f}</option>' for f in figures)
    html='''<!doctype html><meta charset="utf-8"><title>CH11 results</title><style>body{font:17px system-ui;max-width:1200px;margin:32px auto;background:#f4f7fb;color:#17304c}img{width:100%;background:white}select{padding:10px}</style><h1>化学成像：方法与组分分布</h1><p>SOURCE_TEXT</p><p>此图为类别图，不是浓度图。切换噪声和数据划分查看结果。</p><select id="pick">OPTIONS_TEXT</select><img id="map"><script>const p=document.getElementById('pick'),i=document.getElementById('map');function show(){i.src=p.value}p.onchange=show;show()</script>'''
    (out/'viewer.html').write_text(html.replace('SOURCE_TEXT',source).replace('OPTIONS_TEXT',options),encoding='utf8')
    print(f'Done: {out.resolve()} in {time.time()-start:.1f}s',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',help='NPZ: train_cube,test_cube H,W,B; optional axis, *_labels, *_clean')
    p.add_argument('--output',default='results');p.add_argument('--epochs',type=int,default=80)
    p.add_argument('--seed',type=int,default=725);p.add_argument('--clusters',type=int,default=3)
    experiment(p.parse_args())
