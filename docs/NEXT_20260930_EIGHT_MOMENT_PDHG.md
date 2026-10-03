# Eight-coordinate GPU support search, pre-execution protocol

Question: does the independently audited eight-coordinate matching-filtered
moment relaxation admit a strictly positive exact support bound? Family scope
is 120 fixed K edges, 2160 unknown edges and all recorded prescribed absences. The
original 2,290,122 star choices and complete matching partition must be independently
checked before model construction; every model coefficient must be audited
before export; every exported operator/transpose/RHS entry must be checked
before numerical execution. No automorphism assumption.

Use the byte-identical existing `moment_pdhg_gpu.cu` and executable from the
independently calibrated September 17 GPU/CPU controls. A new larger instance
does not inherit an instance-specific numerical trajectory or speed claim.
The existing implementation accepts domain sizes up to 100,000; reject any
larger new domain before launch. Export the 3486 soft moment rows then 2160 hard
reciprocity rows, with 84 simplexes handled by projection. Record exact binary
layout/hashes and complete mapping audit. Inputs are reconstructible LOCAL_ONLY
binary artifacts, not mathematical certificates.

One initial numerical run: cold uniform probabilities and zero duals,
binary64, eta 0.9, theta 1, 60 projection bisections, 256 threads per simplex, checkpoints
at 1000, 5000, and 10000 iterations. Whole executable wall limit 600 seconds. No tuning
or silent retry. Record current RTX 4090 device/driver, available memory and disk
before the run. The observed six-coordinate 135.687-second process time is
historical context, not a new speed guarantee.

Freeze six support attempts: each checkpoint's last and averaged duals, in
that order. Negate exact binary64 rationals, multiply by 2^20 and round to
nearest integer with ties-to-even. Clip moment coefficients to [-2^20, 2^20];
reciprocity coefficients remain unbounded. Check an integer-product overflow
guard before all int64 sparse arithmetic, then use Python integers for final
sums. Preserve every missing, failed, zero and negative attempt.

Acceptance is exact numerator>0 after independent raw-neighborhood checking
of every retained star, all 84maxima, sound rejected-star evidence, model
necessity and unchanged inputs. No floating tolerance can establish an exclusion.
A numerical zero is not a graph or feasibility certificate. A positive bound
would exclude only this frozen family; an independent complete 99-vertex SRG
validator remains required for any target construction. A nonpositive bound
means these chosen coefficients did not prove an exclusion, not feasibility.

Current status: prepared protocol only. Run manifests and actual process
observations must establish whether execution has started or completed.
