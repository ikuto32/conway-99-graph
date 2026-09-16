# E71 unsigned-kernel filter independent audit

Status: **E71_UNSIGNED_KERNEL_INDEPENDENT_AUDIT_PASS**.

The E71 `Q>=2` input contains 3,220 positive support rows and 599,222 port-feasible state tuples. The legacy `Q_at_least_4` field names in this pipeline mean the configured E71 threshold `Q>=2`.

A separate exact implementation, using right-to-left rational pivots and a combinatorial signless-incidence rank check, reproduces 1,660 inconsistent diagonal systems and 48 uniquely forced non-PSD systems. Thus 1,512 rows / 361,900 tuples remain; 1,708 rows / 237,322 tuples are rejected. All 233 unique invariant `Z` matrices and the producer's stored coordinate `H` matrices were checked by exact principal minors.

Soundness boundary: underdetermined consistent Gram systems are always retained. This is a support-only necessary condition, not an E71 exclusion, graph construction, or proof-assistant certificate.
