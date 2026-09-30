"""Mapping-only continuation of the frozen completed case0 core extraction."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter,defaultdict
import argparse,gzip,hashlib,itertools,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
GATE='acceleration/results/20260930_independent_review/exact_eight_first12_proofs/summary.json'
ENC='acceleration/results/20260930_independent_review/exact_eight_campaign/summary.json'
OLD='acceleration/results/20260930_first_third_proof_obstructions/summary.json'
BASE='acceleration/results/20260930_exact_eight_first12_cnfs/case_0000/'
CHECKER='build/rook-drat-checker/drat-trim.exe'
PINS={GATE:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9',ENC:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',OLD:'018b134a4f6682e177ba4c95cb98a77036e4a05c42735608cd07dc53af2f1951'}
TOOLS=['drat-trim.exe','build_manifest.json','build_receipt.json','upstream-drat-trim.c','windows-portability.patch','drat-trim.c','build.cmd','build_stdout.log','build_stderr.log']
PINS.update({'acceleration/results/20261001_exact_eight_case0_core/case0_core_replay.receipt.json': '1aa047f04fa4519a755ff1b62df16031c8ca9320b8d11baec2b8307365c6888b', 'acceleration/results/20261001_exact_eight_case0_core/case0_core_replay.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/case0_core_replay.stdout.log': 'f6d524c948df85cc5be458cd3cda0962f7d004694b5485e35a51d2dcc63dcf9b', 'acceleration/results/20261001_exact_eight_case0_core/case0_extract.receipt.json': 'eb44f4fdb6f6f46c9e8d568a9e3c3742b348d74b2c8948266ea9caa6cad2e44b', 'acceleration/results/20261001_exact_eight_case0_core/case0_extract.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/case0_extract.stdout.log': '317984257790a79d49b08a21f844fdab35430cc9ffd7dfbac7688314201da52a', 'acceleration/results/20261001_exact_eight_case0_core/changed_sat_extract.receipt.json': 'd193b2c972abaf6a18d99cbd564b0d95eb7a43dd546ccb7702f228280fbf6449', 'acceleration/results/20261001_exact_eight_case0_core/changed_sat_extract.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/changed_sat_extract.stdout.log': '0fb46a1f199cd45b5135224598da8c124af5007f1a5d5021042f440848891a6f', 'acceleration/results/20261001_exact_eight_case0_core/checker_usage.receipt.json': '7ea50f86ae7381f143a560bb9d6f22a198cb566ee7defd9cb4a5059f25aafa9a', 'acceleration/results/20261001_exact_eight_case0_core/checker_usage.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/checker_usage.stdout.log': 'f422797714d484701d57efb2dc2163cf673d5ff54efe1bd5dd0628f6ea805ea0', 'acceleration/results/20261001_exact_eight_case0_core/core.cnf': '900288a299800e4f322e0fd1e63c82c95dcedcec5c3e4ebe4fc29a42f77b313d', 'acceleration/results/20261001_exact_eight_case0_core/core.drat': '7b396e03bfde996f0085e3164be2d0934453aea30e8101cf61d91f1577482c5c', 'acceleration/results/20261001_exact_eight_case0_core/corrupted_core_replay.receipt.json': 'f1db1b2c0dc10fbed51d9edc61413faa6d1b6aad9c9e18e1896c5d9929fe70be', 'acceleration/results/20261001_exact_eight_case0_core/corrupted_core_replay.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/corrupted_core_replay.stdout.log': 'fc5b54ae29e5de1aab40fd8529ce5931a9cdfbb69f257442e2f7e3e87fd28082', 'acceleration/results/20261001_exact_eight_case0_core/failure.json': 'fb8d9d8f329a5835d266a59b566e9a753fd82d15a57317dc2b20afac950890d0', 'acceleration/results/20261001_exact_eight_case0_core/manifest.json': '2483b525c55940d25d12096eed13719255a1b4ec82945304968bc12c5d21933e', 'acceleration/results/20261001_exact_eight_case0_core/missing_reasoning_extract.receipt.json': 'c103147f82517fc400c3ff25dc1ca52ecf7501392e7b39738774c5dadeb8150b', 'acceleration/results/20261001_exact_eight_case0_core/missing_reasoning_extract.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/missing_reasoning_extract.stdout.log': '32787a8554ee451f5921bfe5a6cc0a1316ae9cad0919a58d5711d54fa9a4e6d0', 'acceleration/results/20261001_exact_eight_case0_core/positive_core_replay.receipt.json': '58f5c8c7d529b0df5eb80827a18e5c3f72a17bd6f314de6ab08d8ac74492bfc5', 'acceleration/results/20261001_exact_eight_case0_core/positive_core_replay.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/positive_core_replay.stdout.log': 'f5f7c38617a5dc16278f2d3bfebea955df33d8ebc859cb399c0793c6875d3b0e', 'acceleration/results/20261001_exact_eight_case0_core/positive_extract.receipt.json': '996abcda335d51537088513b86a630e48a203412fad4e75ae8cbeecc20d2a677', 'acceleration/results/20261001_exact_eight_case0_core/positive_extract.stderr.log': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'acceleration/results/20261001_exact_eight_case0_core/positive_extract.stdout.log': 'd34da2d7c8b88650dae9cea0093128fb109b331da73d7bb136068e3574a3bb40', 'acceleration/results/20261001_exact_eight_case0_core/tiny_core.cnf': 'fcd0258b989f04b14820f83b474e024f2bb24404c6cb4bd411d02e5ced21e9cc', 'acceleration/results/20261001_exact_eight_case0_core/tiny_core.drat': '624bdaa120adfa77d4b54fbaf34237709a195493bd7ec9df6d02717347b112fb', 'acceleration/results/20261001_exact_eight_case0_core/tiny_empty_only.drat': '9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa', 'acceleration/results/20261001_exact_eight_case0_core/tiny_sat.cnf': 'cbff19c5ea74c8fc8e307afe9fe1ce08682bb98ec3b10983068b10376f847534', 'acceleration/results/20261001_exact_eight_case0_core/tiny_unsat.cnf': 'bdcfed14408fb3f368fe82437336d283a9dedc953677460e9c7317724c5e1e58', 'acceleration/results/20261001_exact_eight_case0_core/tiny_valid.drat': 'd027e90f95ec33e919db5f35613674e052720492ec373c64724e47eb9c766ea0', 'acceleration/theory_20261001_exact_eight_case0_core.py': '214b813d9622609a252d54c340366fa4c250ac10a509d3aa83e1588c961bd1f4', 'acceleration/theory_20261001_exact_eight_case0_core_spec.md': 'a71883409b2c0572fa1788a6750e1ba575ddbb8bb6379e9bdc5b84371f9a16e3'})
INPUTS={}
def need(v,m):
    if not v:raise ValueError(m)
def safe(p):
    q=(ROOT/p).resolve();need(q.is_relative_to(ROOT),'repository containment');r=q.relative_to(ROOT).as_posix();need(r!='PROMPT.md'and not r.startswith('tools/')and r!='acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log','protected input');return q
def key(p):return safe(p).relative_to(ROOT).as_posix()
def sha(p):
    with safe(p).open('rb')as f:d=hashlib.file_digest(f,'sha256').hexdigest()
    return d
def pin(p,h=None):
    p=key(p);d=sha(p);need(h is None or h==d,'exact hash '+p);INPUTS[p]=d;return d
def read(p):pin(p);return json.loads(safe(p).read_bytes())
def save(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def packed(p,v):
    data=(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
    with p.open('xb')as raw:
        with gzip.GzipFile(fileobj=raw,filename='',mode='wb',mtime=0,compresslevel=9)as f:f.write(data)
def cnf(p):
    header=None;rows=[];locations=[];pending=[];start=None
    for ln,line in enumerate(safe(p).read_text(encoding='ascii').splitlines(),1):
        if not line.strip()or line.lstrip().startswith('c'):continue
        if line.startswith('p '):
            need(header is None and not pending,'unique header');parts=line.split();need(parts[:2]==['p','cnf']and len(parts)==4,'DIMACS header');header=tuple(map(int,parts[2:]));continue
        need(header is not None,'header precedes clauses')
        for v in map(int,line.split()):
            if start is None:start=ln
            if v:need(abs(v)<=header[0],'literal bound');pending.append(v)
            else:rows.append(tuple(pending));locations.append([start,ln]);pending=[];start=None
    need(header is not None and not pending and len(rows)==header[1],'complete DIMACS');return header,rows,locations
def origins(original,core):
    loc=defaultdict(list)
    for i,c in enumerate(original,1):loc[tuple(sorted(c))].append(i)
    counts=Counter(tuple(sorted(c))for c in core)
    need(all(len(loc[k])>=v for k,v in counts.items()),'core exact clause-multiset subset')
    return [list(loc[tuple(sorted(c))])for c in core]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=safe(args.out);out.mkdir(parents=True,exist_ok=False);calls=[];start=time.monotonic()
    try:
        for p,h in PINS.items():pin(p,h)
        gate=read(GATE);enc=read(ENC);old=read(OLD)
        need(gate['status']=='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS','complete first12 proof premise')
        row=next(r for r in gate['case_records']if r['case_index']==0)
        need(row['outcome']=='UNSAT_VERIFIED'and row['trace']['complete_proof']and row['case_id']=='exact_eight_a2a3d60e21811916cde9269f08221000990e8235629bcc67d880ae472b6a18f9','literal selected case0')
        formula=row['cnf_path'];proof=row['trace']['path'];pin(formula,row['cnf_sha256']);pin(proof,row['trace']['sha256']);pin(row['scope_path'],row['scope_sha256'])
        need(formula==BASE+'instance.cnf','exact case0 formula')
        modelpath=BASE+'model.json';pin(modelpath,enc['inputs_sha256'][modelpath]);model=read(modelpath);scope=read(row['scope_path'])
        need(model['scope_sha256']==row['scope_sha256']and scope['selected_full_count_sha256']==row['full_count_profile_sha256'],'literal model/scope/count')
        for name in TOOLS:
            p='build/rook-drat-checker/'+name;pin(p,gate['inputs_sha256'][p])
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        prior_formula_pins={p:h for p,h in old['inputs_sha256'].items()if p.endswith('/instance.cnf')}
        need(row['cnf_sha256']not in prior_formula_pins.values(),'not earlier historical core formula')
        save(out/'manifest.json',dict(status='CANDIDATE_PREREGISTERED_CORE_SCOUT',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=INPUTS,selection=row,duplicate_check=dict(existing_core_summary=OLD,prior_formula_hashes=prior_formula_pins,exact_requested_formula_already_extracted=False,repository_search='Read-only source/document search for proof core, extraction, core-output and exact_eight names; historical first/third and wave154 identified, no exact6fecea81 core found.'),limits=dict(current_checker_wall_seconds=0,mapping_wall_seconds=120,current_research_extractions=0,historical_research_extractions=1,research_sat_calls=0),checker_source_commit=read('build/rook-drat-checker/build_manifest.json')['upstream_commit'],independent_approval=False))
        # No checker launch in this continuation. Authenticate the completed v1 calls.
        previous=safe('acceleration/results/20261001_exact_eight_case0_core')
        failure=read(previous/'failure.json');need(failure['error']=="KeyError('word_indices')",'exact preserved mapping failure')
        calls=failure['checker_calls'];need(len(calls)==8,'usage plus five controls plus extraction/replay')
        for rec in calls:
            need(read(previous/(rec['name']+'.receipt.json'))==rec,'frozen complete checker receipt')
            pin(previous/(rec['name']+'.stdout.log'),rec['stdout_sha256']);pin(previous/(rec['name']+'.stderr.log'),rec['stderr_sha256'])
            need(rec['checker_sha256']==INPUTS[CHECKER] and not rec['timed_out'],'authenticated unchanged checker/no timeout')
            if rec['expected_acceptance']is not None:need(rec['accepted']==rec['expected_acceptance'],'prior calibrated outcome')
        need([r['name']for r in calls[-2:]]==['case0_extract','case0_core_replay']and all(r['accepted']for r in calls[-2:]),'one completed extraction/replay')
        core=previous/'core.cnf';lemmas=previous/'core.drat'
        need(origins([(1,2),(2,1),(-1,)],[(2,1)])==[[1,2]],'duplicate origin regression')
        rejected=[]
        for label,original,smallcore in [('invented clause',[(1,)],[(2,)]),('excess duplicate count',[(1,)],[(1,),(1,)])]:
            try:origins(original,smallcore)
            except ValueError:rejected.append(label)
            else:raise ValueError('mapping corruption accepted')
        mapping_start=time.monotonic();header,original,lines=cnf(formula);ch,cr,clines=cnf(core)
        need(header==(model['variables'],model['clauses']),'actual full formula dimensions');matches=origins(original,cr)
        labels=[None]*len(original);variables={}
        def label(r,meta,allowed):
            indices=range(r['first_clause']-1,r['first_clause']-1+r['clause_count'])
            for i in indices:
                need(0<=i<len(labels)and labels[i]is None,'disjoint exhaustive origin interval');need({abs(v)for v in original[i]}<=set(allowed),'semantic clause variable boundary');labels[i]=meta
        for d in model['domains']:
            for c in d['choices']:
                v=c['selector'];need(v not in variables,'unique primary provenance');variables[v]=dict(kind='local_choice_selector',group=d['group'],choice_index=c['choice_index'],support=d['support'],local_survivor_index=c.get('local_survivor_index'),word_indices=c.get('word_indices'),word_indices_null_reason=None if 'word_indices'in c else 'Balanced normalized model stores colour words directly, not historical local-word indices.',colour_words=c['colour_words'])
        for r in model['exact_one_prefix_rows']:
            g=r['group'];need(r['selectors']==[c['selector']for c in model['domains'][g]['choices']],'onehot selector domain identity')
            for i,v in enumerate(r['prefixes']):need(v not in variables,'unique prefix variable');variables[v]=dict(kind='onehot_prefix_auxiliary',group=g,prefix_position=i,semantics='Position in authenticated exact-one prefix row; not an independent factor variable.')
            label(r,dict(family='onehot',group=g),r['selectors']+r['prefixes'])
        for cell in model['pair_cell_counts']:
            a,b=cell['coordinates'];f,z=cell['fibres'];ids=[]
            for part in cell['group_contributions']:
                g=part['group'];d=model['domains'][g];ia=d['support'].index(a);ib=d['support'].index(b)
                coeff=[sum(w[ia]==f and w[ib]==z for w in c['colour_words'])for c in d['choices']];need(coeff==part['coefficients'],'literal raw option contribution')
                for channel in part['channels']:
                    v=channel['variable'];t=channel['threshold'];need(channel['selectors']==[c['selector']for c,k in zip(d['choices'],coeff)if k>=t],'threshold subset exact')
                    need(v not in variables,'unique channel provenance');variables[v]=dict(kind='weighted_threshold_channel',coordinates=[a,b],fibres=[f,z],group=g,threshold=t,selectors=channel['selectors']);ids.append(v)
                    label(channel,dict(family='threshold',coordinates=[a,b],fibres=[f,z],group=g,threshold=t),[v]+channel['selectors'])
            need(ids==cell['count_inputs'],'count cell channel population');label(cell,dict(family='gram_count',coordinates=[a,b],fibres=[f,z],bound=cell['bound'],incident_groups=[r['group']for r in cell['group_contributions']]),ids)
        need(all(x is not None for x in labels)and set(variables)==set(range(1,header[0]+1)),'all original clauses and variables assigned provenance')
        mapping=[];union=set();family_counts=Counter();cellset=set();pairset=set();group_set=set();ambiguous=0
        for i,(c,origins_)in enumerate(zip(cr,matches),1):
            union.update(origins_);ambiguous+=len(origins_)>1;semantics=[labels[j-1]for j in origins_]
            mapping.append(dict(core_clause=i,core_line_span=clines[i-1],literals=list(c),all_original_clause_numbers=origins_))
            for family in {m['family']for m in semantics}:family_counts[family]+=1
            for m in semantics:
                if 'coordinates'in m:pairset.add(tuple(m['coordinates']));cellset.add(tuple(m['coordinates']+m['fibres']))
                if 'group'in m:group_set.add(m['group'])
                group_set.update(m.get('incident_groups',[]))
        corevars=sorted({abs(v)for c in cr for v in c});primarygroups=sorted({variables[v]['group']for v in corevars if variables[v]['kind']=='local_choice_selector'})
        packed(out/'clause_mapping.json.gz',mapping)
        packed(out/'original_locations.json.gz',[dict(original_clause=j,line_span=lines[j-1],semantic=labels[j-1])for j in sorted(union)])
        packed(out/'variable_provenance.json.gz',[dict(variable=v,**variables[v],occurs_in_core=v in set(corevars))for v in sorted(variables)])
        need(time.monotonic()-mapping_start<120,'mapping allocation')
        result=dict(status='CANDIDATE_EXACT_EIGHT_CASE0_CORE_MAPPING_CONTINUATION_COMPLETE',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],inputs_sha256=INPUTS,case_id=row['case_id'],original_cnf=dict(path=formula,sha256=row['cnf_sha256'],variables=header[0],clauses=len(original)),original_proof=row['trace'],core=dict(path=key(core),sha256=sha(core),bytes=core.stat().st_size,variables=ch[0],clauses=len(cr)),trimmed_lemmas=dict(path=key(lemmas),sha256=sha(lemmas),bytes=lemmas.stat().st_size),duplicate_origin_clauses=ambiguous,distinct_possible_original_locations=len(union),family_clause_counts_with_all_origins=dict(family_counts),gram_cells=sorted(cellset),coordinate_pairs=sorted(pairset),semantic_support_groups=sorted(group_set),primary_selector_groups=primarygroups,core_variables=len(corevars),controls=dict(complete_tiny_truth_tables=True,positive_extraction_and_replay=True,corrupt_checker_inputs_rejected=3,duplicate_origin_positive=True,malformed_mappings_rejected=rejected),checker_calls=calls,checker_seconds=sum(r['wall_seconds']for r in calls),mapping_seconds=time.monotonic()-mapping_start,total_seconds=time.monotonic()-start,research_extraction_calls=1,historical_research_extraction_calls=1,current_run_research_extraction_calls=0,current_run_checker_calls=0,research_sat_calls=0,preserved_failure='acceleration/results/20261001_exact_eight_case0_core/failure.json',independent_approval=False,claim_status='CANDIDATE',limitations=['Producer-level calibrated checker outputs and semantic mapping only; not independently approved.','All duplicate original clause locations retained; literal order normalized for subset matching but multiplicity preserved.','Core is not minimal; omitted clauses need not be dispensable globally, and present clauses/groups/Gram cells are not asserted indispensable.','This exact fixed support/count profile only. No general cut, class-wide contradiction, target automorphism or target exclusion.','Provenance uses prior independently checked raw model ranges, strengthened by literal variable-boundary and option-contribution checks; checker/compiler/Windows shim remain shared trusted components.'],outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()})
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],core_clauses=len(cr),coordinate_pairs=len(pairset),gram_cells=len(cellset),support_groups=len(group_set),sha256=sha(out/'summary.json'))))
    except BaseException as ex:
        save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),inputs_sha256=INPUTS,checker_calls=calls,research_sat_calls=0));raise
if __name__=='__main__':main()
