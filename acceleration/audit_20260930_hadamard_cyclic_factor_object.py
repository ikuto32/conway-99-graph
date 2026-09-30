"""Complete native assignment and independent raw cyclic-factor object checker."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,gzip,io,json,platform,subprocess,sys
import audit_20260930_fixed_support_raw_preparation as rawprep
import audit_20260930_hadamard_cyclic_factor_cnf as encoding
shared=rawprep.shared;common=shared.common;native=shared.native
ROOT=encoding.ROOT;B=encoding.B;D=encoding.D
GATE=B/'20260930_independent_review/hadamard_cyclic_factor_cnf/summary.json'
GATE_SHA='494add3aecbd2d7d4629c738be73dda3a884c89ecb624fbdb5e867dca2a6ad64'
need,read,save,digest,key=encoding.need,encoding.read,encoding.save,encoding.digest,encoding.key
N=26360;M=122394

def bind():
    need(digest(GATE)==GATE_SHA and read(GATE)['status']=='INDEPENDENT_FIXED_SUPPORT_CYCLIC_COLORING_CNF_PASS','exact encoding gate')
    bindings={**read(GATE)['inputs_sha256'],key(GATE):GATE_SHA}
    prep=B/'20260930_independent_review/fixed_support_raw_preparation/summary.json';need(digest(prep)=='61c45a7f3efde426bc6e6f6010af1f718885c26f79c487ee877467f2b2d1136e','frozen independent raw positive path')
    bindings.update(read(prep)['inputs_sha256']);bindings[key(prep)]=digest(prep)
    for mod in [rawprep,shared,shared.rawcheck,shared.rawcheck.base,common,native,encoding]:
        p=Path(mod.__file__);need(key(p) not in bindings or bindings[key(p)]==digest(p),'frozen independent helper '+key(p));bindings[key(p)]=digest(p)
    for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_CYCLIC_FACTOR_OBJECT.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
    for p,h in bindings.items():need(digest(ROOT/p)==h,'bound input '+p)
    for name,h in [('instance.cnf','e0895d94060a8d8b25adb78cf298b4b6f6f94f8c89ac242c180c1e4b320580d8'),('model.json','9799d69cd02c2293e0d7f89615ba9000949c5f2bd097dea710acd4ac235f4b57'),('scope.json','847cd3aa5ab82216a552ea9c57bb63663ef9e906fadbb8be7e9b019562ced7f0')]:need(bindings[key(D/name)]==h,'direct input binding '+name)
    model=read(D/'model.json');scope=read(D/'scope.json');need((model['variables'],model['clauses'])==(N,M),'exact model dimensions')
    encoding.scope_check(model,scope,read(encoding.RAW));return model,scope,bindings

def raw_decode(values,model,scope):
    need(len(values)==N+1 and all(v in (0,1) for v in values[1:]),'complete binary assignment array')
    factor=[[0]*60 for _ in range(36)];selected=[];seen=[]
    for p,domain in enumerate(model['domains']):
        ids=list(range(1+30*p,31+30*p));need([x['selector'] for x in domain['choices']]==ids,'all600 selector IDs')
        chosen=[j for j,v in enumerate(ids) if values[v]];need(len(chosen)==1,'one selected cyclic domain choice')
        j=chosen[0];selected.append(ids[j]);word=domain['choices'][j]['coloring'];coords=domain['support_coordinates']
        need(word[0]==0 and all(word.count(g)==2 for g in range(3)),'actual phase gauge and two per fibre')
        for r,d in enumerate(domain['raw_columns']):
            seen.append(d)
            for a,color in zip(coords,word,strict=True):factor[12*((color+r)%3)+a][d]=1
    need(sorted(seen)==list(range(60)),'complete60-column expansion without overlap')
    need([[sum(factor[12*g+a][d] for g in range(3)) for d in range(60)] for a in range(12)]==scope['L'],'all720 literal fixed-support entries')
    return selected,factor

def compare_decoded(dec,factor,selected,raw,scope):
    expected=dict(factor=factor,L=scope['L'],selected_selector_ids=selected,core_adjacency=scope['core_adjacency'],matchings=scope['matchings'],M0=scope['matchings'][0],M1=scope['matchings'][1],M2=scope['matchings'][2],P=list(range(12)),target_gram36=scope['target_gram36'],canonical_factor=raw['canonical_factor']['incidence_matrix'],canonical_column_order=raw['canonical_new_to_raw_old_column'],canonical_C0_columns=[list(p) for p in combinations(range(12),2) if p[1]!=(p[0]^1)],scope_sha256=digest(D/'scope.json'),model_sha256=digest(D/'model.json'),extra_cyclic_factor_constraint=True,target_graph=False,residual_D=None)
    for field,want in expected.items():need(field in dec and type(dec[field])is type(want) and dec[field]==want,'raw producer comparison '+field)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,encoding_gate_sha256=GATE_SHA,verifier='/root/state_literature_audit',producer_imports=False,artifact_availability='LOCAL_ONLY',target_resolution=False,shared_components=['Frozen independent complete assignment/native/CNF parsers and integer raw-factor/canonicalization/support checkers.','Own separately frozen independent domain/CNF checker; no producer decoder/encoder imports.'],limitations=['One literal six-prism coordinate support and additional cyclic fibre-triplet factor restriction only.','Factor/partial99 omit residual D and are not a target graph.','Known243 is a genuine nonempty raw-factor control, not a cyclic research99 witness.'])

def calibrate(args):
    model,scope,bindings=bind();rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('corrupted control accepted '+label)
    fixture=read(B/'20260930_srg243_residual_fixture/triangle_blocks.json');core=fixture['cubic_core60'];factor=fixture['factor60x180']
    support=[[sum(factor[20*g+a][d] for g in range(3)) for d in range(180)] for a in range(20)]
    positive,_,_=rawprep.verify_fixed_support(core,factor,support,research=False)
    reverse,_,_=rawprep.verify_fixed_support(core,[r[::-1] for r in factor],[r[::-1] for r in support],research=False)
    need(reverse['canonical_factor']['incidence_matrix']==positive['canonical_factor']['incidence_matrix'],'noncanonical full positive returns exact canonical F')
    save(args.out/'known243_raw_positive.json',dict(parameters=[243,22,1,2],exact_checks=positive['canonical_factor']['exact_checks'],reversed_columns_checked=180,not_research99=True))
    for label in ['Boolean_entry','changed_F','changed_core','wrong_support','duplicate_C0_pair']:
        c=deepcopy(core);f=deepcopy(factor);l=deepcopy(support)
        if label=='Boolean_entry':f[0][0]=bool(f[0][0])
        elif label=='changed_F':f[20][0]^=1
        elif label=='changed_core':c[0][1]^=1
        elif label=='wrong_support':l[0][0]^=1
        else:
            for row in f[:20]:row[1]=row[0]
        reject(label,lambda c=c,f=f,l=l:rawprep.verify_fixed_support(c,f,l,research=False))
    reject('243_not_research99',lambda:rawprep.verify_fixed_support(core,factor,support))
    # Positive local codec only; all actual research clauses will deliberately
    # reject this arbitrary selection. No valid research factor is invented.
    values=bytearray(N+1)
    for p in range(20):values[1+30*p]=1
    selected,local_factor=raw_decode(values,model,scope);need(len(selected)==20 and all(sum(row)==10 for row in local_factor),'complete local cyclic expansion and automatic row degree')
    reject('arbitrary_local_choices_not_full_research_factor',lambda:rawprep.verify_fixed_support(scope['core_adjacency'],local_factor,scope['L']))
    signed=[i if values[i] else -i for i in range(1,N+1)]
    native_blob=b'c SYNTHETIC FULL CODEC ONLY; NOT RESEARCH SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+80]))+(' 0' if i+80>=N else '')+'\n').encode() for i in range(0,N,80))
    parsed,nrec=native.native_values(io.BytesIO(native_blob),N);need(parsed==common.assignment_values(signed,N),'every native/JSON assignment ID agrees')
    cnf=f'p cnf {N} {M}\n'.encode()+b''.join(f'{signed[i%N]} 0\n'.encode() for i in range(M));crec=common.check_cnf_stream(io.BytesIO(cnf),parsed,N,M)
    for name,blob in [('native',native_blob),('cnf',cnf)]:
        with gzip.open(args.out/f'synthetic_complete.{name}.gz','wb') as stream:stream.write(blob)
    for label,bad in [('missing_status',native_blob.replace(b's SATISFIABLE\n',b'')),('duplicate_ID',native_blob.replace(b'v 1 -2 ',b'v 1 1 ',1)),('missing_terminator',native_blob.rsplit(b' 0\n',1)[0]+b'\n'),('conflicting_status',native_blob+b's UNSATISFIABLE\n')]:reject(label,lambda bad=bad:native.native_values(io.BytesIO(bad),N))
    reject('partial_JSON',lambda:common.assignment_values(signed[:-1],N));reject('invalid_JSON_ID',lambda:common.assignment_values(signed[:-1]+[N+1],N))
    reject('false_clause',lambda:common.check_cnf_stream(io.BytesIO(cnf.replace(b'1 0\n',b'-1 0\n',1)),parsed,N,M));reject('wrong_clause_count',lambda:common.check_cnf_stream(io.BytesIO(cnf.replace(str(M).encode(),str(M-1).encode(),1)),parsed,N,M))
    with (D/'instance.cnf').open('rb') as stream:reject('local_codec_not_research_SAT',lambda:common.check_cnf_stream(stream,parsed,N,M))
    for label in ['no_choice','two_choices']:
        bad=values[:]
        if label=='no_choice':bad[1]=0
        else:bad[2]=1
        reject(label,lambda bad=bad:raw_decode(bad,model,scope))
    save(args.out/'local_codec_only.json',dict(selected_ids=selected,factor=local_factor,label='Valid local domains and row margins only, deliberately rejected by full research Gram and clauses.'))
    report={**provenance(bindings),'status':'INDEPENDENT_FIXED_SUPPORT_CYCLIC_COLORING_OBJECT_CHECKER_CALIBRATION_PASS','variables':N,'clauses':M,'known_nonempty_positive':positive['canonical_factor']['exact_checks'],'synthetic_complete_native':nrec,'synthetic_complete_clauses':crec,'local_codec_selected_domains':20,'local_codec_expanded_columns':60,'corruptions_rejected':rejected,'research_positive_factor':None,'research_positive_factor_null_reason':'No valid research factor is currently known; genuine243, local cyclic and synthetic full-size codec controls have explicitly separate scope.','outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    model,scope,bindings=bind();values=common.assignment_values(read(args.assignment)['assignment'],N)
    with args.native_output.open('rb') as stream:nvalues,nrec=native.native_values(stream,N)
    need(values==nvalues,'complete raw native and JSON agreement')
    with (D/'instance.cnf').open('rb') as stream:crec=common.check_cnf_stream(stream,values,N,M)
    selected,factor=raw_decode(values,model,scope);raw,_,_=rawprep.verify_fixed_support(scope['core_adjacency'],factor,scope['L'])
    need(raw['canonical_factor']['prescribed_gram']==scope['target_gram36'],'all1296 integer prescribed Gram entries')
    if args.decoded:compare_decoded(read(args.decoded),factor,selected,raw,scope)
    save(args.out/'independent_factor_and_partial99.json',{**raw,'L':scope['L'],'selected_selector_ids':selected,'extra_cyclic_factor_constraint':True,'target_graph':False})
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    report={**provenance(bindings),'status':'INDEPENDENT_FIXED_SUPPORT_CYCLIC_COLORING_FACTOR_OBJECT_PASS','all_actual_clauses':crec,'complete_native_assignment':nrec,'selected_domains':20,'expanded_columns':60,'raw_exact_checks':raw['canonical_factor']['exact_checks'],'outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);c=sub.add_parser('calibrate');c.add_argument('--out',type=Path,required=True);s=sub.add_parser('sat');s.add_argument('--assignment',type=Path,required=True);s.add_argument('--native-output',type=Path,required=True);s.add_argument('--decoded',type=Path);s.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
