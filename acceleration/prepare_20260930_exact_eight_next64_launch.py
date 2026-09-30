"""Freeze four separately bounded build invocations; this performs no build."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
PARENT=B+'exact_eight_next64_selection/selection.json'
PINS=['0e56bd94f9fc5cdb6fceee6741c1e19155cb1b46d665ac206ace1a70bf4ba3e3','33633e0ee22a0931105ac0ec565e5e17eaa51e1b990ee37845403b1d6ba975d0','7c1a8c56f43ea65b712dd0388d66760f0745e36845ae1780d876181f2b1e2179','2429be320500e3d5326842a38df1ec75e463d7223216e84f09c5cc7b5d35c0f6']
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    assert h(PARENT)=='0716de33dff78fb10850240e387e3000580e482f9d0768c5098c5e1f07470b18'
    entries=[]
    for i,pin in enumerate(PINS):
        p=B+f'exact_eight_next64_selection/partition_{i:02d}.json';assert h(p)==pin
        out=B+f'exact_eight_next64_cnfs_part{i:02d}';assert not(ROOT/out).exists()
        entries.append(dict(path=p,sha256=pin,attempt_id=f'next64-part{i:02d}-build-attempt01',out=out))
    out=B+'exact_eight_next64_launch_preparation';(ROOT/out).mkdir(exist_ok=False)
    plan=dict(schema='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1',parent_selection_path=PARENT,parent_selection_sha256=h(PARENT),workers=4,seconds_per_chunk=120,build_selections=entries)
    save(out+'/launch_plan.json',plan)
    save(out+'/summary.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={PARENT:h(PARENT),**{e['path']:e['sha256']for e in entries},Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__).relative_to(ROOT))},outputs_sha256={out+'/launch_plan.json':h(out+'/launch_plan.json')},producer_calls=0,native_calls=0,independent_approval=False,scope='Four explicit120-second allocations, maximum480 aggregate allocated build seconds. This preparation does not approve a process supervisor.'))
    print(json.dumps(dict(plan_path=out+'/launch_plan.json',sha256=h(out+'/launch_plan.json'))))
if __name__=='__main__':main()
