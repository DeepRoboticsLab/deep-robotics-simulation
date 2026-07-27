#!/usr/bin/env python3
"""Start a DEEPRobotics simulation by product name."""

from pathlib import Path
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parent


def print_usage() -> None:
    print("Usage: python3 run_sim.py <product>")
    print("Supported products: dr02_pro")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print_usage()
        return 1

    if argv[1] == "dr02_pro":
        from dr02_pro.mujoco_simulation import run

        return run(REPOSITORY_ROOT / "dr02_pro" / "config.yaml")

    print(f"Unknown product: {argv[1]}")
    print_usage()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
