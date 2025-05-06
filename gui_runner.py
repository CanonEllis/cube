#!/usr/bin/env python3
"""
 gui_runner.py – interactive GUI for CUBOTino-T servo control
 ------------------------------------------------------------------
 A small Tkinter interface that lets you build and fire move strings
 at CUBOTino-T by clicking buttons.  It wraps demo_runner.py logic
 so that illegal moves or runtime errors are surfaced to the user
 without terminating the program.

 - Buttons for common cube moves (F1, R1, R3, S1, S3)
 - Entry box shows / lets you edit the current move string
 - Dropdowns for start position, fast-mode and quiet output
 - "Run" executes the current string
 - Errors are caught and shown via messagebox; the GUI keeps running
 - Clean shutdown ensures servos are stopped even on window close

 Usage
 -----
 $ python3 gui_runner.py          # launches the window

 Requirements: same Python env as demo_runner.py (Tkinter + Cubotino)
"""
import signal
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox

from Cubotino_T_servos import init_servo, servo_solve_cube, stopping_servos
import Cubotino_T_servos as ct  # ct.s_disp is created after init_servo

# ------------------------------------------------------------
class CubotinoGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("CUBOTino-T Controller")
        master.resizable(False, False)

        # state ------------------------------------------------
        self.move_var   = tk.StringVar()
        self.start_pos  = tk.StringVar(value="read")
        self.fast_mode  = tk.BooleanVar(value=False)
        self.quiet_mode = tk.BooleanVar(value=False)
        self.servo_ok   = False

        # layout ----------------------------------------------
        self._build_controls()

        # ensure clean quit on Ctrl-C or window close ----------
        signal.signal(signal.SIGINT,  self._quit)
        signal.signal(signal.SIGTERM, self._quit)
        master.protocol("WM_DELETE_WINDOW", self._quit)

    # ---------- UI construction -----------------------------
    def _build_controls(self):
        frm = ttk.Frame(self.master, padding=12)
        frm.grid()

        # Move string entry
        ttk.Label(frm, text="Move string:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frm, textvariable=self.move_var, width=30)
        entry.grid(row=0, column=1, columnspan=5, pady=4, sticky="ew")

        # Move buttons
        moves = ["F1", "R1", "R3", "S1", "S3"]
        for i, m in enumerate(moves, start=1):
            ttk.Button(frm, text=m, width=4, command=lambda mv=m: self._append_move(mv))\
                .grid(row=1, column=i-1, padx=2, pady=4)
        ttk.Button(frm, text="Clear", command=lambda: self.move_var.set(""))\
            .grid(row=1, column=len(moves), padx=6)

        # Options
        opts = ttk.LabelFrame(frm, text="Options", padding=6)
        opts.grid(row=2, column=0, columnspan=6, pady=6, sticky="ew")

        # start position radios
        for col, pos in enumerate(("open", "read", "close")):
            ttk.Radiobutton(opts, text=pos.capitalize(), variable=self.start_pos, value=pos)\
                .grid(row=0, column=col, padx=4, sticky="w")

        # checkboxes
        ttk.Checkbutton(opts, text="Fast",  variable=self.fast_mode).grid(row=0, column=3, padx=8)
        ttk.Checkbutton(opts, text="Quiet", variable=self.quiet_mode).grid(row=0, column=4, padx=4)

        # Run button & status
        ttk.Button(frm, text="Run", style="Accent.TButton", command=self._run_moves, width=10)\
            .grid(row=3, column=0, columnspan=2, pady=8)
        self.status_lbl = ttk.Label(frm, text="Servo not initialised.")
        self.status_lbl.grid(row=3, column=2, columnspan=4, sticky="w")

    # ---------- callbacks -----------------------------------
    def _append_move(self, mv: str):
        cur = self.move_var.get().strip()
        self.move_var.set((cur + mv).strip())

    def _init_servo(self):
        ok, _ = init_servo(print_out=not self.quiet_mode.get(),
                           start_pos=self.start_pos.get(),
                           f_to_close_mode=self.fast_mode.get(),
                           init_display=True)
        self.servo_ok = ok
        self.status_lbl.config(text="Servo ready." if ok else "Servo init failed!")
        return ok

    def _run_moves(self):
        moves = self.move_var.get().strip()
        if not moves:
            return messagebox.showinfo("No moves", "Please enter or build a move string first.")

        if not self.servo_ok and not self._init_servo():
            return  # already informed

        try:
            status, t = servo_solve_cube(moves=moves, print_out=not self.quiet_mode.get())
            if status.lower().startswith("ko"):
                messagebox.showerror("Illegal move", status)
                self.status_lbl.config(text="Error: illegal move")
            else:
                self.status_lbl.config(text=f"Finished in {t:.1f}s")
                # OLED/HAT display
                if hasattr(ct, "s_disp"):
                    ct.s_disp.show_on_display("FINISHED", f"{t:.1f}s", fs1=24, y2=75, fs2=26)
            # small pause so user sees display change
            time.sleep(0.5)
        except Exception as exc:
            messagebox.showerror("Runtime error", str(exc))
            self.status_lbl.config(text="Error – see dialog")

    # ---------- graceful quit -------------------------------
    def _quit(self, *_):
        try:
            stopping_servos()
        finally:
            self.master.destroy()
            sys.exit(0)

# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    CubotinoGUI(root)
    root.mainloop()
