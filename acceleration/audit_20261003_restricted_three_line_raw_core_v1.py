"""SOURCE ONLY: independent full-row reconstruction for Native raw records.

No producer imports or incremental CN/mask updater.  NumPy int64 multiplication
is exact here: binary input, n<=99, every dot product<=99.  The independently
calibrated scalar core remains unchanged and is used only by the new caller's
finite cross-checks, not by this record-generation path.
"""
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path
import re

import numpy as np


class AuditError(ValueError):
    def __init__(self, stage, detail=""):
        self.stage = stage
        super().__init__(stage + (": " + detail if detail else ""))


def need(ok, stage, detail=""):
    if not ok:
        raise AuditError(stage, detail)


def integer(x):
    return type(x) is int


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def same(a, b):
    return canonical(a) == canonical(b)


def strict_json(raw):
    def object_pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "JSON", "duplicate key")
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=object_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(AuditError("JSON", "nonfinite")))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise AuditError("JSON", "invalid encoding") from error


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def matrix_bytes(adjacency):
    return (str(len(adjacency)) + "\n" + "".join("".join(str(int(x)) for x in row) + "\n" for row in adjacency)).encode("ascii")


def geometry(n, degree, rows, root):
    need(all(integer(x) for x in (n, degree, root)) and 3 <= n <= 99
         and 0 < 2 * degree < n and 0 <= root < n, "DOMAIN_DIMENSIONS")
    need(type(rows) in (list, tuple) and 3 * len(rows) == n * degree, "DOMAIN_POPULATION")
    need(all(type(row) in (list, tuple) and len(row) == 3 and all(integer(x) for x in row) for row in rows), "DOMAIN_ROW_TYPES")
    need(all(0 <= x < n for row in rows for x in row), "DOMAIN_POINT_RANGE")
    need(all(len(set(row)) == 3 for row in rows), "DOMAIN_ROW_DISTINCT")
    triples = np.asarray(rows, dtype=np.int64)
    need(triples.dtype == np.dtype("int64"), "INTEGER_DTYPE")
    need(np.array_equal(np.bincount(triples.ravel(), minlength=n), np.full(n, degree, dtype=np.int64)), "DOMAIN_POINT_DEGREE")
    pair_labels = np.concatenate([triples[:, [0, 1]], triples[:, [0, 2]], triples[:, [1, 2]]], axis=0)
    pair_labels.sort(axis=1)
    counts = np.bincount(pair_labels[:, 0] * n + pair_labels[:, 1], minlength=n * n).reshape(n, n)
    need(int(counts.max()) <= 1, "DOMAIN_PAIR_LINEARITY")
    adjacency = counts + counts.T
    need(adjacency.dtype == np.dtype("int64") and np.all((adjacency == 0) | (adjacency == 1))
         and np.all(np.diag(adjacency) == 0) and np.all(adjacency.sum(axis=1) == 2 * degree), "DOMAIN_GRAPH_DEGREE")
    return adjacency


def score(adjacency, root):
    n = len(adjacency)
    need(adjacency.shape == (n, n) and 3 <= n <= 99 and adjacency.dtype == np.dtype("int64")
         and np.all((adjacency == 0) | (adjacency == 1)) and np.array_equal(adjacency, adjacency.T)
         and np.all(np.diag(adjacency) == 0) and integer(root) and 0 <= root < n, "SCORE_DOMAIN")
    # <=99 products of 0/1, then squares <=99^2, <=4851 terms.  All bounds
    # are far below 2^63. No float multiplication, BLAS solve or relaxation.
    cn = adjacency @ adjacency
    need(cn.dtype == np.dtype("int64") and np.all((0 <= cn) & (cn <= n))
         and np.array_equal(cn, cn.T) and np.array_equal(np.diag(cn), adjacency.sum(axis=1)), "INTEGER_PRODUCT")
    x, y = np.triu_indices(n, 1)
    edges = adjacency[x, y] == 1
    el = int(np.sum((cn[x[edges], y[edges]] - 1) ** 2, dtype=np.int64))
    em = int(np.sum((cn[x[~edges], y[~edges]] - 2) ** 2, dtype=np.int64))
    outsiders = (adjacency[root] == 0); outsiders[root] = False
    rr = int(np.sum((cn[root, outsiders] - 2) ** 2, dtype=np.int64))
    return cn, el, em, rr


@dataclass(frozen=True)
class FixedInput:
    n: int
    degree: int
    root: int
    rows: tuple
    adjacency: np.ndarray
    cn: np.ndarray
    E_lambda: int
    E_mu: int
    R_root: int
    frozen: tuple
    mutable: tuple
    digest: str


def fingerprint(base):
    raw = canonical(dict(n=base.n, degree=base.degree, root=base.root, rows=base.rows,
                         frozen=base.frozen, mutable=base.mutable, E_lambda=base.E_lambda,
                         E_mu=base.E_mu, R_root=base.R_root))
    return hashlib.sha256(raw + base.adjacency.tobytes(order="C") + base.cn.tobytes(order="C")).hexdigest()


def fixed_input(n, degree, rows, root):
    adjacency = geometry(n, degree, rows, root)
    cn, el, em, rr = score(adjacency, root)
    adjacency.setflags(write=False); cn.setflags(write=False)
    literal = tuple(tuple(row) for row in rows)
    values = dict(n=n, degree=degree, root=root, rows=literal, adjacency=adjacency, cn=cn,
                  E_lambda=el, E_mu=em, R_root=rr,
                  frozen=tuple((i, *row) for i, row in enumerate(literal) if root in row),
                  mutable=tuple(i for i, row in enumerate(literal) if root not in row))
    provisional = FixedInput(**values, digest="")
    return FixedInput(**values, digest=fingerprint(provisional))


def unchanged(base):
    need(not base.adjacency.flags.writeable and not base.cn.flags.writeable
         and fingerprint(base) == base.digest, "BASE_IMMUTABILITY")


def native_cache(d):
    """Producer-cache adapter: off-diagonal CN exact, diagonal MUST be zero.

    This representation is never used for candidate matrix multiplication or
    an SRG identity. The actual A^2 diagonal remains 2*point_degree.
    """
    b = d["base"]
    cn = b.cn.tolist()
    for x in range(b.n):
        cn[x][x] = 0
    pairs = [[i, j] for at, i in enumerate(b.mutable) for j in b.mutable[at + 1:]]
    uro = d["universe"]["under_incidence_roles"]
    vro = d["universe"]["over_incidence_roles"]
    zero = d["universe"]["zero_neighbor_lines"]
    return dict(base=dict(n=b.n, degree=b.degree, triples=[list(row) for row in b.rows], root=b.root,
        masks=[sum(int(b.adjacency[x, y]) * (1 << y) for y in range(b.n)) for x in range(b.n)],
        cn=cn, lambda_energy=b.E_lambda, mu_energy=b.E_mu, root_residual=b.R_root,
        frozen_rows=[list(row) for row in b.frozen], mutable_labels=list(b.mutable), pairs=pairs, total=len(pairs) * 9),
        universe=d["universe"], u_roles=uro, v_roles=vro, k_choices={str(i): [k for k in zero if k != i] for i in zero},
        per_uv=max(0, len(zero) - 1) * 3, total=len(d["roles"]))


def check_native_cache(d, raw):
    expected = native_cache(d)
    need(type(raw) is dict and type(raw.get("base")) is dict, "CACHE_SCHEMA")
    need(same(raw["base"].get("masks"), expected["base"]["masks"]), "ADJ_CACHE")
    need(same(raw["base"].get("cn"), expected["base"]["cn"]), "CN_CACHE")
    need(all(same(raw["base"].get(key), expected["base"][key]) for key in
             ("lambda_energy", "mu_energy", "root_residual")), "ENERGY_CACHE")
    need(all(same(raw.get(key), expected[key]) for key in ("universe", "u_roles", "v_roles", "k_choices", "per_uv", "total")), "ROLE_CACHE")
    need(same(raw, expected), "CACHE_SCHEMA", "remaining domain fields")


def domain(base):
    unchanged(base)
    need(base.E_lambda == 0, "RESTRICTED_LAMBDA_DOMAIN")
    neighbors = [x for x in range(base.n) if base.adjacency[base.root, x]]
    outsiders = [x for x in range(base.n) if x != base.root and not base.adjacency[base.root, x]]
    under = [x for x in outsiders if base.cn[base.root, x] == 1]
    over = [x for x in outsiders if base.cn[base.root, x] == 3]
    counts = {i: sum(x in neighbors for x in base.rows[i]) for i in base.mutable}
    need(all(x in (0, 1) for x in counts.values()), "RESTRICTED_LINE_CLASSES")
    zero = [i for i in base.mutable if counts[i] == 0]
    one = [i for i in base.mutable if counts[i] == 1]
    uro = sorted((x, i, at) for i in zero for at, x in enumerate(base.rows[i]) if x in under)
    vro = sorted((x, i, at) for i in one for at, x in enumerate(base.rows[i]) if x in over)
    need(len(one) == 2 * base.degree * (base.degree - 1), "RESTRICTED_INCIDENCE_COUNTS")
    need(all(sum(x == u for x, _, _ in uro) == base.degree - 1 for u in under)
         and all(sum(x == v for x, _, _ in vro) == 3 for v in over), "RESTRICTED_ROLE_COUNTS")
    roles = tuple((i, j, k, ix, jy, kz) for _, i, ix in uro for _, j, jy in vro
                  for k in zero if k != i for kz in range(3))
    need(len(roles) == len(uro) * len(vro) * max(0, len(zero) - 1) * 3, "RESTRICTED_POPULATION")
    universe = dict(schema="FROZEN_ROOT_CN1_CN3_ORIENTED_ROLE_UNIVERSE_V1", root=base.root,
        root_neighbors=neighbors, root_outsiders=outsiders, under_vertices=under, over_vertices=over,
        zero_neighbor_lines=zero, one_neighbor_lines=one, under_incidence_roles=[list(x) for x in uro],
        over_incidence_roles=[list(x) for x in vro], proposal_count=len(roles),
        order="u roles lex(u,i,ix), then v roles lex(v,j,jy), then k zero-neighbor original label excluding i, then kz 0,1,2",
        orientation="i:u->w; j:v->u; k:w->v", validity_filter_applied=False,
        role_count_unit="Role-labelled selections before all validity filters; no adjacency/isomorphism collapse",
        expected_root_residual_delta_if_valid=-2)
    return dict(base=base, roles=roles, universe=universe)


RECORD_KEYS = set("schema proposal_id role old_triples new_triples valid invalid_reason conflict_pair toggles changed_root_counts delta_lambda delta_mu new_lambda new_mu new_root_residual root_residual_delta frozen_root_unchanged classification mu_direction".split())


def literal_cycle(base, role, pid=None):
    """All final triple rows/pairs are rebuilt, even unchanged rows.

    Allows arbitrary mutable three-line roles; repeated selected values are
    explicit invalid_selection in this protocol's narrow distinct-value scope.
    """
    need(type(role) in (tuple, list) and len(role) == 6 and all(integer(x) for x in role), "ROLE_TYPES")
    i, j, k, ix, jy, kz = role
    need(all(0 <= x < len(base.rows) for x in (i, j, k)) and all(0 <= x < 3 for x in (ix, jy, kz)), "ROLE_RANGE")
    need(len({i, j, k}) == 3 and all(x in base.mutable for x in (i, j, k)), "ROLE_MUTABLE_LINES")
    need(pid is None or integer(pid) and pid >= 0, "PROPOSAL_ID")
    old = [list(base.rows[x]) for x in (i, j, k)]
    u, v, w = old[0][ix], old[1][jy], old[2][kz]
    record = dict(schema="FROZEN_ROOT_RESTRICTED_THREE_LINE_ROLE_RECORD_V1", proposal_id=pid,
        role=dict(u=u, i=i, ix=ix, v=v, j=j, jy=jy, w=w, k=k, kz=kz), old_triples=old,
        new_triples=None, valid=False, invalid_reason=None, conflict_pair=None, toggles=None,
        changed_root_counts=None, delta_lambda=None, delta_mu=None, new_lambda=None, new_mu=None,
        new_root_residual=None, root_residual_delta=None, frozen_root_unchanged=None,
        classification=None, mu_direction=None)
    if len({u, v, w}) < 3:
        record.update(invalid_reason="selected_points_not_distinct", classification="invalid_selection")
        return record, None, None
    changed = [list(row) for row in base.rows]
    changed[i][ix], changed[j][jy], changed[k][kz] = w, u, v
    new = [changed[x] for x in (i, j, k)]
    record["new_triples"] = new
    if any(len(set(row)) < 3 for row in changed):
        record.update(invalid_reason="receiving_triple_duplicate_point", classification="invalid_selection")
        return record, None, None
    # Reconstruct WHOLE final pair multiplicities. The first duplicate's label
    # is a diagnostic only, derived by subtracting the new occurrences from
    # the whole multiset then counting preceding occurrences in literal order.
    final_counts = Counter(tuple(sorted(edge)) for row in changed for edge in combinations(row, 2))
    new_sequence = [tuple(sorted((row[at], x))) for row, at in zip(new, (ix, jy, kz))
                    for other, x in enumerate(row) if other != at]
    if any(count > 1 for count in final_counts.values()):
        new_occurrences, preceding = Counter(new_sequence), Counter()
        first = None
        for edge in new_sequence:
            if final_counts[edge] - new_occurrences[edge] + preceding[edge] >= 1:
                first = list(edge); break
            preceding[edge] += 1
        need(first is not None, "PAIR_CONFLICT_RECONSTRUCTION")
        record.update(invalid_reason="new_pair_already_present", conflict_pair=first, classification="invalid_linearity")
        return record, None, None
    adjacency = geometry(base.n, base.degree, changed, base.root)
    cn, el, em, rr = score(adjacency, base.root)
    old_set = {tuple(sorted(edge)) for row in base.rows for edge in combinations(row, 2)}
    new_set = set(final_counts)
    toggles = [list(edge) for edge in sorted(old_set ^ new_set)]
    root_changes = [[x, int(base.cn[base.root, x]), int(cn[base.root, x])] for x in range(base.n)
                    if x != base.root and base.cn[base.root, x] != cn[base.root, x]]
    frozen = tuple((at, *row) for at, row in enumerate(changed) if base.root in row)
    need(frozen == base.frozen and np.array_equal(adjacency[base.root], base.adjacency[base.root]), "FROZEN_INVARIANT")
    dr, dm = rr - base.R_root, em - base.E_mu
    classification = "valid_lambda_changed" if el != base.E_lambda else "valid_lambda_preserving_root_" + (
        "down" if dr < 0 else "up" if dr > 0 else "equal")
    record.update(valid=True, toggles=toggles, changed_root_counts=root_changes,
        delta_lambda=el - base.E_lambda, delta_mu=dm, new_lambda=el, new_mu=em,
        new_root_residual=rr, root_residual_delta=dr, frozen_root_unchanged=True,
        classification=classification, mu_direction="down" if dm < 0 else "up" if dm > 0 else "equal")
    return record, adjacency, cn


def expected_record(d, pid):
    need(integer(pid) and 0 <= pid < len(d["roles"]), "PROPOSAL_ID")
    record, adjacency, cn = literal_cycle(d["base"], d["roles"][pid], pid)
    if record["valid"]:
        role = record["role"]
        need(record["changed_root_counts"] == sorted([[role["u"], 1, 2], [role["v"], 3, 2]])
             and record["root_residual_delta"] == -2, "RESTRICTED_ROOT_INVARIANT")
    return record, adjacency, cn


FIELD_STAGES = {
    "schema": "RECORD_SCHEMA", "proposal_id": "RECORD_ID", "role": "RECORD_ROLE",
    "old_triples": "RECORD_TOPOLOGY", "new_triples": "RECORD_TOPOLOGY", "conflict_pair": "RECORD_TOPOLOGY",
    "toggles": "RECORD_TOPOLOGY", "valid": "RECORD_STATUS", "invalid_reason": "RECORD_STATUS",
    "classification": "RECORD_STATUS", "mu_direction": "RECORD_STATUS", "delta_lambda": "RECORD_SCORE",
    "delta_mu": "RECORD_SCORE", "new_lambda": "RECORD_SCORE", "new_mu": "RECORD_SCORE",
    "changed_root_counts": "RECORD_ROOT_CUT", "new_root_residual": "RECORD_ROOT_CUT",
    "root_residual_delta": "RECORD_ROOT_CUT", "frozen_root_unchanged": "RECORD_ROOT_CUT"}


def check_record(d, pid, raw):
    expected, adjacency, cn = expected_record(d, pid)
    need(type(raw) is dict and set(raw) == RECORD_KEYS, "RECORD_SCHEMA")
    for key in expected:
        need(same(raw[key], expected[key]), FIELD_STAGES[key], key)
    return expected, adjacency, cn


class Aggregate:
    def __init__(self):
        self.counts = Counter(); self.mu = Counter(); self.unique = set(); self.accepted = set()
        self.minimum_root = None; self.root_ties = []; self.minimum_pair = None; self.pair_ties = []; self.zero = []

    def add(self, r):
        self.counts[r["classification"]] += 1
        if not r["valid"]:
            return
        key = tuple(tuple(edge) for edge in r["toggles"])
        self.unique.add(key)
        if r["new_lambda"] == 0:
            self.accepted.add(key); self.mu[r["mu_direction"]] += 1
            root = r["new_root_residual"]
            if self.minimum_root is None or root < self.minimum_root:
                self.minimum_root = root; self.root_ties = [r]
            elif root == self.minimum_root:
                self.root_ties.append(r)
            pair = (root, r["new_mu"])
            if self.minimum_pair is None or pair < self.minimum_pair:
                self.minimum_pair = pair; self.pair_ties = [r]
            elif pair == self.minimum_pair:
                self.pair_ties.append(r)
        if r["new_lambda"] == r["new_mu"] == 0:
            self.zero.append(r["proposal_id"])

    def snapshot(self):
        return dict(counts=dict(sorted(self.counts.items())), lambda_preserving_mu_directions=dict(sorted(self.mu.items())),
            unique_valid_neighbor_graphs=len(self.unique), unique_lambda_preserving_graphs=len(self.accepted),
            minimum_root_residual=self.minimum_root, minimum_root_proposal_ids=[r["proposal_id"] for r in self.root_ties],
            minimum_eligible_pair=None if self.minimum_pair is None else list(self.minimum_pair),
            minimum_pair_proposal_ids=[r["proposal_id"] for r in self.pair_ties], zero_score_proposal_ids=self.zero)


def relative_file(workspace, value, allowed_root):
    need(type(value) is str and value and "\\" not in value and not value.startswith("/")
         and ":" not in value and all(x not in ("", ".", "..", ".git") for x in value.split("/")), "ARTIFACT_PATH")
    path = (workspace / value).resolve()
    need(path.is_relative_to(allowed_root.resolve()) and path.is_file(), "ARTIFACT_PATH")
    return path


PART_KEYS = set("path start end record_count raw_bytes raw_sha256 gzip_bytes gzip_sha256".split())


def part_records(workspace, allowed_root, part):
    need(type(part) is dict and set(part) == PART_KEYS and type(part["path"]) is str
         and all(integer(part[key]) and part[key] >= 0 for key in ("start", "end", "record_count", "raw_bytes", "gzip_bytes"))
         and part["end"] - part["start"] == part["record_count"] <= 5000
         and part["raw_bytes"] <= 8192 * part["record_count"]
         and all(type(part[key]) is str and re.fullmatch("[0-9a-f]{64}", part[key]) for key in ("raw_sha256", "gzip_sha256")), "PART_TYPES")
    path = relative_file(workspace, part["path"], allowed_root)
    need(path.stat().st_size == part["gzip_bytes"] and sha(path) == part["gzip_sha256"], "PART_COMPRESSED_HASH")
    digest, raw_bytes, records = hashlib.sha256(), 0, []
    try:
        with gzip.open(path, "rb") as stream:
            while True:
                raw = stream.readline(8193)
                if not raw:
                    break
                need(len(raw) <= 8192 and raw.endswith(b"\n") and len(records) < part["record_count"], "PART_LENGTH")
                value = strict_json(raw)
                need(canonical(value) == raw, "PART_CANONICAL_JSON")
                digest.update(raw); raw_bytes += len(raw); records.append(value)
    except (gzip.BadGzipFile, EOFError, OSError) as error:
        raise AuditError("PART_GZIP", "decompression failed") from error
    need(len(records) == part["record_count"] and raw_bytes == part["raw_bytes"]
         and digest.hexdigest() == part["raw_sha256"], "PART_RAW_HASH")
    need(all(type(r) is dict and integer(r.get("proposal_id")) for r in records)
         and [r["proposal_id"] for r in records] == list(range(part["start"], part["end"])), "PART_SEQUENCE")
    return records


def checkpoint(value, identity, parts, end, aggregate):
    need(type(value) is dict and set(value) == {"schema", "identity", "next_proposal_id", "parts", "aggregate"}
         and integer(value["next_proposal_id"]) and type(value["parts"]) is list and type(value["aggregate"]) is dict,
         "CHECKPOINT_TYPES")
    need(value["schema"] == "FROZEN_ROOT_RESTRICTED_THREE_LINE_CHECKPOINT_V1"
         and same(value["identity"], identity), "CHECKPOINT_IDENTITY")
    need(value["next_proposal_id"] == end and same(value["parts"], parts), "CHECKPOINT_PREFIX")
    need(same(value["aggregate"], aggregate), "CHECKPOINT_AGGREGATE")


MANIFEST_KEYS = set("schema identity universe population completed_proposals starting_proposal_id proposals_evaluated_this_invocation parts checkpoints status budget_stop aggregate selected_proposal_id baseline selection_rule producer independent_approval target_resolution historical_native_state_written limitations".split())


def audit_run(workspace, allowed_root, d, manifest, identity, reserve=lambda: None):
    """Complete raw replay of one whole/prefix/resumed manifest.

    expected identity is caller-reconstructed from fixed source/software/fixture
    pins, never copied unchecked from the producer's manifest.  Every resumed
    prefix record is independently checked again against the original input.
    """
    unchanged(d["base"])
    need(type(manifest) is dict and set(manifest) == MANIFEST_KEYS
         and manifest.get("schema") == "FROZEN_ROOT_RESTRICTED_THREE_LINE_MANIFEST_V1", "MANIFEST_SCHEMA")
    need(same(manifest.get("identity"), identity) and same(manifest.get("universe"), d["universe"]), "MANIFEST_IDENTITY")
    need(all(integer(manifest.get(key)) and 0 <= manifest[key] <= len(d["roles"]) for key in (
        "population", "completed_proposals", "starting_proposal_id", "proposals_evaluated_this_invocation"))
        and manifest["population"] == len(d["roles"]) and manifest["starting_proposal_id"] <= manifest["completed_proposals"]
        and manifest["proposals_evaluated_this_invocation"] == manifest["completed_proposals"] - manifest["starting_proposal_id"], "MANIFEST_POPULATION")
    need(type(manifest.get("parts")) is list and type(manifest.get("checkpoints")) is list
         and type(manifest.get("budget_stop")) is bool and manifest.get("independent_approval") is False
         and manifest.get("historical_native_state_written") is False and manifest.get("target_resolution") == "NONE"
         and manifest.get("producer") == "/root/native_driver"
         and manifest.get("selection_rule") == "Among valid lambda0 proposals minimize root R, then global E_mu, then role proposal ID; mu worsening remains eligible."
         and same(manifest.get("limitations"), ["ONE exact role-labelled CN1/CN3 oriented family on one frozen labelled graph only.",
            "Not all three-line moves, all root-descent moves, a connected move space, or any target exclusion.",
            "Incomplete raw prefix cannot establish absence; exact zero still requires independent full99 integer SRG validation."]), "MANIFEST_TYPES")
    base = d["base"]
    need(same(manifest.get("baseline"), dict(E_lambda=base.E_lambda, E_mu=base.E_mu, R_root=base.R_root)), "MANIFEST_BASELINE")
    aggregate, prefix_parts, end, snapshots, seen_paths = Aggregate(), [], 0, {}, set()
    for part in manifest["parts"]:
        reserve(); unchanged(base)
        records = part_records(workspace, allowed_root, part)
        need(part["start"] == end and part["path"] not in seen_paths and part["end"] <= manifest["completed_proposals"], "PART_COVERAGE")
        seen_paths.add(part["path"])
        for raw in records:
            if raw["proposal_id"] % 32 == 0:
                reserve()
            expected, _, _ = check_record(d, raw["proposal_id"], raw)
            aggregate.add(expected)
        prefix_parts.append(part); end = part["end"]
        snapshots[end] = (list(prefix_parts), aggregate.snapshot())
        unchanged(base)
    need(end == manifest["completed_proposals"] and same(aggregate.snapshot(), manifest.get("aggregate")), "MANIFEST_AGGREGATE")
    if not snapshots:
        snapshots[0] = ([], aggregate.snapshot())
    seen_cp, checked_cp = set(), []
    for ref in manifest["checkpoints"]:
        reserve()
        need(type(ref) is dict and set(ref) == {"path", "sha256"} and ref["path"] not in seen_cp, "CHECKPOINT_REFERENCE")
        path = relative_file(workspace, ref["path"], allowed_root)
        need(sha(path) == ref["sha256"], "CHECKPOINT_HASH")
        value = strict_json(path.read_bytes())
        need(type(value) is dict and integer(value.get("next_proposal_id"))
             and value["next_proposal_id"] in snapshots, "CHECKPOINT_COVERAGE")
        at = value["next_proposal_id"]; parts, snap = snapshots[at]
        checkpoint(value, identity, parts, at, snap)
        seen_cp.add(ref["path"]); checked_cp.append(at)
    # Resumed manifests list only their newly emitted CPs; prefix parts still
    # need replay. Empty prefixes have one explicit zero checkpoint.
    needed_cp = [part["end"] for part in manifest["parts"] if part["start"] >= manifest["starting_proposal_id"]]
    if not needed_cp:
        needed_cp = [manifest["completed_proposals"]]
    need(checked_cp == needed_cp, "CHECKPOINT_COVERAGE")
    complete = end == len(d["roles"])
    need(manifest.get("status") == ("CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK" if complete else "UNKNOWN_PREFIX_ONLY"), "MANIFEST_STATUS")
    selected = min(aggregate.pair_ties, key=lambda r: r["proposal_id"]) if aggregate.pair_ties else None
    need(same(manifest.get("selected_proposal_id"), None if selected is None else selected["proposal_id"]), "MANIFEST_SELECTION")
    unchanged(base)
    return dict(aggregate=aggregate, snapshots=snapshots, complete_records=end, checkpoints=checked_cp, selected=selected)


def audit_ties(run_dir, d, result):
    aggregate, selected = result["aggregate"], result["selected"]
    for filename, records, scope in [
        ("minimum_root_ties.json", aggregate.root_ties,
         "All lambda-preserving proposals tied at minimum R_root among this saved role prefix; mu worsening remains eligible."),
        ("minimum_pair_ties.json", aggregate.pair_ties,
         "All lambda-preserving proposals tied at minimum (R_root,E_mu) among this saved role prefix.")]:
        value = strict_json((run_dir / filename).read_bytes())
        need(same(value, dict(records=records, scope=scope)), "TIE_RECORDS", filename)
    if selected is None:
        need(not (run_dir / "selected_neighbor.adj").exists()
             and not (run_dir / "selected_neighbor_triples.json").exists(), "SELECTED_ABSENCE")
        return
    expected, adjacency, _ = expected_record(d, selected["proposal_id"])
    need((run_dir / "selected_neighbor.adj").read_bytes() == matrix_bytes(adjacency), "SELECTED_MATRIX")
    b = d["base"]
    rows = [list(row) for row in b.rows]
    for key, row in zip(("i", "j", "k"), expected["new_triples"]):
        rows[expected["role"][key]] = row
    value = strict_json((run_dir / "selected_neighbor_triples.json").read_bytes())
    need(same(value, dict(n=b.n, degree=b.degree, root=b.root, frozen_rows=[list(row) for row in b.frozen],
         mutable_labels=list(b.mutable), triples=rows, proposal_id=selected["proposal_id"],
         historical_native_state_written=False)), "SELECTED_TRIPLES")
