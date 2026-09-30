"""Independent wave24 ledger/binding comparison, with no mutations on import."""
from collections import Counter
from pathlib import Path
import hashlib
from audit_20260930_sixteenth_checkpoint import read_ledger, require

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
REGISTRARS=['base','count','gram','final']
NEW_IDS=['C-FIXED-HADAMARD-'+s for s in [
 'COUNT-SIGNATURE-GRAM-INTERVALS','SEVEN-EXCEPTION-PROFILE0001-GRAM-ENCODING',
 'SEVEN-EXCEPTION-PROFILE0001-EXCLUSION','LOCAL-GRAM-FRECHET-EXTREMA-FORMULA',
 'ARBITRARY-EXCEPTION-COUNT-MASTER-ENCODING','AT-LEAST-SEVEN-COUNT-CSP-WITNESS',
 'COUNT-INTERVAL-ENCODING','EIGHT-EXCEPTION-COUNT-INTERVAL-WITNESS',
 'TWOHUNDREDFIFTEEN-SEVEN-EXCEPTION-GRAM-ENCODINGS','EIGHT-COUNT-PROFILE-GRAM-ENCODING',
 'EIGHT-COUNT-PROFILE-EXCLUSION','EIGHT-COUNT-PROFILE-SEPARATE-GRAM-BLOCK-WITNESSES',
 'TWOHUNDREDFIFTEEN-SEVEN-EXCEPTION-PROFILE-EXCLUSIONS','EXACTLY-SEVEN-UNBALANCED-GROUPS-EXCLUSION',
 'AT-MOST-SEVEN-UNBALANCED-GROUPS-EXCLUSION','EIGHT-COUNT-PROFILE-FIBRE-ORBIT-EXCLUSION',
 'COUNT-MASTER-SIX-PROFILE-CUT-ENCODING','217-AFFINE-GRAM-GF2-NONOBSTRUCTIONS',
 'TWOHUNDREDFIFTEEN-PROOF-TRANSPORT']]

def compare_binding(c,row,audit,artifacts,load,registrar):
    for key in ['id','revision','statement','basis','limitations']:
        require(c[key]==row[key], 'unchanged approved field '+key+' '+c['id'])
    status=row.get('status',row.get('recommendation'))
    require(c['status']==status and c['review_state']=='CLEAR','approved status')
    kind='mathematical result' if row['kind'] in ['finite_check','proposed formula'] else row['kind']
    require(c['kind']==kind,'explicit allowed-kind mapping')
    require(c['scope']==dict(description=row['scope'],unrestricted_target=False,target_resolution='NONE'),'exact limited scope')
    if 'assumptions' in row:require(c['assumptions']==row['assumptions'],'approved assumptions')
    else:
        defaults={'base':'The frozen complete local count classes and135 cells named in this proposed formula.','gram':'The pinned fixed support, exact literal count profiles and within-triplicate column caps specified in the statement.','final':'The precise domains and fixed-support matrices named in the statement and bound independent report.'}
        require(c['assumptions']==[defaults[registrar]],'explicit scope assumptions')
    deps=[]
    for d in row['dependencies']+row.get('verification_dependencies',[]):
        deps.append(dict(id=d.get('id',d.get('claim_id')),revision=d['revision'],relation=d['relation']))
    require(c['dependencies']==deps,'exact approved dependencies')
    for key in ['created_at','updated_at']:
        require(c[key]==row.get(key,row.get(key.removesuffix('_at'))),'approved timestamp '+key)
    require(c['external_source'] is None and c['unknowns']==dict(external_source=row['external_review_null_reason'] if registrar=='count' else 'Internal independent checking; no external peer review asserted.'),'no external-review invention')
    require(c['reproducibility']==dict(manifest=c['evidence'][0]),'replay manifest')
    if registrar=='count':
        evidence_paths=[artifacts[i]['path'] for i in c['evidence']]
        expected=evidence_paths[:2]+[v['path'] for v in row.get('evidence',[])]+[v['report_path'] for v in row['verification_records'] if 'report_path' in v]
        require(evidence_paths==list(dict.fromkeys(expected)),'complete original count evidence')
        require(len(c['verification'])==len(row['verification_records']),'all original count verification records')
        for v,rv in zip(c['verification'],row['verification_records'],strict=True):
            require(rv['claim_id']==c['id'] and rv['claim_revision']==1 and rv['verifier']==row['verifier'] and rv['outcome']=='PASS','count original verdict')
            p=rv.get('report_path',evidence_paths[0]); actual=load(p)
            require(actual['status'].startswith('INDEPENDENT_') and actual['status'].endswith('_PASS'),'original count audit PASS')
            expected=dict(claim_revision=1,verifier=rv['verifier'],method='independent_artifact_check',command_or_audit=p,timestamp=rv['timestamp'],outcome='PASS',scope=rv.get('scope',row['scope']),artifact_hashes={a:artifacts[a]['sha256'] for a in c['evidence']},shared_components=row['trusted_components'],controls=[rv.get('method',row.get('checking_method','Exact derivation and artifact checks are recorded in the bound independent reports.')),'Original verifier records, calibrated controls and exact command arrays preserved without rewriting in the bound claim-binding artifact.'],limitations=row['limitations'])
            require(v==expected,'all count verification fields unchanged')
        return
    require(len(c['verification'])==1 and len(c['evidence'])==2,'summary/binding evidence pair')
    v=c['verification'][0]
    require(v['claim_revision']==1 and v['verifier']==row['verifier'] and v['method']=='independent_artifact_check','independent reviewer identity')
    require(v['command_or_audit']==artifacts[c['evidence'][0]]['path'] and v['timestamp']==audit['timestamp'],'audit identity')
    require(v['outcome']==('FAIL' if status=='REFUTED' else 'PASS'),'revision-specific outcome')
    require(v['scope']==row.get('refutation',row['scope']),'verification scope')
    require(v['artifact_hashes']=={a:artifacts[a]['sha256'] for a in c['evidence']},'all evidence hashes')
    shared=row.get('shared_components',row.get('trusted_components',audit.get('shared_components',audit.get('source_sharing'))))
    require(v['shared_components']==shared and shared,'trusted component disclosure')
    require(v['limitations']==row['limitations'],'audit limitations')
    require(v['controls']==[row.get('method',row.get('checking_method')),'Exact controls and corruption outcomes are preserved in the bound independent report; no solver or proof replay repeated by registrar.'],'controls provenance')

def audit_chain(load,pin,final_hash):
    chain=[];added_all=[];previous=None
    for n in REGISTRARS:
        f=B+'twentyfourth_'+n+'_registration/';r=load(f+'summary.json')
        pin(f+'CLAIMS.before.yaml',r['previous_ledger_sha256']);pin(f+'CLAIMS.after.yaml',r['ledger_sha256'])
        old=read_ledger(ROOT/(f+'CLAIMS.before.yaml'));new=read_ledger(ROOT/(f+'CLAIMS.after.yaml'))
        if previous is not None:require((ROOT/(f+'CLAIMS.before.yaml')).read_bytes()==previous,'contiguous snapshots')
        else:
            pub=load(B+'resume/twentythird_publication_pointer_receipt.json')
            p=B+'resume/claims_at_twentythird_milestone.yaml';pin(p,pub['previous_ledger_sha256']);before=read_ledger(ROOT/p)
            require(before['claims']==old['claims'] and len(old['claims'])==229,'historical claims unchanged at publication')
            require(pub['ledger_sha256']==r['previous_ledger_sha256'] and pub['mathematical_claim_changes']==[] and pub['published_commit']==pub['confirmed_remote_ref'],'publication boundary')
            require(all(before[k]==old[k] for k in before if k not in ['updated_at','artifacts']),'only availability metadata changes')
            a,b=({q['id']:q for q in z['artifacts']} for z in [before,old]);require(a.keys()==b.keys(),'historical artifact IDs')
            changed={i for i in a if a[i]!=b[i]};require(changed==set(pub['new_public_artifact_ids']),'exact publication update set')
            for i in changed:
                require(all(a[i].get(k)==b[i].get(k) for k in set(a[i])|set(b[i]) if k not in ['availability','retrieval','unavailable_reason']),'historical artifact identities')
                require(a[i]['availability']=='LOCAL_ONLY' and b[i]['availability']=='PUBLIC' and pub['published_commit'] in b[i]['retrieval'],'confirmed availability')
        oc,nc=({q['id']:q for q in z['claims']} for z in [old,new]);oa,na=({q['id']:q for q in z['artifacts']} for z in [old,new])
        require(all(nc[k]==v for k,v in oc.items()) and all(na[k]==v for k,v in oa.items()),'unchanged previous records')
        added=[q['id'] for q in new['claims'] if q['id'] not in oc]
        require(added==r['new_claim_ids'] and r['existing_claim_records_unchanged'] and r['existing_artifact_records_unchanged'],'literal additions')
        require(not r['registrar_performs_mathematical_verification'] and r['validation']['valid'] and not r['validation']['errors'],'schema validation only')
        for p,h in r['checked_input_bindings'].items():pin(p,h)
        for cid in added:
            c=nc[cid];ev=[na[i] for i in c['evidence']]
            for a in ev:
                pin(a['path'],a['sha256'])
                retrieval='Exact workspace path. Bound independent reports retain commands, inputs, outputs, controls and original verification records.' if n=='count' else 'Exact workspace path; independent reports bind raw evidence, source, commands and controls.'
                require(a['availability']=='LOCAL_ONLY' and a['retrieval']==retrieval and a['unavailable_reason']=='Twenty-fourth immutable evidence publication not yet confirmed.','honest evidence availability')
            audit=load(ev[0]['path']);rows=load(ev[1]['path']);rows=rows if isinstance(rows,list) else [rows]
            matches=[q for q in rows if q.get('id')==cid];require(len(matches)==1,'unique literal binding')
            require(audit['status'].startswith('INDEPENDENT_') and (audit['status'].endswith('_PASS') or audit['status'].endswith('_COMPLETE')),'authored checking receipt')
            compare_binding(c,matches[0],audit,na,load,n)
        previous=(ROOT/(f+'CLAIMS.after.yaml')).read_bytes();added_all+=added
        chain.append(dict(registrar=n,before=r['previous_ledger_sha256'],after=r['ledger_sha256'],added=added))
    require(added_all==NEW_IDS and hashlib.sha256(previous).hexdigest()==final_hash,'exact nineteen-claim cutoff')
    require(len(new['claims'])==248 and Counter(c['status'] for c in new['claims'])==dict(VERIFIED=244,CANDIDATE=2,REFUTED=2),'final status census')
    for cid in NEW_IDS:
        require(nc[cid]['revision']==1 and nc[cid]['review_state']=='CLEAR','exact revision')
        for dep in nc[cid]['dependencies']:require(nc[dep['id']]['revision']==dep['revision'],'dependency revision')
    return dict(ledger=new,claims=nc,artifacts=na,chain=chain,ledger_bytes=previous)
