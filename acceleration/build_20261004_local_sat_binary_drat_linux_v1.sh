#!/usr/bin/bash
# One fresh POSIX DRAT checker build. No proof or formula is checked here.
set -eu
test "$#" -eq 0
test "$(/usr/bin/id -u)" = 1000
cd /mnt/c/Users/ikuto/projects/conway-99-graph
test -f build/rook-drat-checker/upstream-drat-trim.c
test ! -e build/fixed17-local-sat-binary-drat-linux-v1
printf 'd834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee  build/rook-drat-checker/upstream-drat-trim.c\n' | /usr/bin/sha256sum --strict --check -
printf 'bash %s\n' "$BASH_VERSION"
/usr/bin/gcc --version
/usr/bin/sha256sum --version
/usr/bin/timeout --version
/usr/bin/prlimit --version
/usr/bin/mkdir -- build/fixed17-local-sat-binary-drat-linux-v1
/usr/bin/cp -- build/rook-drat-checker/upstream-drat-trim.c build/fixed17-local-sat-binary-drat-linux-v1/drat-trim.c
printf 'd834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee  build/fixed17-local-sat-binary-drat-linux-v1/drat-trim.c\n' | /usr/bin/sha256sum --strict --check -
/usr/bin/prlimit --as=8589934592:8589934592 --fsize=134217728:134217728 --core=0:0 \
    /usr/bin/timeout --foreground --signal=TERM --kill-after=5s 90s \
    /usr/bin/gcc build/fixed17-local-sat-binary-drat-linux-v1/drat-trim.c -std=c99 -O2 -o build/fixed17-local-sat-binary-drat-linux-v1/drat-trim
test -x build/fixed17-local-sat-binary-drat-linux-v1/drat-trim
/usr/bin/sha256sum -- build/fixed17-local-sat-binary-drat-linux-v1/drat-trim.c build/fixed17-local-sat-binary-drat-linux-v1/drat-trim > build/fixed17-local-sat-binary-drat-linux-v1/build.sha256
