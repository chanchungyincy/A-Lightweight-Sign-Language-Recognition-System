#!/usr/bin/env python3
"""
prepare_splits.py
掃描 extracted/ 資料夾，生成 metadata.csv + splits_train/val/test.csv
Split: Participant 01-08 = train, 09 = val, 10 = test
"""

import os
import csv
from pathlib import Path

# ── 改成你的路徑 ──────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent        # script 所在的 27261843/ 資料夾
EXTRACTED_DIR = BASE_DIR / "extracted"      # 你的解壓目的地
OUTPUT_DIR    = BASE_DIR / "splits"         # CSV 輸出位置
GLOSS_CSV     = BASE_DIR / "Pics" / "gloss.csv"       # gloss.csv 路徑
# ─────────────────────────────────────────────────────────────

SPLIT_MAP = {
    "01": "train", "02": "train", "03": "train", "04": "train",
    "05": "train", "06": "train", "07": "train", "08": "train",
    "09": "val",
    "10": "test",
}

# ── Step 1: 讀 gloss.csv 建立 ID → 中文字對照 ─────────────────
id_to_chinese = {}
id_to_english = {}
with open(GLOSS_CSV, encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # 跳過 header
    for row in reader:
        if len(row) >= 3:
            gid     = row[0].strip()
            chinese = row[1].strip()
            english = row[2].strip()
            id_to_chinese[gid] = chinese
            id_to_english[gid] = english

# ── Step 2: 掃描 extracted/ 目錄，收集所有樣本 ────────────────
# 結構: extracted/Participant_01/front/1928/00001.jpg ...
records = []
extracted_path = Path(EXTRACTED_DIR)

for participant_dir in sorted(extracted_path.iterdir()):
    if not participant_dir.is_dir():
        continue
    
    # 從資料夾名取 signer ID，例如 "Participant_01" → "01"
    name = participant_dir.name
    if not name.startswith("Participant_"):
        continue
    signer_id = name.replace("Participant_", "")   # "01" ~ "10"
    split     = SPLIT_MAP.get(signer_id, "unknown")

    for view in ("front", "left"):
        view_dir = participant_dir / view
        if not view_dir.exists():
            continue

        for gloss_dir in sorted(view_dir.iterdir()):
            if not gloss_dir.is_dir():
                continue

            gloss_id = gloss_dir.name   # "1928", "0514", etc.

            # 數一下這個 clip 有多少幀
            frames = sorted(gloss_dir.glob("*.jpg")) + sorted(gloss_dir.glob("*.jpeg"))
            n_frames = len(frames)

            if n_frames == 0:
                continue

            records.append({
                "sample_id": f"P{signer_id}_{gloss_id}_{view}",
                "gloss_id":  gloss_id,
                "gloss_zh":  id_to_chinese.get(gloss_id, "?"),
                "gloss_en":  id_to_english.get(gloss_id, "?"),
                "signer_id": signer_id,
                "view":      view,
                "n_frames":  n_frames,
                "path": gloss_dir.resolve().relative_to(BASE_DIR.resolve()).as_posix(),
                "split":     split,
            })

print(f"總共找到 {len(records)} 個樣本")

# ── Step 3: 輸出 CSV ───────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

FIELDNAMES = ["sample_id","gloss_id","gloss_zh","gloss_en",
              "signer_id","view","n_frames","path","split"]

# metadata.csv（全部）
meta_path = os.path.join(OUTPUT_DIR, "metadata.csv")
with open(meta_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(records)
print(f"✅ metadata.csv → {meta_path}  ({len(records)} rows)")

# splits_train / val / test
for split_name in ("train", "val", "test"):
    subset = [r for r in records if r["split"] == split_name]
    out_path = os.path.join(OUTPUT_DIR, f"splits_{split_name}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(subset)
    
    n_glosses  = len(set(r["gloss_id"] for r in subset))
    n_signers  = len(set(r["signer_id"] for r in subset))
    print(f"✅ splits_{split_name}.csv → {out_path}")
    print(f"   {len(subset)} samples | {n_glosses} glosses | {n_signers} signers")

print("\n=== 完成 ===")
