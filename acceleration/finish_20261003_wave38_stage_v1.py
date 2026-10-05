"""Append only completed staging/CI receipts, scan selected bytes, no commit."""
import argparse,hashlib,json,os,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline
ROOT=Path(__file__).resolve().parents[1]
LEDGER='cc8184dbe3c0c1bc6d539e8925fc392b80a3a4344c29e051118af0157d948a2c'
APPLY='acceleration/results/20261003_independent_review/wave38_index_apply01/summary.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def entries(raw):
    out={}
    for q in raw.split(b'\0'):
        if q:
            meta,name=q.split(b'\t',1);mode,blob,stage=meta.decode().split();assert stage=='0';out[name.decode()]=(mode,blob)
    return out
def blob(p):
    h=hashlib.sha1(('blob '+str(p.stat().st_size)+'\0').encode())
    with p.open('rb')as f:
        for block in iter(lambda:f.read(1024**2),b''):h.update(block)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    d=CommandDeadline(a.seconds,allocation_reason='Finish only exact declared wave38 staging/CI receipts and selected-byte credential marker check;100seconds/20save reserve, no science or commit.')
    out=a.out.resolve();assert out.is_relative_to(ROOT) and not out.exists();out.mkdir()
    def git(argv):
        assert not d.status()['stop_required'] and d.status()['remaining_seconds']>20
        return subprocess.check_output(['git',*argv],cwd=ROOT,timeout=max(1,d.status()['remaining_seconds']-15))
    report=json.loads((ROOT/APPLY).read_bytes());assert report['status']=='WAVE38_EXACT350_APPLY_INDEX_RAW_BYTE_PASS' and not report['failures']
    index=Path(git(['rev-parse','--git-path','index']).decode().strip());index=index if index.is_absolute()else ROOT/index
    assert sha(index)==report['index_after_sha256'] and sha(ROOT/'CLAIMS.yaml')==LEDGER
    valid=json.loads((ROOT/'acceleration/results/20261003_wave38_registry_validation01.json').read_bytes());assert valid['valid'] is True and not valid['errors']
    stderr=(ROOT/'acceleration/results/20261003_wave38_registry_tests_supervision01/stderr.log').read_text();assert 'Ran 56 tests' in stderr and stderr.rstrip().endswith('OK')
    appendix=[APPLY,'acceleration/results/20261003_independent_review/wave38_index_apply01/exact_stage_paths.nul',
        'acceleration/results/20261003_wave38_registry_validation01.json',Path(__file__).relative_to(ROOT).as_posix(),Path(__file__).with_name(Path(__file__).stem+'_spec.md').relative_to(ROOT).as_posix()]
    for name in ('wave38_index_shadow','wave38_index_apply','wave38_registry_validation','wave38_registry_tests'):
        prefix='acceleration/results/20261003_'+name+'_supervision01/'
        s=json.loads((ROOT/(prefix+'summary.json')).read_bytes());assert s['command_exit_code']==0 and s['cleanup']['reaped'] and s['cleanup']['job_active_zero_observed']
        appendix.extend(prefix+n for n in ('manifest.json','summary.json','stdout.log','stderr.log','progress.jsonl')if (ROOT/(prefix+n)).is_file())
    appendix=sorted(set(appendix));before=entries(git(['ls-files','--stage','-z']));pins={name:sha(ROOT/name)for name in appendix}
    expected={name:blob(ROOT/name)for name in appendix}
    # Selected-path byte scan saves only a veto path, never a potential value.
    approved=(ROOT/'acceleration/results/20261003_independent_review/wave38_index_apply01/exact_stage_paths.nul').read_bytes().split(b'\0')
    names=sorted(set(appendix)|{n.decode()for n in approved if n})
    pattern=re.compile(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,}|sk-proj-[A-Za-z0-9_-]{30,}|AKIA[A-Z0-9]{16})')
    for name in names:
        path=(ROOT/name).resolve();assert path.is_relative_to(ROOT) and '.git' not in Path(name).parts and path.stat().st_size<50*1024**2
        if path.suffix=='.gz':continue
        with path.open('rb')as f:
            tail=b''
            for block in iter(lambda:f.read(1024**2),b''):
                assert not pattern.search(tail+block),'CREDENTIAL_MARKER_VETO_PATH:'+name
                tail=block[-256:]
    nul=out/'appendix_paths.nul';nul.write_bytes(b''.join(n.encode()+b'\0'for n in appendix))
    git(['add','-f','--pathspec-from-file='+str(nul),'--pathspec-file-nul']);after=entries(git(['ls-files','--stage','-z']))
    assert all(after.get(n,(None,None))[1]==h for n,h in expected.items())
    assert all(after.get(n)==v for n,v in before.items()if n not in expected)
    assert all(after.get(n)==v for n,v in before.items()if v[0]=='160000') and sha(ROOT/'CLAIMS.yaml')==LEDGER
    result=dict(status='WAVE38_FINAL_DECLARED_RECEIPTS_RAW_INDEX_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=git(['rev-parse','HEAD']).decode().strip(),source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        ledger_sha256=LEDGER,appendix_sha256=pins,appendix_paths=appendix,selected_paths_scanned=len(names),credential_values_printed=False,
        original_index_entries_preserved=True,submodule_entries_preserved=True,ledger_unchanged=True,mathematical_replay=False,
        committed=False,published=False,deadline=d.status())
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=result['status'],appendix_paths=len(appendix),selected_paths_scanned=len(names))))
if __name__=='__main__':main()
