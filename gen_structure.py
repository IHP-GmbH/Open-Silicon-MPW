#!/usr/bin/env python3
# Copyright 2026 IHP OPEN PDK Authors
# SPDX-License-Identifier: Apache-2.0
import json
import os
import random
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path


def usage() -> None:
    print("Usage:")
    print("  ./generate_structure.py <technology> <subcategory> [dependency1 dependency2 ...]")
    print("")
    print("Example:")
    print("  ./generate_structure.py IHP ADC VCO")


def load_categories(categories_source: str) -> dict:
    if categories_source.startswith(("http://", "https://")):
        with urllib.request.urlopen(categories_source) as handle:
            return json.loads(handle.read().decode("utf-8"))
    categories_path = Path(categories_source)
    with categories_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_key(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def resolve_category(categories: dict, category_arg: str) -> str:
    normalized = normalize_key(category_arg)
    for category_name in categories.keys():
        if normalize_key(category_name) == normalized:
            return category_name
    raise ValueError(f"Unknown category: {category_arg}")


def resolve_subcategory(categories: dict, category: str, subcategory_arg: str) -> tuple[str, str]:
    subcategories = categories.get(category, {})
    normalized = normalize_key(subcategory_arg)
    for full_name, abbreviation in subcategories.items():
        if normalize_key(full_name) == normalized or normalize_key(abbreviation) == normalized:
            return full_name, abbreviation
    raise ValueError(f"Unknown subcategory '{subcategory_arg}' for category '{category}'")


def resolve_category_from_subcategory(categories: dict, subcategory_arg: str) -> tuple[str, str, str]:
    normalized = normalize_key(subcategory_arg)
    for category_name, subcategories in categories.items():
        for full_name, abbreviation in subcategories.items():
            if normalize_key(full_name) == normalized or normalize_key(abbreviation) == normalized:
                return category_name, full_name, abbreviation
    raise ValueError(f"Unknown subcategory: {subcategory_arg}")


def normalize_trl_url(url: str) -> str:
    if url.startswith("https://github.com/") and "/blob/" in url:
        return url.replace("github.com/", "raw.githubusercontent.com/").replace("/blob/", "/")
    return url


def write_trl_template(
    base_dir: str,
    mode: str,
    trl_source: str,
    fallback_dir: Path,
) -> None:
    trl_name_map = {
        "A": "TRL-Analog.md",
        "D": "TRL-Digital-Hard-IP.md",
        "M": "TRL-Mixed-Signal-IP.md",
        "R": "TRL-RF.md",
        "P": "TRL-Photonics.md",
    }
    trl_filename = trl_name_map[mode]
    trl_path = os.path.join(base_dir, "doc", trl_filename)
    if os.path.isfile(trl_path):
        return

    if trl_source.startswith(("http://", "https://")):
        trl_url = f"{normalize_trl_url(trl_source).rstrip('/')}/{trl_filename}"
        try:
            urllib.request.urlretrieve(trl_url, trl_path)
            return
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            fallback_path = fallback_dir / trl_filename
            if fallback_path.is_file():
                shutil.copyfile(fallback_path, trl_path)
                return
            raise FileNotFoundError(
                "TRL template download failed and no local template found. "
                f"Provide '{trl_filename}' under '{os.path.join(base_dir, 'doc')}' "
                "or ensure TRL-templates are available locally."
            ) from exc

    local_base = Path(trl_source)
    if not local_base.is_absolute():
        local_base = (fallback_dir.parent / local_base).resolve()
    local_path = local_base / trl_filename
    if not local_path.is_file():
        raise FileNotFoundError(
            "TRL template not found. "
            f"Provide '{trl_filename}' under '{os.path.join(base_dir, 'doc')}' "
            "or ensure TRL-templates are available locally."
        )
    shutil.copyfile(local_path, trl_path)


def write_workflow_template(
    base_dir: str,
    workflow_source: str,
    fallback_dir: Path,
) -> None:
    workflow_filename = "check-workflow-sync.yml"
    workflows_base = os.path.join(base_dir, ".github", "workflows")
    os.makedirs(workflows_base, exist_ok=True)
    workflow_path = os.path.join(workflows_base, workflow_filename)
    if os.path.isfile(workflow_path):
        return

    if workflow_source.startswith(("http://", "https://")):
        workflow_url = f"{workflow_source.rstrip('/')}/{workflow_filename}"
        try:
            urllib.request.urlretrieve(workflow_url, workflow_path)
            return
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            fallback_path = fallback_dir / workflow_filename
            if fallback_path.is_file():
                shutil.copyfile(fallback_path, workflow_path)
                return
            raise FileNotFoundError(
                "Workflow template download failed and no local template found. "
                f"Provide '{workflow_filename}' under '{fallback_dir}' "
                "or ensure workflows are available locally."
            ) from exc

    local_base = Path(workflow_source)
    if not local_base.is_absolute():
        local_base = (fallback_dir.parent / local_base).resolve()
    local_path = local_base / workflow_filename
    if not local_path.is_file():
        raise FileNotFoundError(
            "Workflow template not found. "
            f"Provide '{workflow_filename}' under '{fallback_dir}' "
            "or ensure workflows are available locally."
        )
    shutil.copyfile(local_path, workflow_path)


def create_cell_structure(base: str, cell_name: str, mode: str) -> None:
    if mode == "D":
        base_paths = [
            "rtl",
            "constraints/sdc",
            "synthesis/netlist",
            "synthesis/sdf",
            "synthesis/reports",
            "PlaceAndRoute/netlist",
            "PlaceAndRoute/gds",
            "PlaceAndRoute/lef",
            "PlaceAndRoute/def",
            "PlaceAndRoute/timing/sdf",
            "PlaceAndRoute/timing/lib",
            "PlaceAndRoute/parasitics/spef",
            "Flow/scripts/LibreLane",
            "Flow/scripts/ORFS",
            "testbenches",
            "verification/lint",
            "verification/cdc",
            "verification/drc",
            "verification/lvs",
            "verification/sta",
            "verification/lec",
        ]
    else:
        base_paths = [
            "schematic/xschem",
            "schematic/qucs-s",
            "layout/klayout",
            "layout/magic",
            "layout/lef",
            "layout/def",
            "model/spice",
            "model/verilog-A",
            "netlist/schematic",
            "netlist/layout",
            "netlist/pex",
            "netlist/rcx",
            "verification/drc",
            "verification/lvs",
            "testbenches/ac/xschem",
            "testbenches/tran/xschem",
            "testbenches/noise/xschem",
            "testbenches/corners/xschem",
            "testbenches/ac/qucs-s",
            "testbenches/tran/qucs-s",
            "testbenches/noise/qucs-s",
            "testbenches/corners/qucs-s",
        ]

    if mode == "M":
        base_paths.insert(6, "timing")

    if mode == "R":
        base_paths.insert(-1, "testbenches/em")

    for rel_path in base_paths:
        os.makedirs(os.path.join(base, rel_path), exist_ok=True)

    readme_path = os.path.join(base, "README.md")
    if not os.path.isfile(readme_path):
        with open(readme_path, "w", encoding="utf-8") as handle:
            handle.write(f"# {cell_name}\n\n")
            handle.write(f"Notes for cell `{cell_name}`.\n")


def create_ip_structure(
    base: str,
    ip_name: str,
    mode: str,
    description: str,
    tech: str,
    unique_id: str,
    release_version: str,
    process: str,
    pdk_version: str,
    license_type: str,
    trl_value: int,
    repository_link: str,
    dependencies: dict,
    tools_used: dict,
    trl_source: str,
    fallback_dir: Path,
    workflow_source: str,
    workflow_fallback_dir: Path,
) -> None:
    os.makedirs(os.path.join(base, "doc"), exist_ok=True)
    release_base = os.path.join(base, "release", release_version)
    os.makedirs(release_base, exist_ok=True)
    measurements_base = os.path.join(base, "measurements", release_version)
    os.makedirs(measurements_base, exist_ok=True)
    os.makedirs(os.path.join(release_base, "gds"), exist_ok=True)
    os.makedirs(os.path.join(release_base, "netlist"), exist_ok=True)
    os.makedirs(os.path.join(release_base, "doc"), exist_ok=True)
    os.makedirs(os.path.join(base, "dependencies"), exist_ok=True)

    doc_files = [
        "Datasheet.md",
        "Specification.md",
    ]
    for doc_file in doc_files:
        doc_path = os.path.join(base, "doc", doc_file)
        if not os.path.isfile(doc_path):
            with open(doc_path, "w", encoding="utf-8"):
                pass

    info_path = os.path.join(base, "doc", "info.json")
    if not os.path.isfile(info_path):
        with open(info_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "name": ip_name,
                    "design_type": mode,
                    "technology": tech,
                    "unique_id": unique_id,
                    "license": license_type,
                    "trl": trl_value,
                    "repository": repository_link,
                    "pdk_version": pdk_version,
                    "process": process,
                    "dependencies": dependencies,
                    "tools": tools_used,
                    "release": {
                        "version": release_version,
                        "gds": f"release/{release_version}/gds",
                        "netlist": f"release/{release_version}/netlist",
                        "doc": f"release/{release_version}/doc",
                    },
                },
                handle,
                indent=2,
            )
            handle.write("\n")

    write_trl_template(base, mode, trl_source, fallback_dir)
    write_workflow_template(base, workflow_source, workflow_fallback_dir)

    release_note_path = os.path.join(base, "release", release_version, "ReleaseNote.md")
    if not os.path.isfile(release_note_path):
        with open(release_note_path, "w", encoding="utf-8"):
            pass

    readme_path = os.path.join(base, "README.md")
    if not os.path.isfile(readme_path):
        with open(readme_path, "w", encoding="utf-8") as handle:
            handle.write(f"# {ip_name}\n\n")
            handle.write(f"{description}\n\n")
            handle.write("- doc/     : user documentation\n")
            handle.write("- dependencies/ : sub-cells and blocks\n")
            handle.write("- release/v.1.0.0 : immutable versioned deliveries\n")

    top_cell_name = f"{ip_name}-main"
    create_cell_structure(os.path.join(base, top_cell_name), top_cell_name, mode)


def main() -> int:
    if len(sys.argv) < 3:
        usage()
        return 1

    tech_arg = sys.argv[1]
    subcategory_arg = sys.argv[2]
    cells = sys.argv[3:]

    tech_options = {"SKY", "IHP", "GF"}
    tech = tech_arg.strip().upper()
    if tech not in tech_options:
        raise ValueError(
            f"Unknown technology: {tech_arg}. Expected one of: {', '.join(sorted(tech_options))}"
        )

    repo_raw_base = "https://raw.githubusercontent.com/IHP-GmbH/Open-Silicon-MPW/main"
    categories_url = f"{repo_raw_base}/ip-categories.json"
    categories_path = Path(__file__).resolve().parent / "ip-categories.json"
    try:
        categories = load_categories(categories_url)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        categories = {}

    if categories_path.is_file():
        local_categories = load_categories(str(categories_path))
        if not categories:
            categories = local_categories
        else:
            for category_name, subcategories in local_categories.items():
                categories.setdefault(category_name, {})
                for sub_name, abbreviation in subcategories.items():
                    categories[category_name].setdefault(sub_name, abbreviation)
    try:
        category, subcategory_full, subcategory_abbrev = resolve_category_from_subcategory(
            categories,
            subcategory_arg,
        )
    except ValueError as exc:
        if categories_path.is_file():
            categories = load_categories(str(categories_path))
            category, subcategory_full, subcategory_abbrev = resolve_category_from_subcategory(
                categories,
                subcategory_arg,
            )
        else:
            raise exc

    mode_map = {
        "Analog": "A",
        "Digital": "D",
        "Mixed-Signal": "M",
        "RF": "R",
        "Photonics": "P",
    }
    mode = mode_map[category]

    ip_suffix = f"{random.randint(0, 9999):04d}"
    unique_id = ip_suffix
    ip_name = f"{subcategory_abbrev}-{ip_suffix}"
    root = f"{tech}__{ip_name}"
    release_version = "v.1.0.0"
    process = "SG13G2"
    pdk_version = ""
    license_type = "Apache-2.0"
    trl_value = 0
    repository_link = ""
    dependencies = {cell: {"dependencies": {}} for cell in cells}
    tools_used = {}

    description = "Single-technology IP library."
    if mode == "R":
        description = "Design data."

    trl_source = f"{repo_raw_base}/TRL-templates/"
    fallback_dir = Path(__file__).resolve().parent / "TRL-templates"
    workflow_source = f"{repo_raw_base}/workflows"
    workflow_fallback_dir = Path(__file__).resolve().parent / "workflows"

    create_ip_structure(
        root,
        ip_name,
        mode,
        description,
        tech,
        unique_id,
        release_version,
        process,
        pdk_version,
        license_type,
        trl_value,
        repository_link,
        dependencies,
        tools_used,
        trl_source,
        fallback_dir,
        workflow_source,
        workflow_fallback_dir,
    )

    for cell in cells:
        base = os.path.join(root, "dependencies", cell)
        create_ip_structure(
            base,
            cell,
            mode,
            description,
            tech,
            unique_id,
            release_version,
            process,
            pdk_version,
            license_type,
            trl_value,
            repository_link,
            {},
            tools_used,
            trl_source,
            fallback_dir,
            workflow_source,
            workflow_fallback_dir,
        )

    print(f"IP library created: {root}")
    print(f"Category: {category}")
    print(f"Subcategory: {subcategory_full} ({subcategory_abbrev})")
    print(f"Top cell: {ip_name}")
    print(f"IP cells: {' '.join(cells)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
