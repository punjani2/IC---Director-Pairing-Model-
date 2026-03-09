import streamlit as st
import pandas as pd

EXCEL_FILE = "Anushil_Organization_Skip_Level_Pairings_v4.xlsx"

st.set_page_config(
    page_title="Cross-functional Skip-Level Meeting Pairings",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 45%, #f7f4ff 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

.main-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #1f2a44;
    margin-bottom: 0.2rem;
}

.sub-title {
    font-size: 1rem;
    color: #5b6475;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: linear-gradient(180deg, #ffffff 0%, #f6f9ff 100%);
    border: 1px solid rgba(98, 118, 255, 0.14);
    border-radius: 16px;
    padding: 0.9rem 1rem;
    box-shadow: 0 6px 16px rgba(31, 42, 68, 0.05);
}

.metric-label {
    font-size: 0.9rem;
    color: #667085;
    margin-bottom: 0.35rem;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1f2a44;
}

div[data-testid="stRadio"] > div {
    background: rgba(255,255,255,0.72);
    padding: 0.65rem 0.9rem;
    border-radius: 14px;
    border: 1px solid rgba(120, 140, 180, 0.18);
}

div[data-testid="stTextInput"] > div > div input {
    background-color: white;
    border-radius: 12px;
}

div[data-testid="stDataEditor"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(120, 140, 180, 0.18);
}

.stDownloadButton button {
    border-radius: 10px;
    font-weight: 600;
}

hr {
    margin-top: 1rem;
    margin-bottom: 1rem;
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(100,100,140,0.35), transparent);
}
</style>
""", unsafe_allow_html=True)

df_11 = pd.read_excel(EXCEL_FILE, sheet_name="Q1 1-1 Allowed Dir Only")
df_12 = pd.read_excel(EXCEL_FILE, sheet_name="Q1 1-2 Allowed Dir Only")

REMOVE_PATTERNS = [
    "full stack developer intern",
    "sales product line intern",
    "unfilled",
]

def should_remove(series: pd.Series) -> pd.Series:
    mask = pd.Series(False, index=series.index)
    for pattern in REMOVE_PATTERNS:
        mask = mask | series.astype(str).str.contains(pattern, case=False, na=False)
    return mask

df_11 = df_11[
    ~should_remove(df_11["IC Name"])
].copy()

df_12 = df_12[
    ~should_remove(df_12["IC1 Name"])
    & ~should_remove(df_12["IC2 Name"])
].copy()

df_11["IC Team"] = df_11["IC Team"].fillna("").astype(str).str.strip()
df_11.loc[df_11["IC Team"] == "", "IC Team"] = df_11["IC Title"]

for prefix in ["IC1", "IC2"]:
    df_12[f"{prefix} Team"] = df_12[f"{prefix} Team"].fillna("").astype(str).str.strip()
    df_12.loc[df_12[f"{prefix} Team"] == "", f"{prefix} Team"] = df_12[f"{prefix} Title"]

if "comments_11" not in st.session_state:
    st.session_state["comments_11"] = {}

if "status_11" not in st.session_state:
    st.session_state["status_11"] = {}

if "comments_12" not in st.session_state:
    st.session_state["comments_12"] = {}

if "status_12" not in st.session_state:
    st.session_state["status_12"] = {}

STATUS_OPTIONS = ["", "Scheduled", "Done", "Cancelled"]

st.markdown('<div class="main-title">Cross-functional Skip-Level Meeting Pairings</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Search by IC or Director, track meeting progress, and add comments in one place.</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 2])
with col1:
    model = st.radio(
        "Select Model",
        ["1:1 Model", "1:2 Model"],
        horizontal=True
    )

with col2:
    name = st.text_input("Enter employee name (IC or Director)")

st.markdown("---")

def add_edit_columns_11(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    results["row_key"] = (
        results["Director Name"].astype(str) + " | "
        + results["IC Name"].astype(str)
    )
    results["Comments"] = results["row_key"].map(st.session_state["comments_11"]).fillna("")
    results["Status"] = results["row_key"].map(st.session_state["status_11"]).fillna("")
    return results

def add_edit_columns_12(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()
    results["row_key"] = (
        results["Director Name"].astype(str) + " | "
        + results["IC1 Name"].astype(str) + " | "
        + results["IC2 Name"].astype(str)
    )
    results["Comments"] = results["row_key"].map(st.session_state["comments_12"]).fillna("")
    results["Status"] = results["row_key"].map(st.session_state["status_12"]).fillna("")
    return results

def metric_box(label: str, value: int):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_progress_dashboard_11():
    base = df_11.copy()
    base["row_key"] = (
        base["Director Name"].astype(str) + " | "
        + base["IC Name"].astype(str)
    )
    statuses = base["row_key"].map(st.session_state["status_11"]).fillna("")

    total = len(base)
    scheduled = (statuses == "Scheduled").sum()
    done = (statuses == "Done").sum()
    cancelled = (statuses == "Cancelled").sum()
    blank = (statuses == "").sum()

    st.subheader("Progress Dashboard")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_box("Total Meetings", total)
    with c2:
        metric_box("Scheduled", int(scheduled))
    with c3:
        metric_box("Done", int(done))
    with c4:
        metric_box("Cancelled", int(cancelled))
    with c5:
        metric_box("Blank", int(blank))

def show_progress_dashboard_12():
    base = df_12.copy()
    base["row_key"] = (
        base["Director Name"].astype(str) + " | "
        + base["IC1 Name"].astype(str) + " | "
        + base["IC2 Name"].astype(str)
    )
    statuses = base["row_key"].map(st.session_state["status_12"]).fillna("")

    total = len(base)
    scheduled = (statuses == "Scheduled").sum()
    done = (statuses == "Done").sum()
    cancelled = (statuses == "Cancelled").sum()
    blank = (statuses == "").sum()

    st.subheader("Progress Dashboard")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_box("Total Meetings", total)
    with c2:
        metric_box("Scheduled", int(scheduled))
    with c3:
        metric_box("Done", int(done))
    with c4:
        metric_box("Cancelled", int(cancelled))
    with c5:
        metric_box("Blank", int(blank))

if model == "1:1 Model":
    show_progress_dashboard_11()
else:
    show_progress_dashboard_12()

st.markdown("---")
st.subheader("Pairing Results")

if name:
    if model == "1:1 Model":
        results = df_11[
            df_11["IC Name"].astype(str).str.contains(name, case=False, na=False)
            | df_11["Director Name"].astype(str).str.contains(name, case=False, na=False)
        ].copy()

        if results.empty:
            st.warning("No matching mapping found.")
        else:
            results = add_edit_columns_11(results)

            display_cols = [
                "Director Name",
                "Director Title",
                "Director Team",
                "IC Name",
                "IC Title",
                "IC Team",
                "Comments",
                "Status",
            ]

            edited = st.data_editor(
                results[display_cols + ["row_key"]],
                hide_index=True,
                use_container_width=True,
                disabled=[
                    "Director Name",
                    "Director Title",
                    "Director Team",
                    "IC Name",
                    "IC Title",
                    "IC Team",
                    "row_key",
                ],
                column_config={
                    "Comments": st.column_config.TextColumn("Comments"),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=STATUS_OPTIONS,
                        required=False,
                    ),
                    "row_key": None,
                },
                key="editor_11",
            )

            for _, row in edited.iterrows():
                row_key = row["row_key"]
                st.session_state["comments_11"][row_key] = row["Comments"]
                st.session_state["status_11"][row_key] = row["Status"]

            export_df = edited.drop(columns=["row_key"])
            st.download_button(
                "Download current 1:1 results as CSV",
                export_df.to_csv(index=False).encode("utf-8"),
                file_name="skip_level_pairings_1_1.csv",
                mime="text/csv",
            )

    else:
        results = df_12[
            df_12["IC1 Name"].astype(str).str.contains(name, case=False, na=False)
            | df_12["IC2 Name"].astype(str).str.contains(name, case=False, na=False)
            | df_12["Director Name"].astype(str).str.contains(name, case=False, na=False)
        ].copy()

        if results.empty:
            st.warning("No matching mapping found.")
        else:
            results = add_edit_columns_12(results)

            display_cols = [
                "Director Name",
                "Director Title",
                "Director Team",
                "IC1 Name",
                "IC1 Title",
                "IC1 Team",
                "IC2 Name",
                "IC2 Title",
                "IC2 Team",
                "Comments",
                "Status",
            ]

            edited = st.data_editor(
                results[display_cols + ["row_key"]],
                hide_index=True,
                use_container_width=True,
                disabled=[
                    "Director Name",
                    "Director Title",
                    "Director Team",
                    "IC1 Name",
                    "IC1 Title",
                    "IC1 Team",
                    "IC2 Name",
                    "IC2 Title",
                    "IC2 Team",
                    "row_key",
                ],
                column_config={
                    "Comments": st.column_config.TextColumn("Comments"),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=STATUS_OPTIONS,
                        required=False,
                    ),
                    "row_key": None,
                },
                key="editor_12",
            )

            for _, row in edited.iterrows():
                row_key = row["row_key"]
                st.session_state["comments_12"][row_key] = row["Comments"]
                st.session_state["status_12"][row_key] = row["Status"]

            export_df = edited.drop(columns=["row_key"])
            st.download_button(
                "Download current 1:2 results as CSV",
                export_df.to_csv(index=False).encode("utf-8"),
                file_name="skip_level_pairings_1_2.csv",
                mime="text/csv",
            )
else:
    st.info("Search for an employee name to view their pairing details.")
