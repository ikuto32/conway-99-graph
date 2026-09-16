"""Exact affine audit of the 208 order-seven formulas at (99,14,1,2).

This is an exploratory source-transcription check.  It parses the displayed
formula block in Reimbayev's arXiv:2608.19410 source, specializes n=99,k=14,
and enumerates the already necessary congruence box

    n3 in {708,711,...,4158},  z11 == 0 (mod 4),  2*n3 <= z11 <= 4*n3.

The parser uses exact Fraction arithmetic and refuses nonlinear dependence on
n3 or z11.  A feasible pair means only that all 208 *displayed* frequencies
are nonnegative integers; it is not a graph or an overlap-consistent deck.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import re


SOURCE = Path("scratch_reimbayev_2608_19410_source/The_Subgraphs_of_Order_Seven.tex")
OUTPUT = Path("scratch_root_z208_affine_audit.json")


class Polynomial:
    """Tiny exact polynomial in x=n3 and y=z11."""

    def __init__(self, terms=None):
        self.terms = {
            monomial: Fraction(coefficient)
            for monomial, coefficient in (terms or {}).items()
            if coefficient
        }

    @staticmethod
    def constant(value):
        return Polynomial({(0, 0): Fraction(value)})

    @staticmethod
    def variable(which):
        return Polynomial({(1, 0) if which == "x" else (0, 1): Fraction(1)})

    def __add__(self, other):
        other = as_polynomial(other)
        answer = defaultdict(Fraction, self.terms)
        for monomial, coefficient in other.terms.items():
            answer[monomial] += coefficient
        return Polynomial(answer)

    __radd__ = __add__

    def __neg__(self):
        return Polynomial({monomial: -coefficient for monomial, coefficient in self.terms.items()})

    def __sub__(self, other):
        return self + (-as_polynomial(other))

    def __rsub__(self, other):
        return as_polynomial(other) - self

    def __mul__(self, other):
        other = as_polynomial(other)
        answer = defaultdict(Fraction)
        for (x1, y1), left in self.terms.items():
            for (x2, y2), right in other.terms.items():
                answer[(x1 + x2, y1 + y2)] += left * right
        return Polynomial(answer)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = as_polynomial(other)
        if set(other.terms) - {(0, 0)} or not other.terms.get((0, 0)):
            raise ValueError("division by a nonconstant or zero polynomial")
        return Polynomial({key: value / other.terms[(0, 0)] for key, value in self.terms.items()})

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("only nonnegative integral powers are supported")
        answer = Polynomial.constant(1)
        for _ in range(exponent):
            answer *= self
        return answer

    def affine(self):
        bad = [key for key in self.terms if key not in {(0, 0), (1, 0), (0, 1)}]
        if bad:
            raise ValueError(f"nonlinear monomials: {bad}")
        return tuple(self.terms.get(key, Fraction(0)) for key in ((0, 0), (1, 0), (0, 1)))


def as_polynomial(value):
    return value if isinstance(value, Polynomial) else Polynomial.constant(value)


TOKEN = re.compile(r"\\frac|n_3|z_\{11\}|[nk]|\d+|[+\-*/^(){}]")


class Parser:
    def __init__(self, source: str):
        cleaned = source.replace(r"\left", "").replace(r"\right", "")
        cleaned = cleaned.replace(r"\\&", "").replace("&", "").replace(" ", "")
        self.tokens = TOKEN.findall(cleaned)
        residue = TOKEN.sub("", cleaned)
        if residue:
            raise ValueError(f"unparsed source residue {residue!r} in {source!r}")
        self.position = 0

    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def take(self, expected=None):
        token = self.peek()
        if token is None or (expected is not None and token != expected):
            raise ValueError(f"expected {expected!r}, found {token!r}")
        self.position += 1
        return token

    def parse(self):
        value = self.expression()
        if self.peek() is not None:
            raise ValueError(f"trailing token {self.peek()!r}")
        return value

    def expression(self):
        value = self.term()
        while self.peek() in {"+", "-"}:
            operator = self.take()
            right = self.term()
            value = value + right if operator == "+" else value - right
        return value

    def term(self):
        value = self.unary()
        while True:
            token = self.peek()
            if token in {"*", "/"}:
                operator = self.take()
                right = self.unary()
                value = value * right if operator == "*" else value / right
            elif token is not None and token not in {"+", "-", ")", "}"}:
                # TeX juxtaposition, e.g. nk(k-2)n_3.
                value *= self.unary()
            else:
                return value

    def unary(self):
        if self.peek() == "+":
            self.take("+")
            return self.unary()
        if self.peek() == "-":
            self.take("-")
            return -self.unary()
        value = self.atom()
        if self.peek() == "^":
            self.take("^")
            token = self.take()
            if token == "{":
                exponent = int(self.take())
                self.take("}")
            else:
                exponent = int(token)
            value = value ** exponent
        return value

    def group(self):
        opening = self.take()
        closing = ")" if opening == "(" else "}"
        value = self.expression()
        self.take(closing)
        return value

    def atom(self):
        token = self.peek()
        if token == r"\frac":
            self.take()
            numerator = self.group()
            denominator = self.group()
            return numerator / denominator
        if token in {"(", "{"}:
            return self.group()
        self.take()
        if token.isdigit():
            return Polynomial.constant(int(token))
        if token == "n":
            return Polynomial.constant(99)
        if token == "k":
            return Polynomial.constant(14)
        if token == "n_3":
            return Polynomial.variable("x")
        if token == "z_{11}":
            return Polynomial.variable("y")
        raise ValueError(f"unexpected token {token!r}")


def fraction_text(value: Fraction):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def parse_formulas():
    pattern = re.compile(r"^\s*z_(?:\{(\d+)\}|(\d+))=&(.*?)[,.]\\\\\s*$")
    formulas = {}
    raw = {}
    for line_number, line in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.match(line)
        if not match:
            continue
        index = int(match.group(1) or match.group(2))
        rhs = match.group(3)
        if index in formulas:
            raise ValueError(f"duplicate z_{index}")
        polynomial = Parser(rhs).parse()
        formulas[index] = polynomial.affine()
        raw[index] = {"line": line_number, "rhs": rhs}
    if set(formulas) != set(range(1, 209)):
        raise ValueError(f"formula index mismatch: {sorted(set(range(1, 209)) - set(formulas))}")
    return formulas, raw


def value(coefficients, n3, z11):
    constant, x_coefficient, y_coefficient = coefficients
    return constant + x_coefficient * n3 + y_coefficient * z11


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_multiple(value: Fraction, modulus: int) -> int:
    return modulus * ceil_fraction(value / modulus)


def floor_multiple(value: Fraction, modulus: int) -> int:
    return modulus * floor_fraction(value / modulus)


def main():
    formulas, raw = parse_formulas()
    # Guard the two identities used in the E0 first-moment derivation.
    assert formulas[1] == (Fraction(4158), Fraction(-1), Fraction(0))
    assert formulas[2] == (Fraction(0), Fraction(1), Fraction(-1, 4))
    assert formulas[3] == (Fraction(0), Fraction(-2), Fraction(1))

    feasible = []
    rejected_by = defaultdict(int)
    # On n3 == 0 (mod 3), z11 == 0 (mod 4), integrality is invariant
    # throughout the enumerated lattice.  Prove that before reducing every
    # n3 slice to its exact interval of nonnegativity.
    for coefficients in formulas.values():
        constant, x_coefficient, y_coefficient = coefficients
        assert (constant + 708 * x_coefficient).denominator == 1
        assert (3 * x_coefficient).denominator == 1
        assert (4 * y_coefficient).denominator == 1
    for n3 in range(708, 4159, 3):
        lower = ((2 * n3 + 3) // 4) * 4
        upper = 4 * n3
        lower_sources = []
        upper_sources = []
        impossible_sources = []
        for index, (constant, x_coefficient, y_coefficient) in formulas.items():
            intercept = constant + x_coefficient * n3
            if y_coefficient > 0:
                candidate = ceil_multiple(-intercept / y_coefficient, 4)
                if candidate > lower:
                    lower = candidate
                    lower_sources = [index]
                elif candidate == lower:
                    lower_sources.append(index)
            elif y_coefficient < 0:
                candidate = floor_multiple(-intercept / y_coefficient, 4)
                if candidate < upper:
                    upper = candidate
                    upper_sources = [index]
                elif candidate == upper:
                    upper_sources.append(index)
            elif intercept < 0:
                impossible_sources.append(index)
        if impossible_sources or lower > upper:
            for index in impossible_sources + lower_sources + upper_sources:
                rejected_by[index] += 1
            continue
        # Every multiple of four in this interval is now nonnegative and
        # integral in all 208 rows; retain only its exact aggregate effects.
        for z11 in range(lower, upper + 1, 4):
            e0_sum = 8316 - n3 - z11 // 4
            feasible.append((n3, z11, e0_sum))

    if not feasible:
        status = "NO_PAIR_SATISFIES_ALL_208_DISPLAYED_FORMULAS"
        summary = {"feasible_pairs": 0}
    else:
        by_n3 = defaultdict(list)
        for n3, z11, e0_sum in feasible:
            by_n3[n3].append((z11, e0_sum))
        minimum = min(feasible, key=lambda item: (item[2], item[0], item[1]))
        maximum = max(feasible, key=lambda item: (item[2], -item[0], -item[1]))
        status = "DISPLAYED_FORMULA_FEASIBLE_PAIRS_EXIST"
        summary = {
            "feasible_pairs": len(feasible),
            "feasible_n3_values": len(by_n3),
            "n3_min": min(by_n3),
            "n3_max": max(by_n3),
            "minimum_E0_sum_pair": {"n3": minimum[0], "z11": minimum[1], "sum_E0": minimum[2]},
            "maximum_E0_sum_pair": {"n3": maximum[0], "z11": maximum[1], "sum_E0": maximum[2]},
            "E0_average_interval": [
                fraction_text(Fraction(minimum[2], 99)),
                fraction_text(Fraction(maximum[2], 99)),
            ],
            "boundary_rows": [
                {
                    "n3": n3,
                    "z11_min": min(z for z, _ in values),
                    "z11_max": max(z for z, _ in values),
                    "feasible_z11_count": len(values),
                    "sum_E0_min": min(e for _, e in values),
                    "sum_E0_max": max(e for _, e in values),
                }
                for n3, values in sorted(by_n3.items())
                if n3 in {min(by_n3), max(by_n3), 708, 711, 4155, 4158}
            ],
        }

    result = {
        "status": status,
        "scope": (
            "Exact nonnegative-integral feasibility of the 208 displayed affine "
            "frequency formulas only; not an overlap-consistent deck or graph."
        ),
        "source": str(SOURCE),
        "parameters": {"n": 99, "k": 14, "n3_range": [708, 4158, 3], "z11_modulus": 4},
        "formula_count": len(formulas),
        "affine_formulas": {
            str(index): {
                "constant": fraction_text(coefficients[0]),
                "n3_coefficient": fraction_text(coefficients[1]),
                "z11_coefficient": fraction_text(coefficients[2]),
                **raw[index],
            }
            for index, coefficients in formulas.items()
        },
        "E0_first_moment": {
            "sum_S": "2*z1=8316-2*n3",
            "sum_D": "z2=n3-z11/4",
            "sum_E0": "2*z1+z2=8316-n3-z11/4",
        },
        "summary": summary,
        "most_frequent_rejection_rows": [
            {"z_index": index, "rejected_candidates": count}
            for index, count in sorted(rejected_by.items(), key=lambda item: (-item[1], item[0]))[:20]
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
