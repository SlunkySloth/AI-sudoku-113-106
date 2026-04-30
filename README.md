## Problem 6: Sudoku (Easy level) Solver using CSP

This folder contains a **Python Sudoku GUI** where a user solves a 9×9 Sudoku interactively.
The system can **check** the current entries and shows **“You won”** or **“Try again”**.
It can also **solve** the puzzle using a **Constraint Satisfaction Problem (CSP)** approach.

### Constraints

- **Row constraint**: each row contains digits 1–9 without repetition
- **Column constraint**: each column contains digits 1–9 without repetition
- **3×3 subgrid constraint**: each 3×3 box contains digits 1–9 without repetition

### Algorithm (CSP approach)

The solver models Sudoku as a CSP:

- **Variables**: each cell \((r,c)\)
- **Domains**: \(\{1,\dots,9\}\) for empty cells (restricted by current constraints)
- **Constraints**: all-different across row/column/box peers

Search strategy:

- **Backtracking search**
- **MRV (Minimum Remaining Values)** to pick the next unassigned cell
- **LCV (Least Constraining Value)** to try values that restrict peers less (lightweight heuristic)
- **Forward-checking** to prune peer domains after each assignment

### Folder structure

- `main.py`: Tkinter GUI (interactive input, check, solve, reset)
- `csp_solver.py`: CSP solver + validators
- `puzzles.py`: built-in easy puzzles (0 = blank)

### How to run

From this folder:

```bash
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

