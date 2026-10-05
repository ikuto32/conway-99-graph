"""Candidate exact incidence channels and target-necessary caps for complete six-prism domains."""
from datetime import datetime,timezone
from hashlib import file_digest
from itertools import combinations,product
from pathlib import Path
import argparse
import gzip
import json
import platform
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'acceleration/results/20260930_prism_all_columns'
NORMAL=ROOT/'acceleration/results/20260930_prism_first_choice_normalization'
AUDIT=ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
NORMAL_AUDIT=ROOT/'acceleration/results/20260930_independent_review/prism_first_choice_normalization/summary.json'
PINS={BASE/'model.json':'a801e721a4c03d18e2fa9711a60f053895a4bfb8898b264f5174bcc36265f038',
      NORMAL/'instance.cnf':'9a9188ce1654228f3a88c59994d5324ad3d438c7baed0aff4606e3f908ca881b',
      AUDIT:'07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3',
      NORMAL_AUDIT:'c5963305cff69ef0242db04d373fdf7cba1339e547191554b64b319165bf8223'}

def need(b,s):
    if not b:raise ValueError(s)
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def partial(model,supports,columns):
    f=[[int(i in pair) for pair in model['canonical_C0_columns']] for i in range(12)]+[[-1]*60 for _ in range(24)]
    for col,rows in zip(columns,supports):
        need(any(q['column']==col and q['rows']==rows for q in model['choices']),'exact allowed column choice')
        for i in range(36):f[i][col]=int(i in rows)
    gram=model['target_gram'];counts=[[sum(int(f[i][d]==1 and f[j][d]==1) for d in range(60)) for j in range(36)] for i in range(36)]
    need(all(counts[i][j]<=gram[i][j] for i in range(36) for j in range(36)),'all known Gram contribution caps')
    return f,counts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def cap():need(time.monotonic()-start<120,'120-second producer limit')
    for p,h in PINS.items():need(digest(p)==h,'pinned input');bindings[key(p)]=h
    for p in [AUDIT,NORMAL_AUDIT]:
        for name,h in read(p)['inputs_sha256'].items():need(digest(ROOT/name)==h,'transitive audit input');bindings[name]=h
    for p in [Path(__file__),Path(__file__).with_name('theory_20260930_prism_column_caps_v2_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
    model=read(BASE/'model.json');choices=model['choices'];gram=model['target_gram'];labels=[tuple(q) for q in model['canonical_C0_columns']]
    need(len(choices)==5760 and all(sum(q['column']==d for q in choices)==96 for d in range(60)),'complete frozen96choice domains')
    columns=[labels.index((0,2)),labels.index((0,4))];supports=[[0,2,16,18,32,34],[0,4,14,18,32,35]]
    f,counts=partial(model,supports,columns);choice_ids=[next(q['id'] for q in choices if q['column']==d and q['rows']==r) for d,r in zip(columns,supports)]
    need(choice_ids[0]==1 and len(set(supports[0])&set(supports[1]))==3,'normalized partial overlap3 witness')
    local=dict(status='CANDIDATE_PARTIAL_DOMAIN_WITNESS',selected_choice_ids=choice_ids,columns=columns,column_supports=supports,shared_rows=sorted(set(supports[0])&set(supports[1])),partial_factor_unknown_minus1=f,known_Gram_contributions=counts,prescribed_gram=gram,all_known_Gram_caps=True,complete_abstract_factor=False,conclusion='Column domains plus entrywise known-Gram caps do not imply outside-column caps; full-factor automaticity remains UNKNOWN.')
    save(out/'local_implication_analysis.json',local)
    for q in choices:
        need(sum(gram[i][j] for i in q['rows'] for j in q['rows'])==114,'all5760 allowed column quadratic values')
    distributions=[{0:17,1:30,2:12},{0:16,1:33,2:9,3:1}]
    for dist in distributions:need(sum(dist.values())==59 and sum(k*v for k,v in dist.items())==54 and sum(k*k*v for k,v in dist.items())==78,'exact moment counterdistribution')
    save(out/'moment_analysis.json',dict(column_norm_squared=6,column_Gram_quadratic=114,full_T_row_sum=60,off_diagonal_count=59,off_diagonal_sum=54,off_diagonal_square_sum=78,abstract_distributions=distributions,distributions_are_not_factors=True,full_abstract_factor_implies_caps_status='UNKNOWN'))
    ids={(r,d):245881+(r-12)*60+d for r in range(12,36) for d in range(60)}
    by_column=[[q for q in choices if q['column']==d] for d in range(60)]
    channel_records=[];clauses=[];forward=[]
    for q in choices:
        selected=[r for r in q['rows'] if r>=12];need(len(selected)==4,'four unknown incidences per choice')
        for r in selected:
            clauses.append([-q['id'],ids[r,q['column']]]);forward.append([q['id'],r,q['column'],874801+len(clauses)])
    support_by_bit={}
    for (r,d),v in ids.items():
        support=[q['id'] for q in by_column[d] if r in q['rows']];support_by_bit[r,d]=support;clauses.append([-v,*support]);channel_records.append(dict(id=v,row=r,column=d,supporting_choices=support,reverse_clause=874801+len(clauses)))
    need(len(forward)==23040 and len(channel_records)==1440,'channel counts')
    need(sum(not v for v in support_by_bit.values())==480 and all(len(v) in (0,24) for v in support_by_bit.values()),'support census')
    quartet_records=[];omissions=[];sharing=[]
    for d,e in combinations(range(60),2):
        if not set(labels[d])&set(labels[e]):continue
        sharing.append([d,e])
        for i,j in product(range(12),repeat=2):
            coords=[(12+i,d),(12+i,e),(24+j,d),(24+j,e)];empty=next((k for k,pos in enumerate(coords) if not support_by_bit[pos]),None)
            if empty is not None:omissions.append([d,e,i,j,empty]);continue
            clauses.append([-ids[pos] for pos in coords]);quartet_records.append([d,e,i,j,874801+len(clauses)])
    need((len(sharing),len(omissions),len(quartet_records),len(clauses))==(540,56640,21120,45600),'predeclared exact template/extension counts')
    save(out/'preregistration.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,question='Encode the complete normalized fixed-six-prism abstract factor model plus target-necessary column caps with exact incidence channels; automaticity for fullabstract factors remains UNKNOWN.',expected_variables=247320,expected_clauses=920401,resource_limits=dict(seconds=120,solver_calls=0),selection='All5760choices and all540shared-C0-columnpairs; no heuristic ranking.',seed=None,seed_reason='Deterministic complete source catalogs.',status='CANDIDATE_PENDING_INDEPENDENT_REVIEW'))
    # Complete domain channel positives; no full-factor witness is asserted.
    channel_positive=0
    for d,domain in enumerate(by_column):
        for selected in domain:
            actual=set(selected['rows'])
            for r in range(12,36):
                bit=int(r in actual);expected=int(selected['id'] in support_by_bit[r,d]);need(bit==expected,'channel truth for each selected choice/bit');channel_positive+=1
    for bits in product((0,1),repeat=4):need(any(not x for x in bits)==(not all(bits)),'quartic complete truth control')
    overlap_controls=0
    for bits in product((0,1),repeat=3):need((sum(bits)<=2)==(not all(bits)),'per-fibre overlap cap equivalence');overlap_controls+=1
    negative=[]
    def reject(name,call):
        try:call()
        except (ValueError,IndexError,KeyError,TypeError):negative.append(name)
        else:raise AssertionError('bad control accepted '+name)
    bad=[row[:] for row in supports];bad[1][2]=bad[1][1];reject('invalid_partial_support',lambda:partial(model,bad,columns))
    reject('false_channel_bit',lambda:need(int(12 in choices[0]['rows'])==1-int(choices[0]['id'] in support_by_bit[12,0]),'channel corruption'))
    reject('wrong_local_overlap_claim',lambda:need(len(set(supports[0])&set(supports[1]))==2,'literal overlap corruption'))
    rejected_quartets=[c for c in clauses[24480:] if all(-v in {ids[r,d] for d,rs in zip(columns,supports) for r in rs if r>=12} for v in c)]
    need(len(rejected_quartets)==1,'new clauses reject explicit partial overlap3 witness exactly once')
    save(out/'controls.json',dict(channel_selected_choice_bit_cases=channel_positive,quartic_truth_assignments=16,per_fibre_overlap_cases=overlap_controls,local_witness_rejected_by_clauses=rejected_quartets,negative_controls=negative,full_factor_positive=None,full_factor_positive_reason='No complete research factor available; domain controls are explicitly local.'))
    cap()
    suffix=b''.join((' '.join(map(str,c))+' 0\n').encode() for c in clauses)
    suffix_path=out/'suffix.cnfpart';suffix_path.write_bytes(suffix)
    with (NORMAL/'instance.cnf').open('rb') as source,(out/'instance.cnf').open('xb') as dest:
        need(source.readline()==b'p cnf 245880 874801\n','normalized base exact header');dest.write(b'p cnf 247320 920401\n');shutil.copyfileobj(source,dest);dest.write(suffix)
    with (NORMAL/'instance.cnf').open('rb') as source,(out/'instance.cnf').open('rb') as dest:
        source.readline();need(dest.readline()==b'p cnf 247320 920401\n','new header')
        for data in iter(lambda:source.read(1<<20),b''):need(dest.read(len(data))==data,'complete exact base body')
        need(dest.read()==suffix,'exact only suffix')
    raw_model=dict(schema='SIX_PRISM_FIRST_CHOICE_COLUMN_CAP_CHANNEL_EXTENSION_V1',base_normalized_cnf_path=key(NORMAL/'instance.cnf'),base_normalized_cnf_sha256=digest(NORMAL/'instance.cnf'),base_model_path=key(BASE/'model.json'),base_model_sha256=digest(BASE/'model.json'),normalization_gate_path=key(NORMAL_AUDIT),normalization_gate_sha256=digest(NORMAL_AUDIT),variables=247320,clauses=920401,incidence_variables=channel_records,choice_to_bit_clauses=forward,sharing_C0_column_pairs=sharing,quartic_clauses=quartet_records,omitted_templates=omissions,omission_format='[d,e,F1localrow,F2localrow,first_empty_support_position_in_four_coordinates]',suffix_path=key(suffix_path),suffix_sha256=digest(suffix_path),all_96_choices_retained=True,outside_column_caps_encoded=True,mixed_caps_encoded=False,residual_D_encoded=False,target_graph_encoded=False,abstract_Gram_entailment_claimed=False)
    save(out/'model.json',raw_model);save(out/'scope.json',dict(core_adjacency=model['core_adjacency'],target_gram=gram,canonical_C0_columns=model['canonical_C0_columns'],components=model['components'],base_choice_model_sha256=digest(BASE/'model.json'),all_column_caps='For every0<=d<e<60, sum_i F[i,d]*F[i,e]<=2.',normalization_choice_id=1,full_factor_cap_automaticity='UNKNOWN',fixed_six_prism_only=True,assumed_target_automorphism=False,residual_D=False))
    packages=[]
    for p in [out/'instance.cnf',out/'model.json']:
        gz=out/(p.name+'.gz')
        with p.open('rb') as source,gz.open('xb') as dest:
            with gzip.GzipFile(fileobj=dest,mode='wb',mtime=0) as stream:shutil.copyfileobj(source,stream)
        need(gz.stat().st_size<10*1024**2,'public gzip under10MiB');packages.append(dict(raw_path=key(p),raw_sha256=digest(p),raw_bytes=p.stat().st_size,gzip_path=key(gz),gzip_sha256=digest(gz),gzip_bytes=gz.stat().st_size))
    save(out/'artifact_packages.json',dict(packages=packages,recovery='Decompress each named gzip into its exact raw path in a fresh checkout and verify raw byte length/SHA256.'))
    cap();summary=dict(status='CANDIDATE_SIX_PRISM_COLUMN_CAP_EXTENSION_COMPLETE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=bindings,variables=247320,clauses=920401,appended_variables=1440,appended_clauses=45600,choice_to_bit_clauses=23040,bit_to_choices_clauses=1440,forced_zero_bits=480,quartic_templates=77760,omitted_forced_zero_templates=56640,retained_quartics=21120,all_choices_retained=5760,per_column_choices=96,full_abstract_factor_cap_automaticity='UNKNOWN',partial_counterexample_scope='Two individually allowed columns plus entrywise known-Gram upper bounds only.',independent_verification='PENDING',solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start,outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()})
    save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=digest(out/'summary.json'),variables=summary['variables'],clauses=summary['clauses'],elapsed_seconds=summary['elapsed_seconds'])))

if __name__=='__main__':main()
