"""Independent read-only publication identity and pointer-source review."""
from pathlib import Path
from datetime import datetime,timezone
import ast,copy,hashlib,json,subprocess,sys,yaml
ROOT=Path(__file__).resolve().parents[1]
COMMIT='d43ab1ca6638b565d555b0765044668761de6a64'
SRC='acceleration/publish_20261001_twentyninth_evidence_pointers_v2.py'
FAIL='acceleration/results/20261001_twentyninth_publication_pointer_failure/summary.json'
PINS={SRC:'f54d551566c0397a96f622d4963e7fa3a06904389b548f8ac10850644dc3be6d',FAIL:'16fe0d5a2d8b74fd8d25a3f484b033b22f630e3df15a5df048853f5ef6673b26','CLAIMS.yaml':'297d6d915c244ccc6dd82c39939eef917a2b0ffa8a76126185b386774a097baf'}
OUT='acceleration/results/20261001_independent_review/twentyninth_publication_pointer_v2'

def need(v,m):
 if not v:raise ValueError(m)
def safe(p):
 q=(ROOT/p).resolve();need(q.is_relative_to(ROOT),'path containment');r=q.relative_to(ROOT).as_posix();need(r!='PROMPT.md'and not r.startswith('tools/')and r!='acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log','protected path');return q
def h(p):return hashlib.sha256(safe(p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
 out=ROOT/OUT;out.mkdir(parents=True,exist_ok=False);start_index=git('ls-files','--stage','-z');head=git('rev-parse','HEAD').decode().strip()
 for p,d in PINS.items():need(h(p)==d,'exact frozen identity '+p)
 remote=git('ls-remote','origin','refs/heads/codex/eight-coordinate-continuation-20260930').decode().split()[0];need(remote==COMMIT,'exact published branch commit')
 before=safe('CLAIMS.yaml').read_bytes();old=yaml.safe_load(before);need(len(old['claims'])==300,'300 cutoff')
 expected={'large-gpu-gate-source','large-gpu-gate-build'}
 for cohort in ['initial','followup']:
  for i in range(3):
   for j in range(2):expected.add('twentyninth-'+cohort+'-'+str(i)+'-evidence'+str(j))
 need(len(expected)==14,'independent expected identity population')
 published=[];remaining=[]
 for a in old['artifacts']:
  if a['availability']!='LOCAL_ONLY'or not a['path']:continue
  p=a['path'];safe(p)
  exists=subprocess.run(['git','cat-file','-e',COMMIT+':'+p],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if exists.returncode:
   need(exists.returncode in (1,128),'expected absent Git object');remaining.append(a['id']);continue
  blob=git('cat-file','blob',COMMIT+':'+p);digest=hashlib.sha256(blob).hexdigest()
  need(digest==a['sha256']==h(p),'workspace/ledger/commit exact byte identity');PINS[p]=digest
  published.append(dict(id=a['id'],path=p,sha256=digest,bytes=len(blob),git_blob_sha1=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()))
 need(len(published)==14 and {r['id']for r in published}==expected and len(remaining)==14,'exact fourteen public/fourteen remaining')
 diag=json.loads(safe(FAIL).read_bytes());need({(r['id'],r['path'],r['sha256'])for r in published}=={(r['id'],r['path'],r['sha256'])for r in diag['published_local_artifacts']}and set(remaining)==set(diag['remaining_local_ids']),'independent population matches preserved diagnosis')
 data=copy.deepcopy(old)
 for a in data['artifacts']:
  if a['id']in expected:a.update(availability='PUBLIC',retrieval='https://github.com/ikuto32/conway-99-graph/blob/'+COMMIT+'/'+a['path'],unavailable_reason=None)
 need(data['claims']==old['claims'],'claims remain unchanged')
 for a,b in zip(old['artifacts'],data['artifacts'],strict=True):
  changed={k for k in a.keys()|b.keys()if a.get(k)!=b.get(k)}
  need(changed<= {'availability','retrieval','unavailable_reason'}and (bool(changed)==(a['id']in expected)),'availability fields only')
 tree=ast.parse(safe(SRC).read_text(encoding='utf8'));updates=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='artifact'and n.func.attr=='update'];need(len(updates)==1 and {k.arg for k in updates[0].keywords}=={'availability','retrieval','unavailable_reason'},'source artifact mutation keys')
 text=safe(SRC).read_text(encoding='utf8');need("assert set(changed)==EXPECTED and len(changed)==14 and data['claims']==old['claims']"in text,'source exact set/claim guard')
 need(text.index("save(OUT/'transaction.json'")<text.index('os.replace(pending,path)')<text.index("os.replace(pending_record,OUT/'receipt.json')"),'prepared journal then atomic replacement then receipt')
 need("recovery_required=state!='UNCHANGED_BEFORE'"in text and "state='UNCHANGED_BEFORE' if observed==sha(before) else 'EXPECTED_AFTER' if after is not None and observed==sha(after) else 'UNKNOWN_OR_UNEXPECTED'"in text,'observed-byte failure classification')
 bad=[]
 def reject(label,predicate):need(not predicate,'accepted corruption '+label);bad.append(label)
 reject('old twelve-only assumption',len(published)==12)
 reject('omit older build source',{r['id']for r in published if r['id']!='large-gpu-gate-build'}==expected)
 damaged=copy.deepcopy(published);damaged[0]['sha256']='0'*64;reject('wrong published digest',all(r['sha256']==next(a['sha256']for a in old['artifacts']if a['id']==r['id'])for r in damaged))
 mutated=copy.deepcopy(data);mutated['claims'][0]['statement']+=' altered';reject('claim mutation',mutated['claims']==old['claims'])
 need(safe('CLAIMS.yaml').read_bytes()==before and git('ls-files','--stage','-z')==start_index and git('rev-parse','HEAD').decode().strip()==head,'ledger/index/HEAD unchanged')
 for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:PINS[p.relative_to(ROOT).as_posix()]=h(p.relative_to(ROOT))
 result=dict(status='INDEPENDENT_TWENTYNINTH_PUBLICATION_POINTER_V2_REVIEW_PASS',created_at=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],source_commit=head,published_commit=COMMIT,confirmed_remote_ref=remote,inputs_sha256=PINS,checked_published_artifacts=published,remaining_local_ids=remaining,artifact_changes_allowed=['availability','retrieval','unavailable_reason'],claims_unchanged_in_independent_construction=True,pointer_script_imported=False,pointer_script_executed=False,ledger_writes=0,git_writes=0,mathematical_verification=False,controls_rejected=bad,scope='Read-only exact14 published/workspace/ledger identities plus source-level availability-only and commit/recovery checks. Root owns eventual pointer update.',limitations=['No execution or OS fault injection of the pointer script.','Atomic local-filesystem replacement and single root writer remain trusted operational assumptions.','No mathematical claim/evidence revision or reapproval; older source/build availability is the only extension beyond12 new evidence records.'])
 with(out/'summary.json').open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(dict(status=result['status'],sha256=h(OUT+'/summary.json'))))
if __name__=='__main__':main()
