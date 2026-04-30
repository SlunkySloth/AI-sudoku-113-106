from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from alphametic_csp import AlphameticError, solve_alphametic


SAMPLES: list[str] = [
    "SEND + MORE = MONEY",
    "TWO + TWO = FOUR",
    "I + BB = ILL",
    "BASE + BALL = GAMES",
]


def _format_mapping(mapping: dict[str, int]) -> str:
    items = sorted(mapping.items(), key=lambda kv: kv[0])
    return "\n".join(f"{k} = {v}" for k, v in items)


def _substitute(expr: str, mapping: dict[str, int]) -> str:
    raw = expr.strip().replace(" ", "").upper()
    out = []
    for ch in raw:
        if ch.isalpha():
            out.append(str(mapping[ch]))
        else:
            out.append(ch)
    return "".join(out)


class CryptGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Crypt Arithmetic Solver (CSP)")
        self.root.resizable(False, False)

        self.puzzle_var = tk.StringVar(value=SAMPLES[0])
        self.find_all_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Enter a puzzle like SEND + MORE = MONEY, then click Solve.")

        self._build_ui()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.grid(row=0, column=0, sticky="nsew")

        top = ttk.Frame(outer)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(top, text="Puzzle:").grid(row=0, column=0, padx=(0, 8))
        entry = ttk.Entry(top, textvariable=self.puzzle_var, width=34)
        entry.grid(row=0, column=1, padx=(0, 8))
        entry.focus_set()

        sample_box = ttk.Combobox(top, state="readonly", values=SAMPLES, width=26)
        sample_box.grid(row=0, column=2, padx=(0, 8))
        sample_box.set("Samples")
        sample_box.bind("<<ComboboxSelected>>", lambda _e: self.puzzle_var.set(sample_box.get()))

        ttk.Button(top, text="Solve", command=self._solve).grid(row=0, column=3)

        opts = ttk.Frame(outer)
        opts.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Checkbutton(opts, text="Find all solutions (can be slow)", variable=self.find_all_var).grid(row=0, column=0, sticky="w")

        ttk.Label(outer, textvariable=self.status_var).grid(row=2, column=0, sticky="w", pady=(10, 6))

        out = ttk.Frame(outer)
        out.grid(row=3, column=0, sticky="nsew")

        self.text = tk.Text(out, width=78, height=18, wrap="word")
        self.text.grid(row=0, column=0, sticky="nsew")
        self.text.configure(state="disabled", font=("Consolas", 11))

        scroll = ttk.Scrollbar(out, command=self.text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scroll.set)

        btns = ttk.Frame(outer)
        btns.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(btns, text="Clear Output", command=self._clear).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Quit", command=self.root.destroy).grid(row=0, column=1)

    def _clear(self) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.configure(state="disabled")
        self.status_var.set("Output cleared.")

    def _write(self, s: str) -> None:
        self.text.configure(state="normal")
        self.text.insert(tk.END, s)
        self.text.configure(state="disabled")
        self.text.see(tk.END)

    def _solve(self) -> None:
        expr = self.puzzle_var.get().strip()
        self.status_var.set("Solving with CSP...")
        self.root.update_idletasks()

        try:
            sols = solve_alphametic(expr, find_all=self.find_all_var.get())
        except AlphameticError as e:
            self.status_var.set("Invalid puzzle.")
            messagebox.showerror("Invalid puzzle", str(e))
            return
        except Exception as e:  # safety net
            self.status_var.set("Error while solving.")
            messagebox.showerror("Error", f"Unexpected error: {e}")
            return

        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.configure(state="disabled")

        if not sols:
            self.status_var.set("No solution found.")
            self._write("No solution found.\n")
            return

        self.status_var.set(f"Found {len(sols)} solution(s).")
        for i, sol in enumerate(sols, start=1):
            mapping = sol.mapping
            sub = _substitute(expr, mapping)
            add_vals = sol.addends_values()
            res_val = sol.result_value()
            self._write(f"Solution {i}\n")
            self._write("-" * 72 + "\n")
            self._write("Mapping:\n")
            self._write(_format_mapping(mapping) + "\n\n")
            self._write(f"Substituted: {sub}\n")
            self._write(f"Computed:    {' + '.join(map(str, add_vals))} = {res_val}\n")
            self._write("\n")


def main() -> None:
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    CryptGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

