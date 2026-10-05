"""Independent literal row-content audit and exact normalization manifest.

No producer imports, numerical code, parity elimination or target exclusion.
Dividing every integer coefficient and affine RHS by their common positive
content is exactly equivalent over integers for all parameter values.
"""
import argparse,hashlib,json,math,subprocess,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from command_deadline import CommandDeadline

ROOT=Path(__file__).resolve().parents[1]
MODEL='acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
SHA='a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'

def need(ok,message):
 if not ok:raise ValueError(message)

def raw(row):return json.dumps(row,sort_keys=True,separators=(',',':')).encode()

def normalize(row,divisor=None):
 values=[value for _,value in row['terms']]+row['rhs_affine']
 need(all(type(value) is int for value in values),'integer literal coefficients')
 content=math.gcd(*values) or 1
 if divisor is not None:need(type(divisor) is int and divisor>0 and all(value%divisor==0 for value in values),'exact common positive divisor');content=divisor
 result=dict(terms=[[index,value//content] for index,value in row['terms']],rhs_affine=[value//content for value in row['rhs_affine']])
 need(all(value==content*new for value,(_,new) in zip([v for _,v in row['terms']],result['terms'])) and all(value==content*new for value,new in zip(row['rhs_affine'],result['rhs_affine'])),'every literal coefficient roundtrip')
 return content,result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=float,required=True)
 args=ap.parse_args();out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace audit');out.mkdir(parents=True,exist_ok=False)
 deadline=CommandDeadline(args.seconds,allocation_reason='Complete raw85874-row integer content and product-evenness audit; exact roundtrip and independent negative controls')
 model_path=ROOT/MODEL;need(hashlib.sha256(model_path.read_bytes()).hexdigest()==SHA,'exact pinned raw model');model=json.loads(model_path.read_bytes())
 need(len(model['equations'])==85874 and len(model['variables'])==23019,'exact frozen dimensions')
 fixture=dict(terms=[[0,2],[1,-4]],rhs_affine=[2,6,0]);divisor,normalized=normalize(fixture)
 need(divisor==2 and normalized==dict(terms=[[0,1],[1,-2]],rhs_affine=[1,3,0]),'positive exact content control')
 rejected=[]
 for name,mutate in [('nondividing_factor',3),('zero_factor',0),('negative_factor',-2)]:
  try:normalize(fixture,mutate)
  except ValueError:rejected.append(name)
  else:raise ValueError('invalid normalization accepted')
 rows=[];product_even=0;product_odd_terms=0;counts=Counter();normalized_stream=hashlib.sha256()
 for index,row in enumerate(model['equations']):
  if index%1000==0:need(not deadline.status()['stop_required'] and deadline.status()['remaining_seconds']>20,'not completed within allocated budget')
  divisor,normalized=normalize(row);counts[divisor]+=1;line=raw(normalized)+b'\n';normalized_stream.update(line)
  if index>=82046:
   even=all(value%2==0 for _,value in row['terms']) and all(value%2==0 for value in row['rhs_affine'])
   need(even,'all3828product rows entirely even');product_even+=1;product_odd_terms+=sum(value%2!=0 for _,value in normalized['terms'])
  rows.append(dict(original_row=index,content=divisor,raw_literal_sha256=hashlib.sha256(raw(dict(terms=row['terms'],rhs_affine=row['rhs_affine']))).hexdigest(),normalized_literal_sha256=hashlib.sha256(raw(normalized)).hexdigest()))
 manifest=dict(schema='ROOTED8_EXACT_INTEGER_ROW_CONTENT_V1',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),model=MODEL,model_sha256=SHA,variables=23019,rows=85874,content_counts=dict(counts),product_rows=[82046,85873],product_rows_even=product_even,normalized_product_odd_term_occurrences=product_odd_terms,normalized_literal_jsonl_sha256=normalized_stream.hexdigest(),records=rows,controls=dict(positive_exact_roundtrip=True,corrupt_divisors_rejected=rejected),scope='Exact literal row-content equivalence for all integer a,b; independent of producer normalization code. Necessary target interpretation remains separately conditional.',target_resolution=False,new_exclusions=0,parity_result=None,parity_result_null_reason='No elimination or feasibility computation in this audit.',artifact_availability='LOCAL_ONLY',shared_components=['Python integer arithmetic/math.gcd, hashlib and JSON parser.','Pinned raw model has a separate independently checked conditional necessary encoding.'])
 with (out/'normalization_manifest.json').open('x',encoding='utf8',newline='\n') as stream:json.dump(manifest,stream,indent=2);stream.write('\n')
 print(json.dumps({key:manifest[key] for key in ('rows','content_counts','product_rows_even','normalized_product_odd_term_occurrences','normalized_literal_jsonl_sha256')}))

if __name__=='__main__':main()
