"""Independent literal-row/dense-adjacency checker; SOURCE ONLY until approved.

No producer imports, bitmask delta cache, cut-edge scorer, pruning code or RNG.
The generic simultaneous replacement permits repeated selected values.  The
declared restricted subset separately excludes them, retaining the role ID.
"""
from collections import Counter
from itertools import combinations
import hashlib
import json


class AuditError(ValueError):
    def __init__(self, stage, detail=""):
        self.stage = stage
        super().__init__(stage + (": " + detail if detail else ""))


def need(ok, stage, detail=""):
    if not ok:
        raise AuditError(stage, detail)


def same(a, b):
    # True is not interchangeable with 1 in a mathematical artifact.
    return json.dumps(a, sort_keys=True, separators=(",", ":")) == json.dumps(b, sort_keys=True, separators=(",", ":"))


def integer(x):
    return type(x) is int


def matrix_bytes(adjacency):
    return (str(len(adjacency)) + "\n" + "".join("".join(str(x) for x in row) + "\n" for row in adjacency)).encode("ascii")


def topology(n, degree, rows, root):
    need(all(integer(x) for x in (n, degree, root)) and 3 <= n <= 99
         and 0 < 2 * degree < n and 0 <= root < n, "DOMAIN_DIMENSIONS")
    need(type(rows) is list and 3 * len(rows) == n * degree, "DOMAIN_POPULATION")
    incidence = [0] * n
    adjacency = [[0] * n for _ in range(n)]
    for row in rows:
        need(type(row) is list and len(row) == 3 and all(integer(x) for x in row), "DOMAIN_ROW_TYPES")
        need(all(0 <= x < n for x in row), "DOMAIN_POINT_RANGE")
        need(len(set(row)) == 3, "DOMAIN_ROW_DISTINCT")
        for x in row:
            incidence[x] += 1
        for x, y in combinations(row, 2):
            need(adjacency[x][y] == 0, "DOMAIN_PAIR_LINEARITY")
            adjacency[x][y] = adjacency[y][x] = 1
    need(incidence == [degree] * n, "DOMAIN_POINT_DEGREE")
    need(all(sum(row) == 2 * degree for row in adjacency), "DOMAIN_GRAPH_DEGREE")
    frozen = [[i, *row] for i, row in enumerate(rows) if root in row]
    return dict(n=n, degree=degree, root=root, rows=[row[:] for row in rows], adjacency=adjacency,
                frozen=frozen, mutable=[i for i, row in enumerate(rows) if root not in row])


def dense_score(adjacency, root):
    """Complete scalar matrix products, including diagonal; no cached delta."""
    n = len(adjacency)
    cn = [[0] * n for _ in range(n)]
    for x in range(n):
        for y in range(x, n):
            value = sum(adjacency[x][z] * adjacency[y][z] for z in range(n))
            cn[x][y] = cn[y][x] = value
    el = em = 0
    for x, y in combinations(range(n), 2):
        if adjacency[x][y]:
            el += (cn[x][y] - 1) ** 2
        else:
            em += (cn[x][y] - 2) ** 2
    rr = sum((cn[root][x] - 2) ** 2 for x in range(n) if x != root and not adjacency[root][x])
    return dict(cn=cn, E_lambda=el, E_mu=em, R_root=rr)


def base_graph(n, degree, rows, root):
    base = topology(n, degree, rows, root)
    base.update(dense_score(base["adjacency"], root))
    return base


def checked_base(base):
    need(type(base) is dict and set(base) == {"n", "degree", "root", "rows", "adjacency", "frozen", "mutable", "cn", "E_lambda", "E_mu", "R_root"}, "BASE_SCHEMA")
    expected = base_graph(base["n"], base["degree"], base["rows"], base["root"])
    need(same(base, expected), "BASE_CACHE", "whole literal integer cache including every zero/one cell")


def labels(base, role):
    checked_base(base)
    need(type(role) in (list, tuple) and len(role) == 6 and all(integer(x) for x in role), "ROLE_TYPES")
    i, j, k, ix, jy, kz = role
    need(all(0 <= x < 3 for x in (ix, jy, kz))
         and all(0 <= x < len(base["rows"]) for x in (i, j, k)), "ROLE_RANGE")
    need(len({i, j, k}) == 3, "ROLE_DISTINCT_LINES")
    need(all(x in base["mutable"] for x in (i, j, k)), "ROLE_FROZEN_LINES")
    return i, j, k, ix, jy, kz


def simultaneous_rows(base, role):
    i, j, k, ix, jy, kz = labels(base, role)
    u, v, w = base["rows"][i][ix], base["rows"][j][jy], base["rows"][k][kz]
    changed = [row[:] for row in base["rows"]]
    changed[i][ix], changed[j][jy], changed[k][kz] = w, u, v
    return changed, (u, v, w)


def raw_cycle(base, role):
    """Actual literal cycle, without distinct-selected or CN-role restriction."""
    changed, values = simultaneous_rows(base, role)
    i, j, k, _, _, _ = role
    result = dict(role=list(role), selected_values=list(values), changed_rows=[changed[x][:] for x in (i, j, k)],
                  valid=False, invalid_reason=None, conflict_pairs=None, adjacency=None, cn=None,
                  E_lambda=None, E_mu=None, R_root=None, root_delta=None, changed_root_counts=None,
                  frozen_unchanged=None, matrix_sha256=None)
    if any(len(set(row)) != 3 for row in changed):
        result["invalid_reason"] = "receiving_triple_duplicate_point"
        return result
    # Recount every pair of EVERY final triple, including unchanged lines and
    # remove/re-add cancellations, rather than agreeing with a six-toggle test.
    occupancy = Counter(tuple(sorted(pair)) for row in changed for pair in combinations(row, 2))
    conflicts = sorted([list(pair) for pair, count in occupancy.items() if count > 1])
    if conflicts:
        result.update(invalid_reason="new_pair_already_present", conflict_pairs=conflicts)
        return result
    candidate = topology(base["n"], base["degree"], changed, base["root"])
    scored = dense_score(candidate["adjacency"], base["root"])
    r = base["root"]
    changes = [[x, base["cn"][r][x], scored["cn"][r][x]] for x in range(base["n"])
               if x != r and base["cn"][r][x] != scored["cn"][r][x]]
    result.update(valid=True, adjacency=candidate["adjacency"], cn=scored["cn"], E_lambda=scored["E_lambda"],
                  E_mu=scored["E_mu"], R_root=scored["R_root"], root_delta=scored["R_root"] - base["R_root"],
                  changed_root_counts=changes, frozen_unchanged=candidate["frozen"] == base["frozen"],
                  matrix_sha256=hashlib.sha256(matrix_bytes(candidate["adjacency"])).hexdigest())
    need(result["frozen_unchanged"] and candidate["adjacency"][r] == base["adjacency"][r], "CYCLE_FROZEN_INVARIANT")
    return result


def restricted_domain(base):
    checked_base(base)
    need(base["E_lambda"] == 0, "RESTRICTED_LAMBDA_DOMAIN")
    r = base["root"]
    neighbors = [x for x in range(base["n"]) if base["adjacency"][r][x]]
    nset = set(neighbors)
    outsiders = [x for x in range(base["n"]) if x != r and x not in nset]
    under = [x for x in outsiders if base["cn"][r][x] == 1]
    over = [x for x in outsiders if base["cn"][r][x] == 3]
    counts = {i: sum(x in nset for x in base["rows"][i]) for i in base["mutable"]}
    need(all(count in (0, 1) for count in counts.values()), "RESTRICTED_LINE_CLASSES")
    zero = [i for i in base["mutable"] if counts[i] == 0]
    one = [i for i in base["mutable"] if counts[i] == 1]
    uro = sorted((x, i, p) for i in zero for p, x in enumerate(base["rows"][i]) if x in under)
    vro = sorted((x, i, p) for i in one for p, x in enumerate(base["rows"][i]) if x in over)
    need(len(one) == 2 * base["degree"] * (base["degree"] - 1), "RESTRICTED_INCIDENCE_COUNTS")
    need(all(sum(x == u for x, _, _ in uro) == base["degree"] - 1 for u in under)
         and all(sum(x == v for x, _, _ in vro) == 3 for v in over), "RESTRICTED_ROLE_COUNTS")
    # Direct nested list enumeration, no imported mixed-radix producer decoder.
    roles = [(i, j, k, ip, jp, kp) for _, i, ip in uro for _, j, jp in vro
             for k in zero if k != i for kp in range(3)]
    need(len(roles) == len(uro) * len(vro) * max(0, len(zero) - 1) * 3, "RESTRICTED_POPULATION")
    return dict(base=base, neighbors=neighbors, outsiders=outsiders, under=under, over=over,
                zero_lines=zero, one_lines=one, u_roles=uro, v_roles=vro, roles=roles,
                distinct_selected_subset=True, prefilter_population=len(roles))


def restricted_record(domain, pid):
    need(integer(pid) and 0 <= pid < len(domain["roles"]), "PROPOSAL_ID")
    need(type(domain.get("distinct_selected_subset")) is bool and domain["distinct_selected_subset"] is True
         and integer(domain.get("prefilter_population")) and domain["prefilter_population"] == len(domain["roles"]),
         "RESTRICTED_DOMAIN_SCHEMA")
    base, role = domain["base"], domain["roles"][pid]
    labels(base, role)
    i, j, k, ix, jy, kz = role
    u, v, w = base["rows"][i][ix], base["rows"][j][jy], base["rows"][k][kz]
    record = dict(proposal_id=pid, role=list(role), selected_values=[u, v, w], subset_selected_distinct=len({u, v, w}) == 3,
                  classification=None, valid=False, invalid_reason=None, candidate=None)
    if not record["subset_selected_distinct"]:
        record.update(classification="invalid_selection", invalid_reason="selected_points_not_distinct")
        return record
    candidate = raw_cycle(base, role)
    record["candidate"] = candidate
    if not candidate["valid"]:
        record.update(invalid_reason=candidate["invalid_reason"], classification="invalid_selection" if
                      candidate["invalid_reason"] == "receiving_triple_duplicate_point" else "invalid_linearity")
        return record
    expected_changes = sorted([[u, 1, 2], [v, 3, 2]])
    need(candidate["changed_root_counts"] == expected_changes, "RESTRICTED_ROOT_COUNTS")
    need(candidate["root_delta"] == -2, "RESTRICTED_ROOT_DELTA")
    record.update(valid=True, classification="valid_lambda_preserving_root_down" if candidate["E_lambda"] == 0
                  else "valid_lambda_changed")
    return record


def verify_record(domain, pid, record):
    expected = restricted_record(domain, pid)
    need(type(record) is dict and set(record) == set(expected), "RECORD_SCHEMA")
    for key, stage in [("proposal_id", "RECORD_ID"), ("role", "RECORD_ROLE"), ("selected_values", "RECORD_VALUES"),
                       ("subset_selected_distinct", "RECORD_SUBSET"), ("valid", "RECORD_VALIDITY"),
                       ("invalid_reason", "RECORD_VALIDITY"), ("classification", "RECORD_CLASSIFICATION")]:
        need(same(record[key], expected[key]), stage)
    cand, exact = record["candidate"], expected["candidate"]
    if exact is None:
        need(cand is None, "RECORD_CANDIDATE_ABSENCE")
        return
    need(type(cand) is dict and set(cand) == set(exact), "RECORD_CANDIDATE_SCHEMA")
    field_stages = {"role": "RECORD_ROLE", "selected_values": "RECORD_VALUES", "changed_rows": "RECORD_REPLACEMENT",
                    "valid": "RECORD_VALIDITY", "invalid_reason": "RECORD_VALIDITY", "conflict_pairs": "RECORD_PAIR_CONFLICT",
                    "adjacency": "RECORD_ADJACENCY", "cn": "RECORD_COMPLETE_CN", "E_lambda": "RECORD_GLOBAL_SCORE",
                    "E_mu": "RECORD_GLOBAL_SCORE", "R_root": "RECORD_ROOT_SCORE", "root_delta": "RECORD_ROOT_DELTA",
                    "changed_root_counts": "RECORD_ROOT_COUNTS", "frozen_unchanged": "RECORD_FROZEN",
                    "matrix_sha256": "RECORD_MATRIX_HASH"}
    for key, stage in field_stages.items():
        need(same(cand[key], exact[key]), stage)


def fixtures():
    """Literal doily rows, independently transcribed K6 edge perfect matchings."""
    rook = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8]]
    doily = [[0, 9, 14], [0, 10, 13], [0, 11, 12], [1, 6, 14], [1, 7, 13], [1, 8, 12],
             [2, 5, 14], [2, 7, 11], [2, 8, 10], [3, 5, 13], [3, 6, 11], [3, 8, 9],
             [4, 5, 12], [4, 6, 10], [4, 7, 9]]
    lift = [[2 * x + (sheet ^ int(index == 0 and x == 9)) for x in row]
            for index, row in enumerate(doily) for sheet in (0, 1)]
    return dict(rook9=dict(n=9, degree=2, root=0, rows=rook),
                doily15=dict(n=15, degree=3, root=0, rows=doily),
                doily_two_lift30=dict(n=30, degree=3, root=0, rows=lift))
