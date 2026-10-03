"""Harmless three-generation tree, bounded to six seconds, no stdin barrier."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--level',type=int,required=True);p.add_argument('--seconds',type=float,required=True);p.add_argument('--root-seconds',type=float,required=True);a=p.parse_args()
    assert 0<=a.level<=2 and 0<a.seconds<=6 and 0<a.root_seconds<=6
    d=a.out.resolve();assert d.is_dir()
    with(d/f'level{a.level}.json').open('x',encoding='utf8')as f:json.dump(dict(pid=os.getpid(),parent_pid=os.getppid(),level=a.level),f)
    if a.level<2:
        c=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--out',str(d),'--level',str(a.level+1),'--seconds',str(a.seconds),'--root-seconds',str(a.root_seconds)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
        with(d/f'level{a.level}.spawn.json').open('x',encoding='utf8')as f:json.dump(dict(parent_application_pid=os.getpid(),child_popen_pid=c.pid),f)
    end=time.monotonic()+(a.root_seconds if a.level==0 else a.seconds)
    with(d/f'level{a.level}.heartbeat').open('xb',buffering=0)as f:
        while time.monotonic()<end:f.write(b'.');time.sleep(.02)
if __name__=='__main__':main()
