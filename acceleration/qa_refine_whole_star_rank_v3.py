"""Engineering controls only; toy binary payloads are not scientific models."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import struct

import refine_whole_star_rank_v3 as r


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    out=r.path(a.out);r.require(not out.exists(),'Preserve previous controls');out.mkdir(parents=True)
    controls=[]
    def reject(name,call):
        try:call()
        except (ValueError,KeyError,TypeError) as e:controls.append(dict(name=name,outcome='REJECT',reason=str(e)))
        else:raise ValueError('Accepted corruption: '+name)
    payload=b''.join(struct.pack('<I',i) for i in range(32))
    raw=b'C99SCP01'+struct.pack('<3I',32,1,500)+payload
    source=out/'TOY_NOT_GPU_MODEL_500.bin';source.write_bytes(raw)
    target=out/'TOY_NOT_GPU_MODEL_5000.bin';r.copy_header_only(source,target)
    cases=[dict(index=i,record_byte_offset=20+4*i,byte_length=4,record_sha256=r.sha256(payload[4*i:4*i+4]).hexdigest()) for i in range(32)]
    identity=r.payload_identity(source,target,cases)
    r.require(identity['payload_sha256']==r.sha256(payload).hexdigest(),'Toy payload hash')
    controls.append(dict(name='HEADER_ONLY_FULL_PAYLOAD_AND_RECORD_IDENTITIES',outcome='ACCEPT'))
    mutations=[('bad_magic',0,1),('changed_count',8,1),('changed_checkpoint_count',12,1),('wrong_iteration',16,1),('changed_payload',24,1)]
    for name,offset,xor in mutations:
        data=bytearray(target.read_bytes());data[offset]^=xor;q=out/(name+'.bin');q.write_bytes(data)
        reject(name,lambda q=q:r.payload_identity(source,q,cases))
    for name,data in [('truncated',target.read_bytes()[:-1]),('trailing',target.read_bytes()+b'\0')]:
        q=out/(name+'.bin');q.write_bytes(data);reject(name,lambda q=q:r.payload_identity(source,q,cases))
    for name,change in [('wrong_record_offset',lambda c:c[0].update(record_byte_offset=24)),
        ('wrong_record_hash',lambda c:c[0].update(record_sha256='0'*64)),('wrong_record_length',lambda c:c[0].update(byte_length=5)),
        ('missing_record',lambda c:c.pop()),('wrong_record_order',lambda c:c.reverse())]:
        c=deepcopy(cases);change(c);reject(name,lambda c=c:r.payload_identity(source,target,c))
    reject('overwrite_input',lambda:r.copy_header_only(source,source))
    reject('overwrite_output',lambda:r.copy_header_only(source,target))
    rows=[dict(proposal_index=i,best_lower_numeric=float(128-i),best_upper_numeric=float(129+i)) for i in range(128)]
    excluded=list(range(16));chosen,upper,lower=r.selection(rows,excluded)
    r.require([x['proposal_index'] for x in chosen]==list(range(16,24))+list(range(127,119,-1)) and len(upper)==112,
        'Untested-only union16')
    controls.append(dict(name='UNTESTED112_UNION8_PLUS8',outcome='ACCEPT'))
    equal=[dict(proposal_index=i,best_lower_numeric=1.,best_upper_numeric=2.) for i in range(128)]
    fill,_,_=r.selection(equal,excluded)
    r.require([x['proposal_index'] for x in fill]==list(range(16,32)) and fill[0]['selection_roles']==['upper','lower'] and
        fill[8]['selection_roles']==['upper_fill'],'Tie/order/unionfill')
    controls.append(dict(name='TIES_AND_OVERLAP_FILL',outcome='ACCEPT'))
    for name,change in [('duplicate_id',lambda rr,ee:rr[17].update(proposal_index=16)),
        ('bool_id',lambda rr,ee:rr[0].update(proposal_index=False)),('missing_row',lambda rr,ee:rr.pop()),
        ('missing_exclusion',lambda rr,ee:ee.pop()),('duplicate_exclusion',lambda rr,ee:ee.__setitem__(0,1)),
        ('unknown_exclusion',lambda rr,ee:ee.__setitem__(0,999)),('nan_upper',lambda rr,ee:rr[0].update(best_upper_numeric=float('nan'))),
        ('infinite_lower',lambda rr,ee:rr[0].update(best_lower_numeric=float('inf'))),
        ('inverted_bracket',lambda rr,ee:rr[0].update(best_lower_numeric=1000.)),('bool_score',lambda rr,ee:rr[0].update(best_upper_numeric=True))]:
        rr,ee=deepcopy([rows,excluded]);change(rr,ee);reject(name,lambda rr=rr,ee=ee:r.selection(rr,ee))
    inputs={r.key(p):r.digest(p) for p in [__file__,r.__file__]+list(r.PINS)}
    artifacts={r.key(p):r.digest(p) for p in out.iterdir() if p.is_file()}
    report=dict(status='WHOLE_STAR_RERANK_V3_PRODUCER_CONTROLS_PASS',created_at=r.now(),inputs_sha256=inputs,outputs_sha256=artifacts,
        controls=controls,positive_controls=sum(c['outcome']=='ACCEPT' for c in controls),negative_controls=sum(c['outcome']=='REJECT' for c in controls),
        source_import_shared_with_producer=True,independent_verification=False,scientific_model_fixtures=False,GPU_processes=0,LP_runs=0,
        scope='Header-only byte and record identity plus deterministic untested112 union policy; no scientific claim')
    r.save(out/'report.json',report)
    print(json.dumps(dict(status=report['status'],positive_controls=report['positive_controls'],negative_controls=report['negative_controls'],report_sha256=r.digest(out/'report.json'))))


if __name__=='__main__':main()
