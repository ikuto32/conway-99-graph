"""Independent count-profile screen check through the complete approved extrema table."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';SCREEN=B+'count_witness_interval_screen/';TABLE=B+'hadamard_count_gram_intervals/signature_intervals.json.gz';PROFILE=B+'hadamard_count_master_native_pilot_v2/independent_object/independent_count_profile.json'
PINS={SCREEN+'summary.json':'f2e6970b124bbb1274ea0c6dc272ba914d5ab23968df8e64be4738fb9a0d06ef',TABLE:'41c4269eb86477069e63900e14296e88734d668a160907f5ce1f0277d2cd230a',PROFILE:'0714d44765e29a4f0bf5c0769a25a5ed805a9602ae9a5f25b8c327ce4afe3152',B+'independent_review/count_gram_intervals/summary.json':'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33',B+'independent_review/count_master_sat_outcome/summary.json':'61e7eb9643902c866617a270d856a521f71f5b2723c0e731edae3896baba484d'}
def sha(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def need(x,msg):
    if not x:raise ValueError(msg)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    for p,h in PINS.items():need(sha(p)==h,'exact premise '+p);pins[p]=h
    summary=read(SCREEN+'summary.json')
    for field in ['inputs_sha256','outputs_sha256']:
        for p,h in summary[field].items():need(sha(p)==h,'saved input/output '+p);pins[p]=h
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__).relative_to(ROOT).as_posix())
    profile=read(PROFILE);counts=profile['coordinate_group_fibre_counts'];raw=read(B+'hadamard20_support/six_prism.json');groups=list(dict.fromkeys(tuple(i for i in range(12) if raw['L'][i][j]) for j in range(60)));sigs=read(B+'hadamard_count_master_preflight/local_signatures.json')['signatures'];lookup={tuple(s['counts']):s['index'] for s in sigs}
    with gzip.open(ROOT/TABLE,'rt',encoding='utf8') as f:table=json.load(f)
    selected=[lookup[tuple(x for i in group for x in counts[i][g])] for g,group in enumerate(groups)];need(selected==profile['selected_global_signature_indices'],'literal count-class identities')
    cellindex={tuple(c):j for j,c in enumerate(table['local_cells'])};records=[]
    for x,y in combinations(range(12),2):
        if x//2==y//2:continue
        for f,h in product(range(3),repeat=2):
            terms=[]
            for g,group in enumerate(groups):
                if x not in group or y not in group:continue
                j=cellindex[group.index(x),group.index(y),f,h];r=table['records'][selected[g]];terms.append(dict(group=g,signature_index=selected[g],local_cell=j,minimum=r['minimum'][j],maximum=r['maximum'][j],minimum_witness=r['minimum_witnesses'][j],maximum_witness=r['maximum_witnesses'][j]))
            need(len(terms)==5,'five literal groups');lo=sum(t['minimum'] for t in terms);hi=sum(t['maximum'] for t in terms);target=raw['prescribed_Gram36'][12*f+x][12*h+y];records.append(dict(coordinates=[x,y],fibres=[f,h],target=target,lower=lo,upper=hi,passes=lo<=target<=hi,terms=terms))
    expected=dict(profile_sha256=profile['profile_sha256'],selected_signatures=selected,records=records);need(read(SCREEN+'all540_intervals.json')==expected,'all540 exact coefficients, extrema witnesses and results')
    need(len(records)==540 and all(r['passes'] for r in records),'complete survival, no factor claim')
    local=read(SCREEN+'selected_local_extrema.json')['records']
    need([r['signature_index'] for r in local]==sorted(set(selected)),'complete selected classes')
    for r in local:
        i=r['signature_index'];need(r['local_triples']==sigs[i]['local_survivor_indices'],'complete class membership')
        for field in ['minimum','maximum']:need(r[field]==table['records'][i][field],'independent earlier-table extrema')
    corrupt=[]
    for field in ['lower','upper','target','passes']:
        bad=deepcopy(expected);v=bad['records'][0][field];bad['records'][0][field]=not v if type(v)is bool else v+1
        need(bad!=expected,'corruption detected');corrupt.append(field)
    bad=deepcopy(expected);bad['records'].pop();need(bad!=expected,'missingcell detected');corrupt.append('missing_cell')
    certificate=read(SCREEN+'certificate.json');need(certificate['failed_cells']==[] and certificate['profile_sha256']==profile['profile_sha256'] and certificate['count_profile_sha256']==PINS[PROFILE] and certificate['exceptional_groups']==profile['exceptional_groups'] and not certificate['full_factor'] and not certificate['target_resolution'],'exact certificate object and limitations')
    result=dict(status='INDEPENDENT_EIGHT_COUNT_WITNESS_INTERVAL_SCREEN_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256=pins,profile_sha256=profile['profile_sha256'],checked_cells=540,violations=0,selected_local_classes=len(local),rejected_corruptions=corrupt,verifier='/root',producer='/root/eight_domain_audit',checking_method='Raw counts mapped to complete previously independently approved count-class extrema table; all literal terms/records/witnesses compared. No producer imports.',shared_components=['Pinned raw count profile and independently verified interval table.','Python exact integer arithmetic.'],scope='This exact count profile satisfies all540 necessary scalar bounds; no simultaneous full factor or graph follows.',ledger_claim_note='Supporting evidence for the forthcoming complete interval-CSP witness, not a new exclusion.',elapsed_seconds=time.monotonic()-start,native_calls=0,target_resolution=False)
    with (out/'summary.json').open('x',encoding='utf8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs_sha256'}))
if __name__=='__main__':main()
