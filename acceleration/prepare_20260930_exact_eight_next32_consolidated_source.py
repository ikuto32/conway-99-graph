"""Preserve unexecuted single-summary draft; prepare explicit consolidated input."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration';OLD=A/'native_20260930_exact_eight_next32.py';NEW=A/'native_20260930_exact_eight_next32_v2.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD)=='4dc6fbd4254be6da61ca6a4923f63e2bbad45a21a0534c0ff5260e90f64ddf94'
t=OLD.read_text(encoding='utf8');before="BATCH=B/'20260930_exact_eight_next32_cnfs/summary.json';UNIVERSE=";assert t.count(before)==1;t=t.replace(before,"BATCH=None;UNIVERSE=")
old="def run(args):\n    out=args.out.resolve();"
new="def run(args):\n    global BATCH\n    BATCH=args.batch_summary.resolve();h.require(BATCH.is_relative_to(ROOT)and BATCH.is_file(),'explicit repository-contained complete32 consolidation')\n    out=args.out.resolve();"
assert t.count(old)==1;t=t.replace(old,new)
t=t.replace("for n in ['out','encoding-gate','object-gate','object-checker']:","for n in ['out','batch-summary','encoding-gate','object-gate','object-checker']:")
needle="        summary=h.read(ROOT/r['files']['summary.json']['path'])"
t=t.replace(needle,needle+"\n        h.require(summary['case_id']==r['case_id']and summary['attempt_id']==r['attempt_id']and summary['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT'and summary['native_calls']==0,'individual complete build/attempt identity across consolidation')")
t=t.replace("manifest=dict(timestamp=", "manifest=dict(build_consolidation_path=h.key(BATCH),build_consolidation_sha256=args.batch_summary_sha256,timestamp=")
with NEW.open('x',encoding='utf8',newline='\n')as f:f.write(t)
print(json.dumps(dict(source_path=NEW.relative_to(ROOT).as_posix(),source_sha256=sha(NEW),preserved_unexecuted_draft=OLD.relative_to(ROOT).as_posix(),preserved_draft_sha256=sha(OLD),source_only=True,native_calls=0,preflight_calls=0)))
