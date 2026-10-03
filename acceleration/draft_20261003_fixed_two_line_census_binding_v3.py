"""Metadata only: distinguish supplementary audit records from legacy primary audit."""
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
OLD = 'acceleration/results/20261003_fixed_two_line_census_binding02/claim_binding_schema2_draft.json'
OLD_SHA = '85e943e2b7431deb4cf7ef9c3b49a72d8e714d9a85ed6999273df8894377e82e'
OLD_CLOSURE = 'acceleration/results/20261003_fixed_two_line_census_binding02/closure.json'
OLD_CLOSURE_SHA = '0c717b3dc005990ce2c55492a7bb968890792fdac4a3edb5a4e4d2e3e20483a5'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',required=True,type=float)
    parser.add_argument('--out',required=True,type=Path)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds,allocation_reason='Metadata only: exact existing V2 supplementary records rename for legacy registrar interoperability, no mathematical replay or primary audit change')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(),'Fresh editorial derivative output')
    out.mkdir(parents=True)
    pins = {}

    def pin(name,wanted=None):
        need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds'] > 20,'Not completed within allocated metadata budget')
        path = (ROOT/name).resolve()
        need(type(name) is str and not Path(name).is_absolute() and path.is_relative_to(ROOT) and path.is_file(),'Exact local input '+name)
        identity = sha(path)
        need(wanted is None or identity == wanted,'Frozen identity '+name)
        need(name not in pins or pins[name] == identity,'Consistent repeated identity '+name)
        pins[name] = identity
        return json.loads(path.read_bytes()) if path.suffix == '.json' else None

    old = pin(OLD,OLD_SHA)
    pin(OLD_CLOSURE,OLD_CLOSURE_SHA)
    need(old['id'] == 'C-HYPERGRAPH-WEIGHT60-WARM01-FIXED-V2-TWO-LINE-CENSUS'
         and old['claim_revision'] == old['revision'] == 1 and old['editorial_binding_version'] == 2,'Exact approved r1 editorial predecessor')
    need(old['report_sha256'] == '1d3cecc2fd8d3e689966a334af59a9af7d0a2e8c66b356b98484aef3ed79e589'
         and len(old['verification_records']) == 2 and 'supplemental_verification_records' not in old,'Exact full primary audit and two supplementary records')
    for name,identity in old['inputs_sha256'].items():
        pin(name,identity)
    own = Path(__file__).relative_to(ROOT).as_posix()
    pin(own)
    pin(own.replace('.py','_spec.md'))
    binding = copy.deepcopy(old)
    binding['updated_at'] = datetime.now(timezone.utc).isoformat()
    binding['editorial_binding_version'] = 3
    binding['supplemental_verification_records'] = binding.pop('verification_records')
    binding['previous_editorial_binding'] = dict(path=OLD,sha256=OLD_SHA,
        statement_scope_roles_dependencies_unchanged=True,
        correction='Legacy registrar treats verification_records[0] as a primary audit with audit_path/audit_sha256. These existing report-based precal/full supplemental records are renamed only; primary report1d3 remains authoritative.',
        independent_pre_registration_veto='Separate checkpoint_audit source review before any V13 freeze/execution identified the incompatible key; ROOT authorized this editorial derivative.')
    binding['inputs_sha256'] = pins
    need(binding['supplemental_verification_records'] == old['verification_records'],'Supplementary record values unchanged')
    need('verification_records' not in binding and all(binding[key] == old[key] for key in
        ['id','revision','claim_revision','statement','scope','dependencies','assumptions','status','review_state','kind','basis','producer','verifier','method','report','report_sha256','controls','unavailable_information']),
        'No mathematical/primary audit/control/availability changes')
    save(out/'claim_binding_schema2_draft.json',binding)
    save(out/'closure.json',dict(schema='FIXED_TWO_LINE_CENSUS_BINDING_EDITORIAL_V3_CLOSURE',claim_id=old['id'],claim_revision=1,source_commit=old['source_commit'],
        records=[dict(path=name,sha256=identity,bytes=(ROOT/name).stat().st_size,availability='LOCAL_ONLY') for name,identity in sorted(pins.items())],
        claim_binding=dict(path=(out/'claim_binding_schema2_draft.json').relative_to(ROOT).as_posix(),sha256=sha(out/'claim_binding_schema2_draft.json')),
        new_mathematical_checks=False,statement_unchanged=True,ledger_edited=False))
    print(json.dumps(dict(binding_sha256=sha(out/'claim_binding_schema2_draft.json'),closure_sha256=sha(out/'closure.json'),records=len(pins),new_mathematical_checks=False,ledger_edited=False)))


if __name__ == '__main__':
    main()
