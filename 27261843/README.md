# NationalCSL-DP Sign Language Recognition Data Pipeline

This repository contains the complete data processing pipeline for the Chinese Sign Language recognition project (focusing on a 200-word daily vocabulary subset). The pipeline covers everything from raw frame extraction to a ready-to-use PyTorch DataLoader.

## 📊 Dataset Statistics (EDA)
- **Total Samples**: 4,000
- **Class Balance**: Perfectly balanced (exactly 20 samples per class, no class weights needed)
- **Feature Shape**: `(T, 225)` 
  - `T` = Number of temporal frames  (Min: 5, Max: 44, Mean: 15.1, Median: 15.0, 95th percentile: 22.0).
  - `225` Dimensions = 33 Pose + 21 Left Hand + 21 Right Hand (x, y, z coordinates for each landmark).
- **Train/Val/Test Split**:
  - **Train**: Participants 01 to 08 (80%)
  - **Val**: Participant 09 (10%)
  - **Test**: Participant 10 (10%)
  - *Note: A strict Signer-Independent Split is applied to prevent data leakage.*

## 📁 Directory Structure
- `extracted/`: Contains raw image frames for the selected 200 glosses.
- `landmarks/`: Contains `.npy` files with MediaPipe landmarks (normalized and interpolated).
- `splits/`: CSV files defining the Train/Val/Test splits and mapping metadata.
- `eda_plots/`: Visualizations of sequence length distribution and split ratios.
- `build_dataset.py`: **Main entry point for model training**. Contains the PyTorch `Dataset` and `DataLoader` implementation.

## 🚀 Guide for the Model Training Team

### 1. How to load the data
You don't need to worry about feature extraction or normalization. Simply import `SignLanguageDataset` and `collate_fn` from `build_dataset.py`:

```python
from build_dataset import SignLanguageDataset, collate_fn
from torch.utils.data import DataLoader

# Initialize Dataset (split_name can be "train", "val", or "test")
train_dataset = SignLanguageDataset(split_name="train") 
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)

# Training loop example
for batch_idx, (features, labels, lengths) in enumerate(train_loader):
    # features: Shape (Batch_Size, T_max, 225)
    # labels: Shape (Batch_Size) -> Integer ID from 0 to 195
    # lengths: Shape (Batch_Size) -> Original sequence lengths (sorted in descending order)
    
    # Pass to your model here...
    pass

2. Model Design Recommendations
Input Size: 225

Output Classes (Num Classes): 200 (The dataset contains 200 unique glosses after validation).

Handling Variable Lengths: The lengths tensor outputted by the DataLoader is already sorted in descending order. You can directly pass features and lengths into torch.nn.utils.rnn.pack_padded_sequence before feeding them into your Bi-LSTM.

Max Sequence Length: Since 95% of sequences are under 22 frames and the absolute maximum is 44, setting your LSTM max_length parameter to around 45 will easily cover all samples without excessive padding.