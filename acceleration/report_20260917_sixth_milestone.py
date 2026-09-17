"""Freeze the independently checked two-coordinate extension milestone."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2);f.write('\n')


def main():
    resume=Path('acceleration/results/20260917_resume');snapshot=resume/'claims_at_sixth_milestone.yaml';assert not snapshot.exists()
    snapshot.write_bytes(Path('CLAIMS.yaml').read_bytes())
    rev='acceleration/results/20260917_independent_review/'
    paths=dict(ledger=snapshot.as_posix(),previous_ledger=(resume/'claims_at_fifth_milestone.yaml').as_posix(),
        validation=(resume/'binary_membership_ledger_validation.json').as_posix(),
        parent='acceleration/results/20260917_partial_coordinate_checkpoint.json',
        domains=rev+'two_matchings/summary.json',model=rev+'two_matching_moments.json',
        exact=rev+'two_matching_solve_bound.json',binding=rev+'two_matching_exclusion_claim_binding.json',
        parity=rev+'two_coordinate_binary_span.json',parity_binding=rev+'two_coordinate_binary_span_claim_binding.json',
        transfer=rev+'two_matching_transfer_bound.json',
        execution='acceleration/results/20260917_two_matching_moments/solve_summary.json',
        public_replay='acceleration/results/20260917_moment_public_replay/replay_receipt_v2.json')
    d={k:(yaml.safe_load(Path(p).read_bytes()) if 'ledger' in k else json.loads(Path(p).read_bytes())) for k,p in paths.items()}
    hashes={k:digest(p) for k,p in paths.items()}
    assert hashes['parent']=='8ef4773cd204065495aa3be5f4fa9f2533af5f1874ba578dc1657eb32afb2df2'
    assert d['validation']['valid'] and d['validation']['provenance']['input_hashes']['ledger']['sha256']==hashes['ledger']
    previous={c['id'] for c in d['previous_ledger']['claims']}
    changes=[{k:c[k] for k in ('id','revision','status','review_state','scope')} for c in d['ledger']['claims'] if c['id'] not in previous]
    assert len(changes)==4 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in changes)
    assert d['domains']['domain_choices']==89308 and d['model']['shape']==[5370,96280]
    refs={p:hashes[k] for k,p in paths.items()}
    for k in ('domains','model','exact','binding','parity','parity_binding','transfer'):
        for p,h in d[k]['inputs_sha256'].items():
            assert digest(p)==h,p
            if p in refs:assert refs[p]==h
            refs[p]=h
    now=datetime.now(timezone.utc).isoformat();commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    cp='acceleration/results/20260917_two_coordinate_checkpoint.json'
    checkpoint=dict(status='VERIFIED_TWO_COORDINATE_CONDITIONAL_EXCLUSION_CHECKPOINT',created_utc=now,source_commit=commit,
        previous_checkpoint_preserved=dict(path=paths['parent'],sha256=hashes['parent']),
        inherited_reference_policy='Immutable parent retained; previous entire inventory not rehashed in this indexing step.',
        target_resolution='UNKNOWN',graph_constructed=False,general_nonexistence_proved=False,
        current_best=d['parent']['current_best'],current_star_marginal_best=d['parent']['current_star_marginal_best'],
        no_seed_adoption=True,objective_comparisons_not_inferred=True,
        verified_family=dict(claim_id='C-PARTIAL-K-TWO-COORDINATE-EXCLUSION',revision=1,fixed_outer_edges=156,unknown_outer_edges=1800,
            original_domain_choices=89308,exact_lower_bound='469399553/1048576',prescribed_absences_retained=True,
            objective=d['model']['objective'],domain_manifest='acceleration/results/20260917_partial_two_matchings/manifest.json'),
        binary_affine_membership=dict(witness_differences_checked=1837,reference_columns_checked=84,full_rank_claimed=False,graph_feasibility_claimed=False),
        referenced_files_sha256=refs,directly_hash_checked_reference_count=len(refs),
        next_experiment='Four same-sign coordinates at rootgroups0,1, with144fixedK/1920unknown; independent domain and matching-filter/model gates before a fresh bounded solve.',
        process_state='UNKNOWN; indexing is not live observation',overall_search_coverage='UNKNOWN; no validated denominator',builder_sha256=digest(__file__))
    save(cp,checkpoint)
    report=dict(as_of=now,source_commit=commit,previous_report='docs/RESEARCH_20260917_FIFTH_WAVE.md',checkpoint=cp,checkpoint_sha256=digest(cp),
        target=d['ledger']['target'],claim_changes=changes,counts=dict(families_excluded=1,centers=84,original_domain_choices=89308,old_embedded_choices=54478,
            moment_equalities=3486,reciprocity_equalities=1800,parity_witness_differences=1837,parity_references=84),
        exact_lower_bound='469399553/1048576',objective=d['model']['objective'],completed_execution=d['execution'],
        public_replay_receipt=paths['public_replay'],public_replay_sha256=hashes['public_replay'],
        input_paths=paths,input_sha256=hashes,script_sha256=digest(__file__),other_processes='UNKNOWN; not observed by this generator',draft_pr='https://github.com/ikuto32/conway-99-graph/pull/1')
    save(resume/'sixth_milestone.json',report)
    claims='\n'.join('- `'+c['id']+'` revision '+str(c['revision'])+': '+c['scope']['description'] for c in changes)
    text=f'''# Sixth resumed milestone: two-coordinate family excluded

Since the [fifth milestone](RESEARCH_20260917_FIFTH_WAVE.md), fresh complete
domains and a new integer moment model allowed an exclusion after freeing
both sign coordinates at rootgroup0. A separate binary test passed its
necessary membership condition; that supplies no graph or LP solution.

**As of:** {now}; source `{commit}` plus hash-bound new sources;
checkpoint `{report['checkpoint_sha256']}`.

**Verdict:** repository target resolution UNKNOWN. The new exact certificate
excludes only the family with156fixed outer edges and the recorded prescribed
absences, allowing120coordinate edges and1680disjoint-support edges to vary.
No unrestricted proof, target graph, automorphism assumption or external
target-resolution review is claimed.

**Verified changes:**

{claims}

**Work completed:** all84domains independently enumerated, containing89,308
choices; all54,478old choices embed with identical full neighborhoods. The
5,370×96,280integer model has7,315,157nonzeros. A fresh raw-neighborhood audit
recomputed every89,308column and all84maxima for the positive certificate.
These are stages of one conditional-family result and their counts overlap.

The modular witness uses1,837column differences and84reference columns. Only
the exact witness membership was independently checked; the producer's
partial basis rank and processed-column count are not independently claimed.
Binary affine membership is compatible with a positive real moment bound:
it implies neither nonnegative star mixtures nor one selected star per center.

**Coverage:** one precisely specified two-coordinate family. No count or union
with the earlier family is added to progress. Overall search coverage: UNKNOWN;
no validated denominator.

**Best result:** `469399553/1048576 > 0` is an exact lower bound on this new
family's full moment L1residual with hard reciprocal equalities. Any admitted
target completion would have zero residual. The bound is not a score of a
candidate graph and need not be optimal. Older objectives and configurations
are not compared numerically with it.

**Execution:** the single900-second-capped solve completed successfully; its
recorded solver duration is605.953seconds. The transferred old weights were
evaluated first and gave an independently reproduced negative bound, retained
as an unsuccessful attempt. No wider exclusion was inferred from transfer.
Other process states are not inferred from this report.

**Problems and replay:** the one-coordinate proof was successfully replayed
using only115Git-bound runtime/seed files from public commitd4f4a926. This is
repeated execution of the independent checker, not fresh domain enumeration
or a new mathematical derivation. Initial newline conversion and Windows
provenance-command representation failures were preserved and corrected;
scientific inputs and checker arithmetic remained unchanged. The binary
partial-basis checkpoint is preserved with an exact gzip companion.

**Next experiment:** four freed same-sign coordinates at rootgroups0and1,
leaving144fixed outer edges. Complete-domain review, necessary matching
filtering and a separately checked reduced moment model precede the longer
bounded solve. A nonpositive transferred certificate already gives no
automatic broader-family exclusion.

**References:** [ledger](../CLAIMS.yaml), [new exact audit](../{paths['exact']}),
[scope binding](../{paths['binding']}), [modular audit](../{paths['parity']}),
[checkpoint](../{cp}), [machine-readable milestone](../acceleration/results/20260917_resume/sixth_milestone.json),
[public replay](../{paths['public_replay']}), [replay instructions](REPRODUCING.md),
[draft PR1]({report['draft_pr']}), [source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}).
'''
    with Path('docs/RESEARCH_20260917_SIXTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(claims=[c['id'] for c in changes],checkpoint=cp,checkpoint_sha256=report['checkpoint_sha256'],references=len(refs))))


if __name__=='__main__':main()
