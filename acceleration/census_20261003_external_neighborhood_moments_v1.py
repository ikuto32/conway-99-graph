"""Producer of exact necessary exterior moments; numerical LP only guides candidates."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
TRIPLES = ((0,1,2),(0,3,4),(0,5,6),(1,7,9),(1,8,10),(15,11,14),
           (16,12,13),(2,15,16),(3,7,11),(4,8,12),(5,9,13),(6,10,14))
SCHEMA = "EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1"


def need(condition, stage):
    if not condition:
        raise ValueError(stage)


def tick(deadline):
    need(not deadline.status()["stop_required"] and deadline.status()["remaining_seconds"] > 30, "SAVE_RESERVE")


def digest(path, deadline):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while True:
            tick(deadline)
            block = stream.read(1024*1024)
            tick(deadline)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def save(path, value, deadline):
    tick(deadline)
    with Path(path).open("x", encoding="utf8", newline="\n") as stream:
        json.dump(value, stream, allow_nan=False, separators=(",", ":"))
        stream.write("\n")
    tick(deadline)


def full_product(h):
    m = len(h)
    return [[sum(h[i][v]*h[v][j] for v in range(m)) for j in range(m)] for i in range(m)]


def model(h, target_order, degree, deadline):
    m = len(h)
    need(type(target_order) is int and type(degree) is int and 0 < m <= 17 and
         degree > 0 and degree % 2 == 0 and target_order >= m, "PARAMETERS")
    need(all(type(row) is list and len(row) == m for row in h), "MATRIX_SHAPE")
    need(all(type(v) is int and v in (0,1) for row in h for v in row), "MATRIX_BINARY_INTEGER")
    need(all(h[i][i] == 0 for i in range(m)), "MATRIX_DIAGONAL")
    need(all(h[i][j] == h[j][i] for i in range(m) for j in range(m)), "MATRIX_SYMMETRY")
    c = full_product(h)
    b = [degree-sum(row) for row in h]
    pairs = [(i,j) for i in range(m) for j in range(i+1,m)]
    delta = [[None if i == j else 2-h[i][j]-c[i][j] for j in range(m)] for i in range(m)]
    need(min(b) >= 0 and all(delta[i][j] >= 0 for i,j in pairs), "NEGATIVE_DEMAND_OR_DEFICIT")
    rhs = [target_order-m,*b,*[delta[i][j] for i,j in pairs]]
    rows = [{"kind":"total"}] + [{"kind":"vertex","vertex":i} for i in range(m)]
    rows += [{"kind":"pair","vertices":[i,j]} for i,j in pairs]
    columns, decisions = [], []
    for mask in range(1 << m):
        if mask % 1024 == 0:
            tick(deadline)
        vertices = [i for i in range(m) if mask & (1 << i)]
        reason = "ELIGIBLE"
        if len(vertices) > degree:
            reason = "TARGET_DEGREE_CAPACITY"
        elif any(delta[i][j] == 0 for i in vertices for j in vertices if i < j):
            reason = "ZERO_PAIR_DEFICIT"
        else:
            induced_degrees = [sum(h[i][j] for j in vertices) for i in vertices]
            if any(d > 1 for d in induced_degrees):
                reason = "NOT_INDUCED_MATCHING"
            elif len(vertices)-sum(induced_degrees)//2 > degree//2:
                reason = "NEIGHBOR_MATCHING_CAPACITY"
        decisions.append({"mask":mask,"decision":reason})
        if reason == "ELIGIBLE":
            v = [int(bool(mask & (1 << i))) for i in range(m)]
            columns.append({"mask":mask,"coefficient":[1,*v,*[v[i]*v[j] for i,j in pairs]]})
    d = [[b[i] if i == j else delta[i][j] for j in range(m)] for i in range(m)]
    z = [[target_order-m,*b]] + [[b[i],*d[i]] for i in range(m)]
    return dict(schema=SCHEMA,target_order=target_order,target_degree=degree,adjacent_cn=1,nonadjacent_cn=2,
                ordered_support_vertices=list(range(m)),induced_adjacency=h,H_squared=c,vertex_rhs=b,
                pair_deficits=delta,row_labels=rows,right_hand_side=rhs,gram_matrix=z,
                universe_mask_range=[0,(1 << m)-1],eligible_type_count=len(columns),
                decision_counts=dict(Counter(x["decision"] for x in decisions))), columns, decisions


def exact_gram(z, deadline):
    """Rational congruence preserving explicit original-coordinate basis vectors."""
    m = len(z)
    a = [[Fraction(v) for v in row] for row in z]
    basis = [[Fraction(int(i == j)) for i in range(m)] for j in range(m)]
    pivots = []
    while a:
        tick(deadline)
        pivot = next((i for i in range(len(a)) if a[i][i]), None)
        if pivot is None:
            edge = next(((i,j) for i in range(len(a)) for j in range(i+1,len(a)) if a[i][j]), None)
            if edge is None:
                return dict(status="CANDIDATE_EXACT_PSD_CONGRUENCE",positive_pivots=pivots,zero_dimension=len(a))
            i,j = edge
            q = [u-(1 if a[i][j] > 0 else -1)*v for u,v in zip(basis[i],basis[j])]
            break
        order = [pivot,*[i for i in range(len(a)) if i != pivot]]
        a = [[a[i][j] for j in order] for i in order]
        basis = [basis[i] for i in order]
        p = a[0][0]
        if p < 0:
            q = basis[0]
            break
        pivots.append(str(p))
        basis = [[v-a[0][j]/p*u for u,v in zip(basis[0],basis[j])] for j in range(1,len(a))]
        a = [[a[i][j]-a[i][0]*a[0][j]/p for j in range(1,len(a))] for i in range(1,len(a))]
    else:
        return dict(status="CANDIDATE_EXACT_PSD_CONGRUENCE",positive_pivots=pivots,zero_dimension=0)
    quadratic = sum(q[i]*z[i][j]*q[j] for i in range(m) for j in range(m))
    need(quadratic < 0, "NEGATIVE_DIRECTION_RECONSTRUCTION")
    y = [q[0]*q[0],*[2*q[0]*q[i]+q[i]*q[i] for i in range(1,m)],
         *[2*q[i]*q[j] for i in range(1,m) for j in range(i+1,m)]]
    return dict(status="CANDIDATE_EXACT_NEGATIVE_GRAM_DIRECTION",q=list(map(str,q)),quadratic=str(quadratic),
                farkas_vector=list(map(str,y)),positive_pivots_before_negative=pivots)


def check_primal(raw, columns, rhs):
    need(len(raw) == len(columns), "PRIMAL_POPULATION")
    x = [Fraction(v) for v in raw]
    need(all(v >= 0 for v in x), "PRIMAL_NONNEGATIVE")
    need(all(sum(v*c["coefficient"][i] for v,c in zip(x,columns)) == r for i,r in enumerate(rhs)), "PRIMAL_MOMENTS")
    return all(v.denominator == 1 for v in x)


def check_farkas(raw, columns, rhs):
    y = [Fraction(v) for v in raw]
    need(len(y) == len(rhs), "FARKAS_POPULATION")
    need(sum(v*r for v,r in zip(y,rhs)) < 0, "FARKAS_RHS_SIGN")
    need(all(sum(v*a for v,a in zip(y,c["coefficient"])) >= 0 for c in columns), "FARKAS_COLUMN_SIGN")


def write_case(out, name, h, n, k, deadline, exact_primal=None, use_lp=False):
    folder = out/name
    folder.mkdir()
    raw, columns, decisions = model(h,n,k,deadline)
    gram = exact_gram(raw["gram_matrix"],deadline)
    if "farkas_vector" in gram:
        check_farkas(gram["farkas_vector"],columns,raw["right_hand_side"])
    save(folder/"model.json",raw,deadline)
    save(folder/"types.json",columns,deadline)
    save(folder/"universe.json",decisions,deadline)
    save(folder/"gram.json",gram,deadline)
    result = dict(name=name,eligible_types=len(columns),universe_masks=len(decisions),gram_status=gram["status"])
    if exact_primal is not None:
        values = [str(exact_primal.get(c["mask"],0)) for c in columns]
        integer = check_primal(values,columns,raw["right_hand_side"])
        save(folder/"primal.json",dict(status="CANDIDATE_EXACT_MOMENT_PRIMAL",values=values,integer=integer),deadline)
        result["exact_primal_integer"] = integer
    if use_lp and "farkas_vector" not in gram:
        import numpy as np
        import scipy
        from scipy.optimize import linprog
        tick(deadline)
        a = np.array([c["coefficient"] for c in columns],dtype=np.float64).T
        allocation = max(1.0,(deadline.status()["remaining_seconds"]-60)/2)
        answer = linprog(np.zeros(len(columns)),A_eq=a,b_eq=np.array(raw["right_hand_side"],dtype=np.float64),
                         bounds=(0,None),method="highs",options={"presolve":True,"time_limit":allocation})
        tick(deadline)
        numerical = dict(status=int(answer.status),message=str(answer.message),solver_time_limit_seconds=allocation,
                         scipy=scipy.__version__,numpy=np.__version__,certificate=False)
        if answer.x is not None:
            numerical["primal_float64"] = list(map(float,answer.x))
            values = [str(Fraction(float(v)).limit_denominator(1000000)) for v in answer.x]
            try:
                integer = check_primal(values,columns,raw["right_hand_side"])
            except ValueError as error:
                numerical["rational_reconstruction_failure"] = str(error)
            else:
                save(folder/"primal.json",dict(status="CANDIDATE_EXACT_MOMENT_PRIMAL",values=values,integer=integer),deadline)
                result["exact_primal_integer"] = integer
        save(folder/"numerical_guidance.json",numerical,deadline)
        result["numerical_solver_status_not_a_proof"] = numerical["status"]
    return result


def calibration(out, deadline):
    rook = [[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)] for i in range(9)]
    product = full_product(rook)
    need(all(product[i][j] == (4 if i == j else 2-rook[i][j]) for i in range(9) for j in range(9)), "ROOK_COMPLETE_IDENTITY")
    profiles = [("single",[0],{0:4,1:4}),("adjacent",[0,1],{0:2,1:2,2:2,3:1}),
                ("nonadjacent",[0,4],{0:1,1:2,2:2,3:2}),("row",[0,1,2],{1:2,2:2,4:2}),
                ("diagonal",[0,4,8],{3:2,5:2,6:2})]
    cases = []
    for name,s,wanted in profiles:
        actual = Counter(sum(rook[v][u] << i for i,u in enumerate(s)) for v in range(9) if v not in s)
        need(dict(actual) == wanted, "ROOK_EXTERIOR_PROFILE")
        h = [[rook[i][j] for j in s] for i in s]
        cases.append(write_case(out,name,h,9,4,deadline,dict(actual)))
    gram_controls = []
    for matrix, negative in [([[1,0],[0,2]],False),([[0,1],[1,0]],True),([[1,0],[0,-1]],True),([[0,0],[0,0]],False)]:
        observed = exact_gram(matrix,deadline)
        need(("q" in observed) == negative, "GRAM_CONTROL")
        gram_controls.append(dict(matrix=matrix,expected_negative=negative,observed=observed))
    raw, columns, _ = model([[0]],9,4,deadline)
    negatives = []
    calls = [("bool_matrix","MATRIX_BINARY_INTEGER",lambda:model([[False]],9,4,deadline)),
             ("float_matrix","MATRIX_BINARY_INTEGER",lambda:model([[0.0]],9,4,deadline)),
             ("loop","MATRIX_DIAGONAL",lambda:model([[1]],9,4,deadline)),
             ("asymmetry","MATRIX_SYMMETRY",lambda:model([[0,1],[0,0]],9,4,deadline)),
             ("negative_primal","PRIMAL_NONNEGATIVE",lambda:check_primal(["-1","9"],columns,raw["right_hand_side"])),
             ("altered_primal","PRIMAL_MOMENTS",lambda:check_primal(["4","3"],columns,raw["right_hand_side"])),
             ("wrong_farkas_rhs","FARKAS_RHS_SIGN",lambda:check_farkas(["1","0"],columns,raw["right_hand_side"])),
             ("wrong_farkas_column","FARKAS_COLUMN_SIGN",lambda:check_farkas(["-1","0"],columns,raw["right_hand_side"]))]
    for name,expected,call in calls:
        try:
            call()
        except ValueError as error:
            actual = str(error)
        else:
            actual = "ACCEPTED_CORRUPTION"
        need(actual == expected, "CALIBRATION_STAGE:"+name)
        negatives.append(dict(name=name,expected_stage=expected,actual_stage=actual))
    save(out/"controls.json",dict(rook_identity_entries=81,positive_moment_cases=cases,gram_cases=gram_controls,strict_negative=negatives),deadline)
    return dict(positive_moment_cases=5,gram_cases=4,strict_negative_cases=8)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode",choices=("calibrate","seventeen-base"))
    p.add_argument("--seconds",type=float,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--source-commit",required=True)
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason="Necessary fixed induced exterior moments; all hashes/enumeration/exact arithmetic/LP/serialization share one invocation")
    out = args.out.resolve()
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(), "FRESH_OUTPUT_NAMESPACE")
    out.mkdir(parents=True)
    pins = {}
    try:
        for name in (Path(__file__).resolve().relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+"_spec.md").resolve().relative_to(ROOT).as_posix(),
                     "acceleration/command_deadline.py","pyproject.toml","uv.lock"):
            pins[name] = digest(ROOT/name,deadline)
        controls = calibration(out,deadline)
        science = None
        if args.mode == "seventeen-base":
            h = [[0]*17 for _ in range(17)]
            for triple in TRIPLES:
                for i in triple:
                    for j in triple:
                        if i != j:
                            h[i][j] = 1
            science = write_case(out,"seventeen_base",h,99,14,deadline,use_lp=True)
        for name,identity in pins.items():
            need(digest(ROOT/name,deadline) == identity, "CLOSING_PIN")
        outputs = {path.relative_to(ROOT).as_posix():digest(path,deadline) for path in sorted(out.rglob("*")) if path.is_file()}
        save(out/"summary.json",dict(schema="EXTERIOR_NEIGHBOR_MOMENT_PRODUCER_V1",status="CANDIDATE_FINITE_MOMENT_ARTIFACTS_PENDING_INDEPENDENT_CHECK",
             producer="/root",timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
             source_context_commit=args.source_commit,python=platform.python_version(),inputs_sha256=pins,outputs_sha256=outputs,
             mode=args.mode,controls=controls,scientific_result=science,target_resolution="NONE",independent_approval=False,
             limitations=["One exact induced graph necessary relaxation only; no graph completion or unrestricted coverage.",
                          "Numerical LP status is not an infeasibility certificate. Exact primal/negativeGram remains pending independent checking.",
                          "Combinedaddededges and other supportword configurations are absent."],deadline=deadline.status()),deadline)
        tick(deadline)
        return 0
    except BaseException as error:
        if (out/"summary.json").exists():
            (out/"summary.json").rename(out/"summary.not_approved.json")
        (out/"failure.json").write_text(json.dumps(dict(status="FAILED_NOT_APPROVED",error=repr(error),inputs_sha256=pins,
             deadline=deadline.status(),automatic_retry=False,target_resolution="NONE"),allow_nan=False)+"\n",encoding="utf8")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
