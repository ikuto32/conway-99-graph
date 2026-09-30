"""Independent bounded scheduler countercontrol; no real child or producer calls."""
import argparse,hashlib,importlib.util,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'acceleration/build_20260930_exact_eight_parallel_batch.py'
EXPECTED='6b1b4c4f80a24e6851643032689df37a5a9641ee4c465ae04aab3f008ae8ec44'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    assert h(SOURCE)==EXPECTED
    pins=json.loads(SOURCE.with_name(SOURCE.stem+'_pins.json').read_bytes())['inputs_sha256']
    for p,v in pins.items():assert h(ROOT/p)==v
    spec=importlib.util.spec_from_file_location('reviewed_parallel_build',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    class Clock:
        now=0.0
        def __call__(self):return self.now
        def sleep(self,x):self.now+=x
    def case(delay):
        clock=Clock();events=[];children=[]
        class Child:
            def __init__(self,i):self.i=i;self.done=False;self.cancelled_at=None
            def poll(self):return 0 if self.i==0 and clock.now>=0.025 else None
            def finish(self,cancelled):
                if self.i==0 and not cancelled:clock.sleep(delay)
                if cancelled:self.cancelled_at=clock.now
                self.done=True;return dict(index=self.i,cancelled=cancelled,at=clock.now)
        def launch(i,r,d):
            c=Child(i);children.append(c);return c
        dispatch=m.supervise([{},{}],2,1.0,launch,clock=clock,sleep=clock.sleep,event=events.append)
        return dict(cleanup_delay=delay,deadline=1.0,clock=clock.now,second_child_cancelled_at=children[1].cancelled_at,dispatch=dispatch,events=events)
    positive=case(0.0);counter=case(5.0)
    assert positive['second_child_cancelled_at']<=1.025
    assert counter['second_child_cancelled_at']>5.0
    save(out/'control.json',positive);save(out/'counterexample.json',counter)
    result=dict(status='INDEPENDENT_PARALLEL_BUILD_DEADLINE_COUNTEREXAMPLE',source_sha256=EXPECTED,source_path=SOURCE.relative_to(ROOT).as_posix(),command=[sys.executable,*sys.argv],inputs_sha256={**pins,SOURCE.relative_to(ROOT).as_posix():EXPECTED,Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__)),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix():h(Path(__file__).with_name(Path(__file__).stem+'_spec.md'))},positive_zero_delay_cancelled_at=positive['second_child_cancelled_at'],delayed_cleanup_cancelled_at=counter['second_child_cancelled_at'],deadline=1.0,observed_scope='Exact frozen supervisor with deterministic clock/children; a permitted five-second cleanup blocks deadline handling for another still-working child.',real_process_calls=0,native_calls=0,formula_builds=0,limitation='This control demonstrates a scheduler counterexample, not an observed operating-system stall or a performance benchmark.')
    save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=h(out/'summary.json'),cancelled_at=counter['second_child_cancelled_at'])))
if __name__=='__main__':main()
