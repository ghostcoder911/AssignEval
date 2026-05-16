"""Test case definitions for all 27 assignment questions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class TestCase:
    name: str
    stdin: str
    # any of these patterns must appear in output (case-insensitive)
    expect_patterns: tuple[str, ...]
    # patterns that must NOT appear
    reject_patterns: tuple[str, ...] = ()
    weight: float = 1.0


Checker = Callable[[str, str], tuple[bool, str]]


def _has_all(output: str, patterns: tuple[str, ...]) -> bool:
    out = output.lower()
    return all(re.search(p, out, re.IGNORECASE) for p in patterns)


def _has_any(output: str, patterns: tuple[str, ...]) -> bool:
    out = output.lower()
    return any(re.search(p, out, re.IGNORECASE) for p in patterns)


def _nums(output: str) -> list[int]:
    return [int(x) for x in re.findall(r"-?\d+", output)]


def check_test(case: TestCase, stdout: str, stderr: str) -> tuple[bool, str]:
    combined = f"{stdout}\n{stderr}"
    if case.reject_patterns and _has_any(combined, case.reject_patterns):
        return False, f"Unexpected output matching {case.reject_patterns}"
    if case.expect_patterns and not _has_all(combined, case.expect_patterns):
        return False, f"Expected patterns {case.expect_patterns} not found in output"
    return True, "OK"


def check_fibonacci(stdout: str, _stderr: str, terms: int) -> tuple[bool, str]:
    nums = _nums(stdout)
    if len(nums) < terms:
        return False, f"Expected at least {terms} Fibonacci terms in output"
    seq = nums[:terms]
    if terms >= 1 and seq[0] != 0:
        return False, f"Fibonacci should start with 0, got {seq}"
    if terms >= 2 and seq[1] != 1:
        return False, f"Second Fibonacci term should be 1, got {seq}"
    for i in range(2, terms):
        if seq[i] != seq[i - 1] + seq[i - 2]:
            return False, f"Invalid Fibonacci sequence: {seq}"
    return True, "OK"


def check_digit_freq(stdout: str, _stderr: str, digit: int, count: int) -> tuple[bool, str]:
    pat = rf"digit\s*{digit}\s*[=:]\s*{count}|{digit}.*{count}|frequency.*{digit}.*{count}"
    if re.search(pat, stdout, re.IGNORECASE):
        return True, "OK"
    # looser: digit and count appear
    if str(digit) in stdout and str(count) in stdout:
        return True, "OK"
    return False, f"Expected frequency of digit {digit} to be {count}"


def check_array_contains(stdout: str, expected: list[int]) -> tuple[bool, str]:
    nums = _nums(stdout)
    if not nums:
        return False, "No numbers in output"
    # try to find contiguous subsequence
    for i in range(len(nums) - len(expected) + 1):
        if nums[i : i + len(expected)] == expected:
            return True, "OK"
    # or check multiset for unique-array style
    if sorted(nums[-len(expected) :]) == sorted(expected):
        return True, "OK"
    if expected == sorted(set(expected)) and sorted(set(nums)) == sorted(expected):
        return True, "OK"
    return False, f"Expected array {expected}, got numbers {nums}"


# Per-question test suites: (test_cases, optional custom_checkers keyed by test name)
QUESTION_TESTS: dict[int, list[TestCase]] = {
    1: [
        TestCase("even_positive", "4\n", ("even",)),
        TestCase("odd_negative", "-3\n", ("odd",)),
        TestCase("even_zero", "0\n", ("even",)),
    ],
    2: [
        TestCase("prime_7", "7\n", (r"prime",), (r"not\s*prime",)),
        TestCase("not_prime_4", "4\n", (r"not\s*prime",)),
        TestCase("not_prime_1", "1\n", (r"not\s*prime",)),
    ],
    3: [
        TestCase("factorial_5", "5\n", (r"120",)),
        TestCase("factorial_0", "0\n", (r"\b1\b",)),
    ],
    4: [
        TestCase("fib_5_terms", "5\n", (), ()),
        TestCase("fib_1_term", "1\n", (r"\b0\b",)),
    ],
    5: [
        TestCase("perfect_6", "6\n", (r"perfect",), (r"not\s*perfect",)),
        TestCase("not_perfect_8", "8\n", (r"not\s*perfect",)),
    ],
    6: [
        TestCase("gcd_48_18", "48\n18\n", (r"\b6\b",)),
        TestCase("gcd_17_13", "17\n13\n", (r"\b1\b",)),
    ],
    7: [
        TestCase("freq_11221", "11221\n", (r"1.*2|2.*1|frequency",)),
    ],
    8: [
        TestCase("dec_to_hex", "255\n16\n", (r"ff",)),
        TestCase("dec_to_bin", "5\n2\n", (r"101",)),
    ],
    9: [
        TestCase("add", "3\n4\n+\n", (r"7",)),
        TestCase("multiply", "6\n7\n*\n", (r"42",)),
        TestCase("div_zero", "5\n0\n/\n", (r"zero|error|invalid|divide",)),
    ],
    10: [
        TestCase("str_to_int", "1234\n", (r"\b1234\b",)),
        TestCase("negative", "-42\n", (r"-42|\b42\b",)),
    ],
    11: [
        TestCase("int_to_str", "1234\n", (r"1234",)),
        TestCase("zero", "0\n", (r"\b0\b",)),
    ],
    12: [
        TestCase("palindrome_yes", "madam\n", (r"palindrom",), (r"not\s*palindrom",)),
        TestCase("palindrome_no", "hello\n", (r"not\s*palindrom",)),
    ],
    13: [
        TestCase("reverse", "hello\n", (r"olleh",)),
    ],
    14: [
        TestCase(
            "pangram_yes",
            # fits typical char buffers (30–40) used in student code
            "abcdefghijklmnopqrstuvwxyz\n",
            (r"pangram",),
            (r"not\s*a?\s*pangram",),
        ),
        TestCase("pangram_no", "hello\n", (r"not\s*a?\s*pangram",)),
    ],
    15: [
        TestCase("spaces", "hello   world\n", (r"hello world",)),
    ],
    16: [
        TestCase("tolower", "HeLLo\n", (r"hello",)),
    ],
    17: [
        TestCase("toggle", "12\n2\n1\n", (r"\b1[45]\b|\b1[0-9]\b",)),
    ],
    18: [
        TestCase("extract", "29\n3\n2\n", (r"\b7\b",)),
    ],
    19: [
        TestCase("replace", "15\n7\n2\n1\n", (r"\b1[35]\b|\b17\b|\b19\b",)),
    ],
    20: [
        TestCase("swap_bits", "12\n15\n2\n1\n", (r"\d+\s+\d+",)),
    ],
    21: [
        TestCase(
            "unique",
            "6\n12 34 24 12 34 27\n",
            (r"12.*34.*24.*27|12\s+34\s+24\s+27",),
        ),
    ],
    22: [
        TestCase(
            "second",
            "6\n12 27 48 10 54 7\n",
            (r"48", r"10|second\s+largest.*48",),
        ),
    ],
    23: [
        TestCase(
            "rotate_left",
            "6\n1 2 3 4 5 6\n2\nL\n",
            (r"3\s+4\s+5\s+6\s+1\s+2|3.*4.*5.*6.*1.*2",),
        ),
    ],
    24: [
        TestCase(
            "merge",
            "4\n12 37 39 58\n5\n7 19 28 35 46\n",
            (r"7.*12.*19|7\s+12\s+19",),
        ),
    ],
    25: [
        TestCase(
            "pairs",
            "6\n24 12 18 25 8 6\n30\n",
            (r"24.*6|12.*18|pair",),
        ),
    ],
    26: [
        TestCase(
            "rearrange",
            "6\n12 -37 29 -68 39 -10\n",
            (r"-37|-68|-10",),
        ),
    ],
    27: [
        TestCase(
            "complex_add",
            "3\n5\n2\n7\n",
            (r"5.*12|5\s*\+|real.*5|5.*i.*12|12",),
        ),
    ],
}


CUSTOM_CHECKERS: dict[int, dict[str, Checker]] = {
    4: {
        "fib_5_terms": lambda o, e: check_fibonacci(o, e, 5),
        "fib_1_term": lambda o, e: check_fibonacci(o, e, 1),
    },
    7: {
        "freq_11221": lambda o, e: check_digit_freq(o, e, 1, 2),
    },
    21: {
        "unique": lambda o, e: check_array_contains(o, [12, 34, 24, 27]),
    },
    22: {
        "second": lambda o, e: (
            (True, "OK")
            if "48" in o and "10" in o
            else (False, "Expected second largest 48 and second smallest 10")
        ),
    },
    23: {
        "rotate_left": lambda o, e: check_array_contains(o, [3, 4, 5, 6, 1, 2]),
    },
    24: {
        "merge": lambda o, e: check_array_contains(
            o, [7, 12, 19, 28, 35, 37, 39, 46, 58]
        ),
    },
}


STATIC_CHECKS: dict[int, list[tuple[str, str]]] = {
    6: [(r"\bgcd\b.*\bgcd\b|\bhcf\b", "GCD should use a recursive or repeated Euclidean approach")],
    9: [(r"float|double", "Should use floating-point numbers")],
    27: [(r"struct|typedef\s+struct", "Should define a structure for Complex")],
}
