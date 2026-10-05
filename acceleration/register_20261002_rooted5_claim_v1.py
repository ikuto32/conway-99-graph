"""Register the exact independently bound universal necessary rooted5 theorem.

No discovery or mathematical verification is performed by this registrar.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]
BEFORE='e55403664288e5595316b07a2772735a35dd4de1503239992e7ca7d496c9c423'
BIND='acceleration/results/20261002_independent_review/rooted5_rigidity02/claim_binding.json'
BIND_SHA='9a14b7f1a4af1b0dcbc52cd2bfb71c477e98f6ea95b82017e6fc7a9f657e507a'


def need(ok,why):
    if not ok:raise ValueError(why)


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    before=(ROOT/'CLAIMS.yaml').read_bytes();need(hashlib.sha256(before).hexdigest()==BEFORE,'exact312-claim ledger')
    old=registry.read_ledger(ROOT/'CLAIMS.yaml');data=copy.deepcopy(old)
    need(digest(ROOT/BIND)==BIND_SHA,'immutable exact-revision independent binding')
    binding=json.loads((ROOT/BIND).read_bytes());cid=binding['id']
    need(cid=='C-UNRESTRICTED-ORDERED-PAIR-ROOTED5-RIGIDITY' and binding['revision']==binding['claim_revision']==1,'exact proposed claim')
    need(binding['verifier']=='/root/checkpoint_audit' and binding['producer']=='/root/structural' and binding['method']=='independent_derivation','separate derivation checking path')
    need(cid not in {c['id'] for c in old['claims']},'new stable ID')
    report_path=binding['report'];need(digest(ROOT/report_path)==binding['report_sha256'],'frozen report')
    report=json.loads((ROOT/report_path).read_bytes())
    need(report['status']=='INDEPENDENT_ROOTED5_RIGIDITY_AND_EXPLICIT_MOMENTS_PASS' and report['statement']==binding['statement'],'exact checked statement')
    need([(r['variables'],r['rows'],r['rank_over_Q']) for r in report['families']]==[(87,194,87),(111,224,111)],'complete exact rooted bases/rows/rank')
    # Authenticate every checking input, not just the summary; this is still
    # identity checking rather than a repeated mathematical derivation.
    for path,expected in binding['inputs_sha256'].items():need(digest(ROOT/path)==expected,'checking input identity '+path)
    choices={'audit':report_path,'binding':BIND,'derivation':'docs/DERIVATION_20261002_ROOTED5_MOMENT_RIGIDITY.md',
        'edge-counts':'acceleration/results/20261002_rooted5_flag_rigidity/ordered_edge_forced5flags.json',
        'nonedge-counts':'acceleration/results/20261002_rooted5_flag_rigidity/ordered_nonedge_forced5flags.json',
        'edge-rows':'acceleration/results/20261002_independent_review/rooted5_rigidity02/ordered_edge_audit.json',
        'nonedge-rows':'acceleration/results/20261002_independent_review/rooted5_rigidity02/ordered_nonedge_audit.json'}
    evidence=[];hashes={}
    for suffix,path in choices.items():
        aid='rooted5-'+suffix;need(aid not in {a['id'] for a in data['artifacts']},'new artifact identity')
        hashes[aid]=digest(ROOT/path);evidence.append(aid)
        data['artifacts'].append(dict(id=aid,path=path,sha256=hashes[aid],availability='LOCAL_ONLY',
            retrieval='Exact workspace path; complete small checking closure is bound in the independent report.',
            unavailable_reason='Immutable publication of this new rooted5 evidence has not yet been confirmed.'))
    now=datetime.now(timezone.utc).isoformat()
    verification=dict(claim_revision=1,verifier=binding['verifier'],method=binding['method'],command_or_audit=report_path,
        timestamp=binding['verification_timestamp'],outcome='PASS',scope=binding['scope']['description'],artifact_hashes=hashes,
        shared_components=binding['shared_components'],controls=[json.dumps(binding['controls'],sort_keys=True)],limitations=binding['limitations'])
    claim={key:binding[key] for key in ['id','revision','statement','kind','basis','status','review_state','scope','assumptions','dependencies','limitations']}
    claim.update(evidence=evidence,verification=[verification],created_at=now,updated_at=now,external_source=None,
        unknowns=dict(external_source='Independent finite derivation; literature context does not assert novelty or imported verification.'),
        reproducibility=dict(manifest='rooted5-audit'))
    data['claims'].append(claim);data['updated_at']=now
    need(data['claims'][:-1]==old['claims'] and len(data['claims'])==313,'all312 old records preserved')
    schema=json.loads((ROOT/'docs/claims.schema.json').read_bytes())
    validation=registry.validate(data,ROOT,schema,'none',old);need(validation['valid'],repr(validation['errors']))
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    (out/'CLAIMS.before.yaml').write_bytes(before);(out/'CLAIMS.after.yaml').write_bytes(after);save(out/'validation.json',validation)
    summary=dict(timestamp=now,status='ROOTED5_EXACT_SCOPED_CLAIM_REGISTERED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=digest(Path(__file__)),binding_sha256=BIND_SHA,
        before_ledger_sha256=BEFORE,ledger_sha256=hashlib.sha256(after).hexdigest(),new_claim_id=cid,revision=1,
        claims=313,verified_clear=306,candidate_clear=3,refuted_clear=4,new_exclusions=0,
        target_resolution='UNKNOWN',overall_search_coverage='UNKNOWN; no validated denominator.',
        mathematical_replays=0,limitations=['Registrar checks exact report/input identity only; independent derivation is in the bound report.','No graph, nonexistence or novelty claim.'])
    need((ROOT/'CLAIMS.yaml').read_bytes()==before,'unchanged ledger before atomic save')
    pending=out/'CLAIMS.pending.yaml';pending.write_bytes(after);os.replace(pending,ROOT/'CLAIMS.yaml')
    save(out/'summary.json',summary);print(json.dumps({k:summary[k] for k in ['status','claims','verified_clear','new_claim_id','new_exclusions']}))


if __name__=='__main__':main()
