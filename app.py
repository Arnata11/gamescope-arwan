"""
GameScope — Global Video Game Sales Analytics
Interactive Data Visualization Dashboard
Built with Python, Streamlit, Pandas, and Plotly.
"""

from pathlib import Path
import textwrap
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# 1. PAGE & ENVIRONMENT CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="GameScope | Global Video Game Sales Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    ROOT / "dataset" / "vgsales_clean.csv",
    ROOT / "dataset" / "vgsales.csv",
    ROOT / "vgsales.csv",
]

# Core schema requirements
REQUIRED_COLUMNS = [
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales",
    "Global_Sales",
]
REGION_COLUMNS = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
SALES_COLUMNS = [*REGION_COLUMNS, "Global_Sales"]
REGION_LABELS = {
    "NA_Sales": "North America",
    "EU_Sales": "Europe",
    "JP_Sales": "Japan",
    "Other_Sales": "Other Regions",
}

# ==============================================================================
# 2. DESIGN SYSTEM & COLOR PALETTE
# ==============================================================================
# Modern Editorial Analytics Palette (WCAG AA compliant contrast)
COLOR_PRIMARY = "#2563EB"       # Action & emphasis
COLOR_PRIMARY_DARK = "#1D4ED8"  # Hover & focus
COLOR_PAGE_BG = "#F8FAFC"       # Light slate page background
COLOR_SURFACE = "#FFFFFF"       # Card & widget surface
COLOR_TEXT_PRIMARY = "#0F172A"  # High-contrast slate text
COLOR_TEXT_MUTED = "#64748B"    # Secondary slate text
COLOR_BORDER = "#E2E8F0"        # Subtle card/divider border
COLOR_SUCCESS = "#15803D"       # Positive / active indicator
COLOR_WARNING = "#B45309"       # Warning state
COLOR_ERROR = "#B91C1C"         # Error state

# Harmonious Categorical Palette for 12 Video Game Genres (Colorblind-friendly)
GENRE_PALETTE = {
    "Action": "#2563EB",
    "Sports": "#059669",
    "Shooter": "#DC2626",
    "Role-Playing": "#7C3AED",
    "Platform": "#D97706",
    "Misc": "#0891B2",
    "Racing": "#EA580C",
    "Fighting": "#DB2777",
    "Simulation": "#0D9488",
    "Puzzle": "#4F46E5",
    "Adventure": "#CA8A04",
    "Strategy": "#475569",
}


def render_html(html_str: str):
    """Render raw HTML safely without markdown indentation code block quirks."""
    clean_html = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)


# ==============================================================================
# 3. CENTRALIZED INDONESIAN NUMBER FORMATTERS
# ==============================================================================
def fmt_number(val: float, decimals: int = 2) -> str:
    """Format floating point numbers using Indonesian standard: comma decimal, dot thousand."""
    if pd.isna(val):
        return "-"
    s = f"{float(val):,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_int(val: int) -> str:
    """Format integers using Indonesian dot thousand separators."""
    if pd.isna(val):
        return "-"
    return f"{int(val):,}".replace(",", ".")


def fmt_sales(value: float, include_unit: bool = True) -> str:
    """Format sales volume in million units following Indonesian number conventions.
    
    Examples:
        fmt_sales(82.74, True)  -> '82,74 juta unit'
        fmt_sales(82.74, False) -> '82,74'
    """
    formatted = fmt_number(value, decimals=2)
    return f"{formatted} juta unit" if include_unit else formatted


def fmt_percent(value: float, decimals: int = 1) -> str:
    """Format percentage with Indonesian comma decimal (e.g. '19,6%')."""
    if pd.isna(value):
        return "0,0%"
    return f"{fmt_number(value, decimals=decimals)}%"


# ==============================================================================
# 4. TAILORED CSS STYLING
# ==============================================================================
st.markdown(
    """
<style>
    /* Global Typography & Viewport Setup */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1520px;
    }
    
    /* Editorial Header / Hero Container */
    .hero-container {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #EFF6FF;
        color: #2563EB;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 10px;
        border: 1px solid #DBEAFE;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.03em;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #475569;
        line-height: 1.5;
        margin: 0 0 14px 0;
    }
    .hero-meta-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding-top: 14px;
        border-top: 1px solid #F1F5F9;
    }
    .hero-meta-pill {
        font-size: 0.78rem;
        color: #64748B;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 4px 10px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Active Filter Summary Bar */
    .filter-summary-bar {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 16px;
        margin-bottom: 22px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        font-size: 0.82rem;
    }
    .filter-summary-label {
        font-weight: 700;
        color: #0F172A;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-size: 0.72rem;
    }
    .filter-summary-chip {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 3px 8px;
        color: #334155;
    }
    
    /* Native Metric Cards Redesign - Perfectly Uniform Height */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 18px 20px !important;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04) !important;
        min-height: 116px !important;
        height: 116px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.08) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #64748B !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.025em !important;
        line-height: 1.25 !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    [data-testid="column"] .stCaption {
        min-height: 22px;
        margin-top: 4px;
    }

    /* Clean Editorial Section Divider */
    .section-divider {
        border: none;
        height: 1px;
        background: #E2E8F0;
        margin: 36px 0 24px 0;
    }
    
    /* Section Headings */
    .section-header-box {
        margin-top: 4px;
        margin-bottom: 16px;
    }
    .section-tag {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #2563EB;
        margin-bottom: 4px;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .section-subtitle {
        font-size: 0.86rem;
        color: #64748B;
        margin: 3px 0 0 0;
    }
    
    /* Dynamic Insight Cards Grid (100% Uniform Height via CSS Grid) */
    .insight-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        align-items: stretch;
        margin-top: 10px;
        margin-bottom: 14px;
    }
    @media (max-width: 1100px) {
        .insight-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    @media (max-width: 640px) {
        .insight-grid {
            grid-template-columns: 1fr;
        }
    }
    .insight-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        height: 100%;
        min-height: 195px;
        box-sizing: border-box;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .insight-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.07);
    }
    .insight-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #2563EB;
        margin-bottom: 6px;
    }
    .insight-value {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
        line-height: 1.25;
    }
    .insight-desc {
        font-size: 0.84rem;
        color: #475569;
        line-height: 1.5;
        margin: 0;
        flex-grow: 1;
    }
    
    /* Empty State Banner */
    .empty-state-card {
        background-color: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 14px;
        padding: 44px 24px;
        text-align: center;
        margin: 28px 0;
    }
    .empty-state-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin: 12px 0 6px 0;
    }
    .empty-state-desc {
        font-size: 0.88rem;
        color: #64748B;
        max-width: 520px;
        margin: 0 auto 20px auto;
        line-height: 1.5;
    }
    
    /* Responsive Helper Tweaks */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        .hero-title {
            font-size: 1.45rem;
        }
        .hero-container {
            padding: 18px 20px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 5. DATA LOADING & VALIDATION
# ==============================================================================
def get_dataset_path() -> Optional[Path]:
    """Find the first available dataset path from candidates."""
    return next((p for p in DATA_CANDIDATES if p.exists()), None)


@st.cache_data(show_spinner="Memuat dan memvalidasi dataset...")
def load_data(path_string: str) -> pd.DataFrame:
    """Load, validate schema, clean, and standardize the video game dataset.
    
    Args:
        path_string: Filepath to the CSV dataset.
        
    Returns:
        pd.DataFrame: Validated and sanitized dataframe.
    """
    df = pd.read_csv(path_string)
    df.columns = [str(c).strip() for c in df.columns]

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(sorted(missing))}")

    df = df.copy()
    for col in ["Name", "Platform", "Genre", "Publisher"]:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA, "N/A": pd.NA, "nan": pd.NA})

    numeric_cols = ["Year", *REGION_COLUMNS, "Global_Sales"]
    if "Rank" in df.columns:
        numeric_cols.append("Rank")

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filter out rows missing essential identity and sales attributes
    df = df.dropna(subset=["Name", "Platform", "Genre", "Global_Sales"])
    
    # Non-negative sales verification
    df = df[(df[SALES_COLUMNS] >= 0).all(axis=1)]
    df = df.drop_duplicates()

    df["Year"] = df["Year"].round().astype("Int64")
    df["Release year"] = df["Year"].astype("string").fillna("Unknown")
    df["Game_Identifier"] = df["Name"] + " (" + df["Platform"] + ")"

    return df


# ==============================================================================
# 6. FILTER PROCESSING & AGGREGATION
# ==============================================================================
def apply_filters(
    df: pd.DataFrame,
    year_range: Optional[Tuple[int, int]],
    selected_genres: List[str],
    selected_platforms: List[str],
    search_query: str = "",
) -> pd.DataFrame:
    """Apply interactive user filters across year, genre, platform, and game search.
    
    Args:
        df: Input dataframe.
        year_range: Tuple of (min_year, max_year) or None.
        selected_genres: List of chosen genre names.
        selected_platforms: List of chosen platform names.
        search_query: Search string for game title or publisher.
        
    Returns:
        pd.DataFrame: Filtered subset dataframe.
    """
    filtered = df.copy()

    # Year filter: preserves unknown/missing years in overall aggregations
    if year_range is not None:
        filtered = filtered[
            filtered["Year"].isna()
            | filtered["Year"].between(year_range[0], year_range[1])
        ]

    if selected_genres:
        filtered = filtered[filtered["Genre"].astype(str).isin(selected_genres)]
    else:
        filtered = filtered.iloc[0:0]

    if selected_platforms:
        filtered = filtered[filtered["Platform"].astype(str).isin(selected_platforms)]
    else:
        filtered = filtered.iloc[0:0]

    # Search filter by game title or publisher
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["Name"].astype(str).str.lower().str.contains(q, na=False)
            | filtered["Publisher"].astype(str).str.lower().str.contains(q, na=False)
        ]

    return filtered


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate the core analytical KPIs including top best-selling game title.
    
    Args:
        df: Filtered dataframe.
        
    Returns:
        Dict: Key metric values and supporting metadata (retaining pure numeric values).
    """
    if df.empty:
        return {
            "total_sales": 0.0,
            "game_records": 0,
            "top_genre": "N/A",
            "top_genre_sales": 0.0,
            "top_genre_share": 0.0,
            "avg_sales": 0.0,
            "top_game_name": "N/A",
            "top_game_sales": 0.0,
            "top_game_platform": "N/A",
            "top_game_year": "N/A",
        }

    total_sales = float(df["Global_Sales"].sum())
    game_records = len(df)
    avg_sales = float(df["Global_Sales"].mean()) if game_records > 0 else 0.0

    genre_totals = df.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False)
    if not genre_totals.empty:
        top_genre = str(genre_totals.index[0])
        top_genre_sales = float(genre_totals.iloc[0])
        top_genre_share = (top_genre_sales / total_sales * 100.0) if total_sales > 0 else 0.0
    else:
        top_genre = "N/A"
        top_genre_sales = 0.0
        top_genre_share = 0.0

    # Best-selling game title identification
    top_row = df.sort_values("Global_Sales", ascending=False).iloc[0]
    top_game_name = str(top_row["Name"])
    top_game_sales = float(top_row["Global_Sales"])
    top_game_platform = str(top_row["Platform"])
    top_game_year = str(top_row["Release year"])

    return {
        "total_sales": total_sales,
        "game_records": game_records,
        "top_genre": top_genre,
        "top_genre_sales": top_genre_sales,
        "top_genre_share": top_genre_share,
        "avg_sales": avg_sales,
        "top_game_name": top_game_name,
        "top_game_sales": top_game_sales,
        "top_game_platform": top_game_platform,
        "top_game_year": top_game_year,
    }


def generate_dynamic_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Compute dynamic, data-driven analytical insights following Indonesian number standards.
    
    Args:
        df: Filtered dataframe.
        
    Returns:
        List[Dict]: Insight items containing badge, title, value, and description.
    """
    if df.empty:
        return []

    total_sales = float(df["Global_Sales"].sum())
    insights = []

    # 1. Top Best-Selling Game Title & Gap (Contoh narasi resmi yang diharapkan)
    sorted_df = df.sort_values("Global_Sales", ascending=False)
    top_game_row = sorted_df.iloc[0]
    top_g_name = str(top_game_row["Name"])
    top_g_plat = str(top_game_row["Platform"])
    top_g_sales = float(top_game_row["Global_Sales"])
    
    if len(sorted_df) > 1:
        runner_up_sales = float(sorted_df.iloc[1]["Global_Sales"])
        gap = top_g_sales - runner_up_sales
        gap_desc = f"unggul {fmt_sales(gap)} dibandingkan game di posisi kedua."
    else:
        gap_desc = "merupakan satu-satunya judul pada filter ini."

    insights.append({
        "badge": "Game Terlaris",
        "title": top_g_name,
        "value": fmt_sales(top_g_sales),
        "description": (
            f"<b>{top_g_name} ({top_g_plat})</b> mencatat penjualan global tertinggi sebesar "
            f"<b>{fmt_sales(top_g_sales)}</b>, {gap_desc}"
        ),
    })

    # 2. Top Hardware Platform
    plat_totals = df.groupby("Platform")["Global_Sales"].sum().sort_values(ascending=False)
    plat_counts = df.groupby("Platform")["Name"].count()
    if not plat_totals.empty:
        top_p = str(plat_totals.index[0])
        top_p_sales = float(plat_totals.iloc[0])
        top_p_pct = (top_p_sales / total_sales * 100.0) if total_sales > 0 else 0.0
        top_p_count = int(plat_counts.get(top_p, 0))
        insights.append({
            "badge": "Top Platform",
            "title": top_p,
            "value": fmt_sales(top_p_sales),
            "description": (
                f"Platform <b>{top_p}</b> mencatatkan volume penjualan tertinggi sebesar <b>{fmt_sales(top_p_sales)}</b> "
                f"({fmt_percent(top_p_pct)} pangsa pasar) dari total <b>{fmt_int(top_p_count)}</b> judul rilis terindeks."
            ),
        })

    # 3. Dominant Regional Market
    regional_sums = df[REGION_COLUMNS].sum().sort_values(ascending=False)
    if not regional_sums.empty:
        top_r_col = regional_sums.index[0]
        top_r_name = REGION_LABELS.get(top_r_col, top_r_col)
        top_r_sales = float(regional_sums.iloc[0])
        all_regional = float(regional_sums.sum())
        top_r_pct = (top_r_sales / all_regional * 100.0) if all_regional > 0 else 0.0
        insights.append({
            "badge": "Wilayah Terbesar",
            "title": top_r_name,
            "value": fmt_sales(top_r_sales),
            "description": (
                f"Pasar <b>{top_r_name}</b> menjadi motor penggerak geografis utama dengan total penjualan <b>{fmt_sales(top_r_sales)}</b> "
                f"atau <b>{fmt_percent(top_r_pct)}</b> dari seluruh volume penjualan regional aktif."
            ),
        })

    # 4. Peak Historical Year & Best-Seller of that Year
    valid_years = df.dropna(subset=["Year"])
    if not valid_years.empty:
        yearly_sales = valid_years.groupby("Year")["Global_Sales"].sum().sort_values(ascending=False)
        yearly_counts = valid_years.groupby("Year")["Name"].count()
        peak_y = int(yearly_sales.index[0])
        peak_y_sales = float(yearly_sales.iloc[0])
        peak_y_count = int(yearly_counts.get(peak_y, 0))
        
        peak_year_games = valid_years[valid_years["Year"] == peak_y]
        peak_year_top_game = peak_year_games.sort_values("Global_Sales", ascending=False).iloc[0]["Name"]

        insights.append({
            "badge": "Tahun Puncak",
            "title": f"Tahun {peak_y}",
            "value": fmt_sales(peak_y_sales),
            "description": (
                f"Tahun <b>{peak_y}</b> mencetak rekor tahunan sebesar <b>{fmt_sales(peak_y_sales)}</b> "
                f"dari <b>{fmt_int(peak_y_count)}</b> gim bertahun valid. Judul terlaris era ini: <i>{peak_year_top_game}</i>."
            ),
        })
    else:
        insights.append({
            "badge": "Tahun Puncak",
            "title": "N/A",
            "value": "Data Kosong",
            "description": "Tidak ada catatan tahun rilis yang valid pada kriteria filter aktif saat ini.",
        })

    return insights


# ==============================================================================
# 7. VISUALIZATION CREATION (CORE CHARTS + GAME-CENTRIC EXPANSIONS)
# ==============================================================================
def create_top10_games_chart(df: pd.DataFrame) -> go.Figure:
    """Visualisasi A: Top 10 Best-Selling Video Games (Horizontal Bar Chart)."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Tidak ada data game yang cocok dengan filter saat ini.",
            showarrow=False,
            font=dict(size=13, color=COLOR_TEXT_MUTED),
        )
        fig.update_layout(template="plotly_white", height=380)
        return fig

    # Ambil 10 game teratas, dibalik urutannya agar rank 1 tampil di paling atas
    top10 = df.nlargest(10, "Global_Sales").iloc[::-1].copy()

    # Berikan penekanan visual warna emas/amber untuk peringkat 1, biru untuk peringkat lainnya
    colors = [COLOR_PRIMARY] * len(top10)
    if len(colors) > 0:
        colors[-1] = "#D97706"  # Highlight emas untuk Rank #1

    # Format label sumbu Y dengan nama game dan platform agar jelas
    y_labels = [f"{r['Name']} ({r['Platform']})" for _, r in top10.iterrows()]
    bar_texts = [f"{fmt_number(v)} juta unit" for v in top10["Global_Sales"]]
    formatted_sales = [fmt_sales(v) for v in top10["Global_Sales"]]

    top10["Formatted_Sales"] = formatted_sales

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top10["Global_Sales"],
            y=y_labels,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color=COLOR_PRIMARY_DARK, width=1),
            ),
            text=bar_texts,
            textposition="auto",
            textfont=dict(size=11, color="#FFFFFF"),
            customdata=top10[["Name", "Platform", "Release year", "Genre", "Publisher", "Formatted_Sales"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Platform: <b>%{customdata[1]}</b> | Tahun Rilis: <b>%{customdata[2]}</b><br>"
                "Genre: <b>%{customdata[3]}</b> | Publisher: <b>%{customdata[4]}</b><br>"
                "Penjualan Global: <b>%{customdata[5]}</b>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=10, r=30, t=25, b=25),
        font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY),
        hoverlabel=dict(bgcolor=COLOR_TEXT_PRIMARY, font_size=12, font_color="#FFFFFF"),
        xaxis=dict(
            title=dict(text="Penjualan Global (Juta Unit)", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY),
        ),
        showlegend=False,
    )
    return fig


def create_game_comparison_chart(df: pd.DataFrame, selected_titles: List[str]) -> go.Figure:
    """Visualisasi C: Perbandingan Penjualan Antar-Game (Compare Game Sales - Regional Breakdown)."""
    if df.empty or not selected_titles:
        fig = go.Figure()
        fig.add_annotation(
            text="Pilih minimal satu judul game pada dropdown di atas untuk membandingkan penjualan regional.",
            showarrow=False,
            font=dict(size=13, color=COLOR_TEXT_MUTED),
        )
        fig.update_layout(
            template="plotly_white",
            height=380,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    # Cocokkan pilihan berdasarkan Game_Identifier atau Nama Game
    comp_df = df[df["Game_Identifier"].isin(selected_titles)].copy()
    if comp_df.empty:
        comp_df = df[df["Name"].isin(selected_titles)].copy()

    # Batasi maksimal 10 game agar grafik tetap bersih dan mudah dibaca
    comp_df = comp_df.head(10).iloc[::-1]

    y_labels = comp_df["Game_Identifier"].tolist()

    fig = go.Figure()

    region_colors = {
        "NA_Sales": ("North America", "#2563EB"),
        "EU_Sales": ("Europe", "#059669"),
        "JP_Sales": ("Japan", "#D97706"),
        "Other_Sales": ("Other Regions", "#7C3AED"),
    }

    # Pre-format total global sales
    global_sales_formatted = [fmt_sales(v) for v in comp_df["Global_Sales"]]

    for col, (reg_name, reg_color) in region_colors.items():
        reg_formatted = [fmt_sales(v) for v in comp_df[col]]
        custom = list(
            zip(
                comp_df["Name"],
                comp_df["Platform"],
                comp_df["Genre"],
                reg_formatted,
                global_sales_formatted,
            )
        )

        fig.add_trace(
            go.Bar(
                name=reg_name,
                y=y_labels,
                x=comp_df[col],
                orientation="h",
                marker=dict(color=reg_color),
                customdata=custom,
                hovertemplate=(
                    f"<b>%{{customdata[0]}}</b> (%{{customdata[1]}})<br>"
                    f"Wilayah: <b>{reg_name}</b><br>"
                    "Penjualan Wilayah: <b>%{customdata[3]}</b><br>"
                    "Total Penjualan Global: <b>%{customdata[4]}</b>"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="stack",
        template="plotly_white",
        height=380,
        margin=dict(l=10, r=20, t=25, b=25),
        font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY),
        hoverlabel=dict(bgcolor=COLOR_TEXT_PRIMARY, font_size=12, font_color="#FFFFFF"),
        xaxis=dict(
            title=dict(text="Total Penjualan Regional (Juta Unit)", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(size=11, color=COLOR_TEXT_PRIMARY),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
    )
    return fig


def create_sales_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Chart B: Global Sales Trend over Release Years dengan info game terlaris per tahun."""
    valid_years = df.dropna(subset=["Year"]).copy()
    if valid_years.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Tidak ada data tahun rilis yang valid untuk membentuk tren.",
            showarrow=False,
            font=dict(size=13, color=COLOR_TEXT_MUTED),
        )
        fig.update_layout(
            template="plotly_white",
            height=370,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=20, r=20, t=30, b=30),
        )
        return fig

    # Hitung game terlaris di setiap tahun
    top_per_year = {}
    for year, group in valid_years.groupby("Year"):
        top_row = group.loc[group["Global_Sales"].idxmax()]
        top_per_year[int(year)] = (str(top_row["Name"]), float(top_row["Global_Sales"]))

    yearly = (
        valid_years.groupby("Year", as_index=False)
        .agg(Global_Sales=("Global_Sales", "sum"), Game_Records=("Name", "size"))
        .sort_values("Year")
    )

    formatted_sales = [fmt_sales(v) for v in yearly["Global_Sales"]]
    formatted_records = [fmt_int(v) for v in yearly["Game_Records"]]
    top_game_names = [top_per_year.get(int(y), ("-", 0.0))[0] for y in yearly["Year"]]
    top_game_sales_fmt = [fmt_sales(top_per_year.get(int(y), ("-", 0.0))[1]) for y in yearly["Year"]]

    customdata = list(
        zip(
            formatted_records,
            formatted_sales,
            top_game_names,
            top_game_sales_fmt,
        )
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly["Year"],
            y=yearly["Global_Sales"],
            mode="lines+markers",
            name="Global Sales",
            line=dict(color=COLOR_PRIMARY, width=2.5, shape="spline", smoothing=0.3),
            marker=dict(size=6, color=COLOR_PRIMARY, line=dict(color="#FFFFFF", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.08)",
            customdata=customdata,
            hovertemplate=(
                "<b>Tahun %{x}</b><br>"
                "Total Penjualan: <b>%{customdata[1]}</b><br>"
                "Jumlah Rilis Gim: <b>%{customdata[0]}</b> judul<br>"
                "Gim Terlaris Era Ini: <b>%{customdata[2]}</b> (%{customdata[3]})"
                "<extra></extra>"
            ),
        )
    )

    year_span = yearly["Year"].max() - yearly["Year"].min()
    dtick_val = 5 if year_span > 15 else 1

    fig.update_layout(
        template="plotly_white",
        height=370,
        margin=dict(l=10, r=20, t=25, b=25),
        font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY),
        hoverlabel=dict(bgcolor=COLOR_TEXT_PRIMARY, font_size=12, font_color="#FFFFFF"),
        xaxis=dict(
            title=dict(text="Tahun Rilis", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=False,
            linecolor=COLOR_BORDER,
            tickmode="auto",
            dtick=dtick_val,
        ),
        yaxis=dict(
            title=dict(text="Penjualan Global (Juta Unit)", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor=COLOR_BORDER,
            zeroline=True,
            zerolinecolor=COLOR_BORDER,
        ),
        showlegend=False,
    )
    return fig


def create_genre_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Chart 2: Global Sales by Genre (Horizontal Bar Chart)."""
    genre_sales = (
        df.groupby("Genre", as_index=False)["Global_Sales"]
        .sum()
        .sort_values("Global_Sales", ascending=True)  # Ascending so highest is at top
    )

    if genre_sales.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Tidak ada data genre yang cocok.",
            showarrow=False,
            font=dict(size=13, color=COLOR_TEXT_MUTED),
        )
        fig.update_layout(template="plotly_white", height=370)
        return fig

    total_sales = genre_sales["Global_Sales"].sum()
    genre_sales["Share"] = (genre_sales["Global_Sales"] / total_sales * 100.0) if total_sales > 0 else 0.0

    bar_texts = [f"{fmt_number(v, 1)} juta unit" for v in genre_sales["Global_Sales"]]
    formatted_sales = [fmt_sales(v) for v in genre_sales["Global_Sales"]]
    formatted_share = [fmt_percent(v) for v in genre_sales["Share"]]

    customdata = list(zip(formatted_sales, formatted_share))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=genre_sales["Global_Sales"],
            y=genre_sales["Genre"],
            orientation="h",
            marker=dict(
                color=COLOR_PRIMARY,
                line=dict(color=COLOR_PRIMARY_DARK, width=1),
            ),
            text=bar_texts,
            textposition="auto",
            textfont=dict(size=11, color="#FFFFFF"),
            customdata=customdata,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Penjualan Global: <b>%{customdata[0]}</b><br>"
                "Pangsa Pasar: <b>%{customdata[1]}</b>"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=370,
        margin=dict(l=10, r=30, t=25, b=25),
        font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY),
        hoverlabel=dict(bgcolor=COLOR_TEXT_PRIMARY, font_size=12, font_color="#FFFFFF"),
        xaxis=dict(
            title=dict(text="Penjualan Global (Juta Unit)", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(size=12, color=COLOR_TEXT_PRIMARY),
        ),
        showlegend=False,
    )
    return fig


def create_regional_heatmap(df: pd.DataFrame) -> go.Figure:
    """Chart 3: Regional Sales Comparison by Genre (Heatmap)."""
    regional = df.groupby("Genre", as_index=False)[REGION_COLUMNS].sum()
    if regional.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Data regional tidak tersedia untuk kombinasi filter ini.",
            showarrow=False,
            font=dict(size=13, color=COLOR_TEXT_MUTED),
        )
        fig.update_layout(template="plotly_white", height=390)
        return fig

    # Sort genres by total regional sales for logical visual hierarchy
    regional["Total"] = regional[REGION_COLUMNS].sum(axis=1)
    regional = regional.sort_values("Total", ascending=True)

    heat_data = regional.set_index("Genre")[REGION_COLUMNS]
    heat_data.columns = [REGION_LABELS[c] for c in heat_data.columns]

    # Pre-format cell texts and tooltips
    cell_texts = [[fmt_number(val, 1) for val in row] for row in heat_data.values]
    customdata = [[fmt_sales(val) for val in row] for row in heat_data.values]

    # Harmonious sequential blue scale matching design system
    colorscale = [
        [0.0, "#F8FAFC"],
        [0.2, "#DBEAFE"],
        [0.5, "#60A5FA"],
        [0.8, "#2563EB"],
        [1.0, "#1E40AF"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=heat_data.values,
            x=list(heat_data.columns),
            y=list(heat_data.index),
            colorscale=colorscale,
            text=cell_texts,
            customdata=customdata,
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate=(
                "<b>%{y}</b> — <b>%{x}</b><br>"
                "Penjualan: <b>%{customdata}</b>"
                "<extra></extra>"
            ),
            colorbar=dict(
                title=dict(text="Juta Unit", font=dict(size=11, color=COLOR_TEXT_MUTED)),
                thickness=12,
                len=0.9,
                tickfont=dict(size=10, color=COLOR_TEXT_MUTED),
            ),
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=390,
        margin=dict(l=10, r=20, t=25, b=25),
        font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY),
        hoverlabel=dict(bgcolor=COLOR_TEXT_PRIMARY, font_size=12, font_color="#FFFFFF"),
        xaxis=dict(
            title=None,
            tickfont=dict(size=12, color=COLOR_TEXT_PRIMARY, weight=600),
            side="bottom",
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=12, color=COLOR_TEXT_PRIMARY),
        ),
    )
    return fig


def create_na_vs_eu_scatter(df: pd.DataFrame, highlight_titles: Optional[List[str]] = None) -> go.Figure:
    """Chart 4: North America vs Europe Sales Comparison (Scatter Plot dengan penyorotan game pilihan)."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Tidak ada data untuk scatter plot.",
            showarrow=False,
            font=dict(size=13, color=COLOR_TEXT_MUTED),
        )
        fig.update_layout(template="plotly_white", height=390)
        return fig

    scatter_df = df.copy()
    scatter_df["NA_Fmt"] = [fmt_sales(v) for v in scatter_df["NA_Sales"]]
    scatter_df["EU_Fmt"] = [fmt_sales(v) for v in scatter_df["EU_Sales"]]
    scatter_df["Global_Fmt"] = [fmt_sales(v) for v in scatter_df["Global_Sales"]]

    # Plotly express scatter dengan automatic WebGL rendering engine
    fig = px.scatter(
        scatter_df,
        x="NA_Sales",
        y="EU_Sales",
        color="Genre",
        color_discrete_map=GENRE_PALETTE,
        hover_name="Name",
        custom_data=["Platform", "Release year", "NA_Fmt", "EU_Fmt", "Global_Fmt"],
        render_mode="auto",
        template="plotly_white",
        opacity=0.7,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Platform: <b>%{customdata[0]}</b> | Tahun Rilis: <b>%{customdata[1]}</b><br>"
            "Penjualan NA: <b>%{customdata[2]}</b><br>"
            "Penjualan EU: <b>%{customdata[3]}</b><br>"
            "Penjualan Global: <b>%{customdata[4]}</b>"
            "<extra></extra>"
        ),
        marker=dict(size=7, line=dict(width=0.5, color="#FFFFFF")),
        selector=dict(mode="markers"),
    )

    # Garis diagonal paritas pasar (NA == EU)
    max_val = max(df["NA_Sales"].max(), df["EU_Sales"].max())
    if max_val > 0:
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode="lines",
                name="Paritas (NA = EU)",
                line=dict(color="#CBD5E1", width=1.5, dash="dash"),
                hoverinfo="skip",
                showlegend=True,
            )
        )

    # Penyorotan interaktif jika ada game yang dipilih atau dicari
    if highlight_titles:
        hl_df = scatter_df[
            scatter_df["Game_Identifier"].isin(highlight_titles)
            | scatter_df["Name"].isin(highlight_titles)
        ].copy()
        if not hl_df.empty:
            custom_hl = list(
                zip(
                    hl_df["Platform"],
                    hl_df["Release year"],
                    hl_df["NA_Fmt"],
                    hl_df["EU_Fmt"],
                    hl_df["Global_Fmt"],
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=hl_df["NA_Sales"],
                    y=hl_df["EU_Sales"],
                    mode="markers+text",
                    name="Game Pilihan/Disorot",
                    text=hl_df["Name"],
                    textposition="top center",
                    textfont=dict(size=10, color=COLOR_TEXT_PRIMARY, weight=600),
                    marker=dict(
                        size=13,
                        symbol="diamond",
                        color="#D97706",
                        line=dict(color="#0F172A", width=2),
                    ),
                    customdata=custom_hl,
                    hovertemplate=(
                        "⭐ <b>%{text}</b> (%{customdata[0]})<br>"
                        "Tahun Rilis: %{customdata[1]} | Global: %{customdata[4]}<br>"
                        "NA: %{customdata[2]} | EU: %{customdata[3]}"
                        "<extra></extra>"
                    ),
                )
            )

    fig.update_layout(
        template="plotly_white",
        height=390,
        margin=dict(l=10, r=20, t=25, b=25),
        font=dict(family="Inter, -apple-system, sans-serif", color=COLOR_TEXT_PRIMARY),
        hoverlabel=dict(bgcolor=COLOR_TEXT_PRIMARY, font_size=12, font_color="#FFFFFF"),
        xaxis=dict(
            title=dict(text="Penjualan North America (Juta Unit)", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor=COLOR_BORDER,
        ),
        yaxis=dict(
            title=dict(text="Penjualan Europe (Juta Unit)", font=dict(size=12, color=COLOR_TEXT_MUTED)),
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor=COLOR_BORDER,
        ),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=COLOR_TEXT_MUTED),
        ),
    )
    return fig


# ==============================================================================
# 8. UI SECTIONS RENDERING
# ==============================================================================
def render_header(total_catalog_records: int, min_year: int, max_year: int):
    """Render the top Modern Editorial Hero Header banner."""
    render_html(
        f"""
        <div class="hero-container">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 14px;">
                <div>
                    <div class="hero-badge">🎮 GameScope Intelligence</div>
                    <h1 class="hero-title">Global Video Game Sales Analytics</h1>
                    <p class="hero-subtitle">
                        Eksplorasi mendalam performa video game global historis lintas judul game terlaris, 
                        konsol hardware, genre, dan dinamika pasar regional utama.
                    </p>
                </div>
                <div style="text-align: right; min-width: 170px;">
                    <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #64748B; font-weight: 700;">STATUS DATASET</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #15803D; margin-top: 2px;">● Terverifikasi Aktif</div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">Kaggle / Gregory Smith</div>
                </div>
            </div>
            <div class="hero-meta-bar">
                <span class="hero-meta-pill">📁 <b>{fmt_int(total_catalog_records)}</b> Judul Terindeks</span>
                <span class="hero-meta-pill">📅 Periode Rilis <b>{min_year}–{max_year}</b></span>
                <span class="hero-meta-pill">🌐 <b>4</b> Wilayah Analisis (NA, EU, JP, Other)</span>
                <span class="hero-meta-pill">📐 Satuan Ukur: <b>Juta Unit (Kopi Terjual)</b></span>
            </div>
        </div>
        """
    )


def render_filter_summary(
    year_range: Optional[Tuple[int, int]],
    selected_genres: List[str],
    all_genres: List[str],
    selected_platforms: List[str],
    all_platforms: List[str],
    search_query: str,
    filtered_count: int,
    total_count: int,
):
    """Render the active filter summary bar including game search query status."""
    pct = (filtered_count / total_count * 100.0) if total_count > 0 else 0.0
    year_str = f"{year_range[0]}–{year_range[1]}" if year_range else "Semua"

    search_chip = (
        f'<span class="filter-summary-chip">🔍 Cari: <b>"{search_query}"</b></span>'
        if search_query.strip()
        else ""
    )

    render_html(
        f"""
        <div class="filter-summary-bar">
            <span class="filter-summary-label">FILTER AKTIF:</span>
            {search_chip}
            <span class="filter-summary-chip">📅 Tahun: <b>{year_str}</b></span>
            <span class="filter-summary-chip">🎮 Genre: <b>{fmt_int(len(selected_genres))}/{fmt_int(len(all_genres))}</b></span>
            <span class="filter-summary-chip">🕹️ Platform: <b>{fmt_int(len(selected_platforms))}/{fmt_int(len(all_platforms))}</b></span>
            <span class="filter-summary-chip">📊 Hasil: <b>{fmt_int(filtered_count)}</b> ({fmt_percent(pct)})</span>
        </div>
        """
    )


def render_kpi_cards(kpis: Dict[str, Any]):
    """Render the 4 mandatory KPI summary cards with prominent best-selling game title."""
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            label="TOTAL PENJUALAN GLOBAL (JUTA UNIT)",
            value=f"{fmt_number(kpis['total_sales'])} juta unit",
            help=f"Total volume penjualan global: {fmt_sales(kpis['total_sales'])} pada data aktif.",
        )
        st.caption("Juta unit di seluruh wilayah")

    with k2:
        st.metric(
            label="JUMLAH GAME RECORDS",
            value=fmt_int(kpis["game_records"]),
            help=f"Jumlah baris judul gim yang memenuhi seluruh kriteria filter aktif: {fmt_int(kpis['game_records'])}.",
        )
        st.caption("Judul unik terindeks")

    with k3:
        top_title = kpis.get("top_game_name", "N/A")
        short_title = (top_title[:18] + "…") if len(top_title) > 20 else top_title
        st.metric(
            label="GAME TERLARIS",
            value=short_title,
            help=(
                f"Judul game terlaris: {top_title}\n"
                f"Platform: {kpis.get('top_game_platform', 'N/A')}\n"
                f"Tahun: {kpis.get('top_game_year', 'N/A')}\n"
                f"Penjualan Global: {fmt_sales(kpis.get('top_game_sales', 0.0))}"
            ),
        )
        st.caption(f"{fmt_sales(kpis.get('top_game_sales', 0.0))} ({kpis.get('top_game_platform', '-')})")

    with k4:
        st.metric(
            label="GENRE TERLARIS",
            value=kpis["top_genre"],
            help=(
                f"Genre terlaris: {kpis['top_genre']} "
                f"({fmt_sales(kpis['top_genre_sales'])} / {fmt_percent(kpis['top_genre_share'])} pangsa volume aktif)."
            ),
        )
        st.caption(f"{fmt_sales(kpis['top_genre_sales'])} ({fmt_percent(kpis['top_genre_share'])})")


def render_insight_cards(insights: List[Dict[str, str]]):
    """Render dynamic analytical insight cards in a structured responsive CSS Grid with 100% equal uniform height."""
    if not insights:
        return

    cards_html = []
    for ins in insights:
        card = (
            f'<div class="insight-card">'
            f'<div class="insight-badge">{ins["badge"]}</div>'
            f'<div class="insight-value">{ins["title"]}</div>'
            f'<p class="insight-desc">{ins["description"]}</p>'
            f'</div>'
        )
        cards_html.append(card)

    all_cards = "".join(cards_html)
    grid_html = f'<div class="insight-grid">{all_cards}</div>'
    render_html(grid_html)


# ==============================================================================
# 9. MAIN APPLICATION CONTROLLER
# ==============================================================================
def main():
    # 1. Dataset Resolution & Guard
    data_path = get_dataset_path()
    if data_path is None:
        st.warning("⚠️ Dataset belum ditemukan. Unduh CSV resmi lalu simpan sebagai `dataset/vgsales.csv`.")
        st.markdown(
            """
            **Panduan Singkat Penyiapan Data:**
            1. Unduh dataset resmi dari [Kaggle — Video Game Sales](https://www.kaggle.com/datasets/gregorut/videogamesales).
            2. Simpan file sebagai `dataset/vgsales.csv` pada direktori proyek ini.
            3. Jalankan skrip pembersihan opsional: `python scripts/clean_data.py`.
            4. Refresh atau jalankan ulang dashboard Streamlit.
            
            *Dashboard GameScope mengedepankan integritas data dan tidak menampilkan angka contoh tiruan sebelum dataset valid dimuat.*
            """
        )
        st.stop()

    try:
        df = load_data(str(data_path))
    except Exception as exc:
        st.error(f"❌ Dataset tidak dapat dimuat: {exc}")
        st.info("Pastikan file CSV memiliki kolom yang sesuai dengan spesifikasi di README.md.")
        st.stop()

    if df.empty:
        st.error("❌ Dataset kosong setelah validasi data. Periksa isi file CSV.")
        st.stop()

    # 2. Filter Bounds Initialization
    years_series = df["Year"].dropna()
    min_year = int(years_series.min()) if not years_series.empty else 1980
    max_year = int(years_series.max()) if not years_series.empty else 2020
    all_genres = sorted(df["Genre"].dropna().astype(str).unique().tolist())
    all_platforms = sorted(df["Platform"].dropna().astype(str).unique().tolist())

    # Session State Initialization for Predictable Reset Behavior
    if "filter_search" not in st.session_state:
        st.session_state["filter_search"] = ""
    if "filter_year" not in st.session_state:
        st.session_state["filter_year"] = (min_year, max_year)
    if "filter_genres" not in st.session_state:
        st.session_state["filter_genres"] = list(all_genres)
    if "filter_platforms" not in st.session_state:
        st.session_state["filter_platforms"] = list(all_platforms)
    if "compare_selected" not in st.session_state:
        st.session_state["compare_selected"] = []

    def reset_filters_callback():
        st.session_state["filter_search"] = ""
        st.session_state["filter_year"] = (min_year, max_year)
        st.session_state["filter_genres"] = list(all_genres)
        st.session_state["filter_platforms"] = list(all_platforms)
        st.session_state["compare_selected"] = []

    # 3. Sidebar Filter Panel
    with st.sidebar:
        render_html(
            """
            <div style="padding-bottom: 12px; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A; display: flex; align-items: center; gap: 8px;">
                    <span>🎮</span> GameScope
                </div>
                <div style="font-size: 0.8rem; color: #64748B; margin-top: 2px;">
                    Panel Kontrol Filter Analitik
                </div>
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed #E2E8F0; font-size: 0.78rem; color: #64748B;">
                    <div style="font-size: 0.7rem; letter-spacing: 0.05em; text-transform: uppercase;">Disusun oleh</div>
                    <div style="margin-top: 2px; color: #0F172A; font-weight: 700;">Arwan Priyadinata</div>
                    <div style="margin-top: 2px;">NIM/NPM: <b style="color: #0F172A;">241041005</b></div>
                </div>
            </div>
            """
        )

        # Quick Reset Button
        st.button(
            "↺ Reset Filter ke Default",
            on_click=reset_filters_callback,
            use_container_width=True,
            help="Kembalikan semua filter pencarian, tahun, genre, dan platform ke kondisi awal penuh.",
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # A. Game Search Input
        search_query = st.text_input(
            "🔍 Cari Judul Game / Publisher",
            key="filter_search",
            placeholder="Contoh: Mario, Pokemon, Wii...",
            help="Filter data secara langsung berdasarkan nama game atau publisher.",
        )

        # B. Year Range Slider
        if not years_series.empty:
            year_range = st.slider(
                "1. Rentang Tahun Rilis",
                min_value=min_year,
                max_value=max_year,
                key="filter_year",
                help="Filter judul gim berdasarkan rentang tahun peluncuran resmi.",
            )
            st.caption("Catatan: Judul tanpa tahun rilis tetap diikutsertakan pada metrik agregat.")
        else:
            year_range = None
            st.caption("Tidak ada nilai tahun valid; filter tahun dinonaktifkan.")

        # C. Genre Multiselect
        selected_genres = st.multiselect(
            "2. Kategori Genre",
            options=all_genres,
            key="filter_genres",
            help="Pilih satu atau lebih genre video game untuk dianalisis.",
        )

        # D. Platform Multiselect
        selected_platforms = st.multiselect(
            "3. Platform Hardware",
            options=all_platforms,
            key="filter_platforms",
            help="Pilih satu atau lebih platform konsol/PC.",
        )

        st.divider()

        # Metadata Box in Sidebar
        st.markdown(
            f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; font-size: 0.78rem; color: #64748B;">
            <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">Informasi Sumber Dataset</div>
            <div>Berkas: <code>{data_path.name}</code></div>
            <div style="margin-top: 4px;">Total Katalog: <b>{fmt_int(len(df))}</b> baris</div>
            <div style="margin-top: 4px;">Satuan: <b>Juta Unit Terjual</b></div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 4. Filter Processing
    filtered = apply_filters(df, year_range, selected_genres, selected_platforms, search_query)

    # 5. Header Rendering
    render_header(len(df), min_year, max_year)

    # 6. Active Filter Summary
    render_filter_summary(
        year_range,
        selected_genres,
        all_genres,
        selected_platforms,
        all_platforms,
        search_query,
        len(filtered),
        len(df),
    )

    # 7. Empty State Handling with Quick Action
    if filtered.empty:
        render_html(
            """
            <div class="empty-state-card">
                <div style="font-size: 2.2rem;">🔍</div>
                <div class="empty-state-title">Tidak Ada Data yang Cocok</div>
                <div class="empty-state-desc">
                    Kombinasi pencarian, rentang tahun, pilihan genre, atau platform saat ini menghasilkan 0 baris catatan.
                    Silakan sesuaikan kata kunci pencarian atau gunakan tombol di bawah untuk mereset seluruh filter.
                </div>
            </div>
            """
        )
        btn_col = st.columns([1, 2, 1])[1]
        with btn_col:
            st.button(
                "↺ Reset Filter ke Semula",
                key="btn_reset_empty",
                on_click=reset_filters_callback,
                use_container_width=True,
            )
        st.stop()

    # 8. KPI Summary Section
    kpis = calculate_kpis(filtered)
    render_kpi_cards(kpis)

    render_html('<hr class="section-divider">')

    # 9. SECTION 1 — GAME-LEVEL ANALYSIS (TOP BEST-SELLERS & COMPARISON)
    render_html(
        """
        <div class="section-header-box">
            <div class="section-tag">Section 1 — Game-Level Analysis</div>
            <h2 class="section-title">Visualisasi Penjualan Berbasis Nama Game</h2>
            <p class="section-subtitle">Daftar game dengan penjualan global tertinggi serta perbandingan volume antar-game pilihan pengguna.</p>
        </div>
        """
    )

    col_top_games, col_comp_games = st.columns((1.1, 1.0))

    with col_top_games:
        st.markdown("**Top 10 Best-Selling Video Games**")
        st.caption("Peringkat dihitung berdasarkan nilai penjualan global dari data yang sedang aktif.")
        fig_top10 = create_top10_games_chart(filtered)
        st.plotly_chart(fig_top10, use_container_width=True)

    with col_comp_games:
        st.markdown("**Compare Game Sales**")
        st.caption("Bandingkan volume dan proporsi penjualan regional antar-game (maksimal 10 judul).")
        
        # Pilihan judul game yang tersedia pada filtered data
        available_game_ids = filtered["Game_Identifier"].dropna().unique().tolist()
        
        # Default pilihan awal: 3 game teratas pada filtered data
        top_defaults = filtered.nlargest(3, "Global_Sales")["Game_Identifier"].dropna().tolist()
        
        # Multiselect game selector
        selected_compare = st.multiselect(
            "Pilih Judul Game untuk Dibandingkan:",
            options=available_game_ids,
            default=top_defaults[:3],
            max_selections=10,
            key="compare_game_select",
            help="Pilih hingga 10 game untuk membandingkan penjualan regional (NA, EU, JP, Other).",
        )
        
        fig_comp = create_game_comparison_chart(filtered, selected_compare)
        st.plotly_chart(fig_comp, use_container_width=True)

    render_html('<hr class="section-divider">')

    # 10. SECTION 2 — MACRO TRENDS & GENRE BREAKDOWN
    render_html(
        """
        <div class="section-header-box">
            <div class="section-tag">Section 2 — Macro Trends & Genre Performance</div>
            <h2 class="section-title">Kinerja & Tren Penjualan Global</h2>
            <p class="section-subtitle">Trajektori volume historis per tahun dan komparasi performa lintas kategori genre.</p>
        </div>
        """
    )

    col_trend, col_genre = st.columns((1.15, 1.0))
    with col_trend:
        st.markdown("**Global Sales Trend over Release Years**")
        fig_trend = create_sales_trend_chart(filtered)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_genre:
        st.markdown("**Sales by Genre**")
        fig_genre = create_genre_bar_chart(filtered)
        st.plotly_chart(fig_genre, use_container_width=True)

    render_html('<hr class="section-divider">')

    # 11. SECTION 3 — REGIONAL ANALYSIS & SCATTER PLOT
    render_html(
        """
        <div class="section-header-box">
            <div class="section-tag">Section 3 — Regional Analysis & Cross-Market Correlation</div>
            <h2 class="section-title">Dinamika Pasar Regional & Komparasi Geografis</h2>
            <p class="section-subtitle">Peta preferensi regional per genre serta korelasi penjualan antara Amerika Utara dan Eropa.</p>
        </div>
        """
    )

    col_heat, col_scatter = st.columns((1.0, 1.0))
    with col_heat:
        st.markdown("**Regional Sales by Genre**")
        fig_heat = create_regional_heatmap(filtered)
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_scatter:
        st.markdown("**North America vs Europe Sales (Game Level)**")
        # Berikan highlight pada scatter jika ada game yang dipilih pada compare tool
        fig_scatter = create_na_vs_eu_scatter(filtered, highlight_titles=selected_compare)
        st.plotly_chart(fig_scatter, use_container_width=True)

    render_html('<hr class="section-divider">')

    # 12. KEY INSIGHTS & ANALYTICAL STORYTELLING
    render_html(
        """
        <div class="section-header-box">
            <div class="section-tag">Analytical Storytelling</div>
            <h2 class="section-title">Key Insights — What the Data Reveals</h2>
            <p class="section-subtitle">Temuan analitik utama yang dihitung secara dinamis dari subset data yang sedang aktif.</p>
        </div>
        """
    )

    insights = generate_dynamic_insights(filtered)
    render_insight_cards(insights)

    st.caption(
        "ℹ️ *Catatan Metodologi: Seluruh interpretasi dihitung secara langsung dari data aktif. "
        "Korelasi atau divergensi visual pada grafik tidak dengan sendirinya membuktikan hubungan sebab-akibat.*"
    )

    render_html('<hr class="section-divider">')

    # 13. DATA EXPLORER & CSV EXPORT
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    with st.expander("🔍 Jelajahi Data Mentah & Tabel Terfilter", expanded=False):
        col_exp_info, col_exp_btn = st.columns([3, 1])
        with col_exp_info:
            st.markdown(
                f"Menampilkan **{fmt_int(len(filtered))}** baris gim video yang memenuhi kriteria filter aktif "
                f"(Total volume: **{fmt_sales(filtered['Global_Sales'].sum())}**)."
            )
        with col_exp_btn:
            csv_data = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Unduh Data Terfilter (CSV)",
                data=csv_data,
                file_name="gamescope_filtered_data.csv",
                mime="text/csv",
                use_container_width=True,
                help="Unduh subset data hasil filter saat ini dalam format CSV.",
            )

        # Formatted dataframe view with Streamlit column_config
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
                "Name": st.column_config.TextColumn("Nama Game"),
                "Platform": st.column_config.TextColumn("Platform"),
                "Year": st.column_config.NumberColumn("Tahun Rilis", format="%d"),
                "Genre": st.column_config.TextColumn("Genre"),
                "Publisher": st.column_config.TextColumn("Publisher"),
                "NA_Sales": st.column_config.NumberColumn("NA Sales (Juta Unit)", format="%.2f"),
                "EU_Sales": st.column_config.NumberColumn("EU Sales (Juta Unit)", format="%.2f"),
                "JP_Sales": st.column_config.NumberColumn("JP Sales (Juta Unit)", format="%.2f"),
                "Other_Sales": st.column_config.NumberColumn("Other Sales (Juta Unit)", format="%.2f"),
                "Global_Sales": st.column_config.NumberColumn("Global Sales (Juta Unit)", format="%.2f"),
                "Release year": None,
                "Game_Identifier": None,
            },
        )

    # 14. PROFESSIONAL EDITORIAL FOOTER
    render_html(
        """
        <div style="margin-top: 48px; padding-top: 24px; border-top: 1px solid #E2E8F0; text-align: center; color: #64748B; font-size: 0.82rem; line-height: 1.6;">
            <div><b>GameScope — Global Video Game Sales Analytics</b> · Proyek Visualisasi Data UTS</div>
            <div>Sumber Dataset: Kaggle (Gregory Smith) · Metrik volume penjualan dinyatakan dalam <i>juta unit</i> (juta unit kopi terjual).</div>
            <div style="margin-top: 4px; color: #94A3B8; font-size: 0.76rem;">Dirancang dengan Modern Editorial Analytics System · Data Integrity & Visual Accessibility Standards</div>
        </div>
        """
    )


if __name__ == "__main__":
    main()
