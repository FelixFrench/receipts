# Provides a function to get the most recent 24h of energy consumption available on the Octopus Energy API

import requests
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

def get_energy_consumption(key, product, postcode, mpan, msn) -> str:
    """
    Creates a formatted block of text giving information on recent energy consumption for one metering point
    """
    
    # ---------- Get Grid Supply Point code from postcode ----------
    def get_gsp_code(postcode:str)->str:
        """
        Finds the Octopus "grid supply point code" for the given postcode
        """

        url = f"https://api.octopus.energy/v1/industry/grid-supply-points/?postcode={postcode}"
        (r := requests.get(url)).raise_for_status()

        results = r.json().get("results")
        if not results:
            raise Exception("No grid supply point results returned")
        
        group_id = results[0].get("group_id")
        if not group_id:
            raise ValueError("Missing group_id in grid supply point response")

        return group_id.lstrip("_")
    
    gsp_code = get_gsp_code(postcode)
    
    # Form tariff identifier string
    single_tariff = f"E-1R-{product}-{gsp_code}"
    dual_tariff = f"E-2R-{product}-{gsp_code}"
    
    
    # ---------- Get rates ----------
    def get_rate(tariff, rate:str):
        """
        Gets the cost in GBP of a given rate for a given tarriff and product
        """

        url = f"https://api.octopus.energy/v1/products/{product}/electricity-tariffs/{tariff}/{rate}/"
        (r := requests.get(url)).raise_for_status()

        results = r.json().get("results")
        if not results:
            raise Exception("No energy rate results returned")
        
        value = results[0].get("value_inc_vat")
        if value is None:
            raise Exception("Energy rate results not as expected")
        
        return float(value) / 100
    
    single_rate = get_rate(single_tariff, "standard-unit-rates")
    single_standing_charge = get_rate(single_tariff, "standing-charges")

    dual_day_rate = get_rate(dual_tariff, "day-unit-rates")
    dual_night_rate = get_rate(dual_tariff, "night-unit-rates")
    dual_standing_charge = get_rate(dual_tariff, "standing-charges")

    #print(single_rate, single_standing_charge)
    #print(dual_day_rate, dual_night_rate, dual_standing_charge)


    # ---------- Get consumption data from meter ----------
    def get_last_24h_consumption():
        """
        Requests the most recent available 24 hours (48x 30min readings) of consumption data
        """

        url = f"https://api.octopus.energy/v1/electricity-meter-points/{mpan}/meters/{msn}/consumption/"
        url += "?page_size=48&order_by=-period"

        (r := requests.get(url, auth=(key, ''))).raise_for_status()
        return r.json().get('results', [])
    
    consumption_data = get_last_24h_consumption()


    # ---------- Process data ----------
    timeseries_df = pd.DataFrame(consumption_data)
    timeseries_df['interval_start'] = pd.to_datetime(timeseries_df['interval_start'], utc=True)
    start_time = timeseries_df['interval_start'].min()
    end_time = timeseries_df['interval_start'].max() + timedelta(minutes=30)

    # Extract date and time components
    timeseries_df['date'] = timeseries_df['interval_start'].dt.normalize()
    to_unix = lambda x: pd.to_datetime(x.total_seconds(), unit='s', origin='unix')
    timeseries_df['time'] = to_unix((timeseries_df['interval_start'] - timeseries_df['date']).dt)

    # Define the range of the night rate period - these are in UTC like everything else
    night_start = to_unix(pd.Timedelta("00:30:00"))
    day_start = to_unix(pd.Timedelta("07:30:00"))
    day_mask = (timeseries_df['time'] >= day_start) | (timeseries_df['time'] < night_start)
    night_mask = (timeseries_df['time'] < day_start) & (timeseries_df['time'] >= night_start)

    # Calculate usage during day and night periods
    day_usage = timeseries_df[day_mask]['consumption'].sum()
    night_usage = timeseries_df[night_mask]['consumption'].sum()
    total_usage = day_usage + night_usage
    day_usage_percent = day_usage / total_usage * 100
    night_usage_percent = night_usage / total_usage * 100
    
    # Calculate cost in £ for both the single-rate tariff and dual-rate tariff
    single_charge = (day_usage + night_usage) * single_rate
    single_total_charge = single_charge + single_standing_charge
    dual_day_charge = day_usage * dual_day_rate
    dual_night_charge = night_usage * dual_night_rate
    dual_total_charge = dual_day_charge + dual_night_charge + dual_standing_charge
    single_dual_difference = single_total_charge - dual_total_charge

    comparison_string = f"With a single rate tariff, this would have cost £{single_total_charge:.2f} (+£{single_dual_difference:.2f})"

    table = [
        ["Day",         f"{day_usage:.2f} ({day_usage_percent:.0f}%)",        f"£{dual_day_charge:.2f}"],
        ["Night",       f"{night_usage:.2f} ({night_usage_percent:.0f}%)",    f"£{dual_night_charge:.2f}"],
        ["Standing",    "",                                                 f"£{dual_standing_charge:.2f}"],
        ["Total",       f"{total_usage:.2f}",                               f"£{dual_total_charge:.2f}"]
    ]

    data_string = f"From {datetime.strftime(start_time, '%H:%M:%S %d/%m/%Y')}"
    data_string += f"\nTo {datetime.strftime(end_time, '%H:%M:%S %d/%m/%Y')}"
    data_string += "\n" + tabulate(table, headers=[None, "Usage [kWh]", "Charge"])
    data_string += "\n\n" + comparison_string

    return (data_string, "body")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv("../.env")

    ENERGY_API_KEY = os.getenv("ENERGY_API_KEY")
    ENERGY_PRODUCT = os.getenv("ENERGY_PRODUCT")
    POSTCODE = os.getenv("POSTCODE")
    ENERGY_MPAN = os.getenv("ENERGY_MPAN")
    ENERGY_MSN = os.getenv("ENERGY_MSN")

    energy_data = get_energy_consumption(
        ENERGY_API_KEY, ENERGY_PRODUCT, POSTCODE,
        ENERGY_MPAN, ENERGY_MSN
    )

    print("\n\n")
    print(energy_data[0])
    print("\n\n")