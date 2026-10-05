"""Independent dense-integer checking of one finite selected graph export.

No exporter imports. Complete census correctness is reused only through exact
hash-bound ROOT reports; every eligible graph is freshly multiplied here.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import numpy as np
from tqdm import tqdm
from command_deadline import CommandDeadline
from audit_20261003_two_line_dense_delta_v1 import adjacency, energy

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/audit_20261003_root_focused_start_v1.py'
SPEC = 'acceleration/audit_20261003_root_focused_start_v1_spec.md'
EXPORT = 'acceleration/results/20261003_root_focused_start_export01'
CHECKING = {
 'acceleration/audit_20261003_two_line_dense_delta_v1.py':'f51001bda1ca5e197960e2bb2b54ea06e4c8044c9e104d969b3f6106e713d1bd',
 'acceleration/command_deadline.py':'9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
 'acceleration/run_compute_command.py':'593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'acceleration/export_20261003_root_focused_start_v2.py':'51036a982b2a1e1251e805a5e9f9a8e560d4158f1d118ff48cb21cc2f7d44d05',
 'acceleration/export_20261003_root_focused_start_v2_spec.md':'dedc032415e0a6a458faa49fe6819649070ea8ad046fbc4b540e12df32235d6b',
 EXPORT+'/summary.json':'9a3185e7dd28aaae6fbce16f9606394a950012e38beaa0e5a776755e84561443',
}
CENSUSES = (
 ('original','20261003_weight60_two_line_census01','70f4ec893d5ba443effdd29cd6e3d472d736e590af56691b751e822bbae49ffa',
  'two_line_full01','1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589',
  'INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS',187,
  'acceleration/results/20261003_hypergraph_weight60_warm01/native/final.state','c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b',
  'acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj','9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d'),
 ('neighbor','20261003_weight60_two_line_neighbor_census01','15874e9fa9b2f83f9e811ca4efa3e7892fa81e0ebf026778d545466724720480',
  'two_line_neighbor_full01','24c20b8454ba2ac16501e3d7ae49dadf922b1870d6ed72706e9ce8349d4a26e0',
  'INDEPENDENT_TWO_LINE_COMPLETE_NEUTRAL_GRAPH_CENSUS_V3_PASS',186,
  'acceleration/results/20261003_weight60_two_line_census01/best_neighbor_triples.json','11074c406a0b6902e7dcccdd50f1a2e36104a6b964948b3f3fd5299ecdce2968',
  'acceleration/results/20261003_weight60_two_line_census01/best_neighbor.adj','02d66dc7fb84f91b29be399abe760b452f85b6d79c6c37c681e566e6f4c809bd'),
)

def need(ok, why):
    if not ok: raise ValueError(why)

def digest(data): return hashlib.sha256(data).hexdigest()
def filehash(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def unique(pairs):
    d={}
    for k,v in pairs:
        need(k not in d,'duplicate JSON key');d[k]=v
    return d
def decode(data): return json.loads(data,object_pairs_hook=unique)
def canonical(obj): return (json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()
def write(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as f: json.dump(obj,f,indent=2);f.write('\n')
def guard(deadline): need(deadline.status()['remaining_seconds']>20,'not completed within the allocated budget')

def matrix_bytes(a): return (str(len(a))+'\n'+''.join(''.join(map(str,row))+'\n' for row in a.tolist())).encode()

def dense_score(triples,n=99,d=7,root=11):
    a=adjacency(n,d,triples);cn=a@a
    need(type(root) is int and 0<=root<n,'root domain')
    lam,mu,rr=energy(a,cn,root)
    outs=[];pairs=Counter()
    for v in range(n):
        if v==root or a[root,v]:continue
        support=np.flatnonzero(a[root]&a[v]).tolist()
        outs.append(dict(vertex=v,root_neighbors=support,common_neighbors=len(support)))
        if len(support)==2:pairs[tuple(support)]+=1
    ah=Counter(int(cn[root,v]) for v in range(n) if a[root,v])
    nh=Counter(int(cn[root,v]) for v in range(n) if v!=root and not a[root,v])
    raw=matrix_bytes(a)
    score=dict(n=n,degree=d,root=root,lambda_energy=lam,mu_energy=mu,root_residual=rr,
       root_objective=60*lam+rr,base_energy=lam+mu,matrix_sha256=digest(raw),root_neighbors=np.flatnonzero(a[root]).tolist(),
       adjacent_cn_histogram={str(k):v for k,v in sorted(ah.items())},nonadjacent_cn_histogram={str(k):v for k,v in sorted(nh.items())},
       outsider_supports=outs,pair_support_multiplicities=[dict(pair=list(k),multiplicity=v) for k,v in sorted(pairs.items())],support_pair_uniqueness_assumed=False)
    return score,raw,a,cn

def trade(base,rec):
    m=len(base);pid=rec['proposal_id'];need(type(pid) is int and 0<=pid<m*(m-1)//2*9,'proposal label')
    # Decode the triangular lex order without an exporter combinations table.
    pair=pid//9;i=0
    while pair>=m-i-1:pair-=m-i-1;i+=1
    j=i+1+pair;ix=(pid%9)//3;jy=pid%3
    need(all(type(rec[k]) is int and rec[k]==v for k,v in [('i',i),('j',j),('ix',ix),('jy',jy)]),'proposal positions')
    need(rec['old_triples']==[base[i],base[j]],'literal old rows')
    x,y=base[i][ix],base[j][jy];need(x not in base[j] and y not in base[i],'exclusive points')
    out=copy.deepcopy(base);out[i][ix],out[j][jy]=y,x
    need(rec['new_triples']==[out[i],out[j]],'literal new rows')
    return out

def parse_native(data,expected):
    lines=data.decode('ascii').splitlines();n,d,root=expected['n'],expected['degree'],expected['root']
    need(lines[:4]==['ROOT_FOCUSED_GRAPH_INPUT_V1',f'n {n}',f'degree {d}',f'root {root}'],'native header/root')
    keys=['source_matrix_sha256','source_triples_sha256','selection_report_sha256']
    need(len(lines)==9+n*d//3 and lines[-1]=='END','native complete record population')
    for i,k in enumerate(keys,4):need(lines[i]==k+' '+expected[k],'native provenance')
    need(lines[7]==f'triples {n*d//3}','native triple count')
    rows=[]
    for line in lines[8:-1]:
        cells=line.split();need(len(cells)==3 and all(s.isdecimal() and s==str(int(s)) for s in cells),'native canonical integer rows');rows.append(list(map(int,cells)))
    adjacency(n,d,rows)
    need(rows==expected['triples'],'native ordered rows')
    return rows

def calibration(deadline,out):
    rook=[[3*r+c for c in range(3)] for r in range(3)]+[[3*r+c for r in range(3)] for c in range(3)]
    s,raw,a,cn=dense_score(rook,9,2,0)
    scalar=np.array([[sum(int(a[u,k])*int(a[k,v]) for k in range(9)) for v in range(9)] for u in range(9)],dtype=np.int64)
    need(np.array_equal(cn,scalar) and (s['lambda_energy'],s['mu_energy'],s['root_residual'])==(0,0,0),'rook exact positive')
    need(np.array_equal(cn,2*np.eye(9,dtype=np.int64)-a+2*np.ones((9,9),dtype=np.int64)),'rook integer SRG identity')
    positive=3;neg=[]
    def reject(label,call):
        guard(deadline)
        try:call()
        except (ValueError,KeyError,TypeError,UnicodeError) as error:neg.append(dict(label=label,error=str(error)));return
        raise ValueError('accepted calibration corruption '+label)
    for label,changed in [('bool_label',[[False,1,2],*rook[1:]]),('duplicate_line',[*rook[:-1],rook[0]]),('missing_line',rook[:-1]),('outside_label',[[9,1,2],*rook[1:]])]:reject(label,lambda changed=changed:dense_score(changed,9,2,0))
    e=dict(n=9,degree=2,root=0,source_matrix_sha256='a'*64,source_triples_sha256='b'*64,selection_report_sha256='c'*64,triples=rook)
    text='ROOT_FOCUSED_GRAPH_INPUT_V1\nn 9\ndegree 2\nroot 0\nsource_matrix_sha256 '+e['source_matrix_sha256']+'\nsource_triples_sha256 '+e['source_triples_sha256']+'\nselection_report_sha256 '+e['selection_report_sha256']+'\ntriples 6\n'+''.join(' '.join(map(str,t))+'\n' for t in rook)+'END\n'
    need(parse_native(text.encode(),e)==rook,'native positive');positive+=1
    for label,changed in [('root',text.replace('root 0','root 1')),('provenance',text.replace('a'*64,'d'*64)),('missing_row',text.replace('0 1 2\n','')),('leading_zero',text.replace('0 1 2\n','00 1 2\n')),('trailing',text+'END\n'),('changed_frozen_literal',text.replace('0 1 2\n','1 0 2\n'))]:reject('native_'+label,lambda changed=changed:parse_native(changed.encode(),e))
    reject('duplicate_JSON',lambda:decode(b'{"root":0,"root":1}'))
    base=[[0,1,2],[3,4,5]];rec=dict(proposal_id=0,i=0,j=1,ix=0,jy=0,old_triples=base,new_triples=[[3,1,2],[0,4,5]])
    need(trade(base,rec)==[[3,1,2],[0,4,5]],'trade positive');positive+=1
    for label,key,value in [('bool_id','proposal_id',False),('bad_label','proposal_id',9),('bad_position','ix',1),('bad_new','new_triples',base)]:
        bad=copy.deepcopy(rec);bad[key]=value;reject(label,lambda bad=bad:trade(base,bad))
    return dict(positive_controls=positive,strict_negative_controls=neg,strict_negative_count=len(neg),all_products_exact=True,calibration_timing='After producer export; before this full independent check. No pre-producer calibration is claimed.')

def full(deadline,out,pin,read,args):
    cal=read(args.calibration,args.calibration_sha256)
    need(cal['status']=='INDEPENDENT_ROOT_FOCUSED_START_V1_PREFULL_CALIBRATION_PASS' and cal['inputs_sha256'][SELF]==filehash(ROOT/SELF),'fresh source-bound calibration')
    selected=read(EXPORT+'/selection.json','9a58ae85bdd2fed2bafc4dd6bc4c33c62457f2879948bad9effdbeda44581472')
    summary=read(EXPORT+'/summary.json',CHECKING[EXPORT+'/summary.json'])
    for name,h in selected['output_hashes'].items():pin(EXPORT+'/'+name,h)
    for name,h in selected['source_inputs_sha256'].items():pin(name,h)
    need(selected['schema']=='ROOT_FOCUSED_START_SELECTION_V1' and selected['producer']=='/root/checkpoint_audit' and selected['root']==11,'selection exact scope')
    need(selected['selection_rule']==['root_residual','mu_energy','input_adjacency_sha256','proposal_id'],'selection exact rule')
    need(selected['target_resolution']=='NONE' and selected['support_pair_uniqueness_assumed'] is False and summary['independent_approval'] is False,'no self approval/target promotion')
    population=[];base_rows={};stage=[];parts_checked=0
    for label,folder,mh,reviewfolder,rh,status,count,tp,th,ap,ah in CENSUSES:
        mp='acceleration/results/'+folder+'/manifest.json';rp='acceleration/results/20261003_independent_review/'+reviewfolder+'/summary.json'
        m=read(mp,mh);r=read(rp,rh);pin(tp,th);pin(ap,ah)
        need(r['status']==status and r['verifier']=='/root' and r['complete_proposals_checked']==239085 and r['complete_universe'] is True and r['inputs_sha256'][mp]==mh,'complete frozen independent census')
        need(m['completed_proposals']==239085 and m['budget_stop'] is False and len(m['parts'])==48,'completed census output')
        raw=(ROOT/tp).read_bytes()
        if label=='original':
            lines=raw.decode('ascii').splitlines();need(lines[0]=='HYPERGRAPH_WEIGHT60_ANNEAL_STATE_V2' and lines.count('current 231')==1,'source state');ix=lines.index('current 231');base=[list(map(int,s.split())) for s in lines[ix+1:ix+232]]
        else:base=decode(raw)['triples']
        bs,br,_,_=dense_score(base);need(br==(ROOT/ap).read_bytes() and (bs['lambda_energy'],bs['mu_energy'],bs['root_residual'])==(0,3480,52),'source dense graph')
        base_rows[label]=base;next_id=0;hist=Counter();eligible=[]
        for part in tqdm(m['parts'],desc='independent '+label+' raw parts',unit='part',mininterval=1):
            guard(deadline);pin(part['path'],part['gzip_sha256']);path=ROOT/part['path']
            need(part['start']==next_id and part['end']==next_id+part['record_count'] and path.stat().st_size==part['gzip_bytes'],'complete part ordering/size')
            h=hashlib.sha256();size=0;records=0
            with gzip.open(path,'rb') as stream:
                while line:=stream.readline(4097):
                    need(len(line)<=4096 and line.endswith(b'\n'),'bounded raw records');rec=decode(line)
                    need(canonical(rec)==line and type(rec['proposal_id']) is int and rec['proposal_id']==next_id,'canonical ordered proposal')
                    need(type(rec['valid']) is bool,'typed validity');category=rec['classification'];hist[category]+=1
                    if rec['valid']:
                        need(all(type(rec[k]) is int for k in ('delta_lambda','delta_mu','new_lambda','new_mu','new_root_residual','root_residual_delta')),'typed exact energies')
                        if rec['delta_lambda']==0:
                            rows=trade(base,rec);s,_,_,_=dense_score(rows)
                            need((s['lambda_energy'],s['mu_energy'],s['root_residual'])==(0,rec['new_mu'],rec['new_root_residual']),'complete eligible dense products')
                            need(rec['new_lambda']==0 and rec['delta_mu']==s['mu_energy']-3480 and rec['root_residual_delta']==s['root_residual']-52,'exact eligible deltas')
                            sign='up' if rec['delta_mu']>0 else 'down' if rec['delta_mu']<0 else 'equal'
                            need(category=='valid_lambda_preserving_mu_'+sign,'eligible classification')
                            v=dict(census=label,input_adjacency_sha256=ah,proposal_id=rec['proposal_id'],root_residual=s['root_residual'],mu_energy=s['mu_energy'],lambda_energy=0,adjacency_sha256=s['matrix_sha256'],raw_record_sha256=digest(line),raw_part=part['path'],raw_part_sha256=part['raw_sha256'],full_record=rec,literal_record=line.decode('ascii'),census_manifest=mp,census_manifest_sha256=mh)
                            population.append(v);eligible.append(v)
                    next_id+=1;records+=1;size+=len(line);h.update(line)
                    need(records<=part['record_count'] and size<=part['raw_bytes'],'bounded gzip decode')
            need(records==part['record_count'] and size==part['raw_bytes'] and h.hexdigest()==part['raw_sha256'] and next_id==part['end'],'full raw identity');parts_checked+=1
        need(next_id==239085 and len(eligible)==count and dict(hist)==m['aggregate']['counts']==r['aggregate']['counts'],'complete eligible population')
        mr=min(v['root_residual'] for v in eligible)
        stage.append(dict(label=label,labels_scanned=next_id,eligible_labels=count,category_counts=dict(hist),minimum_root_residual=mr,minimum_root_ties=sum(v['root_residual']==mr for v in eligible)))
    order=lambda v:(v['root_residual'],v['mu_energy'],v['input_adjacency_sha256'],v['proposal_id'])
    population.sort(key=order);need(len(population)==373,'complete373 labels')
    need(read(EXPORT+'/eligible_population.json')['records']==population,'full population contents/order')
    chosen=population[0];need(chosen==selected['selected']==summary['selection'],'exact lex selected record')
    need(chosen['proposal_id']==25587 and chosen['census']=='neighbor','frozen expected selection')
    rows=trade(base_rows[chosen['census']],chosen['full_record']);score,raw,a,cn=dense_score(rows)
    need(raw==(ROOT/EXPORT/'selected.adj').read_bytes() and score==selected['exact_scores']==summary['scores'],'raw selected full matrix/components/supports')
    typed=read(EXPORT+'/ordered_triples.json');frozen=[dict(index=i,points=t) for i,t in enumerate(rows) if 11 in t]
    need(typed==dict(schema='ROOT_FOCUSED_ORDERED_TRIPLES_V1',n=99,degree=7,root=11,triples=rows,root_triples=frozen),'complete ordered exported rows')
    need(len(frozen)==7 and [t['index'] for t in frozen]==[15,18,22,57,61,82,154] and selected['seven_frozen_literal_root_triples']==summary['seven_root_triples']==frozen,'seven original frozen literal rows')
    need((ROOT/EXPORT/'selected_record.jsonl').read_bytes()==chosen['literal_record'].encode(),'selected literal record')
    groups={}
    for v in population:groups.setdefault(v['adjacency_sha256'],[]).append(dict(census=v['census'],proposal_id=v['proposal_id']))
    duplicates=dict(unique_graphs=len(groups),duplicate_groups=[dict(adjacency_sha256=h,labelled_proposals=v) for h,v in sorted(groups.items()) if len(v)>1])
    need(read(EXPORT+'/duplicate_graph_ties.json')==duplicates and len(groups)==220==selected['unique_eligible_graphs']==summary['unique_eligible_graphs'],'all duplicate graph groups')
    ties=[{k:v[k] for k in ('census','proposal_id','input_adjacency_sha256','adjacency_sha256')} for v in population if (v['root_residual'],v['mu_energy'])==order(chosen)[:2]]
    need(len(ties)==6 and ties==selected['minimum_root_mu_ties'],'complete six root/mu ties')
    need(selected['census_records']==stage and selected['eligible_count']==373 and selected['distinct_input_graphs']==2,'complete stage counts')
    native=ROOT/EXPORT/'graph_input.txt';pin(EXPORT+'/graph_input.txt','203e9a28106304476efeb92bae143be448e0423e87e227cf2a0ec85852ded30e')
    e=dict(n=99,degree=7,root=11,triples=rows,source_matrix_sha256=filehash(ROOT/EXPORT/'selected.adj'),source_triples_sha256=filehash(ROOT/EXPORT/'ordered_triples.json'),selection_report_sha256=filehash(ROOT/EXPORT/'selection.json'))
    parse_native(native.read_bytes(),e)
    need((score['lambda_energy'],score['mu_energy'],score['root_residual'])==(0,3484,50),'selected exact objective values')
    mismatch=int(np.count_nonzero(cn-(12*np.eye(99,dtype=np.int64)-a+2*np.ones((99,99),dtype=np.int64))))
    need(mismatch>0,'selected object is not target')
    write(out/'eligible_population_recomputed.json',dict(unit='eligible labelled proposal',count=373,records=population))
    return dict(status='INDEPENDENT_ROOT_FOCUSED_START_V1_COMPLETE_FINITE_SELECTION_PASS',graph_input=EXPORT+'/graph_input.txt',graph_input_sha256=filehash(native),selection_sha256=e['selection_report_sha256'],selected_matrix_sha256=e['source_matrix_sha256'],selected_triples_sha256=e['source_triples_sha256'],selected_proposal=chosen,exact_scores=score,frozen_root_rows=frozen,mutable_line_count=224,complete_raw_parts=parts_checked,authenticated_raw_labels=478170,eligible_labelled_graphs_checked=373,unique_eligible_graphs=220,minimum_root_mu_tie_count=6,ordered_target_identity_mismatches=mismatch,complete_dense_products=376,target_resolution='NONE',overall_search_coverage='UNKNOWN; no validated denominator.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('calibration','full'));ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--calibration');ap.add_argument('--calibration-sha256');args=ap.parse_args()
    start=time.monotonic();deadline=CommandDeadline(args.seconds,allocation_reason='Independent finite373 dense graph products and bounded96-part raw selection checking; no search')
    out=args.out.resolve();need(out.is_relative_to(ROOT) and not out.exists(),'fresh output');out.mkdir(parents=True);pins={}
    def pin(name,expected=None):
        guard(deadline);actual=filehash(ROOT/name);need(expected is None or actual==expected,'exact pin '+name);pins[name]=actual;return actual
    def read(name,expected=None):pin(name,expected);return decode((ROOT/name).read_bytes())
    for name,h in CHECKING.items():pin(name,h)
    pin(SELF);pin(SPEC)
    controls=calibration(deadline,out)
    report=dict(status='INDEPENDENT_ROOT_FOCUSED_START_V1_PREFULL_CALIBRATION_PASS',producer='/root/checkpoint_audit',verifier='/root',timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),tool_versions=dict(python=platform.python_version(),numpy=np.__version__,tqdm=__import__('tqdm').__version__),controls=controls,target_resolution='NONE',shared_components=['ROOT dense adjacency/energy helper f510 from separately calibrated two-line checker, NumPy int64 matrix products; exporter set-intersection implementation is not imported.','Two prior complete ROOT census reviews establish all frozen proposal classifications; this checker authenticates every raw byte and independently multiplies all eligible graphs.','Python gzip/SHA256, JSON, deadline and supported Job supervisor.'],limitations=['No entire plateau closure, unrestricted coverage, global optimum, automorphism assumption or target exclusion.','Graph selection minimizes only the exact frozen373 labelled input population. Root error zero alone would remain partial.'])
    if args.mode=='full':need(args.calibration and args.calibration_sha256,'fresh calibration arguments');report.update(full(deadline,out,pin,read,args))
    report.update(inputs_sha256=pins,elapsed_seconds=time.monotonic()-start,deadline=deadline.status());write(out/'summary.json',report)
    print(json.dumps(dict(path=str(out/'summary.json'),sha256=filehash(out/'summary.json'),status=report['status'],strict_controls=controls['strict_negative_count'])))

if __name__=='__main__':main()
