#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-import CJK glyphs from the Fusion Pixel 12px mono zh_hans BDF into
resources/font.bz2, reproducing the exact committed result.

Usage:
    python resources/cjkfont/import_cjk.py <fusion-pixel-12px-monospaced-zh_hans.bdf> [--repo <repo>]

Requirements: python3 (stdlib only), git, and repo's fonttool.py.
The script resets resources/font.bz2 to HEAD (pristine Latin-only), then runs
fonttool addbdf for the three CJK ranges with yoffs=-2 (critical: preserves the
glyph's full height; default import clips the bottom 2 rows).
"""
import argparse, hashlib, os, subprocess, sys

RANGES = [
    (0x3000, 0x303F),
    (0x4E00, 0x9FFF),
    (0xFF00, 0xFFEF),
]
EXPECTED_BDF_SHA256 = "9CB8F307B8835FF071E62EAA2FD473FA0683D0AE2C5AF8583EB9C5A183953F00"
FONT_REL = os.path.join("resources", "font.bz2")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bdf", help="path to fusion-pixel-12px-monospaced-zh_hans.bdf")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    args = ap.parse_args()

    bdf = os.path.abspath(args.bdf)
    if not os.path.isfile(bdf):
        sys.exit("BDF not found: %s" % bdf)
    actual = sha256(bdf)
    if actual != EXPECTED_BDF_SHA256:
        print("WARNING: BDF sha256 mismatch:\n  got  %s\n  want %s" % (actual, EXPECTED_BDF_SHA256))

    repo = os.path.abspath(args.repo)
    os.chdir(repo)
    if not os.path.isfile("fonttool.py"):
        sys.exit("fonttool.py not found in %s" % repo)

    print("Resetting %s to HEAD (pristine Latin-only font)..." % FONT_REL)
    subprocess.run(["git", "checkout", "HEAD", "--", FONT_REL], check=True)

    for first, last in RANGES:
        print("addbdf U+%04X..U+%04X (yoffs=-2)..." % (first, last))
        subprocess.run(
            ["python", "fonttool.py", "addbdf", str(first), str(last), bdf, "0", "-2"],
            check=True,
        )
    print("Done. New %s written." % FONT_REL)
    print("Verify: only additions vs HEAD, Latin untouched (addbdf never overwrites).")


if __name__ == "__main__":
    main()
