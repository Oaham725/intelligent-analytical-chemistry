"""Check archived simulation output and source hashes; no training or NumPy needed."""
from pathlib import Path
import argparse,hashlib,json,re

ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'resources/annual/2026-2027/results/ch17'

def verify(folder):
 data=json.loads((folder/'manifest.json').read_text('utf-8'))
 if data.get('schema')!='ch17-run-archive-v1'or data.get('data_type')!='teaching_simulation'or data.get('exit_code')!=0:raise ValueError('Invalid or failed run manifest.')
 for name,digest in data['sources'].items():
  f=(ROOT/name).resolve()
  if not f.is_relative_to(ROOT)or hashlib.sha256(f.read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=digest:raise ValueError('Source checksum differs: '+name)
 for name,digest in data['artifacts'].items():
  f=(folder/name).resolve()
  if not f.is_relative_to(folder.resolve())or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:raise ValueError('Artifact checksum differs: '+name)
 text=(folder/'stdout.txt').read_text('utf-8')
 for token in ['# 练习 1:','# 练习 2:','# 练习 3:','完成 A 信号奖励','完成 B 误差奖励','完成 C 误差奖励+屏蔽器','静默错误(未报警)']:
  if token not in text:raise ValueError('Incomplete simulation output: '+token)
 if not re.search(r'稀释=\s*8\.50',text):raise ValueError('Expected default MDP Q-value not found.')
 print('PASS: three simulations completed; archived output and four source SHA-256 values match.')
 print('This verifies recorded output integrity, not a new training run or independent external review.')

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',type=Path,default=DEFAULT);args=parser.parse_args();verify(args.archive.resolve())
