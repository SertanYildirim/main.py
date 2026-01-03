# modules/visualizer.py

import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def run():
    """
    Visualizes the data.
    """
    sns.set(style="whitegrid")
    st.subheader("📊 Data Visualization")

    if "data" not in st.session_state:
        st.warning("Please load data first.")
        return

    df = st.session_state["data"]

    # 1. Select Chart Type
    plot_type = st.selectbox(
        "Select chart type:",
        ["Scatter Plot", "Histogram", "Box Plot", "Line Plot", "Heatmap", "Interactive Scatter"]
    )

    # 2. Select Columns
    # We filter columns based on utility (usually numeric for plotting, but allowing all for flexibility)
    columns = st.multiselect("Select column(s):", df.columns.tolist())

    # 3. Specific Options based on Plot Type
    combine_plots = False
    hue_col = None

    if plot_type in ["Histogram", "Box Plot", "Line Plot"]:
        # User experience improvement: Option to combine plots
        if len(columns) > 1:
            combine_plots = st.checkbox("Combine columns in one chart?", value=False)
            
    if plot_type == "Scatter Plot" and len(columns) >= 2:
        # UX Improvement: Color by category
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            use_hue = st.checkbox("Color by category (Hue)?")
            if use_hue:
                hue_col = st.selectbox("Select categorical column for color:", cat_cols)

    # 4. Generate Charts Button
    if st.button("Generate Charts"):
        
        # --- Scatter Plot ---
        if plot_type == "Scatter Plot":
            if len(columns) < 2:
                st.error("You must select at least 2 columns for a Scatter Plot.")
                return
            
            # Generate pairs
            for i in range(len(columns)-1):
                for j in range(i+1, len(columns)):
                    x_col, y_col = columns[i], columns[j]
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    if hue_col:
                        sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax)
                    else:
                        sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
                    
                    ax.set_title(f"Scatter Plot: {x_col} vs {y_col}")
                    st.pyplot(fig)

        # --- Interactive Scatter ---
        elif plot_type == "Interactive Scatter":
            if len(columns) < 2:
                st.error("You must select at least 2 columns for Interactive Scatter.")
                return
            
            try:
                import plotly.express as px
                for i in range(len(columns)-1):
                    for j in range(i+1, len(columns)):
                        x_col, y_col = columns[i], columns[j]
                        fig = px.scatter(df, x=x_col, y=y_col, title=f"Interactive: {x_col} vs {y_col}")
                        st.plotly_chart(fig)
            except ImportError:
                st.error("Plotly library is missing. Please install it or use standard Scatter Plot.")

        # --- Histogram ---
        elif plot_type == "Histogram":
            if not columns:
                st.error("Please select at least 1 column.")
                return

            if combine_plots:
                # Combined Chart
                fig, ax = plt.subplots(figsize=(10, 6))
                for col in columns:
                    sns.histplot(df[col], kde=True, label=col, alpha=0.5, ax=ax)
                ax.set_title("Combined Histogram")
                ax.legend()
                st.pyplot(fig)
            else:
                # Separate Charts
                for col in columns:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    sns.histplot(df[col], kde=True, ax=ax)
                    ax.set_title(f"Histogram: {col}")
                    st.pyplot(fig)

        # --- Box Plot ---
        elif plot_type == "Box Plot":
            if not columns:
                st.error("Please select at least 1 column.")
                return

            if combine_plots:
                # Combined Chart
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.boxplot(data=df[columns], ax=ax)
                ax.set_title("Combined Box Plot")
                st.pyplot(fig)
            else:
                # Separate Charts
                for col in columns:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    sns.boxplot(y=df[col], ax=ax)
                    ax.set_title(f"Box Plot: {col}")
                    st.pyplot(fig)

        # --- Line Plot ---
        elif plot_type == "Line Plot":
            if not columns:
                st.error("Please select at least 1 column.")
                return

            if combine_plots:
                # Combined Chart
                fig, ax = plt.subplots(figsize=(10, 6))
                for col in columns:
                    # Check if index is datetime for better plotting
                    if pd.api.types.is_datetime64_any_dtype(df.index):
                        ax.plot(df.index, df[col], label=col)
                    else:
                        ax.plot(df[col].values, label=col)
                ax.set_title("Combined Line Plot")
                ax.legend()
                st.pyplot(fig)
            else:
                # Separate Charts
                for col in columns:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    if pd.api.types.is_datetime64_any_dtype(df.index):
                         ax.plot(df.index, df[col], label=col)
                    else:
                         ax.plot(df[col].values, label=col)
                    ax.set_title(f"Line Plot: {col}")
                    ax.legend()
                    st.pyplot(fig)

        # --- Heatmap ---
        elif plot_type == "Heatmap":
            # If no columns selected, use all numeric columns
            target_cols = columns if columns else df.select_dtypes(include=['number']).columns.tolist()
            
            if len(target_cols) < 2:
                st.error("Heatmap requires at least 2 numerical columns.")
                return

            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(df[target_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            ax.set_title("Correlation Heatmap")
            st.pyplot(fig)
