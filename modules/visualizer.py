import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

def run():
    """
    Veriyi görselleştirir.
    """
    sns.set(style="whitegrid")
    st.subheader("📊 Veri Görselleştirme")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"]

    # Grafik türünü seç
    plot_type = st.selectbox(
        "Grafik türünü seçiniz:",
        ["scatter", "hist", "box", "line", "heatmap", "interactive_scatter"]
    )

    # Kolonları seç
    columns = st.multiselect("Kolon(lar) seçiniz:", df.columns.tolist())

    # Grafikleri oluştur
    if st.button("Grafikleri Göster"):
        if plot_type == "scatter" or plot_type == "interactive_scatter":
            # Scatter: kolon çiftleri ile ayrı grafikler
            if len(columns) < 2:
                st.error("Scatter plot için en az 2 sütun seçmelisiniz.")
                return
            for i in range(len(columns)-1):
                for j in range(i+1, len(columns)):
                    x_col, y_col = columns[i], columns[j]
                    plt.figure(figsize=(8,6))
                    if plot_type == "scatter":
                        sns.scatterplot(data=df, x=x_col, y=y_col)
                        plt.title(f"Scatter Plot: {x_col} vs {y_col}")
                        st.pyplot(plt)
                    else:
                        import plotly.express as px
                        fig = px.scatter(df, x=x_col, y=y_col, title=f"Interactive Scatter: {x_col} vs {y_col}")
                        st.plotly_chart(fig)

        elif plot_type == "hist" or plot_type == "box":
            # Histogram ve Box: her kolon için ayrı
            if len(columns) < 1:
                st.error(f"{plot_type} için en az 1 sütun seçmelisiniz.")
                return
            for col in columns:
                plt.figure(figsize=(8,6))
                if plot_type == "hist":
                    sns.histplot(df[col], kde=True)
                    plt.title(f"Histogram: {col}")
                else:
                    sns.boxplot(y=df[col])
                    plt.title(f"Box Plot: {col}")
                st.pyplot(plt)

        elif plot_type == "line":
            # Line: her kolon ayrı grafikte
            if len(columns) < 1:
                st.error("Line plot için en az 1 sütun seçmelisiniz.")
                return
            for col in columns:
                plt.figure(figsize=(8,6))
                plt.plot(df.index, df[col], label=col)
                plt.legend()
                plt.title(f"Line Plot: {col}")
                st.pyplot(plt)

        elif plot_type == "heatmap":
            # Heatmap: tüm sayısal kolonlar için
            plt.figure(figsize=(10,6))
            sns.heatmap(df[columns].corr(), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Heatmap - Korelasyon Matrisi")
            st.pyplot(plt)
