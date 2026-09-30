"""Independent complete assignment and raw coarse60 bit-lift factor checker."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import gzip
import io
import json
import platform
import subprocess
import sys
import audit_20260930_noncanonical_triangle_factor as rawcheck
import audit_20260930_full99_sat_object as common
import audit_20260930_unrestricted_full99_sat_object as native

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_cnf/summary.json'
GATE_SHA='b82eb3d3c999ae8bdcdbfd246dd28ea9cd6a9dd8d1ce811abc82ee0f3e38d88d'
PINS={
 'model.json':'a437d3f1381e9554bff2376726a991f1d1e0ea23c240f8ebacf005c57e82fcb5',
 'scope.json':'3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9',
 'instance.cnf':'eaace18635e6c0140a7020ef9f05af298298267dc1545e451d147f4b47577eb5'}
need=rawcheck.need
def digest(p):
    import hashlib
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def bind():
    need(digest(GATE)==GATE_SHA and read(GATE)['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS','exact independent encoding gate')
    bindings={**read(GATE)['inputs_sha256'],key(GATE):GATE_SHA}
    need(digest(rawcheck.base.__file__)=='8146a2d1c3eedd9d623ee5074b96b0657da5d2786f1f556898c720352165ee82','frozen independent base factor checker')
    _,_,_,base_bindings=rawcheck.base.bind_inputs();bindings.update(base_bindings)
    for name,h in PINS.items():need(bindings[key(D/name)]==h,'exact raw research input')
    for p in [Path(__file__),Path(rawcheck.__file__),Path(common.__file__),Path(native.__file__),
              ROOT/'docs/AUDIT_20260930_PRISM_COARSE60_BITLIFT_OBJECT.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:
        bindings[key(p)]=digest(p)
    fixturegate=ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json'
    need(digest(fixturegate)=='28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e','nonempty positive fixture gate')
    bindings[key(fixturegate)]=digest(fixturegate)
    bindings.update(read(fixturegate)['inputs_sha256'])
    for path,h in bindings.items():need(digest(ROOT/path)==h,'bound input hash '+path)
    model=read(D/'model.json');scope=read(D/'scope.json');words=scope['columns60']
    need((model['variables'],model['clauses'])==(5238,85698),'complete dimensions')
    need(len(words)==60 and len({tuple(w) for w in words})==60 and
         all(len(w)==6 and all(w.count(g)==2 for g in range(3)) for w in words),'exact coarse scope dimensions')
    expected=[dict(variable=2449+6*d+a,column=d,component=a,fibre=words[d][a]) for d in range(60) for a in range(6)]
    need(model['raw_bits']==expected,'independent bit mapping')
    return model,scope,bindings

def raw_bits(values,model,scope):
    bits=[[int(values[2449+6*d+a]) for a in range(6)] for d in range(60)]
    selected=[]
    for index,domain in enumerate(model['domains']):
        a,g=divmod(index,3);ids=list(range(1+136*index,1+136*(index+1)))
        need((domain['component'],domain['fibre'])==(a,g) and domain['selectors']==ids,'exact domain selector mapping')
        choices=[j for j,v in enumerate(ids) if values[v]];need(len(choices)==1,'one actual domain choice')
        j=choices[0];mask=domain['local_masks'][j];positions=[d for d,w in enumerate(scope['columns60']) if w[a]==g]
        need(domain['column_positions']==positions and len(positions)==20,'exact domain bit positions')
        need(all(bits[d][a]==((mask>>t)&1) for t,d in enumerate(positions)),'selected local mask equals all raw bits')
        selected.append(ids[j])
    factor=[[0]*60 for _ in range(36)]
    for d,word in enumerate(scope['columns60']):
        for a,g in enumerate(word):factor[12*g+2*a+bits[d][a]][d]=1
    need(all(sum(factor[12*g+2*a+b][d] for g in range(3) for b in range(2))==1 for a in range(6) for d in range(60)),
         'all360 component-one positions')
    return bits,selected,factor

def provenance(bindings):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
        verifier='/root/state_literature_audit',producer_imports=False,artifact_availability='LOCAL_ONLY',target_resolution=False,
        shared_components=['Frozen independent full assignment/native/CNF parsers and raw integer factor checker.',
                           'New explicit complete C0-column bijection and inverse check; no producer decoder imports.'],
        limitations=['Only this fixed60-pattern template is checked; no all-prism or all-core coverage.',
                     'A factor and partial99 object still omit residual D and are not a target graph.',
                     'No target automorphism or complement-pairing assumption is made.'])

def calibrate(args):
    model,scope,bindings=bind();rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('corrupt control accepted '+label)
    fixture=read(ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json')
    core=fixture['cubic_core60'];factor=fixture['factor60x180'];reverse=[row[::-1] for row in factor]
    positive=rawcheck.canonicalize_and_check(core,reverse,research=False)
    need(positive['canonical_factor']['incidence_matrix']==factor and positive['canonical_new_to_raw_old_column']==list(reversed(range(180))),
         'nonempty known243 complete relabel/inverse positive')
    save(args.out/'known243_column_relabel_positive.json',dict(column_map=positive['canonical_new_to_raw_old_column'],
        exact_checks=positive['canonical_factor']['exact_checks'],label='Known243 positive; not research99'))
    for label in ['Boolean_bit','missing_C0_entry','duplicated_C0_pair','wrong_F1','changed_core']:
        c=deepcopy(core);f=deepcopy(reverse)
        if label=='Boolean_bit':f[20][0]=bool(f[20][0])
        elif label=='missing_C0_entry':f[0][0]^=1
        elif label=='duplicated_C0_pair':
            for row in f[:20]:row[1]=row[0]
        elif label=='wrong_F1':
            for row in f[20:40]:row[0],row[1]=row[1],row[0]
        else:c[0][1]^=1
        reject(label,lambda c=c,f=f:rawcheck.canonicalize_and_check(c,f,research=False))
    reject('243_not_research99',lambda:rawcheck.canonicalize_and_check(core,reverse))
    # This assignment satisfies each selected local mask but is NOT asserted to
    # satisfy research Gram or caps. Synthetic clauses exercise full codecs only.
    values=bytearray([0])*5239
    for domain in model['domains']:
        values[domain['selectors'][0]]=1
        for t,d in enumerate(domain['column_positions']):values[2449+6*d+domain['component']]=(domain['local_masks'][0]>>t)&1
    for i in range(2809,5239):values[i]=1
    bits,selected,f=raw_bits(values,model,scope)
    need(len(bits)==60 and len(selected)==18 and len(f)==36,'local-only bit decode positive')
    signed=[i if values[i] else -i for i in range(1,5239)]
    native_raw=b'c SYNTHETIC CODEC ONLY; NOT RESEARCH SAT\ns SATISFIABLE\n'+b''.join(
        ('v '+' '.join(map(str,signed[i:i+100]))+(' 0' if i+100>=5238 else '')+'\n').encode() for i in range(0,5238,100))
    parsed,nativerec=native.native_values(io.BytesIO(native_raw),5238);need(parsed[1:]==values[1:],'all native values')
    jsonvalues=common.assignment_values(signed,5238);need(jsonvalues==parsed,'all native and JSON values')
    cnf=b'p cnf 5238 85698\n'+b''.join(f'{signed[i%5238]} 0\n'.encode() for i in range(85698))
    cnfrec=common.check_cnf_stream(io.BytesIO(cnf),parsed,5238,85698)
    for label,blob in [('native',native_raw),('cnf',cnf)]:
        with gzip.open(args.out/f'synthetic_fullsize.{label}.gz','wb') as stream:stream.write(blob)
    for label,bad in [('missing_status',native_raw.replace(b's SATISFIABLE\n',b'')),
                     ('duplicate_variable',native_raw.replace(b'v 1 -2 ',b'v 1 1 ',1)),
                     ('missing_terminator',native_raw.replace(b'5238 0\n',b'5238\n')),
                     ('false_UNSAT',native_raw+b's UNSATISFIABLE\n')]:reject(label,lambda bad=bad:native.native_values(io.BytesIO(bad),5238))
    reject('partial_JSON',lambda:common.assignment_values(signed[:-1],5238))
    reject('wrong_header',lambda:common.check_cnf_stream(io.BytesIO(cnf.replace(b'85698',b'85697',1)),parsed,5238,85698))
    reject('false_actual_clause',lambda:common.check_cnf_stream(io.BytesIO(cnf.replace(b'1 0\n',b'-1 0\n',1)),parsed,5238,85698))
    for label in ['no_choice','two_choices','changed_raw_bit']:
        bad=values[:]
        if label=='no_choice':bad[1]=0
        elif label=='two_choices':bad[2]=1
        else:bad[2449]^=1
        reject(label,lambda bad=bad:raw_bits(bad,model,scope))
    report={**provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_OBJECT_CHECKER_CALIBRATION_PASS',
        'encoding_gate_sha256':GATE_SHA,'variables':5238,'clauses':85698,'raw_bits':360,
        'known_nonempty_positive':positive['canonical_factor']['exact_checks'],'local_mask_codec_positive_only':True,
        'synthetic_complete_native':nativerec,'synthetic_complete_CNF':cnfrec,'synthetic_research_SAT_witness':False,
        'corruptions_rejected':rejected,'research_positive_factor':None,
        'research_positive_factor_null_reason':'No factor in this research template is currently verified.',
        'outputs_sha256':{key(p):digest(p) for p in args.out.iterdir() if p.is_file()}}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def sat(args):
    model,scope,bindings=bind();values=common.assignment_values(read(args.assignment)['assignment'],5238)
    with args.native_output.open('rb') as stream:nativevalues,nativerec=native.native_values(stream,5238)
    need(values==nativevalues,'complete native/JSON assignment agreement')
    with (D/'instance.cnf').open('rb') as stream:cnfrec=common.check_cnf_stream(stream,values,5238,85698)
    bits,selected,factor=raw_bits(values,model,scope)
    core=[row[3:] for row in scope['core_adjacency39'][3:]]
    raw=rawcheck.canonicalize_and_check(core,factor)
    need(raw['canonical_factor']['prescribed_gram']==scope['target_gram36'],'raw prescribed Gram identity')
    if args.decoded:
        produced=read(args.decoded)
        for field,expected in [('factor',factor),('rawbits60x6',bits),('selected_domain_selector_ids',selected)]:
            need(produced[field]==expected,'independent raw decode '+field)
        if 'canonical_factor' in produced:need(produced['canonical_factor']==raw['canonical_factor']['incidence_matrix'],'canonical factor comparison')
        if 'canonical_column_order' in produced:need(produced['canonical_column_order']==raw['canonical_new_to_raw_old_column'],'canonical column map comparison')
        need(produced['target_graph'] is False,'factor-only boundary')
    save(args.out/'independent_factor_and_partial99.json',{**raw,'bits60x6':bits,'selected_domain_selector_ids':selected})
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    report={**provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_FACTOR_OBJECT_PASS',
        'all_raw_clauses':cnfrec,'native_assignment':nativerec,'raw_component_bits_checked':360,
        'raw_exact_checks':raw['canonical_factor']['exact_checks'],'raw_object_sha256':digest(args.out/'independent_factor_and_partial99.json')}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('sat');p.add_argument('--out',type=Path,required=True);p.add_argument('--assignment',type=Path,required=True)
    p.add_argument('--native-output',type=Path,required=True);p.add_argument('--decoded',type=Path)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
