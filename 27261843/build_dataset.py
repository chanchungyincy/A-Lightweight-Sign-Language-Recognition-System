import os
import csv
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

# ── 設定 ─────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
SPLITS_DIR    = BASE_DIR / "splits"
LANDMARKS_DIR = BASE_DIR / "landmarks"
# ─────────────────────────────────────────────────────────────

class SignLanguageDataset(Dataset):
    def __init__(self, split_name="train", max_len=None):
        """
        split_name: "train", "val", or "test"
        max_len: 如果設定，會把超過長度的序列截斷 (通常設為 100 左右，可選)
        """
        self.csv_path = SPLITS_DIR / f"splits_{split_name}.csv"
        self.max_len = max_len
        self.samples = []
        
        # 建立 Label 字典 (Gloss ID -> 0~199)
        self.label_map = self._build_label_map()
        
        # 讀取 CSV
        if not self.csv_path.exists():
            raise FileNotFoundError(f"找不到 {self.csv_path}")
            
        with open(self.csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sample_id = row["sample_id"]
                npy_path = LANDMARKS_DIR / f"{sample_id}.npy"
                
                # 確保 .npy 檔案存在
                if npy_path.exists():
                    self.samples.append({
                        "sample_id": sample_id,
                        "gloss_id": row["gloss_id"],
                        "npy_path": str(npy_path),
                        "label": self.label_map[row["gloss_id"]]
                    })
                else:
                    print(f"Warning: 找不到檔案 {npy_path.name}，已跳過。")
                    
        print(f"[{split_name.upper()}] 載入完成，共 {len(self.samples)} 筆資料。")

    def _build_label_map(self):
        """從 metadata.csv 建立所有出現過的 gloss_id 對應的整數標籤"""
        meta_path = SPLITS_DIR / "metadata.csv"
        unique_glosses = set()
        with open(meta_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                unique_glosses.add(row["gloss_id"])
        
        # 排序確保每次對應的 ID 都是一致的
        sorted_glosses = sorted(list(unique_glosses))
        return {gloss: i for i, gloss in enumerate(sorted_glosses)}

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        
        # 讀取 .npy 特徵 (Shape: T x 225)
        feature = np.load(item["npy_path"])
        
        # 轉為 PyTorch Tensor
        feature_tensor = torch.FloatTensor(feature)
        
        # 截斷 (可選)
        if self.max_len is not None and feature_tensor.shape[0] > self.max_len:
            feature_tensor = feature_tensor[:self.max_len]
            
        length = feature_tensor.shape[0]
        label = item["label"]
        
        return feature_tensor, label, length


def collate_fn(batch):
    """
    DataLoader 用的自訂合併函數，處理變長序列
    將一個 batch 的 [(T1, D), (T2, D), ...] 打包成 (B, T_max, D)
    """
    # 按照序列長度降序排列 (PyTorch pack_padded_sequence 的要求)
    batch.sort(key=lambda x: x[2], reverse=True)
    
    features = [item[0] for item in batch]
    labels = torch.LongTensor([item[1] for item in batch])
    lengths = torch.LongTensor([item[2] for item in batch])
    
    # Pad sequences: 自動補 0 到該 batch 的最大長度
    # 輸出形狀: (Batch_Size, T_max, 225)  (注意 batch_first=True)
    padded_features = pad_sequence(features, batch_first=True, padding_value=0.0)
    
    return padded_features, labels, lengths


# ── 測試代碼 ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("測試 DataLoader...")
    
    # 1. 建立 Dataset
    train_dataset = SignLanguageDataset(split_name="train")
    
    # 2. 建立 DataLoader
    train_loader = DataLoader(
        train_dataset, 
        batch_size=32, 
        shuffle=True, 
        collate_fn=collate_fn
    )
    
    # 3. 測試讀取一個 Batch
    for batch_idx, (features, labels, lengths) in enumerate(train_loader):
        print(f"\nBatch {batch_idx + 1}")
        print(f"Features shape: {features.shape}  (Batch_Size, T_max, 225)")
        print(f"Labels shape:   {labels.shape}    (Batch_Size)")
        print(f"Lengths:        {lengths.tolist()}")
        print(f"第一筆 Label:    {labels[0]}")
        break  # 只測試第一個 batch
