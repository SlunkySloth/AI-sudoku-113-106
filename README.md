## AI Problem Solving Assignment (CSP) — Problems 4 and 6

This README documents **two CSP-based GUI programs** in this repository:

- **Problem 4**: Crypt Arithmetic (Alphametic) Puzzle Solver using CSP
- **Problem 6**: Sudoku (Easy level) Solver using CSP

### Repository / folder structure

- `problem4_cryptarithm_csp/`
  - `main.py`: Tkinter GUI (input puzzle, solve, show mapping + computed result)
  - `alphametic_csp.py`: CSP parser + solver (column-wise addition constraints)
- `problem6_sudoku_csp/`
  - `main.py`: Tkinter GUI (interactive input, check, solve, reset)
  - `csp_solver.py`: CSP solver + validators
  - `puzzles.py`: built-in easy puzzles (0 = blank)

---

## Problem 4: Crypt Arithmetic Puzzle Solver (CSP)

### Problem statement

Solve cryptarithmetic expressions like `SEND + MORE = MONEY` where:

- **Each letter maps to a unique digit (0–9)**
- **No number starts with zero**

Finally, display the **valid solution mapping** and the **computed numeric result**.

### CSP approach (Alphametic)

- **Variables**: letters appearing in the puzzle
- **Domains**: digits {0..9}
- **Constraints**:
  - **All-different** across letters
  - **Leading letters ≠ 0** for any multi-letter word
  - **Column-wise addition constraints** with carry from right-to-left

### How to run (Problem 4)

```bash
cd problem4_cryptarithm_csp
python main.py
```

### Example

Input: `SEND + MORE = MONEY`

Typical valid output:

- Mapping like `S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2`
- Computed: `9567 + 1085 = 10652`

---

## Problem 6: Sudoku (Easy level) Solver using CSP

### Constraints

- **Row constraint**: each row contains digits 1–9 without repetition
- **Column constraint**: each column contains digits 1–9 without repetition
- **3×3 subgrid constraint**: each 3×3 box contains digits 1–9 without repetition

### CSP approach (Sudoku)

- **Variables**: each cell \((r,c)\)
- **Domains**: \(\{1,\dots,9\}\) for empty cells (restricted by current constraints)
- **Constraints**: all-different across row/column/box peers

Search strategy:

- **Backtracking search**
- **MRV (Minimum Remaining Values)** to pick the next unassigned cell
- **LCV (Least Constraining Value)** to try values that restrict peers less (lightweight heuristic)
- **Forward-checking** to prune peer domains after each assignment

### How to run (Problem 6)

```bash
cd problem6_sudoku_csp
python main.py
```

### Usage (GUI)

- **Select** an easy puzzle from the dropdown.
- **Fill** empty cells with digits 1–9.
- Click:
  - **Check**: validates constraints; if complete and correct → **You won**
  - **Reset**: returns to the original puzzle
  - **Solve (CSP)**: fills the solved Sudoku grid

### Sample output (typical messages)

- “You won”
- “Try again: there is a constraint violation.”
- “Solved! (nodes expanded: …)”

