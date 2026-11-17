import os
import io
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns



st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_theme(style="whitegrid")



st.markdown("""
<style>

/* Main dashboard background */
.stApp {
    background-color: #0B1120;
    color: #F8FAFC;
}

/* Headings */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
}

/* Normal text */
p, label, span {
    color: #E2E8F0;
}

/* KPI metric cards */
[data-testid="stMetric"] {
    background-color: #1E293B;
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 14px;
}

/* KPI labels */
[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
}

/* KPI values */
[data-testid="stMetricValue"] {
    color: #38BDF8 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F8FAFC !important;
}

/* Info messages */
.stAlert {
    background-color: #1E293B;
    color: #F8FAFC;
}

/* Data tables */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


DEFAULT_FILE = (
    r"C:\Users\sansh\OneDrive\Desktop"
    r"\Data_Analytics_Project\pbl data.xlsx"
)




@st.cache_data(show_spinner=False)
def load_excel(uploaded_bytes, file_path, file_name):
    """
    Load Excel from uploaded bytes or a local file.
    """

    if uploaded_bytes is not None:
        return pd.read_excel(io.BytesIO(uploaded_bytes))

    if file_path and os.path.exists(file_path):
        return pd.read_excel(file_path)

    return None




def clean_dataset(data):
    """
    Clean dataset without modifying the original Excel file.
    """

    df = data.copy()

    # Normalize column names by removing extra spaces.
    df.columns = [str(c).strip() for c in df.columns]

    # Remove exact duplicate rows.
    initial_rows = len(df)
    df = df.drop_duplicates().copy()
    duplicates_removed = initial_rows - len(df)

    # Numeric columns.
    numeric_cols = df.select_dtypes(include=np.number).columns

    # Fill missing numeric values with median.
    for col in numeric_cols:
        median_value = df[col].median()

        if pd.notna(median_value):
            df[col] = df[col].fillna(median_value)

    # Fill missing categorical values.
    categorical_cols = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns

    for col in categorical_cols:
        df[col] = df[col].fillna("Unknown")

    # Convert expected numerical columns when present.
    expected_numeric = [
        "Hours_Studied",
        "Attendance",
        "Sleep_Hours",
        "Previous_Scores",
        "Tutoring_Sessions",
        "math score",
        "reading score",
        "writing score"
    ]

    for col in expected_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

            if df[col].notna().any():
                df[col] = df[col].fillna(df[col].median())

    return df, duplicates_removed



def assign_grade(percentage):
    if pd.isna(percentage):
        return "Unknown"
    elif percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"


def calculate_academic_metrics(df):
    """
    Calculate results from the three actual score columns.

    Percentage is calculated out of 100 using the average
    of math, reading and writing scores.
    """

    df = df.copy()

    score_cols = [
        "math score",
        "reading score",
        "writing score"
    ]

    missing_cols = [c for c in score_cols if c not in df.columns]

    if missing_cols:
        raise ValueError(
            "Required score columns are missing: "
            + ", ".join(missing_cols)
        )

    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    
    valid_scores = df[score_cols].notna().all(axis=1)

    df["Total_Marks"] = df[score_cols].sum(
        axis=1,
        min_count=3
    )

    df["Percentage"] = (
        df["Total_Marks"] / 3.0
    ).round(2)

    df["GPA"] = (
        df["Percentage"] / 10.0
    ).round(2)

    df["Grade"] = df["Percentage"].apply(assign_grade)

    # Pass rule is configurable in the sidebar.
    df["Pass_Status"] = np.where(
        valid_scores,
        "Pass",
        "Not Available"
    )

    return df




st.sidebar.title("📊 Dashboard Controls")

st.sidebar.markdown("---")

st.sidebar.subheader("📁 Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel dataset",
    type=["xlsx", "xls"]
)

uploaded_bytes = (
    uploaded_file.getvalue()
    if uploaded_file is not None
    else None
)

try:
    original_df = load_excel(
        uploaded_bytes,
        DEFAULT_FILE,
        uploaded_file.name if uploaded_file else "local"
    )
except Exception as error:
    st.error(f"Unable to read the Excel file: {error}")
    st.stop()

if original_df is None:
    st.title("📊 Student Academic Performance Analytics")

    st.warning(
        "Dataset file nahi mili. Please upload your Excel file "
        "using the sidebar."
    )

    st.info(
        "Default path: " + DEFAULT_FILE
    )

    st.stop()



df, duplicates_removed = clean_dataset(original_df)

try:
    df = calculate_academic_metrics(df)
except ValueError as error:
    st.error(str(error))
    st.stop()




st.markdown(
    '<div class="main-title">'
    '📊 Student Academic Performance Analytics'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive dashboard for exploring student performance, '
    'study habits, attendance and academic results.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="info-box">'
    'Use the sidebar filters to explore different student groups. '
    'The statistics, charts and records will update automatically.'
    '</div>',
    unsafe_allow_html=True
)

st.write("")




st.sidebar.subheader("🔎 Student Filters")

filtered_df = df.copy()


def add_category_filter(data, column, label):
    """
    Add a category filter only when the column exists.
    """

    global filtered_df

    if column not in data.columns:
        return

    values = sorted(
        data[column].dropna().astype(str).unique().tolist()
    )

    selected = st.sidebar.multiselect(
        label,
        options=values,
        default=values,
        key=f"filter_{column}"
    )

    if selected:
        filtered_df = filtered_df[
            filtered_df[column].astype(str).isin(selected)
        ]
    else:
        filtered_df = filtered_df.iloc[0:0]


category_filters = [
    ("gender", "Gender"),
    ("Parental_Involvement", "Parental Involvement"),
    ("Access_to_Resources", "Access to Resources"),
    ("Extracurricular_Activities", "Extracurricular Activities"),
    ("Motivation_Level", "Motivation Level"),
    ("Internet_Access", "Internet Access"),
    ("test preparation course", "Test Preparation Course"),
    ("parental level of education", "Parental Education"),
    ("lunch", "Lunch Category"),
    ("race/ethnicity", "Race / Ethnicity")
]

for column, label in category_filters:
    add_category_filter(df, column, label)


def add_range_filter(data, column, label):
    """
    Display a slider for numerical columns.
    """

    global filtered_df

    if column not in data.columns:
        return

    numeric_values = pd.to_numeric(
        data[column],
        errors="coerce"
    ).dropna()

    if numeric_values.empty:
        return

    minimum = float(numeric_values.min())
    maximum = float(numeric_values.max())

    if minimum == maximum:
        return

    selected_range = st.sidebar.slider(
        label,
        min_value=minimum,
        max_value=maximum,
        value=(minimum, maximum),
        key=f"range_{column}"
    )

    filtered_df = filtered_df[
        pd.to_numeric(
            filtered_df[column],
            errors="coerce"
        ).between(
            selected_range[0],
            selected_range[1],
            inclusive="both"
        )
    ]


numeric_filters = [
    ("Hours_Studied", "Hours Studied"),
    ("Attendance", "Attendance"),
    ("Sleep_Hours", "Sleep Hours"),
    ("Previous_Scores", "Previous Scores"),
    ("Tutoring_Sessions", "Tutoring Sessions")
]

for column, label in numeric_filters:
    add_range_filter(df, column, label)


st.sidebar.markdown("---")
st.sidebar.subheader("🎓 Academic Settings")

pass_mark = st.sidebar.slider(
    "Minimum Passing Percentage",
    min_value=0,
    max_value=100,
    value=40,
    step=5
)

if not filtered_df.empty:
    filtered_df = filtered_df.copy()

    filtered_df["Pass_Status"] = np.where(
        filtered_df["Percentage"] >= pass_mark,
        "Pass",
        "Fail"
    )

st.markdown(
    '<div class="section-heading">📌 Performance Overview</div>',
    unsafe_allow_html=True
)

if filtered_df.empty:
    st.warning(
        "No students match the selected filters. "
        "Change the filters to view the dashboard."
    )
    st.stop()

total_students = len(filtered_df)

avg_percentage = filtered_df["Percentage"].mean()
avg_gpa = filtered_df["GPA"].mean()

avg_attendance = (
    filtered_df["Attendance"].mean()
    if "Attendance" in filtered_df.columns
    else np.nan
)

pass_rate = (
    (filtered_df["Pass_Status"] == "Pass").mean() * 100
)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Students",
    f"{total_students:,}"
)

col2.metric(
    "Average Percentage",
    f"{avg_percentage:.2f}%"
)

col3.metric(
    "Average GPA",
    f"{avg_gpa:.2f}/10"
)

col4.metric(
    "Pass Rate",
    f"{pass_rate:.1f}%"
)

col5.metric(
    "Avg Attendance",
    f"{avg_attendance:.1f}%"
    if pd.notna(avg_attendance)
    else "N/A"
)

st.caption(
    f"Passing threshold: {pass_mark}%. "
    "GPA is calculated as Percentage / 10. "
    "These are project-defined metrics, not official institutional grades."
)

st.divider()


st.markdown(
    '<div class="section-heading">📈 Academic Analysis</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Grade Distribution")

    grade_order = ["A+", "A", "B", "C", "D", "F"]

    grade_counts = (
        filtered_df["Grade"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        grade_counts.index,
        grade_counts.values,
        edgecolor="black"
    )

    ax.set_xlabel("Grade")
    ax.set_ylabel("Number of Students")
    ax.set_title("Student Grade Distribution")

    for bar in bars:
        height = bar.get_height()

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            str(int(height)),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


with col2:
    st.subheader("Pass / Fail Distribution")

    pass_counts = (
        filtered_df["Pass_Status"]
        .value_counts()
        .reindex(["Pass", "Fail"], fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.pie(
        pass_counts.values,
        labels=pass_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Overall Pass / Fail Ratio")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


col1, col2 = st.columns(2)

with col1:
    st.subheader("Study Hours vs Percentage")

    if "Hours_Studied" in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))

        sns.regplot(
            data=filtered_df,
            x="Hours_Studied",
            y="Percentage",
            scatter_kws={"alpha": 0.35},
            line_kws={"linewidth": 2},
            ax=ax
        )

        ax.set_title("Study Hours and Academic Performance")
        ax.set_xlabel("Hours Studied")
        ax.set_ylabel("Percentage")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Hours_Studied column is not available.")



with col2:
    st.subheader("Average Score by Subject")

    subject_cols = [
        "math score",
        "reading score",
        "writing score"
    ]

    subject_names = {
        "math score": "Math",
        "reading score": "Reading",
        "writing score": "Writing"
    }

    available_subjects = [
        c for c in subject_cols
        if c in filtered_df.columns
    ]

    subject_means = (
        filtered_df[available_subjects]
        .mean()
        .rename(index=subject_names)
        .dropna()
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.barh(
        subject_means.index,
        subject_means.values
    )

    ax.set_xlim(0, 100)
    ax.set_xlabel("Average Score")
    ax.set_title("Average Marks by Subject")

    for bar in bars:
        width = bar.get_width()

        ax.text(
            width + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}",
            va="center"
        )

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Parental Involvement vs Performance")

    if "Parental_Involvement" in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))

        sns.boxplot(
            data=filtered_df,
            x="Parental_Involvement",
            y="Percentage",
            order=["Low", "Medium", "High"],
            ax=ax
        )

        ax.set_title("Parental Involvement and Percentage")
        ax.set_xlabel("Parental Involvement")
        ax.set_ylabel("Percentage")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Parental_Involvement column is not available.")

with col2:
    st.subheader("Attendance vs Performance")

    if "Attendance" in filtered_df.columns:
        fig, ax = plt.subplots(figsize=(8, 5))

        sns.regplot(
            data=filtered_df,
            x="Attendance",
            y="Percentage",
            scatter_kws={"alpha": 0.4},
            line_kws={"linewidth": 2},
            ax=ax
        )

        ax.set_title("Attendance and Percentage")
        ax.set_xlabel("Attendance")
        ax.set_ylabel("Percentage")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Attendance column is not available.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sleep Hours vs Performance")

    if "Sleep_Hours" in filtered_df.columns:
        sleep_data = filtered_df.copy()

        sleep_data["Sleep_Hours"] = pd.to_numeric(
            sleep_data["Sleep_Hours"],
            errors="coerce"
        )

        sleep_summary = (
            sleep_data.groupby("Sleep_Hours")["Percentage"]
            .mean()
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(8, 5))

        sns.lineplot(
            data=sleep_summary,
            x="Sleep_Hours",
            y="Percentage",
            marker="o",
            ax=ax
        )

        ax.set_title("Average Percentage by Sleep Hours")
        ax.set_xlabel("Sleep Hours")
        ax.set_ylabel("Average Percentage")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Sleep_Hours column is not available.")

with col2:
    st.subheader("Academic Correlation Heatmap")

    correlation_cols = [
        "Hours_Studied",
        "Attendance",
        "Sleep_Hours",
        "Previous_Scores",
        "Tutoring_Sessions",
        "math score",
        "reading score",
        "writing score",
        "Percentage"
    ]

    available_corr_cols = [
        c for c in correlation_cols
        if c in filtered_df.columns
        and pd.api.types.is_numeric_dtype(filtered_df[c])
    ]

    if len(available_corr_cols) >= 2:
        correlation = filtered_df[
            available_corr_cols
        ].corr()

        fig, ax = plt.subplots(figsize=(10, 7))

        sns.heatmap(
            correlation,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            ax=ax
        )

        ax.set_title("Correlation Between Academic Features")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Not enough numerical columns for correlation analysis.")


st.divider()

st.markdown(
    '<div class="section-heading">📚 Subject Explorer</div>',
    unsafe_allow_html=True
)

subject_options = {
    "Math": "math score",
    "Reading": "reading score",
    "Writing": "writing score"
}

selected_subject = st.selectbox(
    "Select a subject",
    options=list(subject_options.keys())
)

selected_column = subject_options[selected_subject]

subject_average = filtered_df[selected_column].mean()
subject_median = filtered_df[selected_column].median()
subject_highest = filtered_df[selected_column].max()
subject_lowest = filtered_df[selected_column].min()

s1, s2, s3, s4 = st.columns(4)

s1.metric("Average Score", f"{subject_average:.2f}")
s2.metric("Median Score", f"{subject_median:.2f}")
s3.metric("Highest Score", f"{subject_highest:.0f}")
s4.metric("Lowest Score", f"{subject_lowest:.0f}")

fig, ax = plt.subplots(figsize=(12, 4))

sns.histplot(
    data=filtered_df,
    x=selected_column,
    bins=20,
    kde=True,
    ax=ax
)

ax.set_title(f"{selected_subject} Score Distribution")
ax.set_xlabel("Score")
ax.set_ylabel("Number of Students")

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.divider()

st.markdown(
    '<div class="section-heading">🔎 Student Data Explorer</div>',
    unsafe_allow_html=True
)

st.write(
    "Search, sort and explore the student records "
    "after applying sidebar filters."
)

search_text = st.text_input(
    "Search student records",
    placeholder="Type a value, for example female, group B or 75"
)

table_df = filtered_df.copy()

if search_text.strip():
    search_mask = table_df.astype(str).apply(
        lambda column: column.str.contains(
            search_text,
            case=False,
            regex=False,
            na=False
        )
    ).any(axis=1)

    table_df = table_df[search_mask]

st.caption(
    f"Showing {len(table_df):,} records "
    f"out of {len(filtered_df):,} filtered students."
)

st.dataframe(
    table_df,
    use_container_width=True,
    height=420,
    hide_index=True
)

st.subheader("📥 Export Results")

csv_data = table_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="student_performance_filtered.csv",
    mime="text/csv"
)

with st.expander("🧹 Dataset Quality Information"):
    q1, q2, q3 = st.columns(3)

    q1.metric(
        "Original Rows",
        f"{len(original_df):,}"
    )

    q2.metric(
        "Rows After Duplicate Removal",
        f"{len(df):,}"
    )

    q3.metric(
        "Duplicate Rows Removed",
        f"{duplicates_removed:,}"
    )

    missing_values = original_df.isnull().sum()

    missing_report = (
        missing_values[missing_values > 0]
        .rename("Missing Values")
        .reset_index()
        .rename(columns={"index": "Column"})
    )

    st.write("Missing values in the original dataset:")

    if missing_report.empty:
        st.success("No missing values found in the original dataset.")
    else:
        st.dataframe(
            missing_report,
            use_container_width=True,
            hide_index=True
        )

    st.write("Dataset column information:")

    column_report = pd.DataFrame({
        "Column": df.columns,
        "Data Type": [
            str(df[c].dtype) for c in df.columns
        ],
        "Non-Null Values": [
            int(df[c].notna().sum()) for c in df.columns
        ]
    })

    st.dataframe(
        column_report,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#64748b; padding:10px;">
        <b>Student Academic Performance Analytics</b><br>
        Built with Python, Pandas, NumPy, Matplotlib,
        Seaborn and Streamlit.<br>
        BCA Project — Data Analytics
    </div>
    """,
    unsafe_allow_html=True
)