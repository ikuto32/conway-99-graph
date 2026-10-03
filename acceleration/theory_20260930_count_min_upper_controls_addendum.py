"""Append-only completion of the inventory's malformed-recipe controls.

Freeze before running. Reconstruct saved target, complete contributor population,
threshold membership and product bindings from immutable raw inputs, without
importing the inventory producer. Deliberately corrupt each and require rejection.
This is producer calibration, not independent approval. No CNF/native/ledger.
Budget10seconds; fresh output only. It supplements rather than alters the original
run, whose main control file explicitly recorded three structural corruptions and
all selected-count threshold bit flips but no target/contributor mutation records.
"""
import argparse, copy, hashlib, itertools, json, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'acceleration/results/20260930_count_min_upper_inventory'
def sha(p):
    with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def need(x,msg):
    if not x:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
    with Path(p).open('x',encoding='utf8') as s:json.dump(x,s,sort_keys=True);s.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(exist_ok=False,parents=True);start=time.monotonic()
    need(sha(DATA/'summary.json')=='187f1c826dc2e9a71942a59b62abf18ee9c06867ead5f815495e24d9514850ad','frozen inventory')
    summary=read(DATA/'summary.json')
    for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():need(sha(ROOT/p)==h,'bound input '+p)
    raw=read(ROOT/'acceleration/results/20260930_hadamard20_support/six_prism.json')
    master=read(ROOT/'acceleration/results/20260930_hadamard_count_master_cnf/model.json')
    groups=list(dict.fromkeys(map(tuple,raw['support_columns'])));C=raw['core_adjacency']
    channels={(x['coordinate'],x['group']):x for x in master['count_channels']}
    ts=read(DATA/'threshold_channels.json')['records'];ps=read(DATA/'overlap_products.json')['records'];cells=read(DATA/'scalar_cells.json')['records']
    tmap={(x['coordinate'],x['group'],x['fibre'],x['threshold']):x['variable'] for x in ts}
    def threshold(x):
        ch=channels[x['coordinate'],x['group']];f=x['fibre'];t=x['threshold'];need(t in [1,2],'threshold range')
        expected=[v for v,c in zip(ch['variables'],ch['values']) if c[f]>=t]
        need(x['selected_alternatives']==expected,'threshold subset membership')
    def product(x):
        a,b=x['coordinates'];f,h=x['fibres'];g=x['group'];t=x['threshold']
        need([x['left'],x['right']]==[tmap[a,g,f,t],tmap[b,g,h,t]],'two actual threshold IDs')
    def cell(x):
        a,b=x['coordinates'];f,h=x['fibres'];i,j=12*f+a,12*h+b
        target=12*int(i==j)-C[i][j]-sum(C[i][k]*C[k][j] for k in range(36))+2-int(f==h)
        need(x['target']==target,'literal target')
        need(x['incident_groups']==[g for g,s in enumerate(groups) if a in s and b in s],'complete incident groups')
        expected=[p['variable'] for p in ps if p['coordinates']==[a,b] and p['fibres']==[f,h]]
        need(x['product_variables']==expected and len(expected)==5*target,'complete product population')
    for x in ts:threshold(x)
    for x in ps:product(x)
    for x in cells:cell(x)
    records=[]
    def reject(label,value,fn):
        try:fn(value)
        except(ValueError,KeyError):records.append(dict(name=label,rejected=True))
        else:raise ValueError('corruption accepted '+label)
    x=copy.deepcopy(cells[0]);x['target']+=1;reject('changed_target',x,cell)
    x=copy.deepcopy(cells[0]);x['incident_groups']=x['incident_groups'][:-1];reject('missing_group',x,cell)
    x=copy.deepcopy(cells[0]);x['product_variables']=x['product_variables'][:-1];reject('missing_product',x,cell)
    x=copy.deepcopy(next(x for x in ts if x['selected_alternatives']));x['selected_alternatives']=x['selected_alternatives'][:-1];reject('omitted_threshold_alternative',x,threshold)
    x=copy.deepcopy(ts[0]);x['threshold']=3;reject('wrong_threshold',x,threshold)
    x=copy.deepcopy(ps[0]);x['left']=-x['left'];reject('negated_AND_input',x,product)
    need(time.monotonic()-start<10,'ten-second allocation')
    save(out/'summary.json',dict(status='CANDIDATE_COUNT_MIN_UPPER_RECIPE_CONTROL_ADDENDUM',input_summary_sha256=sha(DATA/'summary.json'),source_sha256=sha(__file__),controls=records,positive_thresholds=len(ts),positive_products=len(ps),positive_cells=len(cells),elapsed_seconds=time.monotonic()-start,independent_approval=False,old_files_unchanged=True))
    print(sha(out/'summary.json'))
if __name__=='__main__':main()
