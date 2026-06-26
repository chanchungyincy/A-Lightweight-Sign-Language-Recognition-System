#!/usr/bin/env python3
"""
extract_200_glosses.py
根據 gloss ID 選擇性解壓 Participant_XX.zip 中的 200 個詞
ZIP 內部結構: Participant_XX/Participant_XX/front/NNNN/00001.jpg
                                             left/NNNN/00001.jpg
"""

import zipfile
import os
from pathlib import Path

# ── 改成你自己的路徑 ──────────────────────────────────────────
ZIP_DIR = r".\Pics"       # 放 Participant_01.zip 的資料夾
OUT_DIR = r".\extracted"  # 解壓目的地
# ─────────────────────────────────────────────────────────────

# 200 個選定的 gloss ID（4位數字字串，對應資料夾名）
SELECTED_IDS = {
    # 代詞
    "1928","1925","6450","0488","6571","2441","5599",
    # 基本動詞
    "0603","3703","1887","0071","2732","2400","2415","4691","2535",
    "3504","3185","4870","3993","6254","2961","5094","2130","5316","1752","1270","1614",
    "1256","5022","5800","3735","1328","0246","1653","6526","2180","3031",
    # 情感動詞
    "2462","3672","6654","4910","2039","5610","6105",
    # 形容詞
    "2092","1688","3609","5471","4102","1670","5781","2407","0477","0369",
    "5716","2455","4249","5807","0963","2217","2206",
    "4878","5340","0289","1817","2229","4871","0534","2922",
    # 疑問詞
    "0109","5637","4525","3492",
    # 連接詞
    "5478","5086","0930","5780","4967","5311","2244","6056",
    # 肯定否定
    "0198","0927","1325",
    # 時間
    "1770","4466","4542","1224","1406","6618","4113","2230",
    # 人物
    "1597","0526","2102","5008","0396","2832","4002","3149","4979","2598","1104","4486",
    "6264","3113","1359",
    # 地點
    "1251","1284","5726","2838","1823","3789","4904","5466","6488","6149","5894","2558","2559",
    # 食物
    "0514","6195","0300","0021","1747","2985","3388","0968","0165","4270",
    "2533","5353","0557","0356","1636","1879",
    # 數字
    "5504","2694","2659","2853","5513","1230","2676","5575","0145","1658",
    # 顏色
    "5855","4027","4485","6645","6343","5736",
    # 補充常用
    "2498","2505","4349","4462","0869","3386","6307","1962","5651","2257",
    "2492","6363","2648","3422","6532","2908",
    "2416","5698","2899","4944","5753","2346","1836",
    "4073","3257","2488","5858",
    "3308","0805","2069",
    "2680","6230","2913","5253","0639","2026","0457",
    "1955","3716","0090","2386","2201","2902","2678","2835","2701","1818",
}

MISSING_IDS = {"3031", "2462", "2206", "4878"}  # 實際漏掉的 4 個

ONLY_MISSING = False   # 補完之後改回 False

if ONLY_MISSING:
    SELECTED_IDS = MISSING_IDS

os.makedirs(OUT_DIR, exist_ok=True)

for i in range(1, 11):
    zip_name = f"Participant_{i:02d}.zip"
    zip_path = os.path.join(ZIP_DIR, zip_name)

    if not os.path.exists(zip_path):
        print(f"[SKIP] {zip_name} 不存在，跳過")
        continue

    print(f"\n處理 {zip_name} ...")
    extracted = 0
    skipped   = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        for entry in zf.namelist():
            # structure: Participant_10/Participant_10/front/0001/00001.jpg
            parts = Path(entry).parts
            if len(parts) < 4:
                skipped += 1
                continue

            view     = parts[1]   # 'front' or 'left'
            gloss_id = parts[2]   # '0001', '1928', etc.

            if view not in ("front", "left"):
                skipped += 1
                continue

            if gloss_id not in SELECTED_IDS:
                skipped += 1
                continue

            # 解壓，目標路徑: OUT_DIR/Participant_01/front/1928/00001.jpg
            target = os.path.join(OUT_DIR, f"Participant_{i:02d}", view, gloss_id, parts[3])
            os.makedirs(os.path.dirname(target), exist_ok=True)

            with zf.open(entry) as src, open(target, "wb") as dst:
                dst.write(src.read())
            extracted += 1

    print(f"  ✅ 解壓: {extracted} 檔  |  跳過: {skipped} 檔")

print("\n=== 全部完成 ===")
print(f"輸出目錄: {OUT_DIR}")
