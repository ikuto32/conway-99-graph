"""Independent unrestricted full99 decoded-object and native SAT-output audit.

The frozen conditional checker's pure integer SRG, assignment, JSON and CNF
primitives are reused explicitly. Unrestricted scope and native v-line parsing
are reconstructed here; no producer or solver implementation is imported.
"""
import argparse
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import io
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import audit_20260930_full99_sat_object as common

ROOT,need,digest,key,read,save = common.ROOT,common.need,common.digest,common.key,common.read,common.save
MODEL = ROOT/'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
MODEL_SHA = '77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e'
CNF = MODEL.with_name('instance.cnf')
CNF_SHA = '7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138'
SCOPE = ROOT/'acceleration/results/20260930_unrestricted_full99_preflight_v2/scope.json'
SCOPE_SHA = '2359c7389b4bb23475cf9607a99c07060119976abff8bc70bbdb5d131ab1921d'
GATE = ROOT/'acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json'
GATE_SHA = '2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58'
NORMALIZATION = ROOT/'acceleration/results/20260917_independent_review/root_scaffold.json'
NORMALIZATION_SHA = 'e96941c2bc050aad65b67a4f22a8968d588ae4dbe3cd7b7f22bfe84972a963a8'


def unrestricted_scope(model,scope):
    labels = [(a,b) for left,right in itertools.combinations(range(7),2)
              for a in (2*left,2*left+1) for b in (2*right,2*right+1)]
    a = [[0]*99 for _ in range(99)]
    for i in range(14):
        a[0][i+1] = a[i+1][0] = 1
        a[i+1][(i^1)+1] = 1
    for vertex,(u,v) in enumerate(labels,15):
        a[vertex][u+1] = a[u+1][vertex] = 1
        a[vertex][v+1] = a[v+1][vertex] = 1
    edges = list(itertools.combinations(range(15,99),2))
    for u,v in edges: a[u][v] = a[v][u] = -1
    need(len(edges)==3486,'all outer unordered pairs')
    variables = [dict(id=i+1,u=u,v=v) for i,(u,v) in enumerate(edges)]
    for raw in (model,scope):
        need(raw['known_adjacency_full99']==a and raw['outer_labels']==list(map(list,labels)),'all9801 unrestricted fixed/free entries')
        need(raw['edge_variables']==variables,'all3486 unrestricted edge labels')
        need(raw['branch_units']==[],'no branch units')
    need(scope['fixed_positive_edges']==189 and scope['fixed_outer_edges']==0 and scope['fixed_outer_nonedges']==0 and scope['free_outer_pairs']==3486,'unrestricted scope counts')
    need(scope['automorphism_assumed'] is False and scope['extra_graph_constraints']==[],'no scope symmetry/extra assumptions')
    need(model['fixed_K_edges']==[] and model['fixed_outer_nonedges']==[] and model['target_automorphism_assumed'] is False,'no prescribed outer entries/automorphism')
    need(model['unknown_edges_outer']==[[u-15,v-15] for u,v in edges],'complete outer free-pair inventory')
    need(model['fixed_scaffold_edges']==189 and model['variables']==1186500 and model['clauses']==4136454,'exact model size')
    need(model['scope_path']==key(SCOPE) and model['scope_sha256']==SCOPE_SHA,'scope artifact binding')
    need(model['normalization_dependency']==dict(id='C-ROOT-SCAFFOLD-NORMALIZATION',revision=1),'normalization claim pin')
    need(model['normalization_audit']==key(NORMALIZATION) and model['normalization_audit_sha256']==NORMALIZATION_SHA,'normalization proof artifact')
    return a,edges,dict(full_matrix_entries_checked=9801,free_outer_pairs=3486,fixed_positive_edges=189,
                        fixed_absent_unordered_pairs=1176,fixed_outer_edges=0,fixed_outer_nonedges=0,branch_units=0,target_automorphism_assumed=False)


def native_values(stream,variables):
    """Strict independent native DIMACS status/v-line parser, no producer reuse."""
    status_count=0;terminated=False;count=0;lines=0
    values=bytearray([2])*(variables+1)
    for raw in stream:
        line=raw.decode('ascii').strip()
        if not line: continue
        tokens=line.split()
        if tokens[0]=='c': continue
        if tokens[0]=='s':
            need(status_count==0 and tokens==['s','SATISFIABLE'],'one unique SAT status')
            status_count+=1
        elif tokens[0]=='v':
            need(status_count==1 and not terminated and len(tokens)>1,'model line after SAT and before terminator')
            lines+=1
            for position,token in enumerate(tokens[1:]):
                literal=int(token)
                if literal==0:
                    need(position==len(tokens)-2,'no data after native v0 terminator')
                    terminated=True
                else:
                    need(not terminated and 1<=abs(literal)<=variables,'native variable range')
                    variable=abs(literal)
                    need(values[variable]==2,'native variable assigned once')
                    values[variable]=int(literal>0);count+=1
        else:
            raise ValueError('unexpected non-comment native output: '+tokens[0])
    need(status_count==1 and terminated and count==variables and all(x!=2 for x in values[1:]),'complete native assignment and explicit terminator')
    return values,dict(native_statuses=status_count,native_model_lines=lines,native_assigned_variables=count,native_final_zero=True)


def common_provenance():
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                verifier='/root/state_literature_audit independent checking agent',producer_imported=False,
                shared_components=['Frozen independent conditional checker: generic integer SRG validation, complete signed-assignment validator, raw CNF parser, and six SRG fixtures','Python standard library'],
                external_review=False,artifact_availability='LOCAL_ONLY')


def native_controls(out):
    good=b'c independent synthetic codec control\ns SATISFIABLE\nv 1 -2\nv 3 0\nc done\n'
    values,result=native_values(io.BytesIO(good),3)
    need(values==common.assignment_values([1,-2,3],3),'known raw/JSON assignment agreement')
    rejected=[]
    cases={
        'missing_status':good.replace(b's SATISFIABLE\n',b''),
        'duplicate_status':good+b's SATISFIABLE\n',
        'UNSAT_status':good.replace(b'SATISFIABLE',b'UNSATISFIABLE'),
        'UNKNOWN_status':good.replace(b'SATISFIABLE',b'UNKNOWN'),
        'missing_terminator':good.replace(b'3 0',b'3'),
        'model_after_terminator':good+b'v 1\n',
        'token_after_terminator':good.replace(b'3 0',b'3 0 2'),
        'duplicate_variable':good.replace(b'3 0',b'2 0'),
        'missing_variable':good.replace(b'3 0',b'0'),
        'out_of_range':good.replace(b'3 0',b'4 0'),
        'nonnumeric':good.replace(b'3 0',b'x 0'),
        'unexpected_protocol_line':good+b'done\n'}
    for name,raw in cases.items():
        try: native_values(io.BytesIO(raw),3)
        except ValueError as error: rejected.append(dict(case=name,error=str(error)))
        else: raise ValueError('native corruption accepted: '+name)
    # Same actual sizes as the unrestricted artifacts, but explicitly synthetic
    # all-negative model and repeated negative units: NOT a research SAT witness.
    variables=1186500;clauses=4136454
    path=out/'synthetic_fullsize_native.stdout.txt.gz'
    raw_hash=hashlib.sha256();raw_bytes=0
    with gzip.open(path,'wb',compresslevel=6) as stream:
        def write(raw):
            nonlocal raw_bytes
            stream.write(raw);raw_hash.update(raw);raw_bytes+=len(raw)
        write(b'c SYNTHETIC CODEC CONTROL, NOT RESEARCH SOLVER OUTPUT\ns SATISFIABLE\n')
        for first in range(1,variables+1,512):
            write(('v '+' '.join(str(-x) for x in range(first,min(first+512,variables+1)))+'\n').encode('ascii'))
        write(b'v 0\n')
    with gzip.open(path,'rb') as stream: full_values,full_result=native_values(stream,variables)
    need(full_values[1:]==bytearray(variables),'every fullsize synthetic native value')
    class SyntheticCNF:
        def readline(self): return ('p cnf %d %d\n'%(variables,clauses)).encode('ascii')
        def __iter__(self):
            for i in range(clauses): yield ('-%d 0\n'%(1+i%variables)).encode('ascii')
    cnf_result=common.check_cnf_stream(SyntheticCNF(),full_values,variables,clauses)
    return dict(known_tiny_native=result,corruptions_rejected=rejected,
                fullsize_synthetic_native=full_result,fullsize_synthetic_cnf=cnf_result,
                fullsize_fixture=key(path),fullsize_fixture_sha256=digest(path),uncompressed_bytes=raw_bytes,uncompressed_sha256=raw_hash.hexdigest(),
                fixture_scope='Synthetic codec/parser calibration only, with1186500negative variables and4136454repeated negative unit clauses; not the research CNF or any target witness.',
                fixture_retrieval='Decompress the saved gzip to obtain native-format synthetic stdout. Generate CNF header then clause-(1+i mod1186500) for i=0..4136453, exactly as the saved checker does.')


def calibrate(args):
    args.out.mkdir(parents=True,exist_ok=False)
    generic=common.controls(args.out)
    native=native_controls(args.out)
    pins={MODEL:MODEL_SHA,CNF:CNF_SHA,SCOPE:SCOPE_SHA,GATE:GATE_SHA,NORMALIZATION:NORMALIZATION_SHA}
    for path,expected in pins.items(): need(digest(path)==expected,'exact calibration input pin')
    gate=read(GATE);need(gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','unrestricted encoding gate')
    model,scope=read(MODEL),read(SCOPE)
    a,edges,scope_record=unrestricted_scope(model,scope)
    graph=[row.copy() for row in a]
    for u,v in edges: graph[u][v]=graph[v][u]=0
    save(args.out/'scope_valid_all3486free_zero.json',dict(adjacency_full99=graph,scope_valid=True,target_valid=False))
    try: common.validate_srg(graph,99,14,1,2)
    except ValueError as error: target_rejection=str(error)
    else: raise ValueError('all-free-zero accepted as target')
    rejected=[]
    # Avoid duplicating the large product/prefix metadata: only raw scope fields
    # are copied; the checker under test reads those fields and exact counts.
    required=['known_adjacency_full99','outer_labels','edge_variables','branch_units','fixed_K_edges','fixed_outer_nonedges',
              'target_automorphism_assumed','unknown_edges_outer','fixed_scaffold_edges','variables','clauses','scope_path','scope_sha256','normalization_dependency','normalization_audit','normalization_audit_sha256']
    small={name:model[name] for name in required}
    for name,mutate in [('fixed_outer_edge',lambda m:m['known_adjacency_full99'][15].__setitem__(16,1)),
                        ('fixed_outer_nonedge',lambda m:m['known_adjacency_full99'][15].__setitem__(16,0)),
                        ('missing_free_pair',lambda m:m['edge_variables'].pop()),
                        ('added_branch',lambda m:m['branch_units'].append(1)),
                        ('nontrivial_automorphism_assumed',lambda m:m.__setitem__('target_automorphism_assumed',True)),
                        ('wrong_normalization_revision',lambda m:m['normalization_dependency'].__setitem__('revision',2))]:
        bad=copy.deepcopy(small);mutate(bad)
        try: unrestricted_scope(bad,scope)
        except ValueError as error: rejected.append(dict(case=name,error=str(error)))
        else: raise ValueError('unrestricted scope corruption accepted: '+name)
    inputs={key(path):digest(path) for path in [*pins,Path(__file__),Path(common.__file__),ROOT/'uv.lock']}
    report=common_provenance()
    report.update(status='INDEPENDENT_UNRESTRICTED_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS',inputs_sha256=inputs,
        generic_controls=generic,native_controls=native,scope_check=scope_record,scope_corruptions_rejected=rejected,
        all_free_zero_target_rejection=target_rejection,solver_launched=False,target_resolution=False,
        statement='The independent unrestricted SAT-object checking path is calibrated on six known SRGs, corrupted objects, fullsize synthetic native output/clause streams, and exact raw3486free model scope.',
        limitations=['No known-valid99target fixture exists in this calibration.','Synthetic native/clause controls are not research SAT evidence.','Encoding/normalization equivalence is an independently pinned premise; this checker validates positive raw objects.'])
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))


def check(args):
    start=time.monotonic();args.out.mkdir(parents=True,exist_ok=False);bindings={}
    def pin(path,expected=None):
        path=Path(path)
        if not path.is_absolute(): path=ROOT/path
        value=digest(path);need(expected is None or expected==value,'raw artifact hash '+key(path))
        bindings[key(path)]=value;return path
    def load(path,expected=None): return read(pin(path,expected))
    gate=load(args.encoding_audit,args.encoding_audit_sha256)
    need(gate['status']=='INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS','complete unrestricted encoding gate')
    need(args.encoding_audit_sha256==GATE_SHA,'frozen approved gate')
    model=load(args.model,MODEL_SHA);pin(args.cnf,CNF_SHA)
    authenticated={key(ROOT/name):sha for name,sha in gate['inputs_sha256'].items()}
    for path in (args.model,args.cnf): need(authenticated[key(path)]==digest(path),'encoding gate exact artifact binding')
    scope=load(SCOPE,SCOPE_SHA);pin(NORMALIZATION,NORMALIZATION_SHA)
    a,edges,scope_record=unrestricted_scope(model,scope)
    signed=load(args.assignment)['assignment']
    values=common.assignment_values(signed,model['variables'])
    pin(args.native_output)
    with args.native_output.open('rb') as stream: native,native_record=native_values(stream,model['variables'])
    need(native==values,'all native v-line values equal complete JSON assignment')
    with args.cnf.open('rb') as stream: cnf_record=common.check_cnf_stream(stream,values,model['variables'],model['clauses'])
    graph=[row.copy() for row in a]
    for variable,(u,v) in enumerate(edges,1): graph[u][v]=graph[v][u]=int(values[variable])
    need(all(a[i][j]==-1 or graph[i][j]==a[i][j] for i in range(99) for j in range(99)),'all fixed scaffold entries unchanged')
    if args.decoded is not None:
        need(load(args.decoded)['adjacency_full99']==graph,'producer graph equals independent decode')
    graph_record=common.validate_srg(graph,99,14,1,2)
    graph_path=args.out/'independent_adjacency_full99.json'
    save(graph_path,dict(adjacency_full99=graph,exact_identity='A^2=12I-A+2J',independent_result=graph_record,external_review=False))
    for path in (Path(__file__),Path(common.__file__),ROOT/'uv.lock'): pin(path)
    need(all(digest(ROOT/path)==sha for path,sha in bindings.items()),'stable bound inputs')
    report=common_provenance()
    report.update(status='INDEPENDENT_UNRESTRICTED_TARGET_GRAPH_PASS_PENDING_EXTERNAL_REVIEW',inputs_sha256=bindings,
        native_check=native_record,cnf_check=cnf_record,scope_check=scope_record,graph_check=graph_record,
        graph_path=key(graph_path),graph_sha256=digest(graph_path),target_resolution=True,
        statement='The saved explicit99by99 adjacency is symmetric binary zero-diagonal degree14 and satisfies A^2=12I-A+2J exactly. Its complete native and JSON assignments agree and satisfy every4136454raw clause of the pinned unrestricted encoding.',
        limitations=['Internally independently checked candidate resolution only; external mathematical review remains pending.'],elapsed_seconds=time.monotonic()-start)
    save(args.out/'summary.json',report)
    print(json.dumps(dict(status=report['status'],graph_sha256=digest(graph_path),summary_sha256=digest(args.out/'summary.json'))))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    cal=sub.add_parser('calibrate');cal.add_argument('--out',type=Path,required=True)
    sat=sub.add_parser('sat')
    for name in ('cnf','model','assignment','native-output','encoding-audit','out'): sat.add_argument('--'+name,type=Path,required=True)
    sat.add_argument('--encoding-audit-sha256',required=True);sat.add_argument('--decoded',type=Path)
    args=parser.parse_args();(calibrate if args.command=='calibrate' else check)(args)


if __name__=='__main__': main()
