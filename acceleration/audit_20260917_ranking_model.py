"""Independent integer model reconstruction from dense full99 adjacency.

No producer or producer model builder is imported. Sparse assembly is numerical
storage of exactly represented small integers; cap entries use BE+EB+E.
"""
from itertools import combinations
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, vstack


def require(ok, text):
    if not ok: raise ValueError(text)


def build_model(candidate, domain_records):
    labels = [(2*a+s, 2*b+t) for a in range(7) for b in range(a+1,7) for s in range(2) for t in range(2)]
    B = np.zeros((99,99), dtype=np.int64)
    def put(u,v):
        require(u != v and B[u,v] == 0, 'duplicate/self edge')
        B[u,v] = B[v,u] = 1
    for u in range(1,15): put(0,u)
    for u in range(1,15,2): put(u,u+1)
    for u,pair in enumerate(labels,15):
        for s in pair: put(u,s+1)
    for u,v in candidate['overlap_edges_outer_zero_based']: put(u+15,v+15)
    require(np.array_equal(B.sum(axis=1), [14]*15+[6]*84), 'partial degrees')
    squared = B @ B
    off = ~np.eye(99,dtype=bool)
    require(np.all((squared+B)[off] <= 2), 'partial cap')
    edges = [(u,v) for u,v in combinations(range(84),2)
             if not {x//2 for x in labels[u]} & {x//2 for x in labels[v]}]
    require(len(edges) == 1680, 'unknown universe')
    lookup = {e:i for i,e in enumerate(edges)}
    pairs = np.asarray(list(combinations(range(15,99),2)))
    aa,bb = pairs[:,0],pairs[:,1]
    C = np.zeros((3486,1680),dtype=np.int64)
    for i,(u,v) in enumerate(edges):
        p,q = u+15,v+15
        C[:,i] = ((aa == p)&(bb == q)).astype(np.int64)
        C[:,i] += B[aa,p]*(bb == q)+B[aa,q]*(bb == p)
        C[:,i] += (aa == p)*B[q,bb]+(aa == q)*B[p,bb]
    rhs = 2-B[aa,bb]-squared[aa,bb]
    require(np.all(C.sum(axis=0) == 9), 'derivative incidence')
    require([r['outer_vertex'] for r in domain_records] == list(range(84)), 'domain order')
    counts = [len(r['domain_masks_hex']) for r in domain_records]
    require(min(counts)>0, 'nonempty tables required')
    offsets = np.cumsum([0]+counts)
    rr,cc,vv,er,ec = [],[],[],[],[]
    for u,row in enumerate(domain_records):
        for j,s in enumerate(row['domain_masks_hex']):
            mask = int(s,16)
            require(0 <= mask < 1<<84 and mask.bit_count() == 8, 'domain mask')
            while mask:
                bit = mask & -mask; mask -= bit; v = bit.bit_length()-1
                edge = tuple(sorted((u,v))); require(edge in lookup, 'fixed/self star edge')
                e,col = lookup[edge],int(offsets[u])+j
                rr.append(e);cc.append(col);vv.append(1 if u<v else -1)
                if u<v: er.append(e);ec.append(col)
    n = int(offsets[-1])
    R = coo_matrix((vv,(rr,cc)),shape=(1680,n),dtype=np.int64).tocsr()
    E = coo_matrix((np.ones(len(er),dtype=np.int64),(er,ec)),shape=(1680,n)).tocsr()
    A = vstack((R,csr_matrix(C)@E),format='csr')
    A.sum_duplicates(); A.sort_indices()
    return dict(A=A,AT=A.T.tocsr(),b=np.r_[np.zeros(1680,dtype=np.int64),rhs],offsets=offsets)
