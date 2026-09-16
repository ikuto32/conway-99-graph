"""Independently rebuild the whole-matching matrix and check an integer proof.

No MIP/model producer or optimizer is imported. All matrix coefficients and
bounds are rebuilt from 99-vertex adjacency and individual variable-edge
contributions. Slack columns are set to zero only because an actual completion
satisfies every quota/cap exactly or with zero violation.
"""
import argparse
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require


def integer(value):
    return type(value) is int


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def reconstruct(candidate, group, kind):
    require(integer(group) and 0 <= group < 7 and kind in ("same_0", "same_1", "cross"), "Invalid matching coordinate")
    graph, unknown = full_graph(candidate)
    labels = [{s-1 for s in graph[u+15] if 1 <= s <= 14} for u in range(84)]
    supports = [{s//2 for s in row} for row in labels]
    cohort = {u+15 for u in range(84) if group in supports[u]}
    vertices = sorted(u for u in cohort if kind == "cross" or 2*group+int(kind[-1]) in labels[u-15])
    chosen = set(vertices)
    y_edges = [(u,v) for u,v in combinations(vertices,2)
               if supports[u-15] & supports[v-15] == {group}
               and ((next(s%2 for s in labels[u-15] if s//2 == group) !=
                     next(s%2 for s in labels[v-15] if s//2 == group)) == (kind == "cross"))]
    require(len(y_edges) == (120 if kind == "cross" else 60), "Wrong matching-variable domain")
    old_matching = [(u,v) for u,v in y_edges if v in graph[u]]
    require(Counter(u for edge in old_matching for u in edge) == Counter({u:1 for u in vertices}),
            "Selected initial coordinate is not a perfect matching")
    b = [set(row) for row in graph]
    for u,v in old_matching:
        b[u].remove(v)
        b[v].remove(u)
    x_edges = sorted(unknown)
    nx,ny = len(x_edges),len(y_edges)
    require(nx == 1680, "Wrong disjoint variable domain")
    boxed = nx+ny
    qplus,qminus,capstart = boxed,boxed+840,boxed+1680
    ncols = boxed+1680+3486

    def edge_coordinates(edges, offset):
        incidence = [[] for _ in range(99)]
        index = {}
        for j,(a,c) in enumerate(edges,offset):
            incidence[a].append((j,c))
            incidence[c].append((j,a))
            index[a,c] = j
        return incidence,index

    x_inc,x_index = edge_coordinates(x_edges,0)
    y_inc,y_index = edge_coordinates(y_edges,nx)

    def edge_basis(incidence,index,u,v,include_adjacency=True):
        # A variable edge incident to u contributes the known adjacency from
        # its other endpoint to v, and conversely for a variable incident to v.
        answer = Counter(j for j,w in incidence[u] if w in b[v])
        answer.update(j for j,w in incidence[v] if w in b[u])
        if include_adjacency and (min(u,v),max(u,v)) in index:
            answer[index[min(u,v),max(u,v)]] += 1
        return answer

    rows = []

    def append(kind_,coordinate,co,lo,hi):
        rows.append(dict(kind=kind_,coordinate=coordinate,coefficients={j:v for j,v in co.items() if v},lower=lo,upper=hi))

    for u in vertices:
        append("matching_degree",[u],{j:1 for j,_ in y_inc[u]},1,1)
    for u,v in combinations(range(99),2):
        if u in chosen or v in chosen:
            append("hard_partial_cap",[u,v],edge_basis(y_inc,y_index,u,v),None,
                   2-len(b[u]&b[v])-int(v in b[u]))
    quotas = [(u,s+1) for u in range(15,99) for s in range(14) if s//2 not in supports[u-15]]
    require(len(quotas) == 840, "Wrong quota domain")
    for i,(u,s) in enumerate(quotas):
        co = edge_basis(x_inc,x_index,u,s,False)
        co.update(edge_basis(y_inc,y_index,u,s,False))
        co[qplus+i],co[qminus+i] = -1,1
        rhs = 2-len(b[u]&b[s])
        append("foreign_label_quota",[u,s],co,rhs,rhs)
    for i,(u,v) in enumerate(combinations(range(15,99),2)):
        constant = len(b[u]&b[v])+int(v in b[u])
        co = edge_basis(x_inc,x_index,u,v)
        co[capstart+i] = -1
        if (u in chosen and v not in cohort) or (v in chosen and u not in cohort):
            active,other = (u,v) if u in chosen else (v,u)
            append("completion_cap_baseline",[u,v],co,None,2-constant)
            for z_column,partner in sorted(y_inc[active],key=lambda row:row[1]):
                indicator = dict(co)
                x_column = x_index.get((min(other,partner),max(other,partner)))
                if x_column is not None:
                    indicator[x_column] = indicator.get(x_column,0)+1
                indicator[z_column] = indicator.get(z_column,0)+1
                append("completion_cap_indicator_M1",[u,v,active,partner],indicator,None,
                       3-constant-int(partner in b[other]))
        else:
            co.update(edge_basis(y_inc,y_index,u,v))
            append("linear_completion_cap",[u,v],co,None,2-constant)

    allowed = {u:{v for _,v in y_inc[u]} for u in vertices}
    if kind == "cross":
        left = sorted(u for u in vertices if 2*group in labels[u-15])
        right = sorted(set(vertices)-set(left))
        @lru_cache(None)
        def count(mask):
            i = mask.bit_count()
            if i == len(left):
                return 1
            return sum(count(mask | (1<<j)) for j,v in enumerate(right) if not(mask>>j&1) and v in allowed[left[i]])
        matching_count = count(0)
    else:
        @lru_cache(None)
        def count(mask):
            if not mask:
                return 1
            i = (mask & -mask).bit_length()-1
            rest = mask ^ (1<<i)
            return sum(count(rest ^ (1<<j)) for j in range(len(vertices))
                       if rest>>j&1 and vertices[j] in allowed[vertices[i]])
        matching_count = count((1<<len(vertices))-1)
        require(matching_count == 6040, "Same-sign matching family count differs from6040")
    return dict(rows=rows,ncols=ncols,boxed=boxed,x_edges=x_edges,y_edges=y_edges,
                old_matching=old_matching,b=b,vertices=vertices,matching_count=matching_count,
                costs=[0]*boxed+[1]*(ncols-boxed),lower=[0]*ncols,upper=[1]*boxed+[None]*(ncols-boxed))


def audit(candidate_path,matrix_path,certificate_path):
    started = time.perf_counter()
    candidate,matrix,certificate = (json.loads(path.read_bytes()) for path in (candidate_path,matrix_path,certificate_path))
    require(matrix["status"] == "EXACT_INTEGER_COEFFICIENT_MATRIX_EXPORT", "Unexpected matrix status")
    require(certificate["status"] == "INTEGER_ZERO_SLACK_MATCHING_CONTRADICTION_CANDIDATE", "No matching certificate candidate")
    require(certificate["matrix_sha256"] == digest(matrix_path), "Matrix certificate SHA mismatch")
    require(matrix["blossom_subsets"] == [], "This checker intentionally accepts only the base model without blossoms")
    require(matrix["all_columns_continuous"] is True, "Expected continuous relaxation export")
    expected_candidate_hash = None
    for name,expected in matrix["inputs_sha256"].items():
        path = Path(name)
        require(digest(path) == expected, "Changed matrix input/source: " + name)
        if path.resolve() == Path(str(candidate_path)).resolve():
            expected_candidate_hash = expected
    require(expected_candidate_hash == digest(candidate_path), "Supplied candidate is not the matrix's bound base K")
    if "candidate_sha256" in certificate:
        require(certificate["candidate_sha256"] == digest(candidate_path), "Certificate candidate SHA mismatch")
    require(digest(Path(certificate["relaxation_path"])) == certificate["relaxation_sha256"], "Relaxation provenance SHA mismatch")
    # The numerical relaxation is hashed for provenance only; no status, primal,
    # objective, or floating dual enters either the matrix check or exact proof.
    expected = reconstruct(candidate,matrix["root_group"],matrix["matching_class"])
    rows,ncols,boxed = expected["rows"],expected["ncols"],expected["boxed"]
    require(integer(matrix["nrows"]) and matrix["nrows"] == len(rows) and integer(matrix["ncols"]) and matrix["ncols"] == ncols,
            "Matrix dimensions mismatch")
    require(matrix["edge_variables"] == [[u-15,v-15] for u,v in expected["x_edges"]], "X column coordinates/order mismatch")
    require(matrix["matching_variables"] == [[u-15,v-15] for u,v in expected["y_edges"]], "Y column coordinates/order mismatch")
    for field,truth in (("col_lower",expected["lower"]),("col_upper",expected["upper"]),("col_cost",expected["costs"])):
        require(type(matrix[field]) is list and all(value is None or integer(value) for value in matrix[field]) and matrix[field] == truth,
                "Column bounds/cost mismatch: " + field)
    require(matrix["column_order"] == "1680 X; matching Y;840 quota excess;840 quota shortage;3486 shared pair-cap slacks",
            "Unexpected column-order metadata")
    starts,indices,values = matrix["csr_start"],matrix["csr_index"],matrix["csr_value"]
    require(type(starts) is list and len(starts) == len(rows)+1 and all(integer(x) for x in starts)
            and starts[0] == 0 and starts[-1] == len(indices) == len(values)
            and all(0 <= a <= b for a,b in zip(starts,starts[1:])), "Invalid CSR offsets")
    require(all(integer(j) and 0 <= j < ncols for j in indices) and all(integer(v) and v != 0 for v in values),
            "Invalid CSR column/value")
    require(len(matrix["row_lower"]) == len(matrix["row_upper"]) == len(rows), "Row bound count mismatch")
    for i,row in enumerate(rows):
        begin,end = starts[i:i+2]
        ix = indices[begin:end]
        require(all(a < b for a,b in zip(ix,ix[1:])), "CSR indices not strictly sorted/unique")
        actual = dict(zip(ix,values[begin:end]))
        require(actual == row["coefficients"], f"Independent row coefficient mismatch at{i}:{row['kind']}:{row['coordinate']}")
        for field,truth in (("row_lower",row["lower"]),("row_upper",row["upper"])):
            value = matrix[field][i]
            require((value is None or integer(value)) and value == truth, f"Row bound mismatch at{i}:{field}")
    kinds = dict(Counter(row["kind"] for row in rows))
    require(matrix["row_kinds"] == kinds, "Row-kind counts mismatch")
    require(certificate["projected_box_columns"] == boxed and certificate["zeroed_slack_columns"] == ncols-boxed and
            certificate["matrix_rows"] == len(rows), "Certificate projected dimensions mismatch")
    coefficients,rhs,last = [0]*boxed,0,-1
    weighted_kinds = Counter()
    for record in certificate["weighted_rows"]:
        require(type(record) is list and len(record) == 2 and all(integer(value) for value in record), "Invalid weighted row")
        i,n = record
        require(last < i < len(rows) and n != 0, "Duplicate/unsorted/out-of-range/zero weighted row")
        last = i
        row = rows[i]
        bound = row["lower"] if n > 0 else row["upper"]
        require(bound is not None, "Multiplier sign selects an infinite row bound")
        rhs += n*bound
        for j,a in row["coefficients"].items():
            if j < boxed:
                coefficients[j] += n*a
        weighted_kinds[row["kind"]] += 1
    box_upper = sum(max(0,value) for value in coefficients)
    margin = rhs-box_upper
    require(margin > 0, "No exact zero-slack contradiction")
    require(type(certificate["combined_coefficients"]) is list and all(integer(value) for value in certificate["combined_coefficients"])
            and certificate["combined_coefficients"] == coefficients, "Declared combined coefficients mismatch")
    for field,truth in (("combined_lower_rhs",rhs),("box_upper_bound",box_upper),("contradiction_margin",margin)):
        require(integer(certificate[field]) and certificate[field] == truth, "Declared exact proof scalar mismatch: " + field)
    return dict(status="INDEPENDENT_WHOLE_MATCHING_MATRIX_AND_INTEGER_FARKAS_AUDIT_PASS",
                inputs_sha256={str(path):digest(path) for path in (candidate_path,matrix_path,certificate_path)},
                auditor_sha256=digest(Path(__file__)),graph_auditor_sha256=digest(Path(__file__).with_name("audit_certificate.py")),
                root_group=matrix["root_group"],matching_class=matrix["matching_class"],
                full_matrix_rows_independently_rebuilt=len(rows),full_matrix_columns=ncols,csr_nonzeros_checked=len(values),
                row_kinds=kinds,all_column_bounds_costs_and_shared_slack_positions_checked=True,
                projected_box_variables=boxed,zero_slack_columns=ncols-boxed,
                weighted_rows_checked=len(certificate["weighted_rows"]),weighted_row_kinds=dict(weighted_kinds),
                combined_lower_rhs=rhs,box_upper_bound=box_upper,contradiction_margin=margin,
                positive_combined_coefficients=sum(value>0 for value in coefficients),
                negative_combined_coefficients=sum(value<0 for value in coefficients),
                fixed_overlap_edges=168-len(expected["old_matching"]),free_matching_edges=len(expected["old_matching"]),
                allowed_binary_matchings_before_partial_caps=expected["matching_count"],
                other_matching_coordinates_fixed=20,
                proof="Every zero-slack solution obeys C*z>=R, but boxedX,Y satisfyC*z<=sum(max(C_j,0)); verified positive integer gap is impossible.",
                necessary_system_justification=[
                    "Remove the entire chosen perfect matching from full99 known adjacency to obtainB; all other20matching coordinates remain fixed.",
                    "Binary symmetric degree-one Y has offdiagonalY^2=0, giving affine partial-graph capsB^2+BY+YB+B+Y<=2.",
                    "All840foreign-label common-neighbor equalities are affine inX,Y; preserved own-label categories remain satisfied.",
                    "DiscardedX^2 common-neighbor contributions are nonnegative. Remaining nonlinearY/X pairs use one selectedpartnerg=B_vp+X_vp in[0,1]. Baseline plusM1indicators with one shared zero slack are necessary for every binaryY completion.",
                    "ContinuousX,Y box and degree constraints relax the actual binary completion, so contradiction excludes every admissible binary matching in this fixed coordinate."],
                numerical_solver_status_bound_or_dual_used_as_proof=False,producer_or_optimizer_imported=False,
                elapsed_seconds=time.perf_counter()-started,
                scope="Exact exclusion of this entire one-matching coordinate with20other matchings fixed (including all listed support-allowed matchings before partial caps). No global E0 or Conway nonexistence theorem, no independent-family coverage addition, and no graph construction.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate",type=Path,required=True)
    parser.add_argument("--matrix",type=Path,required=True)
    parser.add_argument("--certificate",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve existing exact audit")
    report = audit(args.candidate,args.matrix,args.certificate)
    with args.out.open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
