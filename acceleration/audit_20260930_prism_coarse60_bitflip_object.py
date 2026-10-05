"""Independent normalized coarse60 assignment and complete raw-factor wrapper."""
from pathlib import Path
from types import SimpleNamespace
import argparse,gzip,io,json,sys
import audit_20260930_prism_coarse60_bitlift_object as base

ROOT=base.ROOT
D=ROOT/'acceleration/results/20260930_prism_coarse60_bitflip'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitflip/summary.json'
GATE_SHA='ea41069f8bad705c1163e55d04735bca99c24276e447e1b1437ac7aa3d1b7123'
need=base.need;read=base.read;save=base.save;digest=base.digest;key=base.key

def bind():
    model,scope,bindings=base.bind()
    old=ROOT/'acceleration/results/20260930_independent_review/prism_coarse60_bitlift_object_calibration/summary.json'
    need(digest(old)=='008c12dd2b5e84c26dc30d2416b878b4fd87ab3b001360f664a4ac29003c00a4','frozen complete raw object calibration')
    need(digest(GATE)==GATE_SHA and read(GATE)['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITFLIP_NORMALIZATION_PASS','independent normalization gate')
    bindings.update(read(GATE)['inputs_sha256']);bindings[key(GATE)]=GATE_SHA;bindings[key(old)]=digest(old)
    for p in [Path(__file__),Path(base.__file__),ROOT/'docs/AUDIT_20260930_PRISM_COARSE60_BITFLIP_OBJECT.md']:bindings[key(p)]=digest(p)
    for p,h in bindings.items():need(digest(ROOT/p)==h,'exact bound input '+p)
    need(digest(D/'instance.cnf')=='afa6581bfc3309e6c1ddb434996fb53aee712771fabaf2aef9432cfc30dc3c72','normalized CNF')
    ext=read(D/'extension.json');need(ext['appended_unit_literals']==list(range(-2449,-2455,-1)),'unit metadata')
    return model,scope,bindings

def first_zero(values,model):
    first=[v for v in model['raw_bits'] if v['column']==0]
    need(len(first)==6 and [v['component'] for v in first]==list(range(6)),'all first-column labels')
    need(all(values[v['variable']]==0 for v in first),'all six actual first-column bits zero')

def calibrate(args):
    model,scope,bindings=bind();out=args.out
    nested=out/'base_raw_calibration';nested.mkdir();base.calibrate(SimpleNamespace(out=nested))
    nested_report=read(nested/'summary.json');need(nested_report['status']=='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_OBJECT_CHECKER_CALIBRATION_PASS','reexecuted raw calibration')
    values=bytearray(5239);chosen=[0]*18
    for a in range(6):
        g=scope['columns60'][0][a];domain=model['domains'][3*a+g];position=domain['column_positions'].index(0)
        flip=(domain['local_masks'][0]>>position)&1
        for h in range(3):
            d=model['domains'][3*a+h];target=d['local_masks'][0]^(((1<<20)-1) if flip else 0);chosen[3*a+h]=d['local_masks'].index(target)
    for d,j,prefix in zip(model['domains'],chosen,model['exact_one_prefixes'],strict=True):
        values[d['selectors'][j]]=1
        for t,column in enumerate(d['column_positions']):values[2449+6*column+d['component']]=(d['local_masks'][j]>>t)&1
        for row in prefix['prefixes']:values[row['variable']]=values[row['previous']]|values[row['selector']]
    first_zero(values,model);bits,selected,factor=base.raw_bits(values,model,scope);need(bits[0]==[0]*6,'literal normalized raw bits')
    signed=[i if values[i] else -i for i in range(1,5239)]
    native=b'c SYNTHETIC CODEC; NOT RESEARCH SAT\ns SATISFIABLE\n'+b''.join(('v '+' '.join(map(str,signed[i:i+80]))+(' 0' if i+80>=5238 else '')+'\n').encode() for i in range(0,5238,80))
    parsed,native_record=base.native.native_values(io.BytesIO(native),5238)
    need(parsed==base.common.assignment_values(signed,5238),'complete native/JSON synthetic agreement')
    cnf=b'p cnf 5238 85704\n'+b''.join(f'{signed[i%5238]} 0\n'.encode() for i in range(85698))+b''.join(f'{v} 0\n'.encode() for v in range(-2449,-2455,-1))
    cnf_record=base.common.check_cnf_stream(io.BytesIO(cnf),parsed,5238,85704)
    for label,blob in [('native',native),('cnf',cnf)]:
        with gzip.open(out/f'synthetic_normalized_fullsize.{label}.gz','wb') as f:f.write(blob)
    rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise ValueError('corrupt control accepted '+label)
    for a in range(6):
        bad=values[:];bad[2449+a]=1
        reject('first_bit_'+str(a),lambda bad=bad:first_zero(bad,model))
    reject('false_appended_unit',lambda:base.common.check_cnf_stream(io.BytesIO(cnf[:-len(b'-2454 0\n')]+b'2454 0\n'),parsed,5238,85704))
    reject('wrong_clause_count',lambda:base.common.check_cnf_stream(io.BytesIO(cnf.replace(b'85704',b'85698',1)),parsed,5238,85704))
    reject('incomplete_assignment',lambda:base.common.assignment_values(signed[:-1],5238))
    reject('native_missing_terminator',lambda:base.native.native_values(io.BytesIO(native.rsplit(b' 0\n',1)[0]+b'\n'),5238))
    report={**base.provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_COARSE60_BITFLIP_OBJECT_CHECKER_CALIBRATION_PASS',
        'encoding_gate_sha256':GATE_SHA,'variables':5238,'clauses':85704,'appended_units':list(range(-2449,-2455,-1)),
        'nested_raw_control_sha256':digest(nested/'summary.json'),'nested_corruptions_rejected':nested_report['corruptions_rejected'],
        'known_nonempty_positive':nested_report['known_nonempty_positive'],'new_corruptions_rejected':rejected,
        'synthetic_native':native_record,'synthetic_clauses':cnf_record,'research_factor_positive':None,
        'research_factor_positive_null_reason':'No factor for this exact research template is known; synthetic codecs and local-mask examples are not research SAT.',
        'outputs_sha256':{key(p):digest(p) for p in out.rglob('*') if p.is_file()}}
    save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))

def sat(args):
    model,scope,bindings=bind();values=base.common.assignment_values(read(args.assignment)['assignment'],5238)
    with args.native_output.open('rb') as f:native_values,native_record=base.native.native_values(f,5238)
    need(values==native_values,'complete native/JSON assignment agreement')
    with (D/'instance.cnf').open('rb') as f:cnf_record=base.common.check_cnf_stream(f,values,5238,85704)
    first_zero(values,model);bits,selected,factor=base.raw_bits(values,model,scope);need(bits[0]==[0]*6,'literal normalized raw factor choices')
    core=[r[3:] for r in scope['core_adjacency39'][3:]]
    raw=base.rawcheck.canonicalize_and_check(core,factor)
    need(raw['canonical_factor']['prescribed_gram']==scope['target_gram36'],'prescribed raw Gram')
    if args.decoded:
        dec=read(args.decoded)
        for field,want in [('factor',factor),('rawbits60x6',bits),('selected_domain_selector_ids',selected)]:need(dec[field]==want,'independent producer comparison '+field)
        if 'canonical_factor' in dec:need(dec['canonical_factor']==raw['canonical_factor']['incidence_matrix'],'canonical raw comparison')
        if 'canonical_column_order' in dec:need(dec['canonical_column_order']==raw['canonical_new_to_raw_old_column'],'canonical column bijection')
        need(dec['target_graph'] is False,'factor-only scope')
    save(args.out/'independent_factor_and_partial99.json',{**raw,'bits60x6':bits,'selected_domain_selector_ids':selected,'first_column_bits_zero':True})
    for p in [args.assignment,args.native_output]+([args.decoded] if args.decoded else []):bindings[key(p)]=digest(p)
    report={**base.provenance(bindings),'status':'INDEPENDENT_SIX_PRISM_COARSE60_BITFLIP_FACTOR_OBJECT_PASS','encoding_gate_sha256':GATE_SHA,
        'all_raw_clauses':cnf_record,'native_assignment':native_record,'raw_component_bits_checked':360,'first_column_bits_zero':True,
        'raw_exact_checks':raw['canonical_factor']['exact_checks'],'raw_object_sha256':digest(args.out/'independent_factor_and_partial99.json')}
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    c=sub.add_parser('calibrate');c.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('sat');s.add_argument('--out',type=Path,required=True);s.add_argument('--assignment',type=Path,required=True);s.add_argument('--native-output',type=Path,required=True);s.add_argument('--decoded',type=Path)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    try:(calibrate if args.mode=='calibrate' else sat)(args)
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
