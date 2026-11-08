"""Download public author data. No credentials, cookies or login needed."""
from pathlib import Path
import hashlib,json,urllib.request

root=Path('data/raw');root.mkdir(parents=True,exist_ok=True)
files={'fov1.tif':'1i1N-SlQdlzZjKS6Et971_xX5NVK3VSa-',
       'fov2.tif':'1tS6sPnNA0yym3Os2awbVsXbVBF10dXeW'}
records=[]
for name,file_id in files.items():
    path=root/name
    url=f'https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t'
    if not path.exists():urllib.request.urlretrieve(url,path)
    with path.open('rb') as f:
        header=f.read(4)
        if header not in [b'II*\x00',b'MM\x00*',b'II+\x00',b'MM\x00+']:
            raise RuntimeError(f'{path}: response is not TIFF (possibly download confirmation/error page)')
    with path.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    records.append(dict(name=name,file_id=file_id,url=url,bytes=path.stat().st_size,sha256=sha))
    print(name,path.stat().st_size,sha)
(root/'download_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
