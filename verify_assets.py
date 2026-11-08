from pathlib import Path
root = Path(__file__).resolve().parent / "assets"
for kind in ("problems", "solutions"):
    missing = [n for n in range(1, 221) if not (root / kind / f"{n:03}.png").is_file()]
    if missing:
        raise SystemExit(f"Missing {len(missing)} {kind} PNGs, starting with {missing[:5]}")
print("Verified: 220 problems and 220 solutions")
