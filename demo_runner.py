#!/usr/bin/env python3
# demo_runner.py --------------------------------------------------------------
"""
Run any move-string on CUBOTino-T.

* 2024-05-31  Andrea Favero / community helper
* Requires the regular CUBOTino-T project structure on the Pi.

Usage examples
--------------
# basic
python3 demo_runner.py --moves "F1R1S3..."

# flip-to-close in one step and start with cover already OPEN
python3 demo_runner.py --moves "F1..." --fast --start open
"""

import argparse, signal, sys, time

# --- CUBOTino imports --------------------------------------------------------
from Cubotino_T_servos import (
    init_servo,           # initialise HW & get timers
    servo_solve_cube,     # run a move string
    stopping_servos,      # emergency stop
    s_disp,               # tiny OLED/HAT display helper
)

# -----------------------------------------------------------------------------
def graceful_quit(signum, frame):
    print("\n[demo_runner] Interrupt received – stopping servos …")
    stopping_servos()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_quit)      # Ctrl-C
signal.signal(signal.SIGTERM, graceful_quit)     # systemd / kill

# -----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Fire a custom move sequence at CUBOTino-T")
    ap.add_argument("--moves", required=True,
                    help="Move string understood by CUBOTino (F n / R n / S n …).")
    ap.add_argument("--start", default="read", choices=("open", "read", "close"),
                    help="Top-cover position to initialise the robot (default: read).")
    ap.add_argument("--fast", action="store_true",
                    help="Use one-step flip-to-close (sets flip_to_close_one_step flag).")
    ap.add_argument("--quiet", action="store_true", help="Suppress debug printouts.")
    args = ap.parse_args()

    # -------------------------------------------------------------------------
    print("[demo_runner] Initialising servos …")
    ok, timers = init_servo(
        print_out=not args.quiet,
        start_pos=args.start,
        f_to_close_mode=args.fast,
        init_display=True,
    )
    if not ok:
        sys.exit("[demo_runner] Servo init failed – aborting.")

    # -------------------------------------------------------------------------
    print("[demo_runner] Running sequence:")
    print(args.moves)
    robot_status, robot_time = servo_solve_cube(
        moves=args.moves,
        print_out=not args.quiet,
    )

    # -------------------------------------------------------------------------
    print(f"[demo_runner] Finished – {robot_status} in {robot_time:.1f} s")
    s_disp.show_on_display("FINISHED", f"{robot_time:.1f}s", fs1=24, y2=75, fs2=26)
    time.sleep(3)
    stopping_servos()

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# -----------------------------------------------------------------------------
   inv = []
   for token in reversed([(s[i], s[i+1]) for i in range(0, len(s), 2)]):
       move, val = token
       if move == "F":
           inv.append(f"F{val}")              # flips are self-inverse by count
       elif val == "1":                       # CW -> CCW
           inv.append(f"{move}3")
       elif val == "3":                       # CCW -> CW
           inv.append(f"{move}1")
       else:                                  # 0 / 4 stay the same (180°)
           inv.append(f"{move}{val}")
   print("".join(inv))
