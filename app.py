"""
Score Spectrum Visualizer — Memory-Optimized Edition
=====================================================
Architecture guarantees:
  • Shared dataset stored once as raw numpy float32 arrays via @st.cache_resource
    → ~40 MB for the entire dataset, shared across ALL user sessions (zero copies)
  • Pre-sorted arrays stored alongside raw data for O(log n) binary search
  • Every user interaction operates only on lightweight numpy views (.values[slice])
    — no pandas DataFrame is ever created during a user-triggered rerun
  • Plotly figures are built from tiny aggregated arrays (one per score bin), not raw rows
  • Per-session RAM contribution: ~1–5 KB (widget state only)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# TRANSLATIONS
# ─────────────────────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "title": "📊 Score Spectrum (Phổ Điểm) Visualizer",
        "subtitle": "Interactive student performance analytics & comparison for college entrance exam blocks (2025 vs 2026)",
        "data_import": "📂 Data Import",
        "loaded_default": "Using Diem20252026.csv dataset.",
        "error_no_file": "Error: Diem20252026.csv not found in the workspace.",
        "viz_settings": "⚙️ Visualization Settings",
        "select_years": "**Select Years to Plot:**",
        "year_2026": "2026 (Current)",
        "year_2025": "2025 (Reference)",
        "select_blocks": "**Select Exam Blocks:**",
        "score_step": "Score Step Size (Binning)",
        "score_step_help": "Define the intervals at which student scores are grouped. Standard grading uses 0.25.",
        "cand_limiters": "🔢 Candidate Limiters (1 to N)",
        "only_mien_bac": "Only miền bắc (Northern region)",
        "only_mien_bac_help": "Limits the dataset to Northern region candidates: first 592,591 (2026) and 666,892 (2025).",
        "mien_bac_applied": "Miền Bắc limits applied:\n- 2026: {limit_2026:,} candidates\n- 2025: {limit_2025:,} candidates",
        "limit_2026_label": "2026 Candidate Limit (N):",
        "limit_2026_help": "Limit the 2026 data to the first N students (rows).",
        "limit_2025_label": "2025 Candidate Limit (M):",
        "limit_2025_help": "Limit the 2025 data to the first M students (rows).",
        "missing_handling": "⚠️ Missing Data Handling",
        "treat_blanks": "Treat blank/missing scores as 0",
        "treat_blanks_help": "If checked, absent/empty scores are counted as 0. Otherwise excluded.",
        "agg_mode_title": "🔗 Aggregation Mode",
        "plot_mode_label": "Plot Mode:",
        "plot_mode_help": "Separate: Plots each selected block as its own line.\nCombine: Pools all selected blocks together.",
        "plot_mode_opt_sep": "Separate Blocks",
        "plot_mode_opt_comb": "Combine Selected Blocks",
        "score_filter_title": "🎯 Score Value Filter",
        "score_filter_label": "Score Value Range Limit:",
        "score_filter_help": "Only include scores within this range.",
        "warning_select": "⚠️ Please select at least one year and one exam block from the sidebar.",
        "warning_no_data": "⚠️ No data matches the selected filters. Please check your sidebar selections.",
        "perf_summary": "📈 Performance Summary",
        "avg_score_label": "Average Score",
        "max_label": "Max",
        "total_label": "Total",
        "high_threshold_label": "pts",
        "dist_spectrum_tab": "📊 Score Distribution Spectrum",
        "cum_curve_tab": "📈 Cumulative Score Curve",
        "dist_title": "Student Frequency per Score",
        "dist_xaxis": "Score",
        "dist_yaxis": "Number of Candidates",
        "cum_title": "Cumulative: Candidates Scoring ≥ X",
        "cum_xaxis": "Score Threshold",
        "cum_yaxis": "Cumulative Number of Candidates",
        "rank_calc_title": "🔍 Custom Score Rank Calculator",
        "rank_calc_desc": "Find the relationship between student scores and top percentage ranks (following active candidate limiters).",
        "score_to_pct_tab": "🎯 Score → Rank %",
        "pct_to_score_tab": "📊 Rank % → Score",
        "score_to_pct_desc": "Type a score below to instantly see how many candidates scored ≥ it and their percentage rank.",
        "score_input_label": "Enter score to calculate rank:",
        "score_input_help": "Type any score to lookup rank instantly.",
        "top_rank_pct_label": "Top Rank Percentage",
        "candidates_ge_label": "Candidates ≥",
        "total_pool_label": "Total Pool",
        "pct_to_score_desc": "Type a target top percentage rank below to instantly see the score threshold required.",
        "pct_input_label": "Enter target top percentage rank (%):",
        "pct_input_help": "E.g. 5.0 for top 5%.",
        "min_score_required": "Minimum Required Score",
        "actual_rank_label": "Actual Rank",
        "cum_table_section": "📋 Cumulative Distribution Table",
        "cum_table_desc": "Exact cumulative count of students at specific score thresholds. Helps predict entry cutoffs.",
        "select_table_block": "Select block to view detailed table:",
        "tab_filtered_scope": "🎯 Filtered Pool (Current Scope)",
        "tab_whole_population": "🌐 Whole Population (All Candidates)",
        "filtered_table_desc": "Statistics for candidates within current candidate limits and score filter (% relative to filtered scope):",
        "whole_table_desc": "Same score scope, but % calculated relative to all candidates following active candidate limiters:",
        "col_threshold": "Score Threshold (≥)",
        "col_num_students": "Number of Students",
        "col_percentage": "Percentage",
        "data_preview_section": "🔍 Data Preview",
        "data_preview_desc": "Showing first 20 rows of the loaded dataset:",
        "no_candidates_scope": "No candidates fall within this dataset scope.",
        "hover_dist": "<b>%{customdata}</b><br>Score: %{x:.2f}<br>Count: %{y:,} candidates<br>Percentage: %{text:.2f}%<extra></extra>",
        "hover_cum": "<b>%{customdata}</b><br>Score ≥ %{x:.2f}<br>Candidates: %{y:,}<br>Top %{text:.2f}%<extra></extra>",
    },
    "Tiếng Việt": {
        "title": "📊 Bộ Trực Quan Hóa Phổ Điểm",
        "subtitle": "Phân tích và so sánh phổ điểm thi đại học, dự đoán điểm chuẩn (2025 vs 2026)",
        "data_import": "📂 Nhập Dữ Liệu",
        "loaded_default": "Đang sử dụng tập dữ liệu Diem20252026.csv.",
        "error_no_file": "Lỗi: Không tìm thấy file Diem20252026.csv trong thư mục làm việc.",
        "viz_settings": "⚙️ Cấu Hình Trực Quan Hóa",
        "select_years": "**Chọn Năm Hiển Thị:**",
        "year_2026": "2026 (Năm hiện tại)",
        "year_2025": "2025 (Năm so sánh)",
        "select_blocks": "**Chọn Khối Thi:**",
        "score_step": "Bước chia điểm (Binned Step)",
        "score_step_help": "Xác định khoảng gộp điểm. Thang điểm chuẩn thường dùng bước 0.25.",
        "cand_limiters": "🔢 Giới Hạn Thí Sinh (1 đến N)",
        "only_mien_bac": "Chỉ tính Miền Bắc",
        "only_mien_bac_help": "Giới hạn về đúng khu vực Miền Bắc: 592,591 thí sinh đầu (2026) và 666,892 thí sinh đầu (2025).",
        "mien_bac_applied": "Đã áp dụng giới hạn Miền Bắc:\n- 2026: {limit_2026:,} thí sinh\n- 2025: {limit_2025:,} thí sinh",
        "limit_2026_label": "Giới hạn thí sinh 2026 (N):",
        "limit_2026_help": "Giới hạn dữ liệu 2026 ở N học sinh đầu tiên.",
        "limit_2025_label": "Giới hạn thí sinh 2025 (M):",
        "limit_2025_help": "Giới hạn dữ liệu 2025 ở M học sinh đầu tiên.",
        "missing_handling": "⚠️ Xử Lý Dữ Liệu Trống",
        "treat_blanks": "Coi điểm trống/vắng thi là 0",
        "treat_blanks_help": "Nếu chọn, điểm vắng hoặc trống sẽ tính là 0.0. Nếu không, chúng sẽ bị loại bỏ.",
        "agg_mode_title": "🔗 Chế Độ Gộp Biểu Đồ",
        "plot_mode_label": "Chế độ hiển thị:",
        "plot_mode_help": "Tách riêng: Vẽ mỗi khối thành một đường riêng.\nGộp khối: Gộp tất cả các khối thành một phân phối chung.",
        "plot_mode_opt_sep": "Tách riêng các khối",
        "plot_mode_opt_comb": "Gộp chung khối đã chọn",
        "score_filter_title": "🎯 Bộ Lọc Khoảng Điểm",
        "score_filter_label": "Giới Hạn Khoảng Điểm Số:",
        "score_filter_help": "Chỉ tính các thí sinh có điểm trong khoảng này.",
        "warning_select": "⚠️ Vui lòng chọn ít nhất một năm và một khối thi từ thanh bên.",
        "warning_no_data": "⚠️ Không có dữ liệu nào khớp với bộ lọc. Vui lòng kiểm tra lại thiết lập ở thanh bên.",
        "perf_summary": "📈 Tóm Tắt Hiệu Năng",
        "avg_score_label": "Điểm Số Trung Bình",
        "max_label": "Cao Nhất",
        "total_label": "Tổng Số",
        "high_threshold_label": "điểm",
        "dist_spectrum_tab": "📊 Phổ Điểm Tần Suất",
        "cum_curve_tab": "📈 Đường Tích Lũy",
        "dist_title": "Số Lượng Học Sinh Theo Từng Mức Điểm",
        "dist_xaxis": "Điểm Số",
        "dist_yaxis": "Số Lượng Thí Sinh",
        "cum_title": "Số Thí Sinh Đạt Mức Điểm ≥ X",
        "cum_xaxis": "Ngưỡng Điểm Số",
        "cum_yaxis": "Số Lượng Thí Sinh Tích Lũy",
        "rank_calc_title": "🔍 Tra Cứu Điểm Số & Thứ Hạng",
        "rank_calc_desc": "Tra cứu mối tương quan giữa điểm số và thứ hạng phần trăm (theo giới hạn thí sinh hiện tại).",
        "score_to_pct_tab": "🎯 Tra Điểm → Thứ Hạng %",
        "pct_to_score_tab": "📊 Nhập % → Tìm Điểm Chuẩn",
        "score_to_pct_desc": "Nhập một điểm số để xem ngay số học sinh đạt ≥ mức đó và tỷ lệ phần trăm tương ứng.",
        "score_input_label": "Nhập điểm số cần tra cứu:",
        "score_input_help": "Nhập bất kỳ điểm số nào để tính thứ hạng ngay lập tức.",
        "top_rank_pct_label": "Tỷ Lệ Phần Trăm Thứ Hạng (Top %)",
        "candidates_ge_label": "Số thí sinh ≥",
        "total_pool_label": "Tổng Số Thí Sinh",
        "pct_to_score_desc": "Nhập phần trăm xếp hạng mong muốn (top %) để tính mức điểm tối thiểu cần đạt.",
        "pct_input_label": "Nhập tỷ lệ phần trăm thứ hạng mong muốn (%):",
        "pct_input_help": "Ví dụ: 5.0 tương ứng với top 5%.",
        "min_score_required": "Mức Điểm Tối Thiểu Cần Đạt",
        "actual_rank_label": "Thứ Hạng Thực Tế Đạt Được",
        "cum_table_section": "📋 Bảng Phân Phối Tích Lũy",
        "cum_table_desc": "Xem chi tiết số lượng thí sinh tích lũy ở các ngưỡng điểm. Hỗ trợ dự đoán điểm chuẩn.",
        "select_table_block": "Chọn khối thi cần hiển thị bảng chi tiết:",
        "tab_filtered_scope": "🎯 Khoảng Điểm Được Lọc (Filtered Pool)",
        "tab_whole_population": "🌐 Toàn Bộ Thí Sinh (Whole Population)",
        "filtered_table_desc": "Thống kê trong khoảng điểm được lọc (tỷ lệ % tính theo lượng điểm lọc):",
        "whole_table_desc": "Giữ nguyên khoảng điểm, nhưng tỷ lệ % tính trên toàn bộ thí sinh theo giới hạn vùng miền:",
        "col_threshold": "Ngưỡng Điểm (≥)",
        "col_num_students": "Số Lượng Học Sinh",
        "col_percentage": "Tỷ Lệ Phần Trăm",
        "data_preview_section": "🔍 Xem Trước Dữ Liệu",
        "data_preview_desc": "Xem trước 20 dòng đầu tiên của tập dữ liệu đã tải:",
        "no_candidates_scope": "Không có thí sinh nào nằm trong khoảng dữ liệu này.",
        "hover_dist": "<b>%{customdata}</b><br>Điểm số: %{x:.2f}<br>Số thí sinh: %{y:,}<br>Tỷ lệ: %{text:.2f}%<extra></extra>",
        "hover_cum": "<b>%{customdata}</b><br>Điểm số ≥ %{x:.2f}<br>Số thí sinh: %{y:,}<br>Top %{text:.2f}%<extra></extra>",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Score Spectrum Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .main-title {
        font-weight: 700; font-size: 2.5rem;
        background: linear-gradient(135deg, #FF4B4B, #FF8F8F, #4A90E2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle { color: #8892B0; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .metric-card {
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 1.5rem; text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.2);
        backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); border: 1px solid rgba(255,75,75,0.4); }
    .metric-val { font-size: 2.2rem; font-weight: 700; color: #FF4B4B; margin-bottom: 0.2rem; }
    .metric-label { font-size: 0.9rem; color: #8892B0; text-transform: uppercase; letter-spacing: 1px; }
    .section-header {
        font-weight: 600; font-size: 1.5rem; color: #E2E8F0;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        padding-bottom: 0.5rem; margin-top: 2rem; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING — cached as a RESOURCE (one shared copy for ALL sessions)
# Stores raw numpy arrays: column_name → (raw_array, sorted_array_of_valid_scores)
# raw_array : float32, length = n_rows, NaN where score < 15 (invalid)
# sorted_valid: float32 1-D sorted array of valid (non-NaN) scores for that column
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading dataset into memory…")
def load_dataset(source):
    """Parse CSV once, store per-column float32 numpy arrays + pre-sorted valid arrays.
    Total RAM: ~40 MB for Diem20252026.csv (10 cols × 1M rows × 4 bytes = 40 MB).
    Pre-sorted arrays only cover valid scores so they are much smaller (~8 MB).
    Grand total ≈ 48 MB shared across all concurrent users/sessions.
    """
    import pandas as pd
    raw = pd.read_csv(source)
    raw.columns = (
        raw.columns.str.strip()
        .str.replace('"', '', regex=False)
        .str.replace("'", '', regex=False)
        .str.replace('\r', '', regex=False)
        .str.replace('\n', '', regex=False)
    )
    if 'Student_ID' in raw.columns:
        raw = raw.drop(columns=['Student_ID'])

    columns = list(raw.columns)
    arrays = {}           # col → float32 numpy array (full length, NaN for invalid)
    sorted_valid = {}     # col → sorted float32 numpy array (valid scores only)
    col_max = {}          # col → global max
    col_min = {}          # col → global min of valid scores

    for col in columns:
        arr = pd.to_numeric(raw[col], errors='coerce').to_numpy(dtype=np.float32)
        arr[arr < 15.0] = np.nan  # mark invalid in-place (no copy)
        arrays[col] = arr
        valid = arr[~np.isnan(arr)]
        sv = np.sort(valid)
        sorted_valid[col] = sv
        col_max[col] = float(sv[-1]) if len(sv) > 0 else 30.0
        col_min[col] = float(sv[0]) if len(sv) > 0 else 15.0

    total_rows = len(raw)
    return {
        "columns": columns,
        "arrays": arrays,
        "sorted_valid": sorted_valid,
        "col_max": col_max,
        "col_min": col_min,
        "total_rows": total_rows,
    }


# ─────────────────────────────────────────────────────────────────────────────
# LIGHTWEIGHT PER-RERUN HELPERS
# All helpers work directly on numpy views — zero pandas overhead per rerun.
# ─────────────────────────────────────────────────────────────────────────────

def get_col_array(dataset, col, limit, fill_zero):
    """Return a float32 numpy array for `col`, sliced to `limit` rows.
    If fill_zero: NaN → 0.0, otherwise NaN rows are dropped.
    No copy of the underlying data — uses numpy indexing.
    """
    arr = dataset["arrays"][col][:limit]  # view, not copy
    if fill_zero:
        arr = np.where(np.isnan(arr), 0.0, arr)
    else:
        arr = arr[~np.isnan(arr)]
    return arr  # float32 array


def apply_score_filter(arr, lo, hi):
    """Return a view of arr filtered to [lo, hi]. Returns float32 array."""
    return arr[(arr >= lo) & (arr <= hi)]


def compute_binned_spectrum(arr, step):
    """Return (bin_centers, counts, percents) as three float32/int64 arrays.
    Only as many bins as distinct binned values — tiny output.
    """
    if len(arr) == 0:
        return np.array([], dtype=np.float32), np.array([], dtype=np.int64), np.array([], dtype=np.float32)
    binned = np.round(arr / step) * step
    unique_bins, counts = np.unique(binned, return_counts=True)
    total = len(arr)
    percents = (counts / total * 100).astype(np.float32)
    return unique_bins.astype(np.float32), counts, percents


def compute_cumulative(arr):
    """Return (sorted_unique_scores, cumulative_ge_counts, cumulative_ge_pct).
    Uses a pre-counted approach — output is one entry per unique score value.
    """
    if len(arr) == 0:
        return np.array([]), np.array([]), np.array([])
    total = len(arr)
    sorted_uniq, counts = np.unique(arr, return_counts=True)
    # Reverse-cumsum: count >= each unique score
    cum_ge = np.cumsum(counts[::-1])[::-1]
    cum_pct = (cum_ge / total * 100).astype(np.float32)
    return sorted_uniq.astype(np.float32), cum_ge, cum_pct


def count_ge(sorted_arr, score):
    """Binary search: count of elements >= score in a pre-sorted array."""
    idx = np.searchsorted(sorted_arr, score, side='left')
    return int(len(sorted_arr) - idx)


def score_at_top_pct(sorted_arr, pct):
    """Return (threshold_score, exact_count, exact_pct) for top pct%."""
    n = len(sorted_arr)
    if n == 0:
        return 0.0, 0, 0.0
    target_idx = int(n * (1.0 - pct / 100.0))
    target_idx = max(0, min(target_idx, n - 1))
    threshold = float(sorted_arr[target_idx])
    idx = np.searchsorted(sorted_arr, threshold, side='left')
    exact_count = int(n - idx)
    exact_pct = exact_count / n * 100.0
    return threshold, exact_count, exact_pct


def build_sorted_limited(arr, fill_zero):
    """Return pre-sorted float32 array for a limited, fill-applied column array."""
    if fill_zero:
        a = np.where(np.isnan(arr), 0.0, arr).astype(np.float32)
    else:
        a = arr[~np.isnan(arr)]
    return np.sort(a)


# ─────────────────────────────────────────────────────────────────────────────
# UI — HEADER + LANGUAGE
# ─────────────────────────────────────────────────────────────────────────────
col_title, col_lang = st.columns([8, 2])
with col_lang:
    selected_lang = st.selectbox(
        "Language Selection",
        options=["English", "Tiếng Việt"],
        index=0,
        label_visibility="collapsed",
    )
t = TRANSLATIONS[selected_lang]

with col_title:
    st.markdown(f'<div class="main-title">{t["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{t["subtitle"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOAD — always loads from bundled Diem20252026.csv (no user uploads)
# ─────────────────────────────────────────────────────────────────────────────
try:
    dataset = load_dataset("Diem20252026.csv")
except FileNotFoundError:
    st.error(t["error_no_file"])
    st.stop()

available_cols = dataset["columns"]
total_rows = dataset["total_rows"]

# ─────────────────────────────────────────────────────────────────────────────
# DYNAMIC BLOCK DETECTION
# ─────────────────────────────────────────────────────────────────────────────
detected_blocks = []
for col in available_cols:
    cleaned = col
    for suffix in [" 2025", " 2026", "2025", "2026"]:
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
    cleaned = cleaned.strip()
    if cleaned and cleaned != "Student_ID" and cleaned not in detected_blocks:
        detected_blocks.append(cleaned)

standard_order = ["A00", "A01", "D01", "A00 TOAN X2", "A01 TOAN X2"]
base_blocks = [b for b in standard_order if b in detected_blocks] + [
    b for b in detected_blocks if b not in standard_order
]
if not base_blocks:
    base_blocks = ["A00", "A01", "D01", "A00 TOAN X2", "A01 TOAN X2"]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"### {t['viz_settings']}")
st.sidebar.write(t["select_years"])
show_2026 = st.sidebar.checkbox(t["year_2026"], value=True)
show_2025 = st.sidebar.checkbox(t["year_2025"], value=True)

st.sidebar.write(t["select_blocks"])
selected_blocks = [b for b in base_blocks if st.sidebar.checkbox(b, value=(b == "A00"))]

score_step = st.sidebar.slider(
    t["score_step"], min_value=0.1, max_value=2.0, value=0.25, step=0.05,
    help=t["score_step_help"],
)

st.sidebar.markdown(f"### {t['cand_limiters']}")
only_mien_bac = st.sidebar.checkbox(t["only_mien_bac"], value=False, help=t["only_mien_bac_help"])
if only_mien_bac:
    limit_2026 = min(592591, total_rows)
    limit_2025 = min(666892, total_rows)
    st.sidebar.info(t["mien_bac_applied"].format(limit_2026=limit_2026, limit_2025=limit_2025))
else:
    limit_2026 = st.sidebar.number_input(
        t["limit_2026_label"], min_value=1, max_value=total_rows,
        value=total_rows, step=10, help=t["limit_2026_help"],
    )
    limit_2025 = st.sidebar.number_input(
        t["limit_2025_label"], min_value=1, max_value=total_rows,
        value=total_rows, step=10, help=t["limit_2025_help"],
    )

st.sidebar.markdown(f"### {t['missing_handling']}")
fill_blanks_with_zero = st.sidebar.checkbox(
    t["treat_blanks"], value=False, help=t["treat_blanks_help"],
)

st.sidebar.markdown(f"### {t['agg_mode_title']}")
agg_mode = st.sidebar.radio(
    t["plot_mode_label"],
    options=[t["plot_mode_opt_sep"], t["plot_mode_opt_comb"]],
    index=0,
    help=t["plot_mode_help"],
)
combine_mode = agg_mode == t["plot_mode_opt_comb"]

# Build selected column tuples: (block, year, col_key)
selected_cols = []
for b in selected_blocks:
    if show_2026 and b in available_cols:
        selected_cols.append((b, "2026", b))
    if show_2025:
        col_25 = f"{b} 2025"
        if col_25 in available_cols:
            selected_cols.append((b, "2025", col_25))

if not selected_cols:
    st.warning(t["warning_select"])
    st.stop()

# Score range slider — use global min/max from selected columns
all_maxes = [dataset["col_max"][c] for _, _, c in selected_cols]
all_mins = [dataset["col_min"][c] for _, _, c in selected_cols]
global_min = float(min(all_mins)) if all_mins else 15.0
global_max = float(max(all_maxes)) if all_maxes else 30.0
slider_max = float(np.ceil(global_max))

st.sidebar.markdown(f"### {t['score_filter_title']}")
score_range = st.sidebar.slider(
    t["score_filter_label"],
    min_value=0.0, max_value=slider_max,
    value=(min(15.0, slider_max), min(30.0, slider_max)),
    step=0.5, help=t["score_filter_help"],
)

# ─────────────────────────────────────────────────────────────────────────────
# PREPARE DATASETS — all numpy, no pandas DataFrames, no copies
# ─────────────────────────────────────────────────────────────────────────────
def build_datasets():
    """Build lightweight dataset descriptors for the current filter state.
    Each descriptor holds only small derived arrays (histogram bins, cum counts).
    The underlying float32 raw arrays are referenced but never duplicated.
    """
    result = []

    def make_entry(name, block, year, raw_arr_limited, filtered_arr):
        """raw_arr_limited: all valid (or zero-filled) scores within limit.
           filtered_arr: raw_arr_limited further filtered by score_range.
        """
        sorted_limited = np.sort(raw_arr_limited)  # for rank calculator
        return {
            "name": name,
            "block": block,
            "year": year,
            "filtered": filtered_arr,        # small: only in-range scores
            "sorted_limited": sorted_limited, # for binary search rank calcs
        }

    if not combine_mode:
        for b, y, col in selected_cols:
            limit = limit_2026 if y == "2026" else limit_2025
            raw_col = dataset["arrays"][col][:limit]
            raw_arr = get_col_array(dataset, col, limit, fill_blanks_with_zero)
            filtered = apply_score_filter(raw_arr, score_range[0], score_range[1])
            result.append(make_entry(f"{b} ({y})", b, y, raw_arr, filtered))
    else:
        for year in ["2026", "2025"]:
            year_entries = [(b, c) for b, y, c in selected_cols if y == year]
            if not year_entries:
                continue
            limit = limit_2026 if year == "2026" else limit_2025
            pooled_raw = np.concatenate([
                get_col_array(dataset, col, limit, fill_blanks_with_zero)
                for _, col in year_entries
            ])
            filtered = apply_score_filter(pooled_raw, score_range[0], score_range[1])
            blocks_label = " + ".join(dict.fromkeys(b for b, _ in year_entries))
            name = f"Combined [{blocks_label}] ({year})"
            result.append(make_entry(name, f"Combined [{blocks_label}]", year, pooled_raw, filtered))

    return result

datasets = build_datasets()

if not datasets or all(len(ds["filtered"]) == 0 for ds in datasets):
    st.warning(t["warning_no_data"])
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────────────────────────────────────
COLORS = ["#FF4B4B", "#4A90E2", "#50E3C2", "#F5A623", "#D0021B", "#B8E986", "#7ED321", "#9013FE"]

def hex_to_rgba(hex_color, alpha=0.15):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ─────────────────────────────────────────────────────────────────────────────
# PERFORMANCE SUMMARY CARDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header">{t["perf_summary"]}</div>', unsafe_allow_html=True)
valid_ds = [ds for ds in datasets if len(ds["filtered"]) > 0]
metrics_cols = st.columns(min(len(valid_ds), 4))

for idx, ds in enumerate(valid_ds[:4]):
    arr = ds["filtered"]
    block = ds["block"]
    year = ds["year"]
    avg_score = float(np.mean(arr))
    max_score = float(np.max(arr))
    total_students = len(arr)
    threshold = 32.0 if "TOAN X2" in block else 24.0
    pct_high = float(np.mean(arr >= threshold) * 100)

    with metrics_cols[idx]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{block} ({year})</div>
            <div class="metric-val">{avg_score:.2f}</div>
            <div style="color:#E2E8F0;font-weight:500;font-size:1.1rem;margin-bottom:0.5rem;">{t["avg_score_label"]}</div>
            <div style="color:#8892B0;font-size:0.85rem;">
                {t["max_label"]}: <b>{max_score:.2f}</b> | {t["total_label"]}: <b>{total_students:,}</b><br>
                ≥{threshold:.0f} {t["high_threshold_label"]}: <b>{pct_high:.1f}%</b>
            </div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHARTS — pre-aggregate to small arrays, then build Plotly figure
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="section-header">📊 {t["dist_spectrum_tab"].replace("📊 ", "")} & {t["cum_curve_tab"].replace("📈 ", "")}</div>',
    unsafe_allow_html=True,
)
tab_dist, tab_cum = st.tabs([t["dist_spectrum_tab"], t["cum_curve_tab"]])

with tab_dist:
    fig_dist = go.Figure()
    for idx, ds in enumerate(datasets):
        arr = ds["filtered"]
        if len(arr) == 0:
            continue
        color = COLORS[idx % len(COLORS)]
        bins, counts, percents = compute_binned_spectrum(arr, score_step)
        fig_dist.add_trace(go.Scatter(
            x=bins, y=counts,
            mode="lines+markers",
            name=ds["name"],
            line=dict(color=color, width=3),
            marker=dict(size=6, symbol="circle"),
            fill="tozeroy",
            fillcolor=hex_to_rgba(color, 0.15),
            hovertemplate=t["hover_dist"],
            text=percents,
            customdata=[ds["name"]] * len(bins),
        ))
    fig_dist.update_layout(
        title=t["dist_title"], xaxis_title=t["dist_xaxis"], yaxis_title=t["dist_yaxis"],
        hovermode="x unified", template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with tab_cum:
    fig_cum = go.Figure()
    for idx, ds in enumerate(datasets):
        arr = ds["filtered"]
        if len(arr) == 0:
            continue
        color = COLORS[idx % len(COLORS)]
        scores_uniq, cum_ge, cum_pct = compute_cumulative(arr)
        fig_cum.add_trace(go.Scatter(
            x=scores_uniq, y=cum_ge,
            mode="lines",
            name=ds["name"],
            line=dict(color=color, width=3, shape="hv"),
            hovertemplate=t["hover_cum"],
            text=cum_pct,
            customdata=[ds["name"]] * len(scores_uniq),
        ))
    fig_cum.update_layout(
        title=t["cum_title"], xaxis_title=t["cum_xaxis"], yaxis_title=t["cum_yaxis"],
        hovermode="x unified", template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
    )
    st.plotly_chart(fig_cum, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# RANK CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header">{t["rank_calc_title"]}</div>', unsafe_allow_html=True)
st.write(t["rank_calc_desc"])

calc_tab1, calc_tab2 = st.tabs([t["score_to_pct_tab"], t["pct_to_score_tab"]])

with calc_tab1:
    st.write(t["score_to_pct_desc"])
    lookup_score = st.number_input(
        t["score_input_label"], min_value=0.0, max_value=40.0, value=25.0,
        step=0.25, key="calc_lookup_score", help=t["score_input_help"],
    )
    calc_cols = st.columns(min(len(datasets), 4))
    for idx, ds in enumerate(datasets):
        sl = ds["sorted_limited"]
        total_len = len(sl)
        if total_len > 0:
            cge = count_ge(sl, lookup_score)
            pct_ge = cge / total_len * 100.0
        else:
            cge, pct_ge = 0, 0.0

        is_26 = ds["year"] == "2026"
        cc = "#10B981" if is_26 else "#EF4444"
        cbg = "rgba(16,185,129,0.05)" if is_26 else "rgba(239,68,68,0.05)"
        with calc_cols[idx % 4]:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid {cc};background:{cbg};">
                <div class="metric-label">{ds["name"]}</div>
                <div class="metric-val" style="color:{cc};font-size:1.8rem;line-height:2.2rem;">{pct_ge:.4f}%</div>
                <div style="color:#E2E8F0;font-weight:500;font-size:0.95rem;margin-top:0.2rem;margin-bottom:0.4rem;">
                    {t["top_rank_pct_label"]}
                </div>
                <div style="color:#8892B0;font-size:0.85rem;">
                    {t["candidates_ge_label"]} <b>{lookup_score:.2f}</b>:
                    <span style="color:#E2E8F0;font-weight:bold;">{cge:,}</span><br>
                    {t["total_pool_label"]}: <b>{total_len:,}</b>
                </div>
            </div>""", unsafe_allow_html=True)

with calc_tab2:
    st.write(t["pct_to_score_desc"])
    lookup_pct = st.number_input(
        t["pct_input_label"], min_value=0.0, max_value=100.0, value=5.0,
        step=0.1, key="calc_lookup_pct", help=t["pct_input_help"],
    )
    calc_cols2 = st.columns(min(len(datasets), 4))
    for idx, ds in enumerate(datasets):
        sl = ds["sorted_limited"]
        threshold_score, exact_count, exact_pct = score_at_top_pct(sl, lookup_pct)
        total_len = len(sl)

        is_26 = ds["year"] == "2026"
        cc = "#10B981" if is_26 else "#EF4444"
        cbg = "rgba(16,185,129,0.05)" if is_26 else "rgba(239,68,68,0.05)"
        with calc_cols2[idx % 4]:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid {cc};background:{cbg};">
                <div class="metric-label">{ds["name"]}</div>
                <div class="metric-val" style="color:{cc};font-size:1.8rem;line-height:2.2rem;">{threshold_score:.2f} pts</div>
                <div style="color:#E2E8F0;font-weight:500;font-size:0.95rem;margin-top:0.2rem;margin-bottom:0.4rem;">
                    {t["min_score_required"]}
                </div>
                <div style="color:#8892B0;font-size:0.85rem;">
                    {t["actual_rank_label"]}:
                    <span style="color:#E2E8F0;font-weight:bold;">{exact_pct:.4f}%</span><br>
                    {t["candidates_ge_label"]} <b>{threshold_score:.2f}</b>: <b>{exact_count:,}</b>
                </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CUMULATIVE TABLE — binary search only, output is a tiny list of strings
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header">{t["cum_table_section"]}</div>', unsafe_allow_html=True)
st.write(t["cum_table_desc"])

selected_ds_name = st.selectbox(
    t["select_table_block"],
    options=[ds["name"] for ds in datasets if len(ds["filtered"]) > 0],
)

if selected_ds_name:
    ds = next(d for d in datasets if d["name"] == selected_ds_name)

    def render_cum_table(data_arr, denominator):
        if len(data_arr) == 0 or denominator == 0:
            st.info(t["no_candidates_scope"])
            return
        sorted_arr = np.sort(data_arr)
        lo, hi = float(data_arr.min()), float(data_arr.max())
        step_scores = np.arange(np.floor(hi), np.floor(lo) - 0.5, -0.5)
        rows = []
        for s in step_scores:
            idx = np.searchsorted(sorted_arr, s, side="left")
            cge = int(len(sorted_arr) - idx)
            pct = cge / denominator * 100.0
            rows.append({
                t["col_threshold"]: f"{s:.2f}",
                t["col_num_students"]: f"{cge:,}",
                t["col_percentage"]: f"{pct:.2f}%",
            })
        # Display as plain markdown table to avoid pyarrow serialization (zero copies)
        header = f"| {t['col_threshold']} | {t['col_num_students']} | {t['col_percentage']} |"
        sep = "| --- | --- | --- |"
        table_rows = [f"| {r[t['col_threshold']]} | {r[t['col_num_students']]} | {r[t['col_percentage']]} |" for r in rows]
        st.markdown("\n".join([header, sep] + table_rows))

    tab_filt, tab_whole = st.tabs([t["tab_filtered_scope"], t["tab_whole_population"]])
    with tab_filt:
        st.write(t["filtered_table_desc"])
        render_cum_table(ds["filtered"], len(ds["filtered"]))
    with tab_whole:
        st.write(t["whole_table_desc"])
        render_cum_table(ds["filtered"], len(ds["sorted_limited"]))

# ─────────────────────────────────────────────────────────────────────────────
# DATA PREVIEW — only 20 rows, rendered as markdown table (no pyarrow)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header">{t["data_preview_section"]}</div>', unsafe_allow_html=True)
st.write(t["data_preview_desc"])

preview_n = 20
cols = dataset["columns"]
header_row = "| # | " + " | ".join(cols) + " |"
sep_row = "| --- | " + " | ".join(["---"] * len(cols)) + " |"
data_rows = []
for i in range(min(preview_n, total_rows)):
    vals = []
    for col in cols:
        v = dataset["arrays"][col][i]
        vals.append("—" if np.isnan(v) else f"{v:.2f}")
    data_rows.append(f"| {i+1} | " + " | ".join(vals) + " |")
st.markdown("\n".join([header_row, sep_row] + data_rows))
