"""In-memory independent-review gate controls; no scientific fixtures persisted."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import build_fresh_whole_v2_checkpoint as b


def fixtures():
    h='a'*64
    a=SimpleNamespace(scope_auditor_sha256=h,scope_auditor='MEMORY/auditor',scope_review='MEMORY/scope',
        exact_review='MEMORY/exact',evaluation='MEMORY/summary')
    records=[dict(proposal_index=i,result='INDEPENDENT_RAW_CHECK_PASS',fixed_K_excluded=True,
        exact_lower=dict(numerator=str(i+1),denominator='1'),exact_upper=dict(numerator=str(i+2),denominator='1')) for i in range(16)]
    summary=dict(records=[dict(**r,audited=True) for r in records],best=records[0])
    scope=dict(status='INDEPENDENT_WHOLE_FRESH_STAR_SHORTLIST_AUDIT_PASS',evaluation_path=a.evaluation,
        evaluation_sha256=h,raw_review_path=a.exact_review,raw_review_sha256=h,records=deepcopy(records),
        selected_indices=list(range(16)),producer_imported=False,original_ranked_masks_unchanged=True,best=records[0],
        inputs_sha256={b.key(p):h for p in (a.evaluation,a.exact_review,a.scope_auditor)})
    exact=dict(status='THIRD_PATH_EXACT_FIXED_K_STAR_REVIEW_PASS',records=deepcopy(records),inputs_sha256={b.key(a.evaluation):h})
    return a,summary,scope,exact


class MemoryBook:
    """Hash association semantics only. Explicitly bypasses real file hashing."""
    def __init__(self,args,scope,exact):self.docs={b.key(args.scope_review):scope,b.key(args.exact_review):exact}
    def bind(self,path,expected=None):
        h='a'*64;b.require(expected is None or expected==h,'Memory hash association');return h
    def read(self,path,status=None):
        d=self.docs[b.key(path)];b.require(status is None or d['status']==status,'Memory status association');return d
    def assert_bound(self,doc,path):b.require(doc['inputs_sha256'].get(b.key(path))==self.bind(path),'Memory binding absent')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    b.require(not a.out.exists(),'Preserve controls');controls=[]
    args,summary,scope,exact=fixtures()
    b.check_independent_review(MemoryBook(args,scope,exact),args,summary)
    for name,change in (
        ('scope_status',lambda a,s,c,e:c.update(status='CANDIDATE')),
        ('raw_status',lambda a,s,c,e:e.update(status='CANDIDATE')),
        ('unfrozen_checker',lambda a,s,c,e:setattr(a,'scope_auditor_sha256',None)),
        ('scope_missing_summary_binding',lambda a,s,c,e:c['inputs_sha256'].pop(b.key(a.evaluation))),
        ('scope_missing_raw_binding',lambda a,s,c,e:c['inputs_sha256'].pop(b.key(a.exact_review))),
        ('scope_missing_checker_binding',lambda a,s,c,e:c['inputs_sha256'].pop(b.key(a.scope_auditor))),
        ('raw_missing_summary_binding',lambda a,s,c,e:e['inputs_sha256'].clear()),
        ('wrong_evaluation_path',lambda a,s,c,e:c.update(evaluation_path='MEMORY/other')),
        ('wrong_evaluation_hash',lambda a,s,c,e:c.update(evaluation_sha256='b'*64)),
        ('wrong_raw_path',lambda a,s,c,e:c.update(raw_review_path='MEMORY/other')),
        ('scope_records_changed',lambda a,s,c,e:c['records'][0].update(proposal_index=99)),
        ('different_selected_order',lambda a,s,c,e:c['selected_indices'].reverse()),
        ('producer_imported',lambda a,s,c,e:c.update(producer_imported=True)),
        ('filtered_domains',lambda a,s,c,e:c.update(original_ranked_masks_unchanged=False)),
        ('changed_exact_lower',lambda a,s,c,e:s['records'][0].update(exact_lower=dict(numerator='0',denominator='1'))),
        ('unaudited_producer',lambda a,s,c,e:s['records'][0].update(audited=False)),
        ('wrong_report_best',lambda a,s,c,e:c.update(best=c['records'][1])),
        ('wrong_summary_best',lambda a,s,c,e:s.update(best=s['records'][1])),
    ):
        values=deepcopy([args,summary,scope,exact]);change(*values);aa,ss,cc,ee=values
        try:b.check_independent_review(MemoryBook(aa,cc,ee),aa,ss)
        except (ValueError,KeyError,TypeError) as err:controls.append(dict(name=name,outcome='REJECT',reason=str(err)))
        else:raise ValueError('Accepted corruption: '+name)
    paths=[Path(__file__),Path(b.__file__)]
    out=dict(status='WHOLE_FRESH_V2_CHECKPOINT_REVIEW_GATE_CONTROLS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),
        inputs_sha256={b.key(p):sha256(p.read_bytes()).hexdigest() for p in paths},positive_controls=1,negative_controls=len(controls),
        controls=controls,semantic_controls_bypass_hash_guards=True,scientific_fixtures_written=False,independent_verification=False,
        scope='Producer engineering gate controls only; actual file binding tested by real checkpoint preflight after review',
        scientific_reruns=0,subprocess_invocations=0,checkpoint_created=False)
    a.out.open('x',encoding='utf8').write(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],negative_controls=len(controls),sha256=sha256(a.out.read_bytes()).hexdigest())))


if __name__=='__main__':main()
