"""Extract selected representatives from a normalized incremental-SAT record."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--record-index", type=int, required=True)
    parser.add_argument("--branch-indices", type=int, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    original = source["records"][args.record_index]
    wanted = list(dict.fromkeys(args.branch_indices))
    by_id = {
        int(rep.get("representative_id", index)): rep
        for index, rep in enumerate(original["representatives"])
    }
    selected = [copy.deepcopy(by_id[index]) for index in wanted]
    assert len(selected) == len(wanted)
    for new_index, representative in enumerate(selected):
        representative["source_representative_id"] = representative.get(
            "representative_id", wanted[new_index]
        )
        representative["representative_id"] = new_index

    record = copy.deepcopy(original)
    record["support_form"] += "-selected-representatives-" + "-".join(map(str, wanted))
    record["representatives"] = selected
    record["orbit_count_direct"] = len(selected)
    record["orbit_sizes"] = [int(rep["orbit_size"]) for rep in selected]
    record["local_graph_count"] = sum(record["orbit_sizes"])
    result = {
        "status": "EXACT_SUBSET",
        "model": "selected complete local representatives for deeper exact SAT",
        "source": str(args.input),
        "source_record_index": args.record_index,
        "source_representative_ids": wanted,
        "support_record_count": 1,
        "local_representative_count": len(selected),
        "labelled_local_graphs_represented": record["local_graph_count"],
        "records": [record],
        "claim_boundary": "Only the explicitly selected source representatives are covered.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "representatives": len(selected),
        "orbit_mass": record["local_graph_count"],
    }))


if __name__ == "__main__":
    main()
