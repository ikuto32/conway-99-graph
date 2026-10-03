"""AST and isolated selection controls; do not import or execute the build wrapper."""
import ast,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';DRIVER=A/'build_20260930_exact_eight_explicit_batch.py';SPEC=DRIVER.with_name(DRIVER.stem+'_spec.md');MANIFEST=A/'results/20260930_exact_eight_campaign_preparation/campaign_manifest.json';OUT=A/'results/20260930_exact_eight_explicit_batch_preparation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    OUT.mkdir(exist_ok=False);text=DRIVER.read_text(encoding='utf8');tree=ast.parse(text);compile(text,str(DRIVER),'exec');assert sha(MANIFEST)=='e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba';u=json.loads(MANIFEST.read_bytes());ns=dict(ROOT=ROOT,MANIFEST=MANIFEST,PINS={MANIFEST:sha(MANIFEST)},Path=Path)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in['key','need','repo_file','selection_ids']];exec(compile(ast.Module(body=nodes,type_ignores=[]),'<isolated selection validation>','exec'),ns)
    select=ns['selection_ids'];ids=[u['records'][100]['case_id'],u['records'][0]['case_id']];base=dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',campaign_manifest_path=key(MANIFEST),campaign_manifest_sha256=sha(MANIFEST),ordered_case_ids=ids,selection_reason='Isolated control only; creates no research selection.')
    assert select(base,u)==ids;assert select(dict(base,ordered_case_ids=ids[::-1]),u)==ids[::-1];controls=[dict(name='literal caller order preserved',passed=True),dict(name='reversed caller order preserved',passed=True)]
    for field,value in [('schema','wrong'),('campaign_manifest_path','wrong'),('campaign_manifest_sha256','0'*64),('ordered_case_ids',[]),('ordered_case_ids',[ids[0],ids[0]]),('ordered_case_ids',['exact_eight_'+'0'*64]),('ordered_case_ids',ids[0]),('selection_reason',' ')]:
        x=copy.deepcopy(base);x[field]=value
        try:select(x,u)
        except(ValueError,KeyError):controls.append(dict(name='reject malformed '+field,value=value,rejected=True))
        else:raise AssertionError('invalid selection accepted '+field)
    assert ns['repo_file']('uv.lock')==ROOT/'uv.lock'
    for bad in['../uv.lock','acceleration/../uv.lock','C:/Windows/not-authorized.txt','acceleration\\bad.json','/tmp/bad']:
        try:ns['repo_file'](bad)
        except ValueError:controls.append(dict(name='reject path escape/noncanonical',value=bad,rejected=True))
        else:raise AssertionError('bad path accepted')
    imports=[n for n in ast.walk(tree)if isinstance(n,(ast.Import,ast.ImportFrom))];assert all(not isinstance(n,ast.ImportFrom)or n.module in['datetime','pathlib']for n in imports);assert 'cadical'not in text and 'automatic_skip=False'in text and 'previous_outcomes_consumed=0'in text
    args=[n.args[0].value for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='add_argument'and n.args and isinstance(n.args[0],ast.Constant)];assert args==['mode','--selection','--selection-sha256','--attempt-id','--seconds','--out'];assert 'resume'not in args
    subprocesses=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='subprocess'];assert len(subprocesses)==1 and subprocesses[0].func.attr=='run'
    pins={key(p):sha(p)for p in[DRIVER,SPEC,MANIFEST,Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']};save(OUT/'summary.json',dict(status='CANDIDATE_EXPLICIT_BUILD_BATCH_SOURCE_PREPARATION_PASS',inputs_sha256=pins,controls=controls,AST_compile_only=True,isolated_function_controls=True,runtime_repository_imports=0,wrapper_plan_calls=0,wrapper_build_calls=0,producer_calls=0,native_calls=0,new_selection_artifacts=0,new_formula_builds=0,independent_approval=False,limitations=['No wrapper entrypoint was called.','Future root supplies a separately hash-bound literal ordered selection.','Source-only checks do not independently approve future formulas or campaign coverage.']));print(json.dumps(dict(driver_sha256=sha(DRIVER),spec_sha256=sha(SPEC),summary_sha256=sha(OUT/'summary.json'),controls=len(controls))))
if __name__=='__main__':
    try:main()
    except BaseException as ex:
        if OUT.is_dir()and not(OUT/'failure.json').exists():save(OUT/'failure.json',dict(error=repr(ex),source_sha256=sha(Path(__file__)),native_calls=0,new_formula_builds=0))
        raise
