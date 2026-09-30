"""Independent literal old-body plus six necessary scalar-clause audit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,gzip,hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
D=B+'count_master_scalar_cuts/';OLD=B+'count_master_eight_orbit_cuts/';MASTER=B+'hadamard_count_master_cnf/'
PINS={D+'summary.json':'d2c4e4eb6c50e5b14aef98039b4a485e7971786ecf420e7dc339a2f167bf8502',I+'count_master_eight_orbit_cuts/summary.json':'4c919b9b48d4c9d6bf085480f9ae166172f33b457e85713c50c109c29bc57493',I+'second_count_partial_cut/summary.json':'727f9aa9aec1b3fe3f0f422e440dd0fb6fb5bfc63602c3aeee28ba3082bccfc8'}
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def composition(old,new,suffix):
    header,body=old.split(b'\n',1);need(header==b'p cnf 155939 705839','old header')
    need(new==b'p cnf 155939 705845\n'+body+suffix,'entire exact new formula')
    rows=new.splitlines();need(len(rows)==705846,'all705845 clauses')
    for row in rows[1:]:
        terms=list(map(int,row.split()));need(terms[-1]==0 and all(0<abs(x)<=155939 for x in terms[:-1]),'literal syntax and range')
    return body
def scopecheck(scope,groups):
    expected=dict(schema='COUNT_MASTER_SIX_ORBIT_PLUS_SIX_SCALAR_CUT_SCOPE_V1',base_variant='at_least_seven',minimum_exception_count=7,old_full_profile_nogoods=6,new_scalar_necessary_clauses=6,new_clause_lengths=[25]*6,raw_literal_support=groups,scalar_coordinate_pair=[9,11],ordered_distinct_fibre_instances=[[f,h]for f in range(3)for h in range(3)if f!=h],new_clauses_use_local_caps=False,new_clauses_use_symmetry=False,local_group_catalogue_membership_retained=True,full_Gram_encoded=False,all_column_caps_encoded=False,residual_D_encoded=False,full_factor=False,target_graph=False,residual_D=None)
    need(all(scope.get(k)==v for k,v in expected.items()),'exact limited scope')
    for p,h in [('base_count_model_path','base_count_model_sha256'),('old_orbit_scope_path','old_orbit_scope_sha256')]:need(sha(scope[p])==scope[h],'scope reference')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        q=sha(p);need(h is None or h==q,'identity '+str(p));need(p not in pins or pins[p]==q,'consistent binding');pins[str(p)]=q
    try:
        for p,h in PINS.items():
            pin(p,h);r=read(p)
            for field in ['inputs_sha256','outputs_sha256']:
                for ref,digest in r[field].items():pin(ref,digest)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_COUNT_MASTER_PARTIAL_CUT_CNF.md','uv.lock','pyproject.toml',MASTER+'scope.json',MASTER+'extension.json',MASTER+'summary.json','acceleration/audit_20260930_hadamard_count_master_object.py','acceleration/audit_20260930_hadamard_count_master_cnf_v2.py','acceleration/audit_20260930_count_master_eight_orbit_cut_object.py']:pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,solver_calls=0,limits_seconds=120))
        independent=read(I+'second_count_partial_cut/independent_instances.json');clauses=independent['clauses'];need(len(clauses)==6 and all(len(c)==25 for c in clauses),'six approved raw clauses')
        suffix=b''.join((' '.join(map(str,c))+' 0\n').encode('ascii')for c in clauses)
        old=(ROOT/OLD/'instance.cnf').read_bytes();new=(ROOT/D/'instance.cnf').read_bytes();body=composition(old,new,suffix)
        need((ROOT/D/'cuts.cnfpart').read_bytes()==suffix,'saved suffix')
        model=read(D+'model.json');scope=read(D+'scope.json');master=read(MASTER+'model.json');scopecheck(scope,master['groups'])
        need(model['schema']=='COUNT_MASTER_SCALAR_CUT_REFERENCE_MODEL_V1' and (model['variables'],model['clauses'],model['old_clause_count'])==(155939,705845,705839),'model dimensions')
        for pathkey,hashkey in [('cnf_path','cnf_sha256'),('scope_path','scope_sha256'),('suffix_path','suffix_sha256'),('old_model_path','old_model_sha256'),('old_cnf_path','old_cnf_sha256'),('base_count_model_path','base_count_model_sha256')]:need(sha(model[pathkey])==model[hashkey],'model reference '+pathkey)
        need(model['old_full_profile_clauses']==read(OLD+'model.json')['clause_records'],'retained old profile cuts')
        need(model['composition']==dict(base_body_sha256=hashlib.sha256(body).hexdigest(),base_body_bytes=len(body),suffix_sha256=hashlib.sha256(suffix).hexdigest(),suffix_bytes=len(suffix)),'byte accounting')
        recipes=read(B+'second_count_partial_cut/ordered_fibre_instances.json')['records'];expected=[dict(index=705840+i,fibres=r['fibres'],coordinates=r['coordinates'],clause=clauses[i],partial_restrictions=r['partial_restrictions'])for i,r in enumerate(recipes)]
        need(model['scalar_clause_records']==expected and read(D+'clause_records.json')==dict(records=expected,new_variables=0,negative_exact_channel_comparison_not_appended=True),'all clause metadata')
        for p,h in model['decoder_inputs_sha256'].items():pin(p,h)
        recovered=[]
        for record in read(D+'artifact_packages.json')['records']:
            blocks=[];offset=0
            for i,part in enumerate(record['parts']):
                compressed=(ROOT/part['path']).read_bytes();need(hashlib.sha256(compressed).hexdigest()==part['gzip_sha256'] and len(compressed)==part['gzip_bytes'],'compressed identity')
                b=gzip.decompress(compressed);need(part['index']==i and part['raw_offset']==offset and len(b)==part['raw_bytes'] and hashlib.sha256(b).hexdigest()==part['raw_sha256'],'part raw identity');blocks.append(b);offset+=len(b)
            recovered_bytes=b''.join(blocks);need(recovered_bytes==(ROOT/record['raw_path']).read_bytes() and len(recovered_bytes)==record['raw_bytes'] and hashlib.sha256(recovered_bytes).hexdigest()==record['raw_sha256'],'literal whole recovery');recovered.append(dict(path=record['raw_path'],bytes=offset,parts=len(blocks)))
        controls=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,TypeError,IndexError):controls.append(name)
            else:raise ValueError('bad control accepted '+name)
        for label,bad in [('header',new.replace(b'705845',b'705844',1)),('missing',new[:-2]),('extra',new+b'1 0\n'),('body_sign',new.replace(b'1 ',b'-1 ',1)),('suffix_sign',new[:-len(suffix)]+b'-'+suffix)]:reject(label,lambda bad=bad:composition(old,bad,suffix))
        for field in ['full_Gram_encoded','all_column_caps_encoded','residual_D_encoded','target_graph','new_clauses_use_symmetry']:
            bad=copy.deepcopy(scope);bad[field]=True;reject('scope_'+field,lambda bad=bad:scopecheck(bad,master['groups']))
        need(time.monotonic()-start<120,'audit limit');save(out/'controls.json',dict(complete_formula_positive=True,rejected=controls,complete_byte_recovery=recovered,solver_calls=0))
        stamp=datetime.now(timezone.utc).isoformat();binding=dict(id='C-FIXED-HADAMARD-SIX-PROFILE-SIX-SCALAR-CUT-COUNT-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The authenticated155939-variable705845-clause formula is exactly the previously verified >=7 count CSP with six whole-profile cuts, conjoined with the six verified partial scalar escape clauses. No variables or other clauses are added.',scope='Literal fixed six-prism support count relaxation only; count assignments need not lift to a factor.',assumptions=['The pinned prior count encoding equivalence and six profile exclusions.','The separately checked necessary scalar clauses and exact count-channel interpretation.'],dependencies=[dict(id='C-FIXED-HADAMARD-COUNT-MASTER-SIX-PROFILE-CUT-ENCODING',revision=1,relation='encoding_equivalence'),dict(id='C-FIXED-HADAMARD-SIX-PARTIAL-SCALAR-COUNT-CUTS',revision=1,relation='uses_result')],verifier='/root',producer='/root/eight_domain_audit',method='Whole-formula byte reconstruction, literal clause and metadata checks, complete compressed artifact recovery and deliberate corruptions.',shared_components=['Prior independent encoding and scalar proof gates are premises; no producer imports.','Python standard library hash/gzip/parsing only.'],inputs_sha256=pins,limitations=['No full Gram or residual D completion.','No unrestricted core/support coverage.','Composition audit does not rerun the entire old count-encoding derivation.'],created_at=stamp,updated_at=stamp);save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_CNF_PASS',timestamp=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT))for p in out.iterdir()if p.is_file()},variables=155939,clauses=705845,new_clauses=6,new_variables=0,controls_rejected=len(controls),recovery=recovered,solver_calls=0,shared_components=binding['shared_components'],elapsed_seconds=time.monotonic()-start);save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__).relative_to(ROOT))));raise
if __name__=='__main__':main()
