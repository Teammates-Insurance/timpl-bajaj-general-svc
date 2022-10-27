import re
from fuzzywuzzy import fuzz, process
import pandas as pd

TARGET_FILE_vehicle = "./vehicle_master.xls"

pattern = re.compile(r"\s+")
vehicle_df = pd.DataFrame()


def trim_all_columns(df):
    def trim_strings(x):
        return x.strip() if isinstance(x, str) else x

    return df.applymap(trim_strings)


def get_vehicle_details(mProfile, type):
    global vehicle_df

    make = mProfile.get("make")
    fuel = mProfile.get("fuelType").lower()
    vehicleId = mProfile.get("vehicleId")
    cc = mProfile.get("cc")
    model = mProfile.get("model").lower()
    variant = mProfile.get("variant").lower()
    if vehicle_df.empty:
        vehicle_df = pd.read_excel(TARGET_FILE_vehicle, index_col=False)
        vehicle_df = trim_all_columns(vehicle_df.astype(str))

    df = vehicle_df

    df = df.loc[df["CATEGORY"].str.lower() == type.lower()]
    df = df[df["fuel"].str.lower() == fuel[0]]
    df = df[(df["vehiclemake"].str.lower() == make.lower())]

    model = process.extractOne(
        model.lower(), df["vehiclemodel"].str.lower(), scorer=fuzz.token_sort_ratio
    )
    df = df[(df["vehiclemodel"].str.lower() == model[0].lower())]

    variant = process.extract(
        variant.lower(), df["vehiclesubtype"].str.lower(), scorer=fuzz.token_sort_ratio
    )

    if variant[0][1] >= 60:
        df = df[(df["vehiclesubtype"].str.lower() == variant[0][0].lower())]
    else:
        return False, {"error": True, "error_message": "Vehicle details not found"}

    if not df.empty:
        return True, df.iloc[0].to_dict()
    else:
        return False, {"error": True, "error_message": "Vehicle details not found"}
