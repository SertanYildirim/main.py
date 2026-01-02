import streamlit as st
from modules import (
    loader,
    cleaner,
    eda,
    transformer,
    merger,
    filter_sort,
    grouper,
    outlier_handler,
    normalizer,
    feature_engineer,
    exporter,
    visualizer,
    logger,
    time_series
)

def main():
    st.set_page_config(page_title="🔍 Data Manipulation", layout="wide")
    st.title("🔍 Data Manipulation Application")

    # Initialize page_selected in session_state if not present
    if "page_selected" not in st.session_state:
        st.session_state.page_selected = "Data Loading"  # Default to Data Loading

    # Page selections inside Sidebar expander
    pages = {
        "Data Loading": "📥",
        "Exploratory Data Analysis (EDA)": "📊",
        "Missing Data Handling": "🧼",
        "Outlier Handling": "⚠️",
        "Data Transformation": "🔄",
        "Data Merging": "🔗",
        "Filtering & Sorting": "🔍",
        "Querying & Filtering": "📏",
        "Grouping": "🗂️",
        "Feature Engineering": "✨",
        "Visualization": "📈",
        "Time Series Analysis": "⏱️",
        "Logging": "📝",
        "Save & Export": "💾"
    }

    # CSS to center expander title and hide close icon
    st.markdown(
        """
        <style>
        /* Center expander title */
        div[data-testid="stExpander"] > div:first-child {
            justify-content: center;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        /* Hide expander close icon */
        div[data-testid="stExpander"] > div:first-child > button {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar.expander("🗂️ Operation Selection", expanded=True):
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", use_container_width=True, key=page_name):
                st.session_state.page_selected = page_name

    # Content on the right side
    if st.session_state.page_selected:
        match st.session_state.page_selected:
            case "Data Loading":
                loader.run()
            case "Exploratory Data Analysis (EDA)":
                eda.run()
            case "Missing Data Handling":
                cleaner.run()
            case "Outlier Handling":
                outlier_handler.run()
            case "Feature Engineering":
                feature_engineer.run()
            case "Data Transformation":
                transformer.run()
            case "Time Series Analysis":
                time_series.run()
            case "Data Merging":
                merger.run()
            case "Filtering & Sorting":
                filter_sort.run()
            case "Querying & Filtering":
                normalizer.run()
            case "Grouping":
                grouper.run()
            case "Visualization":
                visualizer.run()
            case "Save & Export":
                exporter.run()
            case "Logging":
                logger.run()

    else:
        st.info("Select an operation from the left panel.")

if __name__ == "__main__":
    main()
