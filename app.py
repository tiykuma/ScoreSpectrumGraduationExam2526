import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

TRANSLATIONS = {
    "English": {
        "title": "📊 Score Spectrum (Phổ Điểm) Visualizer",
        "subtitle": "Interactive student performance analytics & comparison for college entrance exam blocks (2025 vs 2026)",
        "data_import": "📂 Data Import",
        "upload_csv": "Upload Student Scores (CSV)",
        "success_loaded": "Successfully loaded uploaded CSV file!",
        "loaded_default": "Using default Diem20252026.csv from workspace.",
        "error_no_file": "Error: Diem20252026.csv not found. Please upload a CSV file via the sidebar.",
        "viz_settings": "⚙️ Visualization Settings",
        "select_years": "**Select Years to Plot:**",
        "year_2026": "2026 (Current)",
        "year_2025": "2025 (Reference)",
        "select_blocks": "**Select Exam Blocks:**",
        "score_step": "Score Step Size (Binning)",
        "score_step_help": "Define the intervals at which student scores are grouped. Standard grading uses 0.25.",
        "cand_limiters": "🔢 Candidate Limiters (1 to N)",
        "only_mien_bac": "Only miền bắc (Northern region)",
        "only_mien_bac_help": "If checked, limits the dataset to candidates from the Northern region: first 592,591 candidates for 2026 and 666,892 candidates for 2025.",
        "mien_bac_applied": "Miền Bắc limits applied:\n- 2026: {limit_2026:,} candidates\n- 2025: {limit_2025:,} candidates",
        "limit_2026_label": "2026 Candidate Limit (N):",
        "limit_2026_help": "Limit the 2026 data to the first N students (rows).",
        "limit_2025_label": "2025 Candidate Limit (M):",
        "limit_2025_help": "Limit the 2025 data to the first M students (rows).",
        "missing_handling": "⚠️ Missing Data Handling",
        "treat_blanks": "Treat blank/missing scores as 0",
        "treat_blanks_help": "If checked, absent or empty scores are counted as 0. If unchecked, they are excluded from calculations.",
        "agg_mode_title": "🔗 Aggregation Mode",
        "plot_mode_label": "Plot Mode:",
        "plot_mode_help": "Separate: Plots each selected block as its own line.\nCombine: Pools all selected blocks together into a single distribution per year.",
        "plot_mode_opt_sep": "Separate Blocks",
        "plot_mode_opt_comb": "Combine Selected Blocks",
        "score_filter_title": "🎯 Score Value Filter",
        "score_filter_label": "Score Value Range Limit:",
        "score_filter_help": "Only include scores within this range.",
        "warning_select": "⚠️ Please select at least one year and one exam block from the sidebar to view data.",
        "warning_no_data": "⚠️ No data matches the selected filters and score ranges. Please check your sidebar selections.",
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
        "cum_title": "Cumulative Number of Students Scoring Greater Than or Equal (Score ≥ X)",
        "cum_xaxis": "Score Threshold",
        "cum_yaxis": "Cumulative Number of Candidates",
        "rank_calc_title": "🔍 Custom Score Rank Calculator",
        "rank_calc_desc": "Find the relationship between student scores and top percentage ranks (following active candidate limiters).",
        "score_to_pct_tab": "🎯 Score → Rank %",
        "pct_to_score_tab": "📊 Rank % → Score",
        "score_to_pct_desc": "Type a score below to instantly see how many candidates scored greater than or equal (≥) to it, along with their percentage rank.",
        "score_input_label": "Enter score to calculate rank:",
        "score_input_help": "Type any score to lookup rank instantly.",
        "top_rank_pct_label": "Top Rank Percentage",
        "candidates_ge_label": "Candidates &ge;",
        "total_pool_label": "Total Pool",
        "pct_to_score_desc": "Type a target top percentage rank below to instantly see the score threshold required to hit it.",
        "pct_input_label": "Enter target top percentage rank (%):",
        "pct_input_help": "Type a target top percentage rank (e.g. 5.0 for top 5%).",
        "min_score_required": "Minimum Required Score",
        "actual_rank_label": "Actual Rank",
        "cum_table_section": "📋 Cumulative Distribution Table",
        "cum_table_desc": "Examine the exact cumulative count of students at specific score thresholds. This helps in predicting entry thresholds.",
        "select_table_block": "Select block to view detailed table:",
        "tab_filtered_scope": "🎯 Filtered Pool (Current Scope)",
        "tab_whole_population": "🌐 Whole Population (All Candidates)",
        "filtered_table_desc": "Statistics for candidates within current candidate limits and score filter scope (percentage relative to filtered scope):",
        "whole_table_desc": "Same score scope, but percentage is calculated relative to all candidates following active candidate limiters:",
        "col_threshold": "Score Threshold (≥)",
        "col_num_students": "Number of Students",
        "col_percentage": "Percentage",
        "data_preview_section": "🔍 Data Preview",
        "data_preview_desc": "Showing a preview of the loaded dataset:",
        "no_candidates_scope": "No candidates fall within this dataset scope.",
        "hover_dist": "<b>%{customdata}</b><br>Score: %{x:.2f}<br>Count: %{y:,} candidates<br>Percentage: %{text:.2f}%<extra></extra>",
        "hover_cum": "<b>%{customdata}</b><br>Score &ge; %{x:.2f}<br>Candidates: %{y:,}<br>Top %{text:.2f}%<extra></extra>"
    },
    "Tiếng Việt": {
        "title": "📊 Bộ Trực Quan Hóa Phổ Điểm",
        "subtitle": "Phân tích và so sánh phổ điểm thi đại học, dự đoán điểm chuẩn (2025 vs 2026)",
        "data_import": "📂 Nhập Dữ Liệu",
        "upload_csv": "Tải lên Điểm Số Học Sinh (CSV)",
        "success_loaded": "Tải thành công file CSV đã tải lên!",
        "loaded_default": "Đã tự động tải file Diem20252026.csv từ thư mục làm việc.",
        "error_no_file": "Lỗi: Không tìm thấy file Diem20252026.csv. Vui lòng tải lên file CSV ở thanh bên.",
        "viz_settings": "⚙️ Cấu Hình Trực Quan Hóa",
        "select_years": "**Chọn Năm Hiển Thị:**",
        "year_2026": "2026 (Năm hiện tại)",
        "year_2025": "2025 (Năm so sánh)",
        "select_blocks": "**Chọn Khối Thi:**",
        "score_step": "Bước chia điểm (Binned Step)",
        "score_step_help": "Xác định khoảng gộp điểm của học sinh. Thang điểm chuẩn thường dùng bước 0.25.",
        "cand_limiters": "🔢 Giới Hạn Thí Sinh (1 đến N)",
        "only_mien_bac": "Chỉ tính Miền Bắc",
        "only_mien_bac_help": "Nếu chọn, sẽ giới hạn dữ liệu về đúng khu vực Miền Bắc: 592,591 thí sinh đầu tiên cho năm 2026 và 666,892 thí sinh đầu tiên cho năm 2025.",
        "mien_bac_applied": "Đã áp dụng giới hạn Miền Bắc:\n- 2026: {limit_2026:,} thí sinh\n- 2025: {limit_2025:,} thí sinh",
        "limit_2026_label": "Giới hạn thí sinh 2026 (N):",
        "limit_2026_help": "Giới hạn dữ liệu 2026 ở N học sinh đầu tiên (dòng đầu).",
        "limit_2025_label": "Giới hạn thí sinh 2025 (M):",
        "limit_2025_help": "Giới hạn dữ liệu 2025 ở M học sinh đầu tiên (dòng đầu).",
        "missing_handling": "⚠️ Xử Lý Dữ Liệu Trống",
        "treat_blanks": "Coi điểm trống/vắng thi là 0",
        "treat_blanks_help": "Nếu chọn, điểm vắng hoặc trống sẽ tính là 0.0. Nếu không chọn, chúng sẽ bị loại bỏ khỏi tính toán.",
        "agg_mode_title": "🔗 Chế Độ Gộp Biểu Đồ",
        "plot_mode_label": "Chế độ hiển thị:",
        "plot_mode_help": "Tách riêng: Vẽ mỗi khối đã chọn thành một đường riêng biệt.\nGộp khối: Gộp tất cả các khối đã chọn thành một phân phối chung duy nhất theo từng năm.",
        "plot_mode_opt_sep": "Tách riêng các khối",
        "plot_mode_opt_comb": "Gộp chung khối đã chọn",
        "score_filter_title": "🎯 Bộ Lọc Khoảng Điểm",
        "score_filter_label": "Giới Hạn Khoảng Điểm Số:",
        "score_filter_help": "Chỉ tính các thí sinh có điểm nằm trong khoảng này.",
        "warning_select": "⚠️ Vui lòng chọn ít nhất một năm và một khối thi từ thanh bên để hiển thị dữ liệu.",
        "warning_no_data": "⚠️ Không có dữ liệu nào khớp với bộ lọc khoảng điểm đã chọn. Vui lòng kiểm tra lại thiết lập ở thanh bên.",
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
        "cum_title": "Số Thí Sinh Đạt Mức Điểm Lớn Hơn Hoặc Bằng (Điểm ≥ X)",
        "cum_xaxis": "Ngưỡng Điểm Số",
        "cum_yaxis": "Số Lượng Thí Sinh Tích Lũy",
        "rank_calc_title": "🔍 Tra Cứu Điểm Số & Thứ Hạng",
        "rank_calc_desc": "Tra cứu mối tương quan giữa điểm số và thứ hạng phần trăm (theo giới hạn thí sinh hiện tại).",
        "score_to_pct_tab": "🎯 Tra Điểm → Thứ Hạng %",
        "pct_to_score_tab": "📊 Nhập % → Tìm Điểm Chuẩn",
        "score_to_pct_desc": "Nhập một điểm số bên dưới để xem ngay có bao nhiêu học sinh đạt điểm lớn hơn hoặc bằng (≥) mức đó và tỷ lệ phần trăm tương ứng.",
        "score_input_label": "Nhập điểm số cần tra cứu:",
        "score_input_help": "Nhập bất kỳ điểm số nào để tính thứ hạng ngay lập tức.",
        "top_rank_pct_label": "Tỷ Lệ Phần Trăm Thứ Hạng (Top %)",
        "candidates_ge_label": "Số thí sinh &ge;",
        "total_pool_label": "Tổng Số Thí Sinh",
        "pct_to_score_desc": "Nhập phần trăm xếp hạng mong muốn (top %) để tính ngay mức điểm tối thiểu cần đạt để lọt vào top đó.",
        "pct_input_label": "Nhập tỷ lệ phần trăm thứ hạng mong muốn (%):",
        "pct_input_help": "Nhập phần trăm xếp hạng mong muốn (Ví dụ: 5.0 tương ứng với top 5%).",
        "min_score_required": "Mức Điểm Tối Thiểu Cần Đạt",
        "actual_rank_label": "Thứ Hạng Thực Tế Đạt Được",
        "cum_table_section": "📋 Bảng Phân Phối Tích Lũy",
        "cum_table_desc": "Xem chi tiết số lượng thí sinh tích lũy ở các ngưỡng điểm nửa điểm. Hỗ trợ dự đoán điểm chuẩn xét tuyển.",
        "select_table_block": "Chọn khối thi cần hiển thị bảng chi tiết:",
        "tab_filtered_scope": "🎯 Khoảng Điểm Được Lọc (Filtered Pool)",
        "tab_whole_population": "🌐 Toàn Bộ Thí Sinh (Whole Population)",
        "filtered_table_desc": "Thống kê cho các thí sinh nằm trong khoảng giới hạn và khoảng điểm được lọc (tỷ lệ phần trăm tính theo lượng điểm lọc):",
        "whole_table_desc": "Giữ nguyên khoảng điểm, nhưng tỷ lệ phần trăm được tính trên toàn bộ thí sinh theo giới hạn vùng miền (bỏ qua lọc khoảng điểm):",
        "col_threshold": "Ngưỡng Điểm (≥)",
        "col_num_students": "Số Lượng Học Sinh",
        "col_percentage": "Tỷ Lệ Phần Trăm",
        "data_preview_section": "🔍 Xem Trước Dữ Liệu",
        "data_preview_desc": "Xem trước 20 dòng đầu tiên của tập dữ liệu đã tải:",
        "no_candidates_scope": "Không có thí sinh nào nằm trong khoảng dữ liệu này.",
        "hover_dist": "<b>%{customdata}</b><br>Điểm số: %{x:.2f}<br>Số thí sinh: %{y:,}<br>Tỷ lệ phần trăm: %{text:.2f}%<extra></extra>",
        "hover_cum": "<b>%{customdata}</b><br>Điểm số &ge; %{x:.2f}<br>Số thí sinh: %{y:,}<br>Top %{text:.2f}%<extra></extra>"
    }
}

# Set up page configuration
st.set_page_config(
    page_title="Score Spectrum Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern glassmorphism styling and glowing details
st.markdown("""
<style>
    /* Import modern Google font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Main container styling */
    .main-title {
        font-weight: 700;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #FF4B4B, #FF8F8F, #4A90E2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #8892B0;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* Glassmorphism Card Wrapper */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.3s ease, border 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(255, 75, 75, 0.4);
    }
    
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF4B4B;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #8892B0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Section dividers */
    .section-header {
        font-weight: 600;
        font-size: 1.5rem;
        color: #E2E8F0;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
@st.cache_data
def load_data(file_path_or_buffer):
    df = pd.read_csv(file_path_or_buffer)
    return df

# Header Row with Language Picker in top right corner
col_title, col_lang = st.columns([8, 2])
with col_lang:
    selected_lang = st.selectbox(
        "Language Selection",
        options=["English", "Tiếng Việt"],
        index=0,
        label_visibility="collapsed"
    )

# Active Translations
t = TRANSLATIONS[selected_lang]

# Main Titles in Left Column
with col_title:
    st.markdown(f'<div class="main-title">{t["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{t["subtitle"]}</div>', unsafe_allow_html=True)

# Sidebar layout
st.sidebar.markdown(f"### {t['data_import']}")
uploaded_file = st.sidebar.file_uploader(t["upload_csv"], type=['csv'])

# Default file loading
if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.sidebar.success(t["success_loaded"])
else:
    try:
        # Load Diem20252026.csv as requested by default
        df = load_data("Diem20252026.csv")
        st.sidebar.info(t["loaded_default"])
    except FileNotFoundError:
        st.error(t["error_no_file"])
        st.stop()

# Clean up column names (strip quotes, extra spaces, carriage returns)
df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "").str.replace('\r', '').str.replace('\n', '')

# Convert columns to numeric, converting non-numeric artifacts (like '.....') to NaN
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Treat all scores smaller than 15 as trash (convert them to NaN so they are completely excluded)
for col in df.columns:
    if col != 'Student_ID':
        df.loc[df[col] < 15.0, col] = np.nan

# Check actual columns in dataframe to build filters dynamically
available_cols = list(df.columns)

# Dynamic block detection:
# Find all columns, strip year suffixes like "2025" or " 2025"
detected_blocks = []
for col in available_cols:
    cleaned = col
    for suffix in [" 2025", " 2026", "2025", "2026"]:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)]
    cleaned = cleaned.strip()
    if cleaned and cleaned != "Student_ID" and cleaned not in detected_blocks:
        detected_blocks.append(cleaned)

# Sort detected blocks to look clean, prioritizing standard ones
standard_order = ["A00", "A01", "D01", "A00 TOAN X2", "A01 TOAN X2"]
base_blocks = [b for b in standard_order if b in detected_blocks] + [b for b in detected_blocks if b not in standard_order]

# Fallback if no blocks detected
if not base_blocks:
    base_blocks = ["A00", "A01", "D01", "A00 TOAN X2", "A01 TOAN X2"]

st.sidebar.markdown(f"### {t['viz_settings']}")

# Year checkboxes
st.sidebar.write(t["select_years"])
show_2026 = st.sidebar.checkbox(t["year_2026"], value=True)
show_2025 = st.sidebar.checkbox(t["year_2025"], value=True)

# Exam blocks checkboxes
st.sidebar.write(t["select_blocks"])
selected_blocks = []
for b in base_blocks:
    if st.sidebar.checkbox(b, value=(b == "A00")):
        selected_blocks.append(b)

# Score bin step size slider
score_step = st.sidebar.slider(
    t["score_step"], 
    min_value=0.1, 
    max_value=2.0, 
    value=0.25, 
    step=0.05,
    help=t["score_step_help"]
)

# Year Limiters
st.sidebar.markdown(f"### {t['cand_limiters']}")
max_candidates = len(df)

# Regional Filter Checkbox
only_mien_bac = st.sidebar.checkbox(
    t["only_mien_bac"], 
    value=False,
    help=t["only_mien_bac_help"]
)

if only_mien_bac:
    limit_2026 = min(592591, max_candidates)
    limit_2025 = min(666892, max_candidates)
    st.sidebar.info(t["mien_bac_applied"].format(limit_2026=limit_2026, limit_2025=limit_2025))
else:
    limit_2026 = st.sidebar.number_input(
        t["limit_2026_label"],
        min_value=1,
        max_value=max_candidates,
        value=max_candidates,
        step=10,
        help=t["limit_2026_help"]
    )

    limit_2025 = st.sidebar.number_input(
        t["limit_2025_label"],
        min_value=1,
        max_value=max_candidates,
        value=max_candidates,
        step=10,
        help=t["limit_2025_help"]
    )

# Missing Data Handling
st.sidebar.markdown(f"### {t['missing_handling']}")
fill_blanks_with_zero = st.sidebar.checkbox(
    t["treat_blanks"], 
    value=False,
    help=t["treat_blanks_help"]
)

# Aggregation Mode
st.sidebar.markdown(f"### {t['agg_mode_title']}")
agg_mode = st.sidebar.radio(
    t["plot_mode_label"],
    options=[t["plot_mode_opt_sep"], t["plot_mode_opt_comb"]],
    index=0,
    help=t["plot_mode_help"]
)
agg_mode_internal = "Separate Blocks" if agg_mode == t["plot_mode_opt_sep"] else "Combine Selected Blocks"

# Construct selected columns list based on checkboxes
selected_cols = []
for b in selected_blocks:
    if show_2026:
        # Check if block name is in dataframe columns
        if b in available_cols:
            selected_cols.append((b, "2026", b))
    if show_2025:
        # 2025 suffix column format
        col_2025 = f"{b} 2025"
        if col_2025 in available_cols:
            selected_cols.append((b, "2025", col_2025))

if not selected_cols:
    st.warning(t["warning_select"])
    st.stop()

# Determine dynamic min/max for the slider bounds
selected_col_names = [col for _, _, col in selected_cols]
min_score_val = 0.0
max_score_val = 40.0
if selected_col_names:
    min_score_val = float(df[selected_col_names].min().min())
    max_score_val = float(df[selected_col_names].max().max())

if np.isnan(min_score_val): min_score_val = 0.0
if np.isnan(max_score_val): max_score_val = 40.0

st.sidebar.markdown(f"### {t['score_filter_title']}")
default_min = min(15.0, float(np.ceil(max_score_val)))
default_max = min(30.0, float(np.ceil(max_score_val)))
score_range = st.sidebar.slider(
    t["score_filter_label"],
    min_value=0.0,
    max_value=float(np.ceil(max_score_val)),
    value=(default_min, default_max),
    step=0.5,
    help=t["score_filter_help"]
)

# Prepare the datasets to analyze
datasets_to_analyze = []
if agg_mode_internal == "Separate Blocks":
    for b, y, col in selected_cols:
        limit = limit_2026 if y == "2026" else limit_2025
        col_raw = df[col].head(limit)
        if fill_blanks_with_zero:
            col_limited = col_raw.fillna(0.0)
        else:
            col_limited = col_raw.dropna()
        col_data = col_limited[(col_limited >= score_range[0]) & (col_limited <= score_range[1])]
        
        datasets_to_analyze.append({
            "name": f"{b} ({y})",
            "legend_name": f"{b} ({y})",
            "block": b,
            "year": y,
            "data": col_data,
            "limited_population": col_limited
        })
else:
    # Combine mode: group selected blocks by year
    for year in ["2026", "2025"]:
        year_cols = [col for b, y, col in selected_cols if y == year]
        if year_cols:
            limit = limit_2026 if year == "2026" else limit_2025
            pooled_list = []
            pooled_limited_list = []
            for col in year_cols:
                col_raw = df[col].head(limit)
                if fill_blanks_with_zero:
                    col_limited = col_raw.fillna(0.0)
                else:
                    col_limited = col_raw.dropna()
                col_data = col_limited[(col_limited >= score_range[0]) & (col_limited <= score_range[1])]
                pooled_list.append(col_data)
                pooled_limited_list.append(col_limited)
            
            if pooled_list:
                pooled_data = pd.concat(pooled_list, ignore_index=True)
                pooled_limited = pd.concat(pooled_limited_list, ignore_index=True)
                # Form a label like "A00 + A01"
                selected_blocks_for_year = [b for b, y, _ in selected_cols if y == year]
                unique_blocks = []
                for b in selected_blocks_for_year:
                    if b not in unique_blocks:
                        unique_blocks.append(b)
                blocks_label = " + ".join(unique_blocks)
                name = f"Combined [{blocks_label}] ({year})"
                
                datasets_to_analyze.append({
                    "name": name,
                    "legend_name": name,
                    "block": f"Combined [{blocks_label}]",
                    "year": year,
                    "data": pooled_data,
                    "limited_population": pooled_limited
                })

if not datasets_to_analyze or all(len(ds["data"]) == 0 for ds in datasets_to_analyze):
    st.warning(t["warning_no_data"])
    st.stop()

# --- Key Metrics Section ---
st.markdown(f'<div class="section-header">{t["perf_summary"]}</div>', unsafe_allow_html=True)

# Calculate stats for selected columns/groups
valid_ds = [ds for ds in datasets_to_analyze if len(ds["data"]) > 0]
metrics_cols = st.columns(min(len(valid_ds), 4))
for idx, ds in enumerate(valid_ds):
    col_data = ds["data"]
    block = ds["block"]
    year = ds["year"]
    
    # We display up to 4 metric cards (most relevant)
    if idx < 4:
        avg_score = col_data.mean()
        max_score = col_data.max()
        total_students = len(col_data)
        
        # Calculate % of students scoring high (>= 24.0 or scaled >= 32.0 for TOAN X2)
        threshold = 32.0 if "TOAN X2" in block else 24.0
        pct_high = (col_data >= threshold).mean() * 100
        
        with metrics_cols[idx]:
            card_html = f"""
            <div class="metric-card">
                <div class="metric-label">{block} ({year})</div>
                <div class="metric-val">{avg_score:.2f}</div>
                <div style="color: #E2E8F0; font-weight: 500; font-size: 1.1rem; margin-bottom: 0.5rem;">{t["avg_score_label"]}</div>
                <div style="color: #8892B0; font-size: 0.85rem;">
                    {t["max_label"]}: <b>{max_score:.2f}</b> | {t["total_label"]}: <b>{total_students:,}</b><br>
                    &ge;{threshold:.0f} {t["high_threshold_label"]}: <b>{pct_high:.1f}%</b>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

# --- Graph Section ---
st.markdown(f'<div class="section-header">📊 {t["dist_spectrum_tab"].replace("📊 ", "")} & {t["cum_curve_tab"].replace("📈 ", "")}</div>', unsafe_allow_html=True)

# Tab selection for Spectrum vs Cumulative Graph
tab_dist, tab_cum = st.tabs([t["dist_spectrum_tab"], t["cum_curve_tab"]])

# Clean & Prepare data for plotting
plot_data_list = []
for ds in datasets_to_analyze:
    col_data = ds["data"]
    if len(col_data) == 0:
        continue
    block = ds["block"]
    year = ds["year"]
    legend_name = ds["legend_name"]
    
    # Round/Bin scores based on the step size
    binned_scores = (col_data / score_step).round() * score_step
    
    # Generate frequencies
    counts = binned_scores.value_counts().sort_index().reset_index()
    counts.columns = ['Score', 'Count']
    counts['Percent'] = (counts['Count'] / len(col_data)) * 100
    counts['Block'] = block
    counts['Year'] = year
    counts['Legend'] = legend_name
    
    # Generate cumulative counts (Students scoring >= score)
    cum_data = col_data.value_counts().sort_index(ascending=False).reset_index()
    cum_data.columns = ['Score', 'Count']
    cum_data['Cumulative_Count'] = cum_data['Count'].cumsum()
    cum_data['Cumulative_Percent'] = (cum_data['Cumulative_Count'] / len(col_data)) * 100
    cum_data['Block'] = block
    cum_data['Year'] = year
    cum_data['Legend'] = legend_name
    
    plot_data_list.append((counts, cum_data))

# Plot colors
colors = ['#FF4B4B', '#4A90E2', '#50E3C2', '#F5A623', '#D0021B', '#B8E986', '#7ED321', '#9013FE']

with tab_dist:
    fig_dist = go.Figure()
    
    # Add traces
    for idx, (counts, _) in enumerate(plot_data_list):
        color = colors[idx % len(colors)]
        
        # Line + Area plot for smooth spectrum feel
        fig_dist.add_trace(go.Scatter(
            x=counts['Score'],
            y=counts['Count'],
            mode='lines+markers',
            name=counts['Legend'].iloc[0],
            line=dict(color=color, width=3),
            marker=dict(size=6, symbol='circle'),
            fill='tozeroy',
            fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.15])}", # 15% opacity fill
            hovertemplate=t["hover_dist"],
            text=counts['Percent'],
            customdata=counts['Legend']
        ))
        
    fig_dist.update_layout(
        title=t["dist_title"],
        xaxis_title=t["dist_xaxis"],
        yaxis_title=t["dist_yaxis"],
        hovermode="x unified",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)")
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with tab_cum:
    fig_cum = go.Figure()
    
    # Add traces for cumulative
    for idx, (_, cum_data) in enumerate(plot_data_list):
        color = colors[idx % len(colors)]
        
        # Sort values ascending by Score so the line draws correctly from left to right
        cum_sorted = cum_data.sort_values(by='Score')
        
        fig_cum.add_trace(go.Scatter(
            x=cum_sorted['Score'],
            y=cum_sorted['Cumulative_Count'],
            mode='lines',
            name=cum_sorted['Legend'].iloc[0],
            line=dict(color=color, width=3, shape='hv'), # 'hv' gives step feel which is perfect for cutoffs
            hovertemplate=t["hover_cum"],
            text=cum_sorted['Cumulative_Percent'],
            customdata=cum_sorted['Legend']
        ))
        
    fig_cum.update_layout(
        title=t["cum_title"],
        xaxis_title=t["cum_xaxis"],
        yaxis_title=t["cum_yaxis"],
        hovermode="x unified",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor="rgba(255,255,255,0.2)")
    )
    st.plotly_chart(fig_cum, use_container_width=True)

# --- Custom Rank Calculator (Score <--> Percent) ---
st.markdown(f'<div class="section-header">{t["rank_calc_title"]}</div>', unsafe_allow_html=True)
st.write(t["rank_calc_desc"])

calc_tab1, calc_tab2 = st.tabs([t["score_to_pct_tab"], t["pct_to_score_tab"]])

with calc_tab1:
    st.write(t["score_to_pct_desc"])
    lookup_score = st.number_input(
        t["score_input_label"],
        min_value=0.0,
        max_value=40.0,
        value=25.0,
        step=0.25,
        key="calc_lookup_score",
        help=t["score_input_help"]
    )
    
    calc_cols = st.columns(min(len(datasets_to_analyze), 4))
    for idx, ds in enumerate(datasets_to_analyze):
        col_limited = ds["limited_population"]
        total_len = len(col_limited)
        
        if total_len > 0:
            sorted_arr = np.sort(col_limited.values)
            idx_ge = np.searchsorted(sorted_arr, lookup_score, side='left')
            count_ge = total_len - idx_ge
            pct_ge = (count_ge / total_len) * 100
        else:
            count_ge = 0
            pct_ge = 0.0
            
        with calc_cols[idx % 4]:
            card_html = f"""
            <div class="metric-card" style="border-left: 4px solid #10B981; background: rgba(16, 185, 129, 0.05);">
                <div class="metric-label">{ds["name"]}</div>
                <div class="metric-val" style="color: #10B981; font-size: 1.8rem; line-height: 2.2rem;">{pct_ge:.4f}%</div>
                <div style="color: #E2E8F0; font-weight: 500; font-size: 0.95rem; margin-top: 0.2rem; margin-bottom: 0.4rem;">
                    {t["top_rank_pct_label"]}
                </div>
                <div style="color: #8892B0; font-size: 0.85rem;">
                    {t["candidates_ge_label"]} <b>{lookup_score:.2f}</b>: <span style="color: #E2E8F0; font-weight: bold;">{count_ge:,}</span><br>
                    {t["total_pool_label"]}: <b>{total_len:,}</b>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

with calc_tab2:
    st.write(t["pct_to_score_desc"])
    lookup_pct = st.number_input(
        t["pct_input_label"],
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.1,
        key="calc_lookup_pct",
        help=t["pct_input_help"]
    )
    
    calc_cols2 = st.columns(min(len(datasets_to_analyze), 4))
    for idx, ds in enumerate(datasets_to_analyze):
        col_limited = ds["limited_population"]
        total_len = len(col_limited)
        
        if total_len > 0:
            sorted_arr = np.sort(col_limited.values)
            # Find index matching the target top P%
            target_idx = np.clip(int(total_len * (1 - lookup_pct / 100)), 0, total_len - 1)
            threshold_score = sorted_arr[target_idx]
            
            # Double check exact count scoring >= this score
            idx_ge = np.searchsorted(sorted_arr, threshold_score, side='left')
            exact_count = total_len - idx_ge
            exact_pct = (exact_count / total_len) * 100
        else:
            threshold_score = 0.0
            exact_count = 0
            exact_pct = 0.0
            
        with calc_cols2[idx % 4]:
            card_html = f"""
            <div class="metric-card" style="border-left: 4px solid #3B82F6; background: rgba(59, 130, 246, 0.05);">
                <div class="metric-label">{ds["name"]}</div>
                <div class="metric-val" style="color: #3B82F6; font-size: 1.8rem; line-height: 2.2rem;">{threshold_score:.2f} pts</div>
                <div style="color: #E2E8F0; font-weight: 500; font-size: 0.95rem; margin-top: 0.2rem; margin-bottom: 0.4rem;">
                    {t["min_score_required"]}
                </div>
                <div style="color: #8892B0; font-size: 0.85rem;">
                    {t["actual_rank_label"]}: <span style="color: #E2E8F0; font-weight: bold;">{exact_pct:.4f}%</span><br>
                    {t["candidates_ge_label"]} <b>{threshold_score:.2f}</b>: <b>{exact_count:,}</b>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

# Helper function to generate the cumulative table using binary search
def make_cumulative_table(data_series, denominator):
    total_len = len(data_series)
    if total_len > 0 and denominator > 0:
        # We want a nice lookup table at integer or half-integer steps
        step_scores = np.arange(np.floor(data_series.min()), np.ceil(data_series.max()) + 0.5, 0.5)
        step_scores = np.flip(step_scores) # Higher scores first
        
        # Optimize count computation using binary search
        sorted_arr = np.sort(data_series.values)
        
        table_rows = []
        for s in step_scores:
            idx = np.searchsorted(sorted_arr, s, side='left')
            count_ge = total_len - idx
            pct_ge = (count_ge / denominator) * 100
            table_rows.append({
                t["col_threshold"]: f"{s:.2f}",
                t["col_num_students"]: f"{count_ge:,}",
                t["col_percentage"]: f"{pct_ge:.2f}%"
            })
            
        table_df = pd.DataFrame(table_rows)
        st.dataframe(table_df, width='stretch', height=300)
    else:
        st.info(t["no_candidates_scope"])

# --- Details Table / Cumulative Analysis ---
st.markdown(f'<div class="section-header">{t["cum_table_section"]}</div>', unsafe_allow_html=True)
st.write(t["cum_table_desc"])

# Create columns for multiple tables, or just select one to display
selected_ds_name = st.selectbox(
    t["select_table_block"],
    options=[ds["name"] for ds in datasets_to_analyze if len(ds["data"]) > 0]
)

if selected_ds_name:
    # Find the dataset
    ds = next(item for item in datasets_to_analyze if item["name"] == selected_ds_name)
    
    tab_filt, tab_whole = st.tabs([t["tab_filtered_scope"], t["tab_whole_population"]])
    
    with tab_filt:
        st.write(t["filtered_table_desc"])
        make_cumulative_table(ds["data"], len(ds["data"]))
        
    with tab_whole:
        st.write(t["whole_table_desc"])
        make_cumulative_table(ds["data"], len(ds["limited_population"]))

# --- Data Preview Section ---
st.markdown(f'<div class="section-header">{t["data_preview_section"]}</div>', unsafe_allow_html=True)
st.write(t["data_preview_desc"])
st.dataframe(df.head(20), width='stretch')
