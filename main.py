from __future__ import annotations

import argparse

from planetary_evolution.game import GameLoop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Turn based planetary evolution simulation")
    parser.add_argument("--seed", type=int, default=None, help="Reuse a known world seed")
    parser.add_argument("--auto", action="store_true", help="Play automatically for testing")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    game = GameLoop(seed=args.seed, auto=args.auto)
    game.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
