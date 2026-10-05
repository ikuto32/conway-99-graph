"""Bind independent general Gram lemma and the exact initial45literal cut."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

import audit_20260930_gram_nogood_v1 as checker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'acceleration/results/20260930_independent_review'
AUDIT = ROOT/'acceleration/results/20260930_rook_gram_minimized/independent_nogood.json'
AUDIT_HASH = 'd0bdbc27029a4c6bf38199fc186afd031affefd2b4531413d83108c967d55ad8'
CERT = ROOT/'acceleration/results/20260930_rook_gram_minimized/certificate.json'
CERT_HASH = '255560186ad410e57582ab34c1b7cb90b899b4d9656ce37285bc06ce98b1145a'
DOC = ROOT/'docs/DERIVATION_20260930_TARGET_GRAM_NOGOODS.md'


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    checker.need(digest(AUDIT) == AUDIT_HASH and digest(CERT) == CERT_HASH,'immutable initial certificate/audit bindings')
    audit = json.loads(AUDIT.read_bytes())
    certificate = json.loads(CERT.read_bytes())
    checker.need(audit['status'] == 'INDEPENDENT_TARGET_GRAM_NOGOOD_PASS'
                 and audit['clause_length'] == 45 and audit['support_size'] == 26
                 and audit['quadratic_value'] == -176426969710399200,'exact checked initial scope')
    checker.need(checker.product_basis((27,-9,1),(27,-9,1)) == (1701,-567,63),'universal expansion')
    bindings = {key(path):digest(path) for path in (AUDIT,CERT,DOC,Path(__file__),Path(checker.__file__),ROOT/'uv.lock')}
    for path,value in audit['inputs_sha256'].items():
        checker.need(digest(ROOT/path) == value,'cut audit dependency changed')
        bindings[path] = value
    now = datetime.now(timezone.utc).isoformat()
    common = dict(timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
                  verifier='/root/eight_domain_audit independent checking agent',
                  verification_type='Independent exact derivation and artifact revision binding',producer_imported=False,
                  target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY')
    general = dict(**common,status='INDEPENDENT_TARGET_GRAM_PSD_SUPPORT_LEMMA_PASS',
                   claim_id='C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS',claim_revision=1,recommendation='VERIFIED',
                   statement='For every symmetric binary99by99zero-diagonal A satisfying A²=12I-A+2J, G=27I-9A+J satisfies G²=63G and is positive semidefinite. For any principal vertex set, fixed/free distinct Boolean edge parameterization, integer vector w, and evaluated negative quadratic, the clause requiring at least one current value of a free edge with nonzero coefficient -18w_uw_v to change is necessary for every target extension.',
                   basis=['DERIVED'],scope='A universal necessary target identity plus a conditional cut theorem; no existence or nonexistence conclusion.',
                   assumptions=['Exactly99vertices, symmetric binary zero-diagonal adjacency, and the exact integer target identity.',
                                'The principal graph lists every pair as fixed or a distinct free Boolean edge; the fixed entries agree with any claimed extension.',
                                'The vector and all quadratic coefficients are exact; the evaluated quadratic is strictly negative; every nonzero free-edge coefficient is included.'],
                   dependencies=[],inputs_sha256={key(DOC):digest(DOC),key(checker.__file__):digest(checker.__file__),key(AUDIT):digest(AUDIT),key(__file__):digest(__file__),key(ROOT/'uv.lock'):digest(ROOT/'uv.lock')},
                   written_audit=key(DOC),exact_expansion=dict(G=[27,-9,1],G_squared=[1701,-567,63],identity_multiplier=63,basis=['I','A','J']),
                   proof='Diagonal entries force degree14 and hence AJ=JA=14J. Expanding G² gives63G. Symmetry gives x^TGx=||Gx||²/63>=0. Zero extension proves principal PSD. The affine edge expansion fixes the same negative value whenever every nonzero-coefficient edge value is preserved, so every target extension must falsify that preserved pattern.',
                   controls=audit['controls'],limitations=['No target graph, unrestricted exclusion, or universal rook containment.',
                                                        'No minimization claim for vector support or clause length.',
                                                        'Cut validity is a target-extension consequence; it is not generally a consequence of a weaker local CNF.'])
    general_path = OUT/'target_gram_support_lemma.json'
    save(general_path,general)
    bindings[key(general_path)] = digest(general_path)
    specific = dict(**common,status='INDEPENDENT_MINIMIZED_GRAM_NOGOOD_CLAIM_BINDING_PASS',
                    claim_id='C-ROOK-FOUR-FACTOR-MINIMIZED-GRAM-NOGOOD',claim_revision=1,recommendation='VERIFIED',
                    statement='Every Conway99target extension of the exact780edge frozen-central-factor family satisfies the45literal clause saved in acceleration/results/20260930_rook_gram_minimized/nogood.clause. Fixing those45edge values to the recorded rejected local graph forces the exact principal quadratic -176426969710399200, independently of the other735free edge values and all40outside vertices.',
                    basis=['DERIVED','COMPUTED'],scope='Only the exact recorded780edge family and this specific45value pattern; not all assignments, factor stars, or targets.',
                    assumptions=['Exact fixed central matching, four incidence blocks, root attachments, and variable labels from the independently audited780edge model.',
                                 'A claimed target completion preserves the fixed entries of this principal59vertex graph.'],
                    dependencies=[dict(id='C-TARGET-GRAM-PSD-AND-SUPPORT-NOGOODS',revision=1,relation='uses_result'),
                                  dict(id='C-ROOK-FOUR-FACTOR-WINDOW-CNF-ENCODING',revision=1,relation='encoding_equivalence')],
                    inputs_sha256=bindings,raw_audit=key(AUDIT),raw_audit_sha256=AUDIT_HASH,
                    certificate=key(CERT),certificate_sha256=CERT_HASH,
                    verified_clause=audit['verified_clause'],clause_length=45,support_size=26,
                    quadratic_value=-176426969710399200,linear_quadratic_constant=audit['linear_quadratic_constant'],
                    checked_edge_variables=780,nonzero_variable_coefficients=45,omitted_zero_coefficients=735,
                    controls=audit['controls'],local_cnf_consequence_claimed=False,
                    limitations=['This is a support-pattern exclusion for target extensions, not another claim that the original local SAT graph is invalid as a local graph.',
                                 'The original59vertex Gram obstruction is recorded separately; this binding adds the exact reusable45literal consequence.',
                                 'No claim that45literals or26vector entries is globally minimal.',
                                 'No whole-family or unrestricted nonexistence conclusion.'])
    specific_path = OUT/'minimized_gram_nogood_claim_binding.json'
    save(specific_path,specific)
    print(json.dumps(dict(general=dict(path=key(general_path),sha256=digest(general_path)),specific=dict(path=key(specific_path),sha256=digest(specific_path)))))


if __name__ == '__main__':
    main()
