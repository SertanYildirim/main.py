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
    st.set_page_config(page_title="🔍 Veri Manipülasyonu", layout="wide")
    st.title("🔍 Veri Manipülasyonu Uygulaması")

    # session_state'de page_selected yoksa başlat
    if "page_selected" not in st.session_state:
        st.session_state.page_selected = "Veri Yükleme"  # Varsayılan olarak veri yükleme açık

    # Sidebar expander içinde sayfa seçimleri
    pages = {
        "Veri Yükleme": "📥",
        "Keşifsel Veri Analizi (EDA)": "📊",
        "Eksik Veri İşlemleri": "🧼",
        "Aykırı Değer İşlemleri": "⚠️",
        "Veri Dönüştürme": "🔄",
        "Veri Birleştirme": "🔗",
        "Filtreleme & Sıralama": "🔍",
        "Sorgulama & Filtreleme": "📏",
        "Gruplama": "🗂️",
        "Özellik Mühendisliği": "✨",
        "Görselleştirme": "📈",
        "Zaman Serisi Analizi": "⏱️",
        "Loglama": "📝",
        "Kaydet & Aktar": "💾"
    }

    # CSS ile expander başlığını ortala ve kapatma ikonunu gizle
    st.markdown(
        """
        <style>
        /* Expander başlığını ortala */
        div[data-testid="stExpander"] > div:first-child {
            justify-content: center;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        /* Expander kapatma ikonunu gizle */
        div[data-testid="stExpander"] > div:first-child > button {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar.expander("🗂️ İşlem Seçimi", expanded=True):
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", use_container_width=True, key=page_name):
                st.session_state.page_selected = page_name

    # Sağ tarafta içerik
    if st.session_state.page_selected:
        match st.session_state.page_selected:
            case "Veri Yükleme":
                loader.run()
            case "Keşifsel Veri Analizi (EDA)":
                eda.run()
            case "Eksik Veri İşlemleri":
                cleaner.run()
            case "Aykırı Değer İşlemleri":
                outlier_handler.run()
            case "Özellik Mühendisliği":
                feature_engineer.run()
            case "Veri Dönüştürme":
                transformer.run()
            case "Zaman Serisi Analizi":
                time_series.run()
            case "Veri Birleştirme":
                merger.run()
            case "Filtreleme & Sıralama":
                filter_sort.run()
            case "Sorgulama & Filtreleme":
                normalizer.run()
            case "Gruplama":
                grouper.run()
            case "Görselleştirme":
                visualizer.run()
            case "Kaydet & Aktar":
                exporter.run()
            case "Loglama":
                logger.run()

    else:
        st.info("Soldaki panelden bir işlem seçin.")

if __name__ == "__main__":
    main()
