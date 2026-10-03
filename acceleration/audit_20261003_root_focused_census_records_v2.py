"""Independent typed raw-record/part/checkpoint auditor; no producer imports."""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import re
import sys
from tqdm import tqdm
from command_deadline import CommandDeadline
import audit_20261003_root_focused_census_core_v1 as K
import audit_20261003_root_focused_core_v2 as S

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/audit_20261003_root_focused_census_records_v2.py'
SPEC = 'acceleration/audit_20261003_root_focused_census_records_v2_spec.md'
IMPLEMENTATION_VERSION = 2
PRODUCER = 'acceleration/census_20261003_root_focused_two_line_v1.py'
PRODUCER_SHA = 'bbc91ed768a07b302e0e417e8c4415925ef6fac01bd14d78051a56b723419017'
PRODUCER_SPEC = 'acceleration/census_20261003_root_focused_two_line_v1_spec.md'
PRODUCER_SPEC_SHA = '9b2fcfc0b330b9183a47c0f3888126ef8dfe8a8dbb4d41366c9adf11006cdcc8'
KERNEL_CAL = 'acceleration/results/20261003_independent_review/root_focused_census_kernel_calibration01/summary.json'
KERNEL_CAL_SHA = '4fe1680ce72f37a6f94f38d7c276978d72fc4584dafb37b2ea2501d8a0c00232'
STATE = 'acceleration/results/20261003_hypergraph_root_focused_pilot01/native/final.state'
STATE_SHA = 'f38346ba0d3367acfc585854587e30bf5748ffe5ede658cd0055f41edd0f0bb3'
MATRIX = 'acceleration/results/20261003_hypergraph_root_focused_pilot01/native/current.adj'
MATRIX_SHA = '3f910d235e38191b5ac47523c22166f1abfc4d1f3ad285b60d4c684392a6670d'
SAVED = 'acceleration/results/20261003_independent_review/root_focused_saved_pilot01/summary.json'
SAVED_SHA = '7b54dfeb4d54c6a0cb99ab18a67bf2a5d0b263290e4a120cebc6d38a0d5af558'
FROZEN = [[15,59,3,11],[18,78,11,62],[22,37,18,11],[57,11,77,15],[61,88,11,12],[82,11,23,96],[154,11,93,46]]
SCHEMA = 'FROZEN_ROOT_TWO_LINE_LABELLED_PROPOSAL_V1'
FIELDS = {'schema','proposal_id','i','j','ix','jy','old_triples','new_triples','valid','invalid_reason','conflict_pair','toggles','delta_lambda','delta_mu','new_lambda','new_mu','new_root_residual','root_residual_delta','frozen_root_unchanged','mu_direction','classification'}
NUMBERS = ['proposal_id','i','j','ix','jy']
SCORE_FIELDS = ['delta_lambda','delta_mu','new_lambda','new_mu','new_root_residual','root_residual_delta']
HEX = re.compile(r'[0-9a-f]{64}\Z')
DEC = re.compile(r'0|[1-9][0-9]*\Z')


def need(ok,stage,message):
    K.require(ok,stage,message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def save(path,value):
    with path.open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')


def literal_equal(left,right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(literal_equal(left[k],right[k]) for k in left)
    if type(left) in (list,tuple):
        return len(left) == len(right) and all(literal_equal(a,b) for a,b in zip(left,right))
    return left == right


def expected_record(base,pid,universe):
    need(type(pid) is int and 0<=pid<len(universe),'LABEL','literal bounded proposal ID')
    indices = universe[pid]
    i,j,pi,pj = indices
    checked = K.evaluate(base,indices)
    record = dict(schema=SCHEMA,proposal_id=pid,i=i,j=j,ix=pi,jy=pj,
                  old_triples=checked['old_triples'],new_triples=None,valid=False,
                  invalid_reason='selected_point_not_exclusive',conflict_pair=None,toggles=None,
                  delta_lambda=None,delta_mu=None,new_lambda=None,new_mu=None,
                  new_root_residual=None,root_residual_delta=None,frozen_root_unchanged=None,
                  mu_direction=None,classification='invalid_selection')
    if not checked['selected_points_exclusive']:
        return record
    record['new_triples'] = checked['proposed_triples']
    if not checked['admissible']:
        # Preserve the declared selected-edge traversal's first conflict. This
        # serialization order is shared format semantics, not the scorer.
        first,second = checked['old_triples']
        x,y = first[pi],second[pj]
        other_first = [v for at,v in enumerate(first) if at!=pi]
        other_second = [v for at,v in enumerate(second) if at!=pj]
        old = {tuple(sorted(pair)) for row in [first,second] for pair in combinations(row,2)}
        new_selected = [tuple(sorted((y,v))) for v in other_first]+[tuple(sorted((x,v))) for v in other_second]
        seen = set()
        for u,v in new_selected:
            if ((base['bits'][u]>>v)&1 and (u,v) not in old) or (u,v) in seen:
                record['conflict_pair'] = [u,v]
                break
            seen.add((u,v))
        need(record['conflict_pair'] is not None,'RECORD','independent first-conflict derivation')
        record.update(invalid_reason='new_pair_already_present',classification='invalid_linearity')
        return record
    old = {tuple(sorted(pair)) for row in checked['old_triples'] for pair in combinations(row,2)}
    new = {tuple(sorted(pair)) for row in checked['proposed_triples'] for pair in combinations(row,2)}
    root_delta = checked['delta_root']
    direction = 'down' if checked['delta_mu']<0 else 'up' if checked['delta_mu']>0 else 'equal'
    classification = 'valid_lambda_changed' if checked['delta_lambda'] else 'valid_lambda_preserving_root_'+('down' if root_delta<0 else 'up' if root_delta>0 else 'equal')
    record.update(valid=True,invalid_reason=None,toggles=[list(pair) for pair in sorted(old^new)],
                  delta_lambda=checked['delta_lambda'],delta_mu=checked['delta_mu'],
                  new_lambda=checked['lambda_energy'],new_mu=checked['mu_energy'],
                  new_root_residual=checked['root_residual'],root_residual_delta=root_delta,
                  frozen_root_unchanged=True,mu_direction=direction,classification=classification)
    return record


def check_record(raw,expected):
    need(type(raw) is dict and raw.keys()==FIELDS,'RECORD_TYPE','exact21field record')
    need(all(type(raw[k]) is int for k in NUMBERS) and type(raw['valid']) is bool,
         'RECORD_TYPE','literal label integers and validity bool')
    need(raw['schema']==SCHEMA,'RECORD_TYPE','exact record schema')
    if raw['valid']:
        need(all(type(raw[k]) is int for k in SCORE_FIELDS) and raw['frozen_root_unchanged'] is True,
             'RECORD_TYPE','literal valid score integers and frozen true')
    else:
        need(all(raw[k] is None for k in SCORE_FIELDS+['toggles','frozen_root_unchanged','mu_direction']),
             'RECORD_TYPE','invalid scores flags and toggles null')
    need(literal_equal(raw,expected),'RECORD_VALUE','complete independently derived record')


def aggregate(records):
    counts=Counter(r['classification'] for r in records)
    valid=[r for r in records if r['valid']]
    preserving=[r for r in valid if r['delta_lambda']==0]
    neutral=[r for r in preserving if r['root_residual_delta']==0]
    def minimum(rows,key):
        if not rows:
            return None,[]
        value=min(r[key] for r in rows)
        return value,[r['proposal_id'] for r in rows if r[key]==value]
    root,best=minimum(preserving,'new_root_residual')
    mu,mu_best=minimum(preserving,'new_mu')
    neutral_mu,neutral_best=minimum(neutral,'new_mu')
    unique=lambda rows:len({tuple(tuple(p) for p in r['toggles']) for r in rows})
    return dict(counts=dict(sorted(counts.items())),lambda_preserving_mu_directions=dict(sorted(Counter(r['mu_direction'] for r in preserving).items())),
                unique_valid_neighbor_graphs=unique(valid),unique_lambda_preserving_graphs=unique(preserving),
                unique_root_neutral_lambda_preserving_graphs=unique(neutral),best_root_residual=root,best_root_proposal_ids=best,
                minimum_mu=mu,minimum_mu_proposal_ids=mu_best,root_neutral_minimum_mu=neutral_mu,
                root_neutral_minimum_mu_proposal_ids=neutral_best,zero_score_proposal_ids=[r['proposal_id'] for r in valid if r['new_lambda']==r['new_mu']==0])


def read_part(part,pin):
    need(type(part) is dict and set(part)=={'path','start','end','record_count','raw_bytes','raw_sha256','gzip_bytes','gzip_sha256'},'PART_TYPE','exact part descriptor')
    need(all(type(part[k]) is int and part[k]>=0 for k in ['start','end','record_count','raw_bytes','gzip_bytes'])
         and part['end']==part['start']+part['record_count'],'PART_TYPE','literal contiguous part dimensions')
    path=(ROOT/part['path']).resolve()
    need(path.is_relative_to(ROOT) and path.is_file(),'PART_PATH','workspace existing part')
    need(path.stat().st_size==part['gzip_bytes'],'PART_HASH','compressed byte count')
    pin(part['path'],part['gzip_sha256'])
    records=[];raw_hash=hashlib.sha256();raw_bytes=0
    with gzip.open(path,'rb') as stream:
        while True:
            line=stream.readline(4097)
            if not line:
                break
            need(len(line)<=4096 and line.endswith(b'\n'),'PART_LENGTH','bounded complete raw line')
            raw_bytes+=len(line)
            need(raw_bytes<=4096*part['record_count'],'PART_LENGTH','bounded raw population')
            raw_hash.update(line)
            def no_duplicates(pairs):
                result={}
                for key,value in pairs:
                    need(key not in result,'PART_JSON','duplicate JSON key')
                    result[key]=value
                return result
            try:
                record=json.loads(line,object_pairs_hook=no_duplicates)
            except json.JSONDecodeError as error:
                raise K.CensusError('PART_JSON','raw JSON syntax') from error
            need(line==(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode(),
                 'PART_JSON','canonical raw JSON bytes')
            records.append(record)
    need(raw_bytes==part['raw_bytes'] and raw_hash.hexdigest()==part['raw_sha256'] and len(records)==part['record_count'],
         'PART_HASH','complete raw part identity')
    need([r.get('proposal_id') for r in records]==list(range(part['start'],part['end'])),
         'PART_SEQUENCE','complete ordered raw IDs')
    return records


def topology(raw):
    try:
        lines=raw.decode('ascii').splitlines()
    except UnicodeError as error:
        raise K.CensusError('TOPOLOGY','ASCII projection') from error
    need(lines and lines[0]=='ROOT_FOCUSED_ANNEAL_STATE_V1' and lines[-1]=='END','TOPOLOGY','exact wrapper')
    positions={}
    for at,line in enumerate(lines):
        key=line.split(' ',1)[0]
        if key in ['objective','lambda_weight','move_kernel','distribution','n','degree','root','frozen','mutable','current','best_root']:
            need(key not in positions,'TOPOLOGY','unique labelled header')
            positions[key]=at
    def tokens(key):
        need(key in positions,'TOPOLOGY','complete labelled headers')
        return lines[positions[key]].split()
    def number(key):
        fields=tokens(key)
        need(len(fields)==2 and DEC.fullmatch(fields[1]) is not None,'TOPOLOGY','canonical header integer')
        return int(fields[1])
    declared={'objective':S.OBJECTIVE,'lambda_weight':'60','move_kernel':S.KERNEL,'distribution':S.DISTRIBUTION}
    need(all(tokens(k)==[k,v] for k,v in declared.items()),'TOPOLOGY','exact declared native scope')
    n,d,root=number('n'),number('degree'),number('root')
    nf,nc=number('frozen'),number('current')
    need(positions['mutable']==positions['frozen']+nf+1 and positions['current']==positions['mutable']+1
         and positions['best_root']==positions['current']+nc+1,'TOPOLOGY','contiguous row sections')
    def rows(at,count,width):
        result=[]
        for line in lines[at:at+count]:
            fields=line.split()
            need(len(fields)==width and all(DEC.fullmatch(v) is not None for v in fields),'TOPOLOGY','canonical literal row')
            result.append([int(v) for v in fields])
        need(len(result)==count,'TOPOLOGY','complete rows')
        return result
    triples=rows(positions['current']+1,nc,3)
    frozen=rows(positions['frozen']+1,nf,4)
    fields=tokens('mutable')
    need(len(fields)>=2 and all(DEC.fullmatch(v) is not None for v in fields[1:]) and int(fields[1])==len(fields)-2,
         'TOPOLOGY','mutable labelled count')
    mutable=list(map(int,fields[2:]))
    base=K.from_triples(triples,n,d,root)
    need(frozen==base['frozen'] and mutable==base['mutable'],'TOPOLOGY_REFERENCE','exact incident rows and mutable complement')
    return base


def full_checkpoint_population(manifest,path):
    ends=list(range(5000,224784,5000))+[224784]
    starts=[0]+ends[:-1]
    expected_parts=[dict(path=(path.parent/('part_'+str(start).zfill(9)+'.jsonl.gz')).relative_to(ROOT).as_posix(),
                         start=start,end=end,record_count=end-start) for start,end in zip(starts,ends)]
    actual_parts=[{key:part[key] for key in ['path','start','end','record_count']} for part in manifest['parts']]
    need(literal_equal(actual_parts,expected_parts) and manifest['starting_proposal_id']==0
         and type(manifest['starting_proposal_id']) is int and manifest['proposals_evaluated_this_invocation']==224784,
         'COVERAGE','all45fixed target parts from one complete invocation')
    expected_paths=[(path.parent/('checkpoint_'+str(end).zfill(9)+'.json')).relative_to(ROOT).as_posix() for end in ends]
    need([descriptor['path'] for descriptor in manifest['checkpoints']]==expected_paths,
         'COVERAGE','all45actual generated target checkpoints')


def check_manifest(path,base,pin,deadline,cache=None,audit_out=None):
    pin(path.relative_to(ROOT).as_posix())
    manifest=json.loads(path.read_bytes())
    universe=K.labelled_universe(base)
    total=len(universe);completed=manifest['completed_proposals']
    need(manifest['schema']=='FROZEN_ROOT_TWO_LINE_CENSUS_MANIFEST_V1' and type(completed) is int
         and 0<=completed<=total and type(manifest['population']) is int and manifest['population']==total,
         'MANIFEST','exact declared labelled population')
    need(literal_equal(manifest['baseline'],dict(lambda_energy=base['lambda_energy'],mu_energy=base['mu_energy'],root=base['root'],root_residual=base['root_residual'],frozen_rows=base['frozen'],mutable_labels=base['mutable'])),
         'MANIFEST','independent exact baseline')
    need(all(type(manifest[key]) is int for key in ['starting_proposal_id','proposals_evaluated_this_invocation'])
         and 0<=manifest['starting_proposal_id']<=completed
         and manifest['proposals_evaluated_this_invocation']==completed-manifest['starting_proposal_id'],
         'MANIFEST','literal invocation prefix counts')
    identity=manifest['identity']
    need(literal_equal({key:identity[key] for key in ['n','degree','root','total','frozen_rows','mutable_labels']},
                      dict(n=base['n'],degree=base['degree'],root=base['root'],total=total,frozen_rows=base['frozen'],mutable_labels=base['mutable'])),
         'MANIFEST','exact raw domain identity')
    for name,wanted in identity['software'].items():
        pin(name,wanted)
    need(manifest['independent_approval'] is False and manifest['target_resolution'] is False,'MANIFEST','producer pending scope')
    expected=[];all_raw=[];end=0
    bar=tqdm(total=completed,desc='Independent literal census rows',unit='record',mininterval=1,disable=base['n']<99)
    for part in manifest['parts']:
        need(deadline.status()['remaining_seconds']>20,'DEADLINE','checking serialization reserve')
        need(part['start']==end,'PART_SEQUENCE','gap-free manifest coverage')
        raw=read_part(part,pin)
        for record in raw:
            pid=record['proposal_id']
            wanted=cache[pid] if cache is not None and pid in cache else expected_record(base,pid,universe)
            if cache is not None:
                cache[pid]=wanted
            check_record(record,wanted)
            expected.append(wanted)
            bar.update(1)
        all_raw.extend(raw);end=part['end']
        if audit_out is not None:
            save(audit_out/('checked_prefix_'+str(end)+'.json'),dict(status='UNKNOWN_PREFIX_CHECKED_NO_COMPLETE_CENSUS_CLAIM',
                 checked_proposal_records=end,raw_part_sha256=part['raw_sha256'],gzip_part_sha256=part['gzip_sha256'],
                 input_matrix_sha256=MATRIX_SHA,deadline=deadline.status()))
    bar.close()
    need(end==completed and len(expected)==completed,'PART_SEQUENCE','complete prefix population')
    want=aggregate(expected)
    need(literal_equal(manifest['aggregate'],want),'AGGREGATE','all labels counts minima ties and graph identities')
    need(manifest['status']==('CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK' if completed==total else 'UNKNOWN_PREFIX_ONLY'),
         'MANIFEST','complete versus prefix status')
    for descriptor in manifest['checkpoints']:
        pin(descriptor['path'],descriptor['sha256'])
        cp=json.loads((ROOT/descriptor['path']).read_bytes())
        upto=cp['next_proposal_id']
        need(type(upto) is int and 0<=upto<=completed and cp['schema']=='FROZEN_ROOT_TWO_LINE_CENSUS_CHECKPOINT_V1'
             and literal_equal(cp['identity'],manifest['identity']),'CHECKPOINT','exact source/input/prefix identity')
        matching=[part for part in manifest['parts'] if part['end']<=upto]
        need(literal_equal(cp['parts'],matching) and (matching[-1]['end'] if matching else 0)==upto
             and literal_equal(cp['aggregate'],aggregate(expected[:upto])),'CHECKPOINT','all prefix part and aggregate coverage')
    directory=path.parent
    for filename,ids in [('best_root_ties.json',want['best_root_proposal_ids']),('minimum_mu_ties.json',want['minimum_mu_proposal_ids']),
                         ('root_neutral_minimum_mu_ties.json',want['root_neutral_minimum_mu_proposal_ids'])]:
        member=(directory/filename).relative_to(ROOT).as_posix();pin(member)
        saved=json.loads((ROOT/member).read_bytes())
        need(literal_equal(saved['records'],[expected[pid] for pid in ids]),'TIES','complete literal tie population')
    selected=min((expected[pid] for pid in want['best_root_proposal_ids']),key=lambda r:(r['new_mu'],r['proposal_id']),default=None)
    need(literal_equal(manifest['selected_proposal_id'],None if selected is None else selected['proposal_id']),'SELECTED','lex R mu ID selection')
    selected_scalar=None;all_tie_scalars=[]
    if base['n']<99:
        all_tie_ids=sorted(set(want['best_root_proposal_ids']+want['minimum_mu_proposal_ids']+want['root_neutral_minimum_mu_proposal_ids']))
        for pid in all_tie_ids:
            evaluated=K.evaluate(base,universe[pid]);scalar=S.scalar_matrix(K.matrix_bytes(evaluated['candidate_bits']),base['n'],base['degree'],base['root'])
            need((scalar['lambda_energy'],scalar['mu_energy'],scalar['root_residual'])
                 ==(expected[pid]['new_lambda'],expected[pid]['new_mu'],expected[pid]['new_root_residual']),
                 'TIES','independent full scalar every tiny tie')
            all_tie_scalars.append(dict(proposal_id=pid,scalar=scalar))
    if selected is not None:
        candidate=K.evaluate(base,universe[selected['proposal_id']]);rows=K.reconstruct_triples(base,candidate)
        matrix_member=(directory/'best_root_neighbor.adj').relative_to(ROOT).as_posix();pin(matrix_member)
        need((ROOT/matrix_member).read_bytes()==K.matrix_bytes(candidate['candidate_bits']),'SELECTED','entire selected raw adjacency')
        triples_member=(directory/'best_root_neighbor_triples.json').relative_to(ROOT).as_posix();pin(triples_member)
        saved=json.loads((ROOT/triples_member).read_bytes())
        need(literal_equal(saved,dict(n=base['n'],degree=base['degree'],root=base['root'],frozen_rows=base['frozen'],mutable_labels=base['mutable'],triples=rows,proposal_id=selected['proposal_id'])),
             'SELECTED','entire ordered triples and original frozen rows')
        selected_scalar=S.scalar_matrix((ROOT/matrix_member).read_bytes(),base['n'],base['degree'],base['root'])
        need((selected_scalar['lambda_energy'],selected_scalar['mu_energy'],selected_scalar['root_residual'])
             ==(selected['new_lambda'],selected['new_mu'],selected['new_root_residual']),'SELECTED','separate full scalar selected scores')
    return dict(completed=completed,population=total,aggregate=want,selected_proposal_id=manifest['selected_proposal_id'],
                selected_scalar=selected_scalar,all_tiny_tie_scalars=all_tie_scalars),expected


def calibration(out,pin,deadline):
    rows=[[3*r+c for c in range(3)] for r in range(3)]+[[3*r+c for r in range(3)] for c in range(3)]
    base=K.from_triples(rows,9,2,0);universe=K.labelled_universe(base)
    expected=[expected_record(base,pid,universe) for pid in range(len(universe))]
    for record in expected:
        check_record(copy.deepcopy(record),record)
    records=[]
    def reject(name,callback,stage,message):
        try:
            callback()
        except K.CensusError as error:
            need(error.stage==stage and str(error)==stage+': '+message,'CALIBRATION','precise negative '+name)
            records.append(dict(name=name,stage=stage,diagnostic=message,outcome='REJECTED'))
            return
        except BaseException as error:
            raise AssertionError('Wrong-stage '+name+': '+repr(error)) from error
        raise AssertionError('Accepted '+name)
    valid=next(r for r in expected if r['valid']);invalid=next(r for r in expected if not r['valid'])
    for field in NUMBERS:
        raw=copy.deepcopy(valid);raw[field]=float(raw[field])
        reject('float_'+field,lambda raw=raw:check_record(raw,valid),'RECORD_TYPE','literal label integers and validity bool')
    for field in SCORE_FIELDS:
        raw=copy.deepcopy(valid);raw[field]+=1
        reject('wrong_'+field,lambda raw=raw:check_record(raw,valid),'RECORD_VALUE','complete independently derived record')
    for field,value in [('frozen_root_unchanged',False),('new_mu',True),('new_root_residual',10.0)]:
        raw=copy.deepcopy(valid);raw[field]=value
        reject('literal_'+field,lambda raw=raw:check_record(raw,valid),'RECORD_TYPE','literal valid score integers and frozen true')
    for field,value in [('old_triples',valid['new_triples']),('new_triples',valid['old_triples']),('toggles',[]),('classification','valid_lambda_preserving_root_down'),('mu_direction','wrong')]:
        raw=copy.deepcopy(valid);raw[field]=value
        reject('value_'+field,lambda raw=raw:check_record(raw,valid),'RECORD_VALUE','complete independently derived record')
    raw=copy.deepcopy(invalid);raw['new_mu']=0
    reject('invalid_score',lambda:check_record(raw,invalid),'RECORD_TYPE','invalid scores flags and toggles null')
    raw=copy.deepcopy(valid);raw['extra']=0
    reject('extra_field',lambda:check_record(raw,valid),'RECORD_TYPE','exact21field record')
    raw=copy.deepcopy(valid);raw['schema']='OLD'
    reject('wrong_schema',lambda:check_record(raw,valid),'RECORD_TYPE','exact record schema')
    reject('bool_pid',lambda:expected_record(base,True,universe),'LABEL','literal bounded proposal ID')
    # A complete synthetic compressed raw stream is generated solely by the
    # independent checker, including its declared invalid and valid rows.
    raw=b''.join((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode() for r in expected)
    path=out/'positive.jsonl.gz'
    with path.open('xb') as file:
        with gzip.GzipFile(filename='',fileobj=file,mode='wb',mtime=0) as stream:
            stream.write(raw)
    part=dict(path=path.relative_to(ROOT).as_posix(),start=0,end=54,record_count=54,raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest(),gzip_bytes=path.stat().st_size,gzip_sha256=sha(path))
    need(literal_equal(read_part(part,pin),expected),'CALIBRATION','complete synthetic raw stream')
    bad=copy.deepcopy(part);bad['start']=1
    reject('part_dimensions',lambda:read_part(bad,pin),'PART_TYPE','literal contiguous part dimensions')
    bad=copy.deepcopy(part);bad['gzip_bytes']+=1
    reject('gzip_count',lambda:read_part(bad,pin),'PART_HASH','compressed byte count')
    bad=copy.deepcopy(part);bad['raw_sha256']='0'*64
    reject('raw_hash',lambda:read_part(bad,pin),'PART_HASH','complete raw part identity')
    synthetic=out/'synthetic_manifest';synthetic.mkdir()
    summary=aggregate(expected)
    identity=dict(n=9,degree=2,root=0,total=54,frozen_rows=base['frozen'],mutable_labels=base['mutable'],
                  software={PRODUCER:PRODUCER_SHA,PRODUCER_SPEC:PRODUCER_SPEC_SHA})
    checkpoint=dict(schema='FROZEN_ROOT_TWO_LINE_CENSUS_CHECKPOINT_V1',identity=identity,next_proposal_id=54,parts=[part],aggregate=summary)
    save(synthetic/'checkpoint.json',checkpoint)
    for filename,key in [('best_root_ties.json','best_root_proposal_ids'),('minimum_mu_ties.json','minimum_mu_proposal_ids'),
                         ('root_neutral_minimum_mu_ties.json','root_neutral_minimum_mu_proposal_ids')]:
        save(synthetic/filename,dict(records=[expected[pid] for pid in summary[key]],scope='Synthetic independent calibration fixture'))
    selected=min((expected[pid] for pid in summary['best_root_proposal_ids']),key=lambda r:(r['new_mu'],r['proposal_id']),default=None)
    need(selected is not None,'CALIBRATION','synthetic positive selected proposal')
    evaluated=K.evaluate(base,universe[selected['proposal_id']])
    (synthetic/'best_root_neighbor.adj').write_bytes(K.matrix_bytes(evaluated['candidate_bits']))
    save(synthetic/'best_root_neighbor_triples.json',dict(n=9,degree=2,root=0,frozen_rows=base['frozen'],mutable_labels=base['mutable'],
                                                        triples=K.reconstruct_triples(base,evaluated),proposal_id=selected['proposal_id']))
    manifest=dict(schema='FROZEN_ROOT_TWO_LINE_CENSUS_MANIFEST_V1',identity=identity,population=54,completed_proposals=54,
                  status='CANDIDATE_COMPLETE_PENDING_INDEPENDENT_CHECK',parts=[part],
                  checkpoints=[dict(path=(synthetic/'checkpoint.json').relative_to(ROOT).as_posix(),sha256=sha(synthetic/'checkpoint.json'))],
                  aggregate=summary,baseline=dict(lambda_energy=base['lambda_energy'],mu_energy=base['mu_energy'],root=0,root_residual=base['root_residual'],
                                                 frozen_rows=base['frozen'],mutable_labels=base['mutable']),
                  starting_proposal_id=0,proposals_evaluated_this_invocation=54,selected_proposal_id=selected['proposal_id'],independent_approval=False,target_resolution=False)
    save(synthetic/'manifest.json',manifest)
    synthetic_audit,_=check_manifest(synthetic/'manifest.json',base,pin,deadline)
    def mutated_manifest(name,mutation,stage,message,member_mutation=None):
        directory=out/name;directory.mkdir()
        for filename in ['best_root_ties.json','minimum_mu_ties.json','root_neutral_minimum_mu_ties.json','best_root_neighbor.adj','best_root_neighbor_triples.json']:
            (directory/filename).write_bytes((synthetic/filename).read_bytes())
        bad=copy.deepcopy(manifest);mutation(bad)
        if member_mutation:
            member_mutation(directory,bad)
        save(directory/'manifest.json',bad)
        reject(name,lambda:check_manifest(directory/'manifest.json',base,pin,deadline),stage,message)
    mutated_manifest('float_population',lambda value:value.update(population=54.0),'MANIFEST','exact declared labelled population')
    mutated_manifest('bool_baseline_root',lambda value:value['baseline'].update(root=False),'MANIFEST','independent exact baseline')
    mutated_manifest('dropped_part',lambda value:value.update(parts=[]),'PART_SEQUENCE','complete prefix population')
    mutated_manifest('wrong_aggregate',lambda value:value['aggregate'].update(unique_valid_neighbor_graphs=999),
                     'AGGREGATE','all labels counts minima ties and graph identities')
    mutated_manifest('float_selected_id',lambda value:value.update(selected_proposal_id=float(value['selected_proposal_id'])),
                     'SELECTED','lex R mu ID selection')
    def corrupt_checkpoint(directory,value):
        cp=copy.deepcopy(checkpoint);cp['aggregate']['unique_valid_neighbor_graphs']+=1
        save(directory/'bad_checkpoint.json',cp)
        value['checkpoints']=[dict(path=(directory/'bad_checkpoint.json').relative_to(ROOT).as_posix(),sha256=sha(directory/'bad_checkpoint.json'))]
    mutated_manifest('checkpoint_aggregate',lambda value:None,'CHECKPOINT','all prefix part and aggregate coverage',corrupt_checkpoint)
    def corrupt_ties(directory,value):
        member=directory/'best_root_ties.json';member.unlink()
        save(member,dict(records=[],scope='Deliberately missing saved minimum tie records'))
    mutated_manifest('missing_tie',lambda value:None,'TIES','complete literal tie population',corrupt_ties)
    def corrupt_selected_matrix(directory,value):
        member=directory/'best_root_neighbor.adj';raw=bytearray(member.read_bytes());raw[2]=ord('1') if raw[2]==ord('0') else ord('0')
        member.write_bytes(bytes(raw))
    mutated_manifest('selected_matrix',lambda value:None,'SELECTED','entire selected raw adjacency',corrupt_selected_matrix)
    wrong_stage=False
    try:
        reject('wrong_stage_harness',lambda:need(False,'OTHER','wrong'),'LABEL','literal bounded proposal ID')
    except K.CensusError as error:
        wrong_stage=error.stage=='CALIBRATION' and str(error)=='CALIBRATION: precise negative wrong_stage_harness'
    need(wrong_stage,'CALIBRATION','wrong-stage rejection harness must fail')
    records.append(dict(name='wrong_stage_harness',outcome='WRONG_STAGE_REJECTED'))
    target_path=out/'synthetic_target_metadata'/'manifest.json'
    ends=list(range(5000,224784,5000))+[224784];starts=[0]+ends[:-1]
    target_metadata=dict(starting_proposal_id=0,proposals_evaluated_this_invocation=224784,
        parts=[dict(path=(target_path.parent/('part_'+str(start).zfill(9)+'.jsonl.gz')).relative_to(ROOT).as_posix(),
                    start=start,end=end,record_count=end-start) for start,end in zip(starts,ends)],
        checkpoints=[dict(path=(target_path.parent/('checkpoint_'+str(end).zfill(9)+'.json')).relative_to(ROOT).as_posix()) for end in ends])
    full_checkpoint_population(target_metadata,target_path)
    omitted=copy.deepcopy(target_metadata);omitted['checkpoints'].pop(17)
    reject('omitted_generated_target_checkpoint',lambda:full_checkpoint_population(omitted,target_path),
           'COVERAGE','all45actual generated target checkpoints')
    reordered=copy.deepcopy(target_metadata);reordered['checkpoints'][0],reordered['checkpoints'][1]=reordered['checkpoints'][1],reordered['checkpoints'][0]
    reject('reordered_generated_target_checkpoint',lambda:full_checkpoint_population(reordered,target_path),
           'COVERAGE','all45actual generated target checkpoints')
    wrong_part=copy.deepcopy(target_metadata);wrong_part['parts'][-1]['record_count']+=1
    reject('wrong_target_final_part',lambda:full_checkpoint_population(wrong_part,target_path),
           'COVERAGE','all45fixed target parts from one complete invocation')
    save(out/'synthetic_complete_target_checkpoint_metadata.json',target_metadata)
    save(out/'strict_controls.json',records)
    save(out/'synthetic_records.json',expected)
    return dict(positive_record_checks=54,positive_complete_parts=1,positive_complete_manifests=1,
                positive_complete_target_metadata_populations=1,synthetic_all_tie_scalar_matrices=len(synthetic_audit['all_tiny_tie_scalars']),strict_negative_controls=len(records),producer_outputs_checked=False,
                strict_controls_sha256=sha(out/'strict_controls.json'),kernel_calibration_sha256=KERNEL_CAL_SHA)


def controls(out,pin,deadline,args):
    need(args.supervisor and args.supervisor_sha256,'ACTUAL','explicit producer-controls terminal receipt')
    pin(args.supervisor,args.supervisor_sha256)
    supervisor=json.loads((ROOT/args.supervisor).read_bytes());cleanup=supervisor.get('cleanup',{})
    need(supervisor['command_exit_code']==0 and supervisor['stop_reason']=='COMMAND_EXITED' and supervisor['error'] is None
         and cleanup.get('reaped') is True and cleanup.get('job_active_zero_observed') is True
         and cleanup.get('cleanup_errors')==[],'ACTUAL','producer fixture invocation observed empty')
    pin(args.producer_summary,args.producer_summary_sha256)
    summary=json.loads((ROOT/args.producer_summary).read_bytes());directory=(ROOT/args.producer_summary).parent
    need(summary['status']=='AUTHOR_FROZEN_ROOT_TWO_LINE_V1_CONTROLS_PENDING_INDEPENDENT_GATE'
         and summary['unique_complete_proposal_records_checked']==243 and summary['recorded_proposal_evaluation_calls']==486
         and summary['additional_known_overlap_evaluation_calls']==1 and summary['strict_negative_count']==41
         and summary['whole_split_equal'] is True and summary['independent_approval'] is False,'AUTHOR','exact finite pending population')
    expected_fixtures={
        'rook9':dict(n=9,degree=2,root=0,triples=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]),
        'prism9':dict(n=9,degree=2,root=8,triples=[[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]),
        'cube12':dict(n=12,degree=2,root=0,triples=[[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]])}
    need(literal_equal(summary['fixtures'],expected_fixtures),'AUTHOR','exact three independent fixture definitions')
    audits={};negative_conditions=[];raw_observations=0;expected_diagnostics={}
    for name,fixture in expected_fixtures.items():
        pin((directory/(name+'.json')).relative_to(ROOT).as_posix())
        need(literal_equal(json.loads((directory/(name+'.json')).read_bytes()),fixture),'AUTHOR','saved literal fixture')
        base=K.from_triples(fixture['triples'],fixture['n'],2,fixture['root']);cache={}
        projection=directory/(name+'_topology_projection.txt');pin(projection.relative_to(ROOT).as_posix())
        projected=topology(projection.read_bytes())
        need(projected['triples']==base['triples'] and projected['frozen']==base['frozen'] and projected['mutable']==base['mutable'],'AUTHOR','separate topology decoding')
        whole,wr=check_manifest(directory/(name+'_whole/manifest.json'),base,pin,deadline,cache)
        prefix,pr=check_manifest(directory/(name+'_prefix37/manifest.json'),base,pin,deadline,cache)
        resumed,rr=check_manifest(directory/(name+'_resumed/manifest.json'),base,pin,deadline,cache)
        need(prefix['completed']==37 and literal_equal(wr,rr) and literal_equal(whole['aggregate'],resumed['aggregate']),
             'RESUME','all literal full records and aggregate equality')
        raw_observations+=len(wr)+len(pr)+len(rr)
        audits[name]=dict(whole=whole,prefix=prefix,resumed=resumed,unique_labels=len(cache))
        for kind in ['common_cache','score_cache','adjacency_cache']:
            artifact=directory/(name+'_'+kind+'_input.json');pin(artifact.relative_to(ROOT).as_posix())
            bad=json.loads(artifact.read_bytes());fresh=K.from_triples(bad['triples'],bad['n'],bad['degree'],bad['root'])
            if kind=='common_cache':
                matrix=[[(fresh['bits'][u]&fresh['bits'][v]).bit_count() if u!=v else 0 for v in range(fresh['n'])] for u in range(fresh['n'])]
                failed=not literal_equal(matrix,bad['cn'])
            elif kind=='score_cache':
                failed=any(fresh[k]!=bad[k] for k in ['lambda_energy','mu_energy','root_residual'])
            else:
                failed=fresh['bits']!=bad['masks']
            need(failed,'NEGATIVE','literal malformed cache condition '+name+'_'+kind)
            negative_conditions.append(name+'_'+kind)
            expected_diagnostics[name+'_'+kind]=dict(stage={'common_cache':'CN_CACHE','score_cache':'ENERGY_CACHE','adjacency_cache':'ADJ_CACHE'}[kind],
                diagnostic={'common_cache':'CN_CACHE: common-neighbor cache','score_cache':'ENERGY_CACHE: integer score cache','adjacency_cache':'ADJ_CACHE: adjacency cache'}[kind])
        artifact=directory/(name+'_corrupt_checkpoint.json');pin(artifact.relative_to(ROOT).as_posix());bad=json.loads(artifact.read_bytes())
        need(not literal_equal(bad['aggregate'],aggregate(wr[:37])),'NEGATIVE','corrupt prefix aggregate')
        negative_conditions.append(name+'_checkpoint_aggregate')
        expected_diagnostics[name+'_checkpoint_aggregate']=dict(stage='CHECKPOINT_AGGREGATE',diagnostic='CHECKPOINT_AGGREGATE: prefix metadata reproduced')
        for suffix in ['magic','duplicate_n','boolean_n','wrong_mutable_count','wrong_root','reordered_frozen','truncated']:
            artifact=directory/(name+'_reader_'+suffix+'_state.txt');pin(artifact.relative_to(ROOT).as_posix())
            try:
                topology(artifact.read_bytes())
            except K.CensusError as error:
                need(error.stage in ['TOPOLOGY','TOPOLOGY_REFERENCE'],'NEGATIVE','topology-only failure stage')
            else:
                raise K.CensusError('NEGATIVE','accepted malformed saved projection')
            negative_conditions.append(name+'_reader_'+suffix)
            stage='FROZEN_READER' if suffix in ['wrong_root','reordered_frozen'] else 'STATE_READER'
            detail={'magic':'exact state wrapper','duplicate_n':'exactly one n','boolean_n':'typed n','wrong_mutable_count':'mutable count',
                    'wrong_root':'all exact incident/nonincident literal labels','reordered_frozen':'all exact incident/nonincident literal labels','truncated':'exact state wrapper'}[suffix]
            expected_diagnostics[name+'_reader_'+suffix]=dict(stage=stage,diagnostic=stage+': '+detail)
        need(base['frozen'][0][0] not in base['mutable'],'NEGATIVE','excluded frozen label condition')
        negative_conditions.append(name+'_excluded_frozen_label')
        expected_diagnostics[name+'_excluded_frozen_label']=dict(stage='FROZEN_UNIVERSE',diagnostic='FROZEN_UNIVERSE: only two distinct non-root lines in original order')
    for name in ['duplicate_vertex','out_of_range','duplicate_triple','wrong_point_degree']:
        artifact=directory/(name+'_input.json');pin(artifact.relative_to(ROOT).as_posix());bad=json.loads(artifact.read_bytes())
        try:
            K.from_triples(bad['triples'],bad['n'],bad['degree'],bad['root'])
        except K.CensusError as error:
            need(error.stage=='DOMAIN','NEGATIVE','independent malformed domain stage')
        else:
            raise K.CensusError('NEGATIVE','accepted malformed domain')
        negative_conditions.append(name)
        stage='DEGREE' if name=='wrong_point_degree' else 'DOMAIN'
        detail='complete regular incidence' if name=='wrong_point_degree' else 'duplicate triple' if name=='duplicate_triple' else 'three distinct literal points'
        expected_diagnostics[name]=dict(stage=stage,diagnostic=stage+': '+detail)
    negative_conditions.append('out_of_population_proposal')
    expected_diagnostics['out_of_population_proposal']=dict(stage='PROPOSAL_DOMAIN',diagnostic='PROPOSAL_DOMAIN: proposal ID')
    recorded_labels=[record['label'] for record in summary['strict_negatives']]
    need(sorted(recorded_labels)==sorted(negative_conditions) and len(negative_conditions)==41,'NEGATIVE','all41recorded malformed operations accounted')
    need(all(record['stage']==expected_diagnostics[record['label']]['stage']
             and record['diagnostic']==expected_diagnostics[record['label']]['diagnostic'] for record in summary['strict_negatives']),
         'NEGATIVE','every exact recorded author rejection stage and diagnostic')
    overlap=directory/'prism_known_overlap_9.json';pin(overlap.relative_to(ROOT).as_posix())
    prism=expected_fixtures['prism9'];base=K.from_triples(prism['triples'],9,2,8);wanted=expected_record(base,9,K.labelled_universe(base))
    check_record(json.loads(overlap.read_bytes()),wanted)
    need(wanted['new_lambda']==wanted['new_mu']==0,'AUTHOR','known actual overlapping prism-to-rook matrix')
    for path in sorted(directory.rglob('*')):
        if path.is_file():
            pin(path.relative_to(ROOT).as_posix())
    save(out/'fixture_audits.json',audits)
    save(out/'negative_conditions.json',negative_conditions)
    return dict(unique_complete_labelled_proposals=243,raw_record_observations=raw_observations,whole_split_equalities=3,
                malformed_saved_conditions_checked=41,synthetic_topology_positive_fixtures=3,
                complete_selected_scalar_matrices=sum(item[key]['selected_scalar'] is not None for item in audits.values() for key in ['whole','prefix','resumed']),
                producer_reported_evaluation_calls=486,producer_reported_additional_overlap_call=1,scientific_census_checked=False,
                fixture_audits_sha256=sha(out/'fixture_audits.json'))


def full(out,pin,deadline,args):
    need(args.manifest and args.manifest_sha256 and args.supervisor and args.supervisor_sha256,
         'ACTUAL','explicit terminal census identities')
    pin(args.manifest,args.manifest_sha256);pin(args.supervisor,args.supervisor_sha256)
    supervisor=json.loads((ROOT/args.supervisor).read_bytes())
    cleanup=supervisor.get('cleanup',{})
    need(supervisor['command_exit_code']==0 and supervisor['stop_reason']=='COMMAND_EXITED'
         and supervisor['error'] is None and supervisor['deadline_reached'] is False
         and cleanup.get('reaped') is True and cleanup.get('job_active_zero_observed') is True
         and cleanup.get('cleanup_errors')==[],'ACTUAL','terminal contained process observed empty')
    for name,wanted in [(STATE,STATE_SHA),(MATRIX,MATRIX_SHA),(SAVED,SAVED_SHA)]:
        pin(name,wanted)
    saved=json.loads((ROOT/SAVED).read_bytes())
    need(saved['status']=='INDEPENDENT_ROOT_FOCUSED_SAVED_OBJECTS_V1_PASS' and saved['verifier']=='/root/checkpoint_audit'
         and saved['producer']=='/root/native_driver' and saved['method']=='independent_artifact_check'
         and saved['inputs_sha256'][STATE]==STATE_SHA and saved['inputs_sha256'][MATRIX]==MATRIX_SHA,
         'INPUT','exact separately checked raw input')
    for name,wanted in saved['inputs_sha256'].items():
        pin(name,wanted)
    state=S.parse_state((ROOT/STATE).read_bytes())
    base=K.from_triples(state['current'],99,7,11)
    need(base['frozen']==FROZEN and len(base['mutable'])==224
         and (base['lambda_energy'],base['mu_energy'],base['root_residual'])==(0,5476,10)
         and K.matrix_bytes(base['bits'])==(ROOT/MATRIX).read_bytes(),'INPUT','literal fixed original root graph')
    path=ROOT/args.manifest
    manifest=json.loads(path.read_bytes());identity=manifest['identity']
    full_checkpoint_population(manifest,path)
    need(all(identity['inputs_sha256'].get(name)==wanted for name,wanted in [(STATE,STATE_SHA),(MATRIX,MATRIX_SHA),(SAVED,SAVED_SHA)])
         and identity['software'].get(PRODUCER)==PRODUCER_SHA and identity['software'].get(PRODUCER_SPEC)==PRODUCER_SPEC_SHA,
         'INPUT','actual exact producer/input identity')
    for name,wanted in identity['inputs_sha256'].items():
        pin(name,wanted)
    audit,records=check_manifest(path,base,pin,deadline,audit_out=out)
    need(audit['completed']==audit['population']==224784,'COVERAGE','complete fixed mutable-label universe')
    universe=K.labelled_universe(base)
    scalar_audits=[];target_zeros=[]
    for pid in tqdm(audit['aggregate']['best_root_proposal_ids'],desc='Exact all minimum-R tie matrices',unit='matrix',mininterval=1):
        need(deadline.status()['remaining_seconds']>20,'DEADLINE','tie matrix preservation reserve')
        evaluated=K.evaluate(base,universe[pid]);raw=K.matrix_bytes(evaluated['candidate_bits'])
        scalar=S.scalar_matrix(raw,99,7,11)
        record=records[pid]
        need((scalar['lambda_energy'],scalar['mu_energy'],scalar['root_residual'])
             ==(record['new_lambda'],record['new_mu'],record['new_root_residual']),'TIES','complete independent minimum-R scalar score')
        scalar_audits.append(dict(proposal_id=pid,matrix_sha256=hashlib.sha256(raw).hexdigest(),scalar=scalar))
        if scalar['srg_valid']:
            matrix_name='target_candidate_'+str(pid)+'.adj';triples_name='target_candidate_'+str(pid)+'_triples.json'
            (out/matrix_name).write_bytes(raw)
            save(out/triples_name,K.reconstruct_triples(base,evaluated))
            target_zeros.append(dict(proposal_id=pid,path=(out/matrix_name).relative_to(ROOT).as_posix(),sha256=sha(out/matrix_name)))
            print('FULL99_TARGET_MATRIX_CANDIDATE_PENDING_ROOT_REVIEW '+str(pid),flush=True)
    receipt=path.parent/'run_receipt.json';pin(receipt.relative_to(ROOT).as_posix())
    receipt_data=json.loads(receipt.read_bytes())
    need(receipt_data['manifest_sha256']==args.manifest_sha256 and receipt_data['producer']=='/root/native_driver'
         and receipt_data['independent_approval'] is False and receipt_data['target_resolution'] is False,
         'ACTUAL','exact pending producer receipt')
    save(out/'census_audit.json',audit);save(out/'minimum_root_tie_scalar_audits.json',scalar_audits)
    return dict(complete_labelled_proposals=224784,scope_input_matrix_sha256=MATRIX_SHA,scope_input_state_sha256=STATE_SHA,
                frozen_original_literal_rows=FROZEN,mutable_label_count=224,aggregate=audit['aggregate'],selected_proposal_id=audit['selected_proposal_id'],
                minimum_root_tie_scalar_matrices=len(scalar_audits),target_candidate_objects=target_zeros,
                source_commit_context=identity['source_commit'],literal_one_move_population_only=True,
                census_audit_sha256=sha(out/'census_audit.json'),minimum_root_tie_scalar_audits_sha256=sha(out/'minimum_root_tie_scalar_audits.json'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['calibration','controls','full'])
    parser.add_argument('--seconds',type=float,required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--calibration');parser.add_argument('--calibration-sha256')
    parser.add_argument('--producer-summary');parser.add_argument('--producer-summary-sha256')
    parser.add_argument('--manifest');parser.add_argument('--manifest-sha256')
    parser.add_argument('--supervisor');parser.add_argument('--supervisor-sha256')
    parser.add_argument('--controls-gate');parser.add_argument('--controls-gate-sha256')
    args=parser.parse_args();deadline=CommandDeadline(args.seconds,allocation_reason='New independent typed frozen-root records/checkpoints calibration or complete tiny producer-controls audit;20s save reserve;no native/scientific target calls')
    out=(ROOT/args.out).resolve();need(out.is_relative_to(ROOT),'PATH','workspace output');out.mkdir(parents=True,exist_ok=False)
    pins={};protected={name:sha(ROOT/name) for name in ['CLAIMS.yaml','.git/index']}
    def pin(name,wanted=None):
        path=(ROOT/name).resolve();need(path.is_relative_to(ROOT),'PATH','workspace input')
        identity=sha(path);need(wanted is None or identity==wanted,'IDENTITY','exact preserved input '+name)
        need(name not in pins or pins[name]==identity,'IDENTITY','consistent input closure');pins[name]=identity
        return identity
    try:
        for name in [SOURCE,SPEC,'acceleration/audit_20261003_root_focused_census_core_v1.py',
                     'acceleration/audit_20261003_root_focused_census_core_v1_spec.md','acceleration/audit_20261003_root_focused_core_v2.py',
                     'acceleration/audit_20261003_root_focused_census_core_v1_review.md','acceleration/command_deadline.py',
                     'acceleration/run_compute_command.py','pyproject.toml','uv.lock','acceleration/native_budget_env_v1/pyproject.toml','acceleration/native_budget_env_v1/uv.lock']:
            pin(name)
        pin(PRODUCER,PRODUCER_SHA);pin(PRODUCER_SPEC,PRODUCER_SPEC_SHA);pin(KERNEL_CAL,KERNEL_CAL_SHA)
        kernel=json.loads((ROOT/KERNEL_CAL).read_bytes())
        need(kernel['status']=='INDEPENDENT_FROZEN_ROOT_TWO_LINE_KERNEL_V1_CALIBRATION_PASS' and kernel['positive_labelled_proposals']==259
             and kernel['strict_negative_controls']==16 and kernel['producer_outputs_checked'] is False,'CALIBRATION','new separately calibrated scorer')
        for name,identity in kernel['inputs_sha256'].items():
            pin(name,identity)
        if args.mode=='calibration':
            outcome=calibration(out,pin,deadline);status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_RECORDS_V1_CALIBRATION_PASS'
        else:
            need(args.calibration and args.calibration_sha256,'CALIBRATION','new exact raw-record calibration required')
            pin(args.calibration,args.calibration_sha256);cal=json.loads((ROOT/args.calibration).read_bytes())
            need(cal['status']=='INDEPENDENT_FROZEN_ROOT_TWO_LINE_RECORDS_V1_CALIBRATION_PASS' and cal['producer_outputs_checked'] is False,
                 'CALIBRATION','separate raw-record calibration scope')
            for name,identity in cal['inputs_sha256'].items():
                pin(name,identity)
            if args.mode=='controls':
                need(args.producer_summary and args.producer_summary_sha256,'AUTHOR','explicit producer controls identity')
                outcome=controls(out,pin,deadline,args);status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_CONTROLS_PASS'
            else:
                need(args.controls_gate and args.controls_gate_sha256,'CALIBRATION','exact complete changed producer controls gate')
                pin(args.controls_gate,args.controls_gate_sha256);gate=json.loads((ROOT/args.controls_gate).read_bytes())
                need(gate['status']=='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_CONTROLS_PASS' and gate['verifier']=='/root/checkpoint_audit'
                     and gate['producer']=='/root/native_driver' and gate['method']=='independent_artifact_check',
                     'CALIBRATION','complete new producer finite gate roles')
                for name,wanted in gate['inputs_sha256'].items():
                    pin(name,wanted)
                outcome=full(out,pin,deadline,args);status='INDEPENDENT_FROZEN_ROOT_TWO_LINE_V1_COMPLETE_PASS'
        need(all(sha(ROOT/name)==identity for name,identity in protected.items()),'PROTECTED','ledger/index unchanged')
        now=datetime.now(timezone.utc).isoformat()
        limitations={
            'calibration':['Synthetic record/part/checkpoint/tie/matrix calibration only; no producer-output or actual target-census audit.',
                           'Kernel259labels include a16label target-sized fixture sample; this is not exhaustive target-population verification.'],
            'controls':['Complete243distinct tiny producer proposal labels and their whole/prefix/resume artifacts only; actual224784target census requires separate complete checking.',
                        'Author malformed cache/prefix/reader cases checked by distinct raw conditions and exact recorded rejections, not a repeated producer execution; no general parser theorem.',
                        'Native486evaluations and additional overlap call are reported execution counters, distinct from597raw record observations.'],
            'full':['Complete224784labelled one-move neighbourhood of one exact saved graph with seven frozen original root11 lines; not a global or plateau minimum or unrestricted exclusion.',
                    'All45generated checkpoint prefixes from one fixed5000chunk invocation are authenticated; checking-prefix progress files alone do not establish complete coverage.',
                    'All minimum-R tie matrices receive separate scalar99checks; this does not establish a complete10million-proposal annealer trajectory or an unobserved historical minimum.']
        }[args.mode]+['Literal graph counts use net adjacency toggles, not isomorphism classes; no target automorphism or support-pair uniqueness assumption.',
                     'Tiny rook9 exact identity zero is a control; any full99zero is separately exported and announced for ROOT candidate-resolution review.']
        save(out/'summary.json',dict(status=status,checker_implementation_version=IMPLEMENTATION_VERSION,**outcome,timestamp=now,verifier='/root/checkpoint_audit',producer='/root/native_driver',
            method='independent_artifact_check',inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            deadline=deadline.status(),target_resolution='NONE',native_calls=0,ledger_mutations=0,index_mutations=0,
            historical_protected_execution_state=dict(observations_sha256=protected,role='Historical before/after protected execution observations; not immutable dependencies'),
            shared_components=['Own independent new integer bitmask scorer plus previously calibrated independent set/scalar raw matrix helpers; no producer imports.',
                               'Declared raw21field serialization order including first conflict pair is shared format semantics; exact numeric cost path is independently checked.',
                               'Python/JSON/gzip/SHA256/lockedruntime and supported deadline/containment are trusted components.'],
            limitations=limitations))
        print(status)
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),inputs_sha256=pins,outputs_preserved=True,deadline=deadline.status(),native_calls=0))
        raise


if __name__=='__main__':
    main()
