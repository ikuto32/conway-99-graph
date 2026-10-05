"""Preserve failed inventory v1 and freeze complete local-cap reconstruction v2."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'acceleration'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,t):
    with p.open('x',encoding='utf8',newline='\n')as f:f.write(t)
old=A/'theory_20260930_exact_eight_population_inventory.py';new=A/'theory_20260930_exact_eight_population_inventory_v2.py';spec=old.with_name(old.stem+'_spec.md');newspec=new.with_name(new.stem+'_spec.md')
before="    triples=[list(t)for t in combinations(range(90),3)if all(overlaps[x,y]<=2 for x,y in combinations(t,2))];need(triples==local['survivors']and len(triples)==31110,'all31110 local triples')"
after="""    cells=[[(a,b,w[a],w[b])for a,b in combinations(range(6),2)]for w in words]
    triples=[];overlap_only_rejections=0
    for t in combinations(range(90),3):
        if not all(overlaps[x,y]<=2 for x,y in combinations(t,2)):continue
        observed=Counter(cell for i in t for cell in cells[i])
        if any(n>(1 if f==h else 2)for(a,b,f,h),n in observed.items()):overlap_only_rejections+=1;continue
        triples.append(list(t))
    need(overlap_only_rejections>0,'column-overlap-only false-positive control')
    need(triples==local['survivors']and len(triples)==31110,'all31110 complete local Gram/Y-cap triples')"""
t=old.read_text(encoding='utf8');assert t.count(before)==1;t=t.replace(before,after)
needle="        for p in[Path(__file__),SPEC,ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)"
t=t.replace(needle,needle+"\n        for p in[A/'theory_20260930_exact_eight_population_inventory.py',A/'theory_20260930_exact_eight_population_inventory_spec.md',B/'20260930_exact_eight_population_inventory/failure.json',B/'20260930_exact_eight_population_inventory/correction.json']:pin(p)")
put(new,t)
put(newspec,spec.read_text(encoding='utf8').replace('with the literal within-triple overlap cap2.','with the literal within-triple overlap cap2 AND local Gram entry bounds:1 for\nsame-fibre distinct coordinates and2 for different-fibre distinct coordinates.')+'''\n## V2 provenance correction\n\nV1 stopped at the complete local-catalogue comparison before computing any case.\nIts independent reconstruction omitted local Gram caps and admitted extra triples.\nV2 adds literal Counter pair-frequency tests for those bounds. No raw input,\ncatalogue, existing formula or prior mathematical gate changed. The failed source,\nspec and failure remain; a false-positive control proves overlaps alone insufficient.\n''')
record=dict(status='INVENTORY_V2_COMPLETE_LOCAL_GRAM_CAP_CORRECTION',before_source_sha256=sha(old),before_spec_sha256=sha(spec),failure_sha256=sha(A/'results/20260930_exact_eight_population_inventory/failure.json'),after_source_sha256=sha(new),after_spec_sha256=sha(newspec),change='Add missing local same-fibre1/different-fibre2 Gram bounds to raw catalogue reconstruction, preserving full overlap-cap check.',native_calls=0,new_formula_builds=0)
put(A/'results/20260930_exact_eight_population_inventory/correction.json',json.dumps(record,indent=2)+'\n');print(json.dumps(record))
