"""Independent exact full-formula audit, with no producer imports."""
from pathlib import Path
from itertools import product
from datetime import datetime, timezone
from collections import Counter
import argparse, copy, hashlib, json, platform, subprocess, sys, time, zlib

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/'
D=B+'count_min_upper_cnf/';BASE=B+'count_master_scalar_cuts/'
MASTER=B+'hadamard_count_master_cnf/model.json'
RAW=B+'hadamard20_support/six_prism.json'
PROFILE=I+'count_master_partial_cut_sat_outcome/independent_count_profile.json'
ASSIGN=B+'count_master_partial_cuts_native_pilot/main/parsed_model.json'
PINS={
    MASTER:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
    RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    PROFILE:'03d68bdfff62aa6f73dd44d72eab80acfdb8d001bb1b504df7aa36707b8d695e',
    ASSIGN:'29a86b25a32b466bb7ff8b501421f1c38306728506306be343d006cc1f9a4324',
    BASE+'instance.cnf':'baca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b',
    I+'count_master_partial_cut_cnf/summary.json':'dc1ada9d87d41b5cc6597cd0ff7ce2ed0a06981d8b487dbb797505240f435460',
    I+'count_master_partial_cut_sat_outcome/summary.json':'736ccbcda81ee34c21ede2a80253d5b224fabb96a2e83d0a2c1c76dba435d071',
}

def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def literal_bytes(cs):return b''.join((' '.join(map(str,c))+' 0\n').encode()for c in cs)
def holds(cs,truth):return all(any(truth[abs(v)]==(v>0)for v in c)for c in cs)
def threshold(q,xs):return [[-v,q]for v in xs]+[[-q]+list(xs)]
def conjunction(q,a,b):return [[-q,a],[-q,b],[q,-a,-b]]
def at_least(xs,k):
    need((len(xs),k)in[(5,1),(10,2)],'supported exact bound')
    return [list(xs)]if k==1 else [list(xs[:i])+list(xs[i+1:])for i in range(len(xs))]

def decode_assignment(xs,n):
    need(type(xs)is list and len(xs)==n,'complete assignment length')
    result={}
    for x in xs:
        need(type(x)is int and 1<=abs(x)<=n and abs(x)not in result,'unique integer IDs')
        result[abs(x)]=x>0
    return result

def composition(old,new,suffix):
    header,body=old.split(b'\n',1);need(header==b'p cnf 155939 705845','exact old header')
    need(new==b'p cnf 161159 726485\n'+body+suffix,'entire formula identity')

def scope_check(scope,groups):
    need(scope['schema']=='FIXED_SUPPORT_COUNT_MIN_UPPER_SCOPE_V1','scope version')
    for k,v in dict(groups=groups,count_only=True,full_factor=False,target_graph=False,independent_approval=False,no_target_automorphism_assumed=True).items():need(scope.get(k)==v,'scope '+k)
    for p,h in [('raw_support_path','raw_support_sha256'),('old_scope_path','old_scope_sha256')]:need(sha(scope[p])==scope[h],'scope identity')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--producer-summary-sha256',required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();pins={}
    def pin(p,h=None):
        q=sha(p);need(h is None or q==h,'identity '+str(p));need(p not in pins or pins[p]==q,'consistent binding');pins[str(p)]=q
    try:
        for p,h in PINS.items():pin(p,h)
        pin(D+'summary.json',args.producer_summary_sha256);producer=read(D+'summary.json')
        for field in ['inputs_sha256','outputs_sha256']:
            for p,h in producer[field].items():pin(p,h)
        for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/AUDIT_20260930_COUNT_MIN_UPPER_CNF.md','uv.lock','pyproject.toml']:pin(p)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,solver_calls=0,limits_seconds=120))
        raw=read(RAW);C=raw['core_adjacency'];groups=[]
        for s in raw['support_columns']:
            if s not in groups:groups.append(s)
        need(len(groups)==20 and all([j for j,x in enumerate(raw['support_columns'])if x==s]==[g,g+20,g+40]for g,s in enumerate(groups)),'literal triplicate support')
        for i in range(36):
            for j in range(36):need(raw['prescribed_Gram36'][i][j]==12*(i==j)-C[i][j]-sum(C[i][z]*C[z][j]for z in range(36))+2-int(i//12==j//12),'all integer Gram entries')
        master=read(MASTER);need(master['groups']==groups,'master group identities')
        channels={(x['coordinate'],x['group']):x for x in master['count_channels']}
        need(set(channels)=={(a,g)for g,s in enumerate(groups)for a in s}and len(channels)==120,'all incidence channels')
        model=read(D+'model.json');scope_check(read(D+'scope.json'),groups)
        need((model['variables'],model['clauses'],model['old_variables'],model['old_clause_count'])==(161159,726485,155939,705845),'dimensions')
        for p,h in [('base_count_model_path','base_count_model_sha256'),('prefix_cnf_path','prefix_cnf_sha256'),('prefix_model_path','prefix_model_sha256'),('cnf_path','cnf_sha256'),('scope_path','scope_sha256'),('suffix_path','suffix_sha256')]:need(sha(model[p])==model[h],'model reference')
        clause_rows=[];thresholds=[];products=[];cells=[];ids={};nextvar=155939;empty=0;local_choices=0
        for a,g in sorted(channels):
            ch=channels[a,g]
            for f in range(3):
                for t in [1,2]:
                    nextvar+=1;ids[a,g,f,t]=nextvar;selected=[v for v,c in zip(ch['variables'],ch['values'],strict=True)if c[f]>=t]
                    r=dict(coordinate=a,group=g,fibre=f,threshold=t,variable=nextvar,selected_alternatives=selected,count_channel_variables=ch['variables'],count_channel_values=ch['values']);thresholds.append(r)
                    cs=threshold(nextvar,selected);clause_rows+=cs;empty+=not selected
                    for chosen,count in enumerate(ch['values']):
                        values={v:k==chosen for k,v in enumerate(ch['variables'])};values[nextvar]=count[f]>=t
                        need(holds(cs,values),'all one-hot count positives');values[nextvar]=not values[nextvar];need(not holds(cs,values),'all inverted threshold negatives');local_choices+=1
        for a in range(12):
            for b in range(a+1,12):
                gs=[g for g,s in enumerate(groups)if a in s and b in s]
                if not gs:need(b==a^1,'omitted matched pair');continue
                need(len(gs)==5,'complete five-group contributions')
                for f in range(3):
                    for h in range(3):
                        i,j=12*f+a,12*h+b;k=raw['prescribed_Gram36'][i][j];need(k==(1 if f==h else 2),'scalar targets');qs=[]
                        for g in gs:
                            for t in range(1,k+1):
                                nextvar+=1;l,r=ids[a,g,f,t],ids[b,g,h,t];qs.append(nextvar)
                                products.append(dict(coordinates=[a,b],fibres=[f,h],group=g,threshold=t,variable=nextvar,left=l,right=r));clause_rows+=conjunction(nextvar,l,r)
                        clause_rows+=at_least(qs,k);cells.append(dict(coordinates=[a,b],fibres=[f,h],rows=[i,j],target=k,incident_groups=gs,product_variables=qs,bound_clause_count=1 if k==1 else 10))
        need((nextvar,len(thresholds),len(products),len(cells),len(clause_rows),empty)==(161159,720,4500,540,20640,27),'complete populations')
        need(model['threshold_channels']==thresholds and model['overlap_products']==products and model['scalar_cells']==cells,'all metadata reconstructed')
        suffix=literal_bytes(clause_rows);old=(ROOT/BASE/'instance.cnf').read_bytes();new=(ROOT/D/'instance.cnf').read_bytes()
        composition(old,new,suffix);need((ROOT/D/'suffix.cnf.body').read_bytes()==suffix and len(suffix)==571440 and len(new)==11834633,'exact suffix and byte sizes')
        # The theorem is checked by exact finite strips; clipping is checked on every minimum vector.
        strips=list(product((0,1),repeat=3))
        for x,y in product(strips,repeat=2):need(sum(a*b for a,b in zip(x,y))<=min(sum(x),sum(y)),'binary-strip inequality')
        for x,y,k in product(range(4),range(4),[1,2]):need(sum(x>=t and y>=t for t in range(1,k+1))==min(x,y,k),'threshold sum is clipped minimum')
        for xs,k in product(product(range(4),repeat=5),[1,2]):need((sum(xs)>=k)==(sum(min(x,k)for x in xs)>=k),'all clipped thresholds')
        gate_cases=0
        for n in range(5):
            for vals in product([False,True],repeat=n+1):
                need(holds(threshold(n+1,list(range(1,n+1))),dict(enumerate(vals,1)))==(vals[-1]==any(vals[:-1])),'OR complete table');gate_cases+=1
        for x,y,z in product([False,True],repeat=3):need(holds(conjunction(3,1,2),{1:x,2:y,3:z})==(z==(x and y)),'AND complete table')
        for n,k in [(5,1),(10,2)]:
            for vals in product([False,True],repeat=n):need(holds(at_least(list(range(1,n+1)),k),dict(enumerate(vals,1)))==(sum(vals)>=k),'bound complete table')
        original=read(ASSIGN)['assignment'];candidate=read(D+'candidate_auxiliary_assignment.json')['assignment'];v=decode_assignment(candidate,161159)
        need(candidate[:155939]==original,'all old assignment IDs unchanged');counts=read(PROFILE)['coordinate_group_fibre_counts']
        for r in thresholds:need(v[r['variable']]==(counts[r['coordinate']][r['group']][r['fibre']]>=r['threshold']),'threshold from independent raw counts')
        for r in products:need(v[r['variable']]==(v[r['left']]and v[r['right']]),'every conjunction auxiliary')
        for c in cells:
            a,b=c['coordinates'];f,h=c['fibres'];need(sum(min(counts[a][g][f],counts[b][g][h])for g in c['incident_groups'])>=c['target'],'all540 raw upper inequalities')
        actual=[]
        for line in new.splitlines()[1:]:
            row=list(map(int,line.split()));need(row[-1]==0 and all(0<abs(v)<=161159 for v in row[:-1]),'actual DIMACS syntax');actual.append(row[:-1])
        need(len(actual)==726485 and holds(actual,v),'all actual clauses satisfied')
        recovered=[]
        for record in read(D+'artifact_packages.json')['records']:
            blocks=[];offset=0
            for part in record['parts']:
                z=(ROOT/part['path']).read_bytes();need(hashlib.sha256(z).hexdigest()==part['gzip_sha256']and len(z)==part['gzip_bytes'],'compressed hash/size')
                decoder=zlib.decompressobj(31);plain=decoder.decompress(z)+decoder.flush();need(decoder.eof and not decoder.unused_data,'single complete gzip member')
                need(part['raw_offset']==offset and len(plain)==part['raw_bytes']and hashlib.sha256(plain).hexdigest()==part['raw_sha256'],'raw part identity');blocks.append(plain);offset+=len(plain)
            plain=b''.join(blocks);need(plain==(ROOT/record['path']).read_bytes()and len(plain)==record['bytes']and hashlib.sha256(plain).hexdigest()==record['sha256'],'complete literal recovery');recovered.append(dict(path=record['path'],bytes=len(plain),parts=len(blocks)))
        rejected=[]
        def reject(name,fn):
            try:fn()
            except(ValueError,KeyError,TypeError,IndexError):rejected.append(name)
            else:raise ValueError('corruption accepted '+name)
        for label,bad in [('header',new.replace(b'726485',b'726484',1)),('missing_clause',new[:-2]),('extra_clause',new+b'1 0\n'),('suffix_sign',new[:-len(suffix)]+b'-'+suffix),('prefix_sign',new.replace(b'1 ',b'-1 ',1))]:reject(label,lambda bad=bad:composition(old,bad,suffix))
        for label,bad in [('missing_id',candidate[:-1]),('duplicate_id',[candidate[0]]+candidate[:-1]),('boolean_id',[True]+candidate[1:]),('out_of_range',[161160]+candidate[1:])]:reject(label,lambda bad=bad:decode_assignment(bad,161159))
        for r in [thresholds[0],products[0]]:
            wrong=v.copy();wrong[r['variable']]=not wrong[r['variable']];need(not holds(clause_rows,wrong),'changed auxiliary rejected');rejected.append('flipped_auxiliary_'+str(r['variable']))
        for field in ['count_only','full_factor','target_graph','no_target_automorphism_assumed']:
            bad=read(D+'scope.json');bad[field]=not bad[field];reject('scope_'+field,lambda bad=bad:scope_check(bad,groups))
        save(out/'controls.json',dict(rejected=rejected,strip_pairs=64,clipped_pair_tests=32,minimum_vectors=2048,OR_assignments=gate_cases,AND_assignments=8,bound_assignments=1056,one_hot_threshold_choices=local_choices,actual_clauses=726485,recovery=recovered))
        need(time.monotonic()-start<120,'cooperative audit limit');stamp=datetime.now(timezone.utc).isoformat()
        binding=dict(id='C-FIXED-HADAMARD-ALL-SCALAR-UPPER-COUNT-ENCODING',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='The exact161159-variable726485-clause formula is satisfiable iff the frozen twelve-cut count relaxation has a count assignment satisfying all540 inequalities sum_g min(n[a,g,f],n[b,g,h]) >= G[12f+a,12h+b], for all60 nonmatching coordinate pairs and nine ordered fibre pairs. It adds5220 uniquely determined Boolean auxiliaries and20640 clauses. The previously checked third count assignment has a checked auxiliary extension satisfying every clause.',scope='Literal six-prism Hadamard support and inherited >=7 count relaxation only. Universal scalar upper bounds are necessary but do not assert exact local extrema or simultaneous Gram realization.',assumptions=['Independently checked twelve-cut count encoding and its exact count-channel semantics.','Frozen raw support and exact integer Gram.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PROFILE-SIX-SCALAR-CUT-COUNT-ENCODING',revision=1,relation='encoding_equivalence'),dict(id='C-FIXED-HADAMARD-PARTIAL-CUT-COUNT-CSP-WITNESS',revision=1,relation='verification_dependency')],verifier='/root',producer='/root/state_literature_audit',method='Independent raw support/count reconstruction, every clause and auxiliary, complete finite gate controls and literal gzip recovery.',shared_components=['Prior independent count encoding and third count witness are pinned premises. No producer imports or solver calls.','Python standard library and the same raw support/count metadata are shared trusted inputs.'],inputs_sha256=pins,limitations=['No fresh count profile or native outcome; only the same saved witness extended by deterministic auxiliaries.','No full factor, residualD, whole-support exclusion or unrestricted target result.','Prior count encoding derivation is not repeated here.'],created_at=stamp,updated_at=stamp)
        save(out/'claim_binding.json',binding)
        result=dict(status='INDEPENDENT_COUNT_MIN_UPPER_CNF_PASS',timestamp=stamp,inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p.relative_to(ROOT))for p in out.iterdir()if p.is_file()},variables=161159,clauses=726485,new_variables=5220,new_clauses=20640,thresholds=720,empty_threshold_ORs=27,products=4500,scalar_cells=540,controls_rejected=len(rejected),solver_calls=0,native_calls=0,shared_components=binding['shared_components'],elapsed_seconds=time.monotonic()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha((out/'summary.json').relative_to(ROOT)),binding_sha256=sha((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),source_sha256=sha(Path(__file__).relative_to(ROOT))));raise
if __name__=='__main__':main()
