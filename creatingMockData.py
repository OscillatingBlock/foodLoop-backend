import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# Set a seed for reproducibility
np.random.seed(42)

# Number of NGOs
num_ngos = 5

# Number of days to simulate (around 3 months)
num_days = 90

# Create a list of NGO IDs
ngo_ids = list(range(1, num_ngos + 1))

# Generate dates
start_date = pd.to_datetime("2025-01-01")
dates = pd.date_range(start=start_date, periods=num_days)

# Create an empty list to store data
data = []

# Simulate irregular requests for each NGO
for ngo_id in ngo_ids:
    # Number of requests for this NGO over the period (can vary)
    num_requests = np.random.randint(15, 30)

    # Randomly select dates for requests
    request_dates = np.random.choice(dates, size=num_requests, replace=False)
    request_dates.sort()

    # Generate random quantities for each request
    quantities = np.random.uniform(50, 300, size=num_requests)

    for date, quantity in zip(request_dates, quantities):
        data.append({"ngo_id": ngo_id, "request_date": date, "quantity": quantity})

# Create the DataFrame
df = pd.DataFrame(data)
df = df.sort_values(["ngo_id", "request_date"]).reset_index(drop=True)

print(df)
print("\nShape of the DataFrame:", df.shape)
print("\nNumber of unique NGOs:", df["ngo_id"].nunique())
print("\nRange of dates:", df["request_date"].min(), "to", df["request_date"].max())


def train_model(df):
    # Todo Train the model
    df["request_date"] = pd.to_datetime(df["request_date"])

    # Resample to weekly (sum of requests per week)
    df_weekly_wide = (
        df.groupby("ngo_id")
        .apply(lambda x: x.set_index("request_date").resample("W-Mon")["quantity"].sum())
    )
    df_weekly = df_weekly_wide.reset_index().melt(
        id_vars='ngo_id',
        value_vars=[col for col in df_weekly_wide.columns],
        var_name='request_date',
        value_name='weekly_request'
    )
    df_weekly = df_weekly.sort_values(["ngo_id", "request_date"])
    df_weekly = df_weekly[df_weekly['weekly_request'].notna()] # Remove weeks with no requests

    # Create lagged features (previous week's request)
    df_weekly["last_week_request"] = df_weekly.groupby("ngo_id")[
        "weekly_request"
    ].shift(1)

    # Create target variable (next week's request)
    df_weekly["next_week_request"] = df_weekly.groupby("ngo_id")[
        "weekly_request"
    ].shift(-1)

    df_weekly = df_weekly.dropna()

    # Encode NGO IDs
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoded_ngo_ids = encoder.fit_transform(df_weekly[["ngo_id"]])
    encoded_df_weekly = pd.concat(
        [
            df_weekly.drop("ngo_id", axis=1).reset_index(drop=True),
            pd.DataFrame(
                encoded_ngo_ids,
                columns=[f"ngo_{i}" for i in range(encoded_ngo_ids.shape[1])],
            ),
        ],
        axis=1,
    )

    # Separate features and target
    X_weekly = encoded_df_weekly[
        ["last_week_request"]
        + [col for col in encoded_df_weekly.columns if col.startswith("ngo_")]
    ]
    y_weekly = encoded_df_weekly["next_week_request"]

    # Split and train (as before)
    X_train_weekly, X_test_weekly, y_train_weekly, y_test_weekly = train_test_split(
        X_weekly, y_weekly, test_size=0.2, random_state=42
    )
    model_weekly = LinearRegression()
    model_weekly.fit(X_train_weekly, y_train_weekly)

    return model_weekly, encoder


def predict_demand(model, encoder, historical_df, ngo_id, current_date, all_trained_ngo_ids):
    """
    Predicts the food demand for a given NGO for the week following the current_date.

    Args:
        model: The trained linear regression model.
        encoder: The fitted OneHotEncoder.
        historical_df: The DataFrame containing historical food request data.
        ngo_id: The ID of the NGO for which to predict.
        current_date: The last date for which you have request data (pd.Timestamp).
        all_trained_ngo_ids: A list of all unique NGO IDs that the encoder was trained on.

    Returns:
        The predicted food demand for the following week.
    """

    # Filter historical data for the specific NGO
    ngo_history = historical_df[historical_df["ngo_id"] == ngo_id].copy()
    ngo_history["request_date"] = pd.to_datetime(ngo_history["request_date"])

    # Resample to weekly (sum of requests per week)
    ngo_weekly = (
        ngo_history.set_index("request_date")
        .resample("W-Mon")["quantity"]
        .sum()
        .reset_index()
    )
    ngo_weekly = ngo_weekly.rename(columns={"quantity": "weekly_request"})
    ngo_weekly = ngo_weekly.sort_values("request_date")

    # Find the weekly request for the current week (the week ending on or after current_date)
    current_week_start = pd.to_datetime(current_date) - pd.Timedelta(
        days=current_date.dayofweek
    )
    current_week_data = ngo_weekly[ngo_weekly["request_date"] == current_week_start]

    if current_week_data.empty:
        print(
            f"Warning: No data found for NGO {ngo_id} for the week starting {current_week_start}."
        )
        return None  # Or return a default/fallback prediction

    last_week_request = current_week_data["weekly_request"].values[0]

    # Encode the NGO ID
    encoded_ngo = encoder.transform(pd.DataFrame([ngo_id], columns=["ngo_id"]))

    # Create the prediction DataFrame with the features
    prediction_data = pd.DataFrame(
        {
            "last_week_request": [last_week_request],
            **{
                f"ngo_{i}": encoded_ngo[0][i] if i < encoded_ngo.shape[1] else 0
                for i in range(len(all_trained_ngo_ids))
            },
        }
    )

    # Ensure the order of columns in prediction_data matches the order in X_weekly
    prediction_data = prediction_data[
        ["last_week_request"] + [f"ngo_{i}" for i in range(len(all_trained_ngo_ids))]
    ]

    # Make the prediction
    predicted_demand = model.predict(prediction_data)
    return predicted_demand[0]


model_weekly, encoder = train_model(df.copy())


def get_trained_ngo_ids(encoder):
    categories = encoder.categories_[0]
    trained_ids = [int(cat) for cat in categories]
    trained_ids.sort()
    return trained_ids

all_trained_ngo_ids = get_trained_ngo_ids(encoder)

# Example usage:
current_prediction_date = pd.to_datetime("2025-03-24")  # Changed prediction date
num_ngos = df["ngo_id"].nunique()  # Get the number of NGOs from the data

for ngo_id_to_predict in range(1, num_ngos + 1):
    prediction = predict_demand(
        model_weekly,
        encoder,
        df.copy(),
        ngo_id_to_predict,
        current_prediction_date,
        all_trained_ngo_ids,
    )
    if prediction is not None:
        print(
            f"Predicted food demand for NGO {ngo_id_to_predict} for the week starting {current_prediction_date + pd.Timedelta(days=7)}: {prediction:.2f}"
        )
