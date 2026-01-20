# Provides a function to get the most recent 24h of energy consumption available on the Octopus Energy API

import requests
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

def get_energy_consumption(key, product, tariff, mpan, msn) -> str:
    
    # ---------- Get rates ----------
    def get_rate(rate):
        url = f"https://api.octopus.energy/v1/products/{product}/electricity-tariffs/{tariff}/{rate}/"
        (r := requests.get(url)).raise_for_status()
        results = r.json().get("results")
        if results is None:
            raise Exception("No energy rate results returned")
        
        value = results[0].get("value_inc_vat")
        if results is None:
            raise Exception("Energy rate results not as expected")
        
        return float(value) / 100
    
    day_rate = get_rate("day-unit-rates")
    night_rate = get_rate("night-unit-rates")
    standing_charge = get_rate("standing-charges")
    #print(day_rate, night_rate, standing_charge)


    # ---------- Get consumption data from meter ----------
    def get_last_24h_consumption():
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

    night_start = to_unix(pd.Timedelta("00:30:00"))
    day_start = to_unix(pd.Timedelta("07:30:00"))

    day_mask = (timeseries_df['time'] >= day_start) | (timeseries_df['time'] < night_start)
    night_mask = (timeseries_df['time'] < day_start) & (timeseries_df['time'] >= night_start)

    day_usage = timeseries_df[day_mask]['consumption'].sum()
    night_usage = timeseries_df[night_mask]['consumption'].sum()
    total_usage = day_usage + night_usage

    day_charge = day_usage * day_rate
    night_charge = night_usage * night_rate
    total_charge = day_charge + night_charge + standing_charge

    table = [
        ["Day",         f"{day_usage:.2f}",     f"£{day_charge:.2f}"],
        ["Night",       f"{night_usage:.2f}",   f"£{night_charge:.2f}"],
        ["Standing",    "",                     f"£{standing_charge:.2f}"],
        ["Total",       f"{total_usage:.2f}",   f"£{total_charge:.2f}"]
    ]

    data_string = f"From {datetime.strftime(start_time, "%H:%M:%S %d/%m/%Y")}"
    data_string += f"\nTo {datetime.strftime(end_time, "%H:%M:%S %d/%m/%Y")}"
    data_string += "\n" + tabulate(table, headers=[None, "Usage [kWh]", "Charge"])

    return data_string


if __name__ == "__main__":
    from Secrets import energy_api_key, energy_product, energy_tariff, energy_mpan, energy_msn
    energy_data = get_energy_consumption(energy_api_key, energy_product, energy_tariff, energy_mpan, energy_msn)


    print("\n\n")
    print(energy_data)
    print("\n\n")