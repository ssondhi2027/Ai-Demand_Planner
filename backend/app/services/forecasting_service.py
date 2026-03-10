import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# -------------------------------
# Feature Engineering
# -------------------------------
def _aggregate_by_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return (
        df.groupby("date", as_index=False)["demand"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["lag_1"] = df["demand"].shift(1)
    df["lag_7"] = df["demand"].shift(7)
    df["rolling_7"] = df["demand"].rolling(7).mean()
    df["rolling_14"] = df["demand"].rolling(14).mean()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    return df.dropna()

def _build_feature_row(history: list[float], next_date: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "lag_1": history[-1],
                "lag_7": history[-7],
                "rolling_7": float(np.mean(history[-7:])),
                "rolling_14": float(np.mean(history[-14:])),
                "day_of_week": next_date.dayofweek,
                "month": next_date.month,
            }
        ]
    )

# -------------------------------
# ARIMA Forecast
# -------------------------------
def forecast_arima(df: pd.DataFrame, horizon: int) -> dict:
    df_agg = _aggregate_by_date(df)
    if len(df_agg) < 10:
        raise ValueError("Not enough data points for ARIMA forecast (min 10)")

    series = df_agg.set_index("date")["demand"].sort_index()
    freq = pd.infer_freq(series.index)
    if freq is None:
        series = series.asfreq("D", fill_value=0)
    else:
        series = series.asfreq(freq)

    model = ARIMA(series, order=(1, 1, 1))
    fitted = model.fit()

    forecast_result = fitted.get_forecast(steps=horizon)
    forecast = forecast_result.predicted_mean
    conf_int = forecast_result.conf_int()

    future_dates = pd.date_range(
        start=series.index[-1] + pd.Timedelta(days=1),
        periods=horizon,
    )

    return {
        "model": "arima",
        "dates": future_dates.astype(str).tolist(),
        "forecast": forecast.tolist(),
        "lower": conf_int.iloc[:, 0].tolist(),
        "upper": conf_int.iloc[:, 1].tolist()
    }

# -------------------------------
# XGBoost Forecast
# -------------------------------
def forecast_xgboost(df: pd.DataFrame, horizon: int) -> dict:
    df_agg = _aggregate_by_date(df)
    if len(df_agg) < 30:
        raise ValueError("Not enough data points for XGBoost forecast (min 30)")

    df_feat = create_features(df_agg)

    features = [
        "lag_1", "lag_7", "rolling_7",
        "rolling_14", "day_of_week", "month"
    ]

    X = df_feat[features]
    y = df_feat["demand"]

    # Train / test split
    split = int(len(df_feat) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        objective="reg:squarederror"
    )

    model.fit(X_train, y_train)

    # Validation metrics
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    # Recursive forecasting
    history = df_agg["demand"].astype(float).tolist()
    last_date = pd.to_datetime(df_agg["date"].iloc[-1])
    forecasts = []

    for _ in range(horizon):
        next_date = last_date + pd.Timedelta(days=1)
        X_last = _build_feature_row(history, next_date)[features]
        pred = model.predict(X_last)[0]
        forecasts.append(pred)

        history.append(pred)
        last_date = next_date

    # Confidence intervals using residuals
    residuals = y_test - y_pred
    sigma = residuals.std()

    lower = [f - 1.96 * sigma for f in forecasts]
    upper = [f + 1.96 * sigma for f in forecasts]

    future_dates = pd.date_range(
        start=df_agg["date"].iloc[-1] + pd.Timedelta(days=1),
        periods=horizon,
    )

    return {
        "model": "xgboost",
        "dates": future_dates.astype(str).tolist(),
        "forecast": forecasts,
        "lower": lower,
        "upper": upper,
        "metrics": {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2)
        }
    }

# -------------------------------
# Unified Service Entry Point
# -------------------------------
def forecast_demand(
    df: pd.DataFrame,
    horizon: int = 30,
    model: str = "arima"
) -> dict:
    """
    Unified forecasting interface used by API layer
    """
    if model == "arima":
        return forecast_arima(df, horizon)
    elif model == "xgboost":
        return forecast_xgboost(df, horizon)
    else:
        raise ValueError(f"Unsupported model: {model}")
