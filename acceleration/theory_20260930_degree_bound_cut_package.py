"""Package an already saved candidate degree-block cut; no new optimization."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/'acceleration/results/20260930_degree_block_gram_bounds/run01'


def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def save(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def main():
    summary_path = RUN/'summary.json'
    summary = json.loads(summary_path.read_bytes())
    assert digest(summary_path) == '7bf8ba56668e61095be383d07006d10f98e0cc5cab87b88c25344dcf2c40f100'
    accepted = [record for record in summary['attempts'] if record['accepted']]
    witness_path = ROOT/accepted[-1]['path'] if accepted else RUN/'initial21_degree_bound.json'
    if accepted:assert digest(witness_path) == accepted[-1]['sha256']
    witness = json.loads(witness_path.read_bytes())
    assert witness['fixed_values'] == summary['final_fixed_values'] and witness['exact_degree_relaxation_maximum'] < 0
    polynomial_path = RUN/'polynomial_00.json'
    polynomial = json.loads(polynomial_path.read_bytes())
    clause = [-int(var) if value else int(var) for var,value in sorted(witness['fixed_values'].items(),key=lambda row:int(row[0]))]
    assert clause == summary['final_clause']
    record = dict(status='CANDIDATE',independent_review_pending=True,cut_kind='GRAM_DEGREE_BLOCK_MAXIMUM',matrix='27I-9A+J',
                  timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                  command=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
                  input_hashes={key(p):digest(p) for p in (Path(__file__),summary_path,witness_path,polynomial_path,RUN/'blocks.json',ROOT/'uv.lock')},
                  graph_path=polynomial['graph_path'],graph_sha256=polynomial['graph_sha256'],encoding_model_sha256=polynomial['model_sha256'],
                  base_cnf_sha256='ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403',
                  polynomial=key(polynomial_path),polynomial_sha256=digest(polynomial_path),
                  block_definitions=key(RUN/'blocks.json'),block_definitions_sha256=digest(RUN/'blocks.json'),
                  block_maximum_witness=key(witness_path),block_maximum_witness_sha256=digest(witness_path),
                  integer_negative_vector=polynomial['vector'],linear_quadratic_constant=polynomial['constant'],
                  exact_degree_relaxation_maximum=witness['exact_degree_relaxation_maximum'],fixed_values=witness['fixed_values'],
                  nogood_clause=clause,nogood_clause_length=len(clause),parent_box_clause_length=21,
                  scope='One frozen780edge family; independent degree-block relaxation with fixed literal values. Proposed necessary target-extension cut only.',
                  independent_verification=None,independent_verification_null_reason='Discovery producer must not approve its own new bound or cut',
                  target_resolution=False,solver_launched=False)
    save(RUN/'final_cut_certificate.json',record)
    with (RUN/'final_nogood.clause').open('x',encoding='ascii',newline='\n') as stream:
        stream.write(' '.join(map(str,clause))+' 0\n')
    print(json.dumps(dict(certificate=key(RUN/'final_cut_certificate.json'),sha256=digest(RUN/'final_cut_certificate.json'),literals=len(clause))))


if __name__ == '__main__':main()
