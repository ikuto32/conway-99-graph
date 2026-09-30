"""Independent exact Gram matrices, indexed extrema and global block-sum audit."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
import numpy as np
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';DATA=B+'hadamard_count_gram_intervals/';PRE=B+'hadamard_count_master_preflight/'
PINS={DATA+'summary.json':'f8b2af79f5092d2173d5c930d9dbaa2a62c4a0d332f155465090c1a2d907cadf',B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',B+'hadamard_triplicate_counts/local_triples.json':'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',B+'hadamard_six_profile_local_domains/profiles.jsonl.gz':'221d913515ad8e8dedfbca6a9453b2dce1f538462bce1c7cb9f66b202a3bc2a0'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def packed(p):
    with gzip.open(ROOT/p,'rt',encoding='utf8') as f:return json.load(f)
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def controls():
    checked=0
    for domains in [[[(0,1),(1,0)],[(1,1),(2,0)],[(0,0),(0,1)]], [[(0,0),(2,2)],[(1,2),(3,1)]]]:
        sums=[tuple(map(sum,zip(*choice))) for choice in product(*domains)]
        low=[sum(min(v[k] for v in d) for d in domains) for k in range(2)];high=[sum(max(v[k] for v in d) for d in domains) for k in range(2)]
        need(low==list(map(min,zip(*sums))) and high==list(map(max,zip(*sums))),'Cartesian-product extrema')
        need(all(all(low[k]<=v[k]<=high[k] for k in range(2)) for v in sums),'all actual sums positive')
        for k in range(2):need(any(v[k]==low[k] for v in sums) and any(v[k]==high[k] for v in sums),'narrowed-bound corruptions witnessed')
        checked+=len(sums)
    return dict(complete_product_choices=checked,narrowed_bound_corruptions=8,full_research_factor_positive=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,expected=None):
        pins[p]=sha(p);need(expected is None or pins[p]==expected,'input '+p)
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(DATA+'summary.json')
        for field in ('inputs_sha256','outputs_sha256'):
            for p,h in summary[field].items():pin(p,h)
        for p in (Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_COUNT_GRAM_INTERVALS.md','uv.lock','pyproject.toml'):pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,inputs_sha256=pins,limit_seconds=180,producer_imports=False,arithmetic='Exact int16 local binary products<=3; summed global entries<=60.'))
        save(out/'controls.json',controls());raw=read(B+'hadamard20_support/six_prism.json');cat=read(B+'hadamard_triplicate_counts/local_triples.json');words=np.array(cat['words'],dtype=np.int16);triples=np.array(cat['survivors'],dtype=np.int32)
        need(words.shape==(90,6) and triples.shape==(31110,3),'literal catalogue dimensions')
        # Local rows are (coordinate,fibre); columns are the three chosen words.
        values=words[triples].transpose(0,2,1);binary=(values[:,:,None,:]==np.arange(3)[None,None,:,None]).astype(np.int16).reshape(31110,18,3)
        counts=binary.sum(axis=2);grams=binary@binary.transpose(0,2,1);classes=defaultdict(list)
        for i,row in enumerate(counts):classes[tuple(map(int,row))].append(i)
        signatures=sorted(classes);need(len(signatures)==6061,'complete count classes');lookup={s:i for i,s in enumerate(signatures)};classids=np.array([lookup[tuple(map(int,row))] for row in counts])
        old=read(PRE+'local_signatures.json')['signatures'];need(len(old)==6061,'saved class count')
        for i,s in enumerate(signatures):need(old[i]['index']==i and old[i]['counts']==list(s) and old[i]['local_survivor_indices']==classes[s],'complete partition and witness order')
        cells=[(a,b,f,g) for a,b in combinations(range(6),2) for f,g in product(range(3),repeat=2)];rows=np.array([3*a+f for a,b,f,g in cells]);cols=np.array([3*b+g for a,b,f,g in cells]);local=grams[:,rows,cols]
        low=np.full((6061,135),4,dtype=np.int16);high=np.full((6061,135),-1,dtype=np.int16);np.minimum.at(low,classids,local);np.maximum.at(high,classids,local)
        saved=packed(DATA+'signature_intervals.json.gz');need(saved['local_cells']==[list(c) for c in cells],'all local cells')
        def check_interval(record,i):
            need(record['signature_index']==i and record['minimum']==low[i].tolist() and record['maximum']==high[i].tolist(),'complete exact interval')
            for field,extrema in [('minimum_witnesses',low),('maximum_witnesses',high)]:
                witness=record[field];need(len(witness)==135 and all(type(j)is int and 0<=j<31110 for j in witness),'witness indices')
                need(np.all(classids[witness]==i) and np.all(local[witness,np.arange(135)]==extrema[i]),'extremum attained in exact class')
        need(len(saved['records'])==6061,'all interval records')
        for i,r in enumerate(saved['records']):check_interval(r,i)
        groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)));need(len(groups)==20 and all(len(g)==6 for g in groups),'literal supports')
        # Embed full symmetric local interval matrices; retain diagonal counts.
        lm=np.zeros((6061,18,18),dtype=np.int16);um=lm.copy();lm[:,rows,cols]=low;lm[:,cols,rows]=low;um[:,rows,cols]=high;um[:,cols,rows]=high
        lm[:,np.arange(18),np.arange(18)]=np.array(signatures);um[:,np.arange(18),np.arange(18)]=np.array(signatures)
        maps=[np.array([a+12*f for a in support for f in range(3)]) for support in groups]
        globalcells=[(a,b,f,g) for a,b in combinations(range(12),2) if a//2!=b//2 for f,g in product(range(3),repeat=2)];gr=np.array([a+12*f for a,b,f,g in globalcells]);gc=np.array([b+12*g for a,b,f,g in globalcells]);target=np.array(raw['prescribed_Gram36'],dtype=np.int16);targets=target[gr,gc]
        screen=packed(DATA+'profile_screens.json.gz');need(screen['global_cells']==[list(c) for c in globalcells] and len(globalcells)==540,'all global cells')
        def computed(table):
            selected=[lookup[tuple(v for a in support for v in table[a][g])] for g,support in enumerate(groups)];lower=np.zeros((36,36),dtype=np.int16);upper=lower.copy()
            for g,idx in enumerate(maps):lower[np.ix_(idx,idx)]+=lm[selected[g]];upper[np.ix_(idx,idx)]+=um[selected[g]]
            return selected,lower[gr,gc].tolist(),upper[gr,gc].tolist()
        def check_screen(record,table):
            selected,lo,hi=computed(table);need(record['group_signature_indices']==selected and record['lower_bounds']==lo and record['upper_bounds']==hi,'all exact block-summed bounds');bad=np.flatnonzero((targets<lo)|(targets>hi)).tolist();need([r['cell_index'] for r in record['violations']]==bad,'complete ordered violation list')
            for r,k in zip(record['violations'],bad):
                a,b,f,g=globalcells[k];need(r['coordinates']==[a,b] and r['fibres']==[f,g] and r['target']==int(targets[k]) and r['lower']==lo[k] and r['upper']==hi[k],'literal violated row')
                expected=[]
                for j,support in enumerate(groups):
                    if a in support and b in support:
                        c=cells.index((support.index(a),support.index(b),f,g));sid=selected[j];sr=saved['records'][sid];expected.append(dict(group=j,signature_index=sid,local_cell=c,minimum=int(low[sid,c]),maximum=int(high[sid,c]),minimum_witness=sr['minimum_witnesses'][c],maximum_witness=sr['maximum_witnesses'][c]))
                need(len(expected)==5 and r['terms']==expected,'all five literal contribution terms')
            return bool(bad)
        balanced=[[[1,1,1] if a in support else [0,0,0] for support in groups] for a in range(12)];bc=read(DATA+'balanced_count_control.json');need(bc['counts']==balanced and bc['full_factor'] is False and not check_screen(bc['screen'],balanced),'balanced count-relaxation positive')
        with gzip.open(ROOT/(B+'hadamard_six_profile_local_domains/profiles.jsonl.gz'),'rt',encoding='utf8') as f:profiles=[json.loads(line) for line in f]
        need(len(profiles)==len(screen['records'])==984,'all frozen calibration profiles');excluded=[];tables=[]
        for i,p in enumerate(tqdm(profiles,desc='Independent block-sum interval audit',mininterval=1)):
            table=deepcopy(balanced)
            for a in range(12):
                for side,g in enumerate(p['group_ids']):table[a][g]=[table[a][g][f]+p['coordinate_fibre_deviations'][a][f][side] for f in range(3)]
            r=screen['records'][i];need(r['index']==i and r['id']==p['id'] and r['profile_sha256']==p['profile_sha256'],'exact profile identity')
            if check_screen(r,table):excluded.append(p['id'])
            if i<2:tables.append(table)
            need(time.monotonic()-start<180,'audit allocation')
        need(read(DATA+'excluded_profile_ids.json')['ids']==excluded and len(excluded)==summary['interval_excluded_profiles']==546 and 984-len(excluded)==summary['interval_surviving_profiles']==438,'complete exclusion population');need(sum(len(r['violations']) for r in screen['records'])==summary['total_failed_cells']==1104,'all failed cells')
        corrupt=[]
        for field in ('minimum','maximum','minimum_witnesses','maximum_witnesses'):
            r=deepcopy(saved['records'][0]);r[field][0]=r[field][0]+1 if 'witness' not in field else -1
            try:check_interval(r,0)
            except ValueError:corrupt.append(field)
            else:raise ValueError('corrupted interval accepted')
        for field in ('lower_bounds','upper_bounds','group_signature_indices'):
            r=deepcopy(screen['records'][0]);r[field][0]+=1
            try:check_screen(r,tables[0])
            except ValueError:corrupt.append(field)
            else:raise ValueError('corrupted screen accepted')
        first=next(i for i,r in enumerate(screen['records']) if r['violations']);need(first==1,'first violation position');r=deepcopy(screen['records'][first]);r['violations'][0]['target']+=1
        try:check_screen(r,tables[first])
        except ValueError:corrupt.append('wrong_target')
        else:raise ValueError('corrupted target accepted')
        r=deepcopy(screen['records'][first]);r['violations']=[]
        try:check_screen(r,tables[first])
        except ValueError:corrupt.append('missing_violation')
        else:raise ValueError('missing violation accepted')
        save(out/'checked_records.json',dict(excluded_profile_ids=excluded,rejected_artifact_corruptions=corrupt,all_extremal_witnesses_checked=6061*270,all_global_bounds_checked=984*540*2))
        now=datetime.now(timezone.utc).isoformat();scope='One literal support; exact necessary coefficient-wise Gram bounds for arbitrary local count signatures. Complete finite calibration on the984 saved exactly-six-exception profiles only.';limits=['Surviving intervals do not prove simultaneous local choices, a full factor, residual completion or a target graph.','All984 calibration profiles were already excluded by a stronger independently checked route; no new whole-support or target exclusion follows.','The prior complete31110 local-catalogue census is a pinned premise, not re-enumerated here.'];shared=['Previously independently checked literal support and complete local catalogue.','Python and NumPy exact int16 products and indexed reductions; no producer imports.']
        binding=dict(id='C-FIXED-HADAMARD-COUNT-SIGNATURE-GRAM-INTERVALS',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For every factor on the pinned support whose local triples belong to the complete31110-option catalogue, each full Gram entry is bounded below and above by the sums of the exact selected local-count-class minima and maxima. The saved6061 classes contain complete exact135-cell extrema and attaining witnesses. On the984 frozen six-exception count profiles, exactly546 violate at least one of540 recorded bounds (1104 violations), and438 survive.',scope=scope,assumptions=['Pinned literal support, prescribed Gram, complete local-triple catalogue and frozen984 calibration profiles.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-EXCEPTION-LOCAL-DOMAIN-FILTER',revision=1,relation='coverage')],verifier='/root',producer='/root/eight_domain_audit',checking_method='Rebuilt binary local Gram matrices, complete indexed extrema and witnesses, full36x36 block sums and all frozen profile violations; independent scalar-bound argument.',shared_components=shared,limitations=limits,artifact_hashes=pins,created_at=now,updated_at=now)
        save(out/'claim_binding.json',binding);result=dict(status='INDEPENDENT_COUNT_SIGNATURE_GRAM_INTERVALS_PASS',timestamp=now,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT).as_posix()) for p in out.iterdir()},local_classes=6061,local_coefficients=6061*135,extremal_witnesses=6061*270,profiles=984,global_cells_per_profile=540,excluded_profiles=546,surviving_profiles=438,failed_cells=1104,rejected_artifact_corruptions=len(corrupt),scope=scope,shared_components=shared,limitations=limits,native_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__).relative_to(ROOT).as_posix()),inputs_sha256=pins));raise
if __name__=='__main__':main()
