# Submission guidelines

> **Warning**
> Read this document carefully before starting the implementation.

## Overview

This repository aggregates production-ready IPs as submodules. IP development and
release preparation happen in standalone repositories. When ready, a submission request
is made to include the IP as a submodule under the relevant MPW category directory.

Four directory structures are available, corresponding to Analog, Digital, RF, and
Mixed-Signal design categories.

## Categories

### Category table

Categories and subcategories are standardized. Select the correct subcategory before
generation and keep the category consistent with the repository placement under
`March-2026/<Category>`. Subcategories map to fixed abbreviations and those abbreviations
must be used in the top-level IP name and kept consistent with `doc/info.json`. If you
would like to add more subcategories or abbreviations, request them via a GitHub issue on
[Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW).

| Category | Subcategory | Abbreviation |
| --- | --- | --- |
| Analog | Bandgap Reference | BGR |
| Analog | Comparator | CMP |
| Analog | Operational Amplifier | OPA |
| Analog | Low Dropout Regulator | LDO |
| Analog | Voltage Reference | VREF |
| Analog | Charge Pump | CP |
| Analog | Temperature Sensor | TSENSE |
| Analog | Oscillator | OSC |
| Analog | Power Management IC | PMIC |
| Digital | Microcontroller | MCU |
| Digital | Microprocessor | MPU |
| Digital | RISC-V Core | RISCV |
| Digital | Memory Controller | MEMCTRL |
| Digital | DMA Controller | DMA |
| Digital | Security Engine | SEC |
| Digital | Cryptographic Accelerator | CRYPTO |
| Digital | Interconnect/Fabric | NOC |
| Digital | GPIO | GPIO |
| Digital | Timer/Counter | TIMER |
| Digital | UART | UART |
| Digital | SPI | SPI |
| Digital | I2C | I2C |
| Mixed-Signal | Analog to Digital Converter | ADC |
| Mixed-Signal | Digital to Analog Converter | DAC |
| Mixed-Signal | Phase-Locked Loop | PLL |
| Mixed-Signal | Sigma-Delta Modulator | SDM |
| Mixed-Signal | Clock and Data Recovery | CDR |
| Mixed-Signal | SerDes | SERDES |
| Mixed-Signal | Mixed-Signal PHY | MSPHY |
| RF | Low Noise Amplifier | LNA |
| RF | Power Amplifier | PA |
| RF | Mixer | MIX |
| RF | Voltage-Controlled Oscillator | VCO |
| RF | RF PLL | RFPLL |
| RF | Frequency Synthesizer | FSYN |
| RF | RF Front End | RFFE |
| RF | RF Switch | RFSW |
| RF | Balun | BALUN |

## Submission process

### Steps

1) Select category and subcategory.

   Select the category and subcategory that match the IP and confirm the
   abbreviation that will appear in the top-level IP name and repository path.

2) Clone the Open-Silicon-MPW repository.

   Clone the [Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW)
   repository locally to obtain the `gen_structure.py` script.

3) Generate the IP repository structure.

   Run the generator outside the [Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW)
   repository to create a new IP repo skeleton.

   ```
   python3 gen_structure.py <technology> <subcategory> [dependency1 dependency2 ...]
   ```

   > **Tip**
   > Dependencies can be submodules, provided they follow the same IP structure
   > conventions as the top-level repository.

   > **Note**
   > `technology` must be `IHP`.

4) Develop and document the IP.

   In the standalone IP repository:

   - Implement the design and keep the directory layout intact.
   - Keep the top cell name aligned with the generated name (for example,
     `OPA-4532`) across all views in the repository.
   - Maintain `doc/info.json` with accurate metadata, release paths, and
     dependencies.
   - Fill the corresponding Technology Readiness Level (TRL) document under
     `doc/`.
   - Populate `release/<version>/` with production-ready deliverables (GDS,
     netlist, and supporting documentation).

5) Publish the IP repository.

   Initialize a Git repository and push it to GitHub.

   ```
   git init
   git add .
   git commit -s -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<org>/<repo>.git
   git push -u origin main
   ```

6) Sync shared workflows (optional but recommended).

   If the generated IP repo includes `check-workflow-sync.yml`, it will stage
   workflow updates from [Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW)
   into `.github/workflows-staged/` and open an issue describing what was staged.

   > **Tip**
   > To activate a staged workflow, copy it manually into `.github/workflows/`.

7) Request submodule inclusion.

   Open a GitHub issue in [Open-Silicon-MPW](https://github.com/IHP-GmbH/Open-Silicon-MPW)
   requesting the submodule addition. Include a copy-ready `.gitmodules` snippet:

   ```
   ## Submodule request

   - Repository URL: https://github.com/<org>/<repo>.git
   - Category directory: March-2026/<Category> (Analog, Digital, RF, Mixed-Signal)
   - Submodule path: March-2026/<Category>/IHP__<subcategory-abbrev>-<4digits>

   ### .gitmodules snippet

   [submodule "March-2026/<Category>/IHP__<subcategory-abbrev>-<4digits>"]
     path = March-2026/<Category>/IHP__<subcategory-abbrev>-<4digits>
     url = https://github.com/<org>/<repo>.git
   ```

## Physical verification

### Verification flow

Physical verification is expected to be automated and reproducible. The flow
performs DRC and LVS using the official IHP SG13G2 KLayout decks. It resolves
`release.gds` and `release.netlist` from `doc/info.json` before any tool
installation. If neither is referenced, the flow exits early with a warning and
skips both stages. If a reference is present but the file is missing, the run
fails immediately. When a layout is present without a netlist, DRC runs and LVS
is skipped with a warning; LVS requires both artifacts.

> **Warning**
> If `release.gds` or `release.netlist` is referenced in `doc/info.json`
> but the file is missing, the verification run fails immediately.

The flow installs minimal system prerequisites (`jq` and `python3-pip`), then
selects a KLayout package matching the runner's Ubuntu major version. It
validates the downloaded package before installation to avoid toolchain
mismatches. Python dependencies are installed from the IHP Open PDK
requirements. The official DRC and LVS rule decks are fetched via a sparse
checkout to keep the download lightweight and deterministic.

DRC runs with the official deck and pre-checks enabled, writing results to a
dedicated temporary directory. LVS runs only when both layout and netlist are
present, writing results to a separate temporary directory. Both result
directories are uploaded as artifacts even when a stage fails, enabling
post-mortem analysis and consistent traceability across submissions. Ensure
`doc/info.json` paths match actual deliverables and that release files can be
consumed by the automated flow without manual intervention.

> **Tip**
> Keep release artifacts and their paths in `doc/info.json` aligned before
> triggering verification to avoid avoidable re-runs.

## Acceptance criteria

### Checklist

Submissions are expected to meet the following:

- The repository matches the generated structure and naming convention.
- `doc/info.json` is complete and correct.
- Release data is present under `release/<version>/` with paths referenced in
  `doc/info.json`.
- Dependencies are present under `dependencies/` and follow the same structure
  (submodules are acceptable).

> **Note**
> A submission-ready GDS must satisfy the complete sign-off checklist:
>
> 1. A seal ring must be present.
> 2. Filler cells must be generated and included.
> 3. The layout must be DRC clean, including the minimal rules in
>    https://github.com/IHP-GmbH/IHP-Open-PDK/blob/main/ihp-sg13g2/libs.tech/klayout/tech/drc/docs/precheck_rules.md.
> 4. The layout must be LVS clean against the final netlist.
> 5. The final release under `release/<version>/` must be saved using the KLayout
>    options shown in the figure below.

![KLayout save options for release GDS](fig/klayout_save.png)

### IP preparation checklist

- [ ] Category and subcategory selected; abbreviation matches naming.
- [ ] Repository follows the generated structure and naming convention.
- [ ] Top cell name matches the generated name across all views.
- [ ] `doc/info.json` is complete and current.
- [ ] TRL document is present under `doc/`.
- [ ] Dependencies are listed under `dependencies/` and follow the structure.
- [ ] `release/<version>/` contains final GDS and netlist.
- [ ] Release paths in `doc/info.json` resolve to existing files.
- [ ] Seal ring present.
- [ ] Fillers generated and included.
- [ ] DRC clean (including minimal precheck rules).
- [ ] LVS clean against the final netlist.
- [ ] Final GDS saved with the documented KLayout options.
