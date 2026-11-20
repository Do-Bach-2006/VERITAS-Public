# MalGuise — How To Run

This guide covers running MalGuise evaluation on the `data/Test_part_2` split packaged with the source code.

## 1. Extract Archive

If using `.7z`:

```bash
7z x MalGuise_with_Test_part_2.7z
cd MalGuise
```

If using `.zip`:

```bash
unzip MalGuise_with_Test_part_2.zip
cd MalGuise
```

After extraction, the directory layout should be:

```text
MalGuise/
  actions/
  cfg/
  core/
  data/
    Test_part_2/
      Locker/
      Mediyes/
      Zbot/
      Zeroaccess/
  detector/
  pipeline/
  scripts/
  search/
  requirements.txt
  requirements_det.txt
  setup.sh
```

## 2. Verify Dataset

Run from inside `MalGuise/`:

```bash
find data/Test_part_2 -mindepth 2 -maxdepth 2 -type f | sed 's#^data/Test_part_2/##; s#/.*##' | sort | uniq -c
```

Expected counts per family:

```text
49 Locker
290 Mediyes
420 Zbot
138 Zeroaccess
```

Total executable count:

```bash
find data/Test_part_2 -mindepth 2 -maxdepth 2 -type f -name "*.exe" | wc -l
```

Expected total:

```text
897
```

## 3. Environment Setup

Recommended environment: Linux/Ubuntu with Python 3.10 and sufficient disk space. The setup script creates a dedicated virtual environment for the detector at `detector/det_venv`.

Run:

```bash
chmod +x setup.sh
./setup.sh
```

If system packages for Python virtual environments are missing, install them first:

```bash
sudo apt update
sudo apt install -y python3-venv python3-dev build-essential p7zip-full unzip
```

Then re-run:

```bash
./setup.sh
```

## 4. Verify Black-Box MAGIC Detector

The default detector for batch evaluation is `magic`. The detector workflow is:

```text
PE bytes
  -> detector/MAGIC adapter writes temporary sample.exe
  -> detector/MSACFG/prepare_data.py extracts ASM via angr
  -> detector/MAGIC/maldefender/acfg_pipeline.py builds ACFG
  -> detector/MAGIC/maldefender/predict_model.py loads .pt checkpoint
  -> submission.csv
  -> MalwareProb + is_malware returned to MCTS
```

Run a single-file smoke test before launching a large batch:

```bash
MPLCONFIGDIR=/tmp/matplotlib python3 -c "from pathlib import Path; import sys; sys.path.insert(0, '.'); from detector.magic_adapter import MagicAdapter; sample=next(Path('data/Test_part_2/Zbot').glob('*.exe')); d=MagicAdapter('detector/MAGIC'); r=d.predict(sample.read_bytes()); print(sample); print('MalwareProb=', r.malware_prob, 'is_malware=', r.is_malware)"
```

If configured properly, the command prints the sample path, `MalwareProb`, and `is_malware`.

## 5. Run Batch Evaluation

Choose the worker count based on available CPU cores and `/tmp` capacity (`angr -> ACFG -> predict_model.py` is compute- and I/O-intensive).

```text
Recommended workers = 16 to 24
```

Run batch evaluation:

```bash
MPLCONFIGDIR=/tmp/matplotlib python3 scripts/batch_evaluate.py \
  --data-dir data/Test_part_2 \
  --results-dir results \
  --c-budget 40 \
  --max-length 6 \
  --workers 24 \
  --timeout 1800 \
  --resume
```

`--timeout 1800` enforces a 30-minute hard limit per sample. MCTS uses a soft time budget roughly 2 minutes shorter than the hard timeout and stops early as soon as a candidate evades MAGIC (`is_malware=False`).

## 6. Resuming Interrupted Runs

To resume after an interruption, re-run the same command with `--resume`:

```bash
MPLCONFIGDIR=/tmp/matplotlib python3 scripts/batch_evaluate.py \
  --data-dir data/Test_part_2 \
  --results-dir results \
  --c-budget 40 \
  --max-length 6 \
  --workers 24 \
  --timeout 1800 \
  --resume
```

With `--resume`, the script skips samples that already have `results/<Family>/<SampleId>/<SampleId>_adv_result.json` or `results/<Family>/<SampleId>/<SampleId>_adv_failure.json`. Add `--retry-failed` to re-run failed/timed-out samples, or `--retry-best-effort` to re-run non-evasive best-effort samples.

## 7. Output Layout

Successful outputs are organized by malware family:

```text
results/
  Locker/
    <sample_id>/
      <sample_id>_adv.exe
      <sample_id>_adv_result.json
      <sample_id>_adv_final_cfg.json
  Mediyes/
    <sample_id>/
      <sample_id>_adv.exe
      <sample_id>_adv_result.json
      <sample_id>_adv_final_cfg.json
  Zbot/
    <sample_id>/
      <sample_id>_adv.exe
      <sample_id>_adv_result.json
      <sample_id>_adv_final_cfg.json
  Zeroaccess/
    <sample_id>/
      <sample_id>_adv.exe
      <sample_id>_adv_result.json
      <sample_id>_adv_final_cfg.json
```

## 8. Monitor Progress

In another terminal inside `MalGuise/`, run:

```bash
find results -name "*_adv_result.json" | wc -l
find results -name "*_adv.exe" | wc -l
```

Count by family:

```bash
find results -mindepth 3 -maxdepth 3 -name "*_adv_result.json" | sed 's#^results/##; s#/.*##' | sort | uniq -c
```

## 9. Troubleshooting

If you encounter `No .pt models found`, verify that checkpoints exist under:

```bash
find detector/MAGIC/maldefender/msacfg_models -name "*.pt"
```

If matplotlib logs a cache directory warning, prefix commands with `MPLCONFIGDIR=/tmp/matplotlib`.
