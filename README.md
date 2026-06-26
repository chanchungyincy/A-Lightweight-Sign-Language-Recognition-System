# 4016project - README

This repository contains the source code, training pipelines, and evaluation scripts for the 4016project, which focuses on Chinese Sign Language (CSL) recognition and its integration with Large Language Models (LLMs).

## 📂 Project Structure & File Descriptions

### 1. Model Training Pipelines
These notebooks represent different stages of our model development:
* **🌟 CSL_Training_Pipeline(best).ipynb**
  * The final production model. This version contains the optimized training pipeline and the final model architecture used for our results.
* **CSL_Training_Pipeline(base).ipynb & CSL_Training_Pipeline(notbest).ipynb**
  * These are earlier versions and non-iterated baselines. They are preserved for historical reference and performance comparison.

### 2. LLM Integration & Evaluation
These files handle the connection between the sign language model outputs and the LLM for final sentence-level processing and assessment:
* **LLM_Pipeline.ipynb, posttest.ipynb, & posttest2.ipynb**
  * Main scripts used to connect the model to an LLM for final testing and evaluation.
* **sentence.txt**
  * An annotation file documenting how isolated sign language gestures were concatenated into full sentences for LLM testing.
  * *Note: All data used here are isolated sign language samples from the test set.*

### 3. Data & Checkpoints
* **📁 27261843/**
  * This folder contains the training checkpoints and the primary datasets.
  * *Important: There is a dedicated readme inside this directory that provides detailed information regarding the data specifications and structure.*

### 4. Other Files(No need to pay attention)
* **📁 output/**: Default directory for model outputs and generated logs.
* **Chinese_Sign_Language_baseFront_End_(1).ipynb**: A notebook containing the base front-end implementation for the project.
* **Untitled0.ipynb**: Temporary notebook used for testing.