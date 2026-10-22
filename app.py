import streamlit as st
import pandas as pd

from sample_data import generate_data
from matching import compare_records
from database import create_table, save_review, get_reviews


st.set_page_config(
    page_title="Civify",
    page_icon="C",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #222522;
        color: #F0F0E8;
    }

    [data-testid="stSidebar"] {
        background-color: #1B1E1B;
        border-right: 1px solid #383D38;
    }

    h1, h2, h3 {
        color: #F0F0E8;
    }

    div[data-testid="stMetric"] {
        background-color: #292D29;
        border: 1px solid #3B413B;
        padding: 16px;
        border-radius: 8px;
    }

    div.stButton > button {
        background-color: #465B49;
        color: white;
        border: 1px solid #596F5C;
        border-radius: 6px;
    }

    div.stButton > button:hover {
        background-color: #566E59;
        color: white;
    }

    hr {
        border-color: #3B413B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

create_table()

records = generate_data()
results = []

for record in records:
    analysis = compare_records(
        record["citizen"],
        record["asset"],
    )

    results.append({
        **record,
        "analysis": analysis,
    })


if "page" not in st.session_state:
    st.session_state.page = "Case queue"

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

if "review_saved" not in st.session_state:
    st.session_state.review_saved = False

if st.session_state.pop("review_saved", False):
    st.toast("Review saved successfully!", icon="✅")


def get_case(case_id):
    for case in results:
        if case["case_id"] == case_id:
            return case

    return None


def get_status(case):
    return case["analysis"]["result"]


def get_score(case):
    return case["analysis"].get("score", 0)


def render_record(title, record):
    st.subheader(title)

    for field, value in record.items():
        field_name = field.replace("_", " ").title()
        st.write(f"**{field_name}:** {value if value else 'Not provided'}")


def render_case_detail(case):
    analysis = case["analysis"]

    st.title(case["case_id"])
    st.caption(case.get("issue", "Record mismatch review"))

    col1, col2, col3 = st.columns(3)

    col1.metric("Similarity score", f"{get_score(case):.0f}/100")
    col2.metric("System result", get_status(case))
    col3.metric(
        "Fields compared",
        len(analysis.get("details", [])),
    )

    st.divider()

    citizen_col, asset_col = st.columns(2)

    with citizen_col:
        render_record("Citizen record", case["citizen"])

    with asset_col:
        render_record("Asset / service record", case["asset"])

    st.divider()
    st.subheader("Comparison details")

    details = analysis.get("details", [])

    if details:
        detail_rows = []

        for item in details:
            detail_rows.append({
                "Field": item["field"].replace("_", " ").title(),
                "Citizen value": item["left"] or "Not provided",
                "Asset value": item["right"] or "Not provided",
                "Similarity": (
                    f"{item['similarity']:.1f}%"
                    if item["left"] and item["right"]
                    else "Unavailable"
                ),
                "Status": item["status"],
            })

        st.dataframe(
            pd.DataFrame(detail_rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No field-level comparison details are available.")

    reasons = analysis.get("reasons", [])

    if reasons:
        st.subheader("Why this result was returned")

        for reason in reasons:
            st.write(f"- {reason}")

    st.divider()
    st.subheader("Human review")

    st.caption(
        "Check the records and select a review decision. "
        "The system does not make the final decision."
    )

    with st.form(f"review_form_{case['case_id']}"):
        reviewer = st.text_input(
            "Reviewer name or ID",
            placeholder="Enter reviewer name or ID",
        )

        decision = st.selectbox(
            "Review decision",
            [
                "Confirmed mismatch",
                "No mismatch found",
                "Needs further verification",
                "Insufficient information",
            ],
        )

        notes = st.text_area(
            "Review notes",
            placeholder="Add a short explanation for your decision.",
        )

        submitted = st.form_submit_button(
            "Save review",
            use_container_width=True,
        )

        if submitted:
            if not reviewer.strip():
                st.error("Enter a reviewer name or ID.")
            else:
                save_review(
                    case["case_id"],
                    reviewer.strip(),
                    decision,
                    notes.strip(),
                )

                st.session_state.review_saved = True
                st.rerun()

    st.divider()
    st.subheader("Review history")

    try:
        reviews = get_reviews(case["case_id"])

        if reviews is None or len(reviews) == 0:
            st.caption("No reviews recorded for this case.")
        elif isinstance(reviews, pd.DataFrame):
            st.dataframe(
                reviews,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(
                pd.DataFrame(reviews),
                use_container_width=True,
                hide_index=True,
            )

    except Exception:
        st.caption("Review history is currently unavailable.")


def render_case_queue():
    st.title("Case queue")
    st.caption("Review flagged record mismatches.")

    col1, col2 = st.columns([2, 1])

    with col1:
        search = st.text_input(
            "Search cases",
            placeholder="Search by case ID, name, or issue...",
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            [
                "All cases",
                "Needs review",
                "High similarity",
                "Low similarity",
                "Insufficient data",
            ],
        )

    filtered_cases = []

    for case in results:
        citizen_name = case.get("citizen", {}).get("name", "")
        issue = case.get("issue", "")

        search_text = (
            f"{case['case_id']} {citizen_name} {issue}"
        ).lower()

        if search.lower() not in search_text:
            continue

        if (
            status_filter != "All cases"
            and get_status(case) != status_filter
        ):
            continue

        filtered_cases.append(case)

    st.caption(f"{len(filtered_cases)} cases found")

    if not filtered_cases:
        st.info("No cases match your search or filter.")
        return

    case_rows = []

    for case in filtered_cases:
        case_rows.append({
            "Case ID": case["case_id"],
            "Citizen": case.get("citizen", {}).get("name", "Unknown"),
            "Issue": case.get("issue", "—"),
            "Score": f"{get_score(case):.0f}/100",
            "Status": get_status(case),
        })

    st.dataframe(
        pd.DataFrame(case_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    case_ids = [case["case_id"] for case in filtered_cases]

    if st.session_state.selected_case not in case_ids:
        st.session_state.selected_case = case_ids[0]

    selected_id = st.selectbox(
        "Select a case to open",
        case_ids,
        index=case_ids.index(st.session_state.selected_case),
        format_func=lambda case_id: (
            f"{case_id} — "
            f"{get_case(case_id)['citizen'].get('name', 'Unknown')}"
        ),
    )

    st.session_state.selected_case = selected_id

    if st.button("View case details", use_container_width=True):
        st.session_state.page = "Case details"
        st.rerun()


def render_overview():
    st.title("Overview")
    st.caption("Summary of the synthetic dataset.")

    total_cases = len(results)
    needs_review = 0
    high_similarity = 0
    low_similarity = 0
    insufficient_data = 0

    for case in results:
        status = get_status(case)

        if status == "Needs review":
            needs_review += 1
        elif status == "High similarity":
            high_similarity += 1
        elif status == "Low similarity":
            low_similarity += 1
        elif status == "Insufficient data":
            insufficient_data += 1

    col1, col2, col3 = st.columns(3)

    col1.metric("Total cases", total_cases)
    col2.metric("Needs review", needs_review)
    col3.metric("Insufficient data", insufficient_data)

    col4, col5 = st.columns(2)

    col4.metric("High similarity", high_similarity)
    col5.metric("Low similarity", low_similarity)

    st.divider()
    st.subheader("Cases by system result")

    status_counts = {}

    for case in results:
        status = get_status(case)
        status_counts[status] = status_counts.get(status, 0) + 1

    if status_counts:
        chart_data = pd.DataFrame(
            list(status_counts.items()),
            columns=["Status", "Cases"],
        )

        st.bar_chart(chart_data.set_index("Status"))

    st.caption(
        "These figures describe the synthetic demonstration data, "
        "not real government operations."
    )


def render_evaluation():
    st.title("Evaluation")
    st.caption("Evaluation using synthetic data.")

    total_cases = len(results)

    if total_cases == 0:
        st.info("No cases available.")
        return

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    abstentions = 0

    for case in results:
        status = get_status(case)
        actual_match = bool(case["actual_match"])

        if status in ("Needs review", "Insufficient data"):
            abstentions += 1

        elif status == "High similarity":
            if actual_match:
                true_positive += 1
            else:
                false_positive += 1

        elif status == "Low similarity":
            if actual_match:
                false_negative += 1
            else:
                true_negative += 1

    decided = (
        true_positive
        + true_negative
        + false_positive
        + false_negative
    )

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0
    )

    accuracy = (
        (true_positive + true_negative) / decided
        if decided else 0
    )

    coverage = decided / total_cases

    col1, col2, col3 = st.columns(3)

    col1.metric("Total cases", total_cases)
    col2.metric("Automated results", decided)
    col3.metric("Decision coverage", f"{coverage:.1%}")

    st.write(
        "Decision coverage is the percentage of cases that receive "
        "an automated result. Cases requiring review or having "
        "insufficient data are excluded."
    )

    st.divider()
    st.subheader("Evaluation metrics")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric("Precision", f"{precision:.1%}")
    metric_col2.metric("Recall", f"{recall:.1%}")
    metric_col3.metric("Accuracy", f"{accuracy:.1%}")

    st.caption(
        "Accuracy is calculated on decided cases only. "
        "Precision and recall measure the system's positive-match predictions."
    )

    st.divider()
    st.subheader("Classification counts")

    counts = pd.DataFrame(
        [
            {"Metric": "True positives", "Count": true_positive},
            {"Metric": "True negatives", "Count": true_negative},
            {"Metric": "False positives", "Count": false_positive},
            {"Metric": "False negatives", "Count": false_negative},
            {"Metric": "Abstentions", "Count": abstentions},
        ]
    )

    st.dataframe(
        counts,
        use_container_width=True,
        hide_index=True,
    )

    st.warning(
        "These metrics apply only to the generated synthetic dataset. "
        "They do not establish real-world accuracy or effectiveness."
    )


def render_audit_log():
    st.title("Audit log")
    st.caption("Previously recorded human reviews.")

    try:
        reviews = get_reviews()

        if reviews is None or len(reviews) == 0:
            st.info("No reviews have been recorded yet.")
            return

        if isinstance(reviews, pd.DataFrame):
            review_data = reviews
        else:
            review_data = pd.DataFrame(reviews)

        if review_data.empty:
            st.info("No reviews have been recorded yet.")
        else:
            st.dataframe(
                review_data,
                use_container_width=True,
                hide_index=True,
            )

    except Exception as error:
        st.error(f"Could not load the audit log: {error}")


with st.sidebar:
    st.title("Civify")
    st.caption("Data mismatch detection and human review")
    st.divider()

    pages = [
        "Case queue",
        "Overview",
        "Evaluation",
        "Audit log",
    ]

    for page in pages:
        if st.button(page, use_container_width=True, key=f"nav_{page}"):
            st.session_state.page = page
            st.rerun()

    st.divider()
    st.caption("Prototype · Synthetic data")


if st.session_state.page == "Case queue":
    render_case_queue()

elif st.session_state.page == "Case details":
    case = get_case(st.session_state.selected_case)

    if case is None:
        st.warning("Case not found.")

        if st.button("Back to case queue"):
            st.session_state.page = "Case queue"
            st.rerun()
    else:
        if st.button("← Back to case queue"):
            st.session_state.page = "Case queue"
            st.rerun()

        render_case_detail(case)

elif st.session_state.page == "Overview":
    render_overview()

elif st.session_state.page == "Evaluation":
    render_evaluation()

elif st.session_state.page == "Audit log":
    render_audit_log()


st.divider()

st.caption(
    "Civify — From data mismatch to explainable human review. "
    "This prototype uses synthetic data and does not make "
    "welfare eligibility or fraud determinations."
)