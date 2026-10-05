"""Independent Hall derivation/raw checks for the unrestricted one-star theorem.

Only Python's standard library is imported. No producer or previous checker
implementation supplies labels, matching, graph construction, or pair counts.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = "acceleration/results/20260930_unrestricted_star_matching_redundancy/run01/"
OUT = ROOT / "acceleration/results/20260930_independent_review/unrestricted_star_matching"
SUMMARY_SHA = "8d4bd393abe3325dc3da628e61f50fad74247d26111c0cab3608e8bd03410b07"
DERIVATION = "docs/AUDIT_20260930_UNRESTRICTED_STAR_MATCHING_REDUNDANCY.md"
LABELS = [tuple(p) for p in combinations(range(14), 2) if p[0]//2 != p[1]//2]
INDEX = {p: i+15 for i, p in enumerate(LABELS)}
U = (0, 2)
CENTER = INDEX[U]
QUOTAS = [1]*4+[2]*10


def need(test, message):
    if not test:
        raise ValueError(message)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def star_ok(star):
    need(len(star) == len(set(star)) == 12 and U not in star, "distinct twelve noncenter labels")
    need(all(p in INDEX for p in star), "valid outer labels")
    need([sum(s in p for p in star) for s in range(14)] == QUOTAS, "exact quotas")
    residual = sorted(p for p in star if not set(p).intersection(U))
    need(len(residual) == 10, "ten residual labels")
    need(all(sum(bool(set(p).intersection(q)) for q in residual if q != p) <= 2 for p in residual), "residual intersection degree")
    return residual


def bipartite_matching(left, right, allowed):
    assigned = {}
    def augment(x, visited):
        for y in right:
            if y in visited or not allowed(x, y):
                continue
            visited.add(y)
            if y not in assigned or augment(assigned[y], visited):
                assigned[y] = x
                return True
        return False
    for x in left:
        if not augment(x, set()):
            return None
    return sorted((x, y) for y, x in assigned.items())


def independent_matching(star):
    residual = star_ok(star)
    left, right = residual[:5], residual[5:]
    allowed = lambda p, q: not set(p).intersection(q)
    need(all(sum(allowed(p, q) for q in right) >= 3 for p in left), "left bipartite degree")
    need(all(sum(allowed(p, q) for p in left) >= 3 for q in right), "right bipartite degree")
    # Finite verification of Hall inequalities for this sampled instance is
    # supplementary. The written universal proof applies to every instance.
    for mask in range(1, 32):
        subset = [p for i, p in enumerate(left) if mask >> i & 1]
        neighbors = {q for q in right if any(allowed(p, q) for p in subset)}
        need(len(neighbors) >= len(subset), "sampled Hall inequality")
    result = bipartite_matching(left, right, allowed)
    need(result is not None, "independent matching")
    return result


def scaffold_edges():
    edges = {tuple(sorted((0, 1+s))) for s in range(14)}
    edges.update((1+s, 2+s) for s in range(0, 14, 2))
    edges.update(tuple(sorted((1+s, INDEX[p]))) for p in LABELS for s in p)
    return edges


SCAFFOLD = scaffold_edges()


def raw(star, matching):
    residual = star_ok(star)
    vertices = [p for edge in matching for p in edge]
    need(len(matching) == 5 and len(vertices) == len(set(vertices)) == 10 and set(vertices) == set(residual), "matching coverage")
    need(all(not set(p).intersection(q) for p, q in matching), "disjoint matching partners")
    edges = SCAFFOLD | {tuple(sorted((CENTER, INDEX[p]))) for p in star}
    edges |= {tuple(sorted((INDEX[p], INDEX[q]))) for p, q in matching}
    matrix = [[0]*99 for _ in range(99)]
    for i, j in edges:
        matrix[i][j] = matrix[j][i] = 1
    return matrix


def inspect(matrix, star):
    need(len(matrix) == 99 and all(type(row) is list and len(row) == 99 for row in matrix), "raw99 shape")
    need(all(type(matrix[i][j]) is int and matrix[i][j] in (0, 1) and matrix[i][j] == matrix[j][i]
             and (i != j or matrix[i][j] == 0) for i in range(99) for j in range(99)), "simple raw99 matrix")
    need(all(matrix[i][j] == int((i, j) in SCAFFOLD) for i, j in combinations(range(99), 2) if i < 15), "full scaffold present/absent entries")
    neighbors = [{j for j, bit in enumerate(row) if bit} for row in matrix]
    need(neighbors[CENTER] == {1, 3} | {INDEX[p] for p in star}, "complete center neighborhood")
    need(all(len(neighbors[i]) <= 14 for i in range(99)), "degree caps")
    need(all(len(neighbors[i] & neighbors[CENTER]) == 1 for i in neighbors[CENTER]), "induced neighborhood matching")
    need(all(len(neighbors[CENTER] & neighbors[s+1])+matrix[CENTER][s+1] == 2 for s in range(14)), "fourteen center-inner equalities")
    maximum = 0
    for i, j in combinations(range(99), 2):
        value = len(neighbors[i] & neighbors[j])+matrix[i][j]
        need(value <= 2, "known pair cap")
        maximum = max(maximum, value)
    need(sum(map(len, neighbors))//2 == 206, "exact known-edge count")
    return dict(unordered_pairs=4851, max_pair_value=maximum, degree_distribution=dict(sorted(Counter(map(len, neighbors)).items())), known_edges=206)


def categories():
    selected_cases = 0
    maxima = Counter()
    other = [p for p in LABELS if p != U]
    residual = [p for p in other if not set(p).intersection(U)]
    for y in other:
        partners = [None] if set(y).intersection(U) else [p for p in residual if not set(p).intersection(y)]
        for partner in partners:
            for s in range(14):
                value = int((s ^ 1) in y)+int(s in U)+int(partner is not None and s in partner)+int(s in y)
                need(value <= 2, "inner-selected symbolic category")
                maxima["inner_selected_maximum"] = max(maxima["inner_selected_maximum"], value)
                selected_cases += 1
    outer_cases = 0
    for x, y in combinations(other, 2):
        common_inner = len(set(x).intersection(y))
        for x_selected, y_selected in ((False, False), (False, True), (True, False), (True, True)):
            # A matching edge is possible only between selected residuals
            # with disjoint labels; also check their nonedge option.
            edge_options = (0, 1) if x_selected and y_selected and x in residual and y in residual and not common_inner else (0,)
            for edge in edge_options:
                value = common_inner+int(x_selected and y_selected)+edge
                need(value <= 2, "outer-outer symbolic category")
                outer_cases += 1
    center_cases = 0
    for y in other:
        shared = len(set(U).intersection(y))
        for selected in (False, True):
            partner = int(selected and not shared)
            value = shared+partner+int(selected)
            need(value <= 2 and (not selected or value == 2), "center-outer symbolic category")
            center_cases += 1
    need(all(QUOTAS[s]+int(s in U)+int((s^1) in U) == 2 for s in range(14)), "center-inner symbolic category")
    return dict(inner_selected_local_cases=selected_cases, outer_pair_role_cases=outer_cases,
                center_outer_cases=center_cases, center_inner_cases=14,
                population="Local labels and roles appearing in the proof formulas; not complete stars or target graphs", **maxima)


def main():
    need(not OUT.exists(), "refuse overwrite")
    bindings = {}
    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute(): p = ROOT/p
        value = digest(p)
        need(expected is None or value == expected, "artifact hash: "+str(path))
        bindings[p.relative_to(ROOT).as_posix()] = value
        return p
    def read(path, expected=None):
        return json.loads(bind(path, expected).read_text(encoding="utf-8"))
    summary = read(RUN+"summary.json", SUMMARY_SHA)
    for name, expected in summary["artifact_hashes"].items(): bind(RUN+name, expected)
    manifest = read(RUN+"manifest.json")
    for path, expected in manifest["inputs_sha256"].items(): bind(path, expected)
    model = read("acceleration/results/20260930_unrestricted_full99_cnf/model.json")
    need(model["outer_labels"] == [list(p) for p in LABELS], "independent label order")
    expected_known = [[int(i != j and tuple(sorted((i, j))) in SCAFFOLD) if min(i, j) < 15 or i == j else -1 for j in range(99)] for i in range(99)]
    need(model["known_adjacency_full99"] == expected_known, "independent unrestricted fixed/free scaffold")
    normalization = read(model["normalization_audit"], model["normalization_audit_sha256"])
    bind("acceleration/results/20260917_independent_review/ROOT_SCAFFOLD_DERIVATION.md", "a45fa5c52f3b348e8fb41b347925a363bb79e4d6389f60f760ec85e6cfe8f077")
    records = read(RUN+"records.json")
    need(len(records) == summary["sampled_star_sets"] == 128, "record population")
    results, unique, branches = [], set(), Counter()
    matched_fixtures = 0
    for number, record in enumerate(records):
        star = [tuple(p) for p in record["star_labels"]]
        matching = [tuple(tuple(p) for p in edge) for edge in record["matching_labels"]]
        original = raw(star, matching)
        original_result = inspect(original, star)
        independent = independent_matching(star)
        independent_result = inspect(raw(star, independent), star)
        if record["raw_fixture"]:
            fixture = read(RUN+record["raw_fixture"])
            need(fixture["known_edge_adjacency"] == original and fixture["center"] == CENTER, "raw fixture entire matrix identity")
            matched_fixtures += 1
        unique.add(tuple(sorted(star))); branches[record["branch"]] += 1
        results.append(dict(record_index=number, branch=record["branch"], star_labels=star,
                            independently_constructed_matching=independent, producer_raw_check=original_result,
                            independent_raw_check=independent_result))
    need(len(unique) == 128 and dict(branches) == summary["per_branch"] and matched_fixtures == 4, "saved population distinctions")
    # A deterministic fixture with no producer's optional anchor (4,6).
    fixture_star = [(0,4),(2,6),(1,5),(3,7),(4,8),(5,9),(6,10),(7,11),(8,12),(9,13),(10,12),(11,13)]
    need((4,6) not in fixture_star, "independent unanchored positive")
    fixture_matching = independent_matching(fixture_star)
    fixture_matrix = raw(fixture_star, fixture_matching)
    fixture_result = inspect(fixture_matrix, fixture_star)
    need(bipartite_matching(range(5), range(5,10), lambda x,y: True) is not None, "K5,5 matching positive")
    need(bipartite_matching(range(5), range(5,10), lambda x,y: x < 4) is None, "Hall-deficient matching negative")
    rejected = {}
    def reject(name, call):
        try: call()
        except ValueError as exc: rejected[name] = str(exc)
        else: raise ValueError("corruption accepted: "+name)
    reject("missing_star_label", lambda: star_ok(fixture_star[:-1]))
    reject("duplicate_star_label", lambda: star_ok(fixture_star[:-1]+[fixture_star[0]]))
    reject("center_as_neighbor", lambda: star_ok(fixture_star[:-1]+[U]))
    reject("invalid_same_pair_label", lambda: star_ok(fixture_star[:-1]+[(0,1)]))
    reject("wrong_symbol_quota", lambda: star_ok(fixture_star[:-1]+[(4,13)]))
    reject("repeated_matching_endpoint", lambda: raw(fixture_star, fixture_matching[:-1]+[fixture_matching[0]]))
    for label in ("diagonal", "nonbinary", "asymmetry", "missing_center_edge", "missing_matching_edge", "extra_intersecting_edge", "changed_scaffold"):
        bad = deepcopy(fixture_matrix)
        if label == "diagonal": bad[CENTER][CENTER] = 1
        elif label == "nonbinary": bad[0][1] = bad[1][0] = 2
        elif label == "asymmetry": bad[0][1] = 0
        elif label == "missing_center_edge":
            v = INDEX[fixture_star[0]]; bad[CENTER][v] = bad[v][CENTER] = 0
        elif label == "missing_matching_edge":
            x,y = map(INDEX.get,fixture_matching[0]); bad[x][y] = bad[y][x] = 0
        elif label == "extra_intersecting_edge":
            a,b = next((a,b) for a,b in combinations(fixture_star,2) if set(a).intersection(b))
            x,y = INDEX[a],INDEX[b]; bad[x][y] = bad[y][x] = 1
        else: bad[0][1] = bad[1][0] = 0
        reject(label, lambda bad=bad: inspect(bad, fixture_star))
    category_results = categories()
    OUT.mkdir(parents=True, exist_ok=False)
    for name, content in (("sample_checks.json", results), ("independent_unanchored_fixture.json", dict(star_labels=fixture_star, matching_labels=fixture_matching, known_edge_adjacency=fixture_matrix))):
        with (OUT/name).open("x", encoding="utf-8") as stream: json.dump(content, stream, indent=2); stream.write("\n")
        bind(OUT/name)
    bind(DERIVATION); bind(__file__)
    report = dict(status="INDEPENDENT_UNRESTRICTED_ONE_STAR_MATCHING_REDUNDANCY_PASS", timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
        claim_id="C-UNRESTRICTED-ONE-STAR-MATCHING-REDUNDANCY", claim_revision=1,
        verifier="/root/state_literature_audit independent derivation and raw-artifact checking agent",
        recommendation="VERIFIED", review_state="CLEAR", kind="mathematical result", basis=["DERIVED","COMPUTED"],
        statement="For every set S of12 distinct outer labels excluding u={0,2} in the unrestricted root scaffold, with symbol incidences1 on0,1,2,3 and2 on4 through13, there exists a specification of the induced neighborhood N(u) as7K2 and a99vertex known-present graph P with u adjacent to exactly S among outer vertices, every degree at most14, and |N_P(x) intersect N_P(y)|+P_xy<=2 for every distinct x,y. No outer edges beyond the root scaffold and this one star/matching are initially prescribed.",
        scope="Universal conditional local-consistency theorem for one quota-compliant star in the unrestricted root scaffold. No completion to a target is established; no additional fixed outer edges or multiple completed stars are covered.",
        assumptions=["The root scaffold has its exact fourteen inner symbols in seven mate pairs and all84 distinct cross-pair outer labels.", "Exactly the stated quotas and distinctness on S; all other outer entries are initially unspecified.", "No nontrivial target automorphism or target asymmetry is assumed."],
        dependencies=[dict(id="C-ROOT-SCAFFOLD-NORMALIZATION",revision=1,relation="normalization")],
        written_audit=DERIVATION, inputs_sha256=bindings,
        proof_method="Separate Hall proof using any5+5 residual partition; full symbolic case division for all root/inner/outer pair types and exact degree counts",
        sample_checks=dict(population="The producer's saved finite128 stars only", records=len(records), unique_stars=len(unique), branches=dict(branches),
            saved_raw_fixtures_compared=matched_fixtures, producer_matching_graphs_checked=128, independently_matched_graphs_checked=128,
            raw_pair_cap_evaluations=256*4851, hall_subsets_checked=128*31, universal_proof_from_samples=False),
        category_falsification=category_results,
        controls=dict(independent_unanchored_positive=fixture_result, complete_bipartite_matching_positive=True,
            Hall_deficient_matching_rejected=True, corruptions_rejected=rejected),
        producer_imported=False, shared_components=["Python standard library exact arithmetic, JSON and SHA256", "Raw saved star/matching artifacts and immutable root-normalization audit"],
        limitations=["The universal theorem is established by written derivation, not the128 sampled records or category-case counts.",
            "Displayed zeros outside fully specified scaffold/center/neighborhood entries denote unknown target adjacencies.",
            "No target graph, unrestricted nonexistence proof, full-star census, novelty claim, or external peer review.",
            "Conditional matching filters with additional fixed outer edges are not rendered redundant."],
        overall_search_coverage="UNKNOWN; no validated denominator.", solver_calls=0, target_resolution=False, external_review=False, artifact_availability="LOCAL_ONLY")
    need(all(digest(ROOT/path) == expected for path,expected in bindings.items()), "all bound bytes stable")
    with (OUT/"summary.json").open("x", encoding="utf-8") as stream: json.dump(report,stream,indent=2);stream.write("\n")
    print(json.dumps(dict(status=report["status"],sha256=digest(OUT/"summary.json"),sample_checks=report["sample_checks"],category_falsification=category_results),indent=2))


if __name__ == "__main__":
    main()
