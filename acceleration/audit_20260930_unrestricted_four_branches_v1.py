"""Independent unrestricted four-branch cover and exact CNF suffix audit.

No producer imports. Mathematical coverage is separately written; all3360
ordered disjoint-support labels and the complete group-exchange map are checked.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json'
GATE_SHA='2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58'
MODEL=ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
CNF=MODEL.with_name('instance.cnf')
NORMALIZATION=ROOT/'acceleration/results/20260917_independent_review/root_scaffold.json'
DERIVATION=ROOT/'docs/AUDIT_20260930_UNRESTRICTED_FOUR_BRANCH_COVER.md'


def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')


def reconstruct(model):
    labels=[(a,b) for a,b in combinations(range(14),2) if a//2!=b//2]
    labels.sort(key=lambda pair:(pair[0]//2,pair[1]//2,pair[0]%2,pair[1]%2))
    index={frozenset(pair):i+15 for i,pair in enumerate(labels)}
    known=[[0]*99 for _ in range(99)]
    for u,v in combinations(range(99),2):
        if u==0:value=int(v<15)
        elif v<15:value=int((u-1)//2==(v-1)//2)
        elif u<15:value=int(u-1 in labels[v-15])
        else:value=-1
        known[u][v]=known[v][u]=value
    edge_ids={pair:i for i,pair in enumerate(combinations(range(15,99),2),1)}
    need(model['known_adjacency_full99']==known and model['outer_labels']==list(map(list,labels)),'complete unrestricted raw99scope')
    need(model['edge_variables']==[dict(u=u,v=v,id=i) for (u,v),i in edge_ids.items()],'complete3486primary map')
    need(model['fixed_K_edges']==model['fixed_outer_nonedges']==model['branch_units']==[],'no hidden outer restrictions')
    return known,labels,index,edge_ids


def from_symbols(symbols,labels,index):
    need(len(symbols)==14 and set(symbols)==set(range(14)),'symbol permutation')
    need(all(symbols[2*g]//2==symbols[2*g+1]//2 for g in range(7)),'matching groups preserved')
    p=[0]+[x+1 for x in symbols]+[index[frozenset((symbols[a],symbols[b]))] for a,b in labels]
    need(len(p)==99 and set(p)==set(range(99)),'full99 induced permutation')
    return p


def preserve(p,known):
    need(len(p)==99 and all(type(x) is int for x in p) and set(p)==set(range(99)),'strict raw permutation')
    need(all(known[u][v]==known[p[u]][p[v]] for u in range(99) for v in range(99)),'all9801scaffold entries')


def check_recipe(raw,known,labels,index,edge_ids):
    u,v=index[frozenset((0,2))],index[frozenset((4,6))]
    anchor=edge_ids[tuple(sorted((u,v)))]
    neighbors=[index[frozenset(pair)] for pair in ((0,3),(1,2),(1,3))]
    xyz=[edge_ids[tuple(sorted((u,w)))] for w in neighbors]
    need(raw['fixed_edge']==dict(labels=[[0,2],[4,6]],vertices=[u,v],variable=anchor),'exact normalized edge metadata')
    need(raw['xyz_variables']==xyz,'exact xyz edge IDs')
    symbols=[2,3,0,1]+list(range(4,14))
    exchange=from_symbols(symbols,labels,index);preserve(exchange,known)
    need(raw['exchange_pair_groups_0_1']==exchange,'exact exchange map')
    need(exchange[u]==u and exchange[v]==v and [exchange[w] for w in neighbors]==[neighbors[1],neighbors[0],neighbors[2]],'exchange fixes anchor and swapsxy')
    mapped={old:edge_ids[tuple(sorted((exchange[a],exchange[b])))] for (a,b),old in edge_ids.items()}
    need(set(mapped.values())==set(range(1,3487)),'exchange primary-variable bijection')
    need(mapped[anchor]==anchor and [mapped[e] for e in xyz]==[xyz[1],xyz[0],xyz[2]],'literal exchange direction')
    expected=[('a0',(0,0,0)),('a1_complement',(0,0,1)),('a1_cross',(1,0,0)),('a2_crosses',(1,1,0))]
    need(len(raw['branches'])==4,'exact fourbranches')
    for record,(name,bits) in zip(raw['branches'],expected):
        need(record['branch']==name and record['pattern_xyz']==list(bits),'canonical pattern metadata')
        units=[anchor]+[variable if bit else -variable for variable,bit in zip(xyz,bits)]
        need(record['units']==units and all(type(x) is int for x in record['units']),'exact signed four-unit recipe')
    allowed=[bits for bits in product((0,1),repeat=3) if bits[0]+bits[2]<=1 and bits[1]+bits[2]<=1]
    chosen={bits for _,bits in expected}
    witnesses=[]
    for bits in allowed:
        transformed=bits if bits in chosen else (bits[1],bits[0],bits[2])
        need(transformed in chosen,'complete relabeling cover of allowed bits')
        witnesses.append(dict(bits=list(bits),use_exchange=bits not in chosen,canonical=list(transformed)))
    need(allowed==[(0,0,0),(0,0,1),(0,1,0),(1,0,0),(1,1,0)],'all eight Booleanpatterns considered')
    return dict(anchor_edge_variable=anchor,xyz_edge_variables=xyz,anchor_full99_vertices=[u,v],
                checked_exchange_fixed_free_entries=9801,exchange_variable_images_checked=3486,allowed_patterns=list(map(list,allowed)),
                canonical_patterns=[list(bits) for _,bits in expected],pattern_coverage_witnesses=witnesses)


def controls(raw,known,labels,index,edge_ids):
    checked=check_recipe(raw,known,labels,index,edge_ids);rejected=[]
    for name in ('wrong_anchor_variable','wrong_anchor_vertex','wrong_xyz_variable','missing_branch','wrong_unit_sign',
                 'impossible_mixed_pattern','wrong_exchange','duplicate_exchange_vertex'):
        bad=deepcopy(raw)
        if name=='wrong_anchor_variable':bad['fixed_edge']['variable']+=1
        elif name=='wrong_anchor_vertex':bad['fixed_edge']['vertices'][1]+=1
        elif name=='wrong_xyz_variable':bad['xyz_variables'][0]+=1
        elif name=='missing_branch':bad['branches'].pop(2)
        elif name=='wrong_unit_sign':bad['branches'][0]['units'][0]*=-1
        elif name=='impossible_mixed_pattern':bad['branches'][3]['pattern_xyz']=[1,0,1]
        elif name=='wrong_exchange':bad['exchange_pair_groups_0_1']=list(range(99))
        else:bad['exchange_pair_groups_0_1'][1]=bad['exchange_pair_groups_0_1'][2]
        try:check_recipe(bad,known,labels,index,edge_ids)
        except ValueError:rejected.append(name)
        else:raise ValueError('corrupt recipe accepted: '+name)
    triples=[(a,s,d) for a,s,d in product(range(13),repeat=3) if 2*a+s==4 and a+s+d==12]
    need(triples==[(0,4,8),(1,2,9),(2,0,10)],'exact aggregate integer possibilities')
    need(all(d==8+a and d>=8 for a,s,d in triples),'derived disjoint-neighbor lower bound')
    return dict(positive_recipe_passed=True,all_boolean_patterns_checked=8,nonnegative_aggregate_triples=list(map(list,triples)),
                deliberately_corrupted_recipes_rejected=rejected,
                positive_control_scope='Exact pattern/quota/recipe checks, not a fabricated valid99graph'),checked


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False);bindings={}
    def bind(path,expected=None):
        h=digest(path);need(expected is None or h==expected,'input hash '+str(path));bindings[key(path)]=h;return Path(path)
    def read(path,expected=None):return json.loads(bind(path,expected).read_bytes())
    gate=read(GATE,GATE_SHA);need(gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','unrestricted encoding gate')
    normalization=read(NORMALIZATION,'e96941c2bc050aad65b67a4f22a8968d588ae4dbe3cd7b7f22bfe84972a963a8')
    need(normalization['status']=='INDEPENDENT_ROOT_SCAFFOLD_DERIVATION_AND_CALIBRATION_PASS','normalization premise')
    for source in (gate,normalization):
        for name,value in source['inputs_sha256'].items():bind(ROOT/name,value)
    model=read(MODEL,gate['inputs_sha256'][key(MODEL)]);bind(CNF,gate['inputs_sha256'][key(CNF)])
    manifest=read(args.run/'manifest.json')
    for name,value in manifest['inputs_sha256'].items():bind(ROOT/name,value)
    raw=read(args.run/'branches.json')
    known,labels,index,edge_ids=reconstruct(model)
    calibration,recipe=controls(raw,known,labels,index,edge_ids)
    # Derive every own/mate inner quota directly from raw known adjacency.
    quota_rows=[]
    for offset,pair in enumerate(labels):
        u=offset+15
        support_symbols={pair[0],pair[0]^1,pair[1],pair[1]^1}
        coefficients={}
        for symbol in sorted(support_symbols):
            inner=symbol+1
            constant=sum(known[u][w]*known[inner][w] for w in range(15))
            variables=[edge_ids[tuple(sorted((u,w)))] for w in range(15,99) if w!=u and known[inner][w]==1]
            residual=2-known[u][inner]-constant
            need(residual==1,'all own/mate outer quotas exactlyone')
            coefficients[symbol]=set(variables)
            quota_rows.append(dict(outer=u,symbol=symbol,known_inner_common=constant,target_common=2-known[u][inner],outer_quota=residual,variables=variables))
        for w in range(15,99):
            if w==u:continue
            variable=edge_ids[tuple(sorted((u,w)))]
            multiplicity=sum(variable in values for values in coefficients.values())
            shared=len({symbol//2 for symbol in pair}&{symbol//2 for symbol in labels[w-15]})
            need(multiplicity==shared,'2a+s exact coefficient incidence')
    need(len(quota_rows)==336,'all84times4 quotas')
    save(args.out/'independent_quota_rows.json',quota_rows)
    # Construct a normalization for every possible ordered disjoint-support
    # pair, then check all raw fixed/free entries of its full99 permutation.
    anchors=[]
    for i,left in enumerate(labels):
        for j,right in enumerate(labels):
            if {a//2 for a in left}&{a//2 for a in right}:continue
            selected=list(left)+list(right);source_groups=[symbol//2 for symbol in selected]
            remaining=[group for group in range(7) if group not in source_groups]
            group_image={group:position for position,group in enumerate(source_groups+remaining)}
            symbols=[]
            for old in range(14):
                group,side=divmod(old,2)
                chosen=next((symbol%2 for symbol in selected if symbol//2==group),0)
                symbols.append(2*group_image[group]+(side^chosen))
            p=from_symbols(symbols,labels,index);preserve(p,known)
            need(p[i+15]==recipe['anchor_full99_vertices'][0] and p[j+15]==recipe['anchor_full99_vertices'][1],'every disjoint support pair normalizes')
            anchors.append(dict(source_vertices=[i+15,j+15],full99=p))
    need(len(anchors)==84*40==3360,'all ordereddisjoint label pairs')
    save(args.out/'independent_anchor_maps.json',anchors)
    # Stream each future exact CNF recipe into hashes; do not materialize or
    # solve any branch. The base header is replaced, never duplicated.
    hashes=[sha256() for _ in raw['branches']]
    header=f"p cnf {model['variables']} {model['clauses']+4}\n".encode('ascii')
    for h in hashes:h.update(header)
    with CNF.open('rb') as stream:
        need(stream.readline()==f"p cnf {model['variables']} {model['clauses']}\n".encode('ascii'),'literal exact base header')
        for block in iter(lambda:stream.read(1<<20),b''):
            for h in hashes:h.update(block)
    suffix_checks=[]
    for record,h in zip(raw['branches'],hashes):
        need(record['variables']==model['variables'] and record['clauses']==model['clauses']+4,'future branch header counts')
        suffix=bind(ROOT/record['suffix'],record['suffix_sha256']).read_bytes()
        expected=b''.join((str(literal)+' 0\n').encode('ascii') for literal in record['units'])
        need(suffix==expected,'exact four unit suffixbytes');h.update(suffix)
        need(h.hexdigest()==record['cnf_sha256'],'exact future fullCNF recipe hash')
        suffix_checks.append(dict(branch=record['branch'],units=record['units'],suffix_sha256=digest(ROOT/record['suffix']),future_cnf_sha256=h.hexdigest(),variables=record['variables'],clauses=record['clauses']))
    # The old source is historical context only, not a coverage/proof premise.
    historical=ROOT/'scratch_general_exact_sat.py';bind(historical)
    old_text=historical.read_text(encoding='utf-8')
    need('"a2_mixed": [fixed, x, -y, complement]' in old_text,'historical nominal101case identity')
    for path in (__file__,DERIVATION,ROOT/'uv.lock'):bind(path)
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input stability')
    report=dict(status='INDEPENDENT_UNRESTRICTED_FOUR_BRANCH_COVER_PASS',claim_id='C-UNRESTRICTED-FOUR-BRANCH-COVER',claim_revision=1,
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent written coverage proof, all336quotas, all3360anchor relabelings, complete scaffold swap/variable mapping, and raw suffix recipe hashing',
        recommendation='VERIFIED',kind='mathematical result',basis=['DERIVED','COMPUTED'],
        statement='A target exists if and only if at least one of the four exact recorded unrestricted full99 branch CNFs is satisfiable. Every target admits a root/edge labeling with anchor variable44 true and xyz variables1,2,3 respectively000,001,100,or110; the recorded suffixes implement exactly these cases.',
        scope='Complete unrestricted-target coverage up to proved vertex relabeling, using the exactnew unrestrictedbaseCNF; no graph automorphism assumption.',
        assumptions=['The exact target identity and current root-normalization/encoding premises.',
                     'Future branch files must reproduce the checked base-body/header/four-unit recipe hashes.'],
        dependencies=[dict(id='C-ROOT-SCAFFOLD-NORMALIZATION',revision=1,relation='normalization'),
                      dict(id='C-UNRESTRICTED-FULL99-PREFIX-CNF-ENCODING',revision=1,relation='encoding_equivalence')],
        inputs_sha256=bindings,controls=calibration,written_derivation=key(DERIVATION),**recipe,
        exact_own_mate_quota_rows=336,ordered_disjoint_support_normalizations_checked=3360,
        normalization_fixed_free_entries_checked=3360*9801,outer_degree=12,disjoint_neighbor_identity='d=8+a',disjoint_neighbor_lower_bound=8,
        quota_artifact=dict(path=key(args.out/'independent_quota_rows.json'),sha256=digest(args.out/'independent_quota_rows.json')),
        anchor_map_artifact=dict(path=key(args.out/'independent_anchor_maps.json'),sha256=digest(args.out/'independent_anchor_maps.json')),
        checked_branch_recipes=suffix_checks,base_cnf_sha256=digest(CNF),base_model_sha256=digest(MODEL),encoding_gate_sha256=GATE_SHA,
        historical_relationship='Same four viable cases already appeared in the historical five-case portfolio; the nominala2_mixed101case violatesx+z<=1. No historical solver status is used as a proof premise, and no novelty is claimed.',
        producer_imported=False,shared_components=['Python standard library exact integers, hash streams, and JSON',
            'Hash-bound prior independent unrestricted encoding and root-normalization audits are reused; the new coverage derivation and literal mapping are checked separately'],
        limitations=['No branch was solved and no branch UNSAT proof is asserted.',
                     'Relabeling coverage does not imply every fixed-label base assignment satisfies these units.',
                     'Target isomorphism classes may occur in multiple branches; branch counts are not equal graph/runtime fractions.',
                     'Full branch CNFs are currently recipes; this checker did not create large CNF copies or mutate the base.',
                     'General nonexistence still needs complete independently replayed proofs for every exact branch.'],
        solver_calls=0,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],branches=len(suffix_checks),anchor_maps=len(anchors),sha256=digest(args.out/'summary.json'))))


if __name__=='__main__':main()
