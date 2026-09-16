"""Bounded independent-row capacity test of the same fixed overlap lift."""
from collections import Counter
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'.deps'))
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver


def main():
    started = time.monotonic()
    data = json.loads((HERE/'scratch_next_overlap_semantic_map.json').read_bytes())
    output = []
    for vertex in range(84):
        incident = {var for var, u, v in data['edge_variables'] if vertex in (u, v)}
        pool, clauses = IDPool(start_from=1681), []
        groups = []
        for group in data['groups']:
            if group['kind'] == 'label_quota' and group['coordinate'][0] == vertex:
                terms, equality = group['terms'], True
            elif group['kind'] == 'linear_pair_cap':
                terms, equality = [v for v in group['terms'] if v in incident], False
            else:
                continue
            target = group['target']
            if not terms:
                assert target >= 0 and (not equality or target == 0)
                continue
            encoder = CardEnc.equals if equality else CardEnc.atmost
            clauses.extend(encoder(lits=terms, bound=target, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)
            groups.append((group['kind'], group['coordinate']))
        with Solver(name='cadical195', bootstrap_with=clauses) as solver:
            solver.conf_budget(10000)
            answer = solver.solve_limited()
            record = {'vertex':vertex, 'answer':'UNKNOWN' if answer is None else 'SAT' if answer else 'UNSAT'}
            if answer:
                chosen = set(solver.get_model()) & incident
                record['chosen_edge_variables'] = sorted(chosen)
                for group in data['groups']:
                    if group['kind'] == 'label_quota' and group['coordinate'][0] == vertex:
                        assert len(chosen & set(group['terms'])) == group['target']
                    elif group['kind'] == 'linear_pair_cap':
                        assert len(chosen & set(group['terms'])) <= group['target']
                record['direct_integer_check'] = True
            output.append(record)
            if answer is False:
                break
    result = {'status':'BOUNDED_INDIVIDUAL_ROW_LINEAR_CAPACITY_TEST', 'rows':output,
              'histogram':dict(Counter(row['answer'] for row in output)),
              'elapsed_seconds':time.monotonic()-started,
              'scope':'Each row independently meets its own label quotas and every pair cap after all other unknown row terms are dropped. No simultaneous graph claim.'}
    (HERE/'scratch_next_overlap_row_probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
