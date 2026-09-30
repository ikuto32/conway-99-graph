"""Audit the single saved M1-normalized capped attempt; no new solver call."""
from audit_20260930_normalized_unknown_common import run

CONFIG=dict(directory='acceleration/results/20260930_variable_core_m1_orbits_native_pilot',input='acceleration/results/20260930_variable_core_m1_orbits/instance.cnf',summary_sha256='07c92c324307df7414e20846fc524979afab326cc3db040a3a90b470444ed77d',trace_sha256='20f7edffbe62f04cab07b608db3d0e25a9b638ded52f652720b2041948550969',trace_bytes=4740528382,exit=0,variables=110915,clauses=518227,conflicts=5000003,real='788.36',cpu='786.31',status='INDEPENDENT_VARIABLE_CORE_M1_ORBITS_UNKNOWN_RUN_AUDIT_PASS',scope='One capped attempt on the M1-normalized universally necessary variable-core factor encoding. No residual D or complete target graph is supplied.')

if __name__=='__main__': run(CONFIG,__file__)
