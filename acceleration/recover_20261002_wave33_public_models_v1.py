"""Restore exactly five public model inputs using the unchanged byte checker.

CI engineering only. All child checks share the outer supported invocation;
this helper launches no solver and performs no mathematical verification.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
PACKAGES={
 'acceleration/results/20261002_wave33_model_package01/manifest.json':'c3efa198c5f48eddb5ead69a4bb130a3dc55567bb298856143c6fb62eb0e0145',
 'acceleration/results/20261002_wave33_reconstruction_package01/manifest.json':'f639431b7ea9ce0f1500ea48b002629d2523271eead700217dd512e8ade66989',
}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--destination-dir',type=Path,default=ROOT)
 args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
 deadline=CommandDeadline(args.seconds,allocation_reason='Exact five public structural model inputs, existing immutable gzip payloads and unchanged independent byte checker')
 for index,(name,identity) in enumerate(PACKAGES.items()):
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=identity:raise ValueError('exact public payload manifest')
  if deadline.status()['stop_required'] or deadline.status()['remaining_seconds']<20:raise ValueError('not completed within allocated budget')
  command=[sys.executable,str(ROOT/'acceleration/recover_20261001_twentyninth_raw_artifacts.py'),'--manifest',str(ROOT/name),'--manifest-sha256',identity,'--destination-dir',str(args.destination_dir.resolve()),'--receipt',str(out/f'recovery_{index:02d}.json')]
  subprocess.run(command,cwd=ROOT,check=True,timeout=max(1,deadline.status()['remaining_seconds']-10))
 receipts=[json.loads((out/f'recovery_{index:02d}.json').read_bytes()) for index in range(2)]
 raw_count=sum(r['originals'] for r in receipts)
 if raw_count!=5:raise ValueError('exact five raw inputs')
 summary=dict(status='WAVE33_PUBLIC_MODELS_RECOVERED',raw_inputs=raw_count,raw_bytes=sum(r['raw_bytes'] for r in receipts),mathematical_verification=False,receipts=[str(out/f'recovery_{i:02d}.json') for i in range(2)],deadline=deadline.status())
 with (out/'summary.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(summary,stream,indent=2);stream.write('\n')
 print(json.dumps(summary))

if __name__=='__main__':main()
