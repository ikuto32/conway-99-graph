"""Independent phase-I controls, exact binary-dual certificates, and rejection tests."""
import argparse
import copy
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import audit as audit_integer, require
from audit_phase1_kkt import inspect_artifact, exact_integer_certificate


class MemoryPath:
    def __init__(self, value, name):
        self.data = json.dumps(value, allow_nan=True).encode()
        self.name = name

    def read_bytes(self):
        return self.data

    def __str__(self):
        return self.name


def write_new(path, data):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase1", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve previous review")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    records = []
    first = None
    for phase_path in args.phase1:
        result = json.loads(phase_path.read_bytes())
        candidate_path = Path(result["candidate_path"])
        candidate = json.loads(candidate_path.read_bytes())
        audit = inspect_artifact(candidate_path, phase_path)
        stem = args.out.parent / phase_path.stem
        audit_path = Path(str(stem) + "_phase1_audit.json")
        cert_path = Path(str(stem) + "_binary_dual_certificate.json")
        cert_audit_path = Path(str(stem) + "_binary_dual_audit.json")
        write_new(audit_path, audit)
        certificate = exact_integer_certificate(candidate, result, sha256(candidate_path.read_bytes()).hexdigest())
        write_new(cert_path, certificate)
        certificate_audit = audit_integer(candidate_path, cert_path)
        write_new(cert_audit_path, certificate_audit)
        records.append(dict(phase1_path=str(phase_path), exact_dual_lower_bound=audit["exact_dual_lower_bound"],
                            combined_rhs=certificate["combined_rhs"],
                            files_sha256={str(path): sha256(path.read_bytes()).hexdigest()
                                          for path in (candidate_path, phase_path, audit_path, cert_path, cert_audit_path)}))
        if first is None:
            first = candidate_path, result
    candidate_path, baseline = first
    rejected = []

    def reject(name, mutation):
        changed = copy.deepcopy(baseline)
        mutation(changed)
        try:
            inspect_artifact(candidate_path, MemoryPath(changed, name))
        except (ValueError, KeyError, IndexError) as error:
            rejected.append(dict(name=name, reason=str(error)))
        else:
            raise ValueError(f"Invalid result accepted: {name}")

    reject("candidate_hash", lambda value: value.update(candidate_sha256="0"*64))
    reject("wrong_variable_order", lambda value: value["edge_variables"].reverse())
    reject("wrong_row_rhs", lambda value: value["constraint_groups"][0].update(target=999))
    reject("wrong_row_term", lambda value: value["constraint_groups"][0]["terms"].append(0))
    reject("missing_nontrivial_row", lambda value: value["constraint_groups"].pop(0))
    reject("nan_x", lambda value: value["numeric_edge_values"].__setitem__(0, float("nan")))
    reject("outside_box_x", lambda value: value["numeric_edge_values"].__setitem__(0, 1.1))
    reject("false_objective", lambda value: value.update(numeric_objective=0))
    reject("false_dual_bound", lambda value: value.update(numerical_dual_lower_bound=1e9))
    reject("false_row_dual_sign", lambda value: value["row_duals"].__setitem__(0, value["row_duals"][0] + 1))

    def dual_outside(value):
        value["phase1_multipliers"][840] = -0.5
        value["row_duals"][840] = 0.5
    reject("negative_cap_multiplier", dual_outside)

    def nonoptimal(value):
        value["numeric_edge_values"] = [0.0]*1680
        value["row_residuals"] = [-row["target"] for row in value["constraint_groups"]]
        for key in ("numeric_objective", "numeric_slack_objective", "numeric_solver_objective"):
            value[key] = 1344.0
        value["numerical_primal_dual_gap"] = 1344.0 - value["numerical_dual_lower_bound"]
    reject("box_feasible_but_nonoptimal_x", nonoptimal)
    report = dict(status="INDEPENDENT_PHASE1_CONTROL_AND_INTEGER_DUAL_REVIEW_PASS", records=records,
                  corruption_rejections=rejected, solver_or_producer_imported=False,
                  sources_sha256={str(path): sha256(path.read_bytes()).hexdigest() for path in
                                  (Path(__file__), Path(__file__).with_name("audit_phase1_kkt.py"),
                                   Path(__file__).with_name("audit_certificate.py"))},
                  scope="Per-control fixed-K residual model, near-optimality, and exact infeasibility only; no global exclusion.")
    write_new(args.out, report)
    print(json.dumps({"status": report["status"], "controls": len(records), "rejections": len(rejected),
                      "integer_rhs": [record["combined_rhs"] for record in records]}))


if __name__ == "__main__":
    main()
