"""Candidate raw five-incidence scalar obstruction, no solver or shared imports."""
from pathlib import Path
from itertools import product
from collections import defaultdict
from datetime import datetime,timezone
import argparse,copy,hashlib,json,platform,sys,time
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/'
RAW=B+'hadamard20_support/six_prism.json';PROFILE=I+'count_master_eight_orbit_cut_sat_outcome/independent_count_profile.json';MASTER=B+'hadamard_count_master_cnf/model.json';LOCAL=B+'hadamard_triplicate_counts/local_triples.json';ASSIGNMENT=B+'count_master_eight_orbit_cut_native_pilot/main/parsed_model.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',PROFILE:'7a60f7ec211da1e41ee286e0320ef94141b857ed69eb7dfa41e3913527dfe0a0',MASTER:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',ASSIGNMENT:'40174793158d22cb17a0fff711102e9f3053ab04c9b23ba632d94c2976727189',I+'count_master_eight_orbit_cut_sat_outcome/summary.json':'7c80d3e4daef0f259bd354e6e6b28188b660edaaf17c7a20f9c54cfb3abc4c3c',I+'hadamard_count_master_cnf_v2/summary.json':'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',I+'hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',I+'second_count_scalar_obstruction/summary.json':'b10f6ae68f711f299ea34b67613f85c84f2904e64612019696ac7819f40af92c','uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db','pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
PREDECLARED=[(1,11,1,0),(5,9,2,0),(8,9,2,1),(18,11,1,0),(19,9,2,0)]
def need(ok,msg):
 if not ok:raise ValueError(msg)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
 with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def read(p):return json.loads((ROOT/p).read_bytes())
def clause_value(clause,truth):return any(truth[abs(lit)]==(lit>0)for lit in clause)
def overlap(a,b):return sum(x*y for x,y in zip(a,b))
def strip_controls():
 bits=list(product((0,1),repeat=3));rows=[];bycounts=defaultdict(list)
 for a,b in product(bits,repeat=2):
  actual=overlap(a,b);u,v=sum(a),sum(b);need(actual<=min(u,v),'binary intersection upper bound');rows.append(dict(left=list(a),right=list(b),u=u,v=v,overlap=actual));bycounts[u,v].append((actual,a,b))
 maxima=[]
 for (u,v),vals in sorted(bycounts.items()):
  best=max(vals);need(best[0]==min(u,v),'all16 exact universal maxima');maxima.append(dict(counts=[u,v],maximum=best[0],attaining_left=list(best[1]),attaining_right=list(best[2])))
 # Restrictions concern right count in groups1/18, left count in groups5/8/19.
 def constrained(strips,omit=None):
  return all(i==omit or sum(strips[i][0 if a==9 else 1])<=bound for i,(_,a,_,bound)in enumerate(PREDECLARED))
 base=[([0,0,0],[0,0,0])for _ in range(5)];base[2]=([1,0,0],[1,0,0]);need(constrained(base)and sum(overlap(*x)for x in base)==1,'sharp bound1 positive')
 drops=[]
 for omitted in range(5):
  strips=copy.deepcopy(base)
  if omitted==2:strips[2]=([1,1,0],[1,1,0])
  else:strips[omitted]=([1,0,0],[1,0,0])
  need(constrained(strips,omitted)and not constrained(strips)and sum(overlap(*x)for x in strips)==2,'omitted bound local counterexample');drops.append(dict(omitted_index=omitted,strips=strips,total_overlap=2,scope='Local strips only; not full factor.'))
 return dict(binary_pair_cases=rows,exact_count_pair_maxima=maxima,sharp_bound_one_strips=base,removed_bound_counterexamples=drops)
def verify_recipe(terms,exact_clause,escape_clause,channels,counts,restrictions=PREDECLARED):
 need([(x['group'],x['coordinate'],x['fibre'],x['upper_bound'])for x in terms]==restrictions,'exact fixed restriction identities')
 en=[];ex=[]
 for t in terms:
  channel=channels[t['coordinate'],t['group']];val=counts[t['coordinate']][t['group']];need(t['channel_values']==channel['values']and t['channel_variables']==channel['variables'],'all exact channel alternatives');need(t['current_count_vector']==val,'actual current vector');selected=channel['variables'][channel['values'].index(val)];need(t['current_selected_variable']==selected,'literal selected variable')
  expected=[x for x,v in zip(channel['variables'],channel['values'])if v[t['fibre']]>t['upper_bound']];need(t['escaping_variables']==expected,'precise threshold predicate');en.append(-selected);ex.extend(expected)
 need(exact_clause==en and escape_clause==ex,'literal signs/order/population');need(sum(t['upper_bound']for t in terms)==1,'partial upper sum')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins=dict(PINS)
 try:
  for p,h in pins.items():need(sha(ROOT/p)==h,'frozen input '+p)
  for p in [Path(__file__),Path(__file__).with_name('theory_20260930_second_count_partial_cut_spec.md'),ROOT/'docs/DERIVATION_20260930_SECOND_COUNT_PARTIAL_CUT.md']:pins[key(p)]=sha(p)
  save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],python=platform.python_version(),cwd=str(ROOT),inputs_sha256=pins,selection=PREDECLARED,additional_instances=[list(x)for x in product(range(3),repeat=2)if x[0]!=x[1]],additional_instance_basis='Direct separate target-entry bounds, no symmetry premise.',limits_seconds=60,native_calls=0,independent_approval=False))
  local_controls=strip_controls();raw=read(RAW);profile=read(PROFILE);master=read(MASTER);local=read(LOCAL);groups=list(dict.fromkeys(map(tuple,raw['support_columns'])));counts=profile['coordinate_group_fibre_counts'];C=raw['core_adjacency'];G=raw['prescribed_Gram36'];a,b,f,h=9,11,2,1;i,j=12*f+a,12*h+b;target=12*(i==j)-C[i][j]-sum(C[i][k]*C[k][j]for k in range(36))+2-int(i//12==j//12);need(target==G[i][j]==2,'raw prescribed Gram2')
  gs=[g for g,s in enumerate(groups)if a in s and b in s];columns=[d for d,s in enumerate(raw['support_columns'])if a in s and b in s];need(gs==[1,5,8,18,19]and len(columns)==15,'complete5group15column contribution set');need(all([d for d,s in enumerate(raw['support_columns'])if tuple(s)==groups[g]]==[g,g+20,g+40]for g in gs),'three exact labelled columns per group')
  pairs=[(counts[a][g][f],counts[b][g][h])for g in gs];need(pairs==[(2,0),(0,2),(1,1),(2,0),(0,2)],'raw count pairs');universal=[min(u,v)for u,v in pairs];need(universal==[0,0,1,0,0]and sum(universal)<target,'universal current scalar bound')
  diagnostic=[];words=local['words'];triples=local['survivors']
  for g in gs:
   support=groups[g];pa,pb=support.index(a),support.index(b);ranks=[];vals=[]
   for rank,triple in enumerate(triples):
    actual=[[sum(words[w][pos]==fibre for w in triple)for fibre in range(3)]for pos in range(6)]
    if actual!=[counts[c][g]for c in support]:continue
    ranks.append(rank);vals.append(sum(words[w][pa]==f and words[w][pb]==h for w in triple))
   need(ranks==profile['local_survivor_indices_by_group'][g]and ranks,'diagnostic full original signature domain');diagnostic.append(dict(group=g,local_survivor_indices=ranks,contributions=vals,minimum=min(vals),maximum=max(vals),universal_maximum=min(counts[a][g][f],counts[b][g][h])))
  need([x['maximum']for x in diagnostic]==universal,'catalogue diagnostic maxima agree')
  channels={(x['coordinate'],x['group']):x for x in master['count_channels']};terms=[]
  for g,c,fibre,bound in PREDECLARED:
   ch=channels[c,g];val=counts[c][g];selected=ch['variables'][ch['values'].index(val)];terms.append(dict(group=g,coordinate=c,fibre=fibre,upper_bound=bound,current_count_vector=val,current_selected_variable=selected,channel_values=ch['values'],channel_variables=ch['variables'],escaping_variables=[x for x,v in zip(ch['variables'],ch['values'])if v[fibre]>bound]))
  exact=[-t['current_selected_variable']for t in terms];escape=[x for t in terms for x in t['escaping_variables']];verify_recipe(terms,exact,escape,channels,counts);need(len(exact)==5 and len(escape)==25,'actual cut lengths')
  rejected=[]
  def reject(name,fn):
   try:fn()
   except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
   else:raise ValueError('corruption accepted '+name)
  for name in ['group','coordinate','fibre','upper_bound','current_selected_variable']:
   bad=copy.deepcopy(terms);bad[0][name]+=1;reject('changed_'+name,lambda bad=bad:verify_recipe(bad,exact,escape,channels,counts))
  reject('negated_exact_literal',lambda:verify_recipe(terms,[-exact[0],*exact[1:]],escape,channels,counts));reject('removed_escape_literal',lambda:verify_recipe(terms,exact,escape[:-1],channels,counts));reject('changed_target',lambda:need(sum(universal)<1,'bound1 does not contradict target1'));reject('omitted_contributor',lambda:need(gs[:-1]==[g for g,s in enumerate(groups)if a in s and b in s],'incomplete coverage'))
  # Entire finite product of these five existing channel domains, not a global CSP census.
  tests=forbidden=0;selected_only=0;truth_examples={}
  for choice in product(*[range(len(t['channel_values']))for t in terms]):
   truth={var:k==q for t,q in zip(terms,choice)for k,var in enumerate(t['channel_variables'])};selected_vals=[t['channel_values'][q]for t,q in zip(terms,choice)];violates=any(v[t['fibre']]>t['upper_bound']for t,v in zip(terms,selected_vals));es=clause_value(escape,truth);ex=clause_value(exact,truth);need(es==violates,'full local channel escape equivalence');need(not es or ex,'broader cut implies exact cut');tests+=1;forbidden+=not es;selected_only+=not ex
   if not es:need(sum(v[t['fibre']]for t,v in zip(terms,selected_vals))<=1,'all forbidden choices universal sum bound')
   truth_examples.setdefault(str(es),dict(indices=list(choice),values=selected_vals,escape_clause=es,exact_clause=ex))
  need((tests,forbidden,selected_only)==(49000,640,1),'complete truth-table census')
  instances=[];total_instance_cases=0
  for f0,h0 in product(range(3),repeat=2):
   if f0==h0:continue
   restrictions=[(1,11,h0,0),(5,9,f0,0),(8,9,f0,1),(18,11,h0,0),(19,9,f0,0)];ii,jj=12*f0+a,12*h0+b;literal_target=12*(ii==jj)-C[ii][jj]-sum(C[ii][k]*C[k][jj]for k in range(36))+2-int(ii//12==jj//12);need(literal_target==G[ii][jj]==2,'each literal ordered-fibre target')
   ts=[]
   for g,c,fibre,bound in restrictions:
    ch=channels[c,g];val=counts[c][g];ts.append(dict(group=g,coordinate=c,fibre=fibre,upper_bound=bound,current_count_vector=val,current_selected_variable=ch['variables'][ch['values'].index(val)],channel_values=ch['values'],channel_variables=ch['variables'],escaping_variables=[x for x,v in zip(ch['variables'],ch['values'])if v[fibre]>bound]))
   esc=[x for t in ts for x in t['escaping_variables']];verify_recipe(ts,[-t['current_selected_variable']for t in ts],esc,channels,counts,restrictions);checked=removed=0
   for choice in product(*[range(len(t['channel_values']))for t in ts]):
    truth0={var:k==q for t,q in zip(ts,choice)for k,var in enumerate(t['channel_variables'])};vv=[t['channel_values'][q]for t,q in zip(ts,choice)];violates=any(v[t['fibre']]>t['upper_bound']for t,v in zip(ts,vv));need(clause_value(esc,truth0)==violates,'all6 direct local clause equivalences');checked+=1;removed+=not violates
    if not violates:need(sum(v[t['fibre']]for t,v in zip(ts,vv))<=1,'every restricted region universal upper1')
   need(checked==49000 and removed==640 and len(esc)==25,'complete ordered-fibre case');total_instance_cases+=checked;instances.append(dict(coordinates=[a,b],fibres=[f0,h0],target=literal_target,groups=gs,partial_upper=1,partial_restrictions=ts,clause=esc,channel_truth_cases=checked,forbidden_channel_choices=removed,symmetry_premise_used=False))
  need(len(instances)==6 and next(r['clause']for r in instances if r['fibres']==[f,h])==escape,'original bound included literally')
  assignment=read(ASSIGNMENT)['assignment'];need(len(assignment)==155939 and all(type(x)is int and x for x in assignment)and sorted(map(abs,assignment))==list(range(1,155940)),'authenticated complete original assignment');truth={abs(x):x>0 for x in assignment}
  for t in terms:need([x for x in t['channel_variables']if truth[x]]==[t['current_selected_variable']],'actual saved channel choice')
  need(not clause_value(exact,truth)and not clause_value(escape,truth),'both cuts falsified by actual count-CSP witness')
  for rec in instances:rec['current_witness_satisfies_clause']=clause_value(rec['clause'],truth)
  need([r['fibres']for r in instances if not r['current_witness_satisfies_clause']]==[[2,1]],'current witness violates original instance only')
  for filename,c in [('exact_channel_nogood.cnfpart',exact),('scalar_bound_escape.cnfpart',escape)]:
   with (out/filename).open('x',encoding='ascii',newline='\n')as stream:stream.write(' '.join(map(str,c))+' 0\n')
  with (out/'universal_six_bound_cuts.cnfpart').open('x',encoding='ascii',newline='\n')as stream:
   for rec in instances:stream.write(' '.join(map(str,rec['clause']))+' 0\n')
  save(out/'ordered_fibre_instances.json',dict(records=instances,complete_instance_population='The six ordered pairs of distinct fibres for the single coordinate pair9,11 and the same five bound-template groups.',channel_truth_cases=total_instance_cases,preferred_extension_path=key(out/'universal_six_bound_cuts.cnfpart'),preferred_extension_sha256=sha(out/'universal_six_bound_cuts.cnfpart')))
  save(out/'local_catalogue_diagnostic.json',dict(records=diagnostic,used_as_partial_bound_premise=False,scope='Only the five original full group signatures; this diagnostic does not generalize the catalogue.'))
  save(out/'controls.json',dict(**local_controls,malformed_controls_rejected=rejected,channel_product_cases=tests,channel_product_violating_partial_region=forbidden,exact_five_choice_region=selected_only,all_six_instance_channel_cases=total_instance_cases,examples=truth_examples,original_SAT_assignment_falsifies_both=True,all_factor_positive_available=False))
  certificate=dict(schema='SECOND_COUNT_FIVE_INCIDENCE_UNIVERSAL_BOUND_V1',coordinates=[a,b],fibres=[f,h],target=target,cooccurring_groups=gs,cooccurring_columns=columns,raw_full_profile_count_pairs=[list(x)for x in pairs],simple_upper_bounds=universal,total_upper=1,partial_restrictions=terms,exact_channel_nogood=exact,scalar_bound_escape_clause=escape,proof='Every contributing group overlap is at most either incident row count. The chosen count restrictions bound their sum by1; all other groups contribute0 from raw support. Target2 is impossible.',uses_local_within_caps=False,uses_cross_group_caps=False,uses_residual_D=False,uses_global_countmaster_feasibility=False,clauses_require_channel_onehot_semantics=True,claim_status='CANDIDATE');save(out/'certificate.json',certificate)
  save(out/'model.json',dict(schema='COUNT_MASTER_PARTIAL_SCALAR_CLAUSE_RECIPE_V1',base_model=MASTER,base_model_sha256=PINS[MASTER],existing_variable_count=155939,new_variables=0,preferred_extension=dict(clauses=[r['clause']for r in instances],path=key(out/'universal_six_bound_cuts.cnfpart'),sha256=sha(out/'universal_six_bound_cuts.cnfpart')),comparison_clauses=[dict(name='exact_channel_nogood',literals=exact,path=key(out/'exact_channel_nogood.cnfpart'),sha256=sha(out/'exact_channel_nogood.cnfpart')),dict(name='scalar_bound_escape',literals=escape,path=key(out/'scalar_bound_escape.cnfpart'),sha256=sha(out/'scalar_bound_escape.cnfpart'))],relationship='The positive escape clause for fibres2,1 implies the negative exact-channel clause under the existing exactly-one channels; the negative clause is comparison-only and redundant. The six-clause preferred extension includes the original positive clause once.',appended_to_existing_formula=False,full_factor=False,target_graph=False,inputs_sha256=pins))
  need(time.monotonic()-start<60,'bounded60second producer');summary=dict(status='CANDIDATE_SECOND_COUNT_PARTIAL_SCALAR_CUTS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},profile_sha256=profile['profile_sha256'],cooccurring_groups=gs,simple_bound=1,target=2,catalogue_maxima=universal,exact_channel_clause=exact,escape_clause=escape,comparison_clause_lengths=[5,25],preferred_extension_clause_lengths=[len(r['clause'])for r in instances],channel_truth_cases=tests,all_six_instance_channel_cases=total_instance_cases,forbidden_local_channel_choices=forbidden,native_calls=0,independent_approval=False,elapsed_seconds=time.monotonic()-start,scope='Six direct ordered-fibre bounds on the same five literal coordinate/group incidences; valid for binary fixed-support prescribed-Gram completions, not entailed by the weaker count-CSP.',limitations=['No full count-profile extrapolation.','Only this coordinate pair and six ordered distinct-fibre instances; no symmetry premise or broader universe census.','Local channel and binary-strip controls do not construct a full factor.','Separate independent approval required before research use.']);save(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],summary_sha256=sha(out/'summary.json'),certificate_sha256=sha(out/'certificate.json'),exact_channel_clause=exact,escape_clause=escape,elapsed_seconds=summary['elapsed_seconds'])))
 except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__)),elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
