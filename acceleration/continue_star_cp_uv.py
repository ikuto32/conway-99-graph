"""Run the byte-pinned historical orchestrator with the active uv interpreter.

Only the Python executable used for child commands changes. Search, selection,
audit thresholds, native binaries and historical sources remain byte-identical.
The original orchestrator records the actual child commands and executable hash.
"""
from hashlib import sha256
from pathlib import Path
import sys

FROZEN_SHA256 = '5ea5cb381c6a0124bf11731f84f3b6d4d59644d4fa21841082e62bcd50a27e9a'
source = Path(__file__).with_name('continue_star_cp_round.py')
if sha256(source.read_bytes()).hexdigest() != FROZEN_SHA256:
    raise ValueError('Historical orchestrator changed; impact review required')

import continue_star_cp_round as frozen

frozen.PYTHON = Path(sys.executable).resolve()

if __name__ == '__main__':
    frozen.main()
