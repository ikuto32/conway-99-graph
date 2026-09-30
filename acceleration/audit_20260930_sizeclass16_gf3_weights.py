"""Independent literal-column check of16 GF(3) affine witnesses; no rank audit."""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
from copy import deepcopy
import argparse,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
SUMMARY=B+'sizeclass16_affine_gram_gf3/summary.json'
GATE=B+'independent_review/exact_eight_sizeclass16_cnfs_v2/summary.json'
RAW=B+'hadamard20_support/six_prism.json';CAT=B+'hadamard_triplicate_counts/local_triples.json'
SELECT=B+'exact_eight_sizeclass16_selection/selection.json';FIX=B+'srg243_residual_fixture/triangle_blocks.json'
PINS={SUMMARY:'5cde9a1040684ff6e9b6941cd681feea591f677396b854287830ad889b600419',GATE:'b5e5a90ecc9a52996200e3e8cc4988fd04a85122be22b7355de73678ddcb2b0a',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',CAT:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',SELECT:'9e8bb4c4347cd90d1f6a61f7a6cbdde4bc3a6d86fbb3307cc9015b0b53f20b06',FIX:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def gram(n,columns):
    a=[[0]*n for _ in range(n)]
    for col in columns:
        need(len(col)==len(set(col))and all(type(v)is int and 0<=v<n for v in col),'binary incidence column')
        for i in col:
            for j in col:a[i][j]+=1
    return a
def check_weights(target,groups,weights):
    n=len(target);need(len(groups)==len(weights),'complete group count');total=[[0]*n for _ in range(n)]
    for group,ws in zip(groups,weights,strict=True):
        need(set(ws)==set(group),'exact domain keys');need(all(type(w)is int and w in[0,1,2]for w in ws.values()),'ternary coefficients')
        need(sum(ws.values())%3==1,'affine coefficient normalization')
        for index,w in ws.items():
            if not w:continue
            for col in group[index]:
                for i in col:
                    for j in col:total[i][j]+=w
    need(all(total[i][j]%3==target[i][j]%3 for i in range(n)for j in range(n)),'all literal Gram residues')
    return total
def rejected(name,fn,rows):
    try:fn()
    except ValueError as ex:rows.append(dict(name=name,rejected=True,reason=str(ex)));return
    raise AssertionError('Corruption accepted: '+name)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=(ROOT/args.out).resolve();need(out.is_relative_to(ROOT)and not out.exists(),'new contained output');out.mkdir(parents=True);start=time.monotonic();bindings={}
    try:
        for p,pin in PINS.items():need(h(p)==pin,'input hash '+p);bindings[p]=pin
        for p in[Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:q=p.relative_to(ROOT).as_posix();bindings[q]=h(q)
        summary=read(SUMMARY);gate=read(GATE);selection=read(SELECT);raw=read(RAW);catalog=read(CAT)
        need(gate['status']=='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS','prior exact-domain gate')
        # Calibration uses actual raw binary columns, without producer/checker imports.
        fixture=read(FIX);F=fixture['factor60x180'];n=len(F);m=len(F[0]);need(n==60 and m==180 and all(len(r)==m and all(type(v)is int and v in[0,1]for v in r)for r in F),'genuine fixture shape')
        columns=[[i for i in range(n)if F[i][j]]for j in range(m)];target=gram(n,columns);groups=[{0:columns[j:j+3]}for j in range(0,m,3)];weights=[{0:1}for _ in groups]
        check_weights(target,groups,weights);bad=deepcopy(target);bad[0][0]+=1;controls=[]
        rejected('genuine243_changed_target',lambda:check_weights(bad,groups,weights),controls)
        badweights=deepcopy(weights);badweights[0][0]=2;rejected('genuine243_wrong_affine_sum',lambda:check_weights(target,groups,badweights),controls)
        rejected('genuine243_missing_group',lambda:check_weights(target,groups,weights[:-1]),controls)
        C=raw['core_adjacency'];need(len(C)==36 and all(len(r)==36 for r in C),'literal core36')
        G=[[12*(i==j)-C[i][j]+2-sum(C[i][k]*C[k][j]for k in range(36))-(i//12==j//12)for j in range(36)]for i in range(36)]
        need(G==raw['prescribed_Gram36'],'independent integer Gram construction')
        supports=raw['support_columns'][:20];need(all(raw['support_columns'][g+20*t]==supports[g]for g in range(20)for t in range(3)),'triplicate raw supports')
        words=catalog['words'];triples=catalog['survivors'];need(len(words)==90 and len(triples)==31110,'pinned raw catalogue sizes')
        signatures=defaultdict(list)
        for t,tri in enumerate(triples):
            need(len(tri)==3 and all(type(i)is int and 0<=i<90 for i in tri),'catalogue triple indices')
            sig=tuple(sum(words[w][a]==f for w in tri)for a in range(6)for f in range(3));signatures[sig].append(t)
        results=[];outputhashes={};case_paths=sorted(p for p in summary['outputs_sha256']if Path(p).name.startswith('case_')and p.endswith('.json'))
        need(len(case_paths)==16,'complete16 certificate files')
        for ordinal,p in enumerate(tqdm(case_paths,desc='Independently check literal GF3 weights',mininterval=1)):
            need(h(p)==summary['outputs_sha256'][p],'raw certificate hash');bindings[p]=h(p);case=read(p);profilepath=case['profile_path']
            need(h(profilepath)==case['profile_sha256']==gate['inputs_sha256'][profilepath],'independently approved raw profile');bindings[profilepath]=h(profilepath);profile=read(profilepath)
            need(case['case_id']==selection['ordered_case_ids'][ordinal]==profile['campaign_case_id'],'exact selected case')
            counts=profile['coordinate_group_fibre_counts'];expected=[];gg=[];ww=[]
            for g,support in enumerate(supports):
                sig=tuple(counts[a][g][f]for a in support for f in range(3));ids=signatures[sig];expected.append(ids)
                need(ids==profile['local_survivor_indices_by_group'][g]==case['domain_indices'][g],'complete original domain')
                opts={t:[[12*words[w][a]+coord for a,coord in enumerate(support)]for w in triples[t]]for t in ids}
                gg.append(opts);ws=case['affine_weights'][g];need(all(str(int(k))==k for k in ws),'canonical option keys');ww.append({int(k):v for k,v in ws.items()})
            total=check_weights(G,gg,ww)
            altered=deepcopy(ww);key=next(iter(altered[0]));altered[0][key]=(altered[0][key]+1)%3
            rejected(f'case{ordinal}_changed_coefficient',lambda:check_weights(G,gg,altered),controls)
            missing=deepcopy(ww);del missing[0][key];rejected(f'case{ordinal}_missing_domain_member',lambda:check_weights(G,gg,missing),controls)
            poisoned=deepcopy(G);poisoned[0][0]+=1;rejected(f'case{ordinal}_changed_target',lambda:check_weights(poisoned,gg,ww),controls)
            rr=dict(case_id=case['case_id'],case_index=case['case_index'],profile_sha256=h(profilepath),certificate_sha256=h(p),domain_sizes=[len(x)for x in gg],affine_group_sums=[sum(x.values())%3 for x in ww],exact_integer_weighted_Gram=total,checked_residues=1296,verdict='AFFINE_GF3_WITNESS_VERIFIED',rank_check_performed=False)
            q=out/f'case_{ordinal:02d}.json';save(q,rr);outputhashes[q.relative_to(ROOT).as_posix()]=h(q.relative_to(ROOT));results.append(dict(case_id=case['case_id'],case_index=case['case_index']))
            need(time.monotonic()-start<120,'declared120-second checking allocation')
        q=out/'controls.json';save(q,dict(genuine_fixture_entries=3600,positive='Actual raw60x180 incidence columns grouped into60 triples, unit affine weights.',corruptions=controls));outputhashes[q.relative_to(ROOT).as_posix()]=h(q.relative_to(ROOT))
        now=datetime.now(timezone.utc).isoformat();report=dict(status='INDEPENDENT_SIZECLASS16_GF3_AFFINE_WEIGHTS_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,outputs_sha256=outputhashes,records=results,cases=16,residue_entries=16*1296,affine_normalizations=16*20,corruptions_rejected=len(controls),genuine_fixture_entries=3600,elapsed_seconds=time.monotonic()-start,verifier='/root',method='Independent plain integer sums of actual incidence-column outer products; no producer bit planes, elimination, basis or checking code.',shared_components=['Pinned raw support/catalogue/count profiles and previously independent complete-domain encoding gate.','Python standard library and tqdm; no producer or prior checker imports.'],limitations=['No rank193 or basis-spanning claim is checked.','Only16 specified literal domains; arbitrary GF3 affine weights need not select one option or form an integral factor.','No exclusion, residualD or unrestricted target conclusion.'],target_resolution='UNKNOWN',native_calls=0)
        save(out/'summary.json',report)
        claim=dict(id='C-FIXED-HADAMARD-SIZECLASS16-GF3-AFFINE-GRAM-WITNESSES',revision=1,statement='For each of the16 exact literal count profiles in the frozen sizeclass16 selection, there exist GF(3) weights on every group\'s complete initial local-triple domain whose sum in that group is1 and whose20 weighted local Gram contributions sum to the prescribed36x36 Gram matrix modulo3.',kind='mathematical result',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope='Exactly16 pinned literal fixed-support initial-domain affine relaxations over GF(3); no rank, integral-factor, other-profile or target assertion.',assumptions=['Pinned literal support and complete initial local domains independently checked in the sizeclass16 encoding gate.'],dependencies=[dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SIZECLASS16-GRAM-ENCODINGS',revision=1,relation='uses_result')],verifier='/root',method=report['method'],shared_components=report['shared_components'],limitations=report['limitations'],created_at=now,updated_at=now,inputs_sha256=bindings,independent_report=dict(path=(out/'summary.json').relative_to(ROOT).as_posix(),sha256=h((out/'summary.json').relative_to(ROOT))))
        save(out/'claim_binding.json',claim);print(json.dumps(dict(cases=16,summary_sha256=h((out/'summary.json').relative_to(ROOT)),binding_sha256=h((out/'claim_binding.json').relative_to(ROOT)))))
    except BaseException as ex:
        save(out/'failure.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),error=repr(ex),inputs_sha256=bindings,elapsed_seconds=time.monotonic()-start));raise
if __name__=='__main__':main()
