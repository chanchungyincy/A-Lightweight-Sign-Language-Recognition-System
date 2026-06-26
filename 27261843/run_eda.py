import os
import csv
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).parent
SPLITS_DIR = BASE_DIR / "splits"
LANDMARKS_DIR = BASE_DIR / "landmarks"

def generate_eda_report():
    print("=== NationalCSL-DP EDA 報告 ===")
    
    # 1. 讀取 splits
    records = []
    for split in ["train", "val", "test"]:
        csv_path = SPLITS_DIR / f"splits_{split}.csv"
        if not csv_path.exists():
            continue
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["split"] = split
                records.append(row)
                
    df = pd.DataFrame(records)
    print(f"\n總樣本數: {len(df)}")
    
    # 2. 檢查實際存在的 .npy 檔案長度
    lengths = []
    missing = 0
    valid_records = []
    
    for _, row in df.iterrows():
        npy_path = LANDMARKS_DIR / f"{row['sample_id']}.npy"
        if npy_path.exists():
            arr = np.load(npy_path)
            lengths.append(arr.shape[0])
            row['n_frames'] = str(arr.shape[0])  # 更新為實際特徵長度
            valid_records.append(row)
        else:
            missing += 1
            
    print(f"成功抽取特徵樣本數: {len(valid_records)}")
    print(f"失敗/丟棄樣本數: {missing} ({(missing/len(df)*100):.2f}%)")
    
    if not valid_records:
        print("沒有有效的 .npy 檔案，無法進行後續分析。")
        return
        
    valid_df = pd.DataFrame(valid_records)
    
    # 3. 序列長度統計
    print("\n--- 序列長度統計 (Frames) ---")
    print(f"最短: {np.min(lengths)}")
    print(f"最長: {np.max(lengths)}")
    print(f"平均: {np.mean(lengths):.1f}")
    print(f"中位數: {np.median(lengths)}")
    print(f"95% 分位數: {np.percentile(lengths, 95)}")
    
    # 4. Class Distribution
    class_counts = valid_df['gloss_id'].value_counts()
    print("\n--- 類別分佈 ---")
    print(f"總類別數: {len(class_counts)}")
    print(f"每個類別平均樣本數: {class_counts.mean():.1f}")
    print(f"最少樣本的類別數量: {class_counts.min()}")
    print("不平衡嚴重程度 (Max/Min ratio): {:.2f}".format(class_counts.max() / class_counts.min()))
    
    # 5. 生成視覺化圖表
    os.makedirs("eda_plots", exist_ok=True)
    
    # 圖1: 長度分佈直方圖
    plt.figure(figsize=(10, 6))
    plt.hist(lengths, bins=30, color='skyblue', edgecolor='black')
    plt.title('Sequence Length Distribution')
    plt.xlabel('Number of Frames')
    plt.ylabel('Count')
    plt.axvline(np.mean(lengths), color='red', linestyle='dashed', linewidth=1, label=f'Mean: {np.mean(lengths):.1f}')
    plt.axvline(np.percentile(lengths, 95), color='green', linestyle='dashed', linewidth=1, label=f'95th %: {np.percentile(lengths, 95):.1f}')
    plt.legend()
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('eda_plots/length_distribution.png')
    plt.close()
    
    # 圖2: 各 Split 數量圓餅圖
    plt.figure(figsize=(8, 8))
    split_counts = valid_df['split'].value_counts()
    plt.pie(split_counts, labels=split_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
    plt.title('Data Split Distribution')
    plt.savefig('eda_plots/split_distribution.png')
    plt.close()

    print("\nEDA 圖表已保存至 eda_plots/ 資料夾")

if __name__ == "__main__":
    generate_eda_report()
