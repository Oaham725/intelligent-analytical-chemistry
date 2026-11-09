"""Frozen-protocol Raman experiment. Run from any working directory."""
from __future__ import annotations
import os
for env in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[env]='1'
import argparse,csv,json,pathlib,platform,hashlib
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import softmax
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV,StratifiedKFold
from sklearn.metrics import accuracy_score,f1_score,log_loss,roc_auc_score,confusion_matrix
import sklearn,scipy,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

BASE=pathlib.Path(__file__).resolve().parents[2]
DATA=BASE/'data/ch15'
OUT=BASE/'resources/annual/2026-2027/results/ch15'
FIG=OUT/'figures'
KNOWN=['Carbonate','Sulphate','Phosphate']
SHORT=KNOWN
UNKNOWN=['Si_O_without_target_anions']
COLORS=['#29657c','#c57845','#699579','#997da3']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','figure.dpi':150,'savefig.dpi':260})

def wilson(k,n):
    if not n:return [None,None]
    z=1.95996398454;p=k/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [float(mid-half),float(mid+half)]

def calibration_bins(y,p,bins=5):
    conf=p.max(axis=1);correct=p.argmax(axis=1)==y;ind=np.minimum(np.floor(conf*bins).astype(int),bins-1)
    rows=[]
    for b in range(bins):
        m=ind==b;n=int(m.sum());k=int(correct[m].sum())
        rows.append({'bin':b,'lower':b/bins,'upper':(b+1)/bins,'n':n,'confidence':float(conf[m].mean()) if n else None,'accuracy':float(correct[m].mean()) if n else None,'accuracy_wilson95':wilson(k,n)})
    return rows

def metrics(y,p):
    pred=p.argmax(axis=1);b=calibration_bins(y,p)
    return {'n':len(y),'accuracy':float(accuracy_score(y,pred)),'accuracy_wilson95':wilson(int((pred==y).sum()),len(y)),'macro_f1':float(f1_score(y,pred,average='macro',zero_division=0)),'nll':float(log_loss(y,p,labels=np.arange(len(KNOWN)))),'brier':float(np.mean(np.sum((p-np.eye(len(KNOWN))[y])**2,axis=1))),'ece_5_equal_bins':float(sum(r['n']*abs(r['accuracy']-r['confidence']) for r in b if r['n'])/len(y)),'calibration_bins':b,'confusion_matrix':confusion_matrix(y,pred,labels=np.arange(len(KNOWN))).tolist()}

def domain_scores(pca,X,tref,qref):
    t=pca.transform(X);res=X-pca.inverse_transform(t)
    t2=np.sum(t*t/np.maximum(pca.explained_variance_,1e-12),axis=1);q=np.sum(res*res,axis=1)
    return t2,q,np.maximum(t2/tref,q/qref)

def split_roles(y,seed):
    rng=np.random.default_rng(seed);roles=np.full(len(y),'unknown_test',dtype='<U20')
    for label in range(len(KNOWN)):
        ix=np.flatnonzero(y==label);rng.shuffle(ix);assert len(ix)==60
        for role,part in [('train',ix[:30]),('prob_calibration',ix[30:40]),('threshold_validation',ix[40:48]),('known_test',ix[48:])]:roles[part]=role
    return roles

def selective_summary(y,p,score,threshold):
    known=y>=0;accepted=score<=threshold
    m=known&accepted;nk=int(m.sum());nu=int((~known).sum());au=int((~known&accepted).sum())
    err=int((p[m].argmax(axis=1)!=y[m]).sum()) if nk else 0
    return {'threshold':float(threshold),'known_n':int(known.sum()),'known_accepted':nk,'known_acceptance':float(nk/known.sum()),'known_rejection':float(1-nk/known.sum()),'accepted_known_error_rate':err/nk if nk else None,'accepted_known_errors':err,'unknown_n':nu,'unknown_accepted':au,'unknown_acceptance':au/nu,'unknown_acceptance_wilson95':wilson(au,nu),'unknown_positive_auroc':float(roc_auc_score(~known,score)),'all_rejected_error_convention':'not applicable'}

def execute(X,y,ids,seed,primary=False):
    roles=split_roles(y,seed);mask={r:roles==r for r in ['train','prob_calibration','threshold_validation','known_test','unknown_test']}
    groups={r:set(ids[m].tolist()) for r,m in mask.items()}
    assert all(not(groups[a]&groups[b]) for a in groups for b in groups if a<b)
    cv=StratifiedKFold(4,shuffle=True,random_state=seed)
    pipe=Pipeline([('pca',PCA(svd_solver='full',random_state=seed)),('clf',LogisticRegression(max_iter=3000,random_state=seed))])
    search=GridSearchCV(pipe,{'pca__n_components':[5,10,20],'clf__C':[.1,1.,10.]},scoring='neg_log_loss',cv=cv,n_jobs=1,error_score='raise')
    search.fit(X[mask['train']],y[mask['train']]);model=search.best_estimator_
    logits=model.decision_function(X)
    cy=y[mask['prob_calibration']];cl=logits[mask['prob_calibration']]
    loss=lambda logt:log_loss(cy,softmax(cl/np.exp(logt),axis=1),labels=np.arange(len(KNOWN)))
    opt=minimize_scalar(loss,bounds=(-4.,4.),method='bounded',options={'xatol':1e-9});assert opt.success
    T=float(np.exp(opt.x));raw=softmax(logits,axis=1);cal=softmax(logits/T,axis=1)
    assert np.array_equal(raw.argmax(axis=1),cal.argmax(axis=1))
    pca=model.named_steps['pca'];train=X[mask['train']]
    tr=pca.transform(train);res=train-pca.inverse_transform(tr)
    tref=max(float(np.quantile(np.sum(tr*tr/np.maximum(pca.explained_variance_,1e-12),axis=1),.95)),1e-12)
    qref=max(float(np.quantile(np.sum(res*res,axis=1),.95)),1e-12)
    t2,q,score=domain_scores(pca,X,tref,qref)
    threshold=float(np.quantile(score[mask['threshold_validation']],.90,method='higher'))
    msp=1-cal.max(axis=1);msp_threshold=float(np.quantile(msp[mask['threshold_validation']],.90,method='higher'))
    kt=mask['known_test'];test=kt|mask['unknown_test']
    before=metrics(y[kt],raw[kt]);after=metrics(y[kt],cal[kt])
    result={'seed':seed,'selected_hyperparameters':search.best_params_,'inner_cv_nll':float(-search.best_score_),'temperature':T,'temperature_log_bounds':[-4,4],'temperature_optimizer_success':bool(opt.success),'calibration_nll_before':float(loss(0)),'calibration_nll_after':float(opt.fun),'role_counts':{r:int(m.sum()) for r,m in mask.items()},'known_before':before,'known_after':after,'tq_rejection':selective_summary(y[test],cal[test],score[test],threshold),'msp_reference':selective_summary(y[test],cal[test],msp[test],msp_threshold),'training_reference_t2_95':tref,'training_reference_q_95':qref,'argmax_invariant':True,'data_leakage_group_overlap':0}
    if primary:
        delta=-np.log(np.maximum(cal[kt][np.arange(kt.sum()),y[kt]],1e-300))+np.log(np.maximum(raw[kt][np.arange(kt.sum()),y[kt]],1e-300))
        rng=np.random.default_rng(seed+9000);boot=delta[rng.integers(0,len(delta),size=(2000,len(delta)))].mean(axis=1)
        result['paired_nll_delta_after_minus_before']={'mean':float(delta.mean()),'bootstrap95':np.quantile(boot,[.025,.975]).tolist(),'bootstrap_samples':2000}
        joblib.dump({'model':model,'T':T,'t2_reference':tref,'q_reference':qref,'threshold':threshold,'labels':KNOWN},OUT/'fitted_model.joblib')
        np.savez_compressed(OUT/'evaluation_arrays.npz',y=y,ids=ids,roles=roles,X_snv=X,raw_probability=raw,cal_probability=cal,t2=t2,q=q,ad_score=score,ad_threshold=threshold)
        with (OUT/'predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
            fields=['rruff_id','role','true_label','predicted_label','confidence_before','confidence_after','t2','q','ad_score','accepted']+['p_before_'+str(i) for i in range(len(KNOWN))]+['p_after_'+str(i) for i in range(len(KNOWN))]
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for i in range(len(ids)):
                row={'rruff_id':ids[i],'role':roles[i],'true_label':KNOWN[y[i]] if y[i]>=0 else 'unknown','predicted_label':KNOWN[cal[i].argmax()],'confidence_before':float(raw[i].max()),'confidence_after':float(cal[i].max()),'t2':float(t2[i]),'q':float(q[i]),'ad_score':float(score[i]),'accepted':bool(score[i]<=threshold)}
                row.update({'p_before_'+str(k):float(raw[i,k]) for k in range(len(KNOWN))});row.update({'p_after_'+str(k):float(cal[i,k]) for k in range(len(KNOWN))});w.writerow(row)
        with (OUT/'inner_cv_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['pca_components','C','mean_validation_nll','rank'])
            for p,v,r in zip(search.cv_results_['params'],search.cv_results_['mean_test_score'],search.cv_results_['rank_test_score']):w.writerow([p['pca__n_components'],p['clf__C'],-v,r])
    print(json.dumps({'seed':seed,'T':T,'accuracy':before['accuracy'],'nll_before':before['nll'],'nll_after':after['nll'],'known_accepted':result['tq_rejection']['known_accepted'],'unknown_accepted':result['tq_rejection']['unknown_accepted']},ensure_ascii=False),flush=True)
    return result

def savefig(fig,stem):
    fig.savefig(FIG/(stem+'.png'),bbox_inches='tight',facecolor='white');fig.savefig(FIG/(stem+'.svg'),bbox_inches='tight',metadata={'Date':None});plt.close(fig)

def plot_results(X,wn,y,ids,summary):
    a=np.load(OUT/'evaluation_arrays.npz',allow_pickle=False);roles=a['roles'];train=roles=='train';kt=roles=='known_test';ut=roles=='unknown_test';test=kt|ut;cal=a['cal_probability'];raw=a['raw_probability'];scores=a['ad_score'];threshold=float(a['ad_threshold'])
    model=joblib.load(OUT/'fitted_model.joblib')['model'];z=model.named_steps['pca'].transform(X)
    fig,ax=plt.subplots(1,2,figsize=(9.2,3.5))
    for k in range(len(KNOWN)):
        m=train&(y==k);ax[0].plot(wn,X[m].mean(axis=0),color=COLORS[k],label=SHORT[k]);ax[1].scatter(z[train&(y==k),0],z[train&(y==k),1],s=15,color=COLORS[k],label=SHORT[k],alpha=.65)
    ax[0].set(xlabel='Raman shift (cm$^{-1}$)',ylabel='Mean SNV intensity',title='Training spectra only (30 / class)');ax[0].legend(fontsize=8,frameon=False)
    ax[1].set(xlabel='PC1 score',ylabel='PC2 score',title='Training PCA scores');fig.tight_layout();savefig(fig,'fig3_spectra_pca')
    fig,axs=plt.subplots(1,2,figsize=(8.8,3.4))
    for ax,p,title in zip(axs,[raw[kt],cal[kt]],['Before calibration','After calibration']):
        bins=calibration_bins(y[kt],p);valid=[b for b in bins if b['n']]
        x=np.array([b['confidence'] for b in valid]);yy=np.array([b['accuracy'] for b in valid]);lo=np.array([b['accuracy_wilson95'][0] for b in valid]);hi=np.array([b['accuracy_wilson95'][1] for b in valid])
        ax.plot([0,1],[0,1],color='#999999',ls='--',lw=1);ax.errorbar(x,yy,yerr=[yy-lo,hi-yy],fmt='o-',color='#29657c',capsize=3)
        for xx,y0,b in zip(x,yy,valid):ax.annotate('n='+str(b['n']),(xx,y0),xytext=(0,8),textcoords='offset points',fontsize=8,ha='center')
        ax.set(xlim=(0,1),ylim=(-.03,1.13),xlabel='Mean top-class probability',ylabel='Empirical accuracy',title=title+' | known test n='+str(kt.sum()))
    fig.tight_layout();savefig(fig,'fig4_reliability')
    fig,axs=plt.subplots(1,2,figsize=(9,3.5))
    axs[0].boxplot([scores[kt],scores[ut]],tick_labels=['Known test ('+str(kt.sum())+')','Unknown ('+str(ut.sum())+')'],showfliers=True)
    axs[0].axhline(threshold,color='#c57845',ls='--',label='Validation threshold');axs[0].set(ylabel='Combined T2 / Q score',title='Domain score distribution');axs[0].legend(frameon=False,fontsize=8)
    errors=(cal.argmax(axis=1)!=y)
    for mask,label,color in [(kt,'Known test only','#29657c'),(test,str(kt.sum())+' known + '+str(ut.sum())+' unknown','#c57845')]:
        ix=np.flatnonzero(mask);ix=ix[np.argsort(scores[ix],kind='stable')];phi=np.arange(1,len(ix)+1)/len(ix);risk=np.cumsum(errors[ix])/np.arange(1,len(ix)+1)
        axs[1].plot(phi,risk,label=label,color=color)
    axs[1].set(xlabel='Accepted fraction',ylabel='Error among accepted',title='Risk vs acceptance | descriptive curves',ylim=(-.02,1.02));axs[1].legend(frameon=False,fontsize=8)
    fig.tight_layout();savefig(fig,'fig5_domain_risk')
    known_wrong=np.flatnonzero(kt&(cal.argmax(axis=1)!=y));unknown_accepted=np.flatnonzero(ut&(scores<=threshold))
    i1=known_wrong[np.argmax(cal[known_wrong].max(axis=1))] if len(known_wrong) else np.flatnonzero(kt)[np.argmin(cal[kt].max(axis=1))]
    i2=unknown_accepted[np.argmax(cal[unknown_accepted].max(axis=1))] if len(unknown_accepted) else np.flatnonzero(ut)[np.argmin(scores[ut])]
    fig,axs=plt.subplots(1,2,figsize=(9.2,3.4))
    for ax,i,title in zip(axs,[i1,i2],['Known misclassification' if len(known_wrong) else 'Least confident known test','Unknown accepted' if len(unknown_accepted) else 'Lowest-score unknown']):
        ax.plot(wn,X[i],color='#29657c');ax.set(xlabel='Raman shift (cm$^{-1}$)',ylabel='SNV intensity',title=title+' | '+ids[i]);ax.text(.02,.97,'Pred: '+SHORT[cal[i].argmax()]+'\np='+f'{cal[i].max():.3f}'+', AD='+f'{scores[i]:.3f}',transform=ax.transAxes,ha='left',va='top',fontsize=8)
    fig.tight_layout();savefig(fig,'fig6_failure_examples')
    return {'known_error_ids':ids[known_wrong].tolist(),'unknown_accepted_ids':ids[unknown_accepted].tolist(),'illustrated_ids':[str(ids[i1]),str(ids[i2])],'known_high_confidence_errors_0_8':ids[known_wrong[cal[known_wrong].max(axis=1)>=.8]].tolist()}

def main():
    global OUT,FIG
    ap=argparse.ArgumentParser();ap.add_argument('--primary-only',action='store_true');ap.add_argument('--output',type=pathlib.Path,default=OUT);args=ap.parse_args()
    OUT=args.output.resolve();FIG=OUT/'figures';FIG.mkdir(parents=True,exist_ok=True)
    data=np.load(DATA/'selected_spectra.npz',allow_pickle=False);X0=data['X'];names=data['y'];ids=data['ids'];wn=data['wavenumber']
    y=np.array([KNOWN.index(s) if s in KNOWN else -1 for s in names]);X=(X0-X0.mean(axis=1,keepdims=True))/X0.std(axis=1,ddof=1,keepdims=True)
    assert np.isfinite(X).all() and len(set(ids))==280
    result=execute(X,y,ids,2026102901,primary=True)
    result['failure_analysis']=plot_results(X,wn,y,ids,result)
    repeats=[result]
    if not args.primary_only:
        for seed in [2026102902,2026102903,2026102904,2026102905]:repeats.append(execute(X,y,ids,seed))
    result['sensitivity_runs']=[{'seed':r['seed'],'accuracy':r['known_before']['accuracy'],'nll_before':r['known_before']['nll'],'nll_after':r['known_after']['nll'],'temperature':r['temperature'],'known_acceptance':r['tq_rejection']['known_acceptance'],'accepted_known_error_rate':r['tq_rejection']['accepted_known_error_rate'],'unknown_acceptance':r['tq_rejection']['unknown_acceptance']} for r in repeats]
    result['versions']={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'scikit_learn':sklearn.__version__,'matplotlib':matplotlib.__version__}
    result['interpretation_limits']=['RRUFF identifiers, not independently audited physical specimens','Ideal-formula string-rule labels, not fully audited mineralogical ground truth','One curated library and 532 nm; no instrument or laboratory external validation','Unknown mixture prevalence is constructed; risk curve not deployment risk','Sensitivity runs reuse the same sample pool and are not independent experiments']
    (OUT/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print('Wrote results/metrics.json and per-sample predictions.',flush=True)

if __name__=='__main__':main()
