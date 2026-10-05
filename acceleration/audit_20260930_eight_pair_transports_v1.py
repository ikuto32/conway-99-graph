"""Independent finite signed-pair census and full99 clause-transport audit.

No producer or checker imports. The complete raw family and source-clause gate
are authenticated; every supplied map, rejection witness and clause is checked.
"""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,permutations,product
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/'acceleration/results/20260930_independent_review/eight_full99_w81_gram_cut/summary.json'
GATE_SHA='d0b8e269801c7f00b9ec1c04dd504978372c93c4264ae022eeea6d1340fe4fcd'
MODEL=ROOT/'acceleration/results/20260930_eight_full99_cnf/model.json'
MODEL_SHA='f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee'
ENCODING=ROOT/'acceleration/results/20260930_independent_review/eight_full99_cnf/summary.json'
ENCODING_SHA='ecd4adb354a0c8c03589b1446ab511014ea47c7b5bf9ff1d529d34a2d1c79667'


def need(condition,message):
    if not condition:raise ValueError(message)
def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def unique_json(pairs):
    result={}
    for name,value in pairs:need(name not in result,'duplicate JSON key');result[name]=value
    return result
def parse(raw):return json.loads(raw,object_pairs_hook=unique_json)


def reconstruct(model,scope):
    labels=sorted((a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2)
    labels.sort(key=lambda pair:(pair[0]//2,pair[1]//2,pair[0]%2,pair[1]%2))
    fixed={tuple(pair) for pair in scope['remaining_fixed_K_edges_outer']}
    free={tuple(pair) for pair in scope['unknown_edges_outer']}
    need(len(fixed)==120 and len(free)==2160 and not fixed&free,'exact family inventories')
    known=[[0]*99 for _ in range(99)]
    for u,v in combinations(range(99),2):
        if u==0:value=int(v<15)
        elif v<15:value=int((u-1)//2==(v-1)//2)
        elif u<15:value=int(u-1 in labels[v-15])
        else:value=-1 if (u-15,v-15) in free else int((u-15,v-15) in fixed)
        known[u][v]=known[v][u]=value
    need(model['known_adjacency_full99']==known,'complete reconstructed99 scope')
    need(model['outer_labels']==list(map(list,labels)),'outer label ordering')
    mapping={row['id']:(row['u'],row['v']) for row in model['edge_variables']}
    expected={index:(u+15,v+15) for index,(u,v) in enumerate(sorted(free),1)}
    need(mapping==expected and len(model['edge_variables'])==2160,'complete edge labels')
    return known,labels,mapping,{pair:variable for variable,pair in mapping.items()}


def permutation_from_pairs(groups,mask,labels):
    need(len(groups)==7 and set(groups)==set(range(7)) and all(type(x) is int for x in groups),'group permutation')
    need(set(groups[:4])==set(range(4)) and set(groups[4:])==set(range(4,7)),'designated4plus3 partition')
    need(type(mask) is int and 0<=mask<128,'seven-bit sign mask')
    # Independent construction from images of the two vertices of each edge.
    inner=[]
    for symbol in range(14):
        group,side=divmod(symbol,2)
        inner.append(2*groups[group]+((side+((mask>>group)&1))%2))
    outer_index={frozenset(pair):i+15 for i,pair in enumerate(labels)}
    p=[0]+[symbol+1 for symbol in inner]
    p.extend(outer_index[frozenset((inner[a],inner[b]))] for a,b in labels)
    need(set(p)==set(range(99)) and len(p)==99,'induced full99 bijection')
    return p


def forward_clause(clause,edge_map):
    need(all(type(x) is int and x!=0 and abs(x) in edge_map for x in clause),'source literal alphabet')
    need(len({abs(x) for x in clause})==len(clause),'distinct literal variables')
    return sorted(((1 if x>0 else -1)*edge_map[abs(x)] for x in clause),key=abs)


def map_check(record,known,labels,mapping,pairs,source_clause,groups):
    p=record['full99']
    need(len(p)==99 and all(type(x) is int for x in p) and set(p)==set(range(99)),'saved full99 permutation')
    index=record['proposal_index'];need(type(index) is int and 0<=index<len(groups)*128,'proposal index')
    need(record['group_permutation']==list(groups[index//128]) and record['sign_mask']==index%128,'proposal metadata')
    need(p==permutation_from_pairs(record['group_permutation'],record['sign_mask'],labels),'permutation versus pair metadata')
    need(all(known[u][v]==known[p[u]][p[v]] for u in range(99) for v in range(99)),'full99 fixed/free preservation')
    edge_map={variable:pairs[tuple(sorted((p[u],p[v])))] for variable,(u,v) in mapping.items()}
    need(set(edge_map.values())==set(range(1,2161)),'free-variable image bijection')
    need(record['edge_variable_map']==[edge_map[i] for i in range(1,2161)] and all(type(x) is int for x in record['edge_variable_map']),'saved edge images')
    image=forward_clause(source_clause,edge_map)
    need(record['transported_clause']==image,'every signed clause image')
    return image


def check_rejection(record,p,known):
    need(record['accepted'] is False,'rejection state')
    witness=record['first_fixed_edge_violation']
    need(len(witness)==6 and all(type(x) is int for x in witness),'exact rejection witness')
    u,v,old,a,b,new=witness
    need(0<=u<v<99 and (a,b)==(p[u],p[v]),'rejection edge images')
    need(old==known[u][v]==1 and new==known[a][b] and new!=1,'actual fixed-present mismatch')
    first=next((x,y,1,p[x],p[y],known[p[x]][p[y]]) for x,y in combinations(range(99),2)
               if known[x][y]==1 and known[p[x]][p[y]]!=1)
    need(witness==list(first),'first present-edge mismatch metadata')


def controls(identity,known,labels,mapping,pairs,source_clause,groups,rejection):
    map_check(identity,known,labels,mapping,pairs,source_clause,groups)
    rejected=[]
    for label in ('duplicate_vertex','wrong_group_metadata','wrong_sign_metadata','nonpreserving_pair_flip','wrong_edge_image',
                  'wrong_literal_sign','removed_literal','duplicate_literal'):
        bad=deepcopy(identity)
        if label=='duplicate_vertex':bad['full99'][1]=bad['full99'][2]
        elif label=='wrong_group_metadata':bad['group_permutation'][0],bad['group_permutation'][1]=1,0
        elif label=='wrong_sign_metadata':bad['sign_mask']=1
        elif label=='nonpreserving_pair_flip':
            bad['proposal_index']=1;bad['sign_mask']=1;bad['full99']=permutation_from_pairs(groups[0],1,labels)
        elif label=='wrong_edge_image':bad['edge_variable_map'][0],bad['edge_variable_map'][1]=2,1
        elif label=='wrong_literal_sign':bad['transported_clause'][0]*=-1
        elif label=='removed_literal':bad['transported_clause'].pop()
        else:bad['transported_clause'].append(bad['transported_clause'][0])
        try:map_check(bad,known,labels,mapping,pairs,source_clause,groups)
        except (ValueError,KeyError):rejected.append(label)
        else:raise ValueError('corrupt map accepted: '+label)
    bad=deepcopy(rejection);bad['first_fixed_edge_violation'][-1]=1
    try:check_rejection(bad,permutation_from_pairs(groups[0],1,labels),known)
    except ValueError:rejected.append('false_rejection_witness')
    else:raise ValueError('false rejection witness accepted')
    # A non-involutory toy permutation detects confusing a forward image with
    # its inverse. Literal truth is checked under every assignment of K3 edges.
    toy_edges={1:(0,1),2:(0,2),3:(1,2)};toy_pairs={pair:v for v,pair in toy_edges.items()};p=[1,2,0]
    edge_map={v:toy_pairs[tuple(sorted((p[a],p[b])))] for v,(a,b) in toy_edges.items()}
    need(forward_clause([-1,2],edge_map)==[1,-3],'forward3cycle positive fixture')
    for bits in product((0,1),repeat=3):
        old=any(bits[edge_map[abs(x)]-1]==int(x>0) for x in (-1,2))
        image=any(bits[abs(x)-1]==int(x>0) for x in (1,-3))
        need(old==image,'truth transport across forward3cycle')
    return dict(identity_map_passed=True,noninvolutory_forward_cycle_assignments=8,corruptions_rejected=rejected)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();need(not args.out.exists(),'refuse overwrite');bindings={}
    def bind(path,expected=None):
        h=digest(path);need(expected is None or h==expected,'input hash: '+str(path));bindings[key(path)]=h;return Path(path)
    def read(path,expected=None):return parse(bind(path,expected).read_bytes())
    gate=read(GATE,GATE_SHA);encoding=read(ENCODING,ENCODING_SHA)
    need(gate['status']=='INDEPENDENT_FULL99_GRAM_BOOLEAN_BOX_NOGOOD_PASS' and encoding['status']=='INDEPENDENT_EIGHT_FULL99_CNF_ENCODING_PASS','exact source gates')
    for source in (gate,encoding):
        for name,value in source['inputs_sha256'].items():bind(ROOT/name,value)
    model=read(MODEL,MODEL_SHA)
    scope=read(ROOT/model['scope_path'],model['scope_sha256'])
    known,labels,mapping,pairs=reconstruct(model,scope)
    source_clause=gate['verified_clause'];need(len(source_clause)==44,'source44clause')
    manifest=read(args.run/'manifest.json','37767d91e604bfe1c629008952717183ab785bd8b8fb3bae845831c2fb81a327')
    summary=read(args.run/'summary.json','72f3c66c52d06aeaa6dab6ade8dff32bf0fd1299423020170684c0483e5fa862')
    for name,value in manifest['inputs_sha256'].items():bind(ROOT/name,value)
    for name,record in summary['outputs'].items():
        path=bind(args.run/name,record['sha256']);need(path.stat().st_size==record['bytes'],'saved output size')
    groups=[a+b for a in permutations(range(4)) for b in permutations(range(4,7))]
    need(len(groups)==144 and manifest['group_permutations']==list(map(list,groups)) and manifest['proposed_maps']==18432,'complete144by128 finite proposal universe')
    accepted=read(args.run/'accepted_maps.json','45345528697af91aa48846018bc86acbf725932369159ffa4591105efb486b3b')
    image_records=read(args.run/'images.json');unique=read(args.run/'unique_clauses.json')
    attempts_path=bind(args.run/'attempts.jsonl','0d71acd040f989e3d0a828f9471c993f9647ac56063f5752f11a910812bf0939')
    attempts=[parse(line) for line in attempts_path.read_bytes().splitlines()]
    need(len(attempts)==18432 and all(row['index']==i and type(row['index']) is int for i,row in enumerate(attempts)),'every proposal exactly once and ordered')
    need(all(row['id']==i for i,row in enumerate(accepted)),'accepted map IDs')
    calibration=controls(accepted[0],known,labels,mapping,pairs,source_clause,groups,attempts[1])
    accepted_indices=[];rejection_count=0
    for i,record in enumerate(attempts):
        p=permutation_from_pairs(groups[i//128],i%128,labels)
        if record['accepted'] is True:
            map_id=record['accepted_map_id'];need(type(map_id) is int and 0<=map_id<len(accepted),'accepted map reference')
            need(accepted[map_id]['proposal_index']==i and accepted[map_id]['full99']==p,'accepted proposal coverage')
            accepted_indices.append(i)
        else:
            check_rejection(record,p,known);rejection_count+=1
    need(accepted_indices==[record['proposal_index'] for record in accepted],'no unattempted accepted map')
    clauses=[]
    for record in accepted:
        image=map_check(record,known,labels,mapping,pairs,source_clause,groups);clauses.append(image)
        need(type(record['exact_box_upper']) is int and record['exact_box_upper']==gate['exact_boolean_box_upper_bound'],'transport bound invariant')
    expected_unique=[];expected_images=[];by_clause={}
    for index,clause in enumerate(clauses):
        marker=tuple(clause)
        if marker not in by_clause:
            by_clause[marker]=len(expected_unique);expected_unique.append(dict(id=len(expected_unique),clause=clause,map_ids=[]))
        uid=by_clause[marker];expected_unique[uid]['map_ids'].append(index)
        expected_images.append(dict(map_id=index,unique_clause_id=uid))
    need(unique==expected_unique and image_records==expected_images,'complete clause images and deduplication')
    raw_clauses=[]
    for line in (args.run/'clauses.cnfpart').read_text(encoding='ascii').splitlines():
        ints=list(map(int,line.split()));need(ints and ints[-1]==0,'raw clause terminator');raw_clauses.append(ints[:-1])
    need(raw_clauses==[row['clause'] for row in expected_unique],'complete raw clause artifact')
    counts=dict(proposed_population=len(groups)*128,attempted_proposals=len(attempts),unattempted_proposals=0,
                accepted_maps=len(accepted),distinct_maps=len({tuple(row['full99']) for row in accepted}),rejected_proposals=rejection_count,
                signed_clause_attempts=len(clauses),unique_clauses=len(unique),duplicate_clause_images=len(clauses)-len(unique))
    need(all(summary[name]==value for name,value in counts.items()),'summary populations from raw records')
    need(summary['cap_hit'] is False and summary['identity_retained'] is True and summary['source_clause']==source_clause,'summary stage metadata')
    need(len(accepted)==1 and accepted[0]['full99']==list(range(99)) and unique[0]['clause']==source_clause,'verified identity-only finding')
    for path in (__file__,ROOT/'docs/AUDIT_20260930_EIGHT_FULL99_CLAUSE_TRANSPORT.md',ROOT/'uv.lock'):bind(path)
    need(all(digest(ROOT/name)==value for name,value in bindings.items()),'input stability')
    report=dict(status='INDEPENDENT_EIGHT_FULL99_PAIR_RELABELING_TRANSPORT_PASS',claim_id='C-PARTIAL-K-EIGHT-SIGNED-PAIR-RELABELING-CENSUS',claim_revision=1,
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent finite-universe reconstruction, exact mismatch witnesses, complete accepted raw99/2160variable/44literal checks',
        recommendation='VERIFIED',kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],
        statement='Among all18432signed-pair relabelings formed by permutations of groups0..3 and4..6 with independent flips of seven pairs, exactly the identity preserves the recorded eight-coordinate family. Its sole44literal transported clause equals the already independently verified source clause; no additional unique clause is produced.',
        scope='Exhaustive only within this explicit4! times3! times2^7 finite proposal population; not all99vertex permutations or target automorphisms.',
        assumptions=['Frozen120fixedK/2160free full99 family and exact prior source-clause verification.',
                     'Candidate group permutations preserve the designated4plus3 partition; no claim that all family relabelings must have that form.'],
        dependencies=[dict(id='C-PARTIAL-K-EIGHT-COORDINATE-FULL99-SAT-ENCODING',revision=1,relation='encoding_equivalence'),
                      dict(id='C-PARTIAL-K-EIGHT-FULL99-W81-GRAM-BOX-NOGOOD',revision=1,relation='uses_result')],
        inputs_sha256=bindings,controls=calibration,counts=counts,
        accepted_raw_matrix_entries_checked=99*99*len(accepted),accepted_variable_images_checked=2160*len(accepted),
        checked_rejection_witnesses=rejection_count,rejection_witness_kind='Lexicographically first fixed-present edge whose image is not fixed-present',
        universe_coverage_argument='Every group permutation is one of all4! permutations of0..3 concatenated with one of all3! permutations of4..6; all128 flip masks are represented exactly once. Distinct group/flip choices have distinct14inner images. Every resulting proposal has either a fully checked accepted map or a concrete independently checked preservation violation.',
        accepted_proposal_indices=accepted_indices,unique_verified_clauses=[row['clause'] for row in unique],
        source_clause_gate_sha256=GATE_SHA,source_clause_sha256=gate['clause_sha256'],
        extra_unique_clauses_beyond_source=0,full99_transport_derivation='docs/AUDIT_20260930_EIGHT_FULL99_CLAUSE_TRANSPORT.md',
        source_and_image_exact_box_upper=gate['exact_boolean_box_upper_bound'],
        producer_imported=False,shared_components=['Python standard library exact integers; no producer or checking implementation imported',
            'Hash-bound earlier independent full99 encoding and44literal source-clause gate reused, not replayed here'],
        limitations=['No claim of a census of arbitrary99vertex permutations, or nontrivial automorphism of a target.',
                     'No auxiliary-variable/clause permutation of the raw CNF is claimed; transport validity follows from adjacency relabeling.',
                     'No additional unique clause, solver result, family exclusion, or target-wide coverage fraction follows.',
                     'No CNF mutation or solver launch was performed.'],
        target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',solver_calls=0)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(status=report['status'],counts=counts,sha256=digest(args.out))))


if __name__=='__main__':main()
