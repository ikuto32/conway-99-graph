#!/usr/bin/bash
# Fixed-count local-row SAT dispatch only. A result is never a mathematical approval.
set -eu
test "$#" -eq 4
test "$(/usr/bin/id -u)" = 1000
case "$4" in
    10|1800) ;;
    *) exit 64 ;;
esac
cd /mnt/c/Users/ikuto/projects/conway-99-graph
test -f "$1"
test -f "$3"
test ! -e "$2"
printf 'bash %s\n' "$BASH_VERSION"
/usr/bin/sha256sum --version
/usr/bin/timeout --version
/usr/bin/prlimit --version
/usr/bin/sha256sum --strict --check -- "$3"
exec /usr/bin/prlimit --as=8589934592:8589934592 --fsize=4294967296:4294967296 --core=0:0 \
    /usr/bin/timeout --foreground --signal=TERM --kill-after=5s "${4}s" \
    build/research-cadical195/source/build/cadical --seed=0 "$1" "$2"
