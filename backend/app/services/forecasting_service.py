# import pandas as pd
# import numpy as np

# def forecast_demand(df: pd.DataFrame, periods: int = 14):
#     demand = df.groupby("date")["demand"].sum()

#     mean = demand.mean()
#     std = demand.std()

#     future_dates = pd.date_range(
#         start=demand.index.max(),
#         periods=periods + 1,
#         freq="D"
#     )[1:]

#     forecast = np.random.normal(mean, std, size=periods)

#     return future_dates, forecast, forecast - std, forecast + std

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# -------------------------------
# Feature Engineering
# -------------------------------
def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

    df["lag_1"] = df["demand"].shift(1)
    df["lag_7"] = df["demand"].shift(7)
    df["rolling_7"] = df["demand"].rolling(7).mean()
    df["rolling_14"] = df["demand"].rolling(14).mean()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    return df.dropna()

# -------------------------------
# ARIMA Forecast
# -------------------------------
def forecast_arima(df: pd.DataFrame, horizon: int) -> dict:
    df = df.sort_values("date")
    if len(df) < 10:
        raise ValueError("Not enough data points for ARIMA forecast (min 10)")

    series = df.groupby("date")["demand"].sum().sort_index()
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
        start=df["date"].iloc[-1] + pd.Timedelta(days=1),
        periods=horizon
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
    df = df.sort_values("date")
    if len(df) < 30:
        raise ValueError("Not enough data points for XGBoost forecast (min 30)")

    df_feat = create_features(df)

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
    last_row = df_feat.iloc[-1:].copy()
    last_date = pd.to_datetime(df["date"].iloc[-1])
    forecasts = []

    for _ in range(horizon):
        X_last = last_row[features]
        pred = model.predict(X_last)[0]
        forecasts.append(pred)

        # Update lags
        last_row["lag_7"] = last_row["lag_1"]
        last_row["lag_1"] = pred
        last_row["rolling_7"] = np.mean(forecasts[-7:])
        last_row["rolling_14"] = np.mean(forecasts[-14:])
        last_date = last_date + pd.Timedelta(days=1)
        last_row["day_of_week"] = last_date.dayofweek
        last_row["month"] = last_date.month

    # Confidence intervals using residuals
    residuals = y_test - y_pred
    sigma = residuals.std()

    lower = [f - 1.96 * sigma for f in forecasts]
    upper = [f + 1.96 * sigma for f in forecasts]

    future_dates = pd.date_range(
        start=df["date"].iloc[-1] + pd.Timedelta(days=1),
        periods=horizon
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
