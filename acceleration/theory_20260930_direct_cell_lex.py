"""Candidate exact lex normalization; no solver, original formulas preserved."""
from pathlib import Path
from itertools import combinations,product
from collections import defaultdict,Counter
from datetime import datetime,timezone
import argparse,copy,gzip,hashlib,importlib.util,json,platform,shutil,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';BASE=B+'direct_cell_count_cnf/';I=B+'independent_review/'
PRODUCER='acceleration/theory_20260930_direct_cell_count_cnf.py'
PINS={BASE+'summary.json':'4153f081634db52c88cf03421cae38b9919d0b6435e7836a8df8b8c5b77d1aa2',PRODUCER:'ea7a07b7adcea4d5faebd174d3b3755ae8ed7e05d2fa844f135db39c7e075fc3','acceleration/theory_20260930_direct_cell_count_cnf_spec.md':'294a25a5734d7283761fba9b10d65c9533c49417b1c12e77486f6d2559787c2a','acceleration/theory_20260930_direct_cell_count_preflight.py':'902bafedf5099fc27727caf17819e50080e514ed9e0b6788fdd5345fb3d5ffdd','acceleration/theory_20260930_direct_cell_count_preflight_spec.md':'b95c02a2ed80fee55260a57dfce0a05e1b26f84bd48aaae4f770da4c28b05368',I+'direct_cell_count_cnf/summary.json':'a7fd5968681257c60a0e82a36b53f40798487d727f2f467dae47918becf84042',I+'direct_cell_semantics/summary.json':'88d6e8134c34b61d44a29e0bc525aebfb260f3f71c78efa72b98a7049275fdc8',B+'hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e','uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
TARGETS={'standalone':(23272,321684),'at_least_seven':(169311,970160)}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,x):
 with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def conjunction(x,y,z):return [[-x,-y,z],[x,-z],[y,-z]]
def comparator(left,right,equalities,top):
 need(len(left)==len(right)==len(equalities)==6 and all(len(x)==3 for x in left+right),'six onehot positions')
 cs=[];prefixes=[];guard=[None,equalities[0]]
 for pos in range(2,6):
  top+=1;x=guard[pos-1];y=equalities[pos-1];clauses=conjunction(x,y,top);prefixes.append(dict(position=pos,id=top,left=x,right=y,clauses=clauses));cs.extend(clauses);guard.append(top)
 inversion=[]
 for pos in range(6):
  for f in range(3):
   for h in range(f):
    c=([-guard[pos]]if pos else[])+[-left[pos][f],-right[pos][h]];cs.append(c);inversion.append(dict(position=pos,left_fibre=f,right_fibre=h,guard=guard[pos],clause=c))
 return top,cs,dict(left_cells=left,right_cells=right,equality_flags=equalities,prefixes=prefixes,inversions=inversion)
def satisfied(cs,v):return all(any(v[abs(x)]==(x>0)for x in c)for c in cs)
def gram(F):return [[sum(x*y for x,y in zip(a,b))for b in F]for a in F]
def fixture_checks(F,C,D):
 n=20;r=60;m=180
 need(len(F)==r and all(len(row)==m and all(type(x)is int and x in(0,1)for x in row)for row in F),'strict fixture factor')
 need(len(D)==m and all(len(row)==m and all(type(x)is int and x in(0,1)for x in row)for row in D),'strict residual')
 need(all(D[d][d]==0 and sum(D[d])==16 for d in range(m))and all(D[d][e]==D[e][d]for d in range(m)for e in range(m)),'residual simple regular')
 G=[[20*int(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(r))+2-int(i//n==j//n)for j in range(r)]for i in range(r)];need(gram(F)==G,'genuine raw Gram')
 need(all(sum(row)==18 for row in F)and all(sum(F[n*h+a][d]for a in range(n))==2 for h in range(3)for d in range(m)),'genuine margins')
 aggregate=[[sum(F[n*h+a][d]for h in range(3))for d in range(m)]for a in range(n)];need(all(v in(0,1)for row in aggregate for v in row),'binary aggregate')
 fm=[sum(x<<d for d,x in enumerate(row))for row in F];dm=[sum(x<<d for d,x in enumerate(row))for row in D];col=[sum(F[i][d]<<i for i in range(r))for d in range(m)];maxcap=0;maxmixed=0
 for d,e in combinations(range(m),2):maxcap=max(maxcap,(col[d]&col[e]).bit_count())
 need(maxcap<=2,'genuine all column caps')
 for i in range(r):
  for d in range(m):
   mixed=F[i][d]+sum(C[i][j]*F[j][d]for j in range(r));maxmixed=max(maxmixed,mixed);need(mixed<=2 and (fm[i]&dm[d]).bit_count()==2-mixed,'literal FD identity')
 for d in range(m):
  for e in range(m):need((dm[d]&dm[e]).bit_count()+(col[d]&col[e]).bit_count()==20*(d==e)-D[d][e]+2,'literal Dsquare identity')
 return dict(aggregate=aggregate,max_column_overlap=maxcap,max_mixed=maxmixed,Gram_entries=r*r,FD_entries=r*m,residual_square_entries=m*m)
def permute_fixture(F,D,sigma):
 need(len(sigma)==180 and all(type(v)is int for v in sigma)and sorted(sigma)==list(range(180)),'column bijection')
 return [[row[sigma[d]]for d in range(180)]for row in F],[[D[sigma[d]][sigma[e]]for e in range(180)]for d in range(180)]
def controls(out):
 left=[[1+3*a+f for f in range(3)]for a in range(6)];right=[[19+3*a+f for f in range(3)]for a in range(6)];eq=list(range(37,43));top,cs,meta=comparator(left,right,eq,42);need(top==46 and len(cs)==30,'comparator actual size');words=[w for w in product(range(3),repeat=6)if all(w.count(f)==2 for f in range(3))];accepted=0;cases=0
 for x,y in product(words,repeat=2):
  values={left[a][f]:x[a]==f for a in range(6)for f in range(3)};values.update({right[a][f]:y[a]==f for a in range(6)for f in range(3)});values.update({eq[a]:x[a]==y[a]for a in range(6)});n=0
  for bits in product((False,True),repeat=4):
   values.update(dict(zip(range(43,47),bits)));n+=satisfied(cs,values);cases+=1
  need(n==int(x<=y),'complete local comparator equivalence/unique extension');accepted+=n
 for x,y,z in product((False,True),repeat=3):need(satisfied(conjunction(1,2,3),{1:x,2:y,3:z})==(z==(x and y)),'exact conjunction truth')
 rejected=[]
 def reject(name,fn):
  try:fn()
  except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
  else:raise ValueError('corruption accepted '+name)
 eqword=words[0];v={left[a][f]:eqword[a]==f for a in range(6)for f in range(3)};v.update({right[a][f]:eqword[a]==f for a in range(6)for f in range(3)});v.update({i:True for i in range(37,47)});need(satisfied(cs,v),'equal words admitted by weak comparator')
 for z in range(43,47):
  vv=dict(v);vv[z]=False;reject('false_prefix_'+str(z),lambda vv=vv:need(satisfied(cs,vv),'wrong exact prefix'))
 # A descending first coordinate becomes falsely accepted when its sole active inversion is dropped.
 x,y=words[-1],words[0];vv={left[a][f]:x[a]==f for a in range(6)for f in range(3)};vv.update({right[a][f]:y[a]==f for a in range(6)for f in range(3)});vv.update({eq[a]:x[a]==y[a]for a in range(6)});vv.update({z:False for z in range(43,47)});need(not satisfied(cs,vv),'descending words rejected');missing=[c for c in cs if c!=[-left[0][x[0]],-right[0][y[0]]]];need(satisfied(missing,vv),'deleted necessary inversion exposed');rejected.append('deleted_inversion_counterfactual_detected')
 fixture=read(ROOT/(B+'srg243_residual_fixture/triangle_blocks.json'));F=fixture['factor60x180'];C=fixture['cubic_core60'];D=fixture['residual180x180'];before=fixture_checks(F,C,D);groups=defaultdict(list)
 for d in range(180):groups[tuple(a for a in range(20)if before['aggregate'][a][d])].append(d)
 need(len(groups)==60 and all(len(s)==6 and len(ds)==3 for s,ds in groups.items()),'genuine triplicate supports');sigma=list(range(180));ordered=[]
 for support,ds in groups.items():
  word=lambda d:tuple(next(h for h in range(3)if F[20*h+a][d])for a in support)
  old=sorted(ds,key=word);need(len({word(d)for d in ds})==3,'cap-implied genuine distinct words')
  for d,e in zip(ds,old):sigma[d]=e
  ordered.append(dict(support=list(support),columns=ds,old_columns_in_sorted_order=old,words=[list(word(d))for d in old]))
 Fn,Dn=permute_fixture(F,D,sigma);after=fixture_checks(Fn,C,Dn);need(after['aggregate']==before['aggregate'],'literal aggregate preservation');inverse=[sigma.index(d)for d in range(180)];Fb,Db=permute_fixture(Fn,Dn,inverse);need(Fb==F and Db==D,'inverse restores literal arrays')
 bad=sigma[:];bad[0]=bad[1];reject('duplicate_column_permutation',lambda:permute_fixture(F,D,bad));bad=sigma[:-1];reject('short_column_permutation',lambda:permute_fixture(F,D,bad))
 bad=sigma[:];a,b=next((a,b)for a,b in combinations(range(180),2)if tuple(before['aggregate'][i][a]for i in range(20))!=tuple(before['aggregate'][i][b]for i in range(20)));bad[a],bad[b]=bad[b],bad[a];badF,badD=permute_fixture(F,D,bad);reject('cross_support_relabelling',lambda:need([[sum(badF[20*h+i][d]for h in range(3))for d in range(180)]for i in range(20)]==before['aggregate'],'support-changing map'))
 badF=copy.deepcopy(Fn);badF[0][0]^=1;reject('changed_factor_bit',lambda:fixture_checks(badF,C,Dn));badD=copy.deepcopy(Dn);badD[0][1]^=1;reject('changed_residual_bit',lambda:fixture_checks(Fn,C,badD))
 save(out/'genuine243_column_transport.json',dict(sigma_new_to_old=sigma,inverse_new_to_old=inverse,groups=ordered,before=before,after=after,original_factor_sha256=hashlib.sha256(json.dumps(F,separators=(',',':')).encode()).hexdigest(),sorted_factor=Fn,conjugated_residual=Dn,scope='Positive control in parameters243,22,1,2 only; not research99.'))
 return dict(balanced_words=90,ordered_word_pairs=8100,complete_auxiliary_cases=cases,allowed_pairs=accepted,exact_AND_truth_cases=8,corruptions_detected=rejected,genuine243=True,fixture_support_groups=60,residual_transport_checked=True,research_factor_available=False)
def derive(base,raw):
 recipe=base['recipe'];groups=list(dict.fromkeys(map(tuple,raw['support_columns'])));gcols=[[d for d,s in enumerate(raw['support_columns'])if tuple(s)==g]for g in groups];need([list(g)for g in groups]==recipe['groups']and gcols==recipe['group_columns']and len(groups)==20,'raw support/column mapping')
 cells={(d,a,h):x for g,d,a,h,x in recipe['cell_variables']};need(len(cells)==1080,'all base cells');caps={tuple(r['columns']):r for r in recipe['column_caps']};top=base['variables'];clauses=[];records=[]
 for g,support in enumerate(groups):
  need(len(support)==6 and list(support)==sorted(support)and len(gcols[g])==3,'sorted raw group')
  for adjacent in range(2):
   d,e=gcols[g][adjacent:adjacent+2];cap=caps[d,e];need(cap['kind']=='within'and cap['common_coordinates']==list(support)and len(cap['equality_flags'])==6,'existing exact equality flags')
   top,cs,meta=comparator([[cells[d,a,h]for h in range(3)]for a in support],[[cells[e,a,h]for h in range(3)]for a in support],cap['equality_flags'],top);records.append(dict(group=g,adjacent=adjacent,columns=[d,e],support=list(support),first_clause=base['clauses']+len(clauses)+1,clause_count=len(cs),**meta));clauses.extend(cs)
 need(top-base['variables']==160 and len(clauses)==1200 and len(records)==40,'actual extension dimensions');return top,clauses,records
def package(path,folder):
 parts=[];offset=0;whole=hashlib.sha256()
 with path.open('rb')as stream:
  while raw:=stream.read(8*1024**2):
   p=folder/f'{path.name}.part{len(parts):04d}.gz'
   with p.open('xb')as dst:
    with gzip.GzipFile(fileobj=dst,filename='',mtime=0,compresslevel=9)as z:z.write(raw)
   recovered=gzip.decompress(p.read_bytes());need(recovered==raw and p.stat().st_size<=10*1024**2,'public transport equality/size');whole.update(recovered);parts.append(dict(index=len(parts),path=key(p),gzip_sha256=sha(p),gzip_bytes=p.stat().st_size,raw_offset=offset,raw_sha256=hashlib.sha256(raw).hexdigest(),raw_bytes=len(raw)));offset+=len(raw)
 need(whole.hexdigest()==sha(path)and offset==path.stat().st_size,'complete package identity');return dict(raw_path=key(path),raw_sha256=sha(path),raw_bytes=offset,parts=parts,recovery='Concatenate decompressed parts in increasing index; validate part and full identities.',all_bytes_recovered=True)
def original_producer():
 need(sha(ROOT/PRODUCER)==PINS[PRODUCER],'producer decoder identity');s=importlib.util.spec_from_file_location('frozen_base_direct_cell',ROOT/PRODUCER);p=importlib.util.module_from_spec(s);s.loader.exec_module(p);return p
def decode(assignment,model_path,scope_path,cnf_path=None):
 model=read(model_path);scope=read(scope_path);need(sha(scope_path)==model['scope_sha256'],'lex scope identity');base=model['base'];cnf=ROOT/model['cnf_path']if cnf_path is None else Path(cnf_path);need(sha(cnf)==model['cnf_sha256'],'lex CNF identity');p=original_producer();values=p.assignment_values(assignment,model['variables']);checked=p.check_cnf(cnf,values,model['variables'],model['clauses'])
 for k in ('model','scope','cnf'):need(sha(ROOT/base[k+'_path'])==base[k+'_sha256'],'base '+k+' identity')
 prior=[i if values[i]else-i for i in range(1,base['variables']+1)];raw=p.decode(prior,ROOT/base['model_path'],ROOT/base['scope_path'],ROOT/base['cnf_path']);F=raw['factor']
 for support,ds in zip(scope['groups'],scope['group_columns']):
  words=[tuple(next(h for h in range(3)if F[12*h+a][d])for a in support)for d in ds];need(words==sorted(words)and len(set(words))==3,'raw strictly ordered group')
 raw.update(lexicographically_ordered=True,actual_clauses_checked=checked,lex_model_sha256=sha(model_path),lex_scope_sha256=sha(scope_path),lex_cnf_sha256=sha(cnf),producer_shared_decoder=PRODUCER,independent_approval=False);return raw
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins=dict(PINS)
 try:
  for p,h in pins.items():need(sha(ROOT/p)==h,'frozen input '+p)
  base_summary=read(ROOT/(BASE+'summary.json'))
  for p,h in base_summary['inputs_sha256'].items():need(sha(ROOT/p)==h,'base dependency identity '+p);pins[p]=h
  for p in [Path(__file__),Path(__file__).with_name('theory_20260930_direct_cell_lex_spec.md'),ROOT/'docs/DERIVATION_20260930_DIRECT_CELL_LEX.md']:pins[key(p)]=sha(p)
  for rec in base_summary['records']:
   for kind in ('cnf','model','scope'):p=rec[kind+'_path'];h=rec[kind+'_sha256'];need(sha(ROOT/p)==h,'base artifact '+p);pins[p]=h
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],python=platform.python_version(),cwd=str(ROOT),inputs_sha256=pins,variants=list(TARGETS),predicted_additions=dict(variables=160,clauses=1200,comparators=40),native_calls=0,independent_approval=False,limit_seconds=120))
  cal=out/'controls';cal.mkdir();save(cal/'summary.json',controls(cal));raw=read(ROOT/(B+'hadamard20_support/six_prism.json'));records=[];packages=[]
  for rec in base_summary['records']:
   variant=rec['variant'];folder=out/variant;folder.mkdir();base=read(ROOT/rec['model_path']);scope=read(ROOT/rec['scope_path']);top,cs,comparators=derive(base,raw);count=base['clauses']+len(cs);need((top,count)==TARGETS[variant],'predeclared exact variant size');suffix=folder/'lex.units_and_clauses.cnfpart'
   with suffix.open('x',encoding='ascii',newline='\n')as f:
    for c in cs:f.write(' '.join(map(str,c))+' 0\n')
   cnf=folder/'instance.cnf';base_body=hashlib.sha256();written_body=hashlib.sha256()
   with cnf.open('xb')as dst:
    dst.write(f'p cnf {top} {count}\n'.encode())
    with (ROOT/rec['cnf_path']).open('rb')as src:
     need(src.readline()==f"p cnf {base['variables']} {base['clauses']}\n".encode(),'base header')
     while chunk:=src.read(1024**2):base_body.update(chunk);dst.write(chunk)
    dst.write(suffix.read_bytes())
   with cnf.open('rb')as actual:
    need(actual.readline()==f'p cnf {top} {count}\n'.encode(),'new header')
    with (ROOT/rec['cnf_path']).open('rb')as original:
     original.readline()
     while chunk:=original.read(1024**2):got=actual.read(len(chunk));need(got==chunk,'literal retained base bytes');written_body.update(got)
    need(actual.read()==suffix.read_bytes(),'literal exact suffix')
   need(base_body.hexdigest()==written_body.hexdigest(),'retained body hash');scope.update(schema='FIXED_LITERAL_DIRECT_CELL_EQUAL_SUPPORT_LEX_SCOPE_V1',column_normalization='Weak lexicographic order on adjacent labelled columns in every equal-support triplicate; strictness follows existing caps.',column_normalization_null_reason=None,normalization_group='S3^20 acting within the fixed equal-support triples only',auxiliary_permutation_claimed=False,base_scope_path=rec['scope_path'],base_scope_sha256=rec['scope_sha256'],candidate_only=True);save(folder/'scope.json',scope)
   ext=dict(schema='DIRECT_CELL_EQUAL_SUPPORT_LEX_EXTENSION_V1',variant=variant,base=rec,base_body_sha256=base_body.hexdigest(),new_variables=160,new_clauses=1200,comparators=comparators,suffix_path=key(suffix),suffix_sha256=sha(suffix),clauses=cs);save(folder/'extension.json',ext)
   model=dict(schema='DIRECT_CELL_EQUAL_SUPPORT_LEX_REFERENCE_MODEL_V1',variant=variant,variables=top,clauses=count,base=rec,scope_path=key(folder/'scope.json'),scope_sha256=sha(folder/'scope.json'),cnf_path=key(cnf),cnf_sha256=sha(cnf),extension_path=key(folder/'extension.json'),extension_sha256=sha(folder/'extension.json'),inputs_sha256=pins,decode_ABI='decode(assignment,model_path,scope_path,cnf_path=None)',independent_approval=False);save(folder/'model.json',model)
   record=dict(variant=variant,variables=top,clauses=count,ASCII_bytes=cnf.stat().st_size,**{kind+'_path':key(folder/file)for kind,file in [('cnf','instance.cnf'),('model','model.json'),('scope','scope.json'),('extension','extension.json')]});record.update({kind+'_sha256':sha(ROOT/record[kind+'_path'])for kind in ('cnf','model','scope','extension')});records.append(record);save(folder/'summary.json',dict(status='CANDIDATE_DIRECT_CELL_LEX_FORMULA_BUILT',**record,inputs_sha256=pins,native_calls=0,independent_approval=False))
   for artifact in folder.iterdir():
    if artifact.is_file()and artifact.stat().st_size>10*1024**2:packages.append(package(artifact,folder))
   need(time.monotonic()-start<120,'bounded build');print(json.dumps(record),flush=True)
  save(out/'artifact_packages.json',dict(schema='DIRECT_CELL_LEX_GZIP_TRANSPORT_V1',records=packages,raw_originals_preserved=True,independent_transport_approval=False));summary=dict(status='CANDIDATE_DIRECT_CELL_LEX_FORMULAS_BUILT',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},records=records,native_calls=0,independent_approval=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start,limitations=['Candidate semantic normalization and construction awaiting separate reviewer.','Literal fixed L/core only; no target automorphism, new support coverage or residual D.','All original domains/caps retained; at-least-seven restriction unchanged.','Original producer decoder is reused only by the optional producer decode ABI.']);save(out/'summary.json',summary);print(json.dumps(dict(summary_sha256=sha(out/'summary.json'),status=summary['status'])))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
