"""Small observed Linux descendant containment controls; no research search."""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def save(path, data):
    with path.open('x', encoding='utf8') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['success', 'timeout', 'observe'])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--groups', nargs='*', type=int)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    if args.mode == 'observe':
        groups = set(args.groups)
        rows = []
        for stat in Path('/proc').glob('[0-9]*/stat'):
            try:
                fields = stat.read_text().rsplit(')', 1)[1].split()
                if int(fields[2]) in groups:
                    rows.append({'pid': int(stat.parent.name), 'ppid': int(fields[1]), 'process_group': int(fields[2]), 'state': fields[0], 'raw_stat': stat.read_text(), 'cmdline': (stat.parent / 'cmdline').read_bytes().decode(errors='replace').replace('\0', ' ')})
            except (OSError, IndexError, ValueError):
                continue
        save(args.out / 'observation.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'command': [sys.executable, *sys.argv], 'groups': sorted(groups), 'rows': rows, 'live_rows': [row for row in rows if row['state'] != 'Z'], 'scope': 'Observed matching Linux process groups at this instant; zombies cannot compute.'})
        return
    duration = .2 if args.mode == 'success' else 60
    child = subprocess.Popen([sys.executable, '-c', f'import time; time.sleep({duration})'])
    pgid = os.getpgid(0)
    child_group = os.getpgid(child.pid)
    save(args.out / 'started.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'mode': args.mode, 'command': [sys.executable, *sys.argv], 'python': sys.version, 'parent_pid': os.getpid(), 'parent_group': pgid, 'child_pid': child.pid, 'child_group': child_group, 'same_group_observed': child_group == pgid, 'requested_child_seconds': duration})
    if args.mode == 'success':
        code = child.wait(timeout=5)
        save(args.out / 'completed.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'child_exit_code': code, 'child_reaped': child.poll() is not None})
    else:
        time.sleep(60)
        raise RuntimeError('Outer native timeout failed to stop this 60-second fixture')


if __name__ == '__main__':
    main()
