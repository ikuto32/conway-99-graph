"""Exact raw25 incidence object checks, independently authored, no producer."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import audit_20260930_triangle_q1_capacity_cnf as prior

ROOT=Path(__file__).resolve().parents[1]
need,digest,key,save=prior.need,prior.digest,prior.key,prior.save
FIXTURE=ROOT/'acceleration/results/20260930_independent_review/one_c2_synthetic_control/fixture.json'
FIXTURE_SHA='bc72a000380c2d950257b77bbbbe345e477a88ed48947a41965f7c1803e16012'

def derive_scope():
    h,g,columns,known,zeros,entries,refs=prior.base.derive()
    _,components=prior.compaudit.components_from_raw(h)
    kept=[e for e in entries if e['row']<25]
    need(len(kept)==650 and [e['id'] for e in kept]==list(range(1,651)),'650 free positions in first25rows')
    return [row[:25] for row in g[:25]],columns,known[:25],kept,refs[:25],components

def validate(c,g,known,components,columns):
    need(type(c) is list and len(c)==25 and all(type(row) is list and len(row)==60 for row in c),'literal25x60 shape')
    need(all(type(x) is int and x in (0,1) for row in c for x in row),'literal integer binary entries')
    need(len(g)==25 and all(len(row)==25 and all(type(x) is int for x in row) for row in g),'integer25x25 Gram')
    need(all(sum(row)==10 for row in c),'all25row margins10')
    need(all(sum(c[r][d] for r in range(f,f+12))==2 for f in [0,12] for d in range(60)),'complete first-two-fibre column margins2')
    if known is not None:
        need(len(known)==25 and all(len(row)==60 for row in known),'known scope dimensions')
        need(all(known[r][d]==-1 or known[r][d]==c[r][d] for r in range(25) for d in range(60)),'every frozen incidence')
    for a in range(25):
        for b in range(25):need(sum(c[a][d]*c[b][d] for d in range(60))==g[a][b],'exact Gram entry '+str((a,b)))
    need(len(components)==3 and sorted(r for group in components for r in group)==list(range(36)),'complete36row component partition')
    component_totals=[[sum(c[r][d] for r in group if r<25) for d in range(60)] for group in components]
    need(all(x<=2 for row in component_totals for x in row),'all180component capacities')
    pair_totals=[]
    for d in range(60):
        for e in range(d+1,60):
            value=sum(c[r][d]*c[r][e] for r in range(25));need(value<=2,'outside-column overlap cap '+str((d,e)));pair_totals.append(value)
    q=prior.extract_q1(c,columns)
    return dict(rows=25,columns=60,integer_Gram_entries=625,row_margins=25,complete_fibre_column_margins=120,component_capacities=180,outside_column_pair_capacities=1770,component_totals=component_totals,column_overlap_histogram={str(v):pair_totals.count(v) for v in range(3)},Q1=q)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    need(digest(FIXTURE)==FIXTURE_SHA,'synthetic fixture identity')
    fixture=json.loads(FIXTURE.read_bytes());c=fixture['incidence_matrix'];own=fixture['own_target_gram'];g,cols,known,entries,refs,components=derive_scope()
    positive=validate(c,own,None,components,cols);difference=sum(own[a][b]!=g[a][b] for a in range(25) for b in range(25));need(difference==26,'synthetic Gram explicitly differs from researchGram')
    rejected=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,IndexError,KeyError):rejected.append(label)
        else:raise ValueError('corrupt raw25 control accepted '+label)
    reject('synthetic_is_not_research_Gram',lambda:validate(c,g,known,components,cols))
    for label in ['binary_value','boolean_value','missing_row','missing_column','selected_C2_bit','wrong_Gram','wrong_partition']:
        bad=deepcopy(c);bg=deepcopy(own);bc=deepcopy(components)
        if label=='binary_value':bad[24][0]=2
        elif label=='boolean_value':bad[24][0]=bool(bad[24][0])
        elif label=='missing_row':bad.pop()
        elif label=='missing_column':bad[24].pop()
        elif label=='selected_C2_bit':bad[24][0]^=1
        elif label=='wrong_Gram':bg[24][0]+=1
        else:bc[0][0]=bc[1][0]
        reject(label,lambda:validate(bad,bg,None,bc,cols))
    # Preserve every row margin and both complete-fibre margins while creating
    # an outside-column pair with three retained common neighbors.
    bad=deepcopy(c);chosen=next((d,e) for d in range(60) for e in range(d+1,60) if sum(c[r][d]*c[r][e] for r in range(24))==2)
    for d in chosen:
        if bad[24][d]==0:
            remove=next(e for e in range(60) if bad[24][e] and e not in chosen);bad[24][remove]=0;bad[24][d]=1
    bg=[[sum(bad[a][d]*bad[b][d] for d in range(60)) for b in range(25)] for a in range(25)]
    need(sum(bad[r][chosen[0]]*bad[r][chosen[1]] for r in range(25))==3,'deliberate column-pair overlap3')
    reject('column_overlap_three_with_own_Gram_and_row_margins',lambda:validate(bad,bg,None,components,cols))
    bindings={key(__file__):digest(__file__),key(FIXTURE):FIXTURE_SHA,key(prior.__file__):digest(prior.__file__),key(prior.base.__file__):digest(prior.base.__file__),key(prior.compaudit.__file__):digest(prior.compaudit.__file__),'uv.lock':digest(ROOT/'uv.lock')}
    report=dict(status='INDEPENDENT_ONE_C2_RAW25_CHECKER_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,synthetic_positive=positive,synthetic_research_Gram_differences=difference,corrupted_controls_rejected=rejected,producer_imports=False,shared_components=['Frozen independently authored rawcore/Gram/component reconstruction and Q1 extraction helpers.'],target_resolution=False,limitations=['Synthetic positive uses its own Gram, not the researchGram.','This calibrates raw objects only; it does not yet approve a new CNF or SAT assignment.'])
    save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
if __name__=='__main__':main()
