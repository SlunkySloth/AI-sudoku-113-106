from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlphameticSolution:
    mapping: dict[str, int]
    addends: list[str]
    result: str

    def word_value(self, word: str) -> int:
        return int("".join(str(self.mapping[ch]) for ch in word))

    def addends_values(self) -> list[int]:
        return [self.word_value(w) for w in self.addends]

    def result_value(self) -> int:
        return self.word_value(self.result)


class AlphameticError(ValueError):
    pass


def parse_puzzle(expr: str) -> tuple[list[str], str]:
    """
    Parse an expression like 'SEND + MORE = MONEY' into (['SEND','MORE'], 'MONEY').
    Supports any number of addends separated by '+'.
    """
    raw = expr.strip().replace(" ", "").upper()
    if not raw:
        raise AlphameticError("Puzzle is empty.")
    if "=" not in raw:
        raise AlphameticError("Puzzle must contain '=' (e.g., SEND+MORE=MONEY).")

    left, right = raw.split("=", 1)
    if not left or not right:
        raise AlphameticError("Both sides of '=' must be non-empty.")
    addends = [w for w in left.split("+") if w]
    if len(addends) < 1:
        raise AlphameticError("Left side must contain at least one addend.")
    result = right

    words = addends + [result]
    for w in words:
        if not w.isalpha():
            raise AlphameticError("Use letters A-Z only (no digits/symbols inside words).")
        if len(w) == 0:
            raise AlphameticError("Found an empty word.")

    letters = sorted({ch for w in words for ch in w})
    if len(letters) > 10:
        raise AlphameticError(f"Too many unique letters ({len(letters)}). Max is 10.")

    # Typical alphametics need result length >= max(addends length)
    if len(result) < max(len(w) for w in addends):
        raise AlphameticError("Result word is shorter than an addend (no solution for normal addition).")

    return addends, result


def _leading_letters(addends: list[str], result: str) -> set[str]:
    leads: set[str] = set()
    for w in addends + [result]:
        if len(w) > 1:
            leads.add(w[0])
    return leads


def solve_alphametic(expr: str, *, find_all: bool = False, node_limit: int = 5_000_000) -> list[AlphameticSolution]:
    """
    Solve alphametic addition puzzles using a CSP backtracking search with column-wise constraints.
    Returns one solution by default (list of length 0 or 1). If find_all=True, returns all solutions found.
    """
    addends, result = parse_puzzle(expr)
    leads = _leading_letters(addends, result)

    words = addends + [result]
    letters = sorted({ch for w in words for ch in w})

    maxlen = max(len(w) for w in words)

    # Precompute column letter counts for addends and the result letter per column.
    # Column index 0 is rightmost.
    add_counts_per_col: list[dict[str, int]] = []
    res_letter_per_col: list[str | None] = []

    for col in range(maxlen):
        counts: dict[str, int] = {}
        for w in addends:
            idx = len(w) - 1 - col
            if idx >= 0:
                ch = w[idx]
                counts[ch] = counts.get(ch, 0) + 1
        add_counts_per_col.append(counts)

        ridx = len(result) - 1 - col
        res_letter_per_col.append(result[ridx] if ridx >= 0 else None)

    assignment: dict[str, int] = {}
    used: set[int] = set()
    nodes = 0
    solutions: list[AlphameticSolution] = []

    def can_assign(letter: str, digit: int) -> bool:
        if digit in used:
            return False
        if letter in leads and digit == 0:
            return False
        return True

    def assign(letter: str, digit: int) -> None:
        assignment[letter] = digit
        used.add(digit)

    def unassign(letter: str, digit: int) -> None:
        del assignment[letter]
        used.remove(digit)

    def solve_col(col: int, carry: int) -> bool:
        nonlocal nodes
        if nodes >= node_limit:
            return True  # stop search; treat as done
        if col >= maxlen:
            if carry != 0:
                return False
            # All columns satisfied; ensure every letter assigned (may already be true)
            if len(assignment) == len(letters):
                solutions.append(AlphameticSolution(mapping=dict(assignment), addends=addends, result=result))
                return not find_all
            # If some letters never appeared in constrained positions (rare), assign remaining arbitrarily.
            remaining = [ch for ch in letters if ch not in assignment]
            if not remaining:
                solutions.append(AlphameticSolution(mapping=dict(assignment), addends=addends, result=result))
                return not find_all
            # Backfill remaining letters with any unused digits respecting leading constraints.
            def fill(i: int) -> bool:
                if i == len(remaining):
                    solutions.append(AlphameticSolution(mapping=dict(assignment), addends=addends, result=result))
                    return not find_all
                ch = remaining[i]
                for d in range(10):
                    if can_assign(ch, d):
                        assign(ch, d)
                        if fill(i + 1):
                            return True
                        unassign(ch, d)
                return False

            return fill(0)

        add_counts = add_counts_per_col[col]
        res_letter = res_letter_per_col[col]

        # Sum contribution from already-assigned addend letters; collect unassigned add letters.
        sum_known = 0
        unknown_add: list[tuple[str, int]] = []  # (letter, count)
        for ch, cnt in add_counts.items():
            if ch in assignment:
                sum_known += cnt * assignment[ch]
            else:
                unknown_add.append((ch, cnt))

        # Choose digits for unknown add letters in this column.
        def assign_unknown_add(i: int, running_sum: int) -> bool:
            nonlocal nodes
            if nodes >= node_limit:
                return True
            if i == len(unknown_add):
                total = running_sum
                expected_digit = total % 10
                next_carry = total // 10

                if res_letter is None:
                    return False  # should not happen for valid puzzles

                # Enforce result letter digit
                if res_letter in assignment:
                    if assignment[res_letter] != expected_digit:
                        return False
                    return solve_col(col + 1, next_carry)

                if not can_assign(res_letter, expected_digit):
                    return False
                nodes += 1
                assign(res_letter, expected_digit)
                try:
                    return solve_col(col + 1, next_carry)
                finally:
                    unassign(res_letter, expected_digit)

            ch, cnt = unknown_add[i]

            # Lightweight heuristic: try digits in ascending order.
            for d in range(10):
                if not can_assign(ch, d):
                    continue
                nodes += 1
                assign(ch, d)
                try:
                    if assign_unknown_add(i + 1, running_sum + cnt * d):
                        return True
                finally:
                    unassign(ch, d)
            return False

        return assign_unknown_add(0, carry + sum_known)

    solve_col(0, 0)
    return solutions

