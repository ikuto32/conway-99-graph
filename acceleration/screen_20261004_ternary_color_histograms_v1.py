"""Exact necessary colour-histogram domain propagation; no graph construction."""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = "acceleration/screen_20261004_ternary_color_histograms_v1.py"
SPEC = "acceleration/screen_20261004_ternary_color_histograms_v1_spec.md"
SOFTWARE = {
    "acceleration/command_deadline.py": "9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9",
    "acceleration/run_compute_command_v2.py": "46410201dcad20eb056b8206a1b6687f9ac74f0f34e3cc66197eff5c59d55e17",
    "pyproject.toml": "273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339",
    "uv.lock": "a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db",
}
POPULATIONS = ((24,24,51),(24,27,48),(24,30,45),(24,33,42),(24,36,39),
               (27,27,45),(27,30,42),(27,33,39),(27,36,36),
               (30,30,39),(30,33,36),(33,33,33))


class Veto(ValueError):
    pass


def need(ok, stage):
    if not ok:
        raise Veto(stage)


def unique(items):
    out = {}
    for key, value in items:
        need(type(key) is str and key not in out, "DUPLICATE_KEY")
        out[key] = value
    return out


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write("\n")


class Context:
    def __init__(self, deadline, out):
        self.deadline, self.out, self.pins = deadline, out, {}
        self.progress = dict(completed_labels=0, active_label=None, phase="authentication")

    def tick(self):
        need(self.deadline.status()["remaining_seconds"] > 20, "SAVE_GUARD")

    def raw(self, name, wanted):
        self.tick()
        need(type(name) is str and "\\" not in name and not name.startswith("/")
             and ":" not in name and all(p not in ("", ".", "..") for p in name.split("/")), "INPUT_PATH")
        path = ROOT / name
        need(path.is_file() and all(not p.is_symlink() for p in (path, *path.parents))
             and path.resolve().is_relative_to(ROOT) and path.stat().st_size <= 50*1024*1024, "INPUT_PATH")
        data = path.read_bytes()
        need(type(wanted) is str and hashlib.sha256(data).hexdigest() == wanted, "INPUT_SHA")
        self.pins[name] = wanted
        self.tick()
        return data

    def json(self, ref):
        need(type(ref) is dict and set(ref) == {"path", "sha256"}, "REFERENCE")
        return json.loads(self.raw(ref["path"], ref["sha256"]), object_pairs_hook=unique)

    def checkpoint(self, name):
        self.tick()
        save(self.out / name, dict(progress=copy.deepcopy(self.progress), deadline=self.deadline.status()))
        self.tick()


def parameters(n, k, sizes):
    need(type(n) is int and type(k) is int and k > 0 and k % 2 == 0 and n == 1+k*k//2, "PARAMETERS")
    need(type(sizes) in (list, tuple) and len(sizes) == 3
         and all(type(s) is int and s > 0 and s % 3 == 0 for s in sizes)
         and sum(sizes) == n, "POPULATION")


def scalar(n, k, sizes, t):
    parameters(n, k, sizes)
    need(type(t) is int, "T_TYPE")
    need(t % 3 == 0, "T_DIVISIBILITY")
    need(0 <= t <= (k//2)*min(sizes), "T_RANGE")
    need(all(18*t >= s*(n-s) for s in sizes) if (n,k) == (99,14) else True, "SCALAR_RAYLEIGH")
    q = sizes[0]*sizes[1]+sizes[0]*sizes[2]+sizes[1]*sizes[2]
    z = []
    for i in range(3):
        j, ell = [a for a in range(3) if a != i]
        numerator = 3*(2*k+1)*t+6*sizes[j]*sizes[ell]-4*q
        need(numerator % 9 == 0, "SCALAR_Z_INTEGER")
        zi = numerator//9
        need(0 <= zi <= (k//2)*t, "SCALAR_Z_RANGE")
        z.append(zi)
    return z


def histogram(h, size, total, square, max_r):
    need(type(h) in (list, tuple) and len(h) == max_r+1, "HIST_SHAPE")
    need(all(type(a) is int and a >= 0 for a in h), "HIST_TYPE")
    need(sum(h) == size, "HIST_COUNT")
    need(sum(i*a for i,a in enumerate(h)) == total, "HIST_SUM")
    need(sum(i*i*a for i,a in enumerate(h)) == square, "HIST_SQUARES")


def residual_possible(count, total, square, lo, hi):
    if count == 0:
        return total == square == 0
    if not (lo*count <= total <= hi*count) or square % 2 != total % 2:
        return False
    base, rem = divmod(total, count)
    minimum = (count-rem)*base*base+rem*(base+1)*(base+1)
    if lo == hi:
        maximum = count*lo*lo
    else:
        top, leftover = divmod(total-lo*count, hi-lo)
        maximum = top*hi*hi+(count-top)*lo*lo
        if leftover:
            maximum += (lo+leftover)**2-lo*lo
    return minimum <= square <= maximum


def histograms(size, total, square, max_r, tick):
    def walk(r, count, remaining, squares, prefix):
        tick()
        if not residual_possible(count, remaining, squares, r, max_r):
            return
        if r == max_r:
            if remaining == r*count and squares == r*r*count:
                yield tuple(prefix+[count])
            return
        for number in range(count+1):
            yield from walk(r+1, count-number, remaining-r*number,
                            squares-r*r*number, prefix+[number])
    yield from walk(0, size, total, square, [])


def subset_sums(capacities, degree, tick):
    need(type(degree) is int and degree >= 0, "SELECTION_DEGREE")
    need(all(type(a) is int and a >= 0 for a in capacities), "SELECTION_CAPACITY")
    dp = [0]*(degree+1)
    dp[0] = 1
    for weight, capacity in enumerate(capacities):
        tick()
        nxt = [0]*(degree+1)
        for used, bits in enumerate(dp):
            if bits:
                for amount in range(min(capacity, degree-used)+1):
                    nxt[used+amount] |= bits << (weight*amount)
        dp = nxt
    return dp[degree]


def pool_sums(h, degree, tick, own_r=None):
    caps = list(h)
    if own_r is None:
        caps[0] = 0
    else:
        need(type(own_r) is int and 0 <= own_r < len(caps) and caps[own_r] > 0, "SELF_EXCLUSION")
        caps[own_r] -= 1
        caps[-1] = 0
    return subset_sums(caps, degree, tick)


def values(bits):
    while bits:
        last = bits & -bits
        yield last.bit_length()-1
        bits -= last


def pair_capacity(k, sizes, i, r, sums):
    d = k-2*r
    j, ell = [a for a in range(3) if a != i]
    ri, rj, rl = sums[i], sums[j], sums[ell]
    groups = [((k-1)*d-2*ri, rj-r, rl-r, 2*(sizes[i]-1)-d),
              (ri, k*r-2*rj, rl-r, 2*(sizes[j]-r)),
              (ri, k*r-2*rl, rj-r, 2*(sizes[ell]-r))]
    return all(min(a,b,c) >= 0 and a+b+c == maximum and max(a,b,c) <= maximum
               for a,b,c,maximum in groups)


def row_test(k, sizes, i, r, h, other_pools, tick):
    j, ell = [a for a in range(3) if a != i]
    own = pool_sums(h, k-2*r, tick, own_r=r)
    jbits, lbits = other_pools[j][r], other_pools[ell][r]
    difference = k*k+2-3*(k+1)*r+2*(sizes[j]-sizes[i])
    need(difference % 3 == 0 and 2*(sizes[ell]-sizes[j]) % 3 == 0, "ROW_INTEGRAL")
    dij, djl = difference//3, 2*(sizes[ell]-sizes[j])//3
    allowed = 0
    first_sums = None
    for rj in values(jbits):
        ri, rl = rj+dij, rj-djl
        if ri >= 0 and rl >= 0 and (own >> ri)&1 and (lbits >> rl)&1:
            sums = [0,0,0]
            sums[i], sums[j], sums[ell] = ri, rj, rl
            if pair_capacity(k, sizes, i, r, sums):
                allowed |= 1 << rj
                if first_sums is None:
                    first_sums = sums
    return dict(possible=bool(allowed), feasible_j_bits=allowed, first_witness_sums=first_sums,
                rainbow_degree=r, own_bits=own, j_bits=jbits, ell_bits=lbits,
                own_minus_j=dij, j_minus_ell=djl)


def repeated_sum(hist, row_bits, target, tick):
    """Each hypothetical vertex independently chooses one allowed row sum."""
    need(type(target) is int and target >= 0, "AGGREGATE_TARGET")
    bits, mask = 1, (1 << (target+1))-1
    for r, number in enumerate(hist):
        choices = list(values(row_bits[r]))
        for _ in range(number):
            tick()
            nxt = 0
            for value in choices:
                nxt |= bits << value
            bits = nxt & mask
            if not bits:
                return False
    return bool((bits >> target)&1)


def propagate(k, sizes, square_totals, domains, tick, rejected):
    """Synchronous monotone relaxation; pooled histograms need not agree jointly."""
    round_number = 0
    cached = lru_cache(maxsize=8192)(lambda h,d: pool_sums(h,d,tick))
    while all(domains):
        tick()
        round_number += 1
        pools = [[0]*(k//2+1) for _ in range(3)]
        for i, domain in enumerate(domains):
            for _, h in domain:
                tick()
                for degree in range(k//2+1):
                    pools[i][degree] |= cached(h, degree)
        new_domains = [[],[],[]]
        for i, domain in enumerate(domains):
            for ordinal, h in domain:
                tick()
                first = None
                row_bits = [0]*(k//2+1)
                for r, number in enumerate(h):
                    if number:
                        result = row_test(k, sizes, i, r, h, pools, tick)
                        if not result["possible"]:
                            first = dict(round=round_number, color=i, histogram_ordinal=ordinal, **result)
                            break
                        row_bits[r] = result["feasible_j_bits"]
                if first is None:
                    j = next(a for a in range(3) if a != i)
                    if not repeated_sum(h,row_bits,square_totals[j],tick):
                        first = dict(round=round_number,color=i,histogram_ordinal=ordinal,
                                     possible=False,reason="AGGREGATE_STUB_SUM",other_color=j,
                                     required_total=square_totals[j],row_j_bits=row_bits)
                if first is None:
                    new_domains[i].append((ordinal,h))
                else:
                    rejected(first)
        old_sizes, new_sizes = [len(a) for a in domains], [len(a) for a in new_domains]
        domains = new_domains
        if old_sizes == new_sizes:
            break
    return dict(rounds=round_number, surviving_ordinals=[[o for o,_ in d] for d in domains],
                surviving_histograms=[len(d) for d in domains], necessary_screen_pass=all(domains))


def labels():
    return [(s,t) for s in POPULATIONS for t in range(0,7*min(s)+1,3)]


def configuration(payload):
    need(type(payload) is dict and payload.get("schema") == "TERNARY_COLOR_HISTOGRAM_SCREEN_CONFIGURATION_V1"
         and type(payload.get("n")) is int and payload["n"] == 99
         and type(payload.get("k")) is int and payload["k"] == 14
         and payload.get("populations") == [list(s) for s in POPULATIONS]
         and all(type(v) is int for s in payload["populations"] for v in s), "CONFIG_DOMAIN")
    need(type(payload.get("root_authority")) is dict and type(payload.get("written_bound_gate")) is dict
         and type(payload.get("independent_author_controls")) is dict, "CONFIG_GATES")


def scientific(ctx, config_ref):
    cfg = ctx.json(config_ref)
    configuration(cfg)
    ctx.json(cfg["root_authority"])
    gate = ctx.json(cfg["written_bound_gate"])
    need(gate.get("status") == "INDEPENDENT_TARGET_TERNARY_LEFT_CODE_COLOR_MOMENTS_WEIGHTS48_75_V1_WRITTEN_PASS"
         and gate.get("producer") == "/root/structural" and gate.get("verifier") == "/root/native_driver"
         and gate.get("method") == "independent_derivation" and gate.get("claim_revision") == 1
         and type(gate.get("claim_revision")) is int, "WRITTEN_GATE")
    controls = ctx.json(cfg["independent_author_controls"])
    need(controls.get("status") == "INDEPENDENT_TERNARY_COLOR_HISTOGRAM_SCREEN_V1_AUTHOR_CONTROLS_PASS"
         and controls.get("producer") == "/root/structural" and controls.get("verifier") != "/root/structural"
         and controls.get("method") == "independent_artifact_check"
         and controls.get("source_sha256") == ctx.pins[SELF]
         and controls.get("specification_sha256") == ctx.pins[SPEC], "CONTROLS_GATE")
    universe = labels()
    need(len(universe) == 761, "LABEL_UNIVERSE")
    save(ctx.out / "universe.json", dict(populations=[list(s) for s in POPULATIONS],
         labels=[dict(label=i,populations=list(s),rainbow_triangles=t) for i,(s,t) in enumerate(universe)]))
    results = []
    with (ctx.out / "labels.jsonl").open("x",encoding="utf-8",newline="\n") as journal:
        for case, (sizes,t) in enumerate(universe):
            ctx.tick()
            ctx.progress.update(active_label=case, phase="scalar", active_histogram=None, active_round=None)
            result = dict(label=case,populations=list(sizes),rainbow_triangles=t)
            try:
                z = scalar(99,14,sizes,t)
            except Veto as exc:
                result.update(scalar_pass=False, first_veto=str(exc), necessary_screen_pass=False)
            else:
                folder = ctx.out / f"label_{case:03d}"
                folder.mkdir(exist_ok=False)
                domains = [[],[],[]]
                ctx.progress["phase"] = "histogram_generation"
                with (folder / "histograms.jsonl").open("x",encoding="utf-8",newline="\n") as stream:
                    for color in range(3):
                        for ordinal, h in enumerate(histograms(sizes[color],t,z[color],7,ctx.tick)):
                            domains[color].append((ordinal,h))
                            stream.write(json.dumps(dict(color=color,ordinal=ordinal,bins=list(h)),separators=(",",":"))+"\n")
                            ctx.progress["active_histogram"] = [color,ordinal]
                            if ordinal % 256 == 0:
                                stream.flush()
                initial = [len(d) for d in domains]
                ctx.progress["phase"] = "domain_propagation"
                with (folder / "rejections.jsonl").open("x",encoding="utf-8",newline="\n") as stream:
                    def reject(row):
                        stream.write(json.dumps(row,separators=(",",":"))+"\n")
                        ctx.progress["active_round"] = row["round"]
                        stream.flush()
                    outcome = propagate(14,sizes,z,domains,ctx.tick,reject)
                result.update(scalar_pass=True, square_totals=z, initial_histograms=initial, **outcome)
                save(folder / "result.json", result)
            journal.write(json.dumps(result,separators=(",",":"))+"\n")
            journal.flush()
            results.append(result)
            ctx.progress.update(completed_labels=case+1, active_label=None, phase="between_labels")
            ctx.checkpoint(f"checkpoint_{case:03d}.json")
            print(json.dumps(dict(completed_labels=case+1,scalar_pass=result["scalar_pass"],
                                  necessary_screen_pass=result["necessary_screen_pass"])),flush=True)
    return dict(status="CANDIDATE_TERNARY_COLOR_HISTOGRAM_SCREEN_V1_COMPLETE", complete_labels=761,
                scalar_pass=sum(r["scalar_pass"] for r in results),
                necessary_screen_pass=sum(r["necessary_screen_pass"] for r in results),
                excluded_labels=[r["label"] for r in results if not r["necessary_screen_pass"]],
                remaining_labels=[r["label"] for r in results if r["necessary_screen_pass"]],
                graph_cases_enumerated=0, joint_histogram_tuples_enumerated=0,
                actual_left_word_existence_asserted=False, constants_allowed=True)


def calibration(ctx):
    tick = ctx.tick
    rook = (0,3,0)
    ha = (0,0,0,0,0,5,17,2)
    hc = (0,0,14,35,2,0,0,0)
    fixture = dict(sizes=[24,24,51],t=141,z=[835,835,403],histograms=[ha,ha,hc])
    rows = []
    def run(name, expected, payload, action):
        tick()
        try:
            result, observed = action(), "PASS"
        except Veto as exc:
            result, observed = None, str(exc)
        row = dict(index=len(rows),name=name,expected_stage=expected,observed_stage=observed,
                   matched=expected==observed,payload=payload,result=result,synthetic_only=True)
        save(ctx.out / f"case_{len(rows):02d}.json",row)
        rows.append(row)
        need(row["matched"],"CONTROL_MISMATCH")
    def check(ok, stage="HAND_REFERENCE"):
        need(ok,stage)
        return True
    run("rook9_row_colors_scalar","PASS",dict(n=9,k=4,sizes=[3,3,3],t=3,z=[3,3,3]),
        lambda:check(scalar(9,4,[3,3,3],3)==[3,3,3]))
    run("rook9_complete_histogram_universe","PASS",dict(size=3,t=3,z=3,only_bins=list(rook)),
        lambda:check(list(histograms(3,3,3,2,tick))==[rook]))
    run("bounded_subset_sum_exact","PASS",dict(capacities=[2,1],degree=2,sums=[0,1]),
        lambda:check(list(values(subset_sums([2,1],2,tick)))==[0,1]))
    def target_pass():
        for h,s,z in zip((ha,ha,hc),(24,24,51),(835,835,403)):
            histogram(h,s,141,z,7)
        rejected = []
        out = propagate(14,[24,24,51],[835,835,403],[[(0,ha)],[(0,ha)],[(0,hc)]],tick,rejected.append)
        return check(out["necessary_screen_pass"] and out["surviving_histograms"]==[1,1,1] and not rejected)
    run("hand_local24_24_51_survivor","PASS",fixture,target_pass)
    def boundary():
        a=(0,0,0,0,0,0,0,21)
        b=(0,0,0,0,35,0,0,1)
        c=(0,0,0,21,21,0,0,0)
        pools=[[pool_sums(h,d,tick) for d in range(8)] for h in (a,b,c)]
        row=row_test(14,[21,36,42],1,7,b,pools,tick)
        return check(not row["possible"] and list(values(row["j_bits"]))==[49]
                     and max(values(row["ell_bits"]))==28)
    run("old21_boundary_pointwise_rejected","PASS",dict(sizes=[21,36,42],t=147,bin=7),boundary)
    run("zero_r_cross_pool_empty","PASS",dict(h=[3,0,0],degree=1),
        lambda:check(pool_sums((3,0,0),1,tick)==0))
    run("rook_self_copy_removed","PASS",dict(h=list(rook),r=1,degree=2,sums=[2]),
        lambda:check(list(values(pool_sums(rook,2,tick,own_r=1)))==[2]))
    run("rook_pair_CN_capacities","PASS",dict(k=4,sizes=[3,3,3],color=0,r=1,sums=[2,1,1]),
        lambda:check(pair_capacity(4,[3,3,3],0,1,[2,1,1])))
    run("declared12_population761_label_universe","PASS",dict(populations=[list(s) for s in POPULATIONS],count=761),
        lambda:check(len(labels())==761 and len(set(labels()))==761))
    run("exact_weighted_stub_sum_gap","PASS",dict(hist=[2],row_sums=[1,3],allowed=[2,4,6],forbidden=5),
        lambda:check(repeated_sum([2],[(1<<1)|(1<<3)],4,tick)
                     and not repeated_sum([2],[(1<<1)|(1<<3)],5,tick)))
    run("k_boolean","PARAMETERS",dict(k=True),lambda:parameters(9,True,[3,3,3]))
    run("population_boolean","POPULATION",dict(sizes=[True,3,5]),lambda:parameters(9,4,[True,3,5]))
    run("population_total","POPULATION",dict(sizes=[3,3,6]),lambda:parameters(9,4,[3,3,6]))
    run("t_boolean","T_TYPE",dict(t=True),lambda:scalar(9,4,[3,3,3],True))
    run("t_not_divisible3","T_DIVISIBILITY",dict(t=1),lambda:scalar(9,4,[3,3,3],1))
    run("t_negative","T_RANGE",dict(t=-3),lambda:scalar(9,4,[3,3,3],-3))
    run("t_above_capacity","T_RANGE",dict(t=9),lambda:scalar(9,4,[3,3,3],9))
    run("histogram_boolean","HIST_TYPE",dict(h=[0,True,2]),lambda:histogram([0,True,2],3,3,3,2))
    run("histogram_short","HIST_SHAPE",dict(h=[0,3]),lambda:histogram([0,3],3,3,3,2))
    run("histogram_negative","HIST_TYPE",dict(h=[-1,4,0]),lambda:histogram([-1,4,0],3,3,3,2))
    run("histogram_count","HIST_COUNT",dict(h=[0,2,0]),lambda:histogram([0,2,0],3,3,3,2))
    run("histogram_first_moment","HIST_SUM",dict(h=[1,1,1]),lambda:histogram([1,1,1],3,2,3,2))
    changed=(0,0,0,0,0,4,19,1)
    run("histogram_square_only","HIST_SQUARES",dict(h=list(changed),s=24,t=141,z=835),
        lambda:histogram(changed,24,141,835,7))
    run("selection_degree_boolean","SELECTION_DEGREE",dict(degree=True),lambda:subset_sums([2,1],True,tick))
    run("selection_degree_negative","SELECTION_DEGREE",dict(degree=-1),lambda:subset_sums([2,1],-1,tick))
    run("self_copy_missing","SELF_EXCLUSION",dict(h=list(rook),r=0),lambda:pool_sums(rook,2,tick,own_r=0))
    run("duplicate_json","DUPLICATE_KEY",dict(raw='{ "x":1,"x":2 }'),
        lambda:json.loads('{ "x":1,"x":2 }',object_pairs_hook=unique))
    run("parent_relative_input","INPUT_PATH",dict(path="../outside"),lambda:ctx.raw("../outside","0"*64))
    run("wrong_source_hash","INPUT_SHA",dict(path=SELF,sha256="0"*64),lambda:ctx.raw(SELF,"0"*64))
    def reserve():
        class SyntheticDeadline:
            def status(self):
                return {"remaining_seconds":20}
        Context(SyntheticDeadline(),ctx.out).tick()
    run("inclusive_reserve_boundary","SAVE_GUARD",dict(synthetic_remaining_seconds=20),reserve)
    fake=dict(schema="TERNARY_COLOR_HISTOGRAM_SCREEN_CONFIGURATION_V1",n=99,k=14,
              populations=[list(s) for s in POPULATIONS],root_authority={},written_bound_gate={},independent_author_controls={})
    fake["populations"][-1][-1]=True
    run("configuration_population_boolean","CONFIG_DOMAIN",fake,lambda:configuration(fake))
    need(len(rows)==31 and sum(r["expected_stage"]=="PASS" for r in rows)==10,"CONTROL_POPULATION")
    save(ctx.out / "controls.json",rows)
    return dict(status="TERNARY_COLOR_HISTOGRAM_SCREEN_V1_AUTHOR_CONTROLS_CANDIDATE_PASS",
                positive_controls=10,negative_controls=21,total_controls=31,
                target_graph_read=False,scientific_labels_screened=0,actual_calibration_only=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=("calibrate","screen"))
    parser.add_argument("--seconds",type=float,required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--self-sha256",required=True)
    parser.add_argument("--spec-sha256",required=True)
    parser.add_argument("--configuration")
    parser.add_argument("--configuration-sha256")
    args=parser.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason="Exact bounded necessary colour histogram screen or fresh finite author controls; no graph construction.")
    out=Path(args.out).resolve()
    need(out.is_relative_to(ROOT/"acceleration/results") and not out.exists(),"OUTPUT_PATH")
    out.mkdir(parents=True,exist_ok=False)
    ctx=Context(deadline,out)
    try:
        ctx.raw(SELF,args.self_sha256)
        ctx.raw(SPEC,args.spec_sha256)
        for name,wanted in SOFTWARE.items():
            ctx.raw(name,wanted)
        result=calibration(ctx) if args.mode=="calibrate" else scientific(ctx,dict(path=args.configuration,sha256=args.configuration_sha256))
        ctx.progress["phase"]="closing_hashes"
        for name,wanted in list(ctx.pins.items()):
            ctx.raw(name,wanted)
        outputs={}
        for path in sorted(out.rglob("*")):
            ctx.tick()
            if path.is_file():
                outputs[path.relative_to(out).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
                ctx.tick()
        result.update(implementation_version=1,source_sha256=args.self_sha256,specification_sha256=args.spec_sha256,
                      producer="/root/structural",method="candidate_exact_enumeration",target_resolution="NONE",
                      timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=ctx.pins,
                      outputs_sha256=outputs,command=[sys.executable,*sys.argv],deadline=deadline.status(),
                      limitations=["Necessary histogram-domain propagation only; no joint histogram tuple, code, graph or nonconstant word constructed.",
                                   "Pooled domains can use different other-class histograms for different rows; passing is a relaxation.",
                                   "No imports of mathematical producers, solver, automorphism, equitable partition, ledger or Git operation."])
        save(out/"summary.json",result)
        ctx.tick()
        print(json.dumps(dict(status=result["status"],summary=str((out/"summary.json").relative_to(ROOT)))),flush=True)
        ctx.tick()
        return 0
    except Exception as exc:
        save(out/"failure.json",dict(status="FAILED_OR_NOT_COMPLETED_PRESERVED",stage=str(exc),error_type=type(exc).__name__,
             wording="not completed within the allocated budget" if str(exc)=="SAVE_GUARD" else "Engineering or input failure; no target conclusion.",
             progress=ctx.progress,inputs_sha256=ctx.pins,deadline=deadline.status(),
             timestamp=datetime.now(timezone.utc).isoformat(),automatic_retry=False,target_resolution="NONE"))
        print(json.dumps(dict(status="FAILED_OR_NOT_COMPLETED_PRESERVED",stage=str(exc))),flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
