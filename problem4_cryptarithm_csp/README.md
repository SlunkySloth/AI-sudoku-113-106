## Problem 4: Crypt Arithmetic Puzzle Solver (CSP)

This folder contains a Python **GUI crypt-arithmetic (alphametic) solver**.
The user can input a puzzle such as `SEND + MORE = MONEY` and the program finds digits for
letters so that the arithmetic equation is satisfied.

### Requirements satisfied

- **Each letter maps to a unique digit (0–9)** (all-different constraint)
- **No number starts with zero** (leading-letter constraint)
- Displays **valid mapping** and the **computed numeric result**

### CSP formulation

- **Variables**: letters (A–Z) appearing in the puzzle
- **Domains**: digits {0..9} for each letter
- **Constraints**:
  - all letters have **different** digits
  - leading letters of any multi-letter word cannot be 0
  - the full **column-wise addition** must hold with carries

### Algorithm

Backtracking CSP solver with strong pruning using **column-by-column constraints**:

- works from the **rightmost column** to the left
- maintains a **carry**
- assigns digits only when consistent with the current column’s required sum

### Files

- `main.py`: Tkinter GUI (input puzzle, choose sample, solve, show mapping)
- `alphametic_csp.py`: parser + CSP solver

### How to run

From this folder:

```bash
python main.py
```

### Example

Input:

`SEND + MORE = MONEY`

Output:

- a mapping like `S=9, E=5, N=6, D=7, M=1, O=0, R=8, Y=2`
- computed result `9567 + 1085 = 10652`

