"""Bind the independently checked exact MIP encoding, not its numerical result."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/'acceleration/results'
OUT=B/'20260930_independent_review/hadamard_prism_binary_mip_claim_binding'
PINS={
 'acceleration/results/20260930_independent_review/hadamard_prism_binary_mip_calibration/summary.json':'4c27ffee59dbfae792e6776cb5d6175750e31c7f65c9f5e14337d07b3acab6ca',
 'acceleration/results/20260930_hadamard_prism_binary_mip_model/exact_model.json':'8311440e1d4300f70bcdcc32e3c73baef34c9b58b8e15c54179a3a53ac4ae3ad',
 'acceleration/results/20260930_hadamard20_support/six_prism.json':'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 'acceleration/results/20260930_hadamard_support_remaining_lp/six_prism/exact_model.json':'f5ac7adc289d6ca3cc7ce77394565919813138f6322e5ae2dc1856684eef6ae2',
 'acceleration/results/20260930_independent_review/hadamard_six_prism_column_order/summary.json':'0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2',
 'acceleration/results/20260930_independent_review/hadamard20_support_v2/summary.json':'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
 'acceleration/results/20260930_independent_review/hadamard_mip_raw_controls/summary.json':'fe472fcf0b9b7d43698f7e523144475f847103e8cc42d6e82b8efb54836698eb',
}

def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    for p,v in PINS.items():
        if h(ROOT/p)!=v: raise ValueError('input pin '+p)
    gate=json.loads((ROOT/next(iter(PINS))).read_text())
    if gate['status']!='INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_MODEL_OBJECT_CALIBRATION_PASS':raise ValueError('model gate status')
    for p,v in gate['inputs_sha256'].items():
        if h(ROOT/p)!=v:raise ValueError('gate closure '+p)
    proof=[
      'The independent audit reconstructs the 90 distinct balanced fibre colorings of each six-coordinate support directly, for all 60 columns; these are exactly the 5,400 saved binary choice variables.',
      'The 60 one-hot equalities give a bijection between binary feasible choice vectors and one coloring per column. Every selected coloring gives one literal six-element row set and hence one column of the binary 36 by 60 matrix F.',
      'For every 0 <= i <= j < 36, the coefficient of a choice in its Gram row is one if and only if its row set contains both i and j. Under one-hot, the row sum is exactly (F F^T)[i,j]. The 666 equalities have the independently reconstructed prescribed Gram as their right-hand sides. Symmetry supplies the remaining ordered entries.',
      'For each of the 40 saved adjacent identical-support column pairs (d,e), one-hot makes the order row equal to rank(d)-rank(e). Its upper bound -1 is equivalent to rank(d)<rank(e), since ranks are integers. Thus the complete 766-row model is equivalent to the stated ordered Gram-factor class, in both directions.',
      'This exact-model equivalence does not impose the 1,770 outside-column overlap caps. For a proposed lazy cut with distinct columns, independently checking that the two selected row sets intersect in more than two elements proves x_a+x_b<=1 is necessary for cap-valid factors. No such cut was included in the authenticated base matrix; no claim of cap completeness is made.',
      'The existing independent normalization audit explains when column sorting preserves the intended fixed-support class. The present encoding claim states explicit strict order and does not silently add cap constraints or a residual completion.'
    ]
    save(OUT/'written_equivalence.json',dict(method='Independent exact coefficient reconstruction plus elementary bijection proof',proof=proof,producer_imports=False))
    now=datetime.now(timezone.utc).isoformat()
    cid='C-FIXED-HADAMARD-SIX-PRISM-BINARY-MIP-ENCODING'
    metadata=dict(id=cid,revision=1,statement='The authenticated exact 5,400-binary-variable, 766-row MIP model is feasible if and only if the frozen six-prism Hadamard support L admits a binary 36 by 60 factor F with the prescribed full Gram and strictly increasing saved coloring ranks along all 40 specified adjacent identical-support column pairs; outside-column overlap caps and residual D are not encoded in this base model.',kind='encoding',basis=['DERIVED','COMPUTED'],status_recommendation='VERIFIED',review_state='CLEAR',scope='One exact frozen six-prism support L and its 90 colorings per column. This is an exact binary linear encoding equivalence, not a numerical feasibility result or target-level coverage claim.',applicability_to_unrestricted_target='Conditional fixed-support class only; no unrestricted exclusion or construction.',assumptions=['Exact raw six-prism core/support hashes listed below.','Binary choices, exact integer coefficients and equalities; lower=null means negative infinity in the forty order rows.','No nontrivial target automorphism is assumed.'],dependencies=[dict(id='C-FIXED-HADAMARD-SIX-PRISM-IDENTICAL-SUPPORT-ORDER-NORMALIZATION',revision=1,relation='normalization'),dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='verification_dependency')],evidence=[dict(path=p,sha256=v,availability='LOCAL_ONLY') for p,v in PINS.items()],verification_records=[dict(claim_id=cid,claim_revision=1,verifier='/root/state_literature_audit',method='Independent artifact checking and independent derivation',report_path=next(iter(PINS)),report_sha256=next(iter(PINS.values())),outcome='PASS',scope='All 5,400 option columns, 726 equality rows, forty exact order rows, binary bounds/integrality/objective; soundness checks for a proposed lazy cut are separate from the base equivalence.',timestamp=gate['timestamp'],shared_components=gate['shared_components'],controls='Raw-helper genuine nonempty SRG243 fixture and corrupted controls; actual-model local codec explicitly fails research Gram; eleven base-model corruptions, five cut corruptions and local-codec rejection; independent native sparse-model roundtrip without a solve.')],limitations=['The initial model omits all outside-column overlap caps; a Gram-feasible factor may violate them.','No full research factor was available as a positive control; the known-valid SRG243 fixture has different parameters.','No cyclic restriction is imposed, and no residual D is encoded.','Numerical time limits, infeasibility labels, objective gaps, and absence of an incumbent are not certificates.','The separate timeout run is not a premise for this encoding claim.','No external review or novelty claim.'],created_at=now,updated_at=now,artifact_availability='LOCAL_ONLY')
    save(OUT/'claim_binding.json',metadata)
    report=dict(status='INDEPENDENT_FIXED_SUPPORT_PRISM_BINARY_MIP_CLAIM_BINDING_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),inputs_sha256={**PINS,Path(__file__).relative_to(ROOT).as_posix():h(Path(__file__))},verifier='/root/state_literature_audit',claim_id=cid,claim_revision=1,status_recommendation='VERIFIED',ledger_modified=False,solver_calls=0,artifact_availability='LOCAL_ONLY',outputs_sha256={p.relative_to(ROOT).as_posix():h(p)for p in OUT.iterdir()if p.is_file()})
    save(OUT/'summary.json',report)
    print(json.dumps(dict(status=report['status'],summary_sha256=h(OUT/'summary.json'),claim_binding_sha256=h(OUT/'claim_binding.json'))))

if __name__=='__main__':main()
