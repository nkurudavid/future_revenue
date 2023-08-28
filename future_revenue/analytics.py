import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def forecast_revenue(history_data):
    # Convert sales data to a pandas DataFrame
    df = pd.DataFrame(list(history_data.values('date', 'sales_amount')))
    df['date'] = pd.to_datetime(df['date'])

    # Set 'date' as the index
    df.set_index('date', inplace=True)

    # Perform exponential smoothing for forecasting
    model = ExponentialSmoothing(df['sales_amount'], trend='add', seasonal='add', seasonal_periods=12)
    fitted_model = model.fit()

    # Forecast future revenue
    future_dates = pd.date_range(start=df.index[-1], periods=12, freq='M')
    forecasted_revenue = fitted_model.forecast(steps=12)

    # Create a dictionary of predicted revenue for each future month
    predicted_revenue = {str(date): revenue for date, revenue in zip(future_dates, forecasted_revenue)}

    return predicted_revenue
