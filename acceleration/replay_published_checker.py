"""Run a frozen checker with explicit path relocation and no local data fallback."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
import traceback


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--original-root", required=True)
    parser.add_argument("--checker", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--checker-out", type=Path, required=True)
    parser.add_argument("--run", help="Relative batch input path for fresh16 checker")
    parser.add_argument("--relocate", action="store_true")
    parser.add_argument("--controls-only", action="store_true", help="Call the triangle checker's controls without full enumeration")
    args = parser.parse_args()
    isolated = args.root.resolve()
    output = args.report.resolve()
    checker_output = args.checker_out.resolve()
    for path in (output, checker_output):
        if path.exists():
            raise ValueError("Preserve prior evidence: " + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
    script = (isolated / args.checker).resolve()
    script.relative_to(isolated)
    original = args.original_root.replace("\\", "/").rstrip("/")
    mapped, rejected, reads = {}, [], set()
    def translate(value):
        raw = str(value).replace("\\", "/")
        if ".." in raw.split("/"):
            raise ValueError("Rejected path traversal: " + raw)
        incoming = Path(raw)
        if incoming.is_absolute() and incoming.resolve().is_relative_to(isolated):
            return incoming.resolve()
        if raw.lower().startswith(original.lower() + "/"):
            suffix = raw[len(original)+1:]
            resolved = (isolated / suffix).resolve()
            resolved.relative_to(isolated)
            mapped[raw] = str(resolved)
            return resolved
        path = Path(raw)
        if path.is_absolute() or ":" in raw:
            resolved = path.resolve()
            if not resolved.is_relative_to(isolated):
                raise ValueError("Rejected other absolute root: " + raw)
            return resolved
        resolved = (isolated / path).resolve()
        resolved.relative_to(isolated)
        return resolved
    # Controls precede checking and exercise the exact mapping function.
    mapping_controls = []
    for name, value, accept in (
        ("original_prefix", original + "/uv.lock", True),
        ("isolated_absolute", str(isolated / "uv.lock"), True),
        ("relative", "uv.lock", True),
        ("traversal", original + "/../private.json", False),
        ("other_drive_root", "Z:/private/secret.json", False),
        ("prefix_collision", original + "-other/private.json", False),
    ):
        try:
            translated = translate(value)
            passed = accept and translated == isolated / "uv.lock"
        except ValueError:
            passed = not accept
        if not passed:
            raise ValueError("Path mapping control failed: " + name)
        mapping_controls.append(dict(name=name, expected="ACCEPT" if accept else "REJECT", outcome="PASS"))
    mapped.clear()
    header = dict(timestamp=datetime.now(timezone.utc).isoformat(), command_argv=[sys.executable, *sys.argv],
                  working_directory=str(Path.cwd()), isolated_root=str(isolated), original_root=original,
                  explicit_relocation=args.relocate, source_checker_sha256=digest(script),
                  wrapper_sha256=digest(__file__), uv_lock_sha256=digest(isolated / "uv.lock"),
                  python=platform.python_version(), path_mapping_controls=mapping_controls,
                  limitations=["This is repeated execution of an existing independent checker, not a new mathematical derivation.",
                               "The explicit wrapper changes only path resolution; raw artifacts and frozen checking functions remain byte-identical.",
                               "Standard library and packages under the interpreter installation remain trusted execution dependencies."])
    write_roots = {output, checker_output}
    environment_roots = [Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve()]
    def audit(event, values):
        if event != "open" or not values or not isinstance(values[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(values[0])).resolve()
        if path in write_roots or path.is_relative_to(isolated) or any(path.is_relative_to(base) for base in environment_roots):
            if path.is_relative_to(isolated):
                reads.add(path.relative_to(isolated).as_posix())
            return
        rejected.append(str(path))
        raise PermissionError("Public replay guard rejected access outside Git-only root/environment: " + str(path))
    sys.dont_write_bytecode = True
    sys.addaudithook(audit)
    started = time.monotonic()
    status, error, result = "FAIL", None, None
    try:
        spec = importlib.util.spec_from_file_location("frozen_public_checker", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if args.relocate:
            module.path = translate
        if args.controls_only:
            result = module.controls()
        else:
            argv = [str(script), "--out", str(checker_output)]
            if args.run:
                argv.extend(["--run", args.run])
            sys.argv = argv
            module.main()
            result = json.loads(checker_output.read_bytes())
        status = "PASS"
    except Exception as exc:
        error = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
    # Hash only the already observed isolated input files; the guard remains on.
    input_hashes = {name: digest(isolated / name) for name in sorted(reads) if (isolated / name).is_file()}
    report = dict(**header, outcome=status, error=error, mapped_paths=mapped,
                  rejected_outside_paths=rejected, opened_isolated_inputs_sha256=input_hashes,
                  checker_result_status=result.get("status") if isinstance(result, dict) else None,
                  checker_case_count=len(result.get("records", [])) if isinstance(result, dict) else None,
                  control_results=result if args.controls_only else None,
                  checker_output_sha256=digest(checker_output) if checker_output.exists() else None,
                  elapsed_seconds=time.monotonic()-started, target_resolution=False)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(dict(outcome=status, report=str(output), mapped_paths=len(mapped), rejected_paths=len(rejected), error=error["message"] if error else None, seconds=report["elapsed_seconds"])))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
