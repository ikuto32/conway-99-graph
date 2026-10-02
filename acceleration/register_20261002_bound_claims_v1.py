"""Append only exact independently checked revisions supplied by immutable bindings.

Bookkeeping/identity checks, with conservative impact validation; no mathematical
replay or self-approval. The input ledger and each binding must be explicitly pinned.
"""
import argparse,copy,hashlib,json,os,subprocess,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import yaml
import validate_claims as registry

ROOT=Path(__file__).resolve().parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--previous-sha256',required=True)
    ap.add_argument('--binding',action='append',type=Path,required=True);ap.add_argument('--binding-sha256',action='append',required=True)
    args=ap.parse_args();need(len(args.binding)==len(args.binding_sha256),'paired exact binding identities')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    before=(ROOT/'CLAIMS.yaml').read_bytes();need(hashlib.sha256(before).hexdigest()==args.previous_sha256,'exact prior ledger')
    old=registry.read_ledger(ROOT/'CLAIMS.yaml');data=copy.deepcopy(old);now=datetime.now(timezone.utc).isoformat();new=[]
    for binding_path,expected in zip(args.binding,args.binding_sha256):
        path=binding_path.resolve();need(path.is_relative_to(ROOT) and digest(path)==expected,'immutable binding')
        binding=json.loads(path.read_bytes());cid=binding['id'];revision=binding['revision']
        need(revision==1 and cid not in {c['id'] for c in data['claims']},'new exact revision1')
        need(binding['status']=='VERIFIED' and binding['review_state']=='CLEAR','independent exact-scope checking status')
        need(binding['producer']!=binding['verifier'] and binding['verifier'] in {'/root/checkpoint_audit','/root/structural'},'separate checking identity')
        if 'verification_records' in binding:
            check=binding['verification_records'][0];report_path=check['audit_path'];report_sha=check['audit_sha256']
            checked_at=check['timestamp'];method='independent_artifact_check'
        else:
            report_path=binding['report'];report_sha=binding['report_sha256'];checked_at=binding['verification_timestamp'];method=binding['method']
        need(digest(ROOT/report_path)==report_sha,'exact checking report')
        report=json.loads((ROOT/report_path).read_bytes())
        need(report.get('verifier',binding['verifier'])==binding['verifier'],'report checking identity')
        if 'statement' in report:need(report['statement']==binding['statement'],'exact recorded statement')
        paths={path.relative_to(ROOT).as_posix():expected,report_path:report_sha}
        paths.update(binding.get('inputs_sha256',{}))
        for row in binding.get('artifacts',[])+binding.get('evidence',[]):
            if isinstance(row,dict) and 'path' in row:paths[row['path']]=row['sha256']
        evidence=[];hashes={}
        for index,(name,identity) in enumerate(sorted(paths.items())):
            artifact_path=(ROOT/name).resolve();need(artifact_path.is_relative_to(ROOT) and digest(artifact_path)==identity,'complete exact binding input '+name)
            aid=cid.lower()+'-r1-evidence-'+str(index)
            need(aid not in {a['id'] for a in data['artifacts']},'new artifact ID')
            data['artifacts'].append(dict(id=aid,path=name,sha256=identity,availability='LOCAL_ONLY',
                retrieval='Exact workspace path; checking reports give raw input and replay commands.',
                unavailable_reason='Immutable publication of this newly bound evidence has not yet been confirmed.'))
            evidence.append(aid);hashes[aid]=identity
        scope=binding['scope'] if isinstance(binding['scope'],dict) else dict(description=binding['scope'],unrestricted_target=False,target_resolution='NONE')
        need(scope['target_resolution']=='NONE','no resolution promotion in this registrar')
        verification=dict(claim_revision=revision,verifier=binding['verifier'],method=method,command_or_audit=report_path,
            timestamp=checked_at,outcome='PASS',scope=scope['description'],artifact_hashes=hashes,
            shared_components=binding.get('shared_components',report['shared_components']),
            controls=[json.dumps(binding.get('controls',report.get('controls',report.get('corrupted_controls_rejected'))),sort_keys=True)],
            limitations=binding['limitations'])
        claim={key:binding[key] for key in ['id','revision','statement','kind','basis','status','review_state','assumptions','dependencies','limitations']}
        claim.update(scope=scope,evidence=evidence,verification=[verification],created_at=now,updated_at=now,external_source=None,
            unknowns=dict(external_source='Internal scoped checking; no external or novelty status inferred.',premises=json.dumps(binding.get('premise_state',binding.get('mathematical_scope',{})),sort_keys=True)),
            reproducibility=dict(manifest=next(aid for aid in evidence if next(a for a in data['artifacts'] if a['id']==aid)['path']==report_path)))
        data['claims'].append(claim);new.append(cid)
    need(data['claims'][:len(old['claims'])]==old['claims'],'all prior material claim records unchanged')
    data['updated_at']=now
    result=registry.validate(data,ROOT,json.loads((ROOT/'docs/claims.schema.json').read_bytes()),'none',old)
    need(result['valid'],repr(result['errors']))
    after=yaml.safe_dump(data,sort_keys=False,width=110).encode()
    (out/'CLAIMS.before.yaml').write_bytes(before);(out/'CLAIMS.after.yaml').write_bytes(after);save(out/'validation.json',result)
    report=dict(timestamp=now,status='EXACT_BOUND_SCOPED_CLAIMS_REGISTERED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=digest(Path(__file__)),before_ledger_sha256=args.previous_sha256,
        ledger_sha256=hashlib.sha256(after).hexdigest(),new_claim_ids=new,claim_records=len(data['claims']),status_counts=dict(Counter(c['status'] for c in data['claims'])),
        review_state_counts=dict(Counter(c['review_state'] for c in data['claims'])),new_exclusions=0,target_resolution='UNKNOWN',
        overall_search_coverage='UNKNOWN; no validated denominator.',mathematical_replays=0)
    need((ROOT/'CLAIMS.yaml').read_bytes()==before,'no concurrent ledger change')
    pending=out/'CLAIMS.pending.yaml';pending.write_bytes(after);os.replace(pending,ROOT/'CLAIMS.yaml');save(out/'summary.json',report)
    print(json.dumps({k:report[k] for k in ['status','claim_records','status_counts','new_claim_ids']}))


if __name__=='__main__':main()
