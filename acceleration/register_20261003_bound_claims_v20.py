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



# V13 adds only two exact ROOT-verifier adapters. No existing adapter changes.
def v13_root_role(cid,expected,binding):
    exacts={
      'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85':dict(
        binding='2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189',
        statement_sha='0cd6d0c7ef9e1d7c4151babe721ace2f5883d6c56fba0a24b03d6f85ff8b6968',
        producer='/root/structural',kind='mathematical result',basis=['DERIVED','COMPUTED'],unrestricted=True,
        description='Only universal conditional target triangle-kernel size/rank bound with exact complete99-coordinate dual, graph-specific image lower counts and the independently established even36..60 kernel weights. No generic-code application, optimizer optimum or upper rank premise.',
        report='acceleration/results/20261003_independent_review/triangle_kernel_low_weight_lp_full01/summary.json',
        report_sha='1037b20164daf037c7544d316032b15b3fcdc6413ee3b8f7a7b4d10ad9e80fd6',
        dependencies=[dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS',revision=1,relation='uses_result',reason='Its independently written injectivity/character proof supplies image countsN3=231,N4=2079,N6=24486 and sharp shifted rows.'),dict(id='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67',revision=1,relation='uses_result',reason='ONLY the independently established even kernel-weight36..60 derivation in its pinned written proof is reused; its rank67 conclusion is not a premise of rank85.')]),
      'C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS':dict(
        binding='b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1',
        statement_sha='7d370116e9d8011221321d4651f9b52827bcf6bc38adf2ec587d87725fd5a9ac',
        producer='/root/native_driver',kind='exclusion',basis=['COMPUTED'],unrestricted=False,
        description='Complete labelled one-move neighborhood of one exact saved hypergraph under the stated V2 exclusive-point trade; no other starts/moves/global graph minimum/whole plateau/exhaustive target coverage.',
        report='acceleration/results/20261003_independent_review/two_line_full01/summary.json',
        report_sha='1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589',dependencies=[])}
    if cid not in exacts:return False
    exact=exacts[cid]
    need(expected==exact['binding'],'v13 exact binding identity')
    need(binding['id']==cid and type(binding['revision'])is int and type(binding['claim_revision'])is int
         and binding['revision']==binding['claim_revision']==1 and binding['status']=='VERIFIED'
         and binding['review_state']=='CLEAR' and binding['producer']==exact['producer']
         and binding['verifier']=='/root' and binding['producer']!=binding['verifier']
         and binding['method']=='independent_artifact_check' and binding['kind']==exact['kind']
         and binding['basis']==exact['basis'],'v13 exact revision status method and separate roles')
    need(binding['scope']==dict(description=exact['description'],unrestricted_target=exact['unrestricted'],target_resolution='NONE')
         and type(binding['scope']['unrestricted_target'])is bool,'v13 exact scope')
    need(hashlib.sha256(binding['statement'].encode('utf8')).hexdigest()==exact['statement_sha'],'v13 exact statement')
    need(binding['report']==exact['report']and binding['report_sha256']==exact['report_sha'],'v13 exact report reference')
    need(binding['dependencies']==exact['dependencies'],'v13 exact dependencies')
    need('verification_records'not in binding,'v13 legacy record namespace absent')
    return True


def v13_root_report(cid,report_sha,binding,report):
    hashes={
      'C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85':('2080894a078a0fa04b77e155be06e1ca67d41568e4a1a284cbf5b0da30331189','1037b20164daf037c7544d316032b15b3fcdc6413ee3b8f7a7b4d10ad9e80fd6'),
      'C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS':('b01fc9a8faa71e22187128bc2b0affc1c4e8cb74fce83a8dad2b427208b0e0f1','1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589')}
    if cid not in hashes:return
    need(v13_root_role(cid,hashes[cid][0],binding),'v13 exact report role')
    need(report_sha==hashes[cid][1],'v13 exact independent report')
    need(report['producer']==binding['producer']and report['verifier']=='/root'
         and report['method']=='independent_artifact_check'and report['target_resolution']=='NONE','v13 report roles and target scope')
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER85':
        need(report['status']=='INDEPENDENT_TRIANGLE_KERNEL_LOW_WEIGHT_COMPLETE_DUAL_V1_PASS'
             and report['complete_exact_coefficients_checked']==1287
             and report['complete_nonnegative_dual_coordinates_checked']==99
             and report['complete_exact_weight_inequalities_checked']==13
             and report['actual_strict_corruption_controls']==7
             and report['exact_size_upper']==binding['exact_size_upper']==[216950223385397837448,11529151026462413]
             and report['maximum_linear_dimension']==binding['maximum_linear_dimension']==14
             and report['conditional_incidence_rank_lower']==binding['conditional_incidence_rank_lower']==85
             and report['lower_word_counts']=={'3':231,'4':2079,'6':24486}
             and report['optimum_asserted']is binding['optimum_asserted']is False
             and binding['rank_upper_assumed']is False and binding['premise_state']=='UNKNOWN'
             and binding['target_resolution']=='NONE','v13 exact conditional rank85 scope')
        pins={
          'acceleration/theory_20261003_incidence_low_weight_lp_v1.py':'90002c96a9b192562e299bc832ac2e7a6162899b3e97418549023b40d3f32045',
          'acceleration/results/20261003_independent_review/incidence_low_weights01/summary.json':'626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd',
          'acceleration/audit_20261003_triangle_kernel_low_weight_lp_v1.md':'fd4ad293b6aeb99924c8982a00e106c2ba112a65e4d16013ee7404b58b456e7e'}
        need(binding['written_audit']=='acceleration/audit_20261003_triangle_kernel_low_weight_lp_v1.md','v13 exact written audit')
        cal='acceleration/results/20261003_independent_review/triangle_kernel_low_weight_lp_calibration01/summary.json';calsha='b14e03ae12777c593c2fce986256859e14bcd9e6eb7619b2de2e534bd05db44d'
        need(binding['pre_output_calibration']==cal and binding['pre_output_calibration_sha256']==calsha,'v13 exact rank85 calibration reference')
        pins[cal]=calsha
        for path,identity in pins.items():
            need(binding['inputs_sha256'][path]==report['inputs_sha256'][path]==identity and digest(ROOT/path)==identity,'v13 exact rank85 source proof calibration pins')
        controlled=json.loads((ROOT/cal).read_bytes())
        need(controlled['status']=='INDEPENDENT_TRIANGLE_KERNEL_LOW_WEIGHT_LP_CHECKER_V1_CALIBRATION_PASS'
             and controlled['synthetic_schema_controls_only']is True
             and controlled['full_producer_output_inspected']is False
             and controlled['synthetic_complete_coefficients']==1287 and controlled['synthetic_precise_corruptions']==7 and len(controlled['strict_corruptions'])==8,'v13 exact rank85 finite calibration')
        need(binding['recorded_validation']==dict(complete_exact_coefficients=1287,nonnegative_rational_coordinates=99,full_exact_weight_inequalities=13,actual_strict_corruption_controls=7,exact_size_and_power_of_two_comparison=True,independent_interpretation='Complete shifted character written proof and rank-nullity; graph count/weight premises separately pinned.',numerical_status_used_as_certificate=False,preoutput_strict_rook_and_model_controls=8,preoutput_synthetic_precise_corruptions=7),'v13 exact rank85 recorded controls')
    else:
        expected=dict(counts=dict(invalid_linearity=87996,invalid_selection=10395,valid_lambda_changed=140507,valid_lambda_preserving_mu_equal=2,valid_lambda_preserving_mu_up=185),unique_valid_neighbor_graphs=136536,best_mu=3480,best_proposal_ids=[68908,68912])
        need(report['status']=='INDEPENDENT_TWO_LINE_COMPLETE_FIXED_GRAPH_CENSUS_V2_PASS'
             and type(report['complete_proposals_checked'])is int and type(report['frozen_labelled_proposals'])is int
             and report['complete_proposals_checked']==report['frozen_labelled_proposals']==239085
             and report['complete_universe']is True and report['absence_of_descent_asserted']is True
             and report['aggregate']==expected
             and report['independently_checked_chosen_neighbor']==dict(proposal_id=68908,lambda_energy=0,mu_energy=3480,root_residual=52,ordered_srg_identity_mismatches=4754)
             and binding['target_resolution']is False,'v13 exact fixed census outcome')
        pins={
          'acceleration/audit_20261003_two_line_records_v2.py':'d581ea5a2d9ef082aafae5b4de578813d09dc4fd61cb64ee3beaa8b91fa41165',
          'acceleration/results/20261003_weight60_two_line_census01/manifest.json':'70f4ec893d5ba443effdd29cd6e3d472d736e590af56691b751e822bbae49ffa',
          'acceleration/results/20261003_hypergraph_weight60_warm01/native/final.state':'c15b421468af173b6c2ee11e9bcb31d5abca586fcb47a7c7ee312f527b31979b',
          'acceleration/results/20261003_hypergraph_weight60_warm01/native/best.adj':'9d5b88ba2a2eb13d39d2a5edea1c25af9a9105c143c4297fe37e84f666a37a2d'}
        cal='acceleration/results/20261003_independent_review/two_line_records_calibration01/summary.json';calsha='ab51f23bbbd09e6d0b94ce861b391bb349cd583bc62f69439e2da1afb66af3b6'
        pins[cal]=calsha
        for path,identity in pins.items():
            need(binding['inputs_sha256'][path]==report['inputs_sha256'][path]==identity and digest(ROOT/path)==identity,'v13 exact census source input calibration pins')
        controlled=json.loads((ROOT/cal).read_bytes());recorded=binding['pre_output_calibration']
        need(controlled['status']=='INDEPENDENT_TWO_LINE_RECORDS_V2_PREOUTPUT_CALIBRATION_PASS'
             and controlled['complete_unique_tiny_records']==270 and controlled['complete_records_including_split_replay']==540
             and controlled['pre_full_scientific_output']is True and len(controlled['strict_record_corruptions'])==15
             and controlled['complete_new_fullmatrix_and_scalar_comparisons']==96 and controlled['known_overlap_checked']is True
             and recorded['path']==cal and recorded['sha256']==calsha and recorded['known_fixtures']==['rook9','prism9']
             and recorded['complete_unique_records']==270 and recorded['complete_split_stream_records']==540
             and recorded['complete_fullmatrix_and_scalar_valid_comparisons']==96 and recorded['known_overlap_checked']is True
             and recorded['strict_saved_stream_and_metadata_corruptions']==controlled['strict_record_corruptions']
             and recorded['controls_preceded_full_scientific_output']is True,'v13 exact census finite calibration')
        pre=dict(report=cal,report_sha256=calsha,complete_unique_tiny_records=270,complete_records_including_split_replay=540,complete_fullmatrix_and_scalar_valid_comparisons=96,known_overlap_checked=True,strict_saved_corruptions=controlled['strict_record_corruptions'],strict_corruption_count=15,pre_full_scientific_output=True)
        full=dict(report=binding['report'],report_sha256=report_sha,complete_proposals_checked=239085,complete_universe=True,raw_parts=48,checkpoint_prefixes=48,all_ties_and_selected_raw_objects=True,complete_trajectory_checked=False,trajectory_reason='This is a static full neighbor census, not an annealer trajectory audit.')
        need(binding['controls']==dict(pre_output_independent=pre,full_independent=full),'v13 exact explicit census controls')
        previous='acceleration/results/20261003_fixed_two_line_census_binding02/claim_binding_schema2_draft.json';previous_sha='85e943e2b7431deb4cf7ef9c3b49a72d8e714d9a85ed6999273df8894377e82e'
        need(binding['inputs_sha256'][previous]==previous_sha and digest(ROOT/previous)==previous_sha,'v13 exact preserved editorial records')
        supplements=binding['supplemental_verification_records']
        need(supplements==json.loads((ROOT/previous).read_bytes())['verification_records']and len(supplements)==2,'v13 exact supplemental record preservation')
        for record,source,path,identity,kind in zip(supplements,[controlled,report],[cal,binding['report']],[calsha,report_sha],['pre_output_checker_calibration','complete_static_artifact_check']):
            need(record['claim_id']==cid and type(record['claim_revision'])is int and record['claim_revision']==1
                 and record['record_kind']==kind and record['verifier']=='/root'and record['method']=='independent_artifact_check'
                 and record['outcome']=='PASS'and record['report']==path and record['report_sha256']==identity
                 and record['timestamp']==source['timestamp']and record['artifact_hashes']==source['inputs_sha256']
                 and record['command']==source['command']and record['cwd']==source['cwd']
                 and record['versions']==dict(python=source['python'],numpy=source['numpy'])
                 and record['shared_components']==source['shared_components']and record['independent_of_discovery_producer']is True
                 and record['external_review']is False,'v13 exact revision bound supplementary records')
        unavailable=binding['unavailable_information']
        need(len(unavailable)==5 and {r['field']for r in unavailable}=={'verifier_source_commit','hardware_cpu_model','individual_human_reviewer_identity','external_peer_review_record','random_seed'}
             and all(r['value']is None and isinstance(r['reason'],str)and r['reason'].strip()for r in unavailable),'v13 explicit unavailable information')
        evidence=binding['computational_evidence']
        need(evidence['graph_points']==99 and evidence['labelled_triples']==231 and evidence['labelled_proposals']==evidence['completed_labelled_proposals']==239085
             and evidence['classifications']==expected['counts']and evidence['unique_valid_labelled_point_graphs']==136536
             and evidence['raw_gzip_parts']==evidence['checkpoint_count']==48,'v13 exact finite census evidence')


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,data):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(data,stream,indent=2);stream.write('\n')


def v14_lowword_editorial(cid, expected, binding, report_sha, report):
    """Exactly one pre-reviewed editorial pair; preserve both original statements."""
    if cid != 'C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS':
        return None
    need(expected == '40022e026a8c3a479bbdee2a86cecd0fccae6081b2ab153560ad7b36f077fe05',
         'v14 exact editorial binding')
    need(type(binding['revision']) is int and binding['revision'] == 1
         and type(binding['claim_revision']) is int and binding['claim_revision'] == 1
         and binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
         and binding['kind'] == 'mathematical result' and binding['basis'] == ['DERIVED']
         and binding['producer'] == '/root/structural' and binding['verifier'] == '/root/checkpoint_audit'
         and binding['method'] == 'independent_derivation' and binding['dependencies'] == [],
         'v14 exact ordinary revision roles kind basis method dependencies')
    need(binding['scope'] == dict(description='General universal implication for complete triangle incidence in any finite simple graph whose every edge has exactly one common neighbor; includes the unrestricted target conditional corollary and exact sharp character rows. No target existence or graph exclusion.',
                                unrestricted_target=True, target_resolution='NONE')
         and binding['scope']['unrestricted_target'] is True
         and binding['target_resolution'] == 'NONE' and binding['premise_state'] == 'UNKNOWN',
         'v14 exact conditional editorial scope')
    need(hashlib.sha256(binding['statement'].encode()).hexdigest() == 'dc6bf21cf24d90fc2111ee366ac990bbe1437cb51e8e2e2cfaffe5023294a9f4'
         and hashlib.sha256(report['statement'].encode()).hexdigest() == '2ca15439483a3c908f42f03d4ae88e153bffec5e5546906cff15a7dbb28e8a6e',
         'v14 exact two editorial statement strings')
    report_path = 'acceleration/results/20261003_independent_review/incidence_low_weights01/summary.json'
    proof_path = 'acceleration/audit_20261003_incidence_low_weights_v1_proof.md'
    proof_sha = '45e3e4fbb8f39547ea169f65ad0df456f09396442fceed23c4483fb9d2be9f4a'
    need(report_sha == binding['report_sha256'] == '626e405502f6054483d7bc722610e83788c663d50d016f34a48b248edea4c2cd'
         and binding['report'] == report_path and report['written_audit'] == binding['written_audit'] == proof_path
         and binding['inputs_sha256'].get(proof_path) == report['inputs_sha256'].get(proof_path) == proof_sha
         and digest(ROOT/proof_path) == proof_sha,
         'v14 exact independent report and written derivation')
    need(report['status'] == 'INDEPENDENT_TRIANGLE_IMAGE_LOW_WEIGHT_COUNTS_CHARACTER_V1_PASS'
         and report['producer'] == '/root/structural' and report['verifier'] == '/root/checkpoint_audit'
         and report['method'] == 'independent_derivation' and report['target_resolution'] == 'NONE'
         and report['universal_derivation_checked'] is True and report['rank_bound_claimed'] is False
         and report['prior_weight_interval_rederived'] is False and type(report['new_exclusions']) is int and report['new_exclusions'] == 0
         and binding['target_lower_word_counts'] == report['target_lower_word_counts'] == {'3':231,'4':2079,'6':24486},
         'v14 exact written theorem outcome and limitations')
    need(binding['recorded_validation'] == dict(universal_derivation_checked=True,
          meeting_support_recovery='Complete induced2K2 and unique edge completion recovers pair.',
          disjoint_support_recovery='Only two triangles within six-support recover pair.',
          positive_complete_fixtures=5,complete_pair_inverse_checks=25,complete_literal_character_checks=310,
          strict_negative_controls=10,finite_controls_are_universal_proof=False)
         and type(report['strict_negative_controls']) is int and report['strict_negative_controls'] == 10
         and len(report['positive_fixtures']) == 5
         and sum(f['pair_checks'] for f in report['positive_fixtures']) == 25
         and sum(f['literal_character_checks'] for f in report['positive_fixtures']) == 310,
         'v14 exact recorded independent finite controls')
    controls_path = 'acceleration/results/20261003_independent_review/incidence_low_weights01/controls.json'
    controls_sha = '3f67ac8a0b4dff695abbc2ab015990553c2f90387de60699322d8897b00b56f4'
    rows_path = 'acceleration/results/20261003_independent_review/incidence_low_weights01/normalized_rows.json'
    rows_sha = '3da5ba0b186af10894187afc66906c71c5f448e7180b3f7ce895aa428b85efca'
    need(binding['inputs_sha256'].get(controls_path) == controls_sha
         and binding['inputs_sha256'].get(rows_path) == rows_sha
         and digest(ROOT/controls_path) == controls_sha and digest(ROOT/rows_path) == rows_sha
         and binding['controls_references'] == [dict(path=report_path,sha256=report_sha,role='independent_derivation_and_complete_controls',positive_fixtures=5,complete_pair_inverse_checks=25,complete_literal_character_checks=310,strict_negative_controls=10),
                 dict(path=controls_path,sha256=controls_sha,role='exact independent ten-corruption records')],
         'v14 exact immutable control and sharp row artifacts')
    return dict(claim_id=cid,claim_revision=1,binding_sha256=expected,report=report_path,report_sha256=report_sha,
                written_derivation=proof_path,written_derivation_sha256=proof_sha,
                original_report_statement=report['statement'],original_report_statement_sha256='2ca15439483a3c908f42f03d4ae88e153bffec5e5546906cff15a7dbb28e8a6e',
                recorded_binding_statement=binding['statement'],recorded_binding_statement_sha256='dc6bf21cf24d90fc2111ee366ac990bbe1437cb51e8e2e2cfaffe5023294a9f4',
                reason='Exact ROOT-reviewed editorial expansion gives explicit character/zero-word/three-degree convention already proved in the pinned written audit; no semantic inference by registrar and no raw statement overwritten.',
                mathematical_replays=0)


# V15: three exact Wave40 metadata pairs; every V14 adapter stays unchanged.
V15_EXACT = json.loads(r'''{
  "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT": {
    "binding_path": "acceleration/results/20261003_triangle_image_weight5_binding01/claim_binding_schema2.json",
    "binding_sha256": "e816aff2942094e61efc2652acc222fa5de8f60b9b2435c81750a4ba19e65ea7",
    "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT",
    "statement_sha256": "b2a5ab4a3a189f05b5f0b0a5b67cee48a367b3085432db18e41cea296961d68f",
    "kind": "mathematical result",
    "basis": [
      "DERIVED"
    ],
    "method": "independent_derivation",
    "producer": "/root/structural",
    "verifier": "/root/checkpoint_audit",
    "scope": {
      "description": "Universal necessary triangle-path weight5 image lower bound under adjacent-pair common-neighbor uniqueness, with unrestricted Conway99 conditional corollary and exact all-weight character inequality. No existence, rank or exclusion conclusion.",
      "target_resolution": "NONE",
      "unrestricted_target": true
    },
    "dependencies": [],
    "report": "acceleration/results/20261003_independent_review/weight5_full02/summary.json",
    "report_sha256": "dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2",
    "controls": {
      "actual_raw": {
        "actual_k7_three_intersection_paths_checked": true,
        "complete_small_image_coefficient_masks": 234,
        "complete_three_triangle_combinations": 62,
        "every_inverse_fiber_checked": true,
        "path": "acceleration/results/20261003_independent_review/weight5_full02/summary.json",
        "positive_fixtures": 7,
        "saved_strict_negative_controls": 17,
        "separate_fixture_supports": 14,
        "sha256": "dedb5c3affcfd0edb98a1d97ebdc973290b53b67ecbb76f3d78135b2bea688f2",
        "unordered_paths": 23
      },
      "pre_full": {
        "path": "acceleration/results/20261003_independent_review/weight5_calibration01/summary.json",
        "positive_fixtures": 7,
        "producer_outputs_inspected": false,
        "sha256": "f8d31fdbdafc31314d79b3be1e17934477dcd65286f07ab5e28ace9d8423c99a",
        "strict_negative_controls": 21
      }
    },
    "pre_output_calibration": null,
    "written_audit": "acceleration/audit_20261003_triangle_image_weight5_v1_proof.md",
    "written_audit_sha256": "8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee",
    "recorded_validation": {
      "character_orthogonality_and_zero_constant_rederived": true,
      "complete_normalized_weights": 99,
      "exact_character_denominator": 71510670,
      "finite_agreement_used_as_universal_proof": false,
      "new_exclusions": 0,
      "target_unordered_paths": 24948,
      "target_weight5_lower_count": 12474,
      "universal_written_inverse": true
    },
    "target_resolution": "NONE",
    "premise_state": "UNKNOWN"
  },
  "C-HYPERGRAPH-ROOT-FOCUSED-PILOT01-SAVED-OBJECTS": {
    "binding_path": "acceleration/results/20261003_root_focused_pilot_binding01/claim_binding_schema2.json",
    "binding_sha256": "b160388913cc014a2ea1d8a407a150e657078cd9c81ad6333378eac633c4de2f",
    "id": "C-HYPERGRAPH-ROOT-FOCUSED-PILOT01-SAVED-OBJECTS",
    "statement_sha256": "910e972e2788edf2fd415400331e1d92601beae3df6fd270c341c75d9eceb3e0",
    "kind": "empirical/engineering result",
    "basis": [
      "COMPUTED"
    ],
    "method": "independent_artifact_check",
    "producer": "/root/native_driver",
    "verifier": "/root/checkpoint_audit",
    "scope": {
      "description": "One authenticated fixed-root pilot and its exact saved current/best graphs, complete saved-file population and all anchored stored proposals. No whole trajectory or target-wide conclusion.",
      "target_resolution": "NONE",
      "unrestricted_target": false
    },
    "dependencies": [],
    "report": "acceleration/results/20261003_independent_review/root_focused_saved_pilot01/summary.json",
    "report_sha256": "7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558",
    "controls": {
      "calibration": {
        "path": "acceleration/results/20261003_independent_review/root_focused_saved_calibration03/summary.json",
        "positive_controls": 5,
        "sha256": "328e3ee2d503ab4977b23f3fa9dd436109badcadfb1807543169081023c2bd8f",
        "strict_negative_controls": 25
      },
      "full": {
        "anchored_stored_proposals": 10099,
        "distinct_saved_steps": 101,
        "native_files": 106,
        "ordered_matrix_entries": 1999404,
        "path": "acceleration/results/20261003_independent_review/root_focused_saved_pilot01/summary.json",
        "scalar_graph_observations": 204,
        "sha256": "7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558",
        "state_files": 102,
        "unanchored_stored_proposals": 0
      }
    },
    "pre_output_calibration": null,
    "written_audit": null,
    "written_audit_sha256": null,
    "recorded_validation": {
      "best_root": {
        "E_lambda": 0,
        "E_mu": 5520,
        "Froot": 10,
        "Rroot": 10,
        "identity_mismatches": 5580
      },
      "best_root_graph_sha256": "339086c8a1aaf1be2b4068d83945f4de4b1fc130f8ad8698708420ccc5d98467",
      "complete_trajectory_checked": false,
      "current": {
        "E_lambda": 0,
        "E_mu": 5476,
        "Froot": 10,
        "Rroot": 10,
        "identity_mismatches": 5500
      },
      "current_graph_sha256": "3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d",
      "final_state_sha256": "f38346ba0d3367acfc585854587e30bf5748ffe5ede658cd0055f41edd0f0bb3",
      "frozen_literal_triples": 7,
      "graph_degree": 14,
      "linear_triples": 231,
      "n": 99,
      "new_exclusions": 0,
      "point_degree": 7,
      "root": 11,
      "root_nonadjacent_cn_histogram": {
        "1": 5,
        "2": 74,
        "3": 5
      },
      "saved_localzero_objects": 0,
      "zero_target_object_observations": 0
    },
    "target_resolution": "NONE",
    "premise_state": null
  },
  "C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86": {
    "binding_path": "acceleration/results/20261003_triangle_rank86_binding01/claim_binding_schema2.json",
    "binding_sha256": "5d1aa5266a8dd3aaee40e8bdb4f8c10c2093d92969c1f29bdb03587080cec831",
    "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86",
    "statement_sha256": "a6c2b23ee724623d4f8c3867cf80759f2d406f6a10ebe0bc6bac615a48170b44",
    "kind": "mathematical result",
    "basis": [
      "DERIVED",
      "COMPUTED"
    ],
    "method": "independent_artifact_check",
    "producer": "/root/structural",
    "verifier": "/root",
    "scope": {
      "description": "Unrestricted target necessary triangle-incidence kernel size/rank bound, using its even nonzero weights 36..60 and image counts N3>=231,N4>=2079,N5>=12474,N6>=24486. Exact even13 certificate; no generic binary-code application or divided-by-four weight premise.",
      "unrestricted_target": true,
      "target_resolution": "NONE"
    },
    "dependencies": [
      {
        "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67",
        "revision": 1,
        "relation": "uses_result",
        "reason": "Only its independently checked even nonzero kernel-weight interval 36..60 is reused; rank67 is not a premise."
      },
      {
        "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS",
        "revision": 1,
        "relation": "uses_result",
        "reason": "Independently established N3,N4,N6 and sharp character normalization; the selected dual has support only at degree4 and degree5, so its nontrivial image-count use is N4."
      },
      {
        "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT",
        "revision": 1,
        "relation": "uses_result",
        "reason": "Independently established target N5>=12474 and exact degree5 character row. The later candidate strengthened C4 collision count is not used."
      }
    ],
    "report": "acceleration/results/20261003_independent_review/four_counts_lp_even13_full01/summary.json",
    "report_sha256": "3cc0ae7fbd0d340c00a4b1e3b00221ef70df6767812b846875a9483413745674",
    "controls": {
      "independent_preoutput": {
        "report": "acceleration/results/20261003_independent_review/four_counts_lp_calibration01/summary.json",
        "sha256": "15a870349f39da25ff53da630ab2850076aad7fca6efebeafdae13c0f08a888e",
        "literal_character_coefficients": 140,
        "known_rook_kernel_words": 16,
        "complete_selected_synthetic_coefficient_cells_both_domains": 1980,
        "actual_strict_corruptions": 30,
        "full_producer_output_inspected": false
      },
      "independent_actual": {
        "report": "acceleration/results/20261003_independent_review/four_counts_lp_even13_full01/summary.json",
        "sha256": "3cc0ae7fbd0d340c00a4b1e3b00221ef70df6767812b846875a9483413745674",
        "actual_strict_corruptions": 10
      },
      "author": {
        "positive_exact_fixtures": 2,
        "actual_literal_character_coefficients": 139,
        "actual_strict_corruptions": 12,
        "declared_literal_character_coefficients": 140,
        "declaration_deviation": "acceleration/results/20261003_incidence_four_low_counts_plan03/calibration_count_deviation.json",
        "author_controls_are_independent_approval": false
      }
    },
    "pre_output_calibration": null,
    "written_audit": "acceleration/audit_20261003_triangle_kernel_four_counts_lp_v3.md",
    "written_audit_sha256": "17662bc4c8d63fb56bf6b64fd59bfe1509064a11c06279f9a40ba5a4869f9c54",
    "recorded_validation": null,
    "target_resolution": "NONE",
    "premise_state": "UNKNOWN",
    "exact_certificate": {
      "path": "acceleration/results/20261003_incidence_four_counts_even13_guide01/certificate.json",
      "sha256": "770d32d79e88952614ba57aac1bb877a9355f36cc6239237990326202444f05b",
      "upper": [
        97502464,
        9739
      ],
      "nonzero_dual_by_degree": {
        "4": [
          14631155,
          9739
        ],
        "5": [
          82861570,
          9739
        ]
      },
      "complete_dual_coordinates": 99,
      "complete_coefficients": 1287,
      "complete_weight_inequalities": 13,
      "artifact_checked_by": "/root",
      "optimum_asserted": false
    }
  }
}''')


def v15_same(left,right):
    """Typed equality only for exact frozen metadata; not a semantic matcher."""
    if type(left) is not type(right):return False
    if type(left) is dict:return set(left)==set(right) and all(v15_same(left[k],right[k]) for k in left)
    if type(left) is list:return len(left)==len(right) and all(v15_same(a,b) for a,b in zip(left,right))
    return left==right


def v15_role(cid,expected,binding):
    if cid not in V15_EXACT:return False
    exact=V15_EXACT[cid]
    need(expected==exact['binding_sha256'],'v15 exact frozen binding identity')
    need(type(binding['revision'])is int and type(binding['claim_revision'])is int
         and binding['revision']==binding['claim_revision']==1 and binding['id']==cid
         and binding['status']=='VERIFIED' and binding['review_state']=='CLEAR'
         and binding['producer']==exact['producer'] and binding['verifier']==exact['verifier']
         and binding['producer']!=binding['verifier'] and binding['method']==exact['method']
         and binding['kind']==exact['kind'] and v15_same(binding['basis'],exact['basis']),
         'v15 exact revision status independent roles method kind basis')
    need(v15_same(binding['scope'],exact['scope']) and v15_same(binding['dependencies'],exact['dependencies'])
         and binding['target_resolution']=='NONE' and binding.get('premise_state')==exact['premise_state'],
         'v15 exact conditional or finite scope dependencies and unresolved target')
    need('verification_records' not in binding and binding['report']==exact['report']
         and binding['report_sha256']==exact['report_sha256']
         and hashlib.sha256(binding['statement'].encode('utf8')).hexdigest()==exact['statement_sha256'],
         'v15 exact primary report statement and no legacy fallback')
    return True


def v15_report(cid,report_sha,binding,report):
    if cid not in V15_EXACT:return None
    exact=V15_EXACT[cid]
    need(report_sha==exact['report_sha256'] and report['producer']==exact['producer']
         and report['verifier']==exact['verifier'] and report['method']==exact['method']
         and report['target_resolution']=='NONE','v15 exact independent report roles and identity')
    need(v15_same(binding['controls'],exact['controls']),'v15 exact recorded control references')
    def pinned(path,identity):
        need(binding['inputs_sha256'].get(path)==identity and digest(ROOT/path)==identity,'v15 exact source proof control or raw artifact')
    for control in exact['controls'].values():
        if type(control)is dict:
            path=control.get('path',control.get('report'));identity=control.get('sha256')
            if path is not None and identity is not None:pinned(path,identity)
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT':
        need(report['status']=='INDEPENDENT_TRIANGLE_IMAGE_WEIGHT5_PATH_LOWER_COUNT_V1_PASS'
             and report['statement']==binding['statement'] and report['universal_derivation_checked']is True
             and report['rank_bound_claimed']is False and type(report['new_exclusions'])is int and report['new_exclusions']==0
             and type(report['target_unordered_paths'])is int and report['target_unordered_paths']==24948
             and type(report['target_weight5_lower_count'])is int and report['target_weight5_lower_count']==12474,
             'v15 exact N5 universal derivation and necessary count only')
        need(v15_same(binding['recorded_validation'],exact['recorded_validation'])
             and binding['written_audit']==exact['written_audit'],'v15 exact N5 recorded derivation')
        pinned(exact['written_audit'],exact['written_audit_sha256'])
        return None  # Preserve the old ordinary literal-statement path for N5.
    need('statement' not in report,'v15 absent original report statement remains absent')
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER86':
        need(report['status']=='INDEPENDENT_TRIANGLE_KERNEL_FOUR_COUNTS_COMPLETE_DUAL_V2_PASS'
             and report['weight_domain']=='even13' and report['optimum_asserted']is False
             and v15_same(report['exact_size_upper'],[97502464,9739])
             and v15_same([report['complete_exact_coefficients_checked'],report['complete_nonnegative_dual_coordinates_checked'],
                          report['complete_exact_weight_inequalities_checked'],report['maximum_linear_dimension'],
                          report['conditional_incidence_rank_lower'],report['actual_strict_corruption_controls']],[1287,99,13,13,86,10])
             and v15_same(report['lower_word_counts'],{'3':231,'4':2079,'5':12474,'6':24486}),
             'v15 exact even13 conditional rank86 full certificate')
        need(v15_same(binding['exact_certificate'],exact['exact_certificate'])
             and binding['written_audit']==exact['written_audit'] and binding['written_audit_sha256']==exact['written_audit_sha256'],
             'v15 exact conditional rank certificate and written derivation')
        pinned(exact['written_audit'],exact['written_audit_sha256']);pinned(exact['exact_certificate']['path'],exact['exact_certificate']['sha256'])
        supplements=binding['supplemental_verification_records']
        need(type(supplements)is list and len(supplements)==1 and supplements[0]['claim_id']==cid
             and type(supplements[0]['claim_revision'])is int and supplements[0]['claim_revision']==1
             and supplements[0]['verifier']=='/root' and supplements[0]['method']=='independent_artifact_check'
             and supplements[0]['outcome']=='PASS','v15 exact rank revision-bound supplemental provenance')
        reason='Exact frozen conditional theorem statement is an editorial projection of the pinned ROOT even13 certificate and written derivation. Original raw report has no statement field; no generic semantic inference, optimum or target resolution is admitted.'
    else:
        need(report['status']=='INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_PASS'
             and report['complete_trajectory_checked']is False and v15_same(
             [report['saved_state_files'],report['saved_states'],report['saved_trace_records'],report['complete_anchored_proposals'],
              report['locally_checked_global_gaps'],report['saved_selected_object_files'],report['saved_localzero_object_observations'],
              report['zero_target_candidates'],report['native_reported_proposals']],[102,101,10099,10099,0,0,0,0,10000000]),
             'v15 exact pilot saved-object and stored-proposal population')
        need(v15_same(binding['recorded_validation'],exact['recorded_validation']),'v15 exact saved current best object statement fields')
        native='acceleration/results/20261003_hypergraph_root_focused_pilot01/native/'
        raw=[name for name in report['inputs_sha256']if name.startswith(native)]
        need(len(raw)==106 and sum(name.endswith('.state')for name in raw)==102,'v15 exact saved native file population')
        for name,identity in [('current.adj','3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d'),
                              ('best_root.adj','339086c8a1aaf1be2b4068d83945f4de4b1fc130f8ad8698708420ccc5d98467'),
                              ('final.state','f38346ba0d3367acfc585854587e30bf5748ffe5ede658cd0055f41edd0f0bb3')]:
            need(report['inputs_sha256'].get(native+name)==identity,'v15 exact independently bound current best state identities');pinned(native+name,identity)
        objects='acceleration/results/20261003_independent_review/root_focused_saved_pilot01/object_audits.json'
        pinned(objects,'7076894b5c64ef2b5f26f5ec038c32dfbf49159644a263a9273f0e44b701082b')
        audits=json.loads((ROOT/objects).read_bytes())
        final=[row for row in audits if row['path']==native+'final.state']
        need(len(audits)==102 and len(final)==1 and final[0]['step']==10000000
             and sum(len(row['full_scalar_objects'])for row in audits)==204
             and sum(obj['ordered_entries_checked']for row in audits for obj in row['full_scalar_objects'].values())==1999404,
             'v15 complete independently checked scalar object population')
        for name,mu,mismatches in [('current',5476,5500),('best_root',5520,5580)]:
            obj=final[0]['full_scalar_objects'][name]
            need(v15_same([obj['root_energy'],obj['lambda_energy'],obj['mu_energy'],obj['root_residual'],obj['identity_mismatches']],[10,0,mu,10,mismatches])
                 and obj['srg_valid']is False and v15_same(obj['root_nonadjacent_cn_histogram'],{'1':5,'2':74,'3':5}),
                 'v15 exact final scalar scores histogram and target veto')
        reason='Exact frozen saved-object statement projects the pinned checkpoint full artifact report and object_audits; raw summary has no statement field. Native proposal counter is authenticated metadata, not a complete-trajectory verification. Adapter author also authored the native engine; this performs bookkeeping only and requires independent registrar engineering review.'
    return dict(claim_id=cid,original_report=exact['report'],original_report_sha256=report_sha,
                original_report_statement=None,original_report_statement_null_reason='Pinned original report has no statement field; its independently checked literal results remain unchanged.',
                recorded_binding=exact['binding_path'],recorded_binding_sha256=exact['binding_sha256'],
                recorded_binding_statement=binding['statement'],recorded_binding_statement_sha256=exact['statement_sha256'],
                reason=reason,mathematical_replays=0,target_resolution='NONE')


# V16 admits only two frozen ROOT-verifier results. It does not derive mathematics,
# overwrite raw headlines, waive literal equality for unrelated IDs, or add any
# fixed-graph/GF3/profile binding. V15 and earlier adapters remain unchanged.
V16_EXACT = json.loads(r'''{
  "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT": {
    "binding_path": "acceleration/results/20261003_weight5_c4_binding01/claim_binding_schema2.json",
    "binding_sha256": "6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee",
    "statement": "For every finite simple graph with exactly one common neighbor for each adjacent pair, the binary triangle-incidence image contains at least max(ceil(P/2), P-c4(G)) weight-five words, where P is the unordered three-triangle path count and c4(G) the induced four-cycle count. Consequently any srg(99,14,1,2) has N5>=22869 and its exact degree-five kernel-character shifted right-hand side is71500275.",
    "statement_sha256": "2e863864026ccab1d9307c44ecc1653c27c2011815f34c85c33ef2f6150c623a",
    "binding_metadata": {
      "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT",
      "revision": 1,
      "claim_revision": 1,
      "status": "VERIFIED",
      "review_state": "CLEAR",
      "producer": "/root/structural",
      "verifier": "/root",
      "method": "independent_derivation",
      "kind": "mathematical result",
      "basis": [
        "DERIVED"
      ],
      "scope": {
        "description": "Universal finite simple graph triangle-path double-fiber injection into induced four-cycles under exactly one common neighbor per adjacent pair, with conditional unrestricted target N5>=22869 and exact shifted degree5 character row. No existence, rank or exclusion conclusion.",
        "unrestricted_target": true,
        "target_resolution": "NONE"
      },
      "assumptions": [
        "Finite simple graph with exactly one common neighbor for each adjacent pair; incidence contains every actual triangle once.",
        "Target corollary additionally assumes the exact integer99vertex target identity; its existence remains UNKNOWN.",
        "No automorphism, prism absence, rook absence, nonzero-kernel existence or upper-rank assumption."
      ],
      "dependencies": [
        {
          "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-PATH-IMAGE-LOWER-COUNT",
          "revision": 1,
          "relation": "uses_result",
          "reason": "Only its pinned independently checked triangle-path inverse lemma (unique isolated support point, perfect-matching inverse, fiber multiplicity at most2) from written proof8844 is reused. The previous target lower12474 is not treated as the strengthened count."
        }
      ],
      "target_resolution": "NONE",
      "premise_state": "UNKNOWN",
      "controls": {
        "independent_preoutput": {
          "path": "acceleration/results/20261003_independent_review/weight5_c4_raw_calibration03/summary.json",
          "sha256": "e4ba5e7dbe927ce2b3c60b80600bb8436d9e6b47de2a87af784e9157853c27bf",
          "original_fixtures": 7,
          "complete_three_triangle_combinations": 62,
          "complete_image_masks": 234,
          "literal_character_coefficients": 100,
          "normalized_character_weights": 99,
          "precise_interface_corruptions": 27,
          "producer_outputs_checked": false
        },
        "independent_actual": {
          "path": "acceleration/results/20261003_independent_review/weight5_c4_raw_full02/summary.json",
          "sha256": "75bf5f7adc8b082311b4ad786d46f53857960ea07c8cb58576c3a38d2bbce5a5",
          "original_fixtures": 7,
          "complete_three_triangle_combinations": 62,
          "unordered_paths": 23,
          "separate_fixture_supports": 14,
          "induced_c4s": 10,
          "double_fibers": 9,
          "complete_image_masks": 234,
          "positive_relabelled_fixtures": 1,
          "paired_relabel_map_checked": true,
          "precise_interface_corruptions": 27,
          "actual_saved_precise_corruptions": 18,
          "universal_statement_from_written_derivation": true,
          "finite_controls_are_universal_proof": false
        }
      },
      "written_audit": "acceleration/audit_20261003_triangle_image_weight5_c4_v1.md",
      "written_audit_sha256": "bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12",
      "exact_certificate": null,
      "original_independent_report_method": "independent_derivation_and_complete_artifact_checking",
      "original_independent_report_statement_field": "universal_statement"
    },
    "report": "acceleration/results/20261003_independent_review/weight5_c4_raw_full02/summary.json",
    "report_sha256": "75bf5f7adc8b082311b4ad786d46f53857960ea07c8cb58576c3a38d2bbce5a5",
    "statement_field": "universal_statement",
    "report_fields": {
      "status": "INDEPENDENT_WEIGHT5_C4_COLLISION_COMPLETE_RAW_V1_PASS",
      "producer": "/root/structural",
      "verifier": "/root",
      "method": "independent_derivation_and_complete_artifact_checking",
      "claim_revision": 1,
      "checker_implementation_version": 3,
      "target_resolution": "NONE",
      "producer_outputs_checked": true,
      "numerical_solver_invocations": 0,
      "graph_exclusions": 0,
      "actual_saved_strict_corruptions": 18,
      "complete_character_coefficients": 100,
      "complete_double_fibers": 9,
      "complete_induced_c4s": 10,
      "complete_normalized_weights": 99,
      "complete_original_fixtures": 7,
      "complete_small_image_coefficient_masks": 234,
      "complete_three_triangle_combinations": 62,
      "paired_relabel_map_checked": true,
      "positive_relabelled_fixtures": 1,
      "rank_asserted": false,
      "separate_fixture_supports": 14,
      "strict_interface_corruptions": 27,
      "target_character_rhs": 71500275,
      "target_induced_c4_count": 2079,
      "target_unordered_paths": 24948,
      "target_weight5_lower_count": 22869,
      "universal_derivation_checked": true,
      "unordered_paths": 23,
      "written_audit": "acceleration/audit_20261003_triangle_image_weight5_c4_v1.md",
      "written_audit_sha256": "bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12"
    },
    "calibration_path": "acceleration/results/20261003_independent_review/weight5_c4_raw_calibration03/summary.json",
    "calibration_sha256": "e4ba5e7dbe927ce2b3c60b80600bb8436d9e6b47de2a87af784e9157853c27bf",
    "calibration_fields": {
      "status": "INDEPENDENT_WEIGHT5_C4_RAW_V1_CALIBRATION_PASS",
      "producer": "/root/structural",
      "verifier": "/root",
      "method": "independent_derivation_and_complete_artifact_checking",
      "checker_implementation_version": 3,
      "producer_outputs_checked": false,
      "complete_original_fixtures": 7,
      "complete_three_triangle_combinations": 62,
      "complete_small_image_coefficient_masks": 234,
      "complete_character_coefficients": 100,
      "complete_normalized_weights": 99,
      "strict_interface_corruptions": 27,
      "universal_derivation_checked": true,
      "target_resolution": "NONE"
    },
    "explicit_pins": {
      "acceleration/audit_20261003_triangle_image_weight5_c4_v1.md": "bdc99b2f6a2bf92f9e322616227c4be26db7d57b08ccbcfd9353fbf76260ce12",
      "acceleration/results/20261003_independent_review/weight5_c4_raw_calibration03/summary.json": "e4ba5e7dbe927ce2b3c60b80600bb8436d9e6b47de2a87af784e9157853c27bf",
      "acceleration/audit_20261003_triangle_image_weight5_c4_v1_proof.md": "7099b2780b3fe1b8abdbbdb9bff30b2993df6599cb39b3959655eb673ac4a90a",
      "acceleration/audit_20261003_triangle_image_weight5_v1_proof.md": "8844b6f2d6456ea8e8f642fcac172a93143fad7d61600f1ac24567b7b1ea76ee"
    }
  },
  "C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87": {
    "binding_path": "acceleration/results/20261003_triangle_rank87_binding01/claim_binding_schema2.json",
    "binding_sha256": "dc079188f50e43ac31c9b9707e94a5f6db1fe9644c9b3dbccca4c9e02591a39d",
    "statement": "For every srg(99,14,1,2), its complete 99-by231 triangle-incidence matrix B has binary rank at least87: its binary kernel has size at most12187808/2723<8192, hence dimension at most12. This conditional implication allows the zero kernel and uses the even36..60 nonzero-weight interval and image counts N3>=231,N4>=2079,N5>=22869,N6>=24486.",
    "statement_sha256": "46ddebe1ae4cb1e0da955069811a8927f57080d55590922489b37037671a0f17",
    "binding_metadata": {
      "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87",
      "revision": 1,
      "claim_revision": 1,
      "status": "VERIFIED",
      "review_state": "CLEAR",
      "producer": "/root/structural",
      "verifier": "/root",
      "method": "independent_derivation",
      "kind": "mathematical result",
      "basis": [
        "DERIVED",
        "COMPUTED"
      ],
      "scope": {
        "description": "Unrestricted target conditional necessary triangle-incidence kernel bound|C|<=12187808/2723, dimension<=12 and binary rank>=87; complete exact even13 degree4/5 endpoint certificate using strengthened N5>=22869. No generic-code or divisible-four premise.",
        "unrestricted_target": true,
        "target_resolution": "NONE"
      },
      "assumptions": [
        "A is the complete99vertex symmetric binary zero-diagonal adjacency satisfying A^2=12I-A+2J over integers; B contains every actual triangle once. Target existence UNKNOWN.",
        "C=ker_GF(2)(B^T), nonzero weights even36..60, exact image lower counts and character inequalities as separately independently established.",
        "No forced nonzero kernel, minimum kernel dimension, upper rank, automorphism, prism/rook absence, fixed rooted profile, numerical optimum or external acceptance."
      ],
      "dependencies": [
        {
          "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER67",
          "revision": 1,
          "relation": "uses_result",
          "reason": "Only the independently checked even nonzero kernel-weight interval36..60 is used, not rank67."
        },
        {
          "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-LOW-WEIGHT-IMAGE-COUNTS",
          "revision": 1,
          "relation": "uses_result",
          "reason": "Independently established N3/N4/N6 and character normalization; the selected dual has nonzero support only degrees4/5, so N4 is its essential prior lowcount."
        },
        {
          "id": "C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT",
          "revision": 1,
          "relation": "uses_result",
          "reason": "Exact independently checked C4 collision subtraction gives N5>=22869 and degree5 shifted row71500275. Its raw audit75bf/binding6525 are pinned; dependency must be registered before this claim."
        }
      ],
      "target_resolution": "NONE",
      "premise_state": "UNKNOWN",
      "controls": {
        "independent_preoutput": {
          "path": "acceleration/results/20261003_independent_review/c4_endpoint_calibration01/summary.json",
          "sha256": "2a4b999a53075560dc4d38f0af4fd7d10b3aaa63086b5a2e6e56fc9ba709d9a8",
          "complete_literal_characters": 140,
          "strict_corruptions": 34,
          "producer_outputs_checked": false,
          "positive_fixtures": "Complete sharp rook U16 and synthetic1287cell/99coordinate/13inequality model; no target endpoint inspected."
        },
        "independent_actual": {
          "path": "acceleration/results/20261003_independent_review/c4_endpoint_full01/summary.json",
          "sha256": "663c7fffc558e6a45232c08f272230970ff31bcc2d542e3f5c826aaa53dccbc9",
          "complete_coefficients": 1287,
          "complete_dual_coordinates": 99,
          "complete_weight_inequalities": 13,
          "strict_corruptions": 34
        },
        "author": {
          "actual_positive_fixtures": 2,
          "actual_literal_characters": 140,
          "actual_precise_negatives": 13,
          "independent_approval": false,
          "preserved_wrong_rook_dual_and_singular_system": true
        }
      },
      "written_audit": "acceleration/audit_20261003_triangle_kernel_c4_endpoint_v1.md",
      "written_audit_sha256": "d464ee1b3522a0e61784031b2f47efcc4ecf84926dcc64e306f6f2855e384ea0",
      "exact_certificate": {
        "path": "acceleration/results/20261003_triangle_kernel_c4_endpoint01/certificate.json",
        "sha256": "fcff92d4b47c53838f1e9532f6953bed120fef0eb40610cc258555deeafd609f",
        "upper": [
          12187808,
          2723
        ],
        "nonzero_degrees": [
          4,
          5
        ],
        "complete_dual_coordinates": 99,
        "complete_coefficients": 1287,
        "complete_inequalities": 13,
        "endpoint_system": {
          "degrees": [
            4,
            5
          ],
          "endpoint_weights": [
            36,
            60
          ],
          "unnormalized_matrix_pairs": [
            [
              [
                -3465,
                1
              ],
              [
                30429,
                1
              ]
            ],
            [
              [
                3543,
                1
              ],
              [
                6909,
                1
              ]
            ]
          ],
          "determinant": [
            -131749632,
            1
          ],
          "unnormalized_dual_pairs": [
            [
              5,
              28008
            ],
            [
              73,
              1372392
            ]
          ]
        },
        "optimum_asserted": false
      },
      "original_independent_report_method": "independent_derivation_and_complete_artifact_checking",
      "original_independent_report_statement_field": null
    },
    "report": "acceleration/results/20261003_independent_review/c4_endpoint_full01/summary.json",
    "report_sha256": "663c7fffc558e6a45232c08f272230970ff31bcc2d542e3f5c826aaa53dccbc9",
    "statement_field": "statement",
    "report_fields": {
      "status": "INDEPENDENT_TRIANGLE_KERNEL_C4_ENDPOINT_COMPLETE_DUAL_V1_PASS",
      "producer": "/root/structural",
      "verifier": "/root",
      "method": "independent_derivation_and_complete_artifact_checking",
      "claim_revision": 1,
      "checker_implementation_version": 3,
      "target_resolution": "NONE",
      "producer_outputs_checked": true,
      "numerical_solver_invocations": 0,
      "graph_exclusions": 0,
      "complete_exact_coefficients_checked": 1287,
      "complete_nonnegative_dual_coordinates_checked": 99,
      "complete_exact_weight_inequalities_checked": 13,
      "exact_size_upper": [
        12187808,
        2723
      ],
      "maximum_linear_dimension": 12,
      "conditional_incidence_rank_lower": 87,
      "exact_lhs_pairs": [
        [
          1,
          1
        ],
        [
          144523,
          57183
        ],
        [
          150527,
          57183
        ],
        [
          5847,
          2723
        ],
        [
          91487,
          57183
        ],
        [
          31079,
          24507
        ],
        [
          70591,
          57183
        ],
        [
          11765,
          8169
        ],
        [
          298525,
          171549
        ],
        [
          37305,
          19061
        ],
        [
          15817,
          8169
        ],
        [
          91459,
          57183
        ],
        [
          1,
          1
        ]
      ],
      "exact_endpoint_system": {
        "degrees": [
          4,
          5
        ],
        "endpoint_weights": [
          36,
          60
        ],
        "unnormalized_matrix_pairs": [
          [
            [
              -3465,
              1
            ],
            [
              30429,
              1
            ]
          ],
          [
            [
              3543,
              1
            ],
            [
              6909,
              1
            ]
          ]
        ],
        "determinant": [
          -131749632,
          1
        ],
        "unnormalized_dual_pairs": [
          [
            5,
            28008
          ],
          [
            73,
            1372392
          ]
        ]
      },
      "strict_corruptions": 34,
      "complete_literal_characters": 140,
      "lower_word_counts": {
        "3": 231,
        "4": 2079,
        "5": 22869,
        "6": 24486
      },
      "weight_domain": "even13",
      "universal_conditional_derivation_checked": true,
      "optimum_asserted": false,
      "rank_upper_asserted": false,
      "nonzero_kernel_asserted": false
    },
    "calibration_path": "acceleration/results/20261003_independent_review/c4_endpoint_calibration01/summary.json",
    "calibration_sha256": "2a4b999a53075560dc4d38f0af4fd7d10b3aaa63086b5a2e6e56fc9ba709d9a8",
    "calibration_fields": {
      "status": "INDEPENDENT_TRIANGLE_KERNEL_C4_ENDPOINT_CHECKER_V1_CALIBRATION_PASS",
      "producer": "/root/structural",
      "verifier": "/root",
      "method": "independent_derivation_and_complete_artifact_checking",
      "checker_implementation_version": 3,
      "producer_outputs_checked": false,
      "complete_literal_characters": 140,
      "strict_corruptions": 34,
      "target_resolution": "NONE"
    },
    "explicit_pins": {
      "acceleration/audit_20261003_triangle_kernel_c4_endpoint_v1.md": "d464ee1b3522a0e61784031b2f47efcc4ecf84926dcc64e306f6f2855e384ea0",
      "acceleration/results/20261003_independent_review/c4_endpoint_calibration01/summary.json": "2a4b999a53075560dc4d38f0af4fd7d10b3aaa63086b5a2e6e56fc9ba709d9a8",
      "acceleration/results/20261003_triangle_kernel_c4_endpoint01/certificate.json": "fcff92d4b47c53838f1e9532f6953bed120fef0eb40610cc258555deeafd609f",
      "acceleration/results/20261003_weight5_c4_binding01/claim_binding_schema2.json": "6525dae3734dc6c2f7eabcbd12db994f8c283019176388bb0f540690859225ee"
    }
  }
}''')


def v16_role(cid, expected, binding):
    if cid not in V16_EXACT:return False
    exact=V16_EXACT[cid]
    need(expected==exact['binding_sha256'],'v16 exact frozen binding identity')
    keys=['id','revision','claim_revision','status','review_state','producer','verifier','method','kind','basis']
    need(all(key in binding and v15_same(binding[key],exact['binding_metadata'][key]) for key in keys),
         'v16 exact typed revision status roles method kind basis')
    keys=['scope','assumptions','dependencies','target_resolution','premise_state']
    need(all(key in binding and v15_same(binding[key],exact['binding_metadata'][key]) for key in keys),
         'v16 exact scope assumptions dependencies and unresolved premise')
    need('verification_records' not in binding and binding['statement']==exact['statement']
         and binding['report']==exact['report'] and binding['report_sha256']==exact['report_sha256'],
         'v16 exact literal statement primary report and no legacy fallback')
    keys=['controls','written_audit','written_audit_sha256','exact_certificate',
          'original_independent_report_method','original_independent_report_statement_field']
    need(all(v15_same(binding.get(key),exact['binding_metadata'][key]) for key in keys),
         'v16 exact proof controls certificate and original method metadata')
    need(digest(ROOT/exact['binding_path'])==exact['binding_sha256'],
         'v16 original immutable binding bytes')
    original=json.loads((ROOT/exact['binding_path']).read_bytes())
    need(v15_same(binding,original),'v16 complete literal binding metadata')
    return True


def v16_dependency_order(cid, existing_ids):
    if cid=='C-UNRESTRICTED-TRIANGLE-INCIDENCE-BINARY-RANK-LOWER87':
        need('C-UNRESTRICTED-TRIANGLE-INCIDENCE-WEIGHT5-C4-COLLISION-SUBTRACTION-LOWER-COUNT'
             in existing_ids,'v16 C4 dependency must precede rank87')


def v16_report(cid, report_sha, binding, report):
    if cid not in V16_EXACT:return None
    exact=V16_EXACT[cid]
    need(v16_role(cid,exact['binding_sha256'],binding),'v16 exact bound report routing')
    need(report_sha==exact['report_sha256'],'v16 exact primary report identity')
    keys=['status','producer','verifier','method','claim_revision','checker_implementation_version',
          'target_resolution','producer_outputs_checked']
    need(all(key in report and v15_same(report[key],exact['report_fields'][key]) for key in keys),
         'v16 exact typed independent report identity and method')
    field=exact['statement_field']
    need(report.get(field)==binding['statement']
         and (field=='statement' or 'statement' not in report),
         'v16 exact existing raw headline field')
    need(all(key in report and v15_same(report[key],value)
             for key,value in exact['report_fields'].items()),
         'v16 exact checked results and nonresolution limitations')
    for name,identity in exact['explicit_pins'].items():
        need(binding['inputs_sha256'].get(name)==identity and digest(ROOT/name)==identity,
             'v16 exact proof calibration certificate or prior binding pin')
    calibration=json.loads((ROOT/exact['calibration_path']).read_bytes())
    need(all(key in calibration and v15_same(calibration[key],value)
             for key,value in exact['calibration_fields'].items()),
         'v16 exact preoutput calibration scope')
    need(digest(ROOT/exact['report'])==exact['report_sha256'],
         'v16 original immutable report bytes')
    original=json.loads((ROOT/exact['report']).read_bytes())
    need(v15_same(report,original),'v16 complete literal report metadata')
    return dict(claim_id=cid,claim_revision=1,
        original_report=exact['report'],original_report_sha256=report_sha,
        original_report_statement_field=field,original_report_statement=report[field],
        recorded_binding=exact['binding_path'],recorded_binding_sha256=exact['binding_sha256'],
        recorded_binding_statement=binding['statement'],
        recorded_binding_statement_sha256=exact['statement_sha256'],
        original_independent_report_method=report['method'],schema_method=binding['method'],
        original_written_audit=binding['written_audit'],original_written_audit_sha256=binding['written_audit_sha256'],
        original_calibration=exact['calibration_path'],original_calibration_sha256=exact['calibration_sha256'],
        reason='Exact two-ID metadata projection preserves the existing literal raw headline and combined independent derivation/artifact method. The schema records independent_derivation and retains the original method here. Universal mathematics and exact certificates were already checked by ROOT; this registrar does not replay them or infer any wider result.',
        raw_statement_changed=False,mathematical_replays=0,target_resolution='NONE')


# V17 admits only three exact ROOT-verifier metadata records. V16 is preserved.
V17_DESCRIPTOR = dict(
    path='acceleration/proposal_20261003_registrar_v17_exact_diagnostics_v1.json',
    sha256='0a0717a7266398532606d99370edde6f82fd552b7ab32178d840754ee532b780')
V17_EXACT = json.loads(r'''{
  "C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98": {
    "descriptor_index": 0,
    "binding_path": "acceleration/results/20261003_fixed_graph_diagnostics_bindings_v2_01/rank98/claim_binding_schema2.json",
    "binding_sha256": "256b6b664f1228c0339ef445a473b6038ff9bb489ab33e48bc7763e214049207"
  },
  "C-FIXED-ROOTFOCUSED-SELECTED45369-COMPLETE99-ROOT-RESIDUALS": {
    "descriptor_index": 1,
    "binding_path": "acceleration/results/20261003_fixed_graph_diagnostics_bindings_v2_01/all99roots/claim_binding_schema2.json",
    "binding_sha256": "cd9fce2c51677551608e71668aecc97b1377faf0c851978e52431f0cf8ac7f6c"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-RESIDUE-ENERGY-BOUNDS": {
    "descriptor_index": 2,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_residue_energy_bounds01/claim_binding_schema2.json",
    "binding_sha256": "528cbe189342b9afb4791494b66b3b2158214bff3f421b87a83f5f703a5a93ac"
  }
}''')


def v17_descriptor(cid):
    need(cid in V17_EXACT, 'v17 exact descriptor ID')
    need(digest(ROOT/V17_DESCRIPTOR['path']) == V17_DESCRIPTOR['sha256'],
         'v17 immutable reviewed descriptor bytes')
    declared = json.loads((ROOT/V17_DESCRIPTOR['path']).read_bytes())
    need(declared['schema'] == 'PROSPECTIVE_EXACT_REGISTRAR_ADAPTER_DESCRIPTORS_V1'
         and [record['id'] for record in declared['adapters']] == list(V17_EXACT),
         'v17 exact three descriptor records')
    exact = V17_EXACT[cid]
    record = declared['adapters'][exact['descriptor_index']]
    need(record['id'] == cid and record['binding'] == dict(path=exact['binding_path'], sha256=exact['binding_sha256']),
         'v17 exact descriptor binding routing')
    return record


def v17_role(cid, expected, binding):
    if cid not in V17_EXACT: return False
    exact = V17_EXACT[cid]
    need(expected == exact['binding_sha256'], 'v17 exact frozen binding identity')
    record = v17_descriptor(cid)
    keys = ['id', 'revision', 'status', 'review_state', 'producer', 'verifier', 'method', 'kind', 'basis']
    need(all(key in binding and v15_same(binding[key], record[key]) for key in keys)
         and type(binding.get('claim_revision')) is int and binding['claim_revision'] == 1,
         'v17 exact typed revision status roles method kind basis')
    need(all(key in binding and v15_same(binding[key], record[key]) for key in ['scope', 'dependencies'])
         and binding.get('target_resolution') == 'NONE',
         'v17 exact three-key scope empty dependencies and nonresolution')
    need('verification_records' not in binding and binding.get('statement') == record['statement']
         and binding.get('report') == record['primary_report']['path']
         and binding.get('report_sha256') == record['primary_report']['sha256'],
         'v17 exact literal statement primary report and no legacy fallback')
    need(digest(ROOT/exact['binding_path']) == exact['binding_sha256'],
         'v17 original immutable binding bytes')
    original = json.loads((ROOT/exact['binding_path']).read_bytes())
    need(v15_same(binding, original), 'v17 complete literal binding metadata')
    return True


def v17_fixed_evidence(cid, record, binding, report):
    descriptor = json.loads((ROOT/V17_DESCRIPTOR['path']).read_bytes())
    review = descriptor['diagnostic_writer_and_identity_review']
    pins = [record['raw_graph'], record['complete_checking_closure'], record['prior_output_identity_provenance'],
            review['writer'], review['writer_spec'], review['written_identity_review']]
    outputs = record.get('literal_checked_outputs', [record.get('literal_checked_output')])
    need(all(type(row) is dict for row in outputs), 'v17 literal checked output descriptors')
    pins += outputs
    for row in pins:
        name, identity = row['path'], row['sha256']
        need(binding['inputs_sha256'].get(name) == identity and digest(ROOT/name) == identity,
             'v17 exact diagnostic graph output closure provenance writer review pins')
        if 'bytes' in row:
            need(type(row['bytes']) is int and (ROOT/name).stat().st_size == row['bytes'],
                 'v17 exact prior output bytes')
    closure = json.loads((ROOT/record['complete_checking_closure']['path']).read_bytes())
    need(len(closure['inputs_sha256']) == record['complete_checking_closure']['immutable_members']
         and v15_same(closure['inputs_sha256'], report['inputs_sha256'])
         and closure['direct_report'] == record['primary_report']['path']
         and closure['direct_report_sha256'] == record['primary_report']['sha256'],
         'v17 complete original diagnostic input closure')
    for name, identity in closure['inputs_sha256'].items():
        need(digest(ROOT/name) == identity, 'v17 current immutable diagnostic closure member')
    provenance = json.loads((ROOT/record['prior_output_identity_provenance']['path']).read_bytes())
    output_map = {row['path']: row['sha256'] for row in outputs}
    need(provenance['schema'] == 'LITERAL_PRIOR_CHECKER_OUTPUT_IDENTITY_V1'
         and provenance['claim_id'] == cid and type(provenance['claim_revision']) is int
         and provenance['claim_revision'] == 1 and provenance['prior_report'] == record['primary_report']['path']
         and provenance['prior_report_sha256'] == record['primary_report']['sha256']
         and provenance['original_summary_self_output_hashes_present'] is False
         and provenance['raw_output_identity_in_prior_report'] is None
         and type(provenance['raw_output_identity_in_prior_report_null_reason']) is str
         and v15_same(provenance['outputs_sha256'], output_map)
         and provenance['metadata_only'] is True and type(provenance['mathematical_replays']) is int
         and provenance['mathematical_replays'] == 0,
         'v17 no retrospective original self-output identity')
    written_review = json.loads((ROOT/review['written_identity_review']['path']).read_bytes())
    need(written_review['schema'] == review['identity_review_schema']
         and written_review['status'] == review['identity_review_status']
         and written_review['reviewer'] == review['identity_review_reviewer']
         and written_review['method'] == review['identity_review_method']
         and type(written_review['mathematical_replays']) is int and written_review['mathematical_replays'] == 0
         and written_review['target_resolution'] == 'NONE'
         and written_review['scope'] == review['identity_review_scope']
         and written_review['writer_inputs_sha256'] == {review['writer']['path']:review['writer']['sha256'],
                                                       review['writer_spec']['path']:review['writer_spec']['sha256']},
         'v17 exact separate ROOT output identity review')
    expected_records = []
    for item in descriptor['adapters'][:2]:
        items = item.get('literal_checked_outputs', [item.get('literal_checked_output')])
        expected_records.append(dict(report_sha256=item['primary_report']['sha256'],
            outputs_sha256={row['path']:row['sha256'] for row in items}, id=item['id'],
            report=item['primary_report']['path'], raw_graph_sha256=item['raw_graph']['sha256'],
            raw_graph=item['raw_graph']['path'], revision=1))
    need(v15_same(written_review['records'], expected_records), 'v17 exact two prior output review records')
    if record['id'] == 'C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98':
        calibration = record['independent_calibration']
        need(binding['inputs_sha256'].get(calibration['path']) == calibration['sha256']
             and digest(ROOT/calibration['path']) == calibration['sha256'], 'v17 exact rank pre-output calibration')
        cal = json.loads((ROOT/calibration['path']).read_bytes())
        need(cal['status'] == calibration['status'] and cal['producer_outputs_checked'] is False
             and type(cal['hand_certificate_positives']) is int and cal['hand_certificate_positives'] == 5
             and type(cal['precise_certificate_negatives']) is int and cal['precise_certificate_negatives'] == 15
             and type(cal['precise_graph_negatives']) is int and cal['precise_graph_negatives'] == 4
             and type(cal['precise_binding_negatives']) is int and cal['precise_binding_negatives'] == 2
             and len(cal['controls']) == 21,
             'v17 recorded finite rank calibration population')
    else:
        need(v15_same(report['controls'], binding['controls']) and report['controls']['producer_artifact_read_before_controls'] is False,
             'v17 literal all-root precise controls')
    return dict(original_output_identity_provenance=record['prior_output_identity_provenance'],
                later_literal_checked_outputs=outputs, separate_ROOT_written_identity_review=review['written_identity_review'],
                original_checking_closure=record['complete_checking_closure'])


def v17_report(cid, report_sha, binding, report):
    if cid not in V17_EXACT: return None
    exact = V17_EXACT[cid]
    need(v17_role(cid, exact['binding_sha256'], binding), 'v17 exact bound report routing')
    record = v17_descriptor(cid)
    need(report_sha == record['primary_report']['sha256'], 'v17 exact primary report identity')
    wanted = dict(status=record['primary_report_status'], producer=record['producer'], verifier=record['verifier'],
                  method=record['method'], target_resolution='NONE')
    need(all(key in report and v15_same(report[key], value) for key, value in wanted.items()),
         'v17 exact typed independent report status roles and method')
    if record['scope']['unrestricted_target'] is False:
        need(all(key not in report for key in record['primary_report_required_absent_keys'])
             and report.get('mathematical_scope') == record['primary_report_mathematical_scope'],
             'v17 exact absent diagnostic headlines and finite scope')
        fields = record['required_literal_results']
        if cid == 'C-FIXED-LAMBDA1-REGULAR14-TRIANGLE-INCIDENCE-GF3-RANK98':
            fields = {key: fields[key] for key in ('rank', 'kernel_dimension', 'constant_only_kernel',
                      'transform_entries_checked', 'both_row_inverse_entries_checked', 'both_minor_inverse_entries_checked', 'target_exclusions')}
        need(all(key in report and v15_same(report[key], value) for key, value in fields.items()),
             'v17 exact finite diagnostic results')
        evidence = v17_fixed_evidence(cid, record, binding, report)
    else:
        need(report.get('schema') == record['primary_report_schema'] and report.get('claim_id') == cid
             and type(report.get('claim_revision')) is int and report['claim_revision'] == 1,
             'v17 exact written energy schema and revision')
        need(report.get('statement') == binding['statement'] and v15_same(report.get('scope'), binding['scope'])
             and v15_same(report.get('assumptions'), binding['assumptions']) and report.get('dependencies') == [],
             'v17 exact written statement scope and assumptions')
        need(all(key in report and v15_same(report[key], value) for key, value in record['required_literal_results'].items())
             and all(key in report and report[key] is None for key in record['required_explicit_nulls'])
             and report['outcome'] == 'PASS', 'v17 exact written checks and explicit nonexecuted nulls')
        for row in (record['candidate_source'], record['written_audit']):
            need(binding['inputs_sha256'].get(row['path']) == row['sha256'] and digest(ROOT/row['path']) == row['sha256'],
                 'v17 exact written source and independent proof pins')
    need(digest(ROOT/record['primary_report']['path']) == record['primary_report']['sha256'],
         'v17 original immutable report bytes')
    original = json.loads((ROOT/record['primary_report']['path']).read_bytes())
    need(v15_same(report, original), 'v17 complete literal report metadata')
    if record['scope']['unrestricted_target'] is True: return None
    return dict(claim_id=cid, claim_revision=1,
        original_report=record['primary_report']['path'], original_report_sha256=report_sha,
        original_report_statement_field=None, original_report_statement=None,
        original_report_statement_null_reason=record['projection']['original_report_statement_null_reason'],
        original_report_mathematical_scope=report['mathematical_scope'],
        recorded_binding=exact['binding_path'], recorded_binding_sha256=exact['binding_sha256'],
        recorded_binding_statement=binding['statement'],
        recorded_binding_statement_sha256=hashlib.sha256(binding['statement'].encode()).hexdigest(),
        original_independent_report_method=report['method'], schema_method=binding['method'],
        evidence=evidence, descriptor_path=V17_DESCRIPTOR['path'], descriptor_sha256=V17_DESCRIPTOR['sha256'],
        reason='Exact two finite diagnostic IDs only: preserve the absent raw headline and original finite mathematical_scope. The complete binding statement records already independently checked literal results; no report is rewritten, no retrospective self-output hash is invented, and this registrar performs no new mathematics or wider inference.',
        raw_statement_changed=False, mathematical_replays=0, target_resolution='NONE')


# V18 admits only eight frozen ROOT-verifier written metadata records.
V18_DESCRIPTOR = dict(
    path='acceleration/proposal_20261003_registrar_v18_exact_written_v1.json',
    sha256='2692248d4274793d5fb162503d1eb3b9e5b02a517ef13f5fd6080ffc80f49629')
V18_EXACT = json.loads(r'''{
  "C-UNRESTRICTED-DEGREE14-TERNARY-PROPER-SUPPORT-NULLITY-LOWER3": {
    "descriptor_index": 0,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_proper_support_nullity3_01/proper_nullity3/claim_binding_schema2.json",
    "binding_sha256": "2f61ece7163676b90d069b6e50007d9f0b71a2dacd62659ee5c561ab87fea8ec"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-NULLITY2-PROPER-SUPPORT-EXCEPTION98": {
    "descriptor_index": 1,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_proper_support_nullity3_01/nullity2_exception98/claim_binding_schema2.json",
    "binding_sha256": "f5de0f71edc6d833c34e252040c0d44de854b2eefede78141e749dd96042f786"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-EQUAL-OUTSIDE-ROW-BUDGET-FILTER": {
    "descriptor_index": 2,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/equal_outside_filter/claim_binding_schema2.json",
    "binding_sha256": "103ac4be11643eef9660c60dea5fa08b6c1c1d9cb4efaa0d61f54f81d26ae1e1"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-NINE-DEFECT-NONREALIZABILITY": {
    "descriptor_index": 3,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_equal_outside_nine_01/nine_defect/claim_binding_schema2.json",
    "binding_sha256": "07432ba970adc3793d8772cb323b7b3d2388b1090b1cabc8501343c1220dfff2"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-NONZERO-DEFECT-LOWER12": {
    "descriptor_index": 4,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_nonzero_defect_lower12_01/claim_binding_schema2.json",
    "binding_sha256": "1aa6f97c2808aa65a5e10ebb6ab16b65bde67896651acdf05371bae0a47895f8"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-TWELVE-DEFECT-SUPPORT-CLASSIFICATION": {
    "descriptor_index": 5,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_twelve_defect_support_classification01/claim_binding_schema2.json",
    "binding_sha256": "949354d6193616bad1538ef4fb8bad34cd85d512738a522d75ed8245915ed131"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-RESIDUAL-LIFT-EIGEN1-PARITY": {
    "descriptor_index": 6,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_lift_parity_global_subcubic24_01/lift_parity/claim_binding_schema2_v3.json",
    "binding_sha256": "89d19828fe00a204fd38ebf6b5752f1d483e50b581181e469c3cf732dcfd49bd"
  },
  "C-UNRESTRICTED-DEGREE14-TERNARY-GLOBAL-SUBCUBIC-SUPPORT-LOWER24": {
    "descriptor_index": 7,
    "binding_path": "acceleration/results/20261003_independent_review/ternary_lift_parity_global_subcubic24_01/global_subcubic24/claim_binding_schema2_v3.json",
    "binding_sha256": "d84812cc17e23e01a0eece434565ffb92c3229ce0d04ba3ba2c1d5911a438f77"
  }
}''')


def v18_descriptor(cid):
    need(cid in V18_EXACT, 'v18 exact descriptor ID')
    need(digest(ROOT/V18_DESCRIPTOR['path']) == V18_DESCRIPTOR['sha256'],
         'v18 immutable reviewed descriptor bytes')
    declared = json.loads((ROOT/V18_DESCRIPTOR['path']).read_bytes())
    need(declared['schema'] == 'PROSPECTIVE_EXACT_REGISTRAR_V18_WRITTEN_ADAPTER_DESCRIPTORS_V1'
         and [r['id'] for r in declared['adapters']] == list(V18_EXACT)
         and type(declared['mathematical_replays']) is int and declared['mathematical_replays'] == 0,
         'v18 exact eight written descriptor records')
    exact = V18_EXACT[cid]
    record = declared['adapters'][exact['descriptor_index']]
    need(record['id'] == cid and record['binding'] ==
         dict(path=exact['binding_path'], sha256=exact['binding_sha256']),
         'v18 exact descriptor binding routing')
    return record


def v18_role(cid, expected, binding):
    if cid not in V18_EXACT: return False
    exact = V18_EXACT[cid]
    need(expected == exact['binding_sha256'], 'v18 exact frozen binding identity')
    record = v18_descriptor(cid); contract = record['binding_contract']
    keys = ['id', 'revision', 'claim_revision', 'status', 'review_state',
            'kind', 'basis', 'producer', 'verifier', 'method']
    need(all(k in binding and v15_same(binding[k], contract[k]) for k in keys),
         'v18 exact typed revision status roles method kind basis')
    need(all(k in binding and v15_same(binding[k], contract[k])
             for k in ['scope', 'dependencies', 'target_resolution']),
         'v18 exact original scope dependencies and nonresolution')
    need('verification_records' not in binding
         and binding.get('statement') == contract['statement']
         and binding.get('report') == record['primary_report']['path']
         and binding.get('report_sha256') == record['primary_report']['sha256']
         and binding.get('proof') == record['proof']['path']
         and binding.get('proof_sha256') == record['proof']['sha256']
         and 'controls' in binding and v15_same(binding['controls'], contract['controls']),
         'v18 exact literal statement report proof controls and no legacy fallback')
    need(digest(ROOT/exact['binding_path']) == exact['binding_sha256'],
         'v18 original immutable binding bytes')
    original = json.loads((ROOT/exact['binding_path']).read_bytes())
    need(v15_same(binding, original), 'v18 complete literal binding metadata')
    need(binding['inputs_sha256'].get(record['proof']['path']) == record['proof']['sha256']
         and digest(ROOT/record['proof']['path']) == record['proof']['sha256'],
         'v18 exact independently written proof bytes')
    return True


def v18_report(cid, report_sha, binding, report):
    if cid not in V18_EXACT: return None
    exact = V18_EXACT[cid]
    need(v18_role(cid, exact['binding_sha256'], binding), 'v18 exact bound report routing')
    record = v18_descriptor(cid); contract = record['report_contract']
    need(report_sha == record['primary_report']['sha256'],
         'v18 exact primary report identity')
    keys = ['status', 'claim_id', 'claim_revision', 'producer', 'verifier',
            'method', 'target_resolution']
    need(all(k in report and v15_same(report[k], contract[k]) for k in keys),
         'v18 exact typed independent report identity and method')
    headline = record['report_headlines']
    need(all(k in report and v15_same(report[k], v) for k, v in headline['present'].items())
         and all(k not in report for k in headline['absent']),
         'v18 exact literal report headlines and absences')
    need(all(k in report and v15_same(report[k], contract[k])
             for k in ['statement', 'scope', 'assumptions', 'dependencies'])
         and report['statement'] == binding['statement'],
         'v18 exact written statement original scope assumptions dependencies')
    need(all(k in report and v15_same(report[k], v) for k, v in record['explicit_null_fields'].items())
         and all(k in report and report[k] == v and type(v) is str and len(v) > 0
                 for k, v in record['explicit_null_reason_fields'].items()),
         'v18 exact written command null and reason')
    need(all(k in report and v15_same(report[k], v)
             for k, v in record['written_control_fields'].items()),
         'v18 exact nonexecuted written control metadata')
    need(digest(ROOT/record['primary_report']['path']) == report_sha,
         'v18 original immutable report bytes')
    original = json.loads((ROOT/record['primary_report']['path']).read_bytes())
    need(v15_same(report, original), 'v18 complete literal report metadata')
    return dict(claim_id=cid, claim_revision=1,
        recorded_binding=exact['binding_path'], recorded_binding_sha256=exact['binding_sha256'],
        original_report=record['primary_report']['path'], original_report_sha256=report_sha,
        original_report_statement_field='statement', original_report_statement=report['statement'],
        recorded_binding_statement=binding['statement'],
        raw_statement_changed=False, original_report_scope=report['scope'],
        original_binding_scope=binding['scope'], schema_scope=record['schema_scope'],
        original_report_headline_fields=headline['present'],
        original_report_absent_headline_fields={k: None for k in headline['absent']},
        original_report_absent_headline_null_reason=record['missing_headline_mapping'],
        original_report_command=report['command'],
        original_report_command_null_reason=report['command_null_reason'],
        original_report_controls=record['written_control_fields'],
        original_independent_report_method=report['method'], schema_method=binding['method'],
        descriptor_path=V18_DESCRIPTOR['path'], descriptor_sha256=V18_DESCRIPTOR['sha256'],
        reason='Only the exact eight frozen written metadata bindings: keep literal statement equality, complete original scope, every conditional/whole-support premise and explicit raw report absences. Three schema-scope fields are projected in memory. No original report/binding is rewritten and no mathematics or target inference is performed.',
        mathematical_replays=0, target_resolution='NONE')


def v18_scope(cid, expected, binding):
    need(cid in V18_EXACT and v18_role(cid, expected, binding),
         'v18 exact bound scope routing')
    record = v18_descriptor(cid); scope = record['schema_scope']
    need(set(scope) == {'description', 'unrestricted_target', 'target_resolution'}
         and type(scope['description']) is str and len(scope['description']) > 0
         and scope['unrestricted_target'] is True and scope['target_resolution'] == 'NONE'
         and v15_same(binding['scope'], record['original_scope']),
         'v18 exact three schema fields with original scope retained')
    return copy.deepcopy(scope)


# V19 SOURCE_ONLY: six exact existing Native-verifier bindings and one ordinary
# four-class scope projection. Missing wrappers gain no executable route.
V19_DESCRIPTOR = dict(
    path='acceleration/proposal_20261003_registrar_v19_exact_existing_v1.json',
    sha256='2254b33bb130e6a9c409a1dda334279b4906a5d6a2c2623c7287a33caf60d275')
V19_EXACT = {
    'C-FIXED17-EXTERIOR-MOMENT-RELAXATION-RATIONAL-FEASIBLE':
        (0, '1834df526949501ed6c7767d0b9ba4d52fc06f02b85c6b50ea44704ddf1451f1'),
    'C-LOCAL-CN-EXTERIOR-TYPE-CROSS-COMMON-NEIGHBOR-CAP':
        (1, 'ce592293782b207739ac87c34929c6c6417f69c2e71e2f49a5c53a6d0ed352d7'),
    'C-FIXED17-EXTERIOR-MOMENT-OUTSIDE-CN-FILTER-472':
        (2, '82d77964934cade61b9e10296d649584c01174c29460675a63dde25523f4280e'),
    'C-EXTERIOR-TYPE-PAIR-AND-TRIPLE-COMMON-NEIGHBOR-CAPS':
        (3, 'a1ed4e4dd1b039a2aeb8e94df4b05be182285cb8c7ef83940986d2ec3d706151'),
    'C-SEVENTEEN-POINT-LABELLED-TRIANGLE-FAMILY-FOUR-ISOMORPHISM-CLASSES':
        (4, '99573f66be7be07e0ec22867e250b7395537f82fe07b6d9ea941839540cc9fe4'),
    'C-UNRESTRICTED-TARGET-TERNARY-AFFINE-OBSTRUCTION-UNBALANCED-CIRCUIT-LE99':
        (5, '967691cde75d57d5ae4c28f40861ae49e074695312531a146a60d9d7de425fa5'),
    'C-UNRESTRICTED-TARGET-TERNARY-UNBALANCED-CIRCUIT-LE98':
        (6, 'e9128774855a9c9e7eae3265e7919b631bacab08f303dbd511d6473f988bcda3'),
}


def v19_descriptor(cid):
    need(cid in V19_EXACT, 'v19 exact descriptor ID')
    need(digest(ROOT/V19_DESCRIPTOR['path']) == V19_DESCRIPTOR['sha256'],
         'v19 immutable reviewed descriptor bytes')
    declared = json.loads((ROOT/V19_DESCRIPTOR['path']).read_bytes())
    need(declared['schema'] == 'PROSPECTIVE_EXACT_REGISTRAR_V19_EXISTING_BINDING_DESCRIPTORS_V1'
         and [r['id'] for r in declared['adapters']] == list(V19_EXACT)
         and type(declared['mathematical_replays']) is int
         and declared['mathematical_replays'] == 0
         and type(declared['new_Native_role_permissions']) is int
         and declared['new_Native_role_permissions'] == 6
         and declared['generic_ROOT_or_Native_waiver'] is False,
         'v19 exact six role permissions and seven scope records')
    index, identity = V19_EXACT[cid]
    record = declared['adapters'][index]
    need(record['id'] == cid and record['binding']['sha256'] == identity
         and record['report_top_level_statement_required'] is True
         and record['missing_headline_waiver'] is False,
         'v19 exact existing binding routing without absence waiver')
    return record


def v19_role(cid, expected, binding):
    if cid not in V19_EXACT: return False
    record = v19_descriptor(cid); contract = record['binding_contract']
    need(expected == V19_EXACT[cid][1], 'v19 exact frozen binding identity')
    need(set(binding) - {'inputs_sha256'} == set(contract)
         and all(v15_same(binding[k], value) for k, value in contract.items()),
         'v19 complete typed nonmap binding contract')
    need(binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
         and binding['producer'] != binding['verifier']
         and binding['target_resolution'] == 'NONE'
         and 'verification_records' not in binding,
         'v19 exact separate recorded role and no legacy fallback')
    native_role = record['role_permission_added']
    need(type(native_role) is bool
         and native_role is (binding['verifier'] == '/root/native_driver')
         and (native_role or binding['verifier'] == '/root/structural'),
         'v19 six exact Native roles or ordinary Structural scope only')
    need(digest(ROOT/record['binding']['path']) == expected,
         'v19 original immutable binding bytes')
    original = json.loads((ROOT/record['binding']['path']).read_bytes())
    need(v15_same(binding, original), 'v19 complete literal binding including input map')
    for review in record['review_records']:
        need(digest(ROOT/review['path']) == review['sha256'],
             'v19 exact prior scoped ROOT review bytes')
    return True


def v19_report(cid, report_sha, binding, report):
    if cid not in V19_EXACT: return None
    need(v19_role(cid, V19_EXACT[cid][1], binding), 'v19 exact bound report routing')
    record = v19_descriptor(cid); contract = record['report_contract']
    need(report_sha == record['primary_report']['sha256']
         and binding['report'] == record['primary_report']['path']
         and binding['report_sha256'] == report_sha,
         'v19 exact claim-bound report identity')
    need(set(report) - {'inputs_sha256'} == set(contract)
         and all(v15_same(report[k], value) for k, value in contract.items()),
         'v19 complete typed nonmap report contract')
    need(report['claim_id'] == cid and type(report['claim_revision']) is int
         and report['claim_revision'] == 1
         and report['statement'] == binding['statement']
         and report['producer'] == binding['producer']
         and report['verifier'] == binding['verifier']
         and report['method'] == binding['method']
         and report['target_resolution'] == 'NONE'
         and type(binding['verification_timestamp']) is str
         and report[record['report_timestamp_field']] == binding['verification_timestamp'],
         'v19 exact literal statement revision roles method and timestamp spelling')
    need(digest(ROOT/record['primary_report']['path']) == report_sha,
         'v19 original immutable report bytes')
    original = json.loads((ROOT/record['primary_report']['path']).read_bytes())
    need(v15_same(report, original), 'v19 complete literal report including input map')
    return dict(claim_id=cid, claim_revision=1,
        recorded_binding=record['binding']['path'], recorded_binding_sha256=V19_EXACT[cid][1],
        original_report=record['primary_report']['path'], original_report_sha256=report_sha,
        original_report_statement_field='statement', original_report_statement=report['statement'],
        recorded_binding_statement=binding['statement'], raw_statement_changed=False,
        original_report_scope=report['scope'], original_binding_scope=binding['scope'],
        schema_scope=record['schema_scope'], original_dependencies=binding['dependencies'],
        schema_dependencies=record['schema_dependencies'],
        original_verification_timestamp=binding['verification_timestamp'],
        original_report_timestamp_field=record['report_timestamp_field'],
        original_report_timestamp=report[record['report_timestamp_field']],
        original_report_contract=contract, original_report_input_map_preserved=True,
        missing_headline_waiver=False, root_review_records=record['review_records'],
        descriptor_path=V19_DESCRIPTOR['path'], descriptor_sha256=V19_DESCRIPTOR['sha256'],
        reason=record['reason'], mathematical_replays=0, target_resolution='NONE')


def v19_scope(cid, expected, binding):
    need(v19_role(cid, expected, binding), 'v19 exact bound scope routing')
    record = v19_descriptor(cid); scope = record['schema_scope']
    need(set(scope) == {'description', 'unrestricted_target', 'target_resolution'}
         and type(scope['description']) is str and len(scope['description']) > 0
         and type(scope['unrestricted_target']) is bool
         and scope['target_resolution'] == 'NONE'
         and v15_same(binding['scope'], record['original_scope']),
         'v19 exact schema scope and preserved original quantifiers')
    original = binding['scope']
    description = original.get('description', original.get('population'))
    unrestricted = original.get('unrestricted_target', original.get('unrestricted'))
    need(v15_same(scope['description'], description)
         and v15_same(scope['unrestricted_target'], unrestricted),
         'v19 literal scope key projection only')
    return copy.deepcopy(scope)


def v19_dependencies(cid, expected, binding, claims):
    need(v19_role(cid, expected, binding), 'v19 exact bound dependency routing')
    record = v19_descriptor(cid); proposed = record['schema_dependencies']
    need(type(proposed) is list
         and v15_same(binding['dependencies'], record['original_dependencies']),
         'v19 exact original and projected dependencies')
    present = {claim['id']: claim['revision'] for claim in claims}
    for dep in proposed:
        need(type(dep) is dict and set(dep) == {'id', 'revision', 'relation'}
             and type(dep['id']) is str and type(dep['revision']) is int
             and dep['revision'] == 1 and dep['relation'] == 'uses_result'
             and type(present.get(dep['id'])) is int and present[dep['id']] == 1,
             'v19 exact prerequisite revision present before dependent')
    return copy.deepcopy(proposed)


# V20 SOURCE_ONLY: one exact final5184 Native route and one exact finalAPI ROOT
# route. All V19 and inherited ordinary branches remain byte-preserved.
V20_DESCRIPTOR = dict(
    path='acceleration/proposal_20261003_registrar_v20_two_final_v1.json',
    sha256='b56816abdaa8bfca6177e7a189f5e15858a4a10ba8645f537be7bc54882bf9a9')
V20_EXACT = {
    'C-SEVENTEEN-POINT-LABELLED-TRIANGLE-FAMILY-COMPLETE-FINITE-CENSUS':
        (0, '1c01bee9c34ae407512270ec05c66f39e763a829f4e27102da97c86df10a70bb'),
    'C-ADJACENCY-SWITCH-ACTUAL-API-FINITE-PACKET-ENGINEERING':
        (1, '189a71a021c5772dc0125a35e579e6226f5347a5b4bc4e75dfd7beced916df29'),
}


def v20_descriptor(cid):
    need(cid in V20_EXACT, 'v20 exact final descriptor ID')
    need(digest(ROOT/V20_DESCRIPTOR['path']) == V20_DESCRIPTOR['sha256'],
         'v20 immutable two-final descriptor bytes')
    declared = json.loads((ROOT/V20_DESCRIPTOR['path']).read_bytes())
    need(declared['schema'] == 'PROSPECTIVE_EXACT_REGISTRAR_V20_TWO_FINAL_BINDINGS_V1'
         and [r['id'] for r in declared['adapters']] == list(V20_EXACT)
         and type(declared['added_exact_Native_roles']) is int
         and declared['added_exact_Native_roles'] == 1
         and type(declared['added_exact_ROOT_roles']) is int
         and declared['added_exact_ROOT_roles'] == 1
         and type(declared['mathematical_replays']) is int
         and declared['mathematical_replays'] == 0
         and declared['generic_ROOT_or_Native_waiver'] is False
         and declared['scope_or_dependency_projection'] is False,
         'v20 two exact final roles without generic or scope waiver')
    index, identity = V20_EXACT[cid]
    record = declared['adapters'][index]
    need(record['id'] == cid and record['binding']['sha256'] == identity
         and record['report_top_level_statement_required'] is True
         and record['missing_headline_waiver'] is False,
         'v20 exact final binding routing without absence waiver')
    return record


def v20_role(cid, expected, binding):
    if cid not in V20_EXACT: return False
    record = v20_descriptor(cid); contract = record['binding_contract']
    need(expected == V20_EXACT[cid][1], 'v20 exact frozen final binding identity')
    need(set(binding) - {'inputs_sha256'} == set(contract)
         and all(v15_same(binding[k], value) for k, value in contract.items()),
         'v20 complete typed nonmap final binding contract')
    need(binding['status'] == 'VERIFIED' and binding['review_state'] == 'CLEAR'
         and binding['producer'] == '/root/structural'
         and binding['producer'] == record['role_permission_producer']
         and binding['verifier'] == record['role_permission_verifier']
         and binding['verifier'] in {'/root/native_driver', '/root'}
         and binding['producer'] != binding['verifier']
         and binding['method'] == 'independent_artifact_check'
         and binding['method'] == record['method']
         and binding['target_resolution'] == 'NONE'
         and 'verification_records' not in binding,
         'v20 exact separate final role and no legacy fallback')
    need(digest(ROOT/record['binding']['path']) == expected,
         'v20 original immutable final binding bytes')
    original = json.loads((ROOT/record['binding']['path']).read_bytes())
    need(v15_same(binding, original), 'v20 complete literal final binding including input map')
    for review in record['review_records']:
        need(digest(ROOT/review['path']) == review['sha256'],
             'v20 exact scoped ROOT review bytes')
    return True


def v20_report(cid, report_sha, binding, report):
    if cid not in V20_EXACT: return None
    need(v20_role(cid, V20_EXACT[cid][1], binding), 'v20 exact final bound report routing')
    record = v20_descriptor(cid); contract = record['report_contract']
    need(report_sha == record['primary_report']['sha256']
         and binding['report'] == record['primary_report']['path']
         and binding['report_sha256'] == report_sha,
         'v20 exact final claim-bound report identity')
    need(set(report) - {'inputs_sha256'} == set(contract)
         and all(v15_same(report[k], value) for k, value in contract.items()),
         'v20 complete typed nonmap final report contract')
    need(report['claim_id'] == cid and type(report['claim_revision']) is int
         and report['claim_revision'] == 1
         and report['statement'] == binding['statement']
         and v15_same(report['scope'], binding['scope'])
         and report['producer'] == binding['producer']
         and report['verifier'] == binding['verifier']
         and report['method'] == binding['method']
         and report['target_resolution'] == 'NONE'
         and type(binding['verification_timestamp']) is str
         and report[record['report_timestamp_field']] == binding['verification_timestamp'],
         'v20 exact literal final statement revision scope roles method timestamp')
    need(digest(ROOT/record['primary_report']['path']) == report_sha,
         'v20 original immutable final report bytes')
    original = json.loads((ROOT/record['primary_report']['path']).read_bytes())
    need(v15_same(report, original), 'v20 complete literal final report including input map')
    return dict(claim_id=cid, claim_revision=1,
        recorded_binding=record['binding']['path'], recorded_binding_sha256=V20_EXACT[cid][1],
        original_report=record['primary_report']['path'], original_report_sha256=report_sha,
        original_report_statement_field='statement', original_report_statement=report['statement'],
        recorded_binding_statement=binding['statement'], raw_statement_changed=False,
        original_report_scope=report['scope'], original_binding_scope=binding['scope'],
        original_dependencies=binding['dependencies'], schema_scope=binding['scope'],
        schema_dependencies=binding['dependencies'],
        original_verification_timestamp=binding['verification_timestamp'],
        original_report_timestamp_field=record['report_timestamp_field'],
        original_report_timestamp=report[record['report_timestamp_field']],
        original_report_contract=contract, original_report_input_map_preserved=True,
        original_raw_primary_report=record['original_raw_primary_report'],
        original_raw_statement_and_scope_absence_preserved=True,
        original_API_false_flags_and_runtime_preserved=True,
        missing_headline_waiver=False, root_review_records=record['review_records'],
        descriptor_path=V20_DESCRIPTOR['path'], descriptor_sha256=V20_DESCRIPTOR['sha256'],
        reason=record['reason'], mathematical_replays=0, target_resolution='NONE')



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
        exact_v13 = v13_root_role(cid, expected, binding)
        exact_v15 = v15_role(cid, expected, binding)
        exact_v16 = v16_role(cid, expected, binding)
        exact_v17 = v17_role(cid, expected, binding)
        exact_v18 = v18_role(cid, expected, binding)
        exact_v19 = v19_role(cid, expected, binding)
        exact_v20 = v20_role(cid, expected, binding)
        v16_dependency_order(cid, {c['id'] for c in data['claims']})
        need((binding['status']=='VERIFIED' or exact_wave37) and binding['review_state']=='CLEAR','independent exact-scope checking status')
        witness_role=(cid==ROOTED7_WITNESS_ID and expected==ROOTED7_WITNESS_BINDING
                      and binding['producer']=='/root/structural'
                      and binding['verifier']=='/root/native_driver')
        need(binding['producer']!=binding['verifier'] and
             (binding['verifier'] in {'/root/checkpoint_audit','/root/structural'} or witness_role or exact_wave37 or exact_v11 or exact_v12 or exact_v13 or exact_v15 or exact_v16 or exact_v17 or exact_v18 or exact_v19 or exact_v20),
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
        v13_root_report(cid, report_sha, binding, report)
        editorial_statement_mapping = v14_lowword_editorial(cid, expected, binding, report_sha, report)
        wave40_statement_mapping = v15_report(cid, report_sha, binding, report)
        if wave40_statement_mapping is not None:
            need(editorial_statement_mapping is None, 'v15 disjoint editorial adapter')
            editorial_statement_mapping = wave40_statement_mapping
        wave41_statement_mapping = v16_report(cid, report_sha, binding, report)
        if wave41_statement_mapping is not None:
            need(editorial_statement_mapping is None, 'v16 disjoint exact metadata adapter')
            editorial_statement_mapping = wave41_statement_mapping
        wave42_statement_mapping = v17_report(cid, report_sha, binding, report)
        if wave42_statement_mapping is not None:
            need(editorial_statement_mapping is None, 'v17 disjoint exact metadata adapter')
            editorial_statement_mapping = wave42_statement_mapping
        wave43_statement_mapping = v18_report(cid, report_sha, binding, report)
        if wave43_statement_mapping is not None:
            need(editorial_statement_mapping is None, 'v18 disjoint exact written metadata adapter')
            editorial_statement_mapping = wave43_statement_mapping
        wave44_statement_mapping = v19_report(cid, report_sha, binding, report)
        if wave44_statement_mapping is not None:
            need(editorial_statement_mapping is None, 'v19 disjoint exact existing binding adapter')
            editorial_statement_mapping = wave44_statement_mapping
        wave44_final_mapping = v20_report(cid, report_sha, binding, report)
        if wave44_final_mapping is not None:
            need(editorial_statement_mapping is None, 'v20 disjoint exact final binding adapter')
            editorial_statement_mapping = wave44_final_mapping
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
        elif editorial_statement_mapping is not None:pass
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
        if cid in V18_EXACT:
            original_scope = copy.deepcopy(binding['scope'])
            projected_scope = v18_scope(cid, expected, binding)
            binding = copy.deepcopy(binding)
            binding['scope'] = projected_scope
        if cid in V19_EXACT:
            original_scope = copy.deepcopy(binding['scope'])
            projected_scope = v19_scope(cid, expected, binding)
            projected_dependencies = v19_dependencies(cid, expected, binding, data['claims'])
            binding = copy.deepcopy(binding)
            binding['scope'] = projected_scope
            binding['dependencies'] = projected_dependencies
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
        if editorial_statement_mapping is not None:
            claim['unknowns']['editorial_statement_mapping'] = json.dumps(editorial_statement_mapping,sort_keys=True)
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
    report['editorial_statement_mappings'] = [json.loads(c['unknowns']['editorial_statement_mapping']) for c in data['claims'][len(old['claims']):] if 'editorial_statement_mapping' in c['unknowns']]
    need((ROOT/'CLAIMS.yaml').read_bytes()==before,'no concurrent ledger change')
    pending=out/'CLAIMS.pending.yaml';pending.write_bytes(after);os.replace(pending,ROOT/'CLAIMS.yaml');save(out/'summary.json',report)
    print(json.dumps({k:report[k] for k in ['status','claim_records','status_counts','new_claim_ids']}))


if __name__=='__main__':main()



