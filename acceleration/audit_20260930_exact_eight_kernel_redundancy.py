"""Independent literal residual-row and additive-space audit; no producer imports."""
from pathlib import Path
from itertools import combinations, product
from datetime import datetime, timezone
import argparse, copy, gzip, hashlib, json, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_';I=B+'independent_review/';D=B+'exact_eight_kernel_redundancy/'
RAW=B+'hadamard20_support/six_prism.json'
MAN=B+'exact_eight_campaign_preparation/campaign_manifest.json'
PSD=I+'exact_eight_psd_screen/'
INV=I+'exact_eight_campaign_inventory/'
DOC='docs/AUDIT_20260930_EXACT_EIGHT_KERNEL_REDUNDANCY.md'
PINS={D+'summary.json':'16b571378defeae3dc591905466f391fceee159bb8e0075945b42ca5af212ebb',
 RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 MAN:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',
 PSD+'summary.json':'94f6313cbd0bdc6ddef5930a53bb09f22742abe6a3cfe42fccf0cd9416bf259a',
 INV+'summary.json':'555ef430f8a84b8b995c98566decf2c6cb92f9e8de6db1645955c0e48dd0f9ea',
 B+'srg243_residual_fixture/triangle_blocks.json':'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',
 I+'srg243_residual_fixture/summary.json':'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e',
 B+'hadamard_triplicate_counts/local_triples.json':'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776'}
INPUTS={}

def need(condition,message):
    if not condition:raise ValueError(message)
def path(p):
    p=str(p).replace('\\','/');q=(ROOT/p).resolve();need(q.is_relative_to(ROOT),'repository path')
    relative=q.relative_to(ROOT).as_posix()
    need(relative!=I+'hadamard_oriented_unknown/process.stdout.log' and q.name!='PROMPT.md' and not relative.startswith('tools/'),'protected path')
    return q
def pin(p,h=None):
    q=path(p)
    with q.open('rb')as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    need(h is None or h==actual,'hash '+str(p));INPUTS[q.relative_to(ROOT).as_posix()]=actual;return q
def read(p):return json.loads(pin(p).read_bytes())
def gzread(p):return json.loads(gzip.decompress(pin(p).read_bytes()))
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def savegz(p,x):
    with p.open('xb')as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0)as z:z.write((json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode())
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def gram(a):return [[sum(x*y for x,y in zip(r,s))for s in a]for r in a]
def residual(g,n):
    nn=gram(n);return [[3*g[i][j]-nn[i][j]for j in range(len(g))]for i in range(len(g))]

def core_gram(raw):
    edges=[set()for _ in range(36)]
    for f in range(3):
        for a in range(12):
            edges[12*f+a].add(12*f+(a^1))
            edges[12*f+a].update(12*h+a for h in range(3)if h!=f)
    c=[[int(j in edges[i])for j in range(36)]for i in range(36)]
    g=[[12*int(i==j)+2-int(j in edges[i])-len(edges[i]&edges[j])-int(i//12==j//12)for j in range(36)]for i in range(36)]
    need(c==raw['core_adjacency'] and g==raw['prescribed_Gram36'],'literal set-intersection core/Gram');return g

def basis():
    # Column vectors represented by their 36 integer coordinates.
    return [[int(i%12==a)for i in range(36)]for a in range(12)]+[[int(i//12==f)for i in range(36)]for f in (1,2)]
def left_inverse_check(vectors):
    need(len(vectors)==14 and all(len(v)==36 for v in vectors),'basis dimensions')
    # Recover alpha from fibre0; recover beta1/beta2 by differences at coordinate0.
    columns=[v[:12]+[v[12]-v[0],v[24]-v[0]]for v in vectors]
    need(columns==[[int(i==j)for i in range(14)]for j in range(14)],'explicit left inverse')
    return columns
def annihilation_by_row_sums(r):
    need(len(r)==36 and all(len(v)==36 for v in r),'residual dimension')
    return [[sum(row[a+12*f]for f in range(3))for a in range(12)]+[sum(row[12:24]),sum(row[24:36])]for row in r]
def check_zero(r):
    result=annihilation_by_row_sums(r);need(all(x==0 for row in result for x in row),'annihilation');return result
def count_matrix(counts,groups):
    need(len(counts)==12 and all(len(row)==20 for row in counts),'count table dimensions')
    for a in range(12):
        for g,support in enumerate(groups):
            v=counts[a][g]
            need(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v),'literal integer counts')
            need(sum(v)==3*int(a in support),'three supported columns')
    n=[[counts[a][g][f]for g in range(20)]for f in range(3)for a in range(12)]
    need(all(sum(row)==10 for row in n),'full factor row margins')
    need(all(sum(n[12*f+a][g]for a in range(12))==6 for g in range(20)for f in range(3)),'group fibre quotas')
    return n
def words_by_pairs():
    words=[]
    for first in combinations(range(6),2):
        remaining=[i for i in range(6)if i not in first]
        for second in combinations(remaining,2):words.append(tuple(0 if i in first else 1 if i in second else 2 for i in range(6)))
    need(len(words)==len(set(words))==90,'complete disjoint-pair word enumeration');return sorted(words)
def projection(vectors,support,word):return [sum(v[12*f+a]for a,f in zip(support,word))for v in vectors]
def check_word(vectors,support,word):
    need(len(word)==6 and sorted(word)==[0,0,1,1,2,2],'word quotas')
    expected=[int(a in support)for a in range(12)]+[2,2]
    need(projection(vectors,support,word)==expected,'word projection');return expected

def factor_identity(f):
    n=len(f);m=len(f[0]);need(m%3==0 and all(len(r)==m for r in f),'rectangular triplicate factor')
    ng=[[sum(row[j:j+3])for j in range(0,m,3)]for row in f]
    r=residual(gram(f),ng)
    differences=[[row[j]-row[k]for g in range(0,m,3)for j,k in combinations(range(g,g+3),2)]for row in f]
    need(r==gram(differences),'integer sum-of-squares identity')
    return r,differences
def reject(name,fn,records):
    try:fn()
    except(ValueError,KeyError,IndexError):records.append(name);return
    raise ValueError('accepted corruption '+name)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for p,h in PINS.items():pin(p,h)
        for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md'),DOC,'uv.lock','pyproject.toml']:pin(p)
        candidate=read(D+'summary.json');need(candidate['status']=='CANDIDATE_COMPLETE792_KERNEL_REDUNDANCY','candidate completed status')
        for name in ('inputs_sha256','outputs_sha256'):
            for p,h in candidate[name].items():pin(p,h)
        pg=read(PSD+'summary.json');ig=read(INV+'summary.json')
        need(pg['status']=='INDEPENDENT_EXACT_EIGHT_PSD_SCREEN_PASS' and pg['canonical_profiles']==792 and pg['rank_counts']=={'22':792},'complete prior rank22 gate')
        need(ig['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_INVENTORY_PASS','complete prior local-domain gate')
        for gate in [pg,ig]:
            for p,h in gate['outputs_sha256'].items():pin(p,h)
        certs=gzread(PSD+'integer_congruence_checks.json.gz');need(certs['complete']is True,'prior rank checks complete')
        certmap={r['canonical_fibre_profile_sha256']:r for r in certs['records']};need(len(certmap)==792,'prior rank coverage unique')
        inventory=gzread(INV+'independent_inventory.json.gz')['records'];manifest=read(MAN)['records'];savedcases=gzread(D+'cases.json.gz');raw=read(RAW)
        need(len(manifest)==len(inventory)==len(savedcases)==792,'complete792 populations')
        groups=[]
        for j in range(60):
            s=[a for a in range(12)if raw['L'][a][j]]
            if s not in groups:groups.append(s)
        need(len(groups)==20 and all(len(s)==6 for s in groups),'literal support group population')
        need(all(sum([a for a in range(12)if raw['L'][a][j]]==s for j in range(60))==3 for s in groups),'triplicate support multiplicity')
        g=core_gram(raw);vectors=basis();inverse=left_inverse_check(vectors);words=words_by_pairs();saved=read(D+'basis_and_controls.json')
        need(saved['W']==list(map(list,zip(*vectors))) and saved['identity_minor']==inverse,'saved basis and independence certificate')
        wordtables=[]
        for support,item in zip(groups,saved['projections']):
            table=[check_word(vectors,support,w)for w in words]
            need(item==dict(support=support,word_projections=table),'every saved word dot-product')
            wordtables.append(dict(support=support,word_projections=table))
        need(len(saved['projections'])==20,'complete saved projection population')
        local=read(B+'hadamard_triplicate_counts/local_triples.json')
        # The approved complete catalogue supplies normalization/coverage; literal
        # membership of each of its columns in this newly enumerated word universe
        # is sufficient for the universal projection argument.
        need(local['words']==[list(w)for w in words],'raw complete word universe')
        need(len(local['survivors'])==31110 and all(len(t)==3 and len(set(t))==3 and all(type(k)is int and 0<=k<90 for k in t)for t in local['survivors']),'all catalogue columns covered by word argument')
        save(out/'manifest.json',dict(inputs_sha256=dict(INPUTS),command=[sys.executable,*sys.argv],cwd=str(ROOT),allocation_seconds=120,method='Literal full residual entries and restricted row sums, not producer factored products; rank is an explicit authenticated prior dependency.'))
        controls=[]
        # Test the sum-of-squares identity independently of research inputs.
        for bits in product((0,1),repeat=12):factor_identity([list(bits[3*i:3*i+3])for i in range(4)])
        fixture=read(B+'srg243_residual_fixture/triangle_blocks.json')['factor60x180'];rf,df=factor_identity(fixture)
        need(all(sum(row[j]for row in fixture)==6 for j in range(180)),'genuine fixture uniform column size')
        need(all(sum(row)==0 for row in rf) and all(sum(row[j]for row in df)==0 for j in range(180)),'genuine fixture kernel projection necessity')
        outside=[0]*36;outside[0]=1;support=next(s for s in groups if 0 in s)
        need({projection([outside],support,w)[0]for w in words}=={0,1},'non-additive vector distinguishes words')
        bad=copy.deepcopy(vectors);bad[0][0]+=1;reject('basis_entry',lambda:left_inverse_check(bad),controls)
        bad=copy.deepcopy(vectors);bad[-1]=bad[0][:];reject('dependent_basis',lambda:left_inverse_check(bad),controls)
        reject('wrong_word_quota',lambda:check_word(vectors,support,(0,)*6),controls)
        alteredtable=copy.deepcopy(saved['projections']);alteredtable[0]['word_projections'][0][0]+=1
        reject('saved_projection_changed',lambda:need(alteredtable==saved['projections'],'projection equality'),controls)
        allchecks=[];total=0
        for r,inv,old in zip(manifest,inventory,savedcases):
            identity=r['full_count_profile_sha256'];need(inv['case_id']==old['case_id']==r['case_id'] and inv['full_count_profile_sha256']==old['full_count_profile_sha256']==identity,'literal profile joins')
            counts=r['raw_representative']['counts'];n=count_matrix(counts,groups);matrix=residual(g,n);ann=check_zero(matrix)
            cert=certmap[identity];pin(cert['raw_certificate_path'],cert['raw_certificate_sha256'])
            need((digest(g),digest(n),digest(matrix))==(cert['G_sha256'],cert['N_sha256'],cert['R_sha256']),'same exact matrices as approved rank22 certificate')
            need(cert['rank']==22 and cert['nullity']==14,'exact rank premise')
            options=sum(inv['initial_domain_sizes']);total+=options
            need(old==dict(case_id=r['case_id'],case_index=r['case_index'],full_count_profile_sha256=identity,integer_annihilation_residual=ann,initial_options=options,removed_options=0),'complete candidate raw record')
            allchecks.append(dict(case_id=r['case_id'],full_count_profile_sha256=identity,N_sha256=digest(n),R_sha256=digest(matrix),restricted_row_sums=ann,rank22_dependency_raw=cert['raw_certificate_path'],initial_options=options,removed_options=0))
            need(time.monotonic()-start<120,'allocation')
        need(set(certmap)=={r['full_count_profile_sha256']for r in manifest},'exact complete rank population')
        need(total==candidate['initial_options']==1687356 and candidate['profiles']==792 and candidate['removed_options']==0 and candidate['kernel_dimension']==14,'terminal census values')
        n=count_matrix(manifest[0]['raw_representative']['counts'],groups);r=residual(g,n)
        bad=copy.deepcopy(r);bad[0][0]+=1;reject('changed_residual_diagonal',lambda:check_zero(bad),controls)
        bad=copy.deepcopy(manifest[0]['raw_representative']['counts']);bad[0][0][0]+=1;reject('changed_count',lambda:count_matrix(bad,groups),controls)
        wrongg=copy.deepcopy(g);wrongg[0][0]+=1;reject('changed_Gram',lambda:check_zero(residual(wrongg,n)),controls)
        reject('omitted_profile',lambda:need(len(manifest[:-1])==792,'complete population'),controls)
        badcert=copy.deepcopy(cert);badcert['R_sha256']='0'*64;reject('misbound_rank_certificate',lambda:need(digest(matrix)==badcert['R_sha256'],'matrix binding'),controls)
        reject('rank_not22',lambda:need(23==22,'rank dependency'),controls)
        # All entries of the whole kernel space follow from the additive formula,
        # not just the fourteen basis columns checked as raw controls.
        for seed in range(32):
            alpha=[((seed+3*a)%11)-5 for a in range(12)];beta=[0,(seed%7)-3,((2*seed)%9)-4]
            v=[alpha[a]+beta[f]for f in range(3)for a in range(12)]
            for support in groups:
                need(all(projection([v],support,w)==[sum(alpha[a]for a in support)+2*beta[1]+2*beta[2]]for w in words),'whole-space additive controls')
        savegz(out/'literal_residual_checks.json.gz',dict(complete=True,records=allchecks))
        save(out/'basis_and_word_checks.json',dict(basis_vectors=vectors,left_inverse_applied_to_basis=inverse,words=[list(w)for w in words],projections=wordtables,dimension=14))
        save(out/'controls.json',dict(binary_triplicate_identities=4096,genuine243_identity=True,genuine243_constant_projection=True,nonadditive_word_values=[0,1],integer_additive_vectors=32,corruptions_rejected=controls,research_factor_positive=False))
        now=datetime.now(timezone.utc).isoformat();status='INDEPENDENT_EXACT_EIGHT_COMMON_KERNEL_REDUNDANCY_PASS'
        method='Independent set-intersection core/Gram, literal full residual matrices and coordinate/fibre row sums; exact matrix binding to prior rank22 certificates; explicit left inverse and disjoint-pair enumeration of all90 local words.'
        result=dict(status=status,created_at=now,updated_at=now,verifier='/root/state_literature_audit',method=method,profiles=792,kernel_dimension=14,initial_options=total,removed_options=0,word_projection_entries=20*90*14,annihilation_entries=792*36*14,rank_dependency=PSD+'summary.json',controls=dict(binary_identities=4096,genuine243=1,additive_vectors=32,corruptions=len(controls)),inputs_sha256=INPUTS,outputs_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in out.iterdir()if p.is_file()},command=[sys.executable,*sys.argv],cwd=str(ROOT),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),elapsed_seconds=time.monotonic()-start,artifact_availability='LOCAL_ONLY',shared_components=['Python standard library; no producer or prior checker imports.','Previously independently verified exact792 rank22 certificates and complete local-domain inventory are explicit mathematical dependencies, authenticated down to literal matrix hashes.'],limitations=['No new rank recomputation is claimed.','No conclusion for count tables outside these792; no factor existence or exclusion.','The three-profile kernel result is historical context only, not extrapolated as the new claim premise.'])
        save(out/'summary.json',result)
        binding=dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-COMMON-KERNEL-OPTION-REDUNDANCY',revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For every one of the792 authenticated canonical exactly-eight scalar/block survivor count tables on the literal six-prism support, the kernel of R=3G-NN^T is precisely the14-dimensional space v[f,a]=alpha[a]+beta[f], with beta[0]=0. Every vector in this space has constant projection on all90 balanced colour words of each of the20 supports. Consequently the necessary triplicate PSD-kernel projection test removes zero of the1,687,356 complete initial local options.',scope='Only the exact792 canonical count tables and literal support. This is a redundancy result for one necessary local projection test, not simultaneous factor feasibility or target exclusion.',assumptions=['Exact prescribed integer Gram matrix and triplicate support grouping.','The independently verified rank22 certificate applies to each exact same R.','Every initial local option consists of three words selecting one fibre per support coordinate and two coordinates in each fibre.'],dependencies=[dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SURVIVOR-PSD-SCREEN',revision=2,relation='uses_result'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-DOMAIN-INVENTORY',revision=1,relation='coverage'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='coverage')],verifier=result['verifier'],method=method,created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY',independent_verification=dict(report=(out/'summary.json').relative_to(ROOT).as_posix(),sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest(),status=status),inputs_sha256=INPUTS,controls=result['controls'],shared_components=result['shared_components'],limitations=result['limitations'])
        save(out/'claim_binding.json',binding);print(json.dumps(dict(status=status,summary_sha256=hashlib.sha256((out/'summary.json').read_bytes()).hexdigest(),binding_sha256=hashlib.sha256((out/'claim_binding.json').read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start)))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),inputs_sha256=INPUTS,elapsed_seconds=time.monotonic()-start));raise

if __name__=='__main__':main()
