"""Independent exact adjacency/three-triangle/inverse path; no producer imports."""
from collections import Counter
from itertools import combinations
from math import comb


class AuditError(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ': ' + message)


def require(condition, stage, message):
    if not condition:
        raise AuditError(stage, message)


def adjacency(n, triples):
    require(type(n) is int and n >= 0, 'DOMAIN', 'literal vertex population')
    rows = [set() for _ in range(n)]
    for t in triples:
        require(len(t) == 3 and all(type(v) is int and 0 <= v < n for v in t)
                and len(set(t)) == 3, 'DOMAIN', 'literal three-point fixture line')
        for u, v in combinations(t, 2):
            rows[u].add(v)
            rows[v].add(u)
    return rows


def validate_graph(rows, premise=True):
    require(type(rows) is list and all(type(r) is set for r in rows),
            'DOMAIN', 'adjacency sets')
    n = len(rows)
    for u, row in enumerate(rows):
        require(all(type(v) is int and 0 <= v < n and v != u for v in row),
                'DOMAIN', 'simple vertex universe')
        require(all(u in rows[v] for v in row), 'DOMAIN', 'symmetric adjacency')
        if premise:
            require(all(len(row & rows[v]) == 1 for v in row),
                    'PREMISE', 'each adjacent pair has exactly one common neighbor')


def actual_triangles(rows):
    validate_graph(rows, False)
    return [tuple(t) for t in combinations(range(len(rows)), 3)
            if all(v in rows[u] for u, v in combinations(t, 2))]


def mask(points):
    value = 0
    for v in points:
        value ^= 1 << v
    return value


def points(value):
    return [i for i in range(value.bit_length()) if value >> i & 1]


def unordered_paths(rows, triangles):
    """Brute force all unordered triples, independent of the degree formula."""
    records = []
    sets = [set(t) for t in triangles]
    for ids in combinations(range(len(triangles)), 3):
        intersection = {(i, j): sets[i] & sets[j] for i, j in combinations(ids, 2)}
        if sorted(map(len, intersection.values())) != [0, 1, 1]:
            continue
        middle = [i for i in ids if sum(bool(sets[i] & sets[j])
                                      for j in ids if j != i) == 2]
        require(len(middle) == 1, 'PATH', 'unique middle from intersection graph')
        central = middle[0]
        ends = [i for i in ids if i != central]
        meet = [next(iter(sets[central] & sets[i])) for i in ends]
        if meet[0] == meet[1]:
            continue
        support = points(mask(triangles[ids[0]]) ^ mask(triangles[ids[1]])
                         ^ mask(triangles[ids[2]]))
        require(len(support) == 5, 'PATH', 'five-point binary path image')
        records.append({'path': list(ids), 'central': central, 'support': support})
    return records


def inverse(rows, triangles, support):
    require(type(support) is list and len(support) == 5
            and support == sorted(set(support))
            and all(type(v) is int and 0 <= v < len(rows) for v in support),
            'SUPPORT', 'literal sorted five-point support')
    edges = [list(e) for e in combinations(support, 2) if e[1] in rows[e[0]]]
    isolated = [u for u in support if not (rows[u] & set(support))]
    require(len(isolated) == 1, 'ISOLATED', 'unique isolated point of path support')
    r = isolated[0]
    rest = [v for v in support if v != r]
    matchings = []
    for q in rest[1:]:
        leftover = [v for v in rest if v not in [rest[0], q]]
        pairs = sorted([tuple(sorted((rest[0], q))), tuple(leftover)])
        if all(v in rows[u] for u, v in pairs):
            matchings.append(pairs)
    require(1 <= len(matchings) <= 2, 'MATCHING', 'one or two support perfect matchings')
    triangle_id = {t: i for i, t in enumerate(triangles)}
    recovered = []
    completion_records = []
    for matching in matchings:
        completions = []
        for u, v in matching:
            common = sorted(rows[u] & rows[v])
            require(len(common) == 1, 'COMPLETION', 'unique full-graph edge completion')
            completions.append(common[0])
        u, v = completions
        candidates = [tuple(sorted((*matching[0], u))),
                      tuple(sorted((*matching[1], v))), tuple(sorted((u, v, r)))]
        valid = len(set((u, v, r))) == 3 and all(t in triangle_id for t in candidates)
        ids = sorted(triangle_id[t] for t in candidates) if valid else []
        if valid:
            ts = [set(triangles[i]) for i in ids]
            sizes = sorted(len(ts[i] & ts[j]) for i, j in combinations(range(3), 2))
            valid = len(set(ids)) == 3 and sizes == [0, 1, 1]
        if valid:
            require(points(mask(candidates[0]) ^ mask(candidates[1])
                           ^ mask(candidates[2])) == support,
                    'INVERSE', 'reconstructed literal binary support')
            recovered.append(ids)
        completion_records.append({'matching': [list(e) for e in matching],
                                   'completions': completions,
                                   'recovered_path': ids if valid else None})
    return {'support': support, 'isolated': r, 'induced_edges': edges,
            'matchings': [[list(e) for e in m] for m in matchings],
            'completion_records': completion_records,
            'paths': sorted(recovered)}


def formula(triangles, n):
    degrees = Counter(v for t in triangles for v in t)
    return sum((degrees[u] - 1) * (degrees[v] - 1)
               for t in triangles for u, v in combinations(t, 2))


def full_small_graph(rows):
    validate_graph(rows)
    triangles = actual_triangles(rows)
    paths = unordered_paths(rows, triangles)
    fibers = {}
    for record in paths:
        fibers.setdefault(tuple(record['support']), []).append(record['path'])
    inverses = []
    for support, fiber in sorted(fibers.items()):
        result = inverse(rows, triangles, list(support))
        require(result['paths'] == sorted(fiber), 'FIBER', 'complete inverse equals raw fiber')
        require(len(fiber) <= 2, 'FIBER', 'at most two actual paths')
        inverses.append(result)
    require(len(paths) == formula(triangles, len(rows)), 'FORMULA',
            'independent unordered enumeration equals incidence formula')
    require(len(triangles) <= 20, 'DOMAIN', 'small complete binary image allowance')
    code = {0}
    for triangle in triangles:
        generator = mask(triangle)
        code |= {word ^ generator for word in code}
    weight5 = sorted(word for word in code if word.bit_count() == 5)
    require(all(mask(support) in code for support in fibers), 'IMAGE',
            'every path image lies in independently enumerated image code')
    require(2 * len(weight5) >= len(paths), 'IMAGE', 'full-code lower bound')
    return {'vertices': len(rows), 'actual_triangles': [list(t) for t in triangles],
            'paths': paths, 'inverses': inverses, 'path_count': len(paths),
            'distinct_path_words': len(fibers), 'complete_code_words': len(code),
            'complete_weight5_words': len(weight5),
            'fiber_sizes': {str(k): sum(len(v) == k for v in fibers.values())
                            for k in sorted(set(map(len, fibers.values())))}}


def krawtchouk(n, j, w):
    require(all(type(v) is int for v in [n, j, w]) and 0 <= j <= n and 0 <= w <= n,
            'CHARACTER', 'literal Krawtchouk domain')
    return sum((-1) ** s * comb(w, s) * comb(n - w, j - s)
               for s in range(j + 1) if s <= w and j - s <= n - w)


def fixtures():
    return {
        'triangle3': (3, [(0, 1, 2)]),
        'friendship7': (7, [(0, 1, 2), (0, 3, 4), (0, 5, 6)]),
        'intersection_plus_disjoint8': (8, [(0, 1, 2), (0, 3, 4), (5, 6, 7)]),
        'loosechain7': (7, [(0, 1, 2), (0, 3, 4), (1, 5, 6)]),
        'disjoint9': (9, [(0, 1, 2), (3, 4, 5), (6, 7, 8)]),
        'loosecycle8': (8, [(0, 1, 4), (1, 2, 5), (2, 3, 6), (3, 0, 7)]),
        'rook9': (9, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(3)]
                  + [(i, i + 3, i + 6) for i in range(3)]),
    }
