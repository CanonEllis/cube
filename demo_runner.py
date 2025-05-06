#!/usr/bin/env python3
"""
demo_runner.py – run a custom move-string on CUBOTino-T.

USAGE
-----
python3 demo_runner.py --moves "F1R1S3…"          # run sequence
python3 demo_runner.py --moves "F1…" --start open # start with cover open
python3 demo_runner.py --moves "F1…" --fast       # one-step flip-to-close
python3 demo_runner.py --moves "F1…" --quiet      # minimal output
Ctrl-C / SIGTERM always stop the servos cleanly.
"""

import argparse, signal, sys, time
from Cubotino_T_servos import init_servo, servo_solve_cube, stopping_servos
import Cubotino_T_servos as ct          # we’ll fetch ct.s_disp after init()

def _quit(*_):
    stopping_servos()
    sys.exit(0)

signal.signal(signal.SIGINT,  _quit)
signal.signal(signal.SIGTERM, _quit)

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Fire a custom move sequence at CUBOTino-T")
    ap.add_argument("--moves", required=True,
                    help="Move string understood by servo_solve_cube()")
    ap.add_argument("--start", default="read",
                    choices=("open", "read", "close"))
    ap.add_argument("--fast",  action="store_true",
                    help="Enable one-step flip-to-close")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    ok, _ = init_servo(print_out=not args.quiet,
                       start_pos=args.start,
                       f_to_close_mode=args.fast,
                       init_display=True)
    if not ok:
        sys.exit("Servo initialisation failed.")

    status, t = servo_solve_cube(moves=args.moves, print_out=not args.quiet)
    print(f"{status} in {t:.1f}s")

    # display result on the OLED/HAT – now s_disp exists
    ct.s_disp.show_on_display("FINISHED", f"{t:.1f}s",
                              fs1=24, y2=75, fs2=26)
    time.sleep(3)
    stopping_servos()

if __name__ == "__main__":
    main()
