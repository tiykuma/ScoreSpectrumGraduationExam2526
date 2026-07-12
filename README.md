# 📊 Score Spectrum — Phổ Điểm Tốt Nghiệp THPT 2025 & 2026

> **Interactive analytics dashboard for Vietnam's national high school graduation exam (THPT) score distributions — comparing 2025 and 2026 cohorts.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://scorespectrumgraduationexam2526-vnfxvxzvrkbztuygmsjoxd.streamlit.app/)

---

## 🌐 Live Demo

**[→ Open the live app](https://scorespectrumgraduationexam2526-vnfxvxzvrkbztuygmsjoxd.streamlit.app/)**

---

## 📸 Features

### 📊 Score Distribution Spectrum
Visualize the frequency distribution of student scores across all major exam blocks. See exactly how many students fell at each score point, with smooth area charts for instant pattern recognition.

### 📈 Cumulative Score Curve
View the cumulative count of students scoring **≥ X** at every score threshold — the definitive tool for estimating university admission cutoffs.

### 🔍 Custom Score Rank Calculator
Two-way lookup tool:
- **Score → Rank %** — Enter any score and instantly see what percentage of candidates you beat.
- **Rank % → Score** — Enter a target top percentile (e.g. top 1%) and find the exact minimum score required to achieve it.

### 📋 Cumulative Distribution Table
Detailed score-by-score breakdown table, viewable in two modes:
- **Filtered Pool** — Statistics relative to your selected score range.
- **Whole Population** — Statistics relative to all candidates under active limits.

### 🌏 Bilingual Interface
Full English and Vietnamese (Tiếng Việt) support, switchable from the top-right corner.

---

## 🧮 Supported Exam Blocks

| Block | Subjects |
|---|---|
| **A00** | Toán — Vật Lý — Hóa Học |
| **A01** | Toán — Vật Lý — Tiếng Anh |
| **D01** | Toán — Ngữ Văn — Tiếng Anh |
| **A00 TOÁN X2** | A00 với Toán nhân hệ số 2 |
| **A01 TOÁN X2** | A01 với Toán nhân hệ số 2 |

All blocks are available for both **2026** (current year) and **2025** (reference year), enabling direct year-over-year comparison.

---

## ⚙️ Sidebar Controls

| Control | Description |
|---|---|
| **Select Years** | Toggle 2026 and/or 2025 data on/off |
| **Select Exam Blocks** | Choose which blocks to display |
| **Score Step Size** | Binning interval for the histogram (default: 0.25) |
| **Candidate Limiters** | Restrict to the first N candidates (supports Miền Bắc filter: 592,591 for 2026 / 666,892 for 2025) |
| **Missing Data Handling** | Treat absent/blank scores as 0 or exclude them |
| **Aggregation Mode** | Plot blocks separately or pool them into a single combined distribution |
| **Score Value Range** | Filter the visible score range on the charts |

---

## 🏗️ Architecture & Performance

This app is engineered to run comfortably on [Streamlit Community Cloud](https://streamlit.io/cloud)'s free tier with **20+ concurrent users at under 200 MB total RAM**.

### Memory Model

```
┌──────────────────────────────────────────────────┐
│  @st.cache_resource  (shared across ALL sessions) │
│                                                   │
│  Raw dataset: 10 columns × 1.04M rows             │
│  Stored as float32 numpy arrays                   │
│  Total: ~49 MB  ──  loaded ONCE at startup        │
└──────────────────────────────────────────────────┘
         │  pointer reference (zero copy)
         ▼
┌─────────────────────────────┐
│  Per-user rerun (per event) │
│  ~0.1–0.5 MB numpy ops only │
│  No pandas DataFrames       │
│  No pyarrow serialization   │
└─────────────────────────────┘
```

### Key Design Decisions

- **Pure numpy for all computations** — No pandas DataFrames are created during user interactions. All filtering, binning, and cumulative calculations use `np.unique`, `np.searchsorted`, and array slicing.
- **Pre-sorted arrays** — Each column's valid scores are pre-sorted at load time, enabling O(log n) binary search for all rank calculations.
- **No file uploader** — The dataset is bundled with the app. Removing the uploader eliminates per-user file buffering overhead.
- **Markdown tables instead of `st.dataframe`** — The cumulative distribution table and data preview render as markdown to avoid PyArrow C-extension serialization.
- **`@st.cache_resource` not `@st.cache_data`** — `cache_resource` stores a single shared reference; `cache_data` would copy the DataFrame on every user rerun.

### RAM Budget (20 concurrent users)

| Component | RAM |
|---|---|
| Shared dataset (all sessions) | ~49 MB |
| Per-session widget state | ~1–5 KB |
| Per-rerun numpy intermediates | ~0.1–0.5 MB |
| **20 sessions total** | **≈ 59 MB** ✅ |

---

## 📁 Project Structure

```
ScoreSpectrumGraduationExam2526/
├── app.py                  # Main Streamlit application
├── Diem20252026.csv        # Dataset: 1.04M rows × 10 exam block columns
├── requirements.txt        # Pinned Python dependencies
├── .gitignore              # macOS + Python ignores
└── README.md               # This file
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11 or 3.12 (recommended)
- `pip` or `uv`

### Setup

```bash
# Clone the repository
git clone https://github.com/tiykuma/ScoreSpectrumGraduationExam2526.git
cd ScoreSpectrumGraduationExam2526

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will be available at **http://localhost:8501**.

---

## 📦 Dependencies

```
streamlit
pandas<3.0.0
numpy<2.0.0
plotly
```

> **Note:** `numpy` and `pandas` versions are pinned to their stable 1.x/2.x series to prevent binary incompatibilities with PyArrow on the Streamlit Cloud Linux environment.

---

## 📊 Dataset

**File:** `Diem20252026.csv`  
**Rows:** 1,048,575 (one per candidate)  
**Columns:** 10 exam block scores

| Column | Year | Description |
|---|---|---|
| `A00` | 2026 | Toán + Vật Lý + Hóa Học |
| `A01` | 2026 | Toán + Vật Lý + Tiếng Anh |
| `D01` | 2026 | Toán + Ngữ Văn + Tiếng Anh |
| `A00 TOAN X2` | 2026 | A00 với Toán × 2, thang 30 |
| `A01 TOAN X2` | 2026 | A01 với Toán × 2, thang 30 |
| `A00 2025` | 2025 | Toán + Vật Lý + Hóa Học |
| `A01 2025` | 2025 | Toán + Vật Lý + Tiếng Anh |
| `D01 2025` | 2025 | Toán + Ngữ Văn + Tiếng Anh |
| `A00 TOAN X2 2025` | 2025 | A00 với Toán × 2, thang 30 |
| `A01 TOAN X2 2025` | 2025 | A01 với Toán × 2, thang 30 |

Scores below **15.0** are treated as invalid/absent and excluded from all calculations.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Push the repo to GitHub.
2. Log in to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select this repository, branch `main`, and main file `app.py`.
4. Under **Advanced settings**, set **Python version** to `3.11` or `3.12`.
5. Click **Deploy**.

> ⚠️ **Important:** Always set Python to **3.11** or **3.12** in Advanced Settings. The default experimental Python 3.14 environment causes C-extension segmentation faults with numpy and pyarrow.

---

## 📄 License

This project is open source. Data sourced from publicly available Vietnam national exam score releases - huge thanks to **ngocminhta** for the [data](https://github.com/ngocminhta/GraduationExamScoreProcessing).
