"""Complete tiny triangle-pair/code controls; no optimizer or producer imports."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
NOTE='docs/CANDIDATE_20261003_TRIANGLE_INCIDENCE_LOW_WEIGHTS_V1.md'
SPEC='acceleration/theory_20261003_incidence_low_weight_controls_v1_spec.md'
CONTEXT={
 'acceleration/audit_20261003_incidence_griesmer_v1.md':'65d8eea3f4d72eb56391284f95eb43ad021e92a88a41fdcc2fe7a2e10f9dd92d',
 'acceleration/audit_20261003_incidence_code_dual_v1.md':'9fd1522fc60cc001c57e03559ac77582fecee9be75f556a702226a0503376a67',
}

def need(value,stage):
    if not value:raise ValueError(stage)
def sha(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def graph(n,triples):
    result=[[0]*n for _ in range(n)]
    for triple in triples:
        for a,b in combinations(triple,2):result[a][b]=result[b][a]=1
    return result
def validate(g):
    n=len(g)
    need(all(type(row)is list and len(row)==n and all(type(x)is int and x in[0,1]for x in row)for row in g),'LITERAL_GRAPH_DOMAIN')
    need(all(g[v][v]==0 for v in range(n))and all(g[v][w]==g[w][v]for v in range(n)for w in range(n)),'SIMPLE_GRAPH')
    need(all(sum(g[v][u]*g[w][u]for u in range(n))==1 for v,w in combinations(range(n),2)if g[v][w]),'EDGE_UNIQUE_TRIANGLE')
def triangles(g):return [list(t)for t in combinations(range(len(g)),3)if all(g[v][w]for v,w in combinations(t,2))]
def bits(vertices):return sum(1<<v for v in vertices)
def kraw(n,j,w):return sum((-1)**s*math.comb(w,s)*math.comb(n-w,j-s)for s in range(max(0,j-(n-w)),min(j,w)+1))
def exact_bound(g,ts):
    validate(g);need(ts==triangles(g),'COMPLETE_TRIANGLES')
    n=len(g);degree=[sum(v in t for t in ts)for v in range(n)];q=sum(math.comb(t,2)for t in degree);groups={4:defaultdict(list),6:defaultdict(list)};records=[]
    for i,j in combinations(range(len(ts)),2):
        common=sorted(set(ts[i])&set(ts[j]));need(len(common)in[0,1],'TRIANGLE_LINEARITY')
        word=bits(ts[i])^bits(ts[j]);weight=word.bit_count();need(weight==6-2*len(common),'PAIR_WEIGHT')
        support=[v for v in range(n)if word>>v&1]
        if weight==4:
            edges=[list(t)for t in combinations(support,2)if g[t[0]][t[1]]]
            need(len(edges)==2 and len(set(edges[0]+edges[1]))==4,'MEETING_INDUCED_2K2')
            centers=[[v for v in range(n)if g[v][a]and g[v][b]]for a,b in edges]
            need(centers==[common,common],'MEETING_RECOVERY_CENTER')
            recovered=sorted(sorted(edge+common)for edge in edges)
        else:
            recovered=[t for t in triangles(g)if set(t)<=set(support)]
            need(len(recovered)==2,'DISJOINT_RECOVERY_TRIANGLES')
        need(recovered==[ts[i],ts[j]],'PAIR_INVERSE')
        groups[weight][word].append([i,j]);records.append(dict(pair=[i,j],intersection=common,support=support,word=word,weight=weight,recovered_triangles=recovered))
    need(all(len(copies)==1 for group in groups.values()for copies in group.values()),'PAIR_COLLISION')
    counts={3:len(ts),4:q,6:math.comb(len(ts),2)-q}
    need(len(groups[4])==counts[4]and len(groups[6])==counts[6],'PAIR_COUNT')
    return counts,degree,records
def image_kernel(n,ts):
    generators=[bits(t)for t in ts];image={0}
    for t in generators:image|={x^t for x in image}
    kernel=[x for x in range(1<<n)if all((x&t).bit_count()%2==0 for t in generators)]
    dual=[u for u in range(1<<n)if all((x&u).bit_count()%2==0 for x in kernel)]
    need(sorted(image)==dual and len(image)*len(kernel)==1<<n,'FULL_ORTHOGONAL_IMAGE')
    return sorted(image),kernel
def inequality(n,kernel,image,j,nj):
    histogram=Counter(x.bit_count()for x in kernel);m=len(kernel)
    total=sum(count*kraw(n,j,w)for w,count in histogram.items());bj=sum(x.bit_count()==j for x in image)
    need(total==m*bj,'CHARACTER_IDENTITY')
    nonzero=total-math.comb(n,j);rhs=nj*m-math.comb(n,j)
    need(nonzero>=rhs,'SHARP_DUAL_COUNT_INEQUALITY')
    shifted=sum(count*(nj-kraw(n,j,w))for w,count in histogram.items()if w)
    need(shifted<=math.comb(n,j)-nj,'SHIFTED_CONSTANT_INEQUALITY')
    return dict(degree=j,dual_count=bj,lower_count=nj,k_zero=math.comb(n,j),full_sum=total,nonzero_sum=nonzero,sharp_rhs=rhs,shifted_lhs=shifted,shifted_rhs=math.comb(n,j)-nj)
def reject(call,stage):
    try:call()
    except ValueError as error:need(type(error)is ValueError and str(error)==stage,'PRECISE_NEGATIVE_STAGE');return stage
    raise ValueError('NEGATIVE_ACCEPTED')
def fixture(name,n,ts):return dict(label=name,n=n,expected_triangles=sorted(sorted(t)for t in ts),adjacency=graph(n,ts))
FIXTURES=[
 fixture('triangle3',3,[[0,1,2]]),
 fixture('two_disjoint_triangles6',6,[[0,1,2],[3,4,5]]),
 fixture('friendship7',7,[[0,1,2],[0,3,4],[0,5,6]]),
 fixture('loose_cycle8',8,[[0,1,2],[2,3,4],[4,5,6],[0,6,7]]),
 fixture('rook9',9,[[3*r,3*r+1,3*r+2]for r in range(3)]+[[c,c+3,c+6]for c in range(3)]),
]
def collisions(n,ts):
    groups=defaultdict(list)
    for i,j in combinations(range(len(ts)),2):groups[bits(ts[i])^bits(ts[j])].append([i,j])
    return [dict(word=word,support=[v for v in range(n)if word>>v&1],weight=word.bit_count(),pairs=pairs)for word,pairs in sorted(groups.items())if len(pairs)>1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--source-sha256',required=True);ap.add_argument('--note-sha256',required=True);args=ap.parse_args()
    deadline=CommandDeadline(args.seconds,allocation_reason='Five frozen n<=9 graphs and complete ambient/image/kernel words;90outer60worker20internal serialization reserve; no solver/search.');out=args.out.resolve();need(out.is_relative_to(ROOT),'WORKSPACE_OUTPUT');out.mkdir(parents=True,exist_ok=False);pins={};completed=[];negative=[]
    try:
        for name,expected in {Path(__file__).relative_to(ROOT).as_posix():args.source_sha256,NOTE:args.note_sha256,**CONTEXT}.items():pins[name]=sha(ROOT/name);need(pins[name]==expected,'EXACT_INPUT_HASH')
        for name in[SPEC,'acceleration/command_deadline.py','acceleration/run_compute_command.py','docs/COMPUTE_POLICY.md','acceleration/compute_policy.json','pyproject.toml','uv.lock','external_conway99_research/attempts/wave102-prism-incidence-code/derivation.md']:pins[name]=sha(ROOT/name)
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        for f in FIXTURES:
            need(deadline.status()['remaining_seconds']>20,'NOT_COMPLETED_WITHIN_ALLOCATION');g=f['adjacency'];n=f['n'];ts=triangles(g);need(ts==f['expected_triangles'],'FROZEN_FIXTURE_TRIANGLES');counts,degrees,pairs=exact_bound(g,ts);image,kernel=image_kernel(n,ts);ambient=list(range(1<<n));character_checks=0
            for w in range(n+1):
                x=(1<<w)-1
                for j in range(n+1):need(kraw(n,j,w)==sum((-1)**((x&u).bit_count())for u in ambient if u.bit_count()==j),'LITERAL_CHARACTERS');character_checks+=1
            inequalities=[inequality(n,kernel,image,j,counts.get(j,0))for j in range(n+1)]
            raw=dict(**f,triangles=ts,triangle_degrees=degrees,lower_counts=counts,pair_records=pairs,image_words=image,kernel_words=kernel,image_weight_histogram=dict(sorted(Counter(x.bit_count()for x in image).items())),kernel_weight_histogram=dict(sorted(Counter(x.bit_count()for x in kernel).items())),character_inequalities=inequalities,complete_literal_character_checks=character_checks)
            if f['label']=='rook9':need(all(sum(g[v])==4 for v in range(n))and all(sum(g[v][u]*g[w][u]for u in range(n))==(4 if v==w else 1 if g[v][w]else 2)for v in range(n)for w in range(n)),'ROOK9_EXACT_SRG');need(counts=={3:6,4:9,6:6}and len(image)==32 and len(kernel)==16,'ROOK9_FULL_COUNTS')
            save(out/(f['label']+'.json'),raw);completed.append(dict(label=f['label'],vertices=n,triangles=len(ts),meeting_pairs=counts[4],disjoint_pairs=counts[6],image_words=len(image),kernel_words=len(kernel),pair_inverse_checks=len(pairs),character_degrees=n+1,literal_character_checks=character_checks))
            j=3;actual=sum(x.bit_count()==j for x in image);negative.append(dict(case=f['label']+'_overstated_dual_count',diagnostic=reject(lambda:inequality(n,kernel,image,j,actual+1),'SHARP_DUAL_COUNT_INEQUALITY')))
        rook=FIXTURES[-1]['adjacency'];bad=[row[:]for row in rook];bad[0][0]=1;negative.append(dict(case='diagonal',diagnostic=reject(lambda:validate(bad),'SIMPLE_GRAPH')))
        bad=[row[:]for row in rook];bad[0][1]=0;negative.append(dict(case='asymmetry',diagnostic=reject(lambda:validate(bad),'SIMPLE_GRAPH')))
        bad=[row[:]for row in rook];bad[0][1]=True;negative.append(dict(case='bool_entry',diagnostic=reject(lambda:validate(bad),'LITERAL_GRAPH_DOMAIN')))
        bad=[row[:]for row in rook];bad[0][1]=2;negative.append(dict(case='nonbinary_entry',diagnostic=reject(lambda:validate(bad),'LITERAL_GRAPH_DOMAIN')))
        kernel=image_kernel(3,[[0,1,2]])[1];nonzero=sum(kraw(3,3,x.bit_count())for x in kernel if x)
        negative.append(dict(case='omitted_A0_constant',diagnostic=reject(lambda:need(nonzero>=len(kernel),'OMITTED_ZERO_WORD_CONSTANT'),'OMITTED_ZERO_WORD_CONSTANT')))
        pasch=[[0,1,2],[0,3,4],[1,3,5],[2,4,5]];praw=dict(n=6,triples=pasch,adjacency=graph(6,pasch),collisions=collisions(6,pasch));need(all(len(set(a)&set(b))==1 for a,b in combinations(pasch,2))and len(praw['collisions'])==3 and all(c['weight']==4 for c in praw['collisions']),'PASCH_EXPLICIT_LINEAR_COLLISION');negative.append(dict(case='pasch_edge_unique_hypothesis',diagnostic=reject(lambda:validate(praw['adjacency']),'EDGE_UNIQUE_TRIANGLE')));save(out/'pasch_hypothesis_countercontrol.json',praw)
        complete6=[[int(v!=w)for w in range(6)]for v in range(6)];kt=triangles(complete6);kcoll=[c for c in collisions(6,kt)if c['weight']==6];need(len(kcoll)==1 and len(kcoll[0]['pairs'])==10,'K6_DISJOINT_COLLISION');negative.append(dict(case='complete6_edge_unique_hypothesis',diagnostic=reject(lambda:validate(complete6),'EDGE_UNIQUE_TRIANGLE')));save(out/'complete6_hypothesis_countercontrol.json',dict(n=6,adjacency=complete6,triangles=kt,disjoint_collisions=kcoll))
        target=dict(triangles=231,meeting_pairs=99*math.comb(7,2),disjoint_pairs=math.comb(231,2)-99*math.comb(7,2));need(target==dict(triangles=231,meeting_pairs=2079,disjoint_pairs=24486),'TARGET_EXACT_CONSTANTS');target['normalized_denominators']={str(j):math.comb(99,j)-nj for j,nj in[(3,231),(4,2079),(6,24486)]};need(all(x>0 for x in target['normalized_denominators'].values()),'TARGET_POSITIVE_ROW_DENOMINATORS')
        outputs={path.relative_to(ROOT).as_posix():sha(path)for path in sorted(out.iterdir())if path.is_file()}
        report=dict(status='CANDIDATE_TRIANGLE_IMAGE_LOW_WEIGHT_CONTROLS_V1_PASS_PENDING_INDEPENDENT_DERIVATION',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/structural',original_question_author='/root',source_commit=source_commit,source_commit_limitation='New source/note are separately pinned working artifacts; no assertion they occur in this commit.',command=[sys.executable,*sys.argv],cwd=str(ROOT),python_version=platform.python_version(),inputs_sha256=pins,outputs_sha256=outputs,positive_fixtures=completed,strict_negative_controls=negative,target_conditional_counts=target,universal_derivation_status='CANDIDATE pending separate written audit',independent_approval=False,ledger_mutations=0,solver_invocations=0,target_resolution='NONE',limitations=['Finite controls do not establish universal collision recovery.','Pair-generated words give lower bounds, not complete low-weight enumeration of a target image.','All target consequences assume the exact integer SRG identity; no target graph or contradiction.','No rank upper bound, target-wide coverage, optimizer, novelty or external review.'],deadline=deadline.status())
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],positive_fixtures=len(completed),strict_negative_controls=len(negative))))
    except Exception as error:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),exception=type(error).__name__,diagnostic=str(error),inputs_sha256=pins,completed_fixtures=completed,strict_negative_controls=negative,deadline=deadline.status(),target_resolution='NONE',restart='Preserve this source/run; a changed implementation requires new version and applicable controls.'));raise
if __name__=='__main__':main()
