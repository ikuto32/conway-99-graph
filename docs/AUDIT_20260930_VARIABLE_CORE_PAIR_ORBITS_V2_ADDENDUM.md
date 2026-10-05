# Pair-orbit audit v2 schema correction

The first audit stopped at a mistaken checker interpretation of the frozen
census `second_orbits[].representative_index`: it is the representative's index
in the full10395-matching universe, not the orbit's position in the list.
The original audit source and failure report are preserved. V2 checks equality
with the independently reconstructed matching lookup and membership in that
orbit, while the local orbit ordinal continues to come from enumeration order.
This correction changes neither the producer's artifacts nor the mathematical
coverage argument in AUDIT_20260930_VARIABLE_CORE_PAIR_ORBITS.md.
