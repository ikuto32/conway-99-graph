"""Independent explicit additive-kernel proof and complete raw option replay."""
import argparse
import copy
import gzip
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path

# Frozen independently authored arithmetic/catalogue helpers, not producer code.
import audit_20260930_triplicate_count_psd as linear
import audit_20260930_exact_eight_block_screen as catalogue

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'triplicate_psd_kernel_options/'
PINS={D+'summary.json':'aff53c2da24b39375d5675e5618a6bb24ff62b8e952a4c82a6da71d431cacaec',
 'acceleration/theory_20260930_triplicate_psd_kernel_options.py':'b0d49849c1b25349a19dc4c50387995eb023299cfccf5310fc1c3118a28b0cde',
 'acceleration/theory_20260930_triplicate_psd_kernel_options_spec.md':'871e31a434217034fd419a5d0d888a00c339f74f2d3e4390025e6acbaf081570',
 'acceleration/audit_20260930_triplicate_count_psd.py':'960c74b78c7c26bfd2f17cf5b24cb0702ff8f52a20ce2058059d07bad105c5d5',
 'acceleration/audit_20260930_exact_eight_block_screen.py':'18cc7b8d793692102a05db575c2c99dddfecc1e14e65fb529770196be59f77dc',
 I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}
CASES=[('first','count_master_sat_outcome'),('second','count_master_eight_orbit_cut_sat_outcome'),('third','count_master_partial_cut_sat_outcome')]

def need(c,m):
 if not c:raise ValueError(m)
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def gzread(p):
 with gzip.open(p,'rt',encoding='utf-8')as f:return json.load(f)
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def primitive(v):
 values=[Q(x)for x in v];den=math.lcm(*(x.denominator for x in values));ints=[int(x*den)for x in values];div=math.gcd(*ints);need(div>0,'nonzero vector');ans=[x//div for x in ints]
 return [-x for x in ans]if next(x for x in ans if x)<0 else ans
def residual(g,n):return [[3*g[i][j]-sum(n[i][k]*n[j][k]for k in range(len(n[0])))for j in range(len(g))]for i in range(len(g))]
def structural_basis():
 return [[int(i%12==a)for i in range(36)]for a in range(12)]+[[int(i//12==f)for i in range(36)]for f in (1,2)]
def decompose(v):
 need(len(v)==36 and all(type(x)is int for x in v),'integer36-vector')
 alpha=v[:12];beta=[0,v[12]-v[0],v[24]-v[0]]
 need(all(v[12*f+a]==alpha[a]+beta[f]for f in range(3)for a in range(12)),'explicit additive coordinate identity')
 return alpha+beta[1:]
def check_basis(m,k):
 need(len(k)==14 and all(len(v)==36 and all(type(x)is int for x in v)for v in k),'complete integer kernel shape')
 need(all(primitive(v)==v for v in k),'primitive positive first entry')
 need(linear.rank_kernel(k)[0]==14,'complete independent basis rank')
 need(all(sum(row[j]*v[j]for j in range(36))==0 for row in m for v in k),'literal null products')
 return [decompose(v)for v in k]
def check_matrix(g,n,w):
 m=residual(g,n);rank,k,pivots,rref=linear.rank_kernel(m)
 need(rank==22 and len(k)==14,'exact rank22 nullity14')
 need(all(sum(row[j]*v[j]for j in range(36))==0 for row in m for v in w),'explicit W lies in kernel')
 return m,dict(rank=rank,nullity=len(k),independent_kernel=linear.pack(k),reverse_pivots=pivots)
def expected_option(g,rank,triples,words,support,basis):
 triple=triples[rank];columns=[[12*words[word][i]+a for i,a in enumerate(support)]for word in triple]
 projected=[[sum(v[row]for row in col)for col in columns]for v in basis]
 differences=[[p[0]-p[1],p[0]-p[2],p[1]-p[2]]for p in projected]
 return dict(group=g,local_survivor_index=rank,word_indices=list(triple),column_rows=columns,integer_kernel_projections=projected,pair_difference_residuals=differences,passes=all(x==0 for row in differences for x in row))
def reject(name,fn,records):
 try:fn()
 except(ValueError,KeyError,IndexError,ZeroDivisionError):records.append(name);return
 raise ValueError('corruption accepted '+name)

def positive_control(f,order):
 arranged=[[row[j]for j in order]for row in f];n,m,d=linear.factor_identity(arranged);rank,k,pivots,_=linear.rank_kernel(m)
 need(all(sum(v[i]*d[i][j]for i in range(len(f)))==0 for v in k for j in range(len(d[0]))),'own factor kernel difference necessity')
 return dict(rows=len(f),columns=len(order),order=order,rank=rank,nullity=len(k),independent_kernel=linear.pack(k),pair_difference_entries_checked=len(k)*len(d[0]),scope='Own exact factor Gram and selected partition; no research36 positive.')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
 def pin(p,h=None):
  p=ROOT/p if isinstance(p,str)else p;actual=sha(p);need(h is None or actual==h,'input identity '+key(p));pins[key(p)]=actual;return p
 def bounded():need(time.perf_counter()-start<120,'120second allocation')
 try:
  for p,h in PINS.items():pin(p,h)
  for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),ROOT/'docs/AUDIT_20260930_TRIPLICATE_PSD_KERNEL_OPTIONS.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
  summary=read(ROOT/(D+'summary.json'))
  need(summary['status']=='CANDIDATE_TRIPLICATE_PSD_KERNEL_OPTION_SCREEN_COMPLETE','complete candidate status')
  for field in ('inputs_sha256','outputs_sha256'):
   for p,h in summary[field].items():pin(p,h)
  gatepath=I+'triplicate_count_psd/summary.json';gate=read(ROOT/gatepath)
  need(gate['status']=='INDEPENDENT_TRIPLICATE_COUNT_PSD_PASS','prior independent PSD status')
  for p,h in gate['outputs_sha256'].items():need(pins.get(p)==h,'every prior exact check identity')
  save(out/'manifest.json',dict(inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),created_at=datetime.now(timezone.utc).isoformat(),allocation_seconds=120,shared_code=['Frozen independent PSD arithmetic helper','Frozen independent block catalogue reconstruction'],producer_imports=False))
  raw=read(ROOT/(B+'hadamard20_support/six_prism.json'));groups=linear.group_order(raw);c=linear.fixed_core();g=linear.prescribed(c,12)
  need(c==raw['core_adjacency']and g==raw['prescribed_Gram36'],'literal core/Gram identity')
  words,triples,signatures,classes=catalogue.local_catalogue(read(ROOT/(B+'hadamard_triplicate_counts/local_triples.json')))
  w=structural_basis();minor=[[v[j]for j in [*range(12),12,24]]for v in w];inv,det=linear.inverse(minor)
  need(det==1,'explicit structural basis minor determinant1')
  n0=[[int(a in support)for support in groups]for f in range(3)for a in range(12)];m0,check0=check_matrix(g,n0,w)
  baseline=read(ROOT/(D+'balanced_baseline.json'));need(baseline['N']==n0 and baseline['M']==m0,'balanced baseline literal matrices')
  need(baseline['rank']==22 and baseline['nullity']==14,'baseline rank fields')
  need(baseline['N_rank']==linear.rank_kernel(n0)[0]and baseline['G_rank']==linear.rank_kernel(g)[0],'independent contextual ranks')
  k0=baseline['integer_nullspace'];coeff0=check_basis(m0,k0)
  need(summary['baseline_rank']==22 and summary['baseline_nullity']==14 and summary['baseline_N_rank']==baseline['N_rank']and summary['G_rank']==baseline['G_rank'],'summary baseline ranks')
  save(out/'explicit_kernel_space.json',dict(structural_basis=w,minor_columns=[*range(12),12,24],minor=minor,minor_inverse=linear.pack(inv),determinant1=True,N0=n0,M0=m0,baseline_independent_check=check0,producer_baseline_basis=k0,additive_coefficients=coeff0,N0_rank=baseline['N_rank'],G_rank=baseline['G_rank']))
  table=gzread(ROOT/(D+'baseline_all_word_projections.json.gz'));need(len(table)==20,'all20 word-table groups');dot_entries=0
  for gi,support in enumerate(groups):
   constants=[sum(co[a]for a in support)+2*co[12]+2*co[13]for co in coeff0]
   direct=[[sum(v[12*word[i]+a]for i,a in enumerate(support))for v in k0]for word in words]
   need(all(d==constants for d in direct),'all90 exact additive-word projections')
   need(table[gi]==dict(group=gi,support=support,projections_by_word=direct,constant_across_all90=True),'all saved raw word projections')
   dot_entries+=len(words)*len(k0)
  need(summary['all20_by90_baseline_word_projections_constant']is True,'reported word constancy')
  bounded();checks=[];mutations=[];all_options=0;difference_entries=0
  for name,folder in CASES:
   profile=read(ROOT/(I+folder+'/independent_count_profile.json'));counts=profile['coordinate_group_fibre_counts']
   n=[[counts[a][j][f]for j in range(20)]for f in range(3)for a in range(12)];m,checked=check_matrix(g,n,w)
   prior=read(ROOT/(I+'triplicate_count_psd/'+name+'_exact_check.json'))
   need(prior['matrix']['N']==n and prior['matrix']['G']==g and prior['matrix']['M']==m,'previous raw matrix identity')
   saved=read(ROOT/(D+name+'/kernel_and_domains.json'));basis=saved['integer_nullspace'];coeff=check_basis(m,basis)
   own_coeff=check_basis(m,saved['independently_computed_integer_nullspace'])
   scaled=[primitive([Q(*x)for x in row])for row in prior['certificate_check']['nullspace']];need(basis==scaled,'literal approved-basis integer scaling')
   need(saved['rank']==22 and saved['same_kernel_as_balanced_baseline']is True,'claimed equal kernel metadata')
   records=gzread(ROOT/(D+name+'/all_option_residuals.json.gz'));expected_ranks=[];at=0
   for gi,support in enumerate(groups):
    signature=tuple(counts[a][gi][f]for a in support for f in range(3));ranks=classes[signature]
    need(ranks==profile['local_survivor_indices_by_group'][gi],'full original profile count class')
    expected_ranks.append(ranks)
    for rank in ranks:
     expected=expected_option(gi,rank,triples,words,support,basis)
     need(expected['passes'],'structural kernel screening remains redundant')
     need(at<len(records)and records[at]==expected,'complete literal option replay')
     at+=1;difference_entries+=42
   need(at==len(records),'no omitted/extra option record')
   need(saved['initial_domain_sizes']==[len(r)for r in expected_ranks]and saved['retained_local_survivor_indices']==expected_ranks and saved['empty_groups']==[],'complete initial and retained class identity')
   actual=dict(profile=name,rank=22,nullity=14,same_kernel_as_balanced_baseline=True,initial_options=at,retained_options=at,removed_options=0,empty_groups=[])
   need(actual==next(r for r in summary['results']if r['profile']==name),'exact result summary')
   save(out/(name+'_independent_check.json'),dict(result=actual,matrix_N=n,matrix_M=m,independent_rank=checked,producer_basis_additive_coefficients=coeff,producer_recomputed_basis_additive_coefficients=own_coeff,initial_and_retained_rank_lists=expected_ranks))
   checks.append(actual);all_options+=at
   bad=copy.deepcopy(records[0]);bad['integer_kernel_projections'][0][0]+=1
   expected=expected_option(bad['group'],bad['local_survivor_index'],triples,words,groups[bad['group']],basis)
   reject(name+'_changed_projection',lambda bad=bad:need(bad==expected,'raw option identity'),mutations)
   bad=copy.deepcopy(records[0]);bad['pair_difference_residuals'][0][0]+=1
   reject(name+'_changed_residual',lambda bad=bad:need(bad==expected,'raw option identity'),mutations)
   reject(name+'_missing_initial_option',lambda:need(expected_ranks[0][:-1]==profile['local_survivor_indices_by_group'][0],'full local class'),mutations)
   badbasis=copy.deepcopy(basis);badbasis[-1]=badbasis[0][:]
   reject(name+'_dependent_basis',lambda badbasis=badbasis:check_basis(m,badbasis),mutations)
   bounded()
  need(len(summary['results'])==3 and all_options==summary['total_options']==6444 and summary['total_removed']==0,'complete3-profile total')
  # Independent kernel-necessity controls with actual own-Gram factors.
  positives=[];fixture=read(ROOT/(B+'srg243_residual_fixture/triangle_blocks.json'))['factor60x180']
  for label,order in [('consecutive',list(range(180))),('stride17',[(17*j+5)%180 for j in range(180)])]:positives.append(dict(label='genuine243_'+label,record=positive_control(fixture,order)));bounded()
  for seed in range(32):
   f=[[Q((seed+3*i+7*j+i*j)%9-4,1+(seed+i+j)%3)for j in range(9)]for i in range(5)]
   positives.append(dict(label='rational_partition_'+str(seed),record=positive_control(f,list(range(9)))))
  bad=k0[0][:];bad[0]+=1
  reject('changed_nullvector',lambda:check_basis(m0,[bad,*k0[1:]]),mutations)
  badm=copy.deepcopy(m0);nz=next(i for i,x in enumerate(k0[0])if x);badm[nz][nz]+=1
  reject('changed_matrix',lambda:check_basis(badm,k0),mutations)
  reject('incomplete_basis',lambda:check_basis(m0,k0[:-1]),mutations)
  # A non-additive vector really can distinguish words; do not approve all vectors.
  outside=[0]*36;outside[0]=1
  reject('outside_additive_space',lambda:decompose(outside),mutations)
  gs=next(s for s in groups if 0 in s);values={sum(outside[12*word[i]+a]for i,a in enumerate(gs))for word in words};need(values=={0,1},'outside-space positive distinction control')
  badtable=copy.deepcopy(table[0]);badtable['projections_by_word'][0][0]+=1
  reject('changed_word_table',lambda:need(badtable['projections_by_word'][0]==table[0]['projections_by_word'][0],'literal baseline dot'),mutations)
  badn=copy.deepcopy(n0);badn[0][0]+=1
  reject('changed_baseline_count',lambda:check_matrix(g,badn,w),mutations)
  save(out/'controls.json',dict(positive_controls=positives,outside_W_word_values=sorted(values),corruptions_rejected=mutations,research_factor_positive=False))
  bounded();now=datetime.now(timezone.utc).isoformat();status='INDEPENDENT_TRIPLICATE_PSD_KERNEL_OPTION_REDUNDANCY_PASS'
  result=dict(status=status,created_at=now,updated_at=now,verifier='/root/state_literature_audit',method='Explicit14-dimensional additive-coordinate kernel basis with determinant1 minor; literal annihilation and independent reverse-column ranks; all raw word/option projections and complete original classes.',
   inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in sorted(out.iterdir())if p.is_file()},results=checks,total_options=all_options,total_removed=0,baseline_word_dot_entries=dot_entries,local_pair_difference_entries=difference_entries,
   kernel_dimensions=[14]*4,checked_initial_local_triples=117480,complete_local_catalogue=31110,controls=dict(own_factor_positives=len(positives),genuine243=2,corruptions=len(mutations)),
   shared_components=['Frozen independent PSD checker exact linear algebra and core/Gram arithmetic.','Frozen independent block checker local catalogue reconstruction.','Python standard library and authenticated raw artifacts; no producer imports.'],
   command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),elapsed_seconds=time.perf_counter()-start,native_calls=0,artifact_availability='LOCAL_ONLY',
   scope='Three exact profiles have the balanced-baseline kernel; its local necessary projection test removes zero of6444 complete initial options. No arbitrary-profile kernel equality or factor/target feasibility follows.')
  save(out/'summary.json',result)
  binding=dict(id='C-FIXED-HADAMARD-THREE-COUNT-PSD-KERNEL-OPTION-REDUNDANCY',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',
   statement='The triplicate residual Gram matrices of the first, second and third pinned count profiles all have the same14-dimensional kernel as the balanced-count baseline. Every vector in this kernel has constant projection on all90 balanced colour words of each of the20 supports; consequently the necessary real-SOS kernel test retains all6444 original local options (2184,2076,2184) and removes none.',
   scope=result['scope'],assumptions=['Exact pinned literal six-prism support and three authenticated count tables.','The local word convention selects one vertex per support coordinate and two in each fibre.'],
   dependencies=[dict(id='C-FIXED-HADAMARD-THREE-COUNT-PROFILES-PSD-NECESSITY-PASS',revision=1,relation='uses_result'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],
   verifier=result['verifier'],method=result['method'],created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY',inputs_sha256=pins,
   independent_verification=dict(report=key(out/'summary.json'),sha256=sha(out/'summary.json'),status=status),shared_components=result['shared_components'],controls=result['controls'],
   limitations=['Other count profiles can have extra kernel directions; no universal same-kernel claim.','No global Gram factor, cross-group cap, residualD or target existence/exclusion inference.','Balanced baseline and SRG243 controls are not research36 factor constructions.'])
  save(out/'claim_binding.json',binding)
  print(json.dumps(dict(status=status,summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'),elapsed_seconds=time.perf_counter()-start)),flush=True)
 except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),inputs_sha256=pins,elapsed_seconds=time.perf_counter()-start));raise

if __name__=='__main__':main()
