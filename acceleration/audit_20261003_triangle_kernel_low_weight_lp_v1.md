# Independent shifted binary-kernel dual proof

This written checker proof uses the separately audited conditional triangle-image
counts N3=231,N4=2079,N6=24486 and kernel nonzero weights even36..60.
The target premise remains unestablished. No target graph or rank upper bound
is assumed, and no certificate has been inspected while preparing this file.

Let M=|C| and A_w count codewords of weight w, A0=1. Character orthogonality
over the binary linear code gives sum_all A_w K_j(w)=M B_j, where B_j counts
weight-j words in C-perp. The separate image audit proves B_j>=N_j at j3,4,6;
put N_j=0 at other degrees. Hence
sum_nonzero A_w(N_j-K_j(w)) <= K_j(0)-N_j.
All99 denominators K_j(0)-N_j are strictly positive. Divide them to obtain
sum_w A_w G_j(w)<=1. Any complete rational99-vector y>=0 with
sum_j y_j G_j(w)>=1 for every allowed13weights gives
M-1=sum_w A_w<=sum_j y_j. This is an exact upper bound on M, with no claim
of linear-program optimum, realizability of a weight distribution or construction.
Since M is exactly a power of two, compare the rational bound with integer
powers of two; if M<=U<2^(d+1), then dim(C)<=d and rank(B)>=99-d.

K_j(w) is checked by literal integer multiplication of (1-z)^w(1+z)^(n-w).
This differs from discovery's binomial coefficient sum. The full model checks
every99x13 rational coefficient, all99 dual coordinates and all13 inequalities.
Known rook9 complete image/kernel and literal characters test the shifted
constants, including all three modified degrees. Real corrupted certificates
must hit precise syntax/nonnegativity/equality/power-of-two vetoes.

The unchanged independently derived weight interval and complete universal
triangle-image count proof remain separate pinned dependencies. Agreement of
floating solvers, agents or finite fixtures is not a mathematical verification.
