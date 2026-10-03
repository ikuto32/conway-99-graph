"""Fresh wave27 wrappers preserve reviewed wave26 recovery algorithms."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';made=[]
for stem in['recover_20260930_twentysixth_raw_artifacts','check_20260930_twentysixth_recovery_controls']:
    old=A/(stem+'.py');new=A/(stem.replace('twentysixth','twentyseventh')+'.py');text=old.read_text(encoding='utf8').replace('twentysixth','twentyseventh').replace('TWENTYSIXTH','TWENTYSEVENTH').replace('wave26','wave27').replace('fresh two-artifact restoration','fresh fourteen-artifact restoration')
    with new.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    made.append(dict(path=new.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(new.read_bytes()).hexdigest(),preserved_source=old.relative_to(ROOT).as_posix(),preserved_source_sha256=hashlib.sha256(old.read_bytes()).hexdigest()))
print(json.dumps(made))
