"""Run all three teaching simulations and record exact output and environment."""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[2]
SOURCES=['code/ch17.py']+[f'code/ch17_exercises/{name}'for name in ['01_colorimetric_mdp.py','02_reward_and_shield.py','03_fsm_fault_injection.py']]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
 out=args.out.resolve()
 if out.exists()and any(out.iterdir()):p.error('Choose a new or empty output folder.')
 import numpy as np
 out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
 env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
 proc=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'code/ch17.py')],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 # Preserve the actual output content, normalizing CRLF to LF for portable archives.
 output=proc.stdout.replace(b'\r\n',b'\n')
 (out/'stdout.txt').write_bytes(output)
 manifest={'schema':'ch17-run-archive-v1','data_type':'teaching_simulation','python':platform.python_version(),'numpy':np.__version__,'platform':platform.system(),'exit_code':proc.returncode,'elapsed_seconds':round(time.perf_counter()-start,3),'command':'python -X utf8 code/ch17.py','source_hash_normalization':'CRLF normalized to LF','sources':{name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()for name in SOURCES},'artifacts':{'stdout.txt':hashlib.sha256(output).hexdigest()},'scope':'Default fixed-seed simulations only; not real laboratory validation or an independent external review.'}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(f'Exit code: {proc.returncode}; saved stdout.txt and manifest.json in {out}')
 return proc.returncode

if __name__=='__main__':raise SystemExit(main())
