import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from keras.models import Sequential
from keras.layers import GRU, Dense, LSTM

# ====================================
# Yardımcı Fonksiyonlar
# ====================================

def preprocess_data(df):
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
        df.set_index(df.columns[0], inplace=True)

    # Tüm sayısal kolonları al
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) > 1:
        value_col = st.selectbox("Analiz edilecek sayısal kolon", numeric_cols)
    else:
        value_col = numeric_cols[0]

    return df, value_col

def resample_data(df, value_col, freq_unit):
    return df[value_col].resample(freq_unit).mean()

def is_stationary(series):
    pval = sm.tsa.stattools.adfuller(series.dropna())[1]
    return pval < 0.05, pval

def ts_decompose(y, model="additive"):
    result = seasonal_decompose(y, model=model)
    fig, axes = plt.subplots(4, 1, sharex=True, figsize=(12, 8))
    axes[0].plot(y, 'k'); axes[0].set_title("Original")
    axes[1].plot(result.trend); axes[1].set_title("Trend")
    axes[2].plot(result.seasonal, 'g'); axes[2].set_title("Seasonality")
    axes[3].plot(result.resid, 'r'); axes[3].set_title("Residuals")
    st.pyplot(fig)
    return result

def hurst_exponent(series):
    ts = series.dropna().values
    if len(ts) < 10:
        return np.nan
    lags = np.arange(2, min(100, len(ts)//2))
    tau = np.array([np.std(ts[lag:] - ts[:-lag]) for lag in lags])
    valid = tau > 0
    if valid.sum() < 2:
        return np.nan
    lags, tau = lags[valid], tau[valid]
    H = np.polyfit(np.log(lags), np.log(tau), 1)[0]
    return H

def calculate_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return mae, rmse, mape

def run_arima(series, order, steps=12):
    model = sm.tsa.ARIMA(series, order=order)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series, label="Gerçek Seri")
    ax.plot(forecast.index, forecast, label="Tahmin", color="red")
    ax.legend()
    st.pyplot(fig)

    st.dataframe(forecast.rename("Forecast"))

    if len(series) > steps:
        y_true = series[-steps:]
        y_pred = forecast[:steps]
        mae, rmse, mape = calculate_metrics(y_true, y_pred)
        st.success(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} | MAPE: {mape:.2f}%")

def run_prophet(series, periods=12, freq="M"):
    df = pd.DataFrame({"ds": series.index, "y": series.values})
    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    fig1 = model.plot(forecast)
    st.pyplot(fig1)

    st.dataframe(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods))

    if len(df) > periods:
        y_true = df["y"].iloc[-periods:]
        y_pred = forecast["yhat"].iloc[-periods:]
        mae, rmse, mape = calculate_metrics(y_true, y_pred)
        st.success(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} | MAPE: {mape:.2f}%")

def run_sarimax(series, order, seasonal_order, steps):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    # Modeli fit et
    model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
    model_fit = model.fit(disp=False)
    forecast = model_fit.get_forecast(steps=steps)
    forecast_mean = forecast.predicted_mean
    conf_int = forecast.conf_int()

    # Grafik
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series, label="Gerçek Seri")
    ax.plot(forecast_mean.index, forecast_mean, label="SARIMAX Tahmin", color="orange")
    ax.fill_between(conf_int.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1],
                    color="orange", alpha=0.2)
    ax.legend()
    st.pyplot(fig)

    # Tahmin tablosu
    st.dataframe(forecast_mean.rename("Forecast"))

    # Metrikler
    if len(series) > steps:
        y_true = series[-steps:]
        y_pred = forecast_mean[:steps]
        mae, rmse, mape = calculate_metrics(y_true, y_pred)
        st.success(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} | MAPE: {mape:.2f}%")


def run_tes(series, periods, seasonal, trend, seasonal_periods):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    # Modeli fit et
    model = ExponentialSmoothing(series, trend=trend,
                                 seasonal=seasonal,
                                 seasonal_periods=seasonal_periods)
    model_fit = model.fit()
    forecast = model_fit.forecast(periods)

    # Grafik
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series, label="Gerçek Seri")
    ax.plot(forecast.index, forecast, label="TES Tahmin", color="green")
    ax.legend()
    st.pyplot(fig)

    # Tahmin tablosu
    st.dataframe(forecast.rename("Forecast"))

    # Metrikler
    if len(series) > periods:
        y_true = series[-periods:]
        y_pred = forecast[:periods]
        mae, rmse, mape = calculate_metrics(y_true, y_pred)
        st.success(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} | MAPE: {mape:.2f}%")

def run_lstm(series, look_back=10, steps=12, epochs=20, batch_size=16):
    # Sequence oluşturma
    def create_sequences(data, look_back):
        X, y = [], []
        for i in range(len(data) - look_back):
            X.append(data[i:(i+look_back)])
            y.append(data[i + look_back])
        return np.array(X), np.array(y)

    values = series.values
    X, y = create_sequences(values, look_back)

    # Train/Test split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # Model
    model = Sequential()
    model.add(LSTM(50, activation="relu", input_shape=(look_back, 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")

    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

    # Test tahmin
    y_pred = model.predict(X_test, verbose=0).flatten()

    # Gelecek forecast
    last_seq = values[-look_back:].reshape(1, look_back, 1)
    future_preds = []
    for _ in range(steps):
        next_val = model.predict(last_seq, verbose=0)[0][0]
        future_preds.append(next_val)
        last_seq = np.append(last_seq[:, 1:, :], [[[next_val]]], axis=1)

    forecast_index = pd.date_range(start=series.index[-1], periods=steps+1, freq="M")[1:]
    forecast_series = pd.Series(future_preds, index=forecast_index)

    # Grafik
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series, label="Gerçek Seri")
    ax.plot(forecast_series.index, forecast_series.values, label="LSTM Tahmin", color="purple")
    ax.legend()
    st.pyplot(fig)

    # Tahmin tablosu
    st.dataframe(forecast_series.rename("Forecast"))

    # Metrikler
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)  # squared=False kaldırıldı
    rmse = np.sqrt(mse)                       # RMSE manuel hesaplandı
    mape = (abs((y_test - y_pred) / y_test).mean()) * 100
    st.success(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} | MAPE: {mape:.2f}%")

def run_gru(series, look_back=10, steps=12, epochs=20, batch_size=16):

    # Sequence oluşturma
    def create_sequences(data, look_back):
        X, y = [], []
        for i in range(len(data) - look_back):
            X.append(data[i:(i+look_back)])
            y.append(data[i + look_back])
        return np.array(X), np.array(y)

    values = series.values
    X, y = create_sequences(values, look_back)

    # Train/Test split
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # Model
    model = Sequential()
    model.add(GRU(50, activation="relu", input_shape=(look_back, 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")

    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

    # Test tahmin
    y_pred = model.predict(X_test, verbose=0).flatten()

    # Gelecek forecast
    last_seq = values[-look_back:].reshape(1, look_back, 1)
    future_preds = []
    for _ in range(steps):
        next_val = model.predict(last_seq, verbose=0)[0][0]
        future_preds.append(next_val)
        last_seq = np.append(last_seq[:, 1:, :], [[[next_val]]], axis=1)

    forecast_index = pd.date_range(start=series.index[-1], periods=steps+1, freq="M")[1:]
    forecast_series = pd.Series(future_preds, index=forecast_index)

    # Grafik
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series, label="Gerçek Seri")
    ax.plot(forecast_series.index, forecast_series.values, label="GRU Tahmin", color="brown")
    ax.legend()
    st.pyplot(fig)

    # Tahmin tablosu
    st.dataframe(forecast_series.rename("Forecast"))

    # Metrikler
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)  # squared=False kaldırıldı
    rmse = np.sqrt(mse)                       # RMSE manuel hesaplandı
    mape = (abs((y_test - y_pred) / y_test).mean()) * 100
    st.success(f"MAE: {mae:.3f} | RMSE: {rmse:.3f} | MAPE: {mape:.2f}%")


# ====================================
# Ana Çalıştırıcı
# ====================================
def run():
    st.subheader("📈 Zaman Serisi Analizi ve Forecasting")

    if "data" not in st.session_state:
        st.warning("Lütfen önce veri yükleyin.")
        return

    df = st.session_state["data"]

    # --- DatetimeIndex kontrolü ---
    if not isinstance(df.index, pd.DatetimeIndex):
        st.error("⛔ Bu veri zaman serisi verisi değil. Lütfen datetime index içeren bir veri yükleyin.")
        return

    df, value_col = preprocess_data(df)

    st.success(f"Algılanan değer sütunu: **{value_col}**")
    st.write(df.head())

    st.subheader("🔄 Frekans Dönüşümü")
    user_freq = st.selectbox("Hedef Frekans", ["Günlük", "Haftalık", "Aylık", "Yıllık"])
    freq_map = {"Günlük": "D", "Haftalık": "W", "Aylık": "ME", "Yıllık": "YE"}
    converted_data = resample_data(df, value_col, freq_map[user_freq])
    st.line_chart(converted_data)

    st.subheader("📊 Durağanlık Testi")
    stationary, pval = is_stationary(converted_data)
    if stationary:
        st.success(f"Durağan ✅ (p-value={pval:.3f})")
    else:
        st.warning(f"Durağan Değil ❌ (p-value={pval:.3f})")

    st.subheader("🪄 Zaman Serisi Decomposition")
    model = st.radio("Model", ["additive", "multiplicative"])
    if st.button("Decompose"):
        ts_decompose(converted_data, model=model)

    st.subheader("📐 Hurst Exponent")
    H = hurst_exponent(converted_data)
    if H < 0.48:
        st.info(f"H={H:.3f} → Mean-reverting")
    elif 0.48 <= H <= 0.52:
        st.info(f"H={H:.3f} → Random Walk")
    else:
        st.info(f"H={H:.3f} → Trendy (Persistent)")

    st.subheader("🔮 Forecasting")
    model_choice = st.selectbox("Tahmin Modeli", ["ARIMA", "Prophet", "SARIMAX", "TES", "LSTM", "GRU"])

    if model_choice == "ARIMA":
        p = st.slider("p (AR)", 0, 5, 1)
        d = st.slider("d (Fark)", 0, 2, 1)
        q = st.slider("q (MA)", 0, 5, 1)
        steps = st.slider("Tahmin Adımı", 1, 60, 12)
        if st.button("ARIMA Tahmini"):
            run_arima(converted_data, (p, d, q), steps)

    elif model_choice == "Prophet":
        steps = st.slider("Tahmin Periyodu", 1, 60, 12)
        freq = st.radio("Frekans", ["D", "W", "M", "Y"], index=2, horizontal=True)
        if st.button("Prophet Tahmini"):
            run_prophet(converted_data, steps, freq)

        # ---------------- SARIMAX ----------------
    elif model_choice == "SARIMAX":
        st.markdown("**Order Parametreleri**")
        p = st.slider("p (AR)", 0, 5, 1)
        d = st.slider("d (Fark)", 0, 2, 1)
        q = st.slider("q (MA)", 0, 5, 1)

        st.markdown("**Seasonal Order Parametreleri**")
        P = st.slider("P (AR)", 0, 5, 1)
        D = st.slider("D (Fark)", 0, 2, 1)
        Q = st.slider("Q (MA)", 0, 5, 1)
        s = st.number_input("Mevsimsellik Periyodu (s)", min_value=1, value=12)

        steps = st.slider("Tahmin Adımı", 1, 60, 12)
        if st.button("SARIMAX Tahmini"):
            run_sarimax(converted_data, order=(p, d, q), seasonal_order=(P, D, Q, s), steps=steps)

        # ---------------- TES ----------------
    elif model_choice == "TES":
        trend = st.radio("Trend", ["add", "mul"])
        seasonal = st.radio("Mevsimsellik", ["add", "mul"])
        seasonal_periods = st.number_input("Sezon Periyodu", min_value=2, value=12)
        steps = st.slider("Tahmin Adımı", 1, 60, 12)
        if st.button("TES Tahmini"):
            run_tes(converted_data, periods=steps, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)

    # ---------------- LSTM ----------------
    elif model_choice == "LSTM":
        st.markdown("**Model Parametreleri**")
        look_back = st.slider("Look Back", 1, 50, 10)
        epochs = st.slider("Epochs", 1, 100, 20)
        batch_size = st.slider("Batch Size", 1, 128, 16)
        steps = st.slider("Tahmin Adımı", 1, 60, 12)

        if st.button("LSTM Tahmini"):
            run_lstm(converted_data, look_back=look_back, steps=steps, epochs=epochs, batch_size=batch_size)

    # ---------------- GRU ----------------
    elif model_choice == "GRU":
        st.markdown("**Model Parametreleri**")
        look_back = st.slider("Look Back", 1, 50, 10)
        epochs = st.slider("Epochs", 1, 100, 20)
        batch_size = st.slider("Batch Size", 1, 128, 16)
        steps = st.slider("Tahmin Adımı", 1, 60, 12)

        if st.button("GRU Tahmini"):
            run_gru(converted_data, look_back=look_back, steps=steps, epochs=epochs, batch_size=batch_size)
