"""Calibration-only source-closure supplement; original encoding audit preserved."""
from pathlib import Path
import sys
import audit_20260930_direct_cell_count_cnf as audit

def main():
    audit.need(len(sys.argv)>1 and sys.argv[1]=='calibrate','calibration mode only')
    audit.need('--native-driver' in sys.argv,'explicit driver')
    path=Path(sys.argv[sys.argv.index('--native-driver')+1]).resolve()
    specs={p.with_name(p.stem+'_spec.md')for p in audit.closure(path)}
    specs={p for p in specs if p.is_file()}
    extra={Path(__file__).resolve(),Path(__file__).with_name('audit_20260930_direct_cell_count_calibration_spec.md').resolve(),
           audit.ROOT/'acceleration/theory_20260930_direct_cell_count_preflight.py',
           audit.ROOT/'acceleration/theory_20260930_direct_cell_count_preflight_spec.md'}|specs
    audit.PINS.update({p:audit.sha(p)for p in extra})
    audit.PINS.update({audit.ROOT/'build/research-cadical195/source/build/cadical':'021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7',
                      audit.ROOT/'build/rook-drat-checker/drat-trim.exe':'23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac'})
    audit.main()

if __name__=='__main__':main()
