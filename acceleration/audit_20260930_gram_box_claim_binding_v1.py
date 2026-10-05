"""Bind the independently derived general box lemma and initial exact cut."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_gram_box_nogood_v1 as box

ROOT,need,digest,key = box.ROOT,box.need,box.digest,box.key


def save(path,record):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(record,stream,indent=2)
        stream.write('\n')


def main():
    out = ROOT/'acceleration/results/20260930_independent_review'
    audit_path = ROOT/'acceleration/results/20260930_rook_gram_box_cut_initial/independent_box_nogood.json'
    derivation = ROOT/'docs/DERIVATION_20260930_TARGET_GRAM_BOX_NOGOODS.md'
    parent_lemma = out/'target_gram_support_lemma.json'
    need(digest(audit_path) == 'd336249f1ccdd91d9f5b8399faee56a8a589ac98d3ab9eb445e22b5ae1e09251','exact independently completed box audit')
    need(digest(parent_lemma) == 'e194ca054dfe0596ae2b9ff1070ef59289c7c0401497a63c77eb62e217bd1ac6','exact independently derived PSD lemma')
    audit = json.loads(audit_path.read_bytes())
    need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS','box audit status')
    bindings = dict(audit['inputs_sha256'])
    for path in (Path(__file__),derivation,parent_lemma,audit_path,ROOT/'uv.lock'):
        bindings[key(path)] = digest(path)
    need(all(digest(ROOT/path) == value for path,value in bindings.items()),'current exact evidence binding')
    common = dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',verification_type='Independent exact written derivation, explicit maximizing-corner audit, and claim revision binding',
                  inputs_sha256=bindings,producer_imported=False,target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',
                  controls=audit['controls'],written_audit=key(derivation),recommendation='VERIFIED')
    lemma = dict(**common,status='INDEPENDENT_TARGET_GRAM_BOOLEAN_BOX_LEMMA_PASS',claim_id='C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS',claim_revision=1,
                 basis=['DERIVED'],kind='mathematical result',
                 statement='For every target adjacency A, every principal vertex set with fixed edges and distinct Boolean free-edge variables, every exact integer vector w and every prescribed variable subset F, its quadratic q=c+sum(d_e*t_e), d_e=-18*w_u*w_v, has exact Boolean-box maximum U=c+sum_F(d_e*a_e)+sum_notF(max(0,d_e)). If U<0, every target extension preserving the fixed scaffold must change at least one prescribed value in F.',
                 scope='Universal conditional necessary target-extension rule. Strictly generalizes the complete-nonzero-support cut by allowing some nonzero-coefficient variables to vary.',
                 assumptions=['A is symmetric binary99by99 with zero diagonal and satisfies the exact target identity A²=12I-A+2J.',
                              'Every unordered principal pair is fixed or mapped to one distinct Boolean variable; fixed entries agree with any claimed extension.',
                              'All coefficients, assignments and the strictly negative bound are exact; all variables outside F are maximized, including omitted variables.'],
                 dependencies=[dict(id='C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS',revision=1,relation='uses_result')],
                 relationship_to_prior_claim='Uses the already independently established universal PSD identity. It is a new broader cut theorem; no previous claim statement or evidence is replaced.',
                 limitations=['A nonnegative box maximum does not establish feasibility or invalidate other possible cuts.',
                              'A box corner need not obey local graph constraints; the unrestricted box is a safe superset.',
                              'This implication proves neither target existence nor general nonexistence.'])
    specific = dict(**common,status='INDEPENDENT_INITIAL_GRAM_BOX_NOGOOD_CLAIM_BINDING_PASS',claim_id='C-ROOK-FOUR-FACTOR-INITIAL-GRAM-BOX-NOGOOD',claim_revision=1,
                    basis=['DERIVED','COMPUTED'],kind='exclusion',
                    statement='Every Conway99target extension of the recorded780edge frozen-central-factor family satisfies the21literal clause in acceleration/results/20260930_rook_gram_box_cut_initial/nogood.clause. Preserving those21edge values forces its exact principal quadratic to be at most -176426969710399200 for every assignment of the other759free edges and every choice of the40outside vertices.',
                    scope='One exact21value forbidden pattern in one frozen-central-factor family. The excluded pattern is broader than the parent45value pattern; no entire-family or target-level exclusion is asserted.',
                    assumptions=['The exact fixed principal59scaffold and edge-variable labels from the audited780edge encoding.','Target extensions preserve this fixed scaffold.'],
                    dependencies=[dict(id='C-TARGET-GRAM-BOOLEAN-BOX-NOGOODS',revision=1,relation='uses_result'),
                                  dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence'),
                                  dict(id='C-ROOK-FOUR-FACTOR-MINIMIZED-GRAM-NOGOOD',revision=1,relation='derived_from')],
                    global_boolean_box_upper_bound=audit['global_boolean_box_upper_bound'],
                    verified_clause=audit['verified_clause'],fixed_nonzero_variables=audit['fixed_nonzero_variables'],
                    freed_nonzero_variables=audit['freed_nonzero_variables'],zero_coefficient_variables=audit['zero_coefficient_variables'],
                    certificate_sha256=audit['certificate_sha256'],graph_sha256=audit['graph_sha256'],
                    independent_box_audit=key(audit_path),independent_box_audit_sha256=digest(audit_path),
                    limitations=['The21literal clause is a strict subset of the45literal parent, but global minimality is not established.',
                                 'The clause is target-extension-valid, not a consequence of the weaker local CNF.',
                                 'No graph, complete-family UNSAT proof, unrestricted coverage argument, or external review is supplied.'])
    paths = [out/'target_gram_boolean_box_lemma.json',out/'initial_gram_box_nogood_claim_binding.json']
    for path,record in zip(paths,(lemma,specific)):
        save(path,record)
    print(json.dumps({key(path):digest(path) for path in paths}))


if __name__ == '__main__':
    main()
