#!/usr/bin/env python3
"""Compare two same-size screenshots and optionally emit a heatmap.

Requires Pillow. Exit 0 when configured gates pass, 1 when a gate fails,
and 2 for invalid input or a missing dependency.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

Image = None
ImageChops = None
ImageOps = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure screenshot deltas with optional masking and gates."
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument(
        "--mask",
        type=Path,
        help="Grayscale image where non-black pixels are included in metrics.",
    )
    parser.add_argument("--output", type=Path, help="Write an amplified RGB heatmap.")
    parser.add_argument(
        "--pixel-threshold",
        type=int,
        default=16,
        help="Count a pixel as mismatched when its largest RGB delta exceeds this value.",
    )
    parser.add_argument(
        "--max-mismatch-ratio",
        type=float,
        help="Fail when the mismatched-pixel ratio exceeds this 0..1 value.",
    )
    parser.add_argument(
        "--max-mae",
        type=float,
        help="Fail when mean absolute RGB error exceeds this 0..255 value.",
    )
    return parser.parse_args()


def percentile_from_histogram(histogram: list[int], percentile: float) -> int:
    total = sum(histogram)
    if total == 0:
        return 0
    target = math.ceil(total * percentile)
    cumulative = 0
    for value, count in enumerate(histogram):
        cumulative += count
        if cumulative >= target:
            return value
    return 255


def load_pillow() -> None:
    global Image, ImageChops, ImageOps
    try:
        from PIL import Image as pillow_image
        from PIL import ImageChops as pillow_chops
        from PIL import ImageOps as pillow_ops
    except ImportError:
        print(
            "Pillow is required. Use the Codex bundled Python runtime or install Pillow.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    Image = pillow_image
    ImageChops = pillow_chops
    ImageOps = pillow_ops


def load_rgb(path: Path):
    if not path.is_file():
        raise ValueError(f"Image does not exist: {path}")
    return Image.open(path).convert("RGB")


def main() -> int:
    args = parse_args()
    if not 0 <= args.pixel_threshold <= 255:
        raise ValueError("--pixel-threshold must be between 0 and 255")
    if args.max_mismatch_ratio is not None and not 0 <= args.max_mismatch_ratio <= 1:
        raise ValueError("--max-mismatch-ratio must be between 0 and 1")
    if args.max_mae is not None and not 0 <= args.max_mae <= 255:
        raise ValueError("--max-mae must be between 0 and 255")

    load_pillow()

    reference = load_rgb(args.reference)
    candidate = load_rgb(args.candidate)
    if reference.size != candidate.size:
        raise ValueError(
            f"Screenshot sizes differ: reference={reference.size}, candidate={candidate.size}"
        )

    mask = None
    if args.mask:
        if not args.mask.is_file():
            raise ValueError(f"Mask does not exist: {args.mask}")
        mask = Image.open(args.mask).convert("L")
        if mask.size != reference.size:
            raise ValueError(f"Mask size {mask.size} does not match {reference.size}")
        mask = mask.point(lambda value: 255 if value > 0 else 0)

    difference = ImageChops.difference(reference, candidate)
    red, green, blue = difference.split()
    max_channel = ImageChops.lighter(ImageChops.lighter(red, green), blue)

    max_histogram = max_channel.histogram(mask=mask)
    included_pixels = sum(max_histogram)
    if included_pixels == 0:
        raise ValueError("The mask excludes every pixel")

    rgb_histogram = difference.histogram(mask=mask)
    channel_samples = included_pixels * 3
    absolute_total = sum((index % 256) * count for index, count in enumerate(rgb_histogram))
    squared_total = sum(
        ((index % 256) ** 2) * count for index, count in enumerate(rgb_histogram)
    )
    mismatch_pixels = sum(max_histogram[args.pixel_threshold + 1 :])

    mae = absolute_total / channel_samples
    rmse = math.sqrt(squared_total / channel_samples)
    mismatch_ratio = mismatch_pixels / included_pixels

    failures: list[str] = []
    if args.max_mismatch_ratio is not None and mismatch_ratio > args.max_mismatch_ratio:
        failures.append(
            f"mismatch_ratio {mismatch_ratio:.6f} > {args.max_mismatch_ratio:.6f}"
        )
    if args.max_mae is not None and mae > args.max_mae:
        failures.append(f"mae {mae:.4f} > {args.max_mae:.4f}")

    gates_configured = (
        args.max_mismatch_ratio is not None or args.max_mae is not None
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        amplified = max_channel.point(lambda value: min(255, value * 4))
        heatmap = ImageOps.colorize(amplified, black="#000000", white="#ff3b30")
        if mask is not None:
            heatmap = Image.composite(
                heatmap, Image.new("RGB", reference.size, "black"), mask
            )
        heatmap.save(args.output)

    report = {
        "reference": str(args.reference),
        "candidate": str(args.candidate),
        "mask": str(args.mask) if args.mask else None,
        "size": {"width": reference.width, "height": reference.height},
        "included_pixels": included_pixels,
        "pixel_threshold": args.pixel_threshold,
        "mismatched_pixels": mismatch_pixels,
        "mismatch_ratio": round(mismatch_ratio, 8),
        "mae_rgb": round(mae, 6),
        "rmse_rgb": round(rmse, 6),
        "p95_max_channel_delta": percentile_from_histogram(max_histogram, 0.95),
        "heatmap": str(args.output) if args.output else None,
        "gates_configured": gates_configured,
        "gates": {
            "max_mismatch_ratio": args.max_mismatch_ratio,
            "max_mae": args.max_mae,
        },
        "passed": not failures if gates_configured else None,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not gates_configured or not failures else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
