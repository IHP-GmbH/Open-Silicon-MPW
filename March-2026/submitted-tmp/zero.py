#!/usr/bin/env python3
"""Remove zero-area polygons on SG13G2 target layers.

Usage (Python):
    python3 zero.py /path/to/input.gds

Usage (KLayout batch):
    klayout -b -r zero.py -rd input_file=/path/to/input.gds

Output is written next to the input as:
    <input_stem>_zero.gds
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import klayout.db as db
except ImportError:
    try:
        import pya as db  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Error: Could not import 'klayout.db' or 'pya'. Ensure KLayout Python module is installed."
        ) from exc


LAYER_SPECS = [
    (1, 0),
    (5, 0),
    (6, 0),
    (7, 0),
    (8, 0),
    (9, 0),
    (10, 0),
    (14, 0),
    (19, 0),
    (20, 0),
    (27, 0),
    (29, 0),
    (30, 0),
    (31, 0),
    (32, 0),
    (36, 0),
    (44, 0),
    (49, 0),
    (50, 0),
    (66, 0),
    (67, 0),
    (72, 0),
    (73, 0),
    (74, 0),
    (75, 0),
    (77, 0),
    (83, 0),
    (84, 0),
    (125, 0),
    (126, 0),
    (128, 0),
    (129, 0),
    (132, 0),
    (133, 0),
    (134, 0),
    (146, 0),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove zero-area polygons on configured layers"
    )
    parser.add_argument("input_file", type=Path, help="Input GDS file (.gds or .gds.gz)")
    parser.add_argument("--output", type=Path, help="Optional output path")
    parser.add_argument("--report", type=Path, help="Optional report file path")
    return parser.parse_args()


def get_paths() -> tuple[Path, Path | None, Path | None]:
    if "input_file" in globals() and globals()["input_file"] is not None:
        in_path = Path(str(globals()["input_file"]))
        out_path = None
        rep_path = None
        if "output_file" in globals() and globals()["output_file"] is not None:
            out_path = Path(str(globals()["output_file"]))
        if "report_file" in globals() and globals()["report_file"] is not None:
            rep_path = Path(str(globals()["report_file"]))
        return in_path, out_path, rep_path
    args = parse_args()
    return args.input_file, args.output, args.report


def validate_input(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Input file not found: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"Input path is not a file: {resolved}")
    suffixes = [s.lower() for s in resolved.suffixes]
    if not suffixes or (suffixes[-1] != ".gds" and suffixes[-2:] != [".gds", ".gz"]):
        raise ValueError(f"Input file must be .gds or .gds.gz: {resolved}")
    if resolved.stat().st_size == 0:
        raise ValueError(f"Input file is empty: {resolved}")
    return resolved


def default_output_path(input_path: Path) -> Path:
    name = input_path.name
    if name.endswith(".gds.gz"):
        stem = name[: -len(".gds.gz")]
    elif name.endswith(".gds"):
        stem = name[: -len(".gds")]
    else:
        stem = input_path.stem
    return input_path.with_name(f"{stem}_zero.gds")


def default_report_path(input_path: Path) -> Path:
    name = input_path.name
    if name.endswith(".gds.gz"):
        stem = name[: -len(".gds.gz")]
    elif name.endswith(".gds"):
        stem = name[: -len(".gds")]
    else:
        stem = input_path.stem
    return input_path.with_name(f"{stem}_zero_report.txt")


def is_zero_area_polygon(shape: db.Shape) -> bool:
    if shape.is_box():
        try:
            b = shape.box
            return b.width() == 0 or b.height() == 0
        except Exception:
            return False

    if shape.is_path():
        try:
            p = shape.path
            if p.width == 0:
                return True
            return p.polygon().area() == 0
        except Exception:
            return False

    if shape.is_polygon():
        try:
            return shape.polygon.area() == 0
        except Exception:
            return False

    if shape.is_simple_polygon():
        try:
            return shape.simple_polygon.area() == 0
        except Exception:
            return False

    return False


def remove_zero_polygons(layout: db.Layout) -> tuple[int, dict[str, int]]:
    total_removed = 0
    removed_by_layer: dict[str, int] = {}

    layer_indices: dict[tuple[int, int], int] = {}

    def _normalize_layer_index(value: object) -> int | None:
        if value is None:
            return None
        try:
            li = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None
        if li < 0:
            return None
        return li

    for layer, datatype in LAYER_SPECS:
        li = layout.find_layer(layer, datatype)
        li_norm = _normalize_layer_index(li)
        if li_norm is not None:
            layer_indices[(layer, datatype)] = li_norm

    for cell in layout.each_cell():
        if cell is None or cell.is_empty():
            continue

        for spec, li in layer_indices.items():
            shapes = cell.shapes(li)
            if shapes.is_empty():
                continue

            candidates = [shape for shape in shapes.each() if is_zero_area_polygon(shape)]
            if not candidates:
                continue

            for shape in candidates:
                shape.delete()

            key = f"{spec[0]}/{spec[1]}"
            removed_by_layer[key] = removed_by_layer.get(key, 0) + len(candidates)
            total_removed += len(candidates)

    return total_removed, removed_by_layer


def process(input_path: Path, output_path: Path) -> tuple[int, dict[str, int]]:
    layout = db.Layout()
    layout.read(str(input_path))
    total_removed, removed_by_layer = remove_zero_polygons(layout)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    layout.write(str(output_path))
    return total_removed, removed_by_layer


def write_report(
    *,
    report_path: Path,
    input_path: Path,
    output_path: Path,
    total_removed: int,
    removed_by_layer: dict[str, int],
) -> None:
    lines = [
        "Zero-area polygon cleanup report",
        f"Input layout (original): {input_path}",
        f"Output layout: {output_path}",
        f"Total zero-area polygons found on original layout: {total_removed}",
        "",
        "Counts by layer:",
    ]
    if removed_by_layer:
        for layer_key in sorted(removed_by_layer):
            lines.append(f"- {layer_key}: {removed_by_layer[layer_key]}")
    else:
        lines.append("- none")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main() -> int:
    try:
        input_arg, output_arg, report_arg = get_paths()
        input_path = validate_input(input_arg)
        output_path = output_arg.expanduser().resolve() if output_arg else default_output_path(input_path)
        report_path = report_arg.expanduser().resolve() if report_arg else default_report_path(input_path)
        total_removed, removed_by_layer = process(input_path, output_path)
        write_report(
            report_path=report_path,
            input_path=input_path,
            output_path=output_path,
            total_removed=total_removed,
            removed_by_layer=removed_by_layer,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Zero-polygon cleanup failed: {exc}", file=sys.stderr)
        return 1

    print(f"Saved cleaned layout: '{output_path}'")
    if total_removed == 0:
        print("No zero-area polygons were found on configured layers.")
    else:
        print(f"Found and fixed {total_removed} zero-area polygon(s).")
        for layer_key in sorted(removed_by_layer):
            print(f"  - layer {layer_key}: {removed_by_layer[layer_key]}")
    print(f"Report written: '{report_path}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
