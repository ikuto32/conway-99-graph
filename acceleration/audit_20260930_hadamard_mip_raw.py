"""Independent exact binary rounding and cap-aware Gram-factor classification."""
from fractions import Fraction
from itertools import combinations
import math

TOLERANCE=Fraction(1,10000000)
def need(ok,why):
    if not ok:raise ValueError(why)

def rounded_binary(values,expected):
    need(type(values)is list and len(values)==expected,'complete returned numerical vector')
    result=[];worst=Fraction(0)
    for v in values:
        need(type(v)in(int,float)and math.isfinite(v),'finite non-Boolean numerical value')
        q=Fraction(v);d0=abs(q);d1=abs(q-1);bit=int(d1<d0);distance=min(d0,d1)
        need(distance<=TOLERANCE,'outside exact1e-7 distance to binary value');result.append(bit);worst=max(worst,distance)
    return result,dict(threshold_numerator=1,threshold_denominator=10000000,maximum_distance_numerator=worst.numerator,maximum_distance_denominator=worst.denominator,maximum_distance_float=float(worst),comparison='Exact rational distance of the saved IEEE value; every rounded constraint is subsequently checked over integers.')

def exact_linear(bits,columns,rhs,order_rows,cuts):
    need(all(type(v)is int and v in(0,1)for v in bits)and len(bits)==len(columns),'binary vector and sparse column dimensions')
    need(all(type(v)is int for v in rhs),'exact integer right-hand sides')
    sums=[0]*len(rhs)
    for bit,col in zip(bits,columns,strict=True):
        need(len(col)==len(set(col))and all(type(r)is int and 0<=r<len(rhs)for r in col),'binary coefficient column')
        for r in col:sums[r]+=bit
    need(sums==rhs,'all exact equality rows')
    order_values=[]
    for row in order_rows:
        need(all(type(index)is int and 0<=index<len(bits)and type(coefficient)is int for index,coefficient in row['terms']),'integer order coefficients and valid indices')
        value=sum(coefficient*bits[index]for index,coefficient in row['terms']);need(value<=-1,'exact strict order inequality');order_values.append(value)
    for i,j in cuts:need(type(i)is int and type(j)is int and 0<=i<len(bits)and 0<=j<len(bits)and i!=j and bits[i]+bits[j]<=1,'all prior exact pair cuts')
    return sums,order_values

def column_caps(factor):
    width=len(factor[0]);columns=[{i for i,row in enumerate(factor)if row[d]}for d in range(width)]
    overlaps=[];violations=[]
    for d,e in combinations(range(width),2):
        count=len(columns[d]&columns[e]);overlaps.append([d,e,count])
        if count>2:violations.append(dict(columns=[d,e],overlap=count,common_rows=sorted(columns[d]&columns[e])))
    return overlaps,violations

def gram_factor(core,factor,support,research=True):
    h=len(core);need(h%3==0,'three equal fibres');n=h//3;m=n*(n-2)//2
    need(not research or n==12,'research99 dimension')
    need(len(core)==3*n and all(len(r)==3*n and all(type(v)is int and v in(0,1)for v in r)for r in core),'binary core')
    need(all(core[i][i]==0 and sum(core[i])==3 and all(core[i][j]==core[j][i]for j in range(3*n))for i in range(3*n)),'simple cubic core')
    need(len(factor)==3*n and all(len(row)==m and all(type(v)is int and v in(0,1)for v in row)for row in factor),'binary raw factor dimensions')
    need(all(sum(row)==n-2 for row in factor),'all exact row margins')
    need(all(sum(factor[n*g+a][d]for a in range(n))==2 for g in range(3)for d in range(m)),'all exact fibre margins')
    nb=[{j for j,v in enumerate(row)if v}for row in core];rows=[{d for d,v in enumerate(row)if v}for row in factor]
    gram=[[n*int(i==j)-core[i][j]-len(nb[i]&nb[j])+2-int(i//n==j//n)for j in range(3*n)]for i in range(3*n)]
    need(all(len(rows[i]&rows[j])==gram[i][j]for i in range(3*n)for j in range(3*n)),'all literal integer Gram entries')
    need(len(support)==n and all(len(row)==m and all(type(v)is int and v in(0,1)for v in row)for row in support),'literal binary coordinate support')
    need([[sum(factor[g*n+a][d]for g in range(3))for d in range(m)]for a in range(n)]==support,'exact fixed support projection')
    pairs=[tuple(i for i in range(n)if factor[i][d])for d in range(m)];catalog=[(a,b)for a,b in combinations(range(n),2)if not core[a][b]]
    need(sorted(pairs)==catalog and len(set(pairs))==m,'complete canonical first-fibre pair bijection');order=[pairs.index(p)for p in catalog]
    mixed=[[factor[i][d]+sum(factor[j][d]for j in nb[i])for d in range(m)]for i in range(3*n)]
    mixed_bad=[dict(row=i,column=d,value=mixed[i][d])for i in range(3*n)for d in range(m)if mixed[i][d]>2]
    overlaps,violations=column_caps(factor)
    return dict(classification='EXACT_GRAM_FACTOR_CAP_VALID'if not violations and not mixed_bad else'EXACT_GRAM_FACTOR_WITH_CAP_VIOLATIONS',core_adjacency=core,factor=factor,L=support,prescribed_gram=gram,canonical_column_order=order,canonical_factor=[[row[d]for d in order]for row in factor],all_column_overlaps=overlaps,column_cap_violations=violations,mixed_values=mixed,mixed_cap_violations=mixed_bad,all_caps_valid=not violations and not mixed_bad,exact_checks=dict(Gram_entries=9*n*n,row_margins=3*n,fibre_margins=3*m,support_entries=n*m,column_pairs=m*(m-1)//2,mixed_entries=3*n*m),target_graph=False,residual_D=None)
