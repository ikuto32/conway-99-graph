"""Freeze the pre-subset frontier to avoid a live-inventory dependency cycle.

Only input provenance paths change in the two discovery outputs; model rows,
certificates, and the input bytes themselves are preserved exactly.
"""

import hashlib
import json
from pathlib import Path


LIVE = Path("scratch_root_e71_theory_frontier_inventory.json")
FROZEN = Path("scratch_root_e71_theory_frontier_before_label_subset.json")
EXPECTED = "C277833D2A68FE26D1C66C416CCE3A6A7B50631CFBEB9AB1B2AE11D6055A5336"


def main():
    if FROZEN.exists():
        raw = FROZEN.read_bytes()
    else:
        raw = LIVE.read_bytes()
        assert hashlib.sha256(raw).hexdigest().upper() == EXPECTED
        FROZEN.write_bytes(raw)
    assert hashlib.sha256(raw).hexdigest().upper() == EXPECTED
    for name in ("scratch_theory_e71_label_subset_moment_probe.json",
                 "scratch_theory_e71_label_subset_moment_frontier.json"):
        path = Path(name)
        data = json.loads(path.read_text(encoding="utf-8"))
        hashes = data["inputs_sha256"]
        if str(LIVE) in hashes:
            assert hashes.pop(str(LIVE)) == EXPECTED
            hashes[str(FROZEN)] = EXPECTED
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        assert hashes[str(FROZEN)] == EXPECTED
    print(json.dumps({"status": "PRE_SUBSET_FRONTIER_INPUT_FROZEN",
                      "path": str(FROZEN), "sha256": EXPECTED}))


if __name__ == "__main__":
    main()
