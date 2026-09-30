"""Complete native assignment and independent ordered fixed-support factor checker."""
from copy import deepcopy
from datetime import datetime,timezone
from itertools import combinations
from pathlib import Path
import argparse,gzip,io,json,platform,subprocess,sys
import audit_20260930_fixed_support_raw_preparation as rawprep
import audit_20260930_hadamard_prism_ordered_cnf as encoding
shared=rawprep.shared;common=shared.common;native=shared.native
ROOT=encoding.ROOT;B=encoding.B;D=encoding.D
GATE=B/'20260930_independent_review/hadamard_prism_ordered_cnf/summary.json'
GATE_SHA='377e985056a4f6daae704d342c63d4a06d7086ee43b3b5e9636d9a1135d18132'
need,read,save,digest,key=encoding.need,encoding.read,encoding.save,encoding.digest,encoding.key
N=595464;M=3336642

def bind():
    need(digest(GATE)==GATE_SHA and read(GATE)['status']=='INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_CNF_PASS','exact encoding gate')
    bindings={**read(GATE)['inputs_sha256'],key(GATE):GATE_SHA}
    prep=B/'20260930_independent_review/fixed_support_raw_preparation/summary.json';need(digest(prep)=='61c45a7f3efde426bc6e6f6010af1f718885c26f79c487ee877467f2b2d1136e','frozen independent raw positive path')
    bindings.update(read(prep)['inputs_sha256']);bindings[key(prep)]=digest(prep)
    for mod in [rawprep,shared,shared.rawcheck,shared.rawcheck.base,common,native,encoding]:
        p=Path(mod.__file__);need(key(p) not in bindings or bindings[key(p)]==digest(p),'frozen independent helper '+key(p));bindings[key(p)]=digest(p)
    for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PRISM_ORDERED_OBJECT.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
    for p,h in bindings.items():need(digest(ROOT/p)==h,'bound input '+p)
    for name,h in [('instance.cnf','51cedaa0e54ab569e6ec4b8ad19fb17136ad5e8a9bdbd751b994903e4024f5df'),('model.json','85f2008d34c5f089e04e87306462a10be4919c582da6b6a2303523f5f6ea737a'),('scope.json','5d8cac247339006994035ac21c379edafdb8b55ec11213eba2ac22859430b466')]:need(bindings[key(D/name)]==h,'direct input binding '+name)
    model=read(D/'model.json');scope=read(D/'scope.json');need((model['variables'],model['clauses'])==(N,M),'exact model dimensions')
    encoding.scope_check(model,scope,read(encoding.RAW));return model,scope,bindings

def raw_decode(values,model,scope):
    need(len(values)==N+1 and all(v in (0,1) for v in values[1:]),'complete binary assignment array')
    factor=[[0]*60 for _ in range(36)];selected=[];ranks=[]
    need(len(model['domains'])==60,'all sixty independently selected columns')
    for d,domain in enumerate(model['domains']):
        ids=list(range(1+90*d,91+90*d));need(domain['column']==d and[x['selector']for x in domain['choices']]==ids,'all5400 selector IDs')
        chosen=[j for j,v in enumerate(ids)if values[v]];need(len(chosen)==1,'one selected option for each actual column')
        j=chosen[0];selected.append(ids[j]);ranks.append(j);word=domain['choices'][j]['fibres_by_sorted_coordinate'];coords=domain['support_coordinates']
        need(all(word.count(g)==2 for g in range(3)),'two coordinates per fibre')
        for a,color in zip(coords,word,strict=True):factor[12*color+a][d]=1
    need(all(ranks[d]<ranks[e]for d,e in scope['adjacent_order_pairs']),'all40 strict option-rank inequalities')
    need([[sum(factor[12*g+a][d] for g in range(3)) for d in range(60)] for a in range(12)]==scope['L'],'all720 literal fixed-support entries')
    return selected,ranks,factor

def compare_decoded(dec,factor,selected,ranks,raw,scope):
    expected=dict(factor=factor,L=scope['L'],selected_selector_ids=selected,selected_option_ranks=ranks,adjacent_order_pairs=scope['adjacent_order_pairs'],cyclic_colour_constraint=False,core_adjacency=scope['core_adjacency'],matchings=scope['matchings'],M0=scope['matchings'][0],M1=scope['matchings'][1],M2=scope['matchings'][2],P=list(range(12)),target_gram36=scope['target_gram36'],canonical_factor=raw['canonical_factor']['incidence_matrix'],canonical_column_order=raw['canonical_new_to_raw_old_column'],canonical_C0_columns=[list(p) for p in combinations(range(12),2) if p[1]!=(p[0]^1)],scope_sha256=digest(D/'scope.json'),model_sha256=digest(D/'model.json'),target_graph=False,residual_D=None)
    for field,want in expected.items():need(field in dec and type(dec[field])is type(want) and dec[field]==want,'raw producer comparison '+field)

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,encoding_gate_sha256=GATE_SHA,verifier='/root/state_literature_audit',producer_imports=False,artifact_availability='LOCAL_ONLY',target_resolution=False,shared_components=['Frozen independent complete assignment/native/CNF parsers and integer raw-factor/canonicalization/support checkers.','Own separately frozen independent domain/CNF checker; no producer decoder/encoder imports.','Wrapper structure adapted from the independently authored cyclic-object checker; selection and order checks are new.'],limitations=['One literal six-prism coordinate support, normalized only by sorting identical-support columns.','No cyclic restriction or target automorphism is assumed.','Factor/partial99 omit residual D and are not a target graph.','Known243 is a genuine nonempty raw-factor control, not a research99 witness.'])

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
    for group in scope['identical_support_groups']:
        for rank,d in enumerate(group['columns']):values[1+90*d+rank]=1
    selected,ranks,local_factor=raw_decode(values,model,scope);need(len(selected)==60 and all(sum(local_factor[12*g+a][d]for a in range(12))==2 for g in range(3)for d in range(60)),'all60 local columns and quotas')
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
    for label,newrank in [('equal_order_rank',0),('descending_order_rank',89)]:
        bad=values[:];d=scope['identical_support_groups'][0]['columns'][1 if newrank==0 else 0];bad[1+90*d+ranks[d]]=0;bad[1+90*d+newrank]=1
        reject(label,lambda bad=bad:raw_decode(bad,model,scope))
    save(args.out/'local_codec_only.json',dict(selected_ids=selected,selected_option_ranks=ranks,factor=local_factor,label='Valid local domains, strict order and column quotas only, deliberately rejected by full research Gram and clauses.'))
    report={**provenance(bindings),'status':'INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_OBJECT_CHECKER_CALIBRATION_PASS','variables':N,'clauses':M,'known_nonempty_positive':positive['canonical_factor']['exact_checks'],'synthetic_complete_native':nrec,'synthetic_complete_clauses':crec,'local_codec_selected_domains':60,'local_codec_columns':60,'strict_order_pairs':40,'corruptions_rejected':rejected,'research_positive_factor':None,'research_positive_factor_null_reason':'No valid research factor is currently known; genuine243, local choices/order and synthetic full-size codec controls have explicitly separate scope.','outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    model,scope,bindings=bind();values=common.assignment_values(read(args.assignment)['assignment'],N)
    with args.native_output.open('rb') as stream:nvalues,nrec=native.native_values(stream,N)
    need(values==nvalues,'complete raw native and JSON agreement')
    with (D/'instance.cnf').open('rb') as stream:crec=common.check_cnf_stream(stream,values,N,M)
    selected,ranks,factor=raw_decode(values,model,scope);raw,_,_=rawprep.verify_fixed_support(scope['core_adjacency'],factor,scope['L'])
    need(raw['canonical_factor']['prescribed_gram']==scope['target_gram36'],'all1296 integer prescribed Gram entries')
    if args.decoded:compare_decoded(read(args.decoded),factor,selected,ranks,raw,scope)
    save(args.out/'independent_factor_and_partial99.json',{**raw,'L':scope['L'],'selected_selector_ids':selected,'selected_option_ranks':ranks,'cyclic_colour_constraint':False,'target_graph':False})
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    report={**provenance(bindings),'status':'INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_FACTOR_OBJECT_PASS','all_actual_clauses':crec,'complete_native_assignment':nrec,'selected_domains':60,'actual_columns':60,'strict_order_pairs':40,'raw_exact_checks':raw['canonical_factor']['exact_checks'],'outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);c=sub.add_parser('calibrate');c.add_argument('--out',type=Path,required=True);s=sub.add_parser('sat');s.add_argument('--assignment',type=Path,required=True);s.add_argument('--native-output',type=Path,required=True);s.add_argument('--decoded',type=Path);s.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
