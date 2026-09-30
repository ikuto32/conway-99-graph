"""Candidate complete792 common-kernel redundancy; exact integer checking."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,itertools,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
PINS={B+'exact_eight_campaign_preparation/campaign_manifest.json':'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',I+'exact_eight_psd_screen/summary.json':'94f6313cbd0bdc6ddef5930a53bb09f22742abe6a3cfe42fccf0cd9416bf259a',I+'exact_eight_campaign_inventory/summary.json':'555ef430f8a84b8b995c98566decf2c6cb92f9e8de6db1645955c0e48dd0f9ea',I+'exact_eight_campaign_inventory/independent_inventory.json.gz':'b2b847af97c907e90ddb928b60958425e7b84fc6793c7297275a3ba7b9ef611a',I+'triplicate_psd_kernel_options/summary.json':'8e1c37fd59bd3993f11f3faef3b514724a17759a208b2173401bbf1434d60f60'}
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def mm(a,b):return [[sum(x*y for x,y in zip(r,c))for c in zip(*b)]for r in a]
def tr(a):return list(map(list,zip(*a)))
def annihilation(g,n,w):
    a=mm(g,w);b=mm(n,mm(tr(n),w));return [[3*x-y for x,y in zip(r,s)]for r,s in zip(a,b)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(exist_ok=False,parents=True);start=time.monotonic();inputs={}
    try:
        for p,v in PINS.items():assert h(p)==v,p;inputs[p]=v
        for p in[Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix(),'uv.lock','pyproject.toml']:inputs[p]=h(p)
        manifest=read(B+'exact_eight_campaign_preparation/campaign_manifest.json');raw=read(B+'hadamard20_support/six_prism.json');rows=manifest['records'];assert len(rows)==792
        inventory=json.loads(gzip.decompress((ROOT/(I+'exact_eight_campaign_inventory/independent_inventory.json.gz')).read_bytes()))['records'];assert [r['case_id']for r in rows]==[r['case_id']for r in inventory]
        c=raw['core_adjacency'];g=[[12*int(i==j)+2-c[i][j]-sum(c[i][k]*c[k][j]for k in range(36))-int(i//12==j//12)for j in range(36)]for i in range(36)];assert g==raw['prescribed_Gram36']
        w=[[int(i%12==a)for a in range(12)]+[int(i//12==f)for f in[1,2]]for i in range(36)]
        # Subtract fibre0/coordinate0 from the two extra selected rows: identity14.
        minor=[w[i][:]for i in list(range(12))+[12,24]]
        for i in[12,13]:minor[i]=[a-b for a,b in zip(minor[i],minor[0])]
        assert minor==[[int(i==j)for j in range(14)]for i in range(14)]
        supports=[]
        for j in range(60):
            s=[a for a in range(12)if raw['L'][a][j]]
            if s not in supports:supports.append(s)
        assert len(supports)==20 and all(len(s)==6 for s in supports)
        words=[v for v in itertools.product(range(3),repeat=6)if all(v.count(f)==2 for f in range(3))];assert len(words)==90
        projections=[]
        for s in supports:
            expected=[int(a in s)for a in range(12)]+[2,2];actual=[[sum(w[12*f+a][k]for a,f in zip(s,v))for k in range(14)]for v in words];assert all(p==expected for p in actual);projections.append(dict(support=s,word_projections=actual))
        controls=[dict(name='identity14 minor after exact row subtraction',passed=True),dict(name='all20x90 word projection identities',passed=True)]
        broken=[row[:]for row in w];broken[0][0]+=1;assert broken!=w and any(sum(broken[12*f+a][0]for a,f in zip(supports[0],v))!=int(0 in supports[0])for v in words);controls.append(dict(name='changed basis entry detected',rejected=True))
        # One-fibre word violates the universal two-per-fibre premise.
        badword=(0,)*6;assert [sum(w[a][k]for a in supports[0])for k in range(14)]!=[int(a in supports[0])for a in range(12)]+[2,2];controls.append(dict(name='invalid fibre multiplicities detected',rejected=True))
        records=[]
        for r,inv in tqdm(zip(rows,inventory),total=792,desc='Common kernel census',unit='profile'):
            n=[[r['raw_representative']['counts'][a][group][f]for group in range(20)]for f in range(3)for a in range(12)];res=annihilation(g,n,w);assert all(x==0 for row in res for x in row),r['case_id']
            records.append(dict(case_id=r['case_id'],case_index=r['case_index'],full_count_profile_sha256=r['full_count_profile_sha256'],integer_annihilation_residual=res,initial_options=sum(inv['initial_domain_sizes']),removed_options=0))
            assert time.monotonic()-start<120
        altered=[row[:]for row in g];altered[0][0]+=1;n0=[[rows[0]['raw_representative']['counts'][a][group][f]for group in range(20)]for f in range(3)for a in range(12)];assert any(x for row in annihilation(altered,n0,w)for x in row);controls.append(dict(name='changed Gram diagonal detected',rejected=True))
        save(out/'basis_and_controls.json',dict(W=w,identity_minor=minor,controls=controls,projections=projections))
        with(out/'cases.json.gz').open('xb')as f:
            with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0)as z:z.write((json.dumps(records,separators=(',',':'))+'\n').encode())
        summary=dict(status='CANDIDATE_COMPLETE792_KERNEL_REDUNDANCY',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():h(p.relative_to(ROOT))for p in out.iterdir()},profiles=792,kernel_dimension=14,rank22_basis='Dependency on the complete independently verified PSD screen; no fresh rank proof by this producer.',initial_options=sum(r['initial_options']for r in records),removed_options=0,elapsed_seconds=time.monotonic()-start,native_calls=0,independent_approval=False,scope='All792 canonical fixed-support scalar/block survivors; necessary local kernel projections only. No Gram factor, residual completion or target conclusion.')
        save(out/'summary.json',summary);print(json.dumps(dict(summary_sha256=h((out/'summary.json').relative_to(ROOT)),options=summary['initial_options'],removed=0)))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),inputs_sha256=inputs,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
