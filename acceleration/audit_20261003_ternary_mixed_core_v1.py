"""Independent mixed-engine wire/RNG/whole-matrix replay. Source only.

Only prior independent checking code is imported. No native/producer parser,
updater, scorer or execution wrapper is imported or run.
"""
from collections import Counter
import copy
from itertools import combinations
import math
import re

import audit_20261003_ternary_two_line_raw_core_v1 as dense

io = dense.io
MASK = (1 << 64) - 1
OBJECTIVE = 'SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1'
KERNEL = 'ALL_LINE_EXCLUSIVE_SWAP_TERNARY_V1'
DISTRIBUTION = 'ALL_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1'
NATURAL = re.compile(r'(0|[1-9][0-9]*)\Z')
DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')
METRIC_KEYS = ('F3', 'E_lambda', 'E_mu', 'E', 'scalar_weight', 'scalar', 'residue_population')


def need(ok, stage):
    io.need(ok, stage)


def number(raw):
    need(type(raw) is str and NATURAL.fullmatch(raw) is not None, 'WIRE_INTEGER')
    value = int(raw)
    need(value <= MASK, 'WIRE_INTEGER_OVERFLOW')
    return value


def real(raw):
    # The finite contract emits decimal C++ doubles. Python-only underscore
    # syntax is intentionally rejected rather than accepted by float().
    need(type(raw) is str and DECIMAL.fullmatch(raw) is not None, 'WIRE_REAL')
    try:
        value = float(raw)
    except ValueError:
        raise io.AuditError('WIRE_REAL') from None
    need(math.isfinite(value), 'WIRE_REAL')
    return value


def seed_words(seed):
    words = []
    for _ in range(4):
        seed = (seed + 0x9e3779b97f4a7c15) & MASK
        z = seed
        z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & MASK
        z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & MASK
        words.append(z ^ (z >> 31))
    return words


def rotate(value, bits):
    return ((value << bits) | (value >> (64 - bits))) & MASK


def next_word(state):
    need(state['rng_words'] < MASK, 'RNG_WORD_OVERFLOW')
    state['rng_words'] += 1
    s = state['rng']
    result = (rotate((s[1] * 5) & MASK, 7) * 9) & MASK
    t = (s[1] << 17) & MASK
    s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]
    s[2] ^= t; s[3] = rotate(s[3], 45)
    return result


def bounded(draw, bound):
    need(type(bound) is int and 1 <= bound <= (1 << 64), 'RNG_BOUND')
    threshold = (1 << 64) % bound
    while True:
        word = draw()
        need(type(word) is int and 0 <= word <= MASK, 'RNG_WORD_TYPE')
        if word >= threshold:
            return word % bound


def domain(n, degree):
    need(type(n) is int and type(degree) is int
         and (n, degree) in ((99, 7), (9, 2), (12, 2)), 'DOMAIN_DECLARED')


def geometry(n, degree, rows):
    domain(n, degree)
    adjacency = io.geometry(n, degree, rows, 0)
    metrics, cn = dense.score(adjacency, degree)
    return adjacency, metrics, cn


def weight(n, degree):
    return 819820 if n == 99 else n * (n - 1) // 2 * (2 * degree) ** 2 + 1


def counters(step, valid, accepted, updates, words):
    need(step <= 0x0fffffffffffffff and updates <= accepted <= valid <= step
         and words >= 4 * step + valid, 'STATE_COUNTERS')


def config_check(s):
    need(s['schedule_steps'] > 0 and all(math.isfinite(s[k]) and 0 <= s[k] <= 1e12
         for k in ('t_start', 't_end')), 'CONFIG_SCHEDULE')


class Reader:
    def __init__(self, raw):
        try:
            self.tokens = raw.decode('ascii').split()
        except UnicodeError:
            raise io.AuditError('WIRE_ENCODING') from None
        self.at = 0

    def take(self):
        need(self.at < len(self.tokens), 'WIRE_TRUNCATED')
        result = self.tokens[self.at]; self.at += 1
        return result

    def tag(self, name):
        need(self.take() == name, 'WIRE_FIELD:' + name)

    def field(self, name):
        self.tag(name)
        return self.take()

    def integer(self, name):
        return number(self.field(name))

    def rng(self, name):
        self.tag(name)
        words = [number(self.take()) for _ in range(4)]
        need(any(words), 'RNG_ZERO')
        return words

    def rows(self, name, n, degree):
        count = self.integer(name)
        need(count <= 231, 'WIRE_RANGE')
        need(count * 3 == n * degree, 'TRIPLE_POPULATION')
        rows = [[number(self.take()) for _ in range(3)] for _ in range(count)]
        need(all(x < n for row in rows for x in row), 'WIRE_RANGE')
        return rows

    def metrics(self, name, scalar_weight):
        self.tag(name)
        values = [number(self.take()) for _ in range(7)]
        f, el, em, q0, q1, q2, scalar = values
        need(f <= 4851 and el <= 819819 and em <= 819819
             and max(q0, q1, q2) <= 4851
             and scalar == scalar_weight * f + el + em, 'STATE_METRIC_TYPES')
        return dict(F3=f, E_lambda=el, E_mu=em, E=el + em,
                    scalar_weight=scalar_weight, scalar=scalar,
                    residue_population=[q0, q1, q2])

    def end(self):
        self.tag('END')
        need(self.at == len(self.tokens), 'WIRE_TRAILING')


def parse_graph(raw, source):
    r = Reader(raw); r.tag('TERNARY_LINEAR_GRAPH_INPUT_V1')
    n, d = r.integer('n'), r.integer('degree'); domain(n, d)
    saved = r.field('source_graph_sha256')
    need(re.fullmatch('[0-9a-f]{64}', saved) is not None and saved == source, 'GRAPH_SOURCE_IDENTITY')
    rows = r.rows('triples', n, d); r.end()
    geometry(n, d, rows)
    return n, d, rows


def parse_state(raw, source=None, config=None):
    r = Reader(raw); r.tag('HYPERGRAPH_TERNARY_MIXED_STATE_V1')
    need(r.field('objective') == OBJECTIVE and r.field('move_kernel') == KERNEL
         and r.field('distribution') == DISTRIBUTION, 'STATE_VERSION')
    s = {'source_graph_sha256': r.field('source_graph_sha256')}
    need(re.fullmatch('[0-9a-f]{64}', s['source_graph_sha256']) is not None
         and (source is None or s['source_graph_sha256'] == source), 'SOURCE_GRAPH_HASH')
    s['n'], s['degree'] = r.integer('n'), r.integer('degree'); domain(s['n'], s['degree'])
    w = r.integer('scalar_weight'); need(w == weight(s['n'], s['degree']), 'STATE_SCALAR_WEIGHT')
    for k in ('seed', 'mix_steps', 'schedule_steps'):
        s[k] = r.integer(k)
    for k in ('t_start', 't_end'):
        s[k] = real(r.field(k))
    s['forced'] = r.integer('forced'); need(s['forced'] in (0, 1), 'STATE_FORCED')
    config_check(s)
    if config is not None:
        need(all(s[k] == config[k] for k in ('seed', 'mix_steps', 'schedule_steps',
             't_start', 't_end', 'forced')), 'RESUME_CONFIG_MISMATCH')
    for k in ('step', 'admissible', 'accepted', 'best_updates', 'rng_words'):
        s[k] = r.integer(k)
    s['rng'] = r.rng('rng')
    counters(s['step'], s['admissible'], s['accepted'], s['best_updates'], s['rng_words'])
    s['current_metrics'] = r.metrics('current_metrics', w)
    s['best_metrics'] = r.metrics('best_metrics', w)
    s['current'] = r.rows('current', s['n'], s['degree'])
    s['best'] = r.rows('best', s['n'], s['degree'])
    _, current, cn = geometry(s['n'], s['degree'], s['current'])
    _, best, _ = geometry(s['n'], s['degree'], s['best'])
    need(io.same(current, s['current_metrics']) and io.same(best, s['best_metrics'])
         and (best['F3'], best['E']) <= (current['F3'], current['E']), 'STATE_SCORES')
    need(r.integer('cn') == s['n'] * (s['n'] - 1) // 2, 'STATE_CN_POPULATION')
    saved_cn = [number(r.take()) for _ in combinations(range(s['n']), 2)]
    need(saved_cn == [int(cn[u, v]) for u, v in combinations(range(s['n']), 2)], 'STATE_CN_CACHE')
    count = r.integer('zero_archive'); need(count <= s['step'] + 1, 'STATE_ZERO_POPULATION')
    s['zeros'] = []; identities = set()
    for _ in range(count):
        z = {key: r.integer('zero_' + key) for key in ('step', 'admissible', 'accepted')}
        z['best_updates'] = r.integer('zero_updates'); z['rng_words'] = r.integer('zero_rng_words')
        z['rng'] = r.rng('zero_rng'); z['rows'] = r.rows('zero_triples', s['n'], s['degree'])
        counters(z['step'], z['admissible'], z['accepted'], z['best_updates'], z['rng_words'])
        a, m, _ = geometry(s['n'], s['degree'], z['rows']); identity = io.matrix_bytes(a)
        if z['step'] == 0:
            need(z['admissible'] == z['accepted'] == z['best_updates'] == z['rng_words'] == 0
                 and z['rng'] == seed_words(s['seed'])
                 and (s['step'] != 0 or z['rows'] == s['current']), 'STATE_ZERO_INITIAL_RESET')
        need(m['F3'] == 0 and all(z[k] <= s[k] for k in ('step', 'admissible', 'accepted',
             'best_updates', 'rng_words')) and identity not in identities, 'STATE_ZERO_OBJECT')
        need(not s['zeros'] or s['zeros'][-1]['step'] < z['step'], 'STATE_ZERO_ORDER')
        identities.add(identity); s['zeros'].append(z)
    a, _, _ = geometry(s['n'], s['degree'], s['current'])
    b, _, _ = geometry(s['n'], s['degree'], s['best'])
    need(current['F3'] != 0 or io.matrix_bytes(a) in identities, 'STATE_ZERO_COMPLETENESS')
    need(best['F3'] != 0 or io.matrix_bytes(b) in identities, 'STATE_BEST_ZERO_COMPLETENESS')
    need(not s['zeros'] or best['F3'] == 0, 'STATE_ZERO_BEST_ORDER')
    if s['step'] == 0:
        need(s['admissible'] == s['accepted'] == s['best_updates'] == s['rng_words'] == 0
             and s['rng'] == seed_words(s['seed']) and s['current'] == s['best'], 'STATE_INITIAL_RESET')
    r.end()
    return s


def candidate(s, ti, tj, pi, pj):
    rows = s['current']
    need(all(type(x) is int for x in (ti, tj, pi, pj)) and 0 <= ti < len(rows)
         and 0 <= tj < len(rows) and ti != tj and 0 <= pi < 3 and 0 <= pj < 3, 'PROPOSAL_LABEL')
    t, q = rows[ti][:], rows[tj][:]
    x, y = t[pi], q[pj]
    aa = [t[(pi + 1) % 3], t[(pi + 2) % 3]]
    bb = [q[(pj + 1) % 3], q[(pj + 2) % 3]]
    a, before, _ = geometry(s['n'], s['degree'], rows)
    removed = {tuple(sorted((x, v))) for v in aa} | {tuple(sorted((y, v))) for v in bb}
    added = [(y, v) for v in aa] + [(x, v) for v in bb]
    absent = all(u != v and (not a[u, v] or tuple(sorted((u, v))) in removed) for u, v in added)
    exclusive = x not in q and y not in t
    proposed = copy.deepcopy(rows); proposed[ti][pi] = y; proposed[tj][pj] = x
    valid = exclusive and absent
    after = geometry(s['n'], s['degree'], proposed)[1] if valid else before
    return dict(old=[t, q], proposed=[proposed[ti], proposed[tj]], rows=proposed,
                disjoint=not bool(set(t) & set(q)), exclusive=exclusive, absent=bool(absent),
                valid=bool(valid), before=before, candidate=after)


def capture(s):
    if s['current_metrics']['F3'] != 0:
        return False
    identity = io.matrix_bytes(geometry(s['n'], s['degree'], s['current'])[0])
    if any(io.matrix_bytes(geometry(s['n'], s['degree'], z['rows'])[0]) == identity for z in s['zeros']):
        return False
    z = {k: copy.deepcopy(s[k]) for k in ('step', 'admissible', 'accepted', 'best_updates', 'rng_words', 'rng')}
    z['rows'] = copy.deepcopy(s['current']); s['zeros'].append(z)
    return True


def transition(s):
    old_rng = s['rng'][:]; old_words = s['rng_words']; step = s['step']
    m = len(s['current'])
    ti = bounded(lambda: next_word(s), m); tj = bounded(lambda: next_word(s), m - 1)
    if tj >= ti:
        tj += 1
    pi = bounded(lambda: next_word(s), 3); pj = bounded(lambda: next_word(s), 3)
    p = candidate(s, ti, tj, pi, pj)
    temp = s['t_start'] + (s['t_end'] - s['t_start']) * min(1., max(step - s['mix_steps'], 0) / s['schedule_steps'])
    mixing = step < s['mix_steps']; accepted = False; draw = 0; margin = None
    delta = p['candidate']['scalar'] - p['before']['scalar']
    if p['valid']:
        s['admissible'] += 1; draw = next_word(s)
        u = (draw >> 11) * 2. ** -53
        easy = s['forced'] == 1 or mixing or delta <= 0
        threshold = math.exp(-delta / temp) if not easy and temp > 0 else 0.
        accepted = easy or (temp > 0 and u < threshold)
        if not easy and temp > 0:
            margin = abs(u - threshold)
        if accepted:
            s['current'] = p['rows']; s['current_metrics'] = p['candidate']; s['accepted'] += 1
            if (s['current_metrics']['F3'], s['current_metrics']['E']) < (s['best_metrics']['F3'], s['best_metrics']['E']):
                s['best'] = copy.deepcopy(s['current']); s['best_metrics'] = copy.deepcopy(s['current_metrics'])
                s['best_updates'] += 1
    s['step'] += 1; captured = capture(s)
    expected = dict(schema='HYPERGRAPH_TERNARY_MIXED_MOVE_V1', objective=OBJECTIVE,
        move_kernel=KERNEL, distribution=DISTRIBUTION, step=step, ti=ti, tj=tj, pi=pi, pj=pj,
        old_triples=p['old'], proposed_triples=p['proposed'], disjoint=p['disjoint'],
        exclusive=p['exclusive'], absent_after_removal=p['absent'], admissible=p['valid'],
        accepted=bool(accepted), mixing=bool(mixing), temperature=temp, delta_scalar=delta,
        before=p['before'], candidate=p['candidate'], after=copy.deepcopy(s['current_metrics']),
        best=copy.deepcopy(s['best_metrics']), draw=str(draw), rng_words_before=old_words,
        rng_words_after=s['rng_words'], rng_before=list(map(str, old_rng)),
        rng_after=list(map(str, s['rng'])), retained_zero_objects=len(s['zeros']))
    return expected, margin, captured


def check_trace(raw, expected):
    need(type(raw) is dict and set(raw) == set(expected), 'TRACE_FIELDS')
    need(type(raw['temperature']) in (int, float) and math.isfinite(raw['temperature'])
         and math.isclose(raw['temperature'], expected['temperature'], rel_tol=1e-12, abs_tol=1e-10), 'TRACE_TEMPERATURE')
    actual, wanted = dict(raw), dict(expected)
    del actual['temperature']; del wanted['temperature']
    need(io.same(actual, wanted), 'TRACE_CONTENT')


def probe(s, pid, ti, tj, pi, pj):
    p = candidate(s, ti, tj, pi, pj)
    return dict(schema='HYPERGRAPH_TERNARY_MIXED_PROBE_V1', proposal_id=pid, ti=ti, tj=tj,
        pi=pi, pj=pj, disjoint=p['disjoint'], exclusive=p['exclusive'],
        absent_after_removal=p['absent'], admissible=p['valid'], retained=False,
        before=p['before'], candidate=p['candidate'], rollback=p['before'],
        delta_scalar=p['candidate']['scalar'] - p['before']['scalar'])


def pair_costs():
    rows = []
    def cost(c, a):
        r = c + a - 2
        return r % 3, int(r % 3 != 0), a * r * r, (1 - a) * r * r
    for c in range(100):
        for a in range(2):
            old = cost(c, a)
            for kind, change, nc, na in [('CN', d, c + d, a) for d in (-1, 1) if 0 <= c + d <= 99] + [('EDGE', 1 - 2*a, c, 1-a)]:
                new = cost(nc, na)
                rows.append(dict(kind=kind, c=c, a=a, delta=change, new_c=nc, new_a=na,
                    old_residue=old[0], new_residue=new[0], delta_F3=new[1]-old[1],
                    delta_lambda=new[2]-old[2], delta_mu=new[3]-old[3]))
    return rows


def serialize(s):
    lines = ['HYPERGRAPH_TERNARY_MIXED_STATE_V1', 'objective ' + OBJECTIVE,
             'move_kernel ' + KERNEL, 'distribution ' + DISTRIBUTION]
    for k in ('source_graph_sha256', 'n', 'degree'):
        lines.append(k + ' ' + str(s[k]))
    lines.append('scalar_weight ' + str(weight(s['n'], s['degree'])))
    for k in ('seed', 'mix_steps', 'schedule_steps', 't_start', 't_end', 'forced',
              'step', 'admissible', 'accepted', 'best_updates', 'rng_words'):
        value = format(s[k], '.17g') if k in ('t_start', 't_end') else str(s[k])
        lines.append(k + ' ' + value)
    lines.append('rng ' + ' '.join(map(str, s['rng'])))
    for key in ('current_metrics', 'best_metrics'):
        m = s[key]
        lines.append(key + ' ' + ' '.join(map(str, [m['F3'], m['E_lambda'], m['E_mu'],
                     *m['residue_population'], m['scalar']])))
    def append_rows(name, rows):
        lines.append(name + ' ' + str(len(rows)))
        lines.extend(' '.join(map(str, row)) for row in rows)
    append_rows('current', s['current']); append_rows('best', s['best'])
    _, _, cn = geometry(s['n'], s['degree'], s['current'])
    lines.append('cn ' + str(s['n'] * (s['n'] - 1) // 2))
    lines.extend(str(int(cn[u, v])) for u, v in combinations(range(s['n']), 2))
    lines.append('zero_archive ' + str(len(s['zeros'])))
    for z in s['zeros']:
        for raw, key in (('step', 'step'), ('admissible', 'admissible'), ('accepted', 'accepted'),
                         ('updates', 'best_updates'), ('rng_words', 'rng_words')):
            lines.append('zero_' + raw + ' ' + str(z[key]))
        lines.append('zero_rng ' + ' '.join(map(str, z['rng'])))
        append_rows('zero_triples', z['rows'])
    return ('\n'.join(lines) + '\nEND\n').encode('ascii')


def fixture(name):
    if name == 'rook9':
        return 9, 2, [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]
    if name == 'prism9':
        return 9, 2, [[0,2,6],[0,1,7],[1,2,8],[3,5,6],[3,4,7],[4,5,8]]
    if name == 'cube12':
        return 12, 2, [[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]
    need(name == 'target99', 'FIXTURE_NAME')
    return 99, 7, [[x,x+33,x+66] for x in range(33)] + [[x,(x+1)%99,(x+4)%99] for x in range(99)] + [[x,(x+7)%99,(x+18)%99] for x in range(99)]


def initial(name, seed=1, mix=0, start=0., end=0., forced=0):
    n, d, rows = fixture(name); _, metrics, _ = geometry(n, d, rows)
    s = dict(source_graph_sha256='0'*64, n=n, degree=d, seed=seed, mix_steps=mix,
             schedule_steps=2048, t_start=float(start), t_end=float(end), forced=forced,
             step=0, admissible=0, accepted=0, best_updates=0, rng_words=0,
             rng=seed_words(seed), current=rows, best=copy.deepcopy(rows),
             current_metrics=metrics, best_metrics=copy.deepcopy(metrics), zeros=[])
    capture(s)
    return s
