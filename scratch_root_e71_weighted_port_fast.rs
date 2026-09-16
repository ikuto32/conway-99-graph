use std::collections::{HashMap, HashSet};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::time::Instant;

const N: usize = 7;
const M: usize = 21;
const TARGET: u8 = 13;

#[derive(Clone)]
struct Record {
    code: u64,
    orbit_size: usize,
    partition: Vec<u8>,
}

struct Search {
    edges: [(usize, usize); M],
    actions: Vec<[usize; M]>,
    values: [u8; M],
    totals: [u8; N],
    maxima: [u8; N],
    remaining_incident: [u8; N],
    seen: HashSet<u64>,
    records: Vec<Record>,
    balanced_labelled: u64,
    unbalanced_accounted: u64,
    capacity_excluded_leaves: u64,
    recursive_nodes: u64,
    pruned_nodes: u64,
    suffix_memo: HashMap<(u8, u8, u8), u64>,
}

fn edge_list() -> [(usize, usize); M] {
    let mut result = [(0usize, 0usize); M];
    let mut at = 0;
    for a in 0..N {
        for b in (a + 1)..N {
            result[at] = (a, b);
            at += 1;
        }
    }
    assert_eq!(at, M);
    result
}

fn permutations() -> Vec<[usize; N]> {
    fn visit(at: usize, row: &mut [usize; N], used: &mut [bool; N], out: &mut Vec<[usize; N]>) {
        if at == N {
            out.push(*row);
            return;
        }
        for value in 0..N {
            if !used[value] {
                used[value] = true;
                row[at] = value;
                visit(at + 1, row, used, out);
                used[value] = false;
            }
        }
    }
    let mut out = Vec::with_capacity(5040);
    visit(0, &mut [0; N], &mut [false; N], &mut out);
    assert_eq!(out.len(), 5040);
    out
}

fn support_actions(edges: &[(usize, usize); M]) -> Vec<[usize; M]> {
    let mut lookup = [[usize::MAX; N]; N];
    for (index, &(a, b)) in edges.iter().enumerate() {
        lookup[a][b] = index;
        lookup[b][a] = index;
    }
    permutations()
        .into_iter()
        .map(|permutation| {
            let mut action = [0usize; M];
            for (index, &(a, b)) in edges.iter().enumerate() {
                action[index] = lookup[permutation[a]][permutation[b]];
            }
            action
        })
        .collect()
}

impl Search {
    fn new() -> Self {
        let edges = edge_list();
        let actions = support_actions(&edges);
        Self {
            edges,
            actions,
            values: [0; M],
            totals: [0; N],
            maxima: [0; N],
            remaining_incident: [6; N],
            seen: HashSet::new(),
            records: Vec::new(),
            balanced_labelled: 0,
            unbalanced_accounted: 0,
            capacity_excluded_leaves: 0,
            recursive_nodes: 0,
            pruned_nodes: 0,
            suffix_memo: HashMap::new(),
        }
    }

    fn suffix_count(&mut self, positions: u8, sum: u8, capacity_needed: u8) -> u64 {
        let needed = capacity_needed.min(2);
        let key = (positions, sum, needed);
        if let Some(value) = self.suffix_memo.get(&key) {
            return *value;
        }
        let answer = if positions == 0 {
            u64::from(sum == 0 && needed == 0)
        } else {
            let mut total = 0u64;
            for value in 0..=4u8.min(sum) {
                let gain = if value == 2 { 2 } else if value == 3 { 1 } else { 0 };
                total += self.suffix_count(positions - 1, sum - value, needed.saturating_sub(gain));
            }
            total
        };
        self.suffix_memo.insert(key, answer);
        answer
    }

    fn feasible_balance(&self, remaining_sum: u8) -> bool {
        for vertex in 0..N {
            let possible_addition = remaining_sum.min(4 * self.remaining_incident[vertex]);
            if 2 * self.maxima[vertex] > self.totals[vertex] + possible_addition {
                return false;
            }
        }
        true
    }

    fn exact_balance(&self) -> bool {
        (0..N).all(|vertex| {
            self.totals[vertex] == 0 || 2 * self.maxima[vertex] <= self.totals[vertex]
        })
    }

    fn code(&self) -> u64 {
        let mut code = 0u64;
        for index in 0..M {
            code |= (self.values[index] as u64) << (3 * index);
        }
        code
    }

    fn image(&self, code: u64, action: &[usize; M]) -> u64 {
        let mut image = 0u64;
        for index in 0..M {
            let value = (code >> (3 * index)) & 7;
            image |= value << (3 * action[index]);
        }
        image
    }

    fn materialize_orbit(&mut self, code: u64) {
        if self.seen.contains(&code) {
            return;
        }
        let mut images = Vec::with_capacity(5040);
        for action in &self.actions {
            images.push(self.image(code, action));
        }
        images.sort_unstable();
        images.dedup();
        assert!(images.binary_search(&code).is_ok());
        assert!(images.iter().all(|image| !self.seen.contains(image)));
        for &image in &images {
            self.seen.insert(image);
        }
        let mut partition: Vec<u8> = self.values.iter().copied().filter(|&x| x != 0).collect();
        partition.sort_unstable_by(|a, b| b.cmp(a));
        self.records.push(Record {
            code: images[0],
            orbit_size: images.len(),
            partition,
        });
    }

    fn visit(&mut self, position: usize, remaining_sum: u8, capacity: u8) {
        self.recursive_nodes += 1;
        if remaining_sum > 4 * ((M - position) as u8) {
            return;
        }
        if !self.feasible_balance(remaining_sum) {
            self.pruned_nodes += 1;
            let needed = 2u8.saturating_sub(capacity.min(2));
            self.unbalanced_accounted += self.suffix_count(
                (M - position) as u8,
                remaining_sum,
                needed,
            );
            return;
        }
        if position == M {
            assert_eq!(remaining_sum, 0);
            if capacity < 2 {
                self.capacity_excluded_leaves += 1;
                return;
            }
            if !self.exact_balance() {
                self.unbalanced_accounted += 1;
                return;
            }
            self.balanced_labelled += 1;
            self.materialize_orbit(self.code());
            return;
        }

        let (a, b) = self.edges[position];
        self.remaining_incident[a] -= 1;
        self.remaining_incident[b] -= 1;
        let old_a_total = self.totals[a];
        let old_b_total = self.totals[b];
        let old_a_max = self.maxima[a];
        let old_b_max = self.maxima[b];
        for value in 0..=4u8.min(remaining_sum) {
            self.values[position] = value;
            self.totals[a] = old_a_total + value;
            self.totals[b] = old_b_total + value;
            self.maxima[a] = old_a_max.max(value);
            self.maxima[b] = old_b_max.max(value);
            let gain = if value == 2 { 2 } else if value == 3 { 1 } else { 0 };
            self.visit(position + 1, remaining_sum - value, (capacity + gain).min(2));
        }
        self.values[position] = 0;
        self.totals[a] = old_a_total;
        self.totals[b] = old_b_total;
        self.maxima[a] = old_a_max;
        self.maxima[b] = old_b_max;
        self.remaining_incident[a] += 1;
        self.remaining_incident[b] += 1;
    }
}

fn main() {
    let started = Instant::now();
    let mut search = Search::new();
    search.visit(0, TARGET, 0);
    search.records.sort_by(|a, b| a.partition.cmp(&b.partition).then(a.code.cmp(&b.code)));

    let capacity_passing_total = 486_185_889u64;
    assert_eq!(search.balanced_labelled + search.unbalanced_accounted, capacity_passing_total);
    assert_eq!(search.seen.len() as u64, search.balanced_labelled);
    assert_eq!(
        search.records.iter().map(|row| row.orbit_size as u64).sum::<u64>(),
        search.balanced_labelled
    );

    let output = File::create("scratch_root_e71_weighted_port_fast.json").unwrap();
    let mut writer = BufWriter::new(output);
    writeln!(writer, "{{").unwrap();
    writeln!(writer, "  \"status\": \"COMPLETE\",").unwrap();
    writeln!(writer, "  \"model\": \"E0=71,Q>=2 exhaustive weighted-port support census\",").unwrap();
    writeln!(writer, "  \"total_deficit\": 13,").unwrap();
    writeln!(writer, "  \"capacity_passing_labelled_placements\": {},", capacity_passing_total).unwrap();
    writeln!(writer, "  \"balanced_labelled_placements\": {},", search.balanced_labelled).unwrap();
    writeln!(writer, "  \"unbalanced_labelled_placements\": {},", search.unbalanced_accounted).unwrap();
    writeln!(writer, "  \"balanced_orbits\": {},", search.records.len()).unwrap();
    writeln!(writer, "  \"orbit_image_union_size\": {},", search.seen.len()).unwrap();
    writeln!(writer, "  \"recursive_nodes\": {},", search.recursive_nodes).unwrap();
    writeln!(writer, "  \"pruned_nodes\": {},", search.pruned_nodes).unwrap();
    writeln!(writer, "  \"capacity_excluded_reached_leaves\": {},", search.capacity_excluded_leaves).unwrap();
    writeln!(writer, "  \"elapsed_seconds\": {:.6},", started.elapsed().as_secs_f64()).unwrap();
    writeln!(writer, "  \"records\": [").unwrap();
    for (index, row) in search.records.iter().enumerate() {
        let comma = if index + 1 == search.records.len() { "" } else { "," };
        let partition = row.partition.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
        writeln!(
            writer,
            "    {{\"partition\":[{}],\"representative_code_hex\":\"0x{:x}\",\"orbit_size\":{}}}{}",
            partition,
            row.code,
            row.orbit_size,
            comma
        ).unwrap();
    }
    writeln!(writer, "  ],").unwrap();
    writeln!(writer, "  \"checks\": {{").unwrap();
    writeln!(writer, "    \"balanced_plus_unbalanced_equals_capacity_scope\": true,").unwrap();
    writeln!(writer, "    \"orbit_size_sum_equals_balanced_labelled\": true,").unwrap();
    writeln!(writer, "    \"every_orbit_generated_under_all_5040_S7_actions\": true").unwrap();
    writeln!(writer, "  }},").unwrap();
    writeln!(writer, "  \"claim_boundary\": \"Necessary weighted-port support census only; overlap, Gram and local graph expansion remain.\"").unwrap();
    writeln!(writer, "}}").unwrap();
    writer.flush().unwrap();

    println!(
        "{{\"status\":\"COMPLETE\",\"balanced_orbits\":{},\"balanced_labelled\":{},\"elapsed_seconds\":{:.6}}}",
        search.records.len(),
        search.balanced_labelled,
        started.elapsed().as_secs_f64()
    );
}
