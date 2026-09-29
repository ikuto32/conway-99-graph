"""Candidate192-map exact scaffold transport; no solver or producer imports."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, product
import gzip
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
ENCODING=ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json'
SOURCE=ROOT/'acceleration/results/20260930_two_star_empty_domain_cut/run01/certificate.json'
SOURCE_CLAUSE=SOURCE.with_name('nogood.clause')
GATE=ROOT/'acceleration/results/20260930_independent_review/two_star_empty_domain_cut_v2/summary.json'
GATE_SHA='e3aae7ba9b776e9382c1790c64f0e76be6f0497912a9e1440e43a7df959ce16c'
PROOF=ROOT/'docs/DERIVATION_20260930_TWO_STAR_NOGOOD36_ANCHOR_TRANSPORT.md'

def need(x,msg):
    if not x:raise ValueError(msg)
def digest(p):
    h=sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def unique(pairs):
    result={}
    for k,v in pairs:need(k not in result,'duplicate JSON key');result[k]=v
    return result
def read(p):return json.loads(p.read_bytes(),object_pairs_hook=unique)
def save(out,name,obj,compact=False):
    raw=(json.dumps(obj,indent=None if compact else 2,separators=(',',':')if compact else None)+'\n').encode('utf-8')
    with(out/name).open('xb')as f:f.write(raw)
    return raw
def make_map(groups,mask,labels,edges,source_clause):
    need(len(groups)==7 and set(groups)==set(range(7)),'group bijection')
    need(set(groups[:2])=={0,1}and set(groups[2:4])=={2,3}and set(groups[4:])=={4,5,6},'specified group blocks')
    need(type(mask)is int and 0<=mask<8,'three-bit tail mask')
    flips=[0]*4+[(mask>>i)&1 for i in range(3)]
    symbols=[2*groups[s//2]+((s%2)^flips[s//2])for s in range(14)]
    lookup={tuple(lab):15+i for i,lab in enumerate(labels)}
    vertices=[0]+[1+s for s in symbols]+[lookup[tuple(sorted(symbols[s]for s in lab))]for lab in labels]
    pairs={(e['u'],e['v']):e['id']for e in edges}
    emap=[0]+[pairs[tuple(sorted((vertices[e['u']],vertices[e['v']])))]for e in edges]
    image=[(1 if literal>0 else-1)*emap[abs(literal)]for literal in source_clause]
    return{'group_permutation':list(groups),'tail_sign_mask':mask,'symbol_map':symbols,'full99':vertices,'edge_variable_map':emap,'transported_clause':image,'canonical_clause':sorted(image,key=abs)}
def check_map(rec,known,labels,edges,clause):
    expected=make_map(rec['group_permutation'],rec['tail_sign_mask'],labels,edges,clause)
    need(all(rec[k]==expected[k]for k in expected),'exact map metadata and literal image')
    pi=rec['full99'];emap=rec['edge_variable_map']
    need(len(pi)==99 and sorted(pi)==list(range(99))and pi[0]==0,'full99 permutation fixing root')
    need(pi[15]==15 and pi[59]==59,'ordered anchor fixed')
    need(len(emap)==3487 and emap[0]==0 and sorted(emap[1:])==list(range(1,3487)),'all3486 primary-variable images')
    for u in range(99):
        for v in range(99):need(known[u][v]==known[pi[u]][pi[v]],'all9801 fixed/free states')
    need(len(rec['canonical_clause'])==36 and len(set(rec['canonical_clause']))==36,'distinct36 literal image')
    return True
def controls(known,labels,edges,clause):
    identity=make_map(tuple(range(7)),0,labels,edges,clause);check_map(identity,known,labels,edges,clause)
    need(identity['full99']==list(range(99))and identity['transported_clause']==clause,'identity positive')
    cycle=make_map((0,1,2,3,5,6,4),0,labels,edges,clause);check_map(cycle,known,labels,edges,clause)
    need(any(cycle['full99'][cycle['full99'][x]]!=x for x in range(99)),'actual noninvolutory map')
    for values in product((False,True),repeat=3):
        forward=[2,3,1];a=[False]+list(values);b=[False]*4
        for i,j in enumerate(forward,1):b[j]=a[i]
        def sat(literals,bits):return any(bits[abs(t)]==(t>0)for t in literals)
        need(sat([-1,2,-3],a)==sat([-forward[0],forward[1],-forward[2]],b),'forward signed transport truth table')
    rejected=[]
    def reject(name,rec):
        try:check_map(rec,known,labels,edges,clause)
        except ValueError:rejected.append(name)
        else:raise AssertionError(name+' accepted')
    bad=deepcopy(identity);bad['full99'][1]=bad['full99'][2];reject('duplicate_vertex',bad)
    bad=deepcopy(identity);bad['full99'][15],bad['full99'][59]=59,15;reject('anchor_exchange',bad)
    bad=deepcopy(identity);bad['tail_sign_mask']=8;reject('out_of_population_sign_mask',bad)
    bad=deepcopy(identity);bad['group_permutation'][1],bad['group_permutation'][2]=2,1;reject('wrong_group_block',bad)
    bad=deepcopy(identity);bad['edge_variable_map'][1]=bad['edge_variable_map'][2];reject('duplicate_edge_image',bad)
    bad=deepcopy(identity);bad['transported_clause'][0]*=-1;reject('changed_literal_sign',bad)
    bad=deepcopy(identity);bad['canonical_clause']=bad['canonical_clause'][:-1];reject('omitted_literal',bad)
    return{'identity_pass':True,'noninvolutory_tail_cycle_pass':True,'signed_forward_transport_assignments':8,'corruptions_rejected':rejected}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='acceleration/results/20260930_two_star_nogood36_anchor_transport/run01');args=p.parse_args()
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    need(digest(GATE)==GATE_SHA,'independent source gate hash');gate=read(GATE)
    need(gate['status']=='INDEPENDENT_TWO_STAR_EMPTY_DOMAIN_NOGOOD_PASS','independent source gate status')
    authenticated={}
    for name,expected in gate['inputs_sha256'].items():
        actual=digest(ROOT/name);need(actual==expected,'unchanged source audit input '+name);authenticated[name]=actual
    model=read(MODEL);known=model['known_adjacency_full99'];labels=model['outer_labels'];edges=model['edge_variables'];cert=read(SOURCE);clause=cert['clause']
    need(len(edges)==3486 and[e['id']for e in edges]==list(range(1,3487)),'ordered unrestricted primary edge variables')
    need(read(ENCODING)['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','encoding premise')
    rawtokens=list(map(int,SOURCE_CLAUSE.read_text(encoding='ascii').split()));need(rawtokens==clause+[0],'source raw clause interpretation, retaining original bytes')
    need(len(clause)==36 and all(x<0 for x in clause),'verified negative36 clause')
    population=[(p0+p1+tail,mask)for p0 in permutations((0,1))for p1 in permutations((2,3))for tail in permutations((4,5,6))for mask in range(8)]
    need(len(population)==192 and len(set(population))==192,'specified complete192 tuple population')
    files=[GATE,MODEL,ENCODING,SOURCE,SOURCE_CLAUSE,PROOF,Path(__file__).resolve(),ROOT/'uv.lock',ROOT/'pyproject.toml']
    authenticated.update({x.relative_to(ROOT).as_posix():digest(x)for x in files})
    save(out,'manifest.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'python':platform.python_version(),'question':'What unique signed clause images result from all specified192 ordered-anchor-fixing scaffold relabelings?','scope':'Exactly the2!*2!*3!*2^3 map tuples, no target automorphism or arbitrary permutation census.','selection':{'population_size':192,'group_blocks':[[0,1],[2,3],[4,5,6]],'flipped_groups':[4,5,6],'ordered_anchor_vertices':[15,59],'population':[[list(g),mask]for g,mask in population]},'success':'Every exact known/free state and primary variable image preserved; complete source-clause images and canonical dedup saved for separate checking.','resource_wall_seconds':60,'numerical_thresholds':None,'numerical_thresholds_null_reason':'Integer permutation and literal equality only.','inputs_sha256':authenticated,'source_claim':{'id':gate['claim_id'],'revision':gate['claim_revision']},'solver_calls':0})
    save(out,'controls.json',controls(known,labels,edges,clause))
    maps=[];dedup={};unique_clauses=[]
    for number,(groups,mask)in enumerate(population):
        need(time.monotonic()-start<60,'wall cap before map')
        rec=make_map(groups,mask,labels,edges,clause);check_map(rec,known,labels,edges,clause);rec['id']=number
        key=tuple(rec['canonical_clause'])
        if key not in dedup:dedup[key]=len(unique_clauses);unique_clauses.append({'id':len(unique_clauses),'clause':list(key),'map_ids':[]})
        rec['unique_clause_id']=dedup[key];unique_clauses[dedup[key]]['map_ids'].append(number);maps.append(rec)
    need(len({tuple(r['full99'])for r in maps})==192,'distinct full maps')
    raw=save(out,'maps.json',{'edge_map_indexing':'Index0 is reserved0; index i=1..3486 stores forward image of primary variable i.','records':maps},compact=True)
    compressed=gzip.compress(raw,mtime=0);(out/'maps.json.gz').write_bytes(compressed);need(gzip.decompress(compressed)==raw,'exact gzip replay')
    save(out,'unique_clauses.json',unique_clauses)
    suffix=''.join(' '.join(map(str,r['clause']))+' 0\n'for r in unique_clauses).encode('ascii');(out/'clauses.cnfpart').write_bytes(suffix)
    need(len(suffix.splitlines())==len(unique_clauses),'complete suffix row count')
    save(out,'summary.json',{'status':'CANDIDATE_192_SCAFFOLD_NOGOOD36_TRANSPORT_PENDING_INDEPENDENT_REVIEW','timestamp':datetime.now(timezone.utc).isoformat(),'claim_kind':'derived clause transport and finite empirical census','source_claim':{'id':gate['claim_id'],'revision':gate['claim_revision']},'encoding_claim':{'id':'C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING','revision':1},'specified_map_tuples':192,'generated_maps':len(maps),'distinct_maps':len({tuple(r['full99'])for r in maps}),'vertex_images_per_map':99,'nonroot_vertex_images_per_map':98,'primary_variable_images_per_map':3486,'raw_clause_images':len(maps),'unique_signed_clauses':len(unique_clauses),'duplicate_clause_images':len(maps)-len(unique_clauses),'source_canonical_clause_present':tuple(sorted(clause,key=abs))in dedup,'clause_length':36,'unique_clause_population':'Unique signed clauses among these192 transported images only; no comparison with every baseCNF clause is claimed.','wall_seconds':time.monotonic()-start,'solver_calls':0,'existing_cnf_mutations':0,'independent_verification':None,'independent_verification_null_reason':'Producer maps and controls await independently authored complete map/clause replay.','artifact_availability':'LOCAL_ONLY','limitations':['No target automorphism assumed.','No target resolution or family exclusion.','This transport does not claim literal permutation symmetry of the auxiliary CNF.','The unrestricted entailment makes images safe for any four-branch augmentation, but no augmentation is materialized.'],'artifact_hashes':{f.name:digest(f)for f in sorted(out.iterdir())}})
    print(json.dumps({'status':'CANDIDATE','maps':len(maps),'unique_clauses':len(unique_clauses),'seconds':time.monotonic()-start,'summary_sha256':digest(out/'summary.json'),'maps_sha256':digest(out/'maps.json'),'suffix_sha256':digest(out/'clauses.cnfpart')}))
if __name__=='__main__':main()

