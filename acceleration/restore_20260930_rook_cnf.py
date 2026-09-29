"""Replay exact augmented CNF bytes from a pinned base and ordered cut records."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='acceleration/results/20260930_rook_free_internal_sat/instance.cnf'
BASE_SHA='ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403'
def stream_digest(p):
    h=sha256()
    with p.open('rb') as f:
        while b:=f.read(1<<20):h.update(b)
    return h.hexdigest()

def replay(folder,output=None):
    folder=Path(folder).resolve();folder.relative_to(ROOT)
    record=json.loads((folder/'instance_record.json').read_bytes())
    cuts_bytes=(ROOT/record['ordered_cuts']).read_bytes()
    assert sha256(cuts_bytes).hexdigest()==record['ordered_cuts_sha256']
    cuts=json.loads(cuts_bytes)
    assert record['variables']==30420 and record['clauses']==3689820+len(cuts)
    assert stream_digest(ROOT/BASE)==BASE_SHA
    writer=None
    if output is not None:
        output=Path(output).resolve();output.relative_to(ROOT);output.parent.mkdir(parents=True,exist_ok=True)
        writer=output.open('xb')
    h=sha256();n=0
    def emit(b):
        nonlocal n
        h.update(b);n+=len(b)
        if writer:writer.write(b)
    try:
        emit(('p cnf 30420 '+str(3689820+len(cuts))+'\n').encode('ascii'))
        with (ROOT/BASE).open('rb') as f:
            assert f.readline().split()==[b'p',b'cnf',b'30420',b'3689820']
            while b:=f.read(1<<20):emit(b)
        for cut in cuts:
            row=cut['clause'];assert row and all(type(v) is int and 0<abs(v)<=30420 for v in row)
            emit((' '.join(map(str,row))+' 0\n').encode('ascii'))
    finally:
        if writer:writer.close()
    assert h.hexdigest()==record['cnf_sha256'],'Replay hash mismatch; output retained for diagnosis'
    return dict(path=record['cnf'],size_bytes=n,sha256=h.hexdigest(),cuts=len(cuts),original_raw_consulted=False,mathematical_verification=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--round',required=True);p.add_argument('--out');a=p.parse_args()
    print(json.dumps(replay(a.round,a.out)))

if __name__=='__main__':main()
