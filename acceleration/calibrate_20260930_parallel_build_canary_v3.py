"""Harmless owned process-tree canary: small files, maximum eight seconds."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--level',type=int,required=True);ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--root-seconds',type=float,required=True);a=ap.parse_args()
    assert 0<=a.level<=2 and 0<a.seconds<=8 and 0<a.root_seconds<=8
    folder=a.out.resolve();assert folder.is_dir()
    with(folder/f'level{a.level}.startup.json').open('x',encoding='utf8')as f:json.dump(dict(pid=os.getpid(),parent_pid=os.getppid(),level=a.level),f)
    if a.level==0:
        if sys.stdin.buffer.readline()!=b'RUN\n':return 3
    folder=a.out.resolve();assert folder.is_dir()
    with(folder/f'level{a.level}.json').open('x',encoding='utf8')as f:json.dump(dict(pid=os.getpid(),parent_pid=os.getppid(),level=a.level),f)
    if a.level<2:
        child=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--out',str(folder),'--level',str(a.level+1),'--seconds',str(a.seconds),'--root-seconds',str(a.root_seconds)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
        with(folder/f'level{a.level}.spawn.json').open('x',encoding='utf8')as f:json.dump(dict(parent_application_pid=os.getpid(),child_popen_pid=child.pid),f)
    end=time.monotonic()+(a.root_seconds if a.level==0 else a.seconds)
    with(folder/f'level{a.level}.heartbeat').open('xb',buffering=0)as f:
        while time.monotonic()<end:f.write(b'.');time.sleep(0.02)
    return 0
if __name__=='__main__':sys.exit(main())
