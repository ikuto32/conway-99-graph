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
ROOTED8_DERIVATION_BINDINGS={
    'C-PRISMFREE-ROOTED8-NONEDGE-LOCAL-CATALOGUE-COVERAGE':'6119158229ea692cbcb1e12db86a1ae112f3880ff9a492dcd35c704adb72835d',
    'C-PRISMFREE-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING':'461b9f4f3ad9661a0f921ba8c4e9936fade3d30b7dac071ae1d2b341c3baa097',
}


def need(ok,why):
    if not ok:raise ValueError(why)


# V10: three exact independently checked wave37 bindings. These are identity
# adapters, not a new mathematical checker or generic permission for ROOT roles.
WAVE37_EXACT = {
    'C-UNRESTRICTED-ROOTED7-CONTENT-DIVIDED-GF2-FOUR-PRIMALS': (
        '59be79ef4fed77ee65ce500dcbaf22eb1f4788dd53d187f97166e909d2b881e3',
        '2af2ec6f0c527c079249dede08cba32c2c403837390f46c4187ec972738a1f62',
        'VERIFIED', '/root/structural', '/root'),
    'C-HYPERGRAPH-WEIGHT60-PILOT01-TWO-GRAPH-WARM-ROOT-CENSUS': (
        'b3fd150fe6a36c0bac66984c4940fe48957c64dd323fbeb15ba7c91069feb2fb',
        '99a319ea75ca2984e3b5e85dcf42dff7e066cf8fef4d9e510d47479addf06a2f',
        'VERIFIED', '/root/native_driver', '/root'),
    'C-GENERIC-BINARY-PROJECTION-CODOMAIN-ISOTROPY-RANK-LEMMA': (
        '518ac2e90784fe6d14d0ac5a933f77ca4fd4255ad1ab58b48262b5c6b4a64d4b',
        'b61f14f953c34396bf410d443964a4e549753bcdc6b2efbd9e71256eec7aa071',
        'REFUTED', '/root', '/root/structural'),
}


def wave37_role(cid, expected, binding):
    if cid not in WAVE37_EXACT:
        return False
    identity, _, status, producer, verifier = WAVE37_EXACT[cid]
    need(expected == identity, 'exact wave37 binding identity')
    need(binding['status'] == status and binding['review_state'] == 'CLEAR'
         and binding['producer'] == producer and binding['verifier'] == verifier
         and producer != verifier and binding['method'] == 'independent_artifact_check',
         'exact wave37 status and independent artifact roles')
    need(binding['scope']['unrestricted_target'] is False
         and binding['scope']['target_resolution'] == 'NONE', 'exact finite wave37 scope')
    return True


def wave37_report(cid, report_sha, binding, report):
    if cid not in WAVE37_EXACT:
        return
    need(report_sha == WAVE37_EXACT[cid][1], 'exact wave37 independent report')
    if cid == 'C-UNRESTRICTED-ROOTED7-CONTENT-DIVIDED-GF2-FOUR-PRIMALS':
        need(report['status'] == 'INDEPENDENT_UNRESTRICTED_ROOT7_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS'
             and report['normalization_rows_checked'] == 11769
             and report['complete_scalar_primal_row_checks'] == 47076
             and report['profile_population'] == report['compatible_profiles'] == 651
             and report['excluded_profiles'] == 0 and report['rank_asserted'] is False
             and report['target_resolution'] == 'NONE', 'complete literal mod2 scope only')
        need(binding['dependencies'] == [{'id':'C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING',
             'revision':1,'relation':'verification_dependency',
             'reason':'Pinned independently reconstructed necessary-model semantics supplies the interpretation; literal mod2 certificates do not rederive this encoding.'}],
             'exact reused necessary-model dependency')
    elif cid == 'C-HYPERGRAPH-WEIGHT60-PILOT01-TWO-GRAPH-WARM-ROOT-CENSUS':
        need(report['status'] == 'INDEPENDENT_WEIGHT60_TWO_GRAPH_DENSE_ROOT_CENSUS_V1_PASS'
             and report['raw_graphs'] == 2 and report['complete_roots'] == 198
             and report['literal_triangle_population'] == 313698
             and report['complete_scalar_matrix_entries'] == 19602
             and report['target_resolution'] == 'NONE' and binding['dependencies'] == [],
             'complete two-graph census only')
        need([(r['label'], r['matching_roots'], r['fully_cn2_roots'], r['minimum_mu_row_residual'],
               r['minimum_root_ties']) for r in report['graph_records']]
             == [('final_best',99,0,50,[81]),('first_lambda0',99,0,66,[29])],
             'exact two literal graph minima and zero direct warm roots')
    else:
        need(report['status'] == 'INDEPENDENT_REJECTED_CODOMAIN_ISOTROPY_COUNTEREXAMPLE_PASS'
             and report['counterexample_sha256'] == '94d4c5331f30bf86db9d0cac0fb7821ee37d3d770536880429b55267a1d33faf'
             and report['ranks'] == {'P':54,'M':45,'B':99,'C':54}
             and report['target_bound_status'] == 'UNKNOWN' and report['target_resolution'] is False
             and binding['dependencies'] == [], 'exact generic counterexample, target bound remains unknown')

# V11 adds only these two frozen ROOT-verifier metadata adapters. V10 remains
# byte-preserved. No general ROOT role or target-resolution permission is added.
V11_ROOT_EXACT = {
    'C-UNRESTRICTED-ROOTED8-CONTENT-DIVIDED-GF2-FOUR-PRIMALS': dict(
        binding='49f8bf5af0f9c634ff751b41a572bc6219e91b07bb75126ad9575c03b5f76bc1',
        report='410e7e4dd7f4e9caff1f9eb8b349a35afd24808e44826e7d1dc89d4a0b7249c2',
        report_path='acceleration/results/20261003_independent_review/root8_mod2_full01/summary.json',
        producer='/root/structural',
        scope='Only exact primitive-row reconstruction and four literal GF2 primal certificates for one pinned unrestricted necessary model and its frozen651primary-profile population. Integer row division preserves exact equations; finite-field consistency is necessary only.',
        calibration='acceleration/results/20261003_independent_review/root8_mod2_calibration01/summary.json',
        calibration_sha256='d0238a17825e7fe23aa438c6f2f45a1cf26d470f64aa0f79c2524fc4d6900af2'),
    'C-HYPERGRAPH-WEIGHT60-V2-GRAPH-ONLY-SEED61-RESET': dict(
        binding='24bda9181cef4d872db8d1bb5e309b4c101cf9ce0b5489fc77faf730ddcab501',
        report='23917a9077bbce46c0c1222403852cbf40925cf2749f333b0fd74e04bac45d21',
        report_path='acceleration/results/20261003_independent_review/weight60_reset_full01/summary.json',
        producer='/root/native_driver',
        scope='One exact graph-only reset derivative and its four complete serialized objects/config/RNG. No old random-trajectory continuation, scientific outcome or graph search coverage.',
        calibration='acceleration/results/20261003_independent_review/weight60_reset_calibration01/summary.json',
        calibration_sha256='5e93291da1bf0b3acecc4549a8a631e682c2a6e835e695a42a0a40cd19a17d23'),
}


def v11_root_role(cid, expected, binding):
    if cid not in V11_ROOT_EXACT:
        return False
    exact=V11_ROOT_EXACT[cid]
    need(expected==exact['binding'], 'v11 exact binding identity')
    need(binding['id']==cid and binding['revision']==binding['claim_revision']==1
         and binding['status']=='VERIFIED' and binding['review_state']=='CLEAR'
         and binding['producer']==exact['producer'] and binding['verifier']=='/root'
         and binding['producer']!=binding['verifier'] and binding['method']=='independent_artifact_check'
         and binding['kind']=='empirical/engineering result' and binding['basis']==['COMPUTED'],
         'v11 exact revision status method and separate roles')
    need(binding['scope']==dict(description=exact['scope'],unrestricted_target=False,target_resolution='NONE'),
         'v11 exact scope')
    need(binding['report']==exact['report_path'] and binding['report_sha256']==exact['report'],
         'v11 exact report reference')
    return True


def v11_root_calibration(cid, binding, report, calibrated):
    exact=V11_ROOT_EXACT[cid]
    need(calibrated['verifier']=='/root', 'v11 calibration verifier')
    if cid=='C-UNRESTRICTED-ROOTED8-CONTENT-DIVIDED-GF2-FOUR-PRIMALS':
        need(binding['pre_output_calibration']==exact['calibration']
             and binding['pre_output_calibration_sha256']==exact['calibration_sha256']
             and calibrated['status']=='INDEPENDENT_UNRESTRICTED_ROOT8_MOD2_CHECKER_V1_CALIBRATION_PASS'
             and calibrated['positive_controls']==5 and calibrated['strict_negative_controls']==15
             and calibrated['full_producer_output_inspected'] is False
             and report['positive_controls']==5 and report['strict_negative_controls']==16,
             'v11 root8 preoutput and full controls')
    else:
        recorded=binding['pre_output_calibration']
        need(recorded['path']==exact['calibration'] and recorded['sha256']==exact['calibration_sha256']
             and calibrated['status']=='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_CALIBRATION_V1_PASS'
             and calibrated['controls']==report['controls']==recorded['controls']
             and calibrated['controls']['positive_controls']==recorded['positive_control_count']==2
             and calibrated['controls']['strict_negative_controls']==recorded['strict_negative_count']==15
             and calibrated['controls']['producer_output_inspected'] is False,
             'v11 reset preoutput controls')


def v11_root_report(cid, report_sha, binding, report):
    if cid not in V11_ROOT_EXACT:
        return
    exact=V11_ROOT_EXACT[cid]
    need(report_sha==exact['report'], 'v11 exact independent report')
    need(report['verifier']=='/root' and report['producer']==exact['producer'], 'v11 report roles')
    if cid=='C-UNRESTRICTED-ROOTED8-CONTENT-DIVIDED-GF2-FOUR-PRIMALS':
        need(report['status']=='INDEPENDENT_UNRESTRICTED_ROOT8_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS'
             and report['normalization_rows_checked']==86434 and report['complete_scalar_primal_row_checks']==345736
             and report['complete_scalar_relation_column_checks']==0 and report['profile_population']==report['compatible_profiles']==651
             and report['excluded_profiles']==0 and report['rank_asserted'] is False and report['target_resolution']=='NONE',
             'v11 root8 complete literal scope')
        need(binding['dependencies']==[dict(id='C-UNRESTRICTED-ROOTED8-MARKED-UNIVERSAL5-PRODUCT-NECESSARY-ENCODING',
             revision=1,relation='verification_dependency',
             reason='Independent complete necessary-encoding reconstruction supplies the target interpretation; scalar certificate checking does not rederive it.')],
             'v11 root8 exact dependency')
        need(binding['recorded_validation']==dict(normalization_rows=86434,component_scalar_row_checks=345736,
             binary_vectors=4,coordinates_per_vector=23334,profiles=651,compatible_profiles=651,excluded_profiles=0,
             positive_controls=5,strict_negative_controls=16,actual_fullwidth_coordinate_flip_rejected=True,
             content_census={'1':82563,'2':3842,'4':29}), 'v11 root8 recorded validation')
    else:
        need(report['status']=='INDEPENDENT_WEIGHT60_GRAPH_ONLY_RESET_V1_PASS'
             and report['graphs_preserved']==['current','best','first_current','first_best']
             and report['complete_reset_scalar_entries']==39204 and report['lambda_energy']==0
             and report['mu_energy']==3608 and report['identity_mismatches']==4934
             and report['target_resolution']=='NONE' and binding['target_resolution'] is False
             and binding['dependencies']==[], 'v11 reset exact object scope')
        need(report['parameters']==dict(seed=99032061,mix_steps=0,schedule_steps=80000000,t_start=8.0,t_end=0.1,
             forced=0,step=0,admissible=0,accepted=0,best_updates=0), 'v11 reset exact parameters')
        need(report['inputs_sha256']['acceleration/results/20261003_weight60_graph_reset01/reset.state']
             =='f9cd59ab9d9bd3dcb89b6fab32784f17d3c744e047ebe23d212e2fd4f5bf6665'
             and report['inputs_sha256']['acceleration/results/20261002_hypergraph_weight60_pilot01/native/final.state']
             =='0dc37fdc2dd58fb78f55b88fd8e2ee7c43a83d32d1cc7897591151d5aca6a1bb',
             'v11 reset exact source object identities')
    need(digest(ROOT/exact['calibration'])==exact['calibration_sha256'], 'v11 exact calibration bytes')
    calibrated=json.loads((ROOT/exact['calibration']).read_bytes())
    v11_root_calibration(cid,binding,report,calibrated)

# V12 adds exactly two pinned ROOT-verifier adapters; V11.2 is byte-preserved.
V12_ROOT_EXACT={
 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67':dict(
  binding='4e018e2be2705f4684b31266797571d0eaab1eeb5ce15603d4765a77265e4848',
  report='f6d37038fa7f5969331e8d7ee9490bdcc6ebda09b3a0770b7a99dea298a9c59b',
  report_path='acceleration/results/20261003_independent_review/incidence_griesmer01/summary.json',
  producer='/root/structural',method='independent_derivation',kind='mathematical result',basis=['DERIVED'],unrestricted=True,
  scope='Universal conditional necessary rank lower bound for the unrestricted target identity. Complete written independent derivation supplies the quantifiers; finite exact controls challenge critical steps only.',
  statement='For every99x99 binary symmetric zero-diagonal matrix A satisfying A^2=12I-A+2J exactly over the integers, let B be its99x231 binary vertex-by-triangle incidence matrix with one column for every actual triangle. Then rank_GF(2)(B)>=67, equivalently dim_GF(2)ker(B^T)<=32. This is a conditional implication and establishes neither existence nor nonexistence of such A.',
  controls='acceleration/results/20261003_independent_review/incidence_griesmer01/controls.json',controls_sha256='85ae2978864cdb121b8f76e56669d2aa3eef40e194becc074d51fbadea89a327',
  proof='acceleration/audit_20261003_incidence_griesmer_v1.md',proof_sha256='65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d'),
 'C-HYPERGRAPH-WEIGHT60-WARM01-TWO-GRAPH-WARM-ROOT-CENSUS':dict(
  binding='e49ba355e4ca8cf99e883d69594d6a972480b55aade5c6f60ecf9fe7d4566bff',
  report='becf048cbb32ec577a78c7084fc949103af91f66c92c5936137a9740c5cdd35a',
  report_path='acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/summary.json',
  producer='/root/structural',method='independent_artifact_check',kind='empirical/engineering result',basis=['COMPUTED'],unrestricted=False,
  scope='Complete198 labelled-root census of exactly two pinned saved partial graphs; no other graphs or hypothetical target objects. No SAT instance, target exclusion, scaffold-equivalence certificate or target resolution.',
  statement='For exactly the two frozen labelled99-vertex raw warm graphs final_best (adjacency SHA2569d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d) and stepzero first_lambda0 (adjacency SHA256818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836), every one of their198 labelled roots has a14-neighbor perfect matching, and no root has common-neighbor count2 for all84 outsiders. The minimum exact row residual sum_over_outsiders(CN(root,v)-2)^2 is52 at all and only roots11,41,77 in final_best and50 uniquely at root81 in stepzero first_lambda0; their exact global mu residual energies are3480 and3608 respectively.',
  controls='acceleration/results/20261003_independent_review/weight60_warm_roots_dense01/calibration.json',controls_sha256='fb4e8b514c07a85f892fcd2ba0056d7bddb14a6596d6641bb4539624730fd06b'),
}


def v12_root_role(cid,expected,binding):
    if cid not in V12_ROOT_EXACT:return False
    exact=V12_ROOT_EXACT[cid]
    need(expected==exact['binding'],'v12 exact binding identity')
    need(binding['id']==cid and binding['revision']==binding['claim_revision']==1
         and binding['status']=='VERIFIED' and binding['review_state']=='CLEAR'
         and binding['producer']==exact['producer'] and binding['verifier']=='/root'
         and binding['producer']!=binding['verifier'] and binding['method']==exact['method']
         and binding['kind']==exact['kind'] and binding['basis']==exact['basis'],
         'v12 exact revision status method and separate roles')
    need(binding['scope']==dict(description=exact['scope'],unrestricted_target=exact['unrestricted'],target_resolution='NONE'),'v12 exact scope')
    need(binding['statement']==exact['statement'],'v12 exact statement')
    need(binding['report']==exact['report_path']and binding['report_sha256']==exact['report'],'v12 exact report reference')
    need(binding['dependencies']==[],'v12 exact dependencies')
    return True


def v12_root_controls(cid,binding,report,controlled):
    exact=V12_ROOT_EXACT[cid]
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67':
        need(controlled==report['controls']and controlled['positive_graph']=='SRG(9,4,1,2) rook graph'
             and controlled['scalar_matrix_entries']==81 and controlled['complete_kernel_population']==16
             and controlled['nonzero_kernel_words_checked']==15 and controlled['weight_histogram']=={'0':1,'4':9,'6':6}
             and controlled['strict_corrupt_controls']==[
              dict(case='missing_triangle',diagnostic='complete literal triangle incidence'),
              dict(case='duplicate_triangle',diagnostic='complete literal triangle incidence'),
              dict(case='altered_incidence',diagnostic='complete literal triangle incidence'),
              dict(case='altered_graph',diagnostic='diagonal and all degrees'),
              dict(case='nonminimum_puncturing',diagnostic='puncture a minimum-weight word')]
             and controlled['small_binary_code_populations']==[dict(length=n,subspaces=s)for n,s in enumerate([1,2,5,16,67,374,2825])]
             and controlled['total_subspaces']==3290 and controlled['minimum_word_residual_checks']==5855
             and controlled['general_code_without_incidence_not_given_distance36']is True
             and controlled['target_even_weight_set']==list(range(36,61,2))
             and controlled['target_dimension33_griesmer_terms']==[36,18,9,5,3,2]+[1]*27
             and controlled['target_dimension33_sum']==100,'v12 Griesmer complete finite controls')
        need(binding['recorded_validation']==dict(written_derivation='Complete incidence partition, exact integer moments/Cauchy, independent residual-code induction and rank-nullity.',positive_fixture='Rook9 complete16-word triangle kernel,15 nonzero words.',small_code_controls=dict(binary_subspaces=3290,lengths='0..6',minimum_word_residual_checks=5855),strict_negative_controls=5,finite_controls_are_general_proof=False),'v12 Griesmer recorded controls')
    else:
        recorded=binding['pre_output_calibration']
        need(controlled==report['controls']and controlled['positive_roots']==9 and controlled['strict_negative_controls']==5
             and recorded['path']==exact['controls']and recorded['sha256']==exact['controls_sha256']
             and recorded['positive_root_count']==9 and recorded['negative_control_count']==5
             and recorded['corrupted_controls']==['diagonal1','asymmetric edge deletion','boolean entry rejected as nonliteral integer','binary-domain entry2','corrupted dense common-neighbor entry inconsistent with literal witnesses']
             and recorded['timing']==controlled['control_timing'],'v12 warm census complete finite controls')


def v12_root_report(cid,report_sha,binding,report):
    if cid not in V12_ROOT_EXACT:return
    exact=V12_ROOT_EXACT[cid]
    need(report_sha==exact['report'],'v12 exact independent report')
    need(report['producer']==exact['producer']and report['verifier']=='/root'and report['method']==exact['method'],'v12 report roles and method')
    need(binding['dependencies']==[],'v12 exact dependencies')
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67':
        need(report['status']=='INDEPENDENT_CONDITIONAL_TRIANGLE_INCIDENCE_GRIESMER_DERIVATION_V1_PASS'
             and report['exact_claim']=='Every binary symmetric zero-diagonal99matrix A satisfying A^2=12I-A+2J has triangle-incidence rank_GF2(B)>=67, equivalently dim ker(B^T)<=32.'
             and report['minimum_rank']==67 and report['maximum_kernel_dimension']==32
             and report['nonzero_kernel_weights']==list(range(36,61,2))
             and report['conditional_premise']=='Existence of a complete graph with the exact target integer identity remains UNKNOWN.'
             and report['target_resolution']=='NONE'and report['graph_constructed']is False and report['target_nonexistence']is False
             and report['rank_upper72_status']=='UNKNOWN; refuted generic lemma supplies no such premise.'
             and binding['premise_state']=='UNKNOWN'
             and binding['rank_upper72_state']=='UNKNOWN; the separately refuted generic linear lemma is not a dependency or premise.',
             'v12 exact conditional Griesmer scope')
        need(binding['written_audit']==report['written_audit']==exact['proof']
             and report['inputs_sha256'][exact['proof']]==binding['inputs_sha256'][exact['proof']]==exact['proof_sha256']
             and digest(ROOT/exact['proof'])==exact['proof_sha256'],'v12 exact independently written proof')
    else:
        need(report['status']=='INDEPENDENT_WEIGHT60_WARM_TWO_GRAPH_DENSE_ROOT_CENSUS_V2_PASS'
             and report['raw_graphs']==2 and report['complete_roots']==198
             and report['literal_triangle_population']==313698 and report['complete_scalar_matrix_entries']==19602
             and report['target_resolution']=='NONE','v12 exact finite warm census population')
        need(report['graph_records']==[
             dict(label='final_best',matching_roots=99,fully_cn2_roots=0,minimum_mu_row_residual=52,minimum_root_ties=[11,41,77],selected_root=11,triangle_count=231,global_mu_energy=3480),
             dict(label='first_lambda0',matching_roots=99,fully_cn2_roots=0,minimum_mu_row_residual=50,minimum_root_ties=[81],selected_root=81,triangle_count=231,global_mu_energy=3608)],'v12 exact warm census graph records')
        need(report['inputs_sha256']['acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj']=='9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d'
             and report['inputs_sha256']['acceleration/results/20261003_hypergraph_weight60_warm01/native/first_lambda0.adj']=='818314b75fccfa0f3fe702602afb02b6415f3138a770ef15ed0621d189d88836','v12 exact two warm raw graph identities')
    need(binding['inputs_sha256'][exact['controls']]==exact['controls_sha256']
         and digest(ROOT/exact['controls'])==exact['controls_sha256'],'v12 exact control bytes')
    v12_root_controls(cid,binding,report,json.loads((ROOT/exact['controls']).read_bytes()))



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
        exact_wave37 = wave37_role(cid, expected, binding)
        exact_v11 = v11_root_role(cid, expected, binding)
        exact_v12 = v12_root_role(cid, expected, binding)
        need((binding['status']=='VERIFIED' or exact_wave37) and binding['review_state']=='CLEAR','independent exact-scope checking status')
        witness_role=(cid==ROOTED7_WITNESS_ID and expected==ROOTED7_WITNESS_BINDING
                      and binding['producer']=='/root/structural'
                      and binding['verifier']=='/root/native_driver')
        need(binding['producer']!=binding['verifier'] and
             (binding['verifier'] in {'/root/checkpoint_audit','/root/structural'} or witness_role or exact_wave37 or exact_v11 or exact_v12),
             'separate checking identity for the exact recorded discovery')
        if 'verification_records' in binding:
            check=binding['verification_records'][0];report_path=check['audit_path'];report_sha=check['audit_sha256']
            checked_at=check['timestamp'];method='independent_artifact_check'
        else:
            report_path=binding['report'];report_sha=binding['report_sha256'];checked_at=binding['verification_timestamp'];method=binding['method']
        recorded_method=method
        if method=='independent_derivation_and_complete_artifact_checking':
            need(expected==ROOTED8_DERIVATION_BINDINGS.get(cid) and binding['verifier']=='/root/checkpoint_audit',
                 'exact combined derivation binding for schema method mapping')
            method='independent_derivation'
        need(digest(ROOT/report_path)==report_sha,'exact checking report')
        report=json.loads((ROOT/report_path).read_bytes())
        wave37_report(cid, report_sha, binding, report)
        v11_root_report(cid, report_sha, binding, report)
        v12_root_report(cid, report_sha, binding, report)
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
        elif cid == 'C-PRISMFREE-ROOTED7-PER-VERTEX-MEAN-NECESSARY-ROWS':
            need(expected == '15b6edc63b1849b2b2c1302fd91549adc6392a084638d2b3ed534cb5ef9cf7af'
                 and report_sha == 'ffd497c6afacb9173bcb215eceab7603e7530d18d9c4a51dad6ea0e7d8e1d025'
                 and binding['verifier'] == '/root/checkpoint_audit' and binding['producer'] == '/root/structural',
                 'exact conditional rows binding to combined independent means audit')
            need(report['status'] == 'INDEPENDENT_ROOTED6_PER_VERTEX_GLOBAL_MEANS_V2_PASS'
                 and report['derived_conditional_root7_rows'] == report['all_saved_corners_checked'] == report['saved_corners_passing_derived_rows'] == 4
                 and report['profiles_excluded'] == 0 and report['prism_absence_status'] == 'UNKNOWN'
                 and report['root_swap_same_free_orbit'] is True and report['target_resolution'] is False,
                 'exact conditional four-row audit and unchanged unknown premise')
            need(digest(ROOT/report['written_proof']) == '570216537a80c0766737afa52a3a447d8392065d59c1bda95675701e3782625d',
                 'complete independently written necessary-row derivation')
        elif 'statement' in report:need(report['statement']==binding['statement'],'exact recorded statement')
        normalized_adapter = (cid == 'C-PRISMFREE-ROOTED8-NORMALIZED-LITERAL-GF2-THREE-PRIMALS'
                              and expected == '9fb71449199b211ac1cad462df2714384b3e0096022b4adc3799d153ceeb7642')
        original_scope = None
        if normalized_adapter:
            need(report_sha == '5e4eaad1a1d8945e33435d2fb09bb113f648f3adc1c7f568fc000f28a132bc14'
                 and binding['producer'] == '/root/native_driver' and binding['verifier'] == '/root/structural',
                 'exact separately checked normalized literal binding')
            need(report['status'] == 'INDEPENDENT_NORMALIZED_GF2_THREE_FULL_PRIMALS_PASS'
                 and report['rows_normalization_checked'] == 85874
                 and report['full_scalar_row_component_checks'] == 257622
                 and report['rank_claim'] is False and report['target_resolution'] is False
                 and report['profile_parity_population']['all210_integer_profiles_mod2_consistent'] is True,
                 'complete raw scalar checks and no stronger promotion')
            binding = copy.deepcopy(binding)
            binding['shared_components'] = binding['verification']['shared_components']
            binding['inputs_sha256'] = dict(report['inputs_sha256'])
            calibration = binding['pre_output_calibration']
            need(calibration['sha256'] == '63ae57b00a0cdc87ec2209dceb8e185ef70cd1ac350bf3a51ab0b7c13dfe5611'
                 and calibration['full_output_inspected'] is False
                 and digest(ROOT/calibration['path']) == calibration['sha256'], 'exact pre-output checker calibration')
            calibrated = json.loads((ROOT/calibration['path']).read_bytes())
            need(calibrated['status'] == 'INDEPENDENT_NORMALIZED_GF2_FULL_CHECKER_CALIBRATION_V1_PASS',
                 'actual frozen full-checker calibration passed')
            for name, identity in {calibration['path']: calibration['sha256'], **calibrated['inputs_sha256']}.items():
                need(name not in binding['inputs_sha256'] or binding['inputs_sha256'][name] == identity,
                     'consistent complete checking closure')
                binding['inputs_sha256'][name] = identity
            for vector in binding['certificate_artifacts']:
                need(binding['inputs_sha256'][vector['path']] == vector['sha256']
                     and (ROOT/vector['path']).stat().st_size == vector['bytes'], 'bound complete primal vector')
            original_scope = binding['scope']
            binding['scope'] = {key:original_scope[key] for key in ('description','unrestricted_target','target_resolution')}
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
        original_kind = binding['kind']
        if cid == 'C-UNRESTRICTED-ROOTED6-PER-VERTEX-GLOBAL-PRISM-MEAN-IDENTITIES':
            need(expected == 'f39634de8e150908b4846c0c1959ca7d7c7e73df4b3877399de3875c2a0fecf7'
                 and report_sha == 'ffd497c6afacb9173bcb215eceab7603e7530d18d9c4a51dad6ea0e7d8e1d025'
                 and binding['kind'] == 'mathematical_result' and method == 'independent_derivation'
                 and binding['verifier'] == '/root/checkpoint_audit' and report['statement'] == binding['statement'],
                 'exact universal theorem kind spelling adapter')
            binding = copy.deepcopy(binding)
            binding['kind'] = 'mathematical result'
        claim={key:binding[key] for key in ['id','revision','statement','kind','basis','status','review_state','assumptions','dependencies','limitations']}
        dependency_notes=[]
        for dependency in binding['dependencies']:
            need(set(dependency)<= {'id','revision','relation','reason'},'supported bound dependency fields')
            if 'reason' in dependency:dependency_notes.append(dict(id=dependency['id'],revision=dependency['revision'],reason=dependency['reason']))
        claim['dependencies']=[{key:dependency[key] for key in ('id','revision','relation')} for dependency in binding['dependencies']]
        claim.update(scope=scope,evidence=evidence,verification=[verification],created_at=now,updated_at=now,external_source=None,
            unknowns=dict(external_source='Internal scoped checking; no external or novelty status inferred.',premises=json.dumps(binding.get('premise_state',binding.get('mathematical_scope',{})),sort_keys=True),dependency_notes=json.dumps(dependency_notes,sort_keys=True),original_binding_method=recorded_method,original_binding_kind=original_kind,original_binding_scope=json.dumps(original_scope,sort_keys=True) if original_scope is not None else 'No schema projection; binding uses the schema scope fields directly.'),
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
