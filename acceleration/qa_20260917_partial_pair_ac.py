"""Additional producer QA; independent review is still required."""
from argparse import Namespace
from copy import deepcopy
from pathlib import Path
import theory_20260917_partial_pair_ac as producer


def main():
    args = Namespace(filter_dir=None, filter_audit=None, filter_audit_sha256=None)
    masks, rows, active, hashes = producer.prepare(args)
    _, allowed = producer.graph(producer.read(producer.BASE/'manifest.json'))
    failures = []
    for label, change in (
        ('zero_mask', lambda x: x[0].__setitem__(0, 0)),
        ('duplicate_mask', lambda x: x[0].insert(0, x[0][0])),
        ('self_edge', lambda x: x[0].__setitem__(0, x[0][0] | 1)),
        ('wrong_center_count', lambda x: x.pop()),
    ):
        damaged = deepcopy(masks)
        change(damaged)
        try:
            producer.validate_masks(rows, allowed, damaged)
        except ValueError:
            failures.append(label)
        else:
            raise AssertionError('corrupt input accepted: '+label)
    rook = [sum(1 << v for v in range(9) if u != v and (u//3 == v//3 or u%3 == v%3))
            for u in range(9)]
    tables = [[x, 0] for x in rook]
    output = producer.propagate(tables, list(range(9)), [[0, 1] for _ in rook])
    assert output['status'] == 'ARC_CONSISTENT'
    assert output['surviving_original_ids'] == [[0] for _ in rook]
    # Self-QA checks all nine zero-neighborhood deletions while preserving SRG.
    assert sum(len(e['removed_original_ids']) for e in output['events']) == 9
    result = dict(status='ADDITIONAL_PRODUCER_QA_PASS', inputs_sha256=hashes,
                  base_controls=producer.controls(), corrupt_input_rejections=failures,
                  mixed_domain_positive_preserved=True, mixed_domain_bad_choices_removed=9,
                  independence='Imports producer; not independent verification')
    producer.save(Path('acceleration/results/20260917_partial_pair_ac_preparation/additional_controls.json'), result)


if __name__ == '__main__':
    main()
