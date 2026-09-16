"""Preserve producer controls rejected by the independent partial-graph audit."""
from pathlib import Path
import hashlib
import json
from scratch_resume_uniform_fibre_incidence_audit import audit_one


def main():
    good, bad, copies = [], [], []
    for fi in range(21):
        try:
            audit_one(fi)
            good.append(fi)
        except AssertionError:
            bad.append(fi)
            path = Path(f'scratch_resume_uniform_fibre_incidence_f{fi}_q16.json')
            copy = path.with_name(path.stem+'_preincoming_invalid.json')
            assert not copy.exists()
            copy.write_bytes(path.read_bytes())
            copies.append({'source': fi, 'diagnostic_file': str(copy),
                           'sha256': hashlib.sha256(copy.read_bytes()).hexdigest()})
    report = {'status': 'INITIAL_MODEL_PARTIAL_GRAPH_AUDIT_DIAGNOSTIC',
              'valid_source_indices': good, 'invalid_source_indices': bad,
              'cause': 'Initial producer omitted first-layer-label versus target-vertex incoming common-neighbour caps. Invalid outputs are diagnostics only.',
              'preserved_invalid_outputs': copies}
    Path('scratch_resume_uniform_fibre_incidence_repair_checkpoint.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
