"""Audit the single saved first-choice six-prism attempt; no new solver call."""
from audit_20260930_normalized_unknown_common import run

CONFIG=dict(directory='acceleration/results/20260930_prism_first_choice_native_pilot',input='acceleration/results/20260930_prism_first_choice_normalization/instance.cnf',summary_sha256='bd030f1a3ce01d594f936ce40d51dccedec39df0d3e8427d831f96717510121d',trace_sha256='a3c7c1d4bf243985337408d3ef8ed992b10ecb56fc4e1b5532469feb6a468c95',trace_bytes=1701081088,exit=124,variables=245880,clauses=874801,conflicts=2137390,real='900.00',cpu='896.31',status='INDEPENDENT_PRISM_FIRST_CHOICE_UNKNOWN_RUN_AUDIT_PASS',scope='One capped attempt on the first-choice-normalized fixed six-prism abstract factor model. Outside column caps and residual D are omitted; no target exclusion.')

if __name__=='__main__': run(CONFIG,__file__)
