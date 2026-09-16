"""Audit the 208 order-seven frequency formulae at (n,k)=(99,14).

The input is the arXiv 2608.19410 v1 TeX source.  Every displayed frequency
is parsed as an exact rational affine function a+b*n3+c*z11.  We then impose
the necessary conditions that all frequencies are nonnegative integers and
report the surviving lattice region.  This is an audit of consequences of the
paper's formula list, not an independent derivation of those formulae.
"""

from __future__ import annotations

import ast
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re


SOURCE = Path("scratch_reimbayev_2608_19410_source/The_Subgraphs_of_Order_Seven.tex")
OUTPUT = Path("scratch_root_order7_frequency_audit.json")
N = 99
K = 14


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def matching_brace(text: str, start: int) -> int:
    assert text[start] == "{"
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unmatched brace")


def expand_fractions(text: str) -> str:
    while "\\frac" in text:
        start = text.rfind("\\frac")
        numerator_start = start + len("\\frac")
        if numerator_start >= len(text) or text[numerator_start] != "{":
            raise ValueError(text)
        numerator_end = matching_brace(text, numerator_start)
        denominator_start = numerator_end + 1
        if denominator_start >= len(text) or text[denominator_start] != "{":
            raise ValueError(text)
        denominator_end = matching_brace(text, denominator_start)
        numerator = text[numerator_start + 1:numerator_end]
        denominator = text[denominator_start + 1:denominator_end]
        replacement = f"(({numerator})/({denominator}))"
        text = text[:start] + replacement + text[denominator_end + 1:]
    return text


def latex_to_python(text: str) -> str:
    text = text.replace("\\\\", "").replace("&", "")
    text = text.replace("\\,", "").replace("\\!", "")
    text = text.replace("n_3", "x").replace("z_{11}", "y")
    text = expand_fractions(text)
    text = text.replace("{", "(").replace("}", ")")
    text = text.replace("^", "**")
    text = re.sub(r"\s+", "", text).rstrip(",.")
    # After the substitutions every symbolic variable has a one-letter name.
    text = re.sub(r"(?<=[0-9nkxy)])(?=[nkxy(])", "*", text)
    text = re.sub(r"(?<=\))(?=[0-9nkxy(])", "*", text)
    return text


def exact_eval(expression: str, variables: dict[str, Fraction]) -> Fraction:
    tree = ast.parse(expression, mode="eval")

    def visit(node: ast.AST) -> Fraction:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return Fraction(node.value)
        if isinstance(node, ast.Name) and node.id in variables:
            return variables[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return visit(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow):
                assert right.denominator == 1 and right >= 0
                return left ** right.numerator
        raise ValueError(ast.dump(node))

    return visit(tree)


def extract_formulae() -> list[dict]:
    text = SOURCE.read_text(encoding="utf-8")
    start = text.index(" z_1=&")
    end = text.index("\\end{flalign*}", start)
    body = text[start:end]
    starts = list(re.finditer(r"(?m)^\s*z_(?:\{(\d+)\}|(\d+))=&", body))
    assert len(starts) == 208
    answer = []
    for offset, match in enumerate(starts):
        index = int(match.group(1) or match.group(2))
        assert index == offset + 1
        stop = starts[offset + 1].start() if offset + 1 < len(starts) else len(body)
        raw = body[match.end():stop]
        expression = latex_to_python(raw)
        base_variables = {"n": Fraction(N), "k": Fraction(K)}
        a = exact_eval(expression, {**base_variables, "x": Fraction(0), "y": Fraction(0)})
        b = exact_eval(expression, {**base_variables, "x": Fraction(1), "y": Fraction(0)}) - a
        c = exact_eval(expression, {**base_variables, "x": Fraction(0), "y": Fraction(1)}) - a
        # The paper states that n3 and z11 are the only free variables.
        for x, y in ((2, 0), (0, 2), (3, 5)):
            observed = exact_eval(expression, {**base_variables, "x": Fraction(x), "y": Fraction(y)})
            assert observed == a + b * x + c * y
        answer.append({
            "index": index,
            "raw_tex": raw.strip(),
            "python_expression": expression,
            "affine": [a, b, c],
        })
    return answer


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def encode_fraction(value: Fraction) -> int | str:
    if value.denominator == 1:
        return value.numerator
    return f"{value.numerator}/{value.denominator}"


def formula_congruence(coefficients: tuple[Fraction, Fraction, Fraction]) -> tuple[int, int, int, int]:
    denominator = math.lcm(*(value.denominator for value in coefficients))
    integers = tuple(int(value * denominator) for value in coefficients)
    return (*integers, denominator)


def combine_congruence(
    residue_a: int, modulus_a: int, residue_b: int, modulus_b: int
) -> tuple[int, int] | None:
    """Intersect y=r_a (mod m_a) and y=r_b (mod m_b)."""
    common = math.gcd(modulus_a, modulus_b)
    difference = residue_b - residue_a
    if difference % common:
        return None
    reduced_b = modulus_b // common
    if reduced_b == 1:
        return residue_a % modulus_a, modulus_a
    step = (difference // common) * pow(modulus_a // common, -1, reduced_b)
    step %= reduced_b
    modulus = modulus_a * reduced_b
    return (residue_a + modulus_a * step) % modulus, modulus


def y_integrality_class(
    congruences: list[tuple[int, int, int, int]], x: int
) -> tuple[int, int] | None:
    residue, modulus = 0, 1
    for constant, x_coefficient, y_coefficient, denominator in congruences:
        target = -(constant + x_coefficient * x)
        common = math.gcd(y_coefficient, denominator)
        if target % common:
            return None
        reduced_modulus = denominator // common
        if reduced_modulus == 1:
            continue
        reduced_coefficient = y_coefficient // common
        reduced_target = target // common
        required = (reduced_target * pow(reduced_coefficient, -1, reduced_modulus)) % reduced_modulus
        combined = combine_congruence(residue, modulus, required, reduced_modulus)
        if combined is None:
            return None
        residue, modulus = combined
    return residue, modulus


def progression_count(lower: int, upper: int, residue: int, modulus: int) -> tuple[int, int, int] | None:
    first = lower + ((residue - lower) % modulus)
    if first > upper:
        return None
    last = upper - ((upper - residue) % modulus)
    return first, last, (last - first) // modulus + 1


def main() -> None:
    formulae = extract_formulae()
    affine = [tuple(row["affine"]) for row in formulae]
    # z1>=0 gives n3<=4158; n3 and z11 themselves are frequencies.
    congruences = [formula_congruence(row) for row in affine]
    lattice_rows = []
    candidate_count = 0
    minimum_y = None
    maximum_y = None
    feasible_x = []
    active_lower = set()
    active_upper = set()
    for x in range(0, 4158 + 1):
        lower, upper = 0, 10**30
        lower_sources, upper_sources = {11}, set()
        possible = True
        for index, (a, b, c) in enumerate(affine, 1):
            constant = a + b * x
            if c == 0:
                if constant < 0:
                    possible = False
                    break
            elif c > 0:
                bound = ceil_fraction(-constant / c)
                if bound > lower:
                    lower, lower_sources = bound, {index}
                elif bound == lower:
                    lower_sources.add(index)
            else:
                bound = floor_fraction(-constant / c)
                if bound < upper:
                    upper, upper_sources = bound, {index}
                elif bound == upper:
                    upper_sources.add(index)
        if not possible or lower > upper:
            continue
        feasible_x.append(x)
        active_lower.update(lower_sources)
        active_upper.update(upper_sources)
        integrality = y_integrality_class(congruences, x)
        if integrality is None:
            continue
        residue, modulus = integrality
        progression = progression_count(lower, upper, residue, modulus)
        if progression is None:
            continue
        first, last, count = progression
        # Endpoint controls guard the inequality-to-interval conversion.
        for y in {first, last}:
            values = [a + b * x + c * y for a, b, c in affine]
            assert all(value >= 0 and value.denominator == 1 for value in values)
        lattice_rows.append({
            "n3": x,
            "z11_min": first,
            "z11_max": last,
            "z11_residue": residue,
            "z11_modulus": modulus,
            "candidate_pairs": count,
        })
        candidate_count += count
        minimum_y = first if minimum_y is None else min(minimum_y, first)
        maximum_y = last if maximum_y is None else max(maximum_y, last)

    serialized_formulae = []
    for row in formulae:
        copied = dict(row)
        copied["affine"] = [encode_fraction(value) for value in row["affine"]]
        serialized_formulae.append(copied)
    result = {
        "status": "EXACT_FORMULA_LIST_AUDIT_COMPLETE",
        "source": str(SOURCE),
        "source_sha256": sha256(SOURCE),
        "parameters": {"n": N, "k": K},
        "formula_count": len(formulae),
        "parser_checks": {
            "indices_exactly_1_through_208": True,
            "all_expressions_affine_in_n3_z11_at_fixed_n_k": True,
            "exact_rational_arithmetic": True,
        },
        "nonnegative_real_region": {
            "integer_n3_values_with_nonempty_integer_z11_interval": len(feasible_x),
            "minimum_n3": min(feasible_x) if feasible_x else None,
            "maximum_n3": max(feasible_x) if feasible_x else None,
            "active_lower_frequency_indices": sorted(active_lower),
            "active_upper_frequency_indices": sorted(active_upper),
        },
        "nonnegative_integer_frequency_lattice": {
            "candidate_pairs": candidate_count,
            "n3_values": len(lattice_rows),
            "minimum_n3": min((row["n3"] for row in lattice_rows), default=None),
            "maximum_n3": max((row["n3"] for row in lattice_rows), default=None),
            "minimum_z11": minimum_y,
            "maximum_z11": maximum_y,
            "rows": lattice_rows,
        },
        "formulae": serialized_formulae,
        "claim_boundary": (
            "Necessary arithmetic consequences conditional on the 208 displayed "
            "formulae in arXiv:2608.19410v1; their combinatorial derivations are "
            "not independently proved here."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "real_region": result["nonnegative_real_region"],
        "integer_lattice_without_external_n3_bound": {
            key: value
            for key, value in result["nonnegative_integer_frequency_lattice"].items()
            if key != "rows"
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
