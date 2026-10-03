import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'acceleration'))
from theory_20260930_variable_core_residual_screen import validate_factor,compute_screen
b=json.loads(Path(sys.argv[2]).read_bytes())
r={'label':'GENERALIZED243_CALIBRATION_ONLY_NOT_RESEARCH99','validation':validate_factor(b['cubic_core60'],b['factor60x180'],20,research=False),'screen':compute_screen(b['cubic_core60'],b['factor60x180'],16)}
with Path(sys.argv[3]).open('x',encoding='utf-8') as f:json.dump(r,f)
