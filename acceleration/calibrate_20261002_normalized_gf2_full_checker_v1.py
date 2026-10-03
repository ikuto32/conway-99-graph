"""Calibrate exact frozen full-checker tiny controls before full output access.

Extracts only the actual source's tiny control block with Python AST; neither
imports/executes its main nor loads native scientific output. Negative bypass
controls demonstrate that accepting corrupt artifacts vetoes this block.
"""
import argparse
import ast
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from types import SimpleNamespace

from command_deadline import CommandDeadline
import audit_20261002_normalized_gf2_controls_v1 as scalar

ROOT=scalar.ROOT
FULL=ROOT/'acceleration/audit_20261002_normalized_gf2_full_artifact_v1.py'
FULL_SHA='21b96c97ae3482486a021c3c399a4987cb1991035d8bb6be4ee3e60c1a4e0544'
HELPER_SHA='675e393b8ba1cb20b78565b40cb6a478c96dc01e4a6b50de51f5272fb19bc3f0'
PROTOCOL=ROOT/'docs/AUDIT_20261002_NORMALIZED_GF2_FULL_ARTIFACT_PROTOCOL.md'
PROTOCOL_SHA='ad29d3a6f2924f580419116e5ac42ce45bccf8afbe6067f7d5d4c2101f800c37'


def need(ok,message):
    if not ok:raise ValueError(message)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='Extract/execute frozen own-checker2positive4corrupt tinycontrols and2bypassveto controls;60outer40worker,20reserve,no scientific output')
    started=time.monotonic();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(path,wanted=None):
        path=Path(path);need(path.is_file()and path.resolve().is_relative_to(ROOT),'CHECKER_ARTIFACT_PATH')
        need(deadline.status()['remaining_seconds']>10,'not completed within allocated budget')
        value=hashlib.sha256(path.read_bytes()).hexdigest();need(wanted is None or value==wanted,'CHECKER_SOURCE_PIN');pins[scalar.key(path)]=value;return path
    try:
        pin(FULL,FULL_SHA);pin(Path(scalar.__file__),HELPER_SHA);pin(PROTOCOL,PROTOCOL_SHA)
        for path in [Path(__file__),ROOT/'acceleration/command_deadline.py',ROOT/'acceleration/run_compute_command.py',ROOT/'pyproject.toml',ROOT/'uv.lock']:pin(path)
        tree=ast.parse(FULL.read_bytes(),filename=str(FULL));main_node=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='main')
        body=next(node for node in main_node.body if isinstance(node,ast.Try)).body
        def target(node,name):return isinstance(node,ast.Assign)and any(isinstance(item,ast.Name)and item.id==name for item in node.targets)
        begin=next(i for i,node in enumerate(body)if target(node,'tiny'));end=next(i for i,node in enumerate(body)if target(node,'parity_path'))
        selected=body[begin:end];need(len(selected)==13,'EXACT_FROZEN_TINY_BLOCK_SHAPE')
        block=ast.Module(body=selected,type_ignores=[]);ast.fix_missing_locations(block)
        extracted=ast.unparse(block)+'\n';(out/'exact_tiny_block.py.txt').write_text(extracted,encoding='utf8',newline='\n')
        compiled=compile(block,str(FULL),'exec');expected=['tiny_flipped_vector','tiny_changed_RHS','tiny_changed_coefficient','tiny_changed_XORmask']
        def execute(disable=None):
            negatives=[];positives=[]
            def reject(label,call,wanted):
                try:call()
                except ValueError as error:need(str(error)==wanted,'CONTROL_DIAGNOSTIC_STAGE');negatives.append({'label':label,'diagnostic':str(error)})
                else:raise ValueError('CORRUPTED_CONTROL_ACCEPTED '+label)
            def vectors(model,values):
                if disable=='vectors':return None
                scalar.check_vectors(model,values);positives.append({'kind':'raw_integer_scalar_vectors','columns':len(model['variables']),'rows':len(model['equations']),'vectors':len(values)})
            def relation(model,witness):
                if disable=='relation':return None
                result=scalar.check_relation(model,witness);positives.append({'kind':'raw_integer_scalar_relation','columns':len(model['variables']),'rows':len(model['equations']),'mask':result['rhs_mod2_mask']});return result
            namespace={'independent':SimpleNamespace(check_vectors=vectors,check_relation=relation),'json':json,'rejected':reject}
            exec(compiled,namespace,namespace)
            need([record['label']for record in negatives]==expected and len(positives)==2,'EXACT_TINY_CONTROL_COUNTS')
            return positives,negatives
        positives,negatives=execute();bypasses=[]
        for disabled,wanted in [('vectors','CORRUPTED_CONTROL_ACCEPTED tiny_flipped_vector'),('relation','CORRUPTED_CONTROL_ACCEPTED tiny_changed_XORmask')]:
            try:execute(disabled)
            except ValueError as error:need(str(error)==wanted,'BYPASS_CONTROL_STAGE');bypasses.append({'disabled':disabled,'diagnostic':str(error)})
            else:raise ValueError('BYPASSED_CHECKER_ACCEPTED')
        scalar.dump(out/'summary.json',{'status':'INDEPENDENT_NORMALIZED_GF2_FULL_CHECKER_CALIBRATION_V1_PASS','timestamp':datetime.now(timezone.utc).isoformat(),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'cwd':str(ROOT),'python_version':platform.python_version(),
            'verifier':'/root/structural','inputs_sha256':pins,'positive_controls':positives,'corrupted_controls':negatives,'disabled_scalar_checker_vetoes':bypasses,
            'exact_selected_source_lines':[selected[0].lineno,selected[-1].end_lineno],'selected_AST_statement_count':len(selected),
            'extracted_actual_control_source_sha256':hashlib.sha256(extracted.encode('utf8')).hexdigest(),
            'full_solver_output_accessed':False,'native_execution':False,'method':'Execute only exact frozen own-checker tiny AST block with independently authored scalar helper; accepting malformed scalar artifacts fails specific corrupt controls.',
            'shared_trusted_components':['Independent scalar helper675e393b...bc3f0','Python ast/compiler/standard library','command_deadline.py','run_compute_command.py','locked uv environment'],
            'scope':'Checker engineering calibration only. Full mathematical/vector/XOR output has not been inspected or approved.','target_resolution':False,'elapsed_seconds':time.monotonic()-started})
    except BaseException as error:
        scalar.dump(out/'failure.json',{'error':repr(error),'inputs_sha256':pins,'elapsed_seconds':time.monotonic()-started,'outputs_preserved':True,'approval':False});raise


if __name__=='__main__':main()
