"""Exact full99 controls for replacing an entire matching by binary Y.

No MIP, new model producer, or optimization package is imported. X controls
are exact quarters in [0,1]; they need not satisfy the completion constraints.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random

from audit_certificate import full_graph, require
from audit_phase1 import evaluate


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_new(path, data):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--atomic-proposals", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve previous indicator controls")
    outdir = args.out.parent / (args.out.stem + "_controls")
    outdir.mkdir(parents=True, exist_ok=False)
    base = json.loads(args.base.read_bytes())
    proposals = json.loads(args.atomic_proposals.read_bytes())
    original, unknown = full_graph(base)
    labels = [{v-1 for v in original[u+15] if 1 <= v <= 14} for u in range(84)]
    supports = [{s//2 for s in label} for label in labels]
    root = 3

    def in_class(edge, kind):
        u, v = edge
        if supports[u] & supports[v] != {root}:
            return False
        signs = [next(s%2 for s in labels[w] if s//2 == root) for w in (u,v)]
        return (signs[0] != signs[1]) if kind == "cross" else signs == [0,0]

    unknown_order = sorted(unknown)
    rng = random.Random(20260924)
    x_controls = dict(zero=[0]*1680, one=[4]*1680,
                      quarter_pattern=[i%5 for i in range(1680)],
                      random_quarters=[rng.randrange(5) for _ in range(1680)])
    records, counterexamples, input_hashes = [], {}, {str(args.base): digest(args.base), str(args.atomic_proposals): digest(args.atomic_proposals)}
    total_partial, total_caps, total_labels, total_indicators = 0,0,0,0
    for kind in ("cross", "same_0"):
        old_matching = {tuple(edge) for edge in base["overlap_edges_outer_zero_based"] if in_class(edge, kind)}
        require(len(old_matching) == (12 if kind == "cross" else 6), "Wrong entire matching size")
        selected_index = next(i for i, move in enumerate(proposals["moves"])
                              if move["root_group"] == root and move["matching_class"] == kind and move["cycle_size"] == 3)
        changed = {"overlap_edges_outer_zero_based": proposals["overlap_candidates"][selected_index]}
        changed_path = outdir / (kind + "_atomic_candidate.json")
        write_new(changed_path, dict(changed, provenance=dict(base=str(args.base), proposal_index=selected_index,
                                                           move=proposals["moves"][selected_index])))
        input_hashes[str(changed_path)] = digest(changed_path)
        b = [set(row) for row in original]
        for u,v in old_matching:
            b[u+15].remove(v+15)
            b[v+15].remove(u+15)
        vertices = {u+15 for edge in old_matching for u in edge}
        partners = {u: [v for v in vertices if v != u and in_class(tuple(sorted((u-15,v-15))), kind)] for u in vertices}
        require(set(map(len, partners.values())) == {10}, "Expected10allowed partners per vertex")
        for y_name, candidate in (("initial_matching", base), ("atomic_changed_matching", changed)):
            known, candidate_unknown = full_graph(candidate)
            require(candidate_unknown == unknown, "Unknown X domain changed")
            y = [known[u]-b[u] for u in range(99)]
            require(all(b[u] <= known[u] and len(y[u]) == (1 if u in vertices else 0) for u in range(99)),
                    "Y is not a perfect matching on the selected vertices")
            require(all((v in y[u]) == (u in y[v]) for u in range(99) for v in range(99)), "Y not symmetric")
            partial_count = 0
            for u,v in combinations(range(99),2):
                require(not y[u] & y[v], "Offdiagonal Y squared is not zero")
                affine = len(b[u]&b[v]) + len(b[u]&y[v]) + len(y[u]&b[v]) + int(v in b[u]) + int(v in y[u])
                direct = len(known[u]&known[v]) + int(v in known[u])
                require(affine == direct <= 2, "Affine partial cap differs from full99 graph")
                partial_count += 1
            total_partial += partial_count
            for x_name, numbers in x_controls.items():
                q = [[0]*99 for _ in range(99)]
                for (u,v), number in zip(unknown_order,numbers):
                    q[u][v] = q[v][u] = number
                pair_residuals = []
                indicator_rows, nonlinear_pairs = 0,0
                for u,v in combinations(range(15,99),2):
                    h = 4*(len(b[u]&b[v]) + int(v in b[u])) + sum(q[w][v] for w in b[u]) + sum(q[u][w] for w in b[v]) + q[u][v]
                    direct = 4*(len(known[u]&known[v]) + int(v in known[u])-2) + sum(q[w][v] for w in known[u]) + sum(q[u][w] for w in known[v]) + q[u][v]
                    y_linear = 4*(len(b[u]&y[v]) + len(y[u]&b[v]) + int(v in y[u]))
                    y_x = sum(q[w][v] for w in y[u]) + sum(q[u][w] for w in y[v])
                    require(direct == h+y_linear+y_x-8, "Full99 necessary-cap expansion mismatch")
                    nonlinear = ((u in vertices and root not in supports[v-15]) or
                                 (v in vertices and root not in supports[u-15]))
                    if nonlinear:
                        a,c = (u,v) if u in vertices else (v,u)
                        selected = next(iter(y[a]))
                        g = {p: 4*int(p in b[c])+q[c][p] for p in partners[a]}
                        require(selected in g and all(0 <= value <= 4 for value in g.values()), "g not in exact[0,1] interval")
                        require(y_linear+y_x == g[selected], "Selected partner term was omitted or double counted")
                        shared = max([0,h-8]+[h+value+4*int(p == selected)-12 for p,value in g.items()])
                        target = max(0,h+g[selected]-8)
                        require(shared == target == max(0,direct), "Shared-indicator minimum slack differs from fixedK phase-I cap")
                        wrong_m0 = max([0,h-8]+[h+value-8 for value in g.values()])
                        separate = max(0,h-8)+sum(max(0,h+value+4*int(p == selected)-12) for p,value in g.items())
                        double_b = max(0,h+g[selected]+4*int(selected in b[c])-8)
                        for name, wrong in (("M_zero_overconstrains_unselected_partners",wrong_m0),
                                            ("separate_summed_slacks_change_objective",separate),
                                            ("double_counting_selected_B_partner_changes_slack",double_b)):
                            if wrong != target and name not in counterexamples:
                                counterexamples[name] = dict(matching_class=kind,Y_control=y_name,X_control=x_name,
                                    outer_pair=[a-15,c-15],selected_partner=selected-15,scale=4,H_numerator=h,
                                    g_numerators={str(p-15): val for p,val in g.items()},
                                    correct_shared_slack_numerator=target,wrong_slack_or_objective_numerator=wrong)
                        nonlinear_pairs += 1
                        indicator_rows += len(g)
                    else:
                        require(y_x == 0, "A supposedly affine pair contains a YX product")
                    pair_residuals.append(Fraction(direct,4))
                label_residuals = []
                labels_checked = 0
                for u in range(15,99):
                    for symbol in range(14):
                        s = symbol+1
                        target = 1 if s in known[u] else 2
                        direct = 4*(len(known[u]&known[s])-target)+sum(q[u][w] for w in known[s])
                        affine = 4*(len(b[u]&b[s])+len(y[u]&b[s])-target)+sum(q[u][w] for w in b[s])
                        require(direct == affine, "Label quota B/Y/X decomposition mismatch")
                        if symbol//2 not in supports[u-15]:
                            label_residuals.append(Fraction(direct,4))
                        else:
                            require(direct == 0, "Own-label quota not preserved by matching")
                        labels_checked += 1
                independent = evaluate(candidate,[value/4 for value in numbers],exact=True)
                require(independent["quota_residuals"] == label_residuals and independent["pair_residuals"] == pair_residuals,
                        "Full99 matrix residuals differ from independent graph-row evaluator")
                merit = sum(map(abs,label_residuals))+sum(max(0,value) for value in pair_residuals)
                require(merit == independent["total_violation"], "Phase-I objective differs")
                require(nonlinear_pairs == (1440 if kind == "cross" else 720), "Wrong nonlinear-pair support classification")
                records.append(dict(matching_class=kind,Y_control=y_name,X_control=x_name,
                                    exact_phase1_merit=str(merit), nonlinear_pairs=nonlinear_pairs,
                                    indicator_rows_checked=indicator_rows, pair_rows_checked=len(pair_residuals),
                                    all_label_coordinates_checked=labels_checked))
                total_caps += len(pair_residuals)
                total_labels += labels_checked
                total_indicators += indicator_rows
    require(len(counterexamples) == 3, "Missing requested real-graph negative controls")
    scalar_controls = 0
    for h in range(-4,25):
        for selected_g in range(5):
            for other_g in range(5):
                require(max(0,h-8,h+selected_g-8,h+other_g-12) == max(0,h+selected_g-8),
                        "Scalar shared-slack identity failed")
                scalar_controls += 1
    result = dict(status="INDEPENDENT_FULL99_MATCHING_INDICATOR_ALGEBRA_AND_SLACK_CONTROLS_PASS",
                  records=records, partial_graph_pair_equalities_checked=total_partial,
                  exact_joint_pair_rows_checked=total_caps, exact_label_coordinates_checked=total_labels,
                  exact_partner_indicator_rows_checked=total_indicators, scalar_quarter_controls=scalar_controls,
                  negative_controls=counterexamples, inputs_sha256=input_hashes,
                  sources_sha256={str(path): digest(path) for path in (Path(__file__),Path(__file__).with_name("audit_certificate.py"),
                                                                     Path(__file__).with_name("audit_phase1.py"))},
                  universal_binary_Y_proof=[
                      "Y is a matching, so every offdiagonal entry ofY^2 is zero; therefore(B+Y)^2+(B+Y) has affine offdiagonal known-part caps.",
                      "If u lies in chosen matching S and v does not contain its root group, Y has no row at v. The only omitted-Y contribution to H is g_selected=B_vp+X_vp, counted exactly once.",
                      "B_vp and X_vp have disjoint support, so0<=g_p<=1 for every allowed partner.",
                      "The selected indicator implies t>=H+g_selected-2. All unselected indicators are implied byH<=2+t andg_p<=1. Sinceg_selected>=0, the selected row also implies the baseline at integralY.",
                      "Together witht>=0 the exact minimum shared slack is max(0,H+g_selected-2). The baseline can strengthen fractionalY relaxation but no fractional/MIP bound is credited here."],
                  objective_scope="At fixed binary perfect-matching Y and box-feasible X, shared indicator slacks reproduce exactly the prior unweighted necessary phase-I objective. Partial graph caps must separately hold.",
                  solver_or_new_producer_imported=False, mip_bound_or_global_exclusion_claimed=False,
                  X_control_scope="Exactquarter box values; completion feasibility is not assumed.")
    write_new(args.out,result)
    print(json.dumps({key:value for key,value in result.items() if key not in ("records","inputs_sha256","sources_sha256","negative_controls","universal_binary_Y_proof")}))


if __name__ == "__main__":
    main()
