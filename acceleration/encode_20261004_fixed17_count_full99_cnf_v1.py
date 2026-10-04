"""SOURCE ONLY: full99 CNF for one qualified fixed17 integer count profile."""
import argparse
import ast
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem+"_spec.md")
ENCODER_PATH = "acceleration/theory_20260930_eight_full99_cnf.py"
ENCODER_SHA = "21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c"
MAX_JSON = 64*1024*1024
MAX_CNF = 4*1024*1024*1024
SOFTWARE = {
    "acceleration/command_deadline.py":"9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command.py":"593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a",
    "pyproject.toml":"273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock":"a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
    ENCODER_PATH:ENCODER_SHA,
}
COUNT_BASE = "acceleration/results/20261004_fixed17_integer_type_counts01/"
COUNT_PINS = {
    COUNT_BASE+"summary.json":"857dc4a986cf509e697bc61c79562adeec3f561aab827a6e54ad0dbe2e660ab3",
    COUNT_BASE+"exact_integer_candidate.json":"133097b6174aa1a4b1d327b5c72a727f8ad1ac6daeef0654b117a5f8b88de5b5",
    COUNT_BASE+"parsed_fixed_input.json":"cfe5003a2bd0ad4b2b979264c6e6d1648dc3cd67d1ebc03226d44998371b1248",
}
CAL_STATUS = "FIXED17_COUNT_FULL99_CNF_V1_AUTHOR_CONTROLS_PASS"
SCREEN_STATUS = "INDEPENDENT_FIXED17_COUNT_NEIGHBOR_CAPACITY_V1_COMPLETE_PASS"
CONTROL_COUNTS = dict(positive=7, negative=22, total=29)


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k],b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x,y) for x,y in zip(a,b))
    return a == b


def tick(deadline):
    return budget(deadline.status())


def budget(raw):
    need(type(raw) is dict and raw.get("stop_required") is False
         and type(raw.get("remaining_seconds")) in (int,float)
         and math.isfinite(raw["remaining_seconds"]) and raw["remaining_seconds"] > 20,"SAVE_RESERVE")
    return raw


def safe(raw):
    need(type(raw) is str and raw and "\x00" not in raw,"PATH_STRING")
    path = Path(raw)
    path = ROOT/path if not path.is_absolute() else path
    resolved = path.resolve()
    need(resolved.is_relative_to(ROOT),"PATH_SCOPE")
    current = path
    while current != ROOT and current.is_relative_to(ROOT):
        need(not current.is_symlink() and not current.is_junction(),"PATH_LINK")
        current = current.parent
    return resolved


def parse(raw):
    def pairs(items):
        result = {}
        for key,value in items:
            need(key not in result,"JSON_DUPLICATE")
            result[key] = value
        return result
    def constant(_):
        raise ValueError("JSON_NONFINITE")
    return json.loads(raw.decode("utf8"),object_pairs_hook=pairs,parse_constant=constant)


class Reader:
    def __init__(self,deadline):
        self.deadline,self.pins = deadline,{}

    def read(self,raw,expected,mode="json"):
        need(type(expected) is str and re.fullmatch("[0-9a-f]{64}",expected),"SHA256_STRING")
        path = safe(raw)
        need(path.is_file() and path.stat().st_size <= MAX_JSON,"INPUT_BOUND")
        key = path.relative_to(ROOT).as_posix()
        need(key not in self.pins or self.pins[key] == expected,"PIN_CONFLICT")
        digest,blocks,size = hashlib.sha256(),[],0
        with path.open("rb") as handle:
            while True:
                tick(self.deadline)
                block = handle.read(1024*1024)
                if not block:
                    break
                size += len(block)
                need(size <= MAX_JSON,"INPUT_BOUND")
                digest.update(block)
                if mode != "hash":
                    blocks.append(block)
        need(digest.hexdigest() == expected,"INPUT_HASH")
        self.pins[key] = expected
        tick(self.deadline)
        return parse(b"".join(blocks)) if mode == "json" else b"".join(blocks) if mode == "raw" else None

    def mapping(self,pins):
        need(type(pins) is dict and pins,"INPUT_MAP")
        for path,digest in pins.items():
            self.read(path,digest,"hash")

    def closing(self):
        self.mapping(dict(self.pins))


def write(path,value,deadline):
    tick(deadline)
    raw = (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n").encode("utf8")
    need(len(raw) <= MAX_JSON,"OUTPUT_JSON_BOUND")
    temporary = path.with_suffix(path.suffix+".tmp")
    tick(deadline)
    with temporary.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    tick(deadline)
    os.replace(temporary,path)
    tick(deadline)


def helpers(reader):
    # Execute only the exact authenticated logical helper nodes, not historical imports,
    # main(), ResourceCap(), file readers, old120s launcher or graph-validator code.
    raw = reader.read(ENCODER_PATH,ENCODER_SHA,"raw")
    tree = ast.parse(raw.decode("utf8"),filename=ENCODER_PATH)
    names = ("negate","Clauses","Encoder")
    nodes = [node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names]
    need([node.name for node in nodes] == list(names),"ENCODER_HELPER_NODES")
    selected = ast.Module(body=nodes,type_ignores=[])
    namespace = {"__name__":"frozen_count_lift_threshold_helpers"}
    tick(reader.deadline)
    exec(compile(selected,ENCODER_PATH,"exec"),namespace)
    tick(reader.deadline)
    return namespace["Clauses"],namespace["Encoder"]


def profile(raw):
    need(type(raw) is dict and set(raw) == {"target_order","target_degree","support_adjacency",
         "ordered_masks","counts","pair_bits"},"PROFILE_FIELDS")
    order,degree,h = raw["target_order"],raw["target_degree"],raw["support_adjacency"]
    need(type(order) is int and type(degree) is int and 0 <= degree < order <= 99,"TARGET_DOMAIN")
    need(type(h) is list and 1 <= len(h) < order and all(type(row) is list and len(row) == len(h) for row in h),"GRAPH_SHAPE")
    m = len(h)
    need(all(type(x) is int and x in (0,1) for row in h for x in row)
         and all(h[u][u] == 0 and h[u][v] == h[v][u] for u in range(m) for v in range(m)),"GRAPH_DOMAIN")
    masks,counts = raw["ordered_masks"],raw["counts"]
    need(type(masks) is list and masks and all(type(x) is int and 0 <= x < 1 << m for x in masks),"MASK_DOMAIN")
    need(masks == sorted(set(masks)),"MASK_ORDER")
    need(type(counts) is list and len(counts) == len(masks),"COUNT_SHAPE")
    need(all(type(x) is int for x in counts),"COUNT_INTEGER")
    need(all(0 <= x <= order-m for x in counts) and sum(counts) == order-m,"COUNT_TOTAL")
    table = raw["pair_bits"]
    n = len(masks)
    need(type(table) is list and len(table) == n*(n+1)//2,"PAIR_POPULATION")
    lookup = {}
    for row,(i,j) in zip(table,itertools.combinations_with_replacement(range(n),2)):
        need(type(row) is dict and set(row) == {"i","j","bits"}
             and type(row["i"]) is int and type(row["j"]) is int and [row["i"],row["j"]] == [i,j],"PAIR_COORDINATES")
        bits = row["bits"]
        need(type(bits) is list and all(type(x) is int and x in (0,1) for x in bits) and bits == sorted(set(bits)),"PAIR_BITS")
        lookup[i,j] = bits
    labels = [[i,c] for i,n in enumerate(counts) for c in range(n)]
    b = [[(masks[i] >> u) & 1 for i,_ in labels] for u in range(m)]
    need(all(sum(h[u])+sum(b[u]) == degree for u in range(m))
         and all(sum(h[u][k]*h[v][k] for k in range(m))+sum(b[u][x]*b[v][x] for x in range(len(labels)))
             +h[u][v] == 2 for u,v in itertools.combinations(range(m),2)),"FIXED_SUPPORT_MOMENTS")
    return h,masks,labels,b,lookup


def screen_gate(raw,required):
    need(type(raw) is dict and raw.get("status") == SCREEN_STATUS and type(raw.get("implementation_version")) is int
         and raw["implementation_version"] == 1 and raw.get("producer") == "/root/checkpoint_audit"
         and raw.get("verifier") == "/root/native_driver" and raw.get("method") == "independent_artifact_check"
         and raw.get("target_resolution") == "NONE","SCREEN_GATE_HEADER")
    need(type(raw.get("inputs_sha256")) is dict and all(raw["inputs_sha256"].get(p) == digest for p,digest in required.items()),"SCREEN_GATE_PINS")
    scope = raw.get("outcome")
    expected = dict(outside_copies=82,positive_types=68,q_per_positive_type=834,complete_q_rows=56712,failed_positive_types=0)
    need(type(scope) is dict and all(type(scope.get(k)) is int and scope[k] == value for k,value in expected.items()),"SCREEN_GATE_SCOPE")
    # A correct complete checker can certify a failed screen packet. Building requires an all-pass packet separately.
    need(scope.get("all_screens_pass") is True,"SCREEN_NOT_ALL_PASS")


class Cap:
    def __init__(self,deadline):
        self.deadline = deadline

    def check(self):
        tick(self.deadline)


class Sink:
    def __init__(self,path):
        self.handle,self.bytes = path.open("xb"),0

    def write(self,raw):
        self.bytes += len(raw)
        need(self.bytes <= MAX_CNF,"CNF_BYTE_BOUND")
        self.handle.write(raw)

    def close(self):
        self.handle.flush()
        os.fsync(self.handle.fileno())
        self.handle.close()


def encoder_with_trace(base,top,clauses,enabled):
    class Traced(base):
        def __init__(self):
            super().__init__(top,clauses)
            self.trace,self.seen = [],set()

        def record(self,old,ref,kind,args):
            if enabled and self.top > old and type(ref) is int and ref not in self.seen:
                self.trace.append([ref,kind,args])
                self.seen.add(ref)
            return ref

        def conjunction(self,a,b):
            old = self.top
            return self.record(old,super().conjunction(a,b),"and",[a,b])

        def disjunction(self,a,b):
            old = self.top
            return self.record(old,super().disjunction(a,b),"or",[a,b])

        def recurrence(self,a,b,c):
            old = self.top
            return self.record(old,super().recurrence(a,b,c),"threshold",[a,b,c])
    return Traced()


def build(raw,deadline,logical,out=None,trace=False):
    h,masks,labels,b,lookup = profile(raw)
    m,n = len(h),len(labels)
    d = [[False]*n for _ in range(n)]
    base_edges,top = [],0
    for x,y in itertools.combinations(range(n),2):
        tick(deadline)
        i,j = sorted((labels[x][0],labels[y][0]))
        bits = lookup[i,j]
        need(bits,"PAIR_EMPTY_COPIES")
        if len(bits) == 1:
            ref = bool(bits[0])
        else:
            top += 1
            ref = top
        d[x][y] = d[y][x] = ref
        base_edges.append(dict(x=x,y=y,reference=ref,type_i=i,type_j=j,allowed_bits=bits))
    tick(deadline)
    sink = Sink(out/"clauses.body.part") if out is not None else None
    clause_class,encoder_class = logical
    clauses = clause_class(stream=sink,cap=Cap(deadline))
    encoder = encoder_with_trace(encoder_class,top,clauses,trace)
    groups,part,group_count,part_count = [],[],0,0
    def flush():
        nonlocal part,part_count
        if out is not None and part:
            write(out/("counter_part_%03d.json" % part_count),dict(schema="FIXED_COUNT_FULL99_COUNTER_PART_V1",
                index=part_count,first_group=group_count-len(part),stop_group=group_count,groups=part),deadline)
            write(out/("checkpoint_%03d.json" % part_count),dict(completed_groups=group_count,
                variables=encoder.top,clauses=clauses.count,deadline=deadline.status()),deadline)
            part_count += 1
            part = []
    def equality(refs,value,annotation):
        nonlocal group_count
        tick(deadline)
        need(type(value) is int and all(type(x) is bool or type(x) is int and x > 0 for x in refs),"COUNTER_REFERENCES")
        bound = value-sum(x is True for x in refs)
        inputs = [x for x in refs if type(x) is int]
        need(len(inputs) == len(set(inputs)),"COUNTER_DUPLICATE_INPUT")
        if not 0 <= bound <= len(inputs):
            first = clauses.count+1
            clauses.emit(False)
            result = dict(**annotation,inputs=inputs,bound=bound,equality=True,states=[],
                impossible_constant_bound=True,first_clause=first,clause_count=1)
        else:
            result = encoder.counter(inputs,bound,True,annotation)
            result["impossible_constant_bound"] = False
        result["group_index"],result["original_required_sum"],result["fixed_true_terms"] = group_count,value,sum(x is True for x in refs)
        group_count += 1
        (groups if out is None else part).append(result)
        if out is not None and len(part) == 64:
            flush()
        tick(deadline)
    try:
        for x in range(n):
            equality([d[x][y] for y in range(n) if y != x],raw["target_degree"]-masks[labels[x][0]].bit_count(),dict(kind="degree",x=x))
        for u in range(m):
            for x in range(n):
                equality([d[x][y] for y in range(n) if y != x and b[u][y]],
                    2-b[u][x]-sum(h[u][v]*b[v][x] for v in range(m)),dict(kind="cross",u=u,x=x))
        for x,y in itertools.combinations(range(n),2):
            tick(deadline)
            conjunctions,refs = [],[]
            for z in range(n):
                if z in (x,y):
                    continue
                tick(deadline)
                ref = encoder.conjunction(d[x][z],d[y][z])
                conjunctions.append(dict(z=z,left=d[x][z],right=d[y][z],reference=ref))
                refs.append(ref)
            refs.append(d[x][y])
            intersection = (masks[labels[x][0]] & masks[labels[y][0]]).bit_count()
            equality(refs,2-intersection,dict(kind="outside_cn",x=x,y=y,intersection=intersection,conjunctions=conjunctions))
        flush()
    finally:
        if sink is not None:
            sink.close()
    result = dict(base_variables=top,variables=encoder.top,clauses=clauses.rows,clause_count=clauses.count,
        labelled_copies=labels,base_edges=base_edges,groups=groups if out is None else None,group_count=group_count,
        counter_parts=part_count,trace=encoder.trace if trace else None)
    if out is not None:
        tick(deadline)
        header = ("p cnf %d %d\n" % (encoder.top,clauses.count)).encode("ascii")
        written = len(header)
        with (out/"formula.cnf").open("xb") as destination, (out/"clauses.body.part").open("rb") as body:
            destination.write(header)
            while True:
                tick(deadline)
                block = body.read(1024*1024)
                if not block:
                    break
                written += len(block)
                need(written <= MAX_CNF,"CNF_BYTE_BOUND")
                destination.write(block)
            destination.flush()
            os.fsync(destination.fileno())
        tick(deadline)
        # Only the exact private temporary created by this fresh output root is removed.
        (out/"clauses.body.part").unlink()
        write(out/"variable_map.json",dict(schema="FIXED_COUNT_FULL99_VARIABLE_MAP_V1",base_edges=base_edges,
            labelled_copies=labels,support_size=m,outside_size=n,base_variables=top,variables=encoder.top),deadline)
        write(out/"encoding_outcome.json",{k:v for k,v in result.items() if k not in ("clauses","trace","groups")},deadline)
    tick(deadline)
    return result


def value(ref,assignment):
    return ref if type(ref) is bool else assignment[abs(ref)] if ref > 0 else not assignment[-ref]


def extend(encoded,base):
    need(type(base) is list and len(base) == encoded["base_variables"] and all(type(x) is int and x in (0,1) for x in base),"ASSIGNMENT_DOMAIN")
    assignment = {i+1:bool(x) for i,x in enumerate(base)}
    for ref,kind,args in encoded["trace"]:
        values = [value(a,assignment) for a in args]
        assignment[ref] = all(values) if kind == "and" else any(values) if kind == "or" else values[0] or values[1] and values[2]
    need(len(assignment) == encoded["variables"],"AUXILIARY_EXTENSION_POPULATION")
    return assignment


def dense(raw,encoded,assignment):
    h,masks,labels,b,_ = profile(raw)
    m,n = len(h),len(labels)
    matrix = [[0]*(m+n) for _ in range(m+n)]
    for u in range(m):
        for v in range(m):
            matrix[u][v] = h[u][v]
        for x in range(n):
            matrix[u][m+x] = matrix[m+x][u] = b[u][x]
    for edge in encoded["base_edges"]:
        x,y = edge["x"],edge["y"]
        matrix[m+x][m+y] = matrix[m+y][m+x] = int(value(edge["reference"],assignment))
    return matrix


def validate_matrix(matrix,order,degree):
    """Separate dense-integer oracle; no encoder, threshold state or graph-library calls."""
    need(type(order) is int and type(degree) is int and type(matrix) is list and len(matrix) == order
         and all(type(row) is list and len(row) == order for row in matrix),"MATRIX_SHAPE")
    need(all(type(x) is int and x in (0,1) for row in matrix for x in row),"MATRIX_INTEGER")
    need(all(matrix[u][v] == matrix[v][u] for u in range(order) for v in range(order)),"MATRIX_SYMMETRY")
    need(all(matrix[u][u] == 0 for u in range(order)),"MATRIX_DIAGONAL")
    need(all(sum(row) == degree for row in matrix),"MATRIX_DEGREE")
    products = [[sum(matrix[u][k]*matrix[v][k] for k in range(order)) for v in range(order)] for u in range(order)]
    need(all(products[u][v]+matrix[u][v]-(degree-2)*int(u == v)-2 == 0
             for u in range(order) for v in range(order)),"MATRIX_CN")
    return dict(order=order,degree=degree,complete_integer_products=order*order,products=products,
        simple_symmetric_binary=True,adjacent_CN=1,nonadjacent_CN=2)


def target_matrix(matrix,degree):
    try:
        validate_matrix(matrix,len(matrix),degree)
        return True
    except ValueError:
        return False


def equivalence(raw,encoded,deadline):
    need(encoded["base_variables"] <= 10 and encoded["variables"] <= 1000,"TINY_CONTROL_BOUND")
    rows,sat = [],0
    for index,base in enumerate(itertools.product((0,1),repeat=encoded["base_variables"])):
        tick(deadline)
        assignment = extend(encoded,list(base))
        accepted = all(any(value(lit,assignment) for lit in clause) for clause in encoded["clauses"])
        oracle = target_matrix(dense(raw,encoded,assignment),raw["target_degree"])
        need(accepted == oracle,"FULL_ENCODING_EQUIVALENCE")
        sat += int(accepted)
        rows.append(dict(index=index,base=list(base),formula_accepts=accepted,dense_target=oracle))
    need(sat == 1,"KNOWN_ROOK_UNIQUE_LABELED_WITNESS")
    return dict(full_assignments=len(rows),satisfying_count=sat,rows=rows,solver_calls=0)


def rook(forced=False):
    adjacent = {(0,1),(0,2),(0,3),(0,4),(1,4),(2,3)}
    return dict(target_order=9,target_degree=4,support_adjacency=[[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
        ordered_masks=[0,3,5,10,12],counts=[1]*5,pair_bits=[dict(i=i,j=j,bits=([int((i,j) in adjacent)] if forced and i != j else [0,1]))
        for i,j in itertools.combinations_with_replacement(range(5),2)])


def counter_controls(logical,deadline):
    clauses_class,encoder_class = logical
    rows = []
    for n in range(5):
        for bound in range(n+1):
            for equality in (False,True):
                tick(deadline)
                clauses = clauses_class(cap=Cap(deadline))
                encoder = encoder_class(n,clauses)
                encoder.counter(list(range(1,n+1)),bound,equality,{})
                need(encoder.top-n <= 12,"COUNTER_CONTROL_BOUND")
                accepted = 0
                for base in itertools.product((False,True),repeat=n):
                    tick(deadline)
                    oracle = sum(base) == bound if equality else sum(base) <= bound
                    found = 0
                    for suffix in itertools.product((False,True),repeat=encoder.top-n):
                        assignment = {i+1:x for i,x in enumerate(base+suffix)}
                        found += all(any(value(lit,assignment) for lit in clause) for clause in clauses.rows)
                    need(found == int(oracle),"COUNTER_COMPLETE_EQUIVALENCE")
                    accepted += found
                rows.append(dict(n=n,bound=bound,equality=equality,variables=encoder.top,accepted=accepted))
    return dict(complete_rows=30,rows=rows,unique_auxiliary_extension=True)


def dimacs(path,variables,clauses,deadline):
    rows = []
    need(path.stat().st_size <= MAX_JSON,"TINY_DIMACS_BOUND")
    with path.open("r",encoding="ascii",newline="") as handle:
        tick(deadline)
        need(handle.readline() == "p cnf %d %d\n" % (variables,clauses),"DIMACS_HEADER")
        for line in handle:
            tick(deadline)
            tokens = line.split()
            need(tokens and tokens[-1] == "0" and all(re.fullmatch("-?[1-9][0-9]*",x) for x in tokens[:-1]),"DIMACS_ROW")
            row = [int(x) for x in tokens[:-1]]
            need(all(abs(x) <= variables for x in row),"DIMACS_VARIABLE")
            rows.append(row)
    need(len(rows) == clauses,"DIMACS_CLAUSE_COUNT")
    return rows


def and_controls(raw):
    need(type(raw) is list and all(type(row) is list for row in raw),"AND_FIXTURE")
    for a,b,z in itertools.product((False,True),repeat=3):
        values = {1:a,2:b,3:z}
        accepted = all(any(value(lit,values) for lit in clause) for clause in raw)
        need(accepted == (z == (a and b)),"AND_COMPLETE_EQUIVALENCE")
    return dict(complete_assignments=8)


def controls(out,reader,logical):
    deadline = reader.deadline
    free,forced = rook(),rook(True)
    action = lambda p:equivalence(p,build(p,deadline,logical,trace=True),deadline)
    def streamed_action(payload):
        encoded = build(payload,deadline,logical,out,trace=True)
        encoded["clauses"] = dimacs(out/"formula.cnf",encoded["variables"],encoded["clause_count"],deadline)
        encoded["groups"] = []
        for i in range(encoded["counter_parts"]):
            tick(deadline)
            raw = parse((out/("counter_part_%03d.json" % i)).read_bytes())
            encoded["groups"] += raw["groups"]
        need(len(encoded["groups"]) == encoded["group_count"],"STREAM_GROUP_POPULATION")
        return equivalence(payload,encoded,deadline)
    gate = dict(status=SCREEN_STATUS,implementation_version=1,producer="/root/checkpoint_audit",verifier="/root/native_driver",
        method="independent_artifact_check",target_resolution="NONE",inputs_sha256={"synthetic":"0"*64},
        outcome=dict(outside_copies=82,positive_types=68,q_per_positive_type=834,complete_q_rows=56712,
            failed_positive_types=0,all_screens_pass=True))
    gatecheck = lambda p:screen_gate(p,{"synthetic":"0"*64})
    routes = [("known_rook_streamed_full_1024_base_assignments","PASS",free,streamed_action),
        ("known_rook_forced_pair_zero_base_variables","PASS",forced,action),
        ("counter_complete_30_tiny_truth_tables","PASS",dict(n_max=4),lambda p:counter_controls(logical,deadline)),
        ("bidirectional_and_complete_truth_table","PASS",[[1,-3],[2,-3],[-1,-2,3]],and_controls),
        ("genuine_shaped_allpass_screen_header","PASS",gate,gatecheck),
        ("budget_above_save_reserve","PASS",dict(stop_required=False,remaining_seconds=20.000001),budget)]
    full_rook = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    matrixcheck = lambda p:validate_matrix(p,9,4)
    routes.append(("known_valid_full_rook9_integer_matrix","PASS",full_rook,matrixcheck))
    def mutate(name,stage,original,change,check=action):
        p = copy.deepcopy(original)
        change(p)
        routes.append((name,stage,p,check))
    mutate("count_bool","COUNT_INTEGER",free,lambda p:p["counts"].__setitem__(0,True))
    mutate("count_float","COUNT_INTEGER",free,lambda p:p["counts"].__setitem__(0,1.0))
    mutate("count_wrong_total","COUNT_TOTAL",free,lambda p:p["counts"].__setitem__(0,0))
    mutate("mask_bool","MASK_DOMAIN",free,lambda p:p["ordered_masks"].__setitem__(0,False))
    mutate("mask_order","MASK_ORDER",free,lambda p:p["ordered_masks"].reverse())
    mutate("graph_bool","GRAPH_DOMAIN",free,lambda p:p["support_adjacency"][0].__setitem__(0,False))
    mutate("pair_bool","PAIR_BITS",free,lambda p:p["pair_bits"][0].__setitem__("bits",[False,1]))
    mutate("empty_bit_between_distinct_positive_copies","PAIR_EMPTY_COPIES",free,lambda p:p["pair_bits"][1].__setitem__("bits",[]))
    mutate("complete_failed_screen_not_a_build_premise","SCREEN_NOT_ALL_PASS",gate,lambda p:p["outcome"].__setitem__("all_screens_pass",False),gatecheck)
    mutate("screen_bool_implementation","SCREEN_GATE_HEADER",gate,lambda p:p.__setitem__("implementation_version",True),gatecheck)
    routes.append(("and_missing_reverse_clause","AND_COMPLETE_EQUIVALENCE",[[1,-3],[2,-3]],and_controls))
    encoded = build(free,deadline,logical,trace=True)
    badunit = copy.deepcopy(encoded)
    first = badunit["groups"][0]
    index = first["first_clause"]+first["clause_count"]-2
    need(len(badunit["clauses"][index]) == 1,"CORRUPT_UNIT_CONTROL_LOCATION")
    badunit["clauses"][index] = [-badunit["clauses"][index][0]]
    def known_witness(p):
        adjacent = {(0,1),(0,2),(0,3),(0,4),(1,4),(2,3)}
        base = [int((edge["x"],edge["y"]) in adjacent) for edge in p["base_edges"]]
        assignment = extend(p,base)
        need(target_matrix(dense(free,p,assignment),4),"KNOWN_WITNESS_MATRIX")
        need(all(any(value(lit,assignment) for lit in clause) for clause in p["clauses"]),"KNOWN_WITNESS_CLAUSE")
    routes.append(("equality_unit_sign_corruption","KNOWN_WITNESS_CLAUSE",badunit,known_witness))
    deleted = copy.deepcopy(encoded)
    remove = set()
    for group in deleted["groups"]:
        if group["kind"] in ("cross","outside_cn"):
            remove.update(i for i in range(group["first_clause"]-1,group["first_clause"]+group["clause_count"]-1)
                          if len(deleted["clauses"][i]) <= 1)
    deleted["clauses"] = [row for i,row in enumerate(deleted["clauses"]) if i not in remove]
    routes.append(("common_neighbor_assertions_deleted","FULL_ENCODING_EQUIVALENCE",deleted,lambda p:equivalence(free,p,deadline)))
    routes.append(("budget_at_save_reserve","SAVE_RESERVE",dict(stop_required=False,remaining_seconds=20),budget))
    routes.append(("budget_review_stop","SAVE_RESERVE",dict(stop_required=True,remaining_seconds=100),budget))
    mutate("full_matrix_shape","MATRIX_SHAPE",full_rook,lambda p:p.pop(),matrixcheck)
    mutate("full_matrix_bool","MATRIX_INTEGER",full_rook,lambda p:p[0].__setitem__(0,False),matrixcheck)
    mutate("full_matrix_float","MATRIX_INTEGER",full_rook,lambda p:p[0].__setitem__(1,1.0),matrixcheck)
    mutate("full_matrix_asymmetric","MATRIX_SYMMETRY",full_rook,lambda p:p[0].__setitem__(1,0),matrixcheck)
    mutate("full_matrix_diagonal","MATRIX_DIAGONAL",full_rook,lambda p:p[0].__setitem__(0,1),matrixcheck)
    def erase_edge(p):
        p[0][1] = p[1][0] = 0
    mutate("full_matrix_degree","MATRIX_DEGREE",full_rook,erase_edge,matrixcheck)
    circulant = [[int((j-i)%9 in (1,2,7,8)) for j in range(9)] for i in range(9)]
    routes.append(("full_matrix_regular_but_wrong_CN","MATRIX_CN",circulant,matrixcheck))
    need(len(routes) == CONTROL_COUNTS["total"] and sum(expected == "PASS" for _,expected,_,_ in routes) == CONTROL_COUNTS["positive"],"CONTROL_DECLARATION")
    table,mismatches = [],[]
    for index,(name,expected,payload,check) in enumerate(routes):
        tick(deadline)
        write(out/("control_%02d_%s.json" % (index,name)),payload,deadline)
        result = None
        try:
            result,actual = check(payload),"PASS"
        except (ValueError,AssertionError) as exc:
            actual = str(exc) if isinstance(exc,ValueError) else "ENCODER_ASSERTION"
        row = dict(index=index,name=name,expected_stage=expected,actual_stage=actual,matches=expected == actual)
        table.append(row)
        if expected != actual:
            mismatches.append(row)
        if result is not None:
            write(out/("result_%02d.json" % index),result,deadline)
    write(out/"controls.json",table,deadline)
    need(not mismatches,"AUTHOR_CONTROL_STAGE_MISMATCH")
    return dict(counts=CONTROL_COUNTS,stage_mismatches=mismatches,table=table,
        source_helper_nodes_only=True,actual_fixed17_count_read=False,solver_calls=0)


def scientific(reader,config,out,logical):
    need(type(config) is dict and config.get("schema") == "FIXED17_COUNT_FULL99_CNF_CONFIGURATION_V1"
         and type(config.get("inputs_sha256")) is dict,"CONFIGURATION_HEADER")
    need(all(config["inputs_sha256"].get(path) == digest for path,digest in COUNT_PINS.items()),"COUNT_DIRECT_PINS")
    reader.mapping(config["inputs_sha256"])
    cal = reader.read(config["author_calibration_path"],config["author_calibration_sha256"])
    need(type(cal) is dict and cal.get("status") == CAL_STATUS and cal.get("mode") == "calibrate"
         and cal.get("producer") == "/root/checkpoint_audit" and cal.get("independent_approval") is False
         and same(cal.get("outcome",{}).get("counts"),CONTROL_COUNTS)
         and cal["outcome"].get("stage_mismatches") == []
         and type(cal.get("source_software")) is dict
         and cal["source_software"].get(SELF.relative_to(ROOT).as_posix()) == config["inputs_sha256"].get(SELF.relative_to(ROOT).as_posix())
         and cal["source_software"].get(SPEC.relative_to(ROOT).as_posix()) == config["inputs_sha256"].get(SPEC.relative_to(ROOT).as_posix()),"AUTHOR_CALIBRATION")
    gate = reader.read(config["screen_gate_path"],config["screen_gate_sha256"])
    required = {**COUNT_PINS,config["screen_parsed_input_path"]:config["screen_parsed_input_sha256"]}
    screen_gate(gate,required)
    raw = reader.read(config["screen_parsed_input_path"],config["screen_parsed_input_sha256"])
    count = reader.read(COUNT_BASE+"exact_integer_candidate.json",COUNT_PINS[COUNT_BASE+"exact_integer_candidate.json"])
    parsed = reader.read(COUNT_BASE+"parsed_fixed_input.json",COUNT_PINS[COUNT_BASE+"parsed_fixed_input.json"])
    need(same(raw.get("ordered_masks"),count.get("ordered_masks")) and same(raw.get("counts"),count.get("counts"))
         and same(raw.get("support_adjacency"),parsed.get("induced_adjacency"))
         and type(raw.get("target_order")) is int and raw["target_order"] == 99
         and type(raw.get("target_degree")) is int and raw["target_degree"] == 14
         and len(raw["support_adjacency"]) == 17 and len(raw["ordered_masks"]) == 472,"FIXED_COUNT_SCREEN_PROFILE")
    write(out/"input_profile.json",raw,reader.deadline)
    result = build(raw,reader.deadline,logical,out)
    need(len(result["labelled_copies"]) == 82 and result["group_count"] == 4797,"FULL_CARDINALITY_FAMILIES")
    return {k:v for k,v in result.items() if k not in ("clauses","trace","groups")}


def output_hashes(out,deadline):
    result = {}
    for path in sorted(out.iterdir()):
        tick(deadline)
        need(path.is_file() and not path.is_symlink() and path.suffix not in (".part",".tmp"),"OUTPUT_POPULATION")
        limit = MAX_CNF if path.name == "formula.cnf" else MAX_JSON
        need(path.stat().st_size <= limit,"OUTPUT_FILE_BOUND")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                tick(deadline)
                block = handle.read(1024*1024)
                if not block:
                    break
                digest.update(block)
        result[path.name] = digest.hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",choices=("calibrate","build"))
    for name in ("seconds","out","self-sha256","spec-sha256","executor"):
        parser.add_argument("--"+name,required=True,type=float if name == "seconds" else str)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason="One exact full99 fixed-count CNF encoding or finite new caller qualification; all helpers/inputs/outputs share this deadline")
    out = safe(args.out)
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(),"OUTPUT_FRESH_SCOPE")
    out.mkdir(parents=True)
    reader = Reader(deadline)
    software = {**SOFTWARE,SELF.relative_to(ROOT).as_posix():args.self_sha256,SPEC.relative_to(ROOT).as_posix():args.spec_sha256}
    try:
        reader.mapping(software)
        logical = helpers(reader)
        if args.mode == "calibrate":
            outcome,status = controls(out,reader,logical),CAL_STATUS
        else:
            need(args.configuration is not None and args.configuration_sha256 is not None,"CONFIGURATION_ARGUMENTS")
            outcome = scientific(reader,reader.read(args.configuration,args.configuration_sha256),out,logical)
            status = "CANDIDATE_FIXED17_COUNT_FULL99_CNF_V1"
        reader.closing()
        outputs = output_hashes(out,deadline)
        report = dict(schema="FIXED17_COUNT_FULL99_CNF_PRODUCER_REPORT_V1",status=status,implementation_version=1,
            mode=args.mode,timestamp=datetime.now(timezone.utc).isoformat(),producer="/root/checkpoint_audit",
            source_author="/root/checkpoint_audit",executor_declaration=args.executor,
            executor_identity_requires_external_runtime_receipt=True,independent_approval=False,
            target_resolution="NONE",source_software=software,inputs_sha256=dict(reader.pins),outputs_sha256=outputs,
            command=sys.argv,cwd=str(ROOT),deadline=deadline.status(),outcome=outcome,solver_calls=0,
            actual_fixed17_count_read=args.mode == "build",automatic_retry=False,ledger_index_git_mutations=0,
            shared_components=["Three exact authenticated historical logical helper nodes:negate/Clauses/Encoder; no old imports/main/ResourceCap invoked",
                "Common pinned Python/json/SHA/command_deadline and qualified count/screen/pair premises; old gates do not approve changed caller",
                "ROOT selected the lift direction; Checkpoint new mapping/constraint emitter needs distinct complete equivalence verification"],
            limitations=["One exact count profile on one fixed inducedH; no coverage of all count witnesses or unrestricted target",
                "No solver is launched; completed CNF is a candidate until separate full formula/mapping equivalence checking",
                "SAT requires exact complete99 matrix/assignment validation; UNSAT requires exact formula-bound complete proof replay",
                "Helper truth-table and tiny rook caller controls establish only their actual finite scope",
                "All saved64-counter boundaries persist, but hard kill/exception can lose current unflushed metadata suffix",
                "Deadline guards/OS containment are bounded intent and observed receipts, not hard-real-time services"])
        write(out/"summary.json",report,deadline)
        reader.closing()
        tick(deadline)
        print(json.dumps(dict(status=status,outcome={k:v for k,v in outcome.items() if k not in ("table","rows","base_edges","labelled_copies")})),flush=True)
    except Exception as exc:
        try:
            (out/"failure.json").write_text(json.dumps(dict(status="FAILED_PRESERVED",stage=str(exc),exception=type(exc).__name__,
                timestamp=datetime.now(timezone.utc).isoformat(),encoding_complete=False,automatic_retry=False,
                target_resolution="NONE",deadline=deadline.status()),indent=2,allow_nan=False)+"\n",encoding="utf8")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
