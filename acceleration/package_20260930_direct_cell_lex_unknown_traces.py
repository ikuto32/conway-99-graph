"""Candidate deterministic transport of only the two saved lex UNKNOWN host traces."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import copy
import ctypes
import gzip
import hashlib
import json
import platform
import subprocess
import sys
import time
import zlib

import recover_20260930_direct_cell_lex_unknown_traces as recovery

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / 'acceleration/results'
SPEC = Path(__file__).with_name('package_20260930_direct_cell_lex_unknown_traces_spec.md')
LIMITS = dict(seconds=120, peak_working_set_bytes=512 * 1024**2,
              raw_part_bytes=8 * 1024**2, maximum_gzip_part_bytes=10 * 1024**2)
OUTCOME_PINS = {
    'acceleration/results/20260930_independent_review/direct_cell_lex_standalone_unknown/summary.json': 'f56257086586c6cad43bcab89da071551ca6d67e30196749827bb10dda280233',
    'acceleration/results/20260930_independent_review/direct_cell_lex_coupled_unknown/summary.json': 'dde2093be28b749c4bd27e9be06158cce19d84d65aadb1123bc4cfa4d4191e8a',
}
CASES = [
    dict(variant='standalone', directory='20260930_direct_cell_lex_standalone_native_pilot',
         summary_sha256='892a06007aff41ba193c4a1d17955d81b3173a8349e2eb20e045fcf2e81a9544',
         manifest_sha256='0d33a068b0977784007d589e7f30087989795cb06c64a835176c7c8959143c3f',
         raw_sha256='7ac7f9fcee5ee4de44ffa76b8888ad42977a703103156c8e266ec4dfc915edb7',
         raw_bytes=284049408),
    dict(variant='at_least_seven', directory='20260930_direct_cell_lex_coupled_native_pilot',
         summary_sha256='660e0577172e83f4396a36ef043ac87b5f1443b3c1c246584fd6a7ba2d3e65b1',
         manifest_sha256='3df8d301c8df5e64ae067c1a7e39f0e779942ffd4a9910c35f2036b7b22eaa13',
         raw_sha256='e7bd9443aaa76951c37986bd250b732e909fe2313597782362941e7d25a87112',
         raw_bytes=415830016),
]
need, sha = recovery.need, recovery.sha


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def peak():
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
            'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    need(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb), 'memory observation')
    need(counters.PeakWorkingSetSize > 0, 'nonzero peak memory observation')
    return counters.PeakWorkingSetSize


def budget(start):
    need(time.monotonic() - start <= LIMITS['seconds'], '120-second cooperative allocation')
    need(peak() <= LIMITS['peak_working_set_bytes'], '512MiB working-set allocation')


def gzip_part(path, data):
    with path.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=1, mtime=0) as stream:
            stream.write(data)


def make_part(path, data, index, offset, base):
    gzip_part(path, data)
    need(path.stat().st_size <= LIMITS['maximum_gzip_part_bytes'], 'gzip payload <=10MiB')
    need(gzip.decompress(path.read_bytes()) == data, 'immediate literal chunk recovery')
    return dict(index=index, relative_path=path.relative_to(base).as_posix(), raw_offset=offset,
                raw_bytes=len(data), raw_sha256=hashlib.sha256(data).hexdigest(),
                gzip_bytes=path.stat().st_size, gzip_sha256=sha(path))


def controls(out):
    out.mkdir()
    pieces = [bytes(range(256)) * 3, b'preserved incomplete trace\n' * 17]
    parts = []; offset = 0
    for index, data in enumerate(pieces):
        path = out / f'tiny{index}.gz'
        parts.append(make_part(path, data, index, offset, out)); offset += len(data)
    raw = b''.join(pieces)
    original = out / 'tiny.raw'; original.write_bytes(raw)
    record = dict(variant='synthetic', native_outcome='UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME',
                  complete_unsat_proof=False, raw_bytes=len(raw), raw_sha256=sha(original), parts=parts)
    recovery.recover_record(record, out, out / 'tiny.restored', original)
    twin = out / 'determinism.gz'; gzip_part(twin, pieces[0])
    need(twin.read_bytes() == (out / 'tiny0.gz').read_bytes(), 'deterministic compressed bytes')
    rejected = []
    for label in ('whole_hash', 'whole_length', 'part_hash', 'part_length', 'offset', 'index',
                  'compressed_hash', 'compressed_length', 'part_order', 'missing_part', 'path_escape', 'proof_claim', 'outcome'):
        bad = copy.deepcopy(record)
        if label == 'whole_hash': bad['raw_sha256'] = '0' * 64
        elif label == 'whole_length': bad['raw_bytes'] += 1
        elif label == 'part_hash': bad['parts'][0]['raw_sha256'] = '0' * 64
        elif label == 'part_length': bad['parts'][0]['raw_bytes'] += 1
        elif label == 'offset': bad['parts'][0]['raw_offset'] = 1
        elif label == 'index': bad['parts'][0]['index'] = 1
        elif label == 'compressed_hash': bad['parts'][0]['gzip_sha256'] = '0' * 64
        elif label == 'compressed_length': bad['parts'][0]['gzip_bytes'] += 1
        elif label == 'part_order': bad['parts'].reverse()
        elif label == 'missing_part': bad['parts'].pop()
        elif label == 'path_escape': bad['parts'][0]['relative_path'] = '../tiny.gz'
        elif label == 'proof_claim': bad['complete_unsat_proof'] = True
        elif label == 'outcome': bad['native_outcome'] = 'UNSAT'
        try: recovery.recover_record(bad, out)
        except ValueError: rejected.append(label)
        else: raise ValueError('corrupt transport metadata accepted: ' + label)
    corrupt = out / 'corrupt.gz'; data = bytearray((out / 'tiny0.gz').read_bytes()); data[-8] ^= 1; corrupt.write_bytes(data)
    bad = copy.deepcopy(record); bad['parts'][0].update(relative_path='corrupt.gz', gzip_sha256=sha(corrupt))
    try: recovery.recover_record(bad, out)
    except (ValueError, OSError, EOFError, zlib.error): rejected.append('corrupt_gzip_crc')
    else: raise ValueError('corrupt gzip accepted')
    for label, data in [('truncated_gzip', (out/'tiny0.gz').read_bytes()[:-1]),
                        ('extra_gzip_member', (out/'tiny0.gz').read_bytes()+gzip.compress(b'',mtime=0))]:
        path=out/(label+'.gz');path.write_bytes(data)
        bad=copy.deepcopy(record);bad['parts'][0].update(relative_path=path.name,gzip_sha256=sha(path),gzip_bytes=len(data))
        try:recovery.recover_record(bad,out)
        except (ValueError,OSError,EOFError,zlib.error):rejected.append(label)
        else:raise ValueError('bad gzip boundary accepted '+label)
    changed=bytes([pieces[0][0]^1])+pieces[0][1:];path=out/'changed_payload.gz';gzip_part(path,changed)
    bad=copy.deepcopy(record);bad['parts'][0].update(relative_path=path.name,gzip_sha256=sha(path),gzip_bytes=path.stat().st_size,raw_sha256=hashlib.sha256(changed).hexdigest())
    bad['raw_sha256']=hashlib.sha256(changed+pieces[1]).hexdigest()
    try:recovery.recover_record(bad,out,original=original)
    except ValueError:rejected.append('self_consistent_changed_payload')
    else:raise ValueError('changed payload accepted against original')
    save(out / 'summary.json', dict(status='UNKNOWN_HOST_TRACE_TRANSPORT_CONTROLS_PASS',
         positive_bytes=len(raw), deterministic_gzip=True, rejected=rejected, proof_validity_checked=False))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic(); inputs = {}; records = []
    try:
        for name, digest in OUTCOME_PINS.items():
            need(sha(ROOT / name) == digest, 'separate outcome/availability record ' + name)
            inputs[name] = digest
            gate=json.loads((ROOT/name).read_bytes())
            need(gate['status']=='INDEPENDENT_DIRECT_CELL_LEX_UNKNOWN_NATIVE_RUN_AUDIT_PASS' and gate['partial_trace']['current_ext4']['available'] is False,'separate observed missing originals')
        for name,digest in [('acceleration/package_20260930_direct_cell_unknown_trace_package.py','b6931efaaf7263ac435d11de607a47e791b9856641246995e34a26e6afe5793b'),('acceleration/recover_20260930_direct_cell_unknown_trace_package.py','d154ee34d8e2540a7f6620d154f1e9d14cba142be8727e10e2f48f0f51e747d2')]:
            need(sha(ROOT/name)==digest,'preserved source lineage');inputs[name]=digest
        for path in (Path(__file__), SPEC, Path(recovery.__file__), ROOT / 'uv.lock', ROOT / 'pyproject.toml'):
            inputs[key(path)] = sha(path)
        save(out / 'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
             source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, encoding='utf8').strip(),
             command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
             zlib_compile_version=zlib.ZLIB_VERSION, zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION,
             inputs_sha256=inputs, selection=CASES, limits=LIMITS,
             gzip_parameters=dict(compresslevel=1, mtime=0, filename=''), native_calls=0,
             scope='Complete transport of the two saved host UNKNOWN traces only; no complete UNSAT proof claim.'))
        controls(out / 'controls'); budget(start)
        for case in CASES:
            directory = B / case['directory']; raw = directory / 'main/proof.drat'
            summary_path = directory / 'summary.json'; manifest_path = directory / 'manifest.json'
            need(sha(summary_path) == case['summary_sha256'] and sha(manifest_path) == case['manifest_sha256'], 'frozen run summary and tool manifest')
            summary = json.loads(summary_path.read_bytes()); tool_manifest = json.loads(manifest_path.read_bytes())
            need(summary['variant'] == case['variant'] and summary['interpreted_result'] == 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME', 'saved UNKNOWN run')
            need(summary['receipt']['actual_exit_code'] in (0, 124) and not summary['receipt']['outer_windows_guard_expired'], 'historical wrapped UNKNOWN receipt')
            need(summary['proof_copy']['sha256'] == case['raw_sha256'] and summary['proof_copy']['bytes'] == case['raw_bytes'], 'historical transfer identity')
            need(raw.stat().st_size == case['raw_bytes'] and sha(raw) == case['raw_sha256'], 'fresh saved host trace identity')
            for path in (summary_path, manifest_path, raw): inputs[key(path)] = sha(path)
            for name, digest in summary['outputs_sha256'].items():
                path = ROOT / name
                need(sha(path) == digest, 'unchanged saved run output ' + name); inputs[name] = digest
            folder = out / case['variant']; folder.mkdir()
            (folder / 'run_summary.json').write_bytes(summary_path.read_bytes())
            (folder / 'run_manifest.json').write_bytes(manifest_path.read_bytes())
            total = hashlib.sha256(); offset = 0; parts = []
            with raw.open('rb') as stream:
                for index, data in enumerate(iter(lambda: stream.read(LIMITS['raw_part_bytes']), b'')):
                    target = folder / f'saved_unknown_trace.part{index:04d}.drat.gz'
                    parts.append(make_part(target, data, index, offset, out)); total.update(data); offset += len(data)
                    budget(start)
            need(offset == case['raw_bytes'] and total.hexdigest() == case['raw_sha256'], 'whole host bytes during packaging')
            record = dict(variant=case['variant'], raw_original_path=key(raw), raw_bytes=offset,
                raw_sha256=total.hexdigest(), native_outcome=summary['interpreted_result'],
                complete_unsat_proof=False, proof_validity_checked=False, parts=parts,
                run_summary_path=key(summary_path), run_summary_sha256=case['summary_sha256'],
                run_manifest_path=key(manifest_path), run_manifest_sha256=case['manifest_sha256'],
                historical_tool_inputs_sha256=tool_manifest['inputs_sha256'],
                historical_ext4_source=summary['proof_copy']['linux_source'],
                current_ext4_availability='MISSING_AT_PINNED_OUTCOME_AUDIT',
                ext4_scope='Pinned later outcome audit observed ENOENT; this packager makes no fresh ext4 query and preserves only authenticated host bytes.',
                separate_outcome_availability_pins=OUTCOME_PINS,
                host_original_preserved=True)
            recovered = recovery.recover_record(record, out, original=raw)
            need(sha(raw) == case['raw_sha256'], 'original retained unchanged')
            records.append(record); save(folder / 'recovery_identity.json', recovered)
            budget(start)
            save(out / f'checkpoint_{len(records):02d}.json', dict(completed_variants=[r['variant'] for r in records],
                 raw_bytes=sum(r['raw_bytes'] for r in records), elapsed_seconds=time.monotonic()-start))
            print(json.dumps(dict(variant=case['variant'], raw_bytes=offset, parts=len(parts),
                  gzip_bytes=sum(p['gzip_bytes'] for p in parts))), flush=True)
        manifest = dict(schema=recovery.SCHEMA, records=records, inputs_sha256=inputs,
            raw_part_bytes=LIMITS['raw_part_bytes'], maximum_gzip_part_bytes=LIMITS['maximum_gzip_part_bytes'],
            gzip_parameters=dict(compresslevel=1, mtime=0, filename=''), saved_host_transport_complete=True,
            native_outcomes=['UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'] * 2, complete_unsat_proof=False,
            proof_validity_checked=False, host_originals_preserved=True,
            current_ext4_availability='MISSING_AT_PINNED_OUTCOME_AUDIT', artifact_availability='LOCAL_ONLY',independent_transport_approval=False)
        save(out / 'package_manifest.json', manifest); budget(start)
        summary = dict(status='CANDIDATE_TWO_LEX_UNKNOWN_HOST_TRACES_LOSSLESSLY_PACKAGED',
            package_manifest_path=key(out / 'package_manifest.json'), package_manifest_sha256=sha(out / 'package_manifest.json'),
            traces=2, raw_bytes=sum(r['raw_bytes'] for r in records), gzip_parts=sum(len(r['parts']) for r in records),
            gzip_bytes=sum(p['gzip_bytes'] for r in records for p in r['parts']),
            largest_gzip_part_bytes=max(p['gzip_bytes'] for r in records for p in r['parts']),
            complete_saved_host_byte_recovery=True, literal_original_comparison=True,
            host_originals_preserved=True, complete_unsat_proof=False, proof_validity_checked=False,
            native_calls=0, elapsed_seconds=time.monotonic()-start, peak_working_set_bytes=peak(),
            artifact_availability='LOCAL_ONLY', independent_transport_approval=False,
            shared_components=['Fresh source adapted from preserved direct-cell host packaging and restorer conventions.', 'Bounded single-member zlib decoding is used by the new standalone restorer; producer recovery is not independent approval.'], inputs_sha256=inputs,
            outputs_sha256={key(p):sha(p) for p in out.rglob('*') if p.is_file()})
        save(out / 'summary.json', summary)
        print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as error:
        save(out / 'failure.json', dict(error=repr(error), source_sha256=sha(Path(__file__)),
             completed_variants=[r['variant'] for r in records], elapsed_seconds=time.monotonic()-start,
             host_originals_not_deleted=True, complete_unsat_proof=False))
        raise


if __name__ == '__main__':
    main()
