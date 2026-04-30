from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from csp_solver import Grid, is_grid_valid, is_solved, solve_csp
from puzzles import PUZZLES


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


class SudokuGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sudoku Solver (CSP) - Interactive")
        self.root.resizable(False, False)

        self.selected_puzzle = tk.StringVar(value=next(iter(PUZZLES.keys())))
        self.status_var = tk.StringVar(value="Fill the empty cells (1-9) and click Check.")

        self.base_grid: Grid = _copy_grid(PUZZLES[self.selected_puzzle.get()])
        self.solution_grid: Grid | None = None

        self._entries: list[list[tk.Entry]] = [[None for _ in range(9)] for _ in range(9)]  # type: ignore[assignment]

        self._build_ui()
        self._load_puzzle(self.selected_puzzle.get())

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.grid(row=0, column=0, sticky="nsew")

        top = ttk.Frame(outer)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(top, text="Puzzle:").grid(row=0, column=0, padx=(0, 8))
        puzzle_names = list(PUZZLES.keys())
        puzzle_box = ttk.Combobox(top, state="readonly", values=puzzle_names, textvariable=self.selected_puzzle, width=22)
        puzzle_box.grid(row=0, column=1, padx=(0, 12))
        puzzle_box.bind("<<ComboboxSelected>>", lambda _e: self._load_puzzle(self.selected_puzzle.get()))

        ttk.Button(top, text="Reset", command=self._reset_to_base).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(top, text="Check", command=self._check).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(top, text="Solve (CSP)", command=self._solve).grid(row=0, column=4)

        grid_frame = ttk.Frame(outer, padding=(0, 12, 0, 8))
        grid_frame.grid(row=1, column=0)

        vcmd = (self.root.register(self._validate_cell), "%P")

        for r in range(9):
            for c in range(9):
                cell_frame = ttk.Frame(grid_frame, padding=0, borderwidth=0)
                cell_frame.grid(row=r, column=c, padx=(2 if c % 3 else 6, 2), pady=(2 if r % 3 else 6, 2))

                e = tk.Entry(
                    cell_frame,
                    width=2,
                    justify="center",
                    font=("Helvetica", 16),
                    validate="key",
                    validatecommand=vcmd,
                )
                e.grid(row=0, column=0)
                self._entries[r][c] = e

        bottom = ttk.Frame(outer)
        bottom.grid(row=2, column=0, sticky="ew")
        ttk.Label(bottom, textvariable=self.status_var).grid(row=0, column=0, sticky="w")

    def _validate_cell(self, proposed: str) -> bool:
        if proposed == "":
            return True
        if len(proposed) > 1:
            return False
        return proposed in "123456789"

    def _load_puzzle(self, name: str) -> None:
        self.base_grid = _copy_grid(PUZZLES[name])
        self.solution_grid = None
        self.status_var.set("Fill the empty cells (1-9) and click Check.")

        for r in range(9):
            for c in range(9):
                e = self._entries[r][c]
                e.configure(state="normal")
                e.delete(0, tk.END)
                val = self.base_grid[r][c]
                if val != 0:
                    e.insert(0, str(val))
                    e.configure(state="readonly", readonlybackground="#E9ECEF", fg="#212529")
                else:
                    e.configure(bg="white", fg="#212529")

    def _reset_to_base(self) -> None:
        self._load_puzzle(self.selected_puzzle.get())

    def _get_user_grid(self) -> Grid:
        grid: Grid = [[0 for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                s = self._entries[r][c].get().strip()
                grid[r][c] = int(s) if s else 0
        return grid

    def _check(self) -> None:
        grid = self._get_user_grid()

        # Ensure user didn't overwrite givens.
        for r in range(9):
            for c in range(9):
                if self.base_grid[r][c] != 0 and grid[r][c] != self.base_grid[r][c]:
                    self.status_var.set("Try again: you changed a pre-filled cell.")
                    messagebox.showwarning("Try again", "You changed a pre-filled cell. Use Reset if needed.")
                    return

        if not is_grid_valid(grid):
            self.status_var.set("Try again: there is a constraint violation.")
            messagebox.showinfo("Try again", "There is a constraint violation in a row, column, or 3×3 box.")
            return

        if is_solved(grid):
            self.status_var.set("You won!")
            messagebox.showinfo("You won", "You solved the Sudoku correctly.")
            return

        self.status_var.set("So far so good — keep going.")
        messagebox.showinfo("Keep going", "No violations found yet, but the puzzle isn't complete.")

    def _solve(self) -> None:
        grid = self._get_user_grid()

        # Keep givens intact; if user entered contradicting values, refuse to solve.
        for r in range(9):
            for c in range(9):
                if self.base_grid[r][c] != 0 and grid[r][c] != self.base_grid[r][c]:
                    self.status_var.set("Cannot solve: pre-filled cell modified.")
                    messagebox.showwarning("Cannot solve", "A pre-filled cell was modified. Click Reset and try again.")
                    return

        if not is_grid_valid(grid):
            self.status_var.set("Cannot solve: current grid has violations.")
            messagebox.showwarning("Cannot solve", "Current grid violates Sudoku constraints. Fix it or Reset.")
            return

        self.status_var.set("Solving with CSP...")
        self.root.update_idletasks()

        res = solve_csp(grid)
        if not res.solved or res.solution is None:
            self.status_var.set("No solution found (or search limit reached).")
            messagebox.showinfo("No solution", "No solution found for this grid (or search limit reached).")
            return

        self.solution_grid = res.solution
        self._render_solution(res.solution)
        self.status_var.set(f"Solved! (nodes expanded: {res.nodes_expanded})")
        messagebox.showinfo("Solved", "Solved Sudoku grid has been filled in.")

    def _render_solution(self, solution: Grid) -> None:
        for r in range(9):
            for c in range(9):
                e = self._entries[r][c]
                e.configure(state="normal")
                e.delete(0, tk.END)
                e.insert(0, str(solution[r][c]))
                if self.base_grid[r][c] != 0:
                    e.configure(state="readonly", readonlybackground="#E9ECEF", fg="#212529")
                else:
                    e.configure(state="normal", bg="#F8F9FA", fg="#212529")


def main() -> None:
    root = tk.Tk()
    # ttk theme for nicer defaults
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

