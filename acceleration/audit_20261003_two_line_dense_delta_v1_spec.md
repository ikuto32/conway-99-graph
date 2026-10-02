# Independent dense two-line delta calibration V1

Question: does the exact changed-row matrix path reconstruct both energy
categories, adjacency-category switches and the selected root's NEW outsiders?
Freeze all135 labelled proposals of the valid rook9 incidence, two selected
distinct lines and their three point positions. All valid moves are reconstructed
from complete new triples, full matrix products and independent literal scalar
products. Require positive valid overlapping moves and both invalid paths.
Deliberately corrupt population/labels/linearity/degrees/proposal indices.

Changed adjacency D has endpoints only in its changed row set. All outside rows
are identical, so their mutual CN dot products are unchanged. Recompute each
changed row of A'² exactly, assign its transpose, and rescore all unordered pairs
against new adjacency. Root residual uses actual NEW distinct nonneighbors,
never a frozen old outsider set when its neighborhood changes. All arithmetic
uses int64, with n<=99/CN<=99/pair squared sums<=4851*99² and bounded signed
differences. Separate full scalar rook products calibrate NumPy integer behavior.

90outer60worker30shutdown, finite tiny controls only. No239085 scientific census,
native annealer, bitset scorer, producer import or target resolution. Save exact
records/counts/source/spec/runtime/command/time and any failed cases. This gate
does not automatically approve a later checker/source/interface version.
