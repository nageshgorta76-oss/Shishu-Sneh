import pandas as pd


def reference_growth_data():
    return pd.DataFrame(
        {
            "month": [0, 1, 2, 3, 4, 5, 6, 9, 12],
            "weight": [3.2, 4.2, 5.1, 5.8, 6.4, 6.9, 7.3, 8.2, 9.0],
            "height": [49.9, 54.7, 58.4, 61.4, 63.9, 65.9, 67.6, 72.0, 75.7],
        }
    )


def growth_data(current_weight):
    data = reference_growth_data().copy()
    data.loc[data.index[-1], "weight"] = current_weight
    return data


def build_growth_history(records, baby_name=None):
    columns = ["id", "name", "age", "weight", "height"]
    data = pd.DataFrame(records, columns=columns)

    if data.empty:
        return data

    if baby_name:
        data = data[data["name"] == baby_name]

    data = data.dropna(subset=["age", "weight", "height"])
    data["age"] = pd.to_numeric(data["age"], errors="coerce")
    data["weight"] = pd.to_numeric(data["weight"], errors="coerce")
    data["height"] = pd.to_numeric(data["height"], errors="coerce")
    data = data.dropna(subset=["age", "weight", "height"])

    return data.sort_values(by=["age", "id"]).reset_index(drop=True)
