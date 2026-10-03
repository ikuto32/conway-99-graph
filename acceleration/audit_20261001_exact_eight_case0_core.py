"""Independent raw-clause subset, provenance, and complete trimmed-proof check."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import argparse,copy,gzip,hashlib,json,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
ENC='acceleration/results/20260930_independent_review/exact_eight_campaign/summary.json'
PROOF='acceleration/results/20260930_independent_review/exact_eight_first12_proofs/summary.json'
BASE='acceleration/results/20260930_exact_eight_first12_cnfs/case_0000/'
DRAT='build/rook-drat-checker/drat-trim.exe'
PINS={ENC:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',
      PROOF:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9',
      DRAT:'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac'}
INPUTS={}
def need(value,message):
    if not value:raise ValueError(message)
def safe(name):
    p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'contained path')
    rel=p.relative_to(ROOT).as_posix()
    need(rel!='PROMPT.md' and not rel.startswith('tools/') and not rel.endswith('hadamard_oriented_unknown/process.stdout.log'),'protected input')
    return p
def key(p):return p.relative_to(ROOT).as_posix()
def pin(name,expected=None):
    p=safe(name)
    with p.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    need(expected is None or digest==expected,'exact input '+str(name))
    need(str(name) not in INPUTS or INPUTS[str(name)]==digest,'consistent input identity')
    INPUTS[key(p)]=digest;return p
def load(name):return json.loads(pin(name).read_bytes())
def save(p,obj):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def dimacs(raw):
    header=None;rows=[];spans=[];pending=[];begin=None
    for line_number,line in enumerate(raw.decode('ascii').splitlines(),1):
        words=line.split()
        if not words or words[0]=='c':continue
        if words[0]=='p':
            need(header is None and not rows and not pending and len(words)==4 and words[1]=='cnf','one DIMACS header')
            header=tuple(map(int,words[2:]));need(all(n>=0 for n in header),'nonnegative header');continue
        need(header is not None,'header before clauses')
        for word in words:
            n=int(word)
            if begin is None:begin=line_number
            if n==0:
                rows.append(tuple(pending));spans.append([begin,line_number]);pending=[];begin=None
            else:need(abs(n)<=header[0],'variable in range');pending.append(n)
    need(header is not None and not pending and len(rows)==header[1],'complete declared clauses')
    return header,rows,spans
def occurrences(rows):
    index=defaultdict(list)
    for n,row in enumerate(rows,1):index[tuple(sorted(row))].append(n)
    return index
def mapping_for(original,core,spans):
    index=occurrences(original);result=[]
    for n,(row,span)in enumerate(zip(core,spans,strict=True),1):
        origins=index.get(tuple(sorted(row)),[]);need(origins,'core clause belongs to original')
        result.append(dict(core_clause=n,core_line_span=span,literals=list(row),all_original_clause_numbers=origins))
    return result
def owners(model):
    result=[None]*(model['clauses']+1)
    def assign(row,semantic):
        first,count=row['first_clause'],row['clause_count']
        need(type(first)is int and type(count)is int and count>=0 and first>=1 and first+count<=len(result),'ownership range')
        for i in range(first,first+count):need(result[i]is None,'ownership disjoint');result[i]=semantic
    for row in model['exact_one_prefix_rows']:assign(row,dict(family='onehot',group=row['group']))
    for cell in model['pair_cell_counts']:
        shared=dict(coordinates=cell['coordinates'],fibres=cell['fibres'])
        for group in cell['group_contributions']:
            for ch in group['channels']:assign(ch,dict(family='threshold',group=group['group'],threshold=ch['threshold'],**shared))
        assign(cell,dict(family='gram_count',bound=cell['bound'],incident_groups=[r['group']for r in cell['group_contributions']],**shared))
    need(all(row is not None for row in result[1:]),'complete ownership partition')
    return result
def run_checker(out,label,cnf,proof,expect):
    command=[str(ROOT/DRAT),str(cnf),str(proof)];start=time.monotonic();stamp=datetime.now(timezone.utc).isoformat()
    run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30)
    for tag,raw in [('stdout',run.stdout),('stderr',run.stderr)]:
        with(out/(label+'.'+tag+'.log')).open('xb')as f:f.write(raw)
    accepted=run.returncode==0 and b's VERIFIED' in run.stdout
    receipt=dict(timestamp=stamp,command=command,cwd=str(ROOT),actual_exit_code=run.returncode,accepted=accepted,
        expected=expect,elapsed_seconds=time.monotonic()-start,timeout_seconds=30,
        cnf_sha256=hashlib.sha256(cnf.read_bytes()).hexdigest(),proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest())
    save(out/(label+'.receipt.json'),receipt);need(accepted==expect,'calibrated proof outcome '+label);return receipt
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--producer-summary',required=True);ap.add_argument('--producer-summary-sha256',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    out=safe(a.out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();controls=[]
    try:
        for p,h in PINS.items():pin(p,h)
        pin(key(Path(__file__)));pin(key(Path(__file__).with_name(Path(__file__).stem+'_spec.md')));pin('uv.lock');pin('pyproject.toml')
        # Calibrate checker and independent clause/ownership paths before research replay.
        fixtures={'valid.cnf':'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n',
            'valid.drat':'1 0\n0\n','sat.cnf':'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','invalid.drat':'0\n'}
        for n,s in fixtures.items():(out/n).write_bytes(s.encode())
        checks=[run_checker(out,'positive',out/'valid.cnf',out/'valid.drat',True),
            run_checker(out,'changed_input',out/'sat.cnf',out/'valid.drat',False),
            run_checker(out,'invalid_proof',out/'valid.cnf',out/'invalid.drat',False)]
        oh,orr,osp=dimacs(b'c test\np cnf 2 3\n1\n2 0\n2 1 0\n-1 0\n')
        ch,cr,csp=dimacs(b'p cnf 2 1\n2 1 0\n');m=mapping_for(orr,cr,csp)
        need(m[0]['all_original_clause_numbers']==[1,2]and osp==[[3,4],[5,5],[6,6]],'duplicate and multiline positive control')
        def reject(label,fn):
            try:fn()
            except(ValueError,KeyError,TypeError):controls.append(label);return
            raise ValueError('corruption accepted '+label)
        reject('nonmember core clause',lambda:mapping_for(orr,[(2,)],[[1,1]]))
        reject('unterminated DIMACS',lambda:dimacs(b'p cnf 2 1\n1 2\n'))
        reject('wrong clause count',lambda:dimacs(b'p cnf 2 2\n1 0\n'))
        reject('out of range variable',lambda:dimacs(b'p cnf 2 1\n3 0\n'))
        producer=json.loads(pin(a.producer_summary,a.producer_summary_sha256).read_bytes())
        for name,digest in producer['inputs_sha256'].items():pin(name,digest)
        for name,digest in producer['outputs_sha256'].items():pin(name,digest)
        encoding=load(ENC);proof=load(PROOF)
        ec=next(r for r in encoding['checked_cases']if r['case_index']==0);pc=next(r for r in proof['case_records']if r['case_index']==0)
        need(ec['complete_raw_clause_reconstruction']and ec['all_initial_domains']and pc['outcome']=='UNSAT_VERIFIED','prior exact scoped gates')
        for field in ['case_id','cnf_path','cnf_sha256','scope_path','scope_sha256']:need(ec[field]==pc[field],'prior literal association')
        need(producer['case_id']==ec['case_id']and producer['original_cnf']['sha256']==ec['cnf_sha256'],'producer same exact formula')
        original=pin(ec['cnf_path'],ec['cnf_sha256']);model=json.loads(pin(ec['model_path'],ec['model_sha256']).read_bytes());pin(ec['scope_path'],ec['scope_sha256'])
        core=pin(producer['core']['path'],producer['core']['sha256']);lemmas=pin(producer['trimmed_lemmas']['path'],producer['trimmed_lemmas']['sha256'])
        original_header,original_rows,original_spans=dimacs(original.read_bytes());core_header,core_rows,core_spans=dimacs(core.read_bytes())
        need(original_header==(model['variables'],model['clauses'])and core_header[0]==original_header[0],'formula dimensions')
        map_rows=mapping_for(original_rows,core_rows,core_spans);metadata=owners(model)
        pmap=safe(a.producer_summary).parent/'clause_mapping.json.gz';locations=safe(a.producer_summary).parent/'original_locations.json.gz'
        need(map_rows==json.loads(gzip.decompress(pmap.read_bytes())),'complete independently derived clause map')
        used_original=sorted({n for row in map_rows for n in row['all_original_clause_numbers']})
        own_rows=[dict(original_clause=n,line_span=original_spans[n-1],semantic=metadata[n])for n in used_original]
        need(own_rows==json.loads(gzip.decompress(locations.read_bytes())),'all independently reconstructed original semantic locations')
        damaged=copy.deepcopy(map_rows);damaged[0]['all_original_clause_numbers']=[]
        reject('omitted origin',lambda:need(damaged==map_rows,'exact origins'))
        reject('wrong semantic owner',lambda:need(dict(own_rows[0]['semantic'],group=-1)==own_rows[0]['semantic'],'exact owner'))
        families=Counter();cells=set();groups=set();variables={abs(v)for row in core_rows for v in row}
        for row in map_rows:
            for n in row['all_original_clause_numbers']:
                sem=metadata[n];families[sem['family']]+=1
                if 'coordinates'in sem:cells.add(tuple(sem['coordinates']+sem['fibres']))
                if 'group'in sem:groups.add(sem['group'])
                groups.update(sem.get('incident_groups',[]))
        selector_groups={d['group']for d in model['domains']if any(c['selector']in variables for c in d['choices'])}
        derived=dict(duplicate_origin_clauses=sum(len(r['all_original_clause_numbers'])>1 for r in map_rows),
            distinct_possible_original_locations=len(used_original),family_clause_counts_with_all_origins=dict(families),
            gram_cells=[list(x)for x in sorted(cells)],coordinate_pairs=[list(x)for x in sorted({x[:2]for x in cells})],
            semantic_support_groups=sorted(groups),primary_selector_groups=sorted(selector_groups),core_variables=len(variables))
        for k,v in derived.items():need(producer[k]==v,'independent exact statistic '+k)
        checks.append(run_checker(out,'complete_core',core,lemmas,True))
        need(time.monotonic()-start<120,'bounded independent audit allocation')
        save(out/'statistics.json',derived);save(out/'controls.json',dict(rejected=controls,positive='Known nontrivial UNSAT, duplicate clauses and multiline DIMACS.'))
        result=dict(status='INDEPENDENT_EXACT_EIGHT_CASE0_CORE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
            verifier='/root',case_id=ec['case_id'],original_clauses=len(original_rows),core_clauses=len(core_rows),
            core_sha256=producer['core']['sha256'],trimmed_proof_sha256=producer['trimmed_lemmas']['sha256'],
            checked_original_locations=len(own_rows),checked_core_mapping_rows=len(map_rows),statistics=derived,checker_calls=checks,
            inputs_sha256=INPUTS,controls_rejected=controls,elapsed_seconds=time.monotonic()-start,
            shared_components=['No producer imports. Independent DIMACS parser, multiset index, complete ownership-range reconstruction and statistics.',
                'Same pinned drat-trim binary as producer; complete fresh replay with independently generated positive/corrupt controls.',
                'Original formula semantics rely on the separately authored exact first12 encoding gate and its bound model.'],
            limitations=['Only the stated literal formula/core; no new case exclusion, minimality, indispensability, generalized cut or target conclusion.',
                'All possible duplicate clause origins are retained. The variable_provenance sidecar is hash-authenticated, not completely semantically rechecked.',
                'The original full proof is authenticated through prior evidence; this audit freshly replays the complete trimmed proof on the raw subset.'],
            target_resolution='UNKNOWN',outputs_sha256={key(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in out.iterdir()if p.is_file()})
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],core_clauses=len(core_rows),groups=len(groups),coordinate_pairs=len(derived['coordinate_pairs']),cells=len(cells),elapsed_seconds=result['elapsed_seconds'])))
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS));raise
if __name__=='__main__':main()
