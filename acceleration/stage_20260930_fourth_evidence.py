"""Stage completed evidence only, preserving unrelated and active work."""
from hashlib import sha256
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIRS={
'20260930_closed28_gram','20260930_closed28_lower_gram','20260930_closed28_lower_gram_derivation','20260930_closed28_sos',
'20260930_closed29_extension_screen','20260930_degree_block_gram_bounds','20260930_eight_full99_cnf','20260930_eight_full99_solver_calibration','20260930_eight_sat_preflight',
'20260930_matching_cap_composition','20260930_rook_box_batch01','20260930_rook_box_checker_controls','20260930_rook_box_lazy_wave02',
'20260930_rook_cut_orbits01','20260930_rook_gram_box_cut_initial','20260930_rook_scaffold_relabeling','20260930_rook_solver_v2_calibration',
'20260930_rook_orbit_solver_pilot'}
AUDITS={'degree_block_gram','initial_gram_box_nogood_claim_binding.json','local_redundancy','local_redundancy_v2','closed28_lower_lemma',
'rook_box_collection01.json','rook_box_collection02.json','rook_box_wave02_binding.json','rook_cut_orbits','rook_scaffold_relabelings32.json',
'scaffold_cut_transport_lemma.json','scaffold_map_checker_calibration','target_gram_boolean_box_lemma.json','closed29_specific_gram_v2',
'closed29_specific_gram','rook_orbit_sat_calibration'}
def main():
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()
    chosen=['CLAIMS.yaml','.gitignore','README.md','ACTIVE_RESEARCH.md','docs/RESEARCH_MAP.md','docs/REPRODUCING.md']
    for name in untracked:
        p=Path(name);parts=p.parts
        take=False
        if name.startswith('acceleration/') and len(parts)==2 and '20260930' in name:
            take=not any(x in name for x in ['unrestricted','eight_raw29_gram_cut','audit_20260930_eight_full99','audit_20260930_full99_sat_object','rook_orbit_sat_v2','rook_orbit_gram','degree_relaxation'])
        elif name.startswith('acceleration/results/') and len(parts)>3:
            take=parts[2] in DIRS or (parts[2]=='20260930_independent_review' and parts[3] in AUDITS) or (parts[2]=='20260930_resume' and 'fourth' in p.name)
        elif name in ['docs/DERIVATION_20260930_SCAFFOLD_CUT_TRANSPORT.md','docs/DERIVATION_20260930_TARGET_GRAM_BOX_NOGOODS.md','docs/RESEARCH_20260930_FOURTH_WAVE.md','docs/REPRODUCING_20260930_FOURTH_WAVE.md']:
            take=True
        if take:
            assert p.stat().st_size<=10*1024*1024,name
            chosen.append(name)
    chosen=sorted(set(chosen))
    for i in range(0,len(chosen),75):subprocess.run(['git','add','--',*chosen[i:i+75]],check=True)
    # Index checks read the exact staged blobs; no filesystem normalization assumed.
    rows=subprocess.check_output(['git','ls-files','--stage','-z'],text=True).split('\0');index={}
    for row in rows:
        if row:
            metadata,path=row.split('\t',1);index[path]=metadata.split()[1]
    checked=0
    for p in ROOT.glob('acceleration/results/20260930_independent_review/**/*.json'):
        relative=p.relative_to(ROOT).as_posix()
        if relative not in chosen:continue
        d=json.loads(p.read_bytes())
        for name,expected in d.get('inputs_sha256',{}).items():
            normalized=name.replace('\\','/')
            if normalized not in index:continue
            raw=subprocess.check_output(['git','cat-file','blob',index[normalized]])
            assert sha256(raw).hexdigest()==expected,(relative,normalized)
            checked+=1
    print(json.dumps({'staged_paths':len(chosen),'hash_bound_index_checks':checked,'unrelated_user_paths_staged':False}))
if __name__=='__main__':main()
