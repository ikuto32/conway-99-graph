"""Editorial explicit conventions/control references; preserve V1 evidence."""
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
OLD='acceleration/results/20261003_incidence_low_weight_bindings01/'
LOW=OLD+'low_counts_claim_binding_schema2.json'
LOW_SHA='6cbe4a5d0651786155b93ed2f82593a363c28ae59cd62b1bc0d9ef6f85c7af7f'
RANK=OLD+'rank85_claim_binding_schema2.json'
RANK_SHA='7a020918e8a1ee7297c603a72ff15acab404e600d3db5dfb6c84f26ba5b3bfb7'
CAL='acceleration/results/20261003_independent_review/triangle_kernel_low_weight_lp_calibration01/summary.json'
CAL_SHA='b14e03ae12777c593c2fce986256859e14bcd9e6eb7619b2de2e534bd05db44d'
SPEC='acceleration/record_20261003_incidence_low_weight_bindings_v2_spec.md'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Editorial two metadata bindings/controlrefs only; preserve V1/no mathematics/ledger/index.');out=args.out.resolve();need(out.is_relative_to(ROOT),'Workspace output');out.mkdir(parents=True,exist_ok=False)
    def read(name,expected):need(sha(ROOT/name)==expected,'Exact preserved metadata '+name);return json.loads((ROOT/name).read_bytes())
    low=read(LOW,LOW_SHA);rank=read(RANK,RANK_SHA);cal=read(CAL,CAL_SHA);low_report=read(low['report'],low['report_sha256']);full=read(rank['report'],rank['report_sha256']);now=datetime.now(timezone.utc).isoformat();need(len(low_report['positive_fixtures'])==5 and sum(f['pair_checks']for f in low_report['positive_fixtures'])==25 and sum(f['literal_character_checks']for f in low_report['positive_fixtures'])==310 and low_report['strict_negative_controls']==10,'Exact low-count controls');need(len(cal['strict_corruptions'])==8 and cal['synthetic_precise_corruptions']==7 and full['actual_strict_corruption_controls']==7,'Exact weighted calibration/full controls')
    low=copy.deepcopy(low);rank=copy.deepcopy(rank)
    low['statement']='For every finite simple graph G on n vertices in which every edge has exactly one common neighbor, let B be its complete binary vertex-by-triangle incidence matrix, m its number of actual triangles, t_v the number containing vertexv, Q=sum_v binom(t_v,2), and D=im_GF(2)(B). Put N_3=m,N_4=Q,N_6=binom(m,2)-Q. Then D contains at least N_j distinct words of Hamming weightj for every j in{3,4,6}. Let C=ker_GF(2)(B^T), A_w=|{x in C:wt(x)=w}|, M=|C|=1+sum_(w>0)A_w, and K_j(w)=sum_s(-1)^s binom(w,s)binom(n-w,j-s), with binomial coefficients zero outside their integer ranges. For every j in{3,4,6}, sum_(w>0)A_w*(N_j-K_j(w))<=binom(n,j)-N_j. For every99x99 binary symmetric zero-diagonal A satisfying A^2=12I-A+2J exactly over the integers, its graph therefore has N_3=231,N_4=2079,N_6=24486 and satisfies these same sharp character inequalities. All target conclusions are conditional implications and establish neither existence nor nonexistence.'
    control_refs=[dict(path=low['report'],sha256=low['report_sha256'],role='independent_derivation_and_complete_controls',positive_fixtures=5,complete_pair_inverse_checks=25,complete_literal_character_checks=310,strict_negative_controls=10),dict(path='acceleration/results/20261003_independent_review/incidence_low_weights01/controls.json',sha256=sha(ROOT/'acceleration/results/20261003_independent_review/incidence_low_weights01/controls.json'),role='exact independent ten-corruption records')]
    low['controls_references']=control_refs
    rank['controls_references']=[dict(path=CAL,sha256=CAL_SHA,role='independent preoutput changed-checker calibration',complete_literal_small_coefficients=140,strict_rook_and_model_corruptions=8,synthetic_full_coefficients=1287,synthetic_precise_corruptions=7,full_producer_output_inspected=False),dict(path=rank['report'],sha256=rank['report_sha256'],role='independent actual full artifact checking',complete_exact_coefficients=1287,complete_nonnegative_coordinates=99,complete_weight_inequalities=13,actual_strict_corruption_controls=7),dict(path='acceleration/results/20261003_independent_review/triangle_kernel_low_weight_lp_full01/corruptions.json',sha256=sha(ROOT/'acceleration/results/20261003_independent_review/triangle_kernel_low_weight_lp_full01/corruptions.json'),role='exact full seven actual corruption records')]
    rank['recorded_validation']['preoutput_strict_rook_and_model_controls']=8;rank['recorded_validation']['preoutput_synthetic_precise_corruptions']=7
    for binding,path,identity in[(low,LOW,LOW_SHA),(rank,RANK,RANK_SHA)]:
        binding['updated_at']=now;binding['editorial_projection']=dict(original_binding=path,original_binding_sha256=identity,original_statement_preserved=True,material_quantifiers_or_scope_changed=False,revision_unchanged=1,reason='Explicit Krawtchouk/zero-word/three-degree convention and actual control references; no broader mathematical claim.');binding['writer_source_sha256']=sha(Path(__file__));binding['writer_command']=[sys.executable,*sys.argv]
        for name in[path,Path(__file__).relative_to(ROOT).as_posix(),SPEC,'acceleration/record_20261003_incidence_low_weight_bindings_v1.py','acceleration/record_20261003_incidence_low_weight_bindings_v1_spec.md']:
            binding['inputs_sha256'][name]=sha(ROOT/name)
        for rec in binding['controls_references']:binding['inputs_sha256'][rec['path']]=rec['sha256']
    save(out/'low_counts_claim_binding_schema2_v2.json',low);save(out/'rank85_claim_binding_schema2_v2.json',rank);need(sha(ROOT/LOW)==LOW_SHA and sha(ROOT/RANK)==RANK_SHA,'Original drafts preserved');save(out/'summary.json',dict(status='METADATA_ONLY_EDITORIAL_PRECISION_BINDINGS_V2_RECORDED',timestamp=now,low_counts_binding_sha256=sha(out/'low_counts_claim_binding_schema2_v2.json'),rank85_binding_sha256=sha(out/'rank85_claim_binding_schema2_v2.json'),original_low_binding_sha256=LOW_SHA,original_rank_binding_sha256=RANK_SHA,revision_unchanged=1,ledger_mutations=0,index_mutations=0,mathematical_replays=0,scientific_invocations=0,deadline=deadline.status()))
if __name__=='__main__':main()
