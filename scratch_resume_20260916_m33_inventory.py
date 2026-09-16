"""Create an isolated m33 successor ledger; preserve the historical inventory."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import scratch_resume_20260916_m33_inventory_audit as audit


def main():
    before, certificate = audit.verify_certificate()
    successor = deepcopy(before)
    source = successor['source150']
    rows = [row for row in source['macro_rows'] if row['macro'] == [3, 3]]
    audit.require(rows == [dict(macro=[3, 3], coverage=8192, status='OPEN', excluded_coverage=0, open_coverage=8192)], 'm33 is already credited or does not match')
    audit.require(str(audit.CERTIFICATE) not in successor['inputs'], 'Certificate already credited')
    successor['inputs'][str(audit.CERTIFICATE)] = audit.CERTIFICATE_SHA
    rows[0].update(status='EXACT_SYNCHRONIZED_LOCAL_CSP_ENUM_REJECTED', excluded_coverage=8192, open_coverage=0)
    source['m33_joint_primary_additional_rejected_coverage'] = 8192
    source['m33_joint_primary_audit'] = str(audit.CERTIFICATE)
    source['m33_joint_primary_audit_sha256'] = audit.CERTIFICATE_SHA
    source['open_coverage'] -= 8192
    global_counts = successor['global']
    global_counts['classified_nonopen_coverage'] += 8192
    global_counts['unresolved_or_pending_coverage'] -= 8192
    global_counts['exact_executable_non_DRAT_coverage'] += 8192
    index = next(i for i, row in enumerate(successor['buckets']) if row['name'] == 'source150_open')
    successor['buckets'][index]['coverage'] -= 8192
    successor['buckets'].insert(index, dict(name='source150_m33_joint_primary_rejected', coverage=8192,
                                          status='EXACT_SOLVER_FREE_LOCAL_CSP_JOINT_MAP_PRIMARY'))
    if audit.AFTER.exists():
        audit.require(audit.load(audit.AFTER) == successor, 'Existing successor differs')
    else:
        with audit.AFTER.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(successor, indent=2) + '\n')
    subprocess.run([sys.executable, str(Path(audit.__file__))], check=True)
    audit.require(audit.sha(audit.BEFORE) == audit.BEFORE_SHA, 'Historical inventory was modified')


if __name__ == '__main__':
    main()
