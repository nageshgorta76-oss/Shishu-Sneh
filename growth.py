import pandas as pd


def reference_growth_data():
    return pd.DataFrame(
        {
            "month": [1, 2, 3, 4, 5, 6],
            "weight": [3.2, 4.1, 5.0, 5.8, 6.2, 6.8],
            "height": [50, 54, 57, 60, 63, 66],
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

    return data.sort_values(by=["age", "id"]).reset_index(drop=True)
