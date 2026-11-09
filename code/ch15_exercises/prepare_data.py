"""Build a checksum-pinned, grouped RRUFF subset from Celestian's public archive."""
from __future__ import annotations
import argparse,csv,hashlib,json,pathlib,pickle,re,urllib.request,collections,html
import numpy as np

BASE=pathlib.Path(__file__).resolve().parents[2]
DATA=BASE/'data/ch15'
SOURCE_NAME='RamanLab_Database_20250602.sqlite'
SOURCE_URL='https://zenodo.org/api/records/15717961/files/'+SOURCE_NAME+'/content'
SHA256='361888e8e8ea9355205b43d3440cdb066975bac0fdd53be19e47f87afc107c89'
KNOWN=['Carbonate','Sulphate','Phosphate']
UNKNOWN=['Si_O_without_target_anions']
SEED=2026102901

class DataOnlyUnpickler(pickle.Unpickler):
    def find_class(self,module,name):raise pickle.UnpicklingError(f'Executable global rejected: {module}.{name}')

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=pathlib.Path);args=ap.parse_args()
    source=args.source or DATA/'cache'/SOURCE_NAME
    if not source.exists():
        source.parent.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen(SOURCE_URL,timeout=90) as r,source.open('wb') as out:
            while b:=r.read(1024*1024):out.write(b)
    assert digest(source)==SHA256,'Source checksum mismatch'
    with source.open('rb') as f:database=DataOnlyUnpickler(f).load()
    assert isinstance(database,dict)
    grid=np.arange(200.,1200.1,2.)
    excluded_file=DATA/'pilot_excluded_ids.csv'
    assert excluded_file.exists(),'The pilot-exclusion manifest must be supplied.'
    excluded={r['rruff_id'] for r in csv.DictReader(excluded_file.open(encoding='utf-8-sig'))}
    assert len(excluded)==340
    selected={};reject=collections.Counter();label_sets=collections.defaultdict(set);label_audit=[]
    for key,rec in sorted(database.items()):
        parts=key.split('__');meta=rec.get('metadata',{});g=re.search(r'R\d{6}',key)
        if not g or 'rruff' not in str(meta.get('URL','')).lower():reject['not_rruff_identifiable']+=1;continue
        if len(parts)<4 or parts[3]!='532' or 'unoriented' not in key or 'Processed' not in key:reject['acquisition_or_processing_filter']+=1;continue
        gid=g.group()
        if gid in excluded:reject['pilot_identifier_excluded']+=1;continue
        formula=html.unescape(str(meta.get('IDEAL CHEMISTRY',''))).replace('_','').replace('^','').replace(' ','')
        hits=[l for l,pattern in [('Carbonate','CO3'),('Sulphate','SO4'),('Phosphate','PO4'),('Arsenate','AsO4')] if pattern in formula]
        if len(hits)==1 and hits[0] in KNOWN:label=hits[0]
        elif not hits and 'Si' in formula and 'O' in formula:label=UNKNOWN[0]
        else:reject['not_unambiguous_formula_task']+=1;continue
        wn=np.asarray(rec.get('wavenumbers',[]),dtype=float);v=np.asarray(rec.get('intensities',[]),dtype=float)
        if len(wn)!=len(v) or len(wn)<20 or not(np.isfinite(wn).all() and np.isfinite(v).all()):reject['invalid_numeric']+=1;continue
        order=np.argsort(wn);wn,v=wn[order],v[order]
        wn,index=np.unique(wn,return_index=True);v=v[index]
        if wn[0]>200 or wn[-1]<1200:reject['does_not_cover_window']+=1;continue
        x=np.interp(grid,wn,v)
        if x.std()<1e-12:reject['constant_spectrum']+=1;continue
        label_sets[gid].add(label)
        if gid in selected:reject['same_rruff_id']+=1;continue
        selected[gid]={'rruff_id':gid,'class_label':label,'mineral_name':parts[0],'ideal_formula':formula,'source_catalog_class':str(meta.get('HEY CLASSIFICATION','')),'source_record':key,'source_url':'https://rruff.info/'+gid,'laser_nm':532,'axis_unit':'cm^-1','status':str(meta.get('STATUS','')),'x':x,'spectrum_sha256':hashlib.sha256(x.astype('<f8').tobytes()).hexdigest()}
    conflicts=[g for g,s in label_sets.items() if len(s)>1]
    for g in conflicts:selected.pop(g,None)
    reject['class_conflicting_groups']=len(conflicts)
    unique={};seen={}
    for gid,rec in sorted(selected.items()):
        # Exact duplicate signal cannot occur in different split roles.
        fingerprint=rec['spectrum_sha256']
        if fingerprint in seen:reject['identical_interpolated_spectrum']+=1;continue
        seen[fingerprint]=gid;unique[gid]=rec
    counts=collections.Counter(r['class_label'] for r in unique.values())
    rng=np.random.default_rng(SEED);records=[]
    for label in KNOWN+UNKNOWN:
        pool=sorted((r for r in unique.values() if r['class_label']==label),key=lambda r:r['rruff_id'])
        n=60 if label in KNOWN else 100
        assert len(pool)>=n,(label,len(pool),n)
        chosen=rng.choice(len(pool),size=n,replace=False)
        records.extend(pool[int(i)] for i in chosen)
    records.sort(key=lambda r:(KNOWN+UNKNOWN).index(r['class_label'])*1000000+int(r['rruff_id'][1:]))
    dest=DATA;dest.mkdir(exist_ok=True)
    X=np.vstack([r['x'] for r in records]);ids=np.array([r['rruff_id'] for r in records]);y=np.array([r['class_label'] for r in records])
    assert len(set(ids))==len(ids)==280 and not(set(ids)&excluded)
    np.savez_compressed(dest/'selected_spectra.npz',X=X,ids=ids,y=y,wavenumber=grid)
    fields=[k for k in records[0] if k!='x']
    with (dest/'sample_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in records)
    audit={'source_doi':'10.5281/zenodo.15717961','source_sha256':SHA256,'source_records':len(database),'source_format':'data-only pickle dictionary despite .sqlite name','source_declared_license':'CC BY 4.0','label_definition':'deterministic unambiguous ideal-formula motif rules, not source catalog category','pilot_identifiers_excluded':len(excluded),'pilot_overlap':len(set(ids)&excluded),'filters':dict(reject),'available_unique_counts':dict(counts),'selected_counts':dict(collections.Counter(y.tolist())),'selected_samples':len(ids),'spectral_points':len(grid),'range_cm_1':[200,1200],'laser_nm':532,'duplicate_group_count':len(ids)-len(set(ids)),'duplicate_signal_count':len(ids)-len(set(r['spectrum_sha256'] for r in records)),'seed':SEED,'selection_used_model_performance':False}
    (dest/'data_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
