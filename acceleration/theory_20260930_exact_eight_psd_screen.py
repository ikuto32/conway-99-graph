"""Exact rational necessary PSD census, with immutable per-case checkpoints."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import argparse,gzip,hashlib,importlib.util,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PINS={
 'acceleration/theory_20260930_triplicate_count_psd.py':'d7ee121b54fd7f57a0c666699a2b96931fc7d551257c6411c5bdad27df8607c4',
 B+'independent_review/exact_eight_block_screen/summary.json':'6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a',
 B+'exact_eight_block_screen/surviving_representatives.json.gz':'2cf8ab222d5dd220381fdc14bd225438c173aea40d895353e02f752bc537de5f',
 B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
def h(p):
    with (ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def packed(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0,compresslevel=9)as z:
            z.write((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    start=time.perf_counter();deadline=start+300;out=(ROOT/args.out).resolve();assert out.is_relative_to(ROOT)
    pins=dict(PINS)
    for p in pins:assert h(p)==pins[p],p
    for p in [Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:pins[p]=h(p)
    producer_path=ROOT/'acceleration/theory_20260930_triplicate_count_psd.py'
    spec=importlib.util.spec_from_file_location('frozen_psd_producer',producer_path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    records=json.loads(gzip.decompress((ROOT/(B+'exact_eight_block_screen/surviving_representatives.json.gz')).read_bytes()))['records']
    records=sorted(records,key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']))
    assert len(records)==792 and len({r['canonical_fibre_profile_sha256']for r in records})==792
    if args.resume:
        old=json.loads((out/'manifest.json').read_bytes());assert old['inputs_sha256']==pins
    else:
        out.mkdir(parents=True,exist_ok=False)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,population=792,selection='Complete ordered block survivor population',wall_seconds_per_attempt=300,scope='Necessary real PSD only; literal support/exactly-eight profiles.',shared_components=['Frozen three-profile rational-congruence producer, including its calibration controls. Independent approval remains separate.']))
    attempts=sorted(out.glob('attempt_*.json'));attempt=len(attempts)+1
    save(out/f'attempt_{attempt:03d}.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),resume=args.resume,inputs_sha256=pins))
    controls=helper.controls(read(B+'srg243_residual_fixture/triangle_blocks.json'),deadline);save(out/f'controls_{attempt:03d}.json',controls)
    raw=read(B+'hadamard20_support/six_prism.json');c=raw['core_adjacency'];c2=helper.multiply(c,c)
    g=[[12*int(i==j)-c[i][j]-c2[i][j]+2-int(i//12==j//12)for j in range(36)]for i in range(36)]
    assert g==raw['prescribed_Gram36'];results=[]
    for index,row in enumerate(tqdm(records,desc='Exact PSD profiles',mininterval=1)):
        p=out/f'profile_{index:04d}.json.gz'
        if p.exists():
            assert args.resume
            item=json.loads(gzip.decompress(p.read_bytes()));cp=json.loads((out/f'checkpoint_{index+1:04d}.json').read_bytes())
            assert cp['last_profile_sha256']==h(p.relative_to(ROOT)) and item['canonical_fibre_profile_sha256']==row['canonical_fibre_profile_sha256']
            assert cp['inputs_sha256']==pins
        else:
            if time.perf_counter()>deadline:break
            counts=row['counts'];flat=bytes(v for coord in counts for group in coord for v in group)
            assert len(flat)==720 and hashlib.sha256(flat).hexdigest()==row['canonical_fibre_profile_sha256']
            n=[[counts[a][gg][f]for gg in range(20)]for f in range(3)for a in range(12)]
            ng=helper.gram(n);m=[[3*g[i][j]-ng[i][j]for j in range(36)]for i in range(36)]
            certificate=helper.classify(m,deadline)
            if certificate['status']=='UNKNOWN_RESOURCE_BOUND':save(out/f'unfinished_{attempt:03d}.json',dict(index=index,certificate=certificate));break
            item=dict(index=index,subset_index=row['subset_index'],canonical_fibre_profile_sha256=row['canonical_fibre_profile_sha256'],counts=counts,N36x20=n,G36=g,R36=m,certificate=certificate)
            packed(p,item)
            save(out/f'checkpoint_{index+1:04d}.json',dict(completed=index+1,population=792,last_profile=p.relative_to(ROOT).as_posix(),last_profile_sha256=h(p.relative_to(ROOT)),inputs_sha256=pins))
        results.append(dict(index=index,canonical_fibre_profile_sha256=item['canonical_fibre_profile_sha256'],status=item['certificate']['status'],rank=item['certificate'].get('rank'),certificate_path=p.relative_to(ROOT).as_posix(),certificate_sha256=h(p.relative_to(ROOT))))
    summary=dict(status='CANDIDATE_EXACT_EIGHT_PSD_SCREEN_COMPLETE'if len(results)==792 else'CANDIDATE_EXACT_EIGHT_PSD_SCREEN_RESOURCE_CHECKPOINT',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,completed=len(results),population=792,result_counts=dict(Counter(r['status']for r in results)),rank_counts=dict(Counter(str(r['rank'])for r in results)),results=results,elapsed_seconds=time.perf_counter()-start,independent_approval=False,solver_calls=0,scope='Only necessary triplicate PSD on792 canonical fixed-support count profiles; no factor or target conclusion.',restart_command=[sys.executable,'-B',str(Path(__file__).relative_to(ROOT)),'--out',args.out,'--resume'])
    save(out/f'summary_{attempt:03d}.json',summary);print(json.dumps({k:summary[k]for k in ['status','completed','population','result_counts','rank_counts','elapsed_seconds']}))
if __name__=='__main__':main()
