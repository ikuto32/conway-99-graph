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

# Two separately scoped revisions are independently bound to one combined audit.
# This is an exact frozen adapter, not generic substring or implication matching.
NONEDGE_BINDINGS={
    'C-UNRESTRICTED-ROOTED6-NONEDGE-NECESSARY-SYSTEM-NULLSPACE':
        'd1d98cc87c9320dab95442c77826abe3071bf40bbc4691b01c3f2f4199dec3e8',
    'C-PRISMFREE-ORDERED-NONEDGE-ROOTED6-INTEGER-DOMAIN':
        '0569ea768ae8ef2389667446cc4544cfd8c8f3e90f3d20d417c6fdab03ced653',
}
NONEDGE_REPORT='65081849ccf721eae5bdf569b16f44c88255e0421f5fab1ec26a7fa7f36e8271'

# This verifier authored the construction engine, but did not author the
# structural model or witnesses. Admit only this independently checked object.
ROOTED7_WITNESS_ID='C-ROOTED7-LITERAL-AFFINE-RATIONAL-WITNESS-RECTANGLE'
ROOTED7_WITNESS_BINDING='c86c8aaa81b82f24de95d9a1b4d6b1010f05a429d95e7ae6951f21bc17485636'
ROOTED7_WITNESS_REPORT='382459c568c8e5f9251746f60376e07c82ba981d1bab68ae2c0bc22790f04ca1'


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
        witness_role=(cid==ROOTED7_WITNESS_ID and expected==ROOTED7_WITNESS_BINDING
                      and binding['producer']=='/root/structural'
                      and binding['verifier']=='/root/native_driver')
        need(binding['producer']!=binding['verifier'] and
             (binding['verifier'] in {'/root/checkpoint_audit','/root/structural'} or witness_role),
             'separate checking identity for the exact recorded discovery')
        if 'verification_records' in binding:
            check=binding['verification_records'][0];report_path=check['audit_path'];report_sha=check['audit_sha256']
            checked_at=check['timestamp'];method='independent_artifact_check'
        else:
            report_path=binding['report'];report_sha=binding['report_sha256'];checked_at=binding['verification_timestamp'];method=binding['method']
        need(digest(ROOT/report_path)==report_sha,'exact checking report')
        report=json.loads((ROOT/report_path).read_bytes())
        need(report.get('verifier',binding['verifier'])==binding['verifier'],'report checking identity')
        if cid in NONEDGE_BINDINGS:
            need(expected==NONEDGE_BINDINGS[cid] and report_sha==NONEDGE_REPORT,
                 'exact independently bound component revision and combined report')
            need(report['status']=='INDEPENDENT_ROOTED6_NONEDGE_EXACT_NULLSPACES_AND_CONDITIONAL_DOMAIN_PASS',
                 'complete independent nonedge audit')
            need((report['variables'],report['unrestricted_rows'],report['conditional_rows'])==(567,1445,1446)
                 and report['exact_rational_ranks']==[564,565] and report['exact_nullities']==[3,2],
                 'combined audit exact operator dimensions and ranks')
            need(report['complete_integer_profiles']==210 and report['conditional_count_axes']==[[6,8024],[6,15540]]
                 and report['new_exclusions']==0 and not report['target_resolution']
                 and not report['graph_realizability_asserted'] and not report['prismfree_premise_established'],
                 'combined audit exact conditional domain and limitations')
        elif witness_role:
            need(report_sha==ROOTED7_WITNESS_REPORT and
                 report['status']=='INDEPENDENT_ROOTED7_LITERAL_CORNERS_AND_BILINEAR_WITNESSES_V1_PASS',
                 'exact independently bound literal witness audit')
            need(report['model_dimensions']==dict(variables=2766,equations=11749,term_occurrences=86129)
                 and report['integer_interpolated_point_count']==4
                 and report['rational_noninteger_interpolated_point_count']==206
                 and not report['target_resolution'],
                 'exact finite witness population and recorded limitations')
        elif 'statement' in report:need(report['statement']==binding['statement'],'exact recorded statement')
        paths={path.relative_to(ROOT).as_posix():expected,report_path:report_sha}
        paths.update(binding.get('inputs_sha256',{}))
        for collection in ('artifacts','evidence'):
            records=binding.get(collection,[])
            if isinstance(records,dict):
                for key,name in records.items():
                    if not key.endswith('_sha256'):
                        need(key+'_sha256' in records,'paired evidence mapping identity')
                        identity=records[key+'_sha256']
                        need(name not in paths or paths[name]==identity,'consistent evidence mapping')
                        paths[name]=identity
            else:
                need(isinstance(records,list),'supported evidence sequence')
                for row in records:
                    if isinstance(row,dict) and 'path' in row:
                        need(row['path'] not in paths or paths[row['path']]==row['sha256'],'consistent evidence sequence')
                        paths[row['path']]=row['sha256']
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
            shared_components=binding['shared_components'] if 'shared_components' in binding else report['shared_components'],
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
