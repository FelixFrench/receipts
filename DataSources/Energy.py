# Provides a function to get the most recent 24h of energy consumption available on the Octopus Energy API
import requests
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta
from typing import TypedDict, cast, assert_never
from blocks import Block, ImageBlock, TextBlock

class ConsumptionReading(TypedDict):
    consumption: float      # kWh
    interval_start: str     # ISO 8601 timestamp
    interval_end: str


def get_gsp_code(postcode: str) -> str:
    """
    Finds the Octopus "grid supply point code" for the given postcode
    """

    url = f"https://api.octopus.energy/v1/industry/grid-supply-points/?postcode={postcode}"
    (r := requests.get(url)).raise_for_status()

    results = r.json().get("results")
    if not results:
        raise ValueError(f"No grid supply point results returned for postcode {postcode}")
    
    group_id = results[0].get("group_id")
    if not group_id:
        raise ValueError(f"Missing group_id in grid supply point response for postcode {postcode}")
    
    if not isinstance(group_id, str):
        raise ValueError(f"Octopus API returned invalid group_id {group_id} for postcode {postcode}")

    return group_id.lstrip("_")


def get_rate(product:str, tariff: str, rate: str) -> float:
    """
    Gets the cost in GBP of a given rate for a given tariff and product
    """

    url = f"https://api.octopus.energy/v1/products/{product}/electricity-tariffs/{tariff}/{rate}/"
    (r := requests.get(url)).raise_for_status()

    results = r.json().get("results")
    if not results:
        raise ValueError(f"No energy rate results returned for {tariff}/{rate}")
    
    value = results[0].get("value_inc_vat")
    if value is None:
        raise ValueError(f"Energy rate results malformed for {tariff}/{rate}")
    
    return float(value) / 100


def get_last_24h_consumption(mpan:str, msn: str, key: str) -> list[ConsumptionReading]:
    """
    Requests the most recent available 24 hours (48x 30min readings) of consumption data
    """

    url = f"https://api.octopus.energy/v1/electricity-meter-points/{mpan}/meters/{msn}/consumption/"
    url += "?page_size=48&order_by=-period"

    (r := requests.get(url, auth=(key, ''))).raise_for_status()

    consumption = r.json().get('results')
    if not isinstance(consumption, list):
        raise ValueError("Octopus API returned invalid consumption data")
    
    return cast(list[ConsumptionReading], consumption)


def get_energy_consumption(key: str, product: str, postcode: str, mpan: str, msn: str) -> list[Block]:
    """
    Creates a formatted block of text giving information on recent energy consumption for one metering point
    """
    
    # ---------- Get Grid Supply Point code from postcode ----------
    gsp_code = get_gsp_code(postcode)
    
    # Form tariff identifier string
    single_tariff = f"E-1R-{product}-{gsp_code}"
    dual_tariff = f"E-2R-{product}-{gsp_code}"
    
    
    # ---------- Get rates ----------
    single_rate = get_rate(product, single_tariff, "standard-unit-rates")
    single_standing_charge = get_rate(product, single_tariff, "standing-charges")

    dual_day_rate = get_rate(product, dual_tariff, "day-unit-rates")
    dual_night_rate = get_rate(product, dual_tariff, "night-unit-rates")
    dual_standing_charge = get_rate(product, dual_tariff, "standing-charges")


    # ---------- Get consumption data from meter ----------
    consumption_data = get_last_24h_consumption(mpan, msn, key)


    # ---------- Process data ----------
    timeseries_df = pd.DataFrame(consumption_data)
    timeseries_df['interval_start'] = pd.to_datetime(timeseries_df['interval_start'], utc=True)
    start_time = timeseries_df['interval_start'].min()
    end_time = timeseries_df['interval_start'].max() + timedelta(minutes=30)

    # Extract date and time components
    date = timeseries_df['interval_start'].dt.normalize()
    time_of_day = timeseries_df['interval_start'] - date   # Series of Timedeltas
    night_start = pd.Timedelta("00:30:00")
    day_start = pd.Timedelta("07:30:00")
    night_mask = (time_of_day >= night_start) & (time_of_day < day_start)
    day_mask = ~night_mask


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

    signed_difference_str = ("+" if single_dual_difference >= 0 else "-") + f"£{abs(single_dual_difference):.2f}"
    comparison_string = f"With a single rate tariff, this would have cost £{single_total_charge:.2f} ({signed_difference_str})"

    table = [
        ["Day",         f"{day_usage:.2f} ({day_usage_percent:.0f}%)",        f"£{dual_day_charge:.2f}"],
        ["Night",       f"{night_usage:.2f} ({night_usage_percent:.0f}%)",    f"£{dual_night_charge:.2f}"],
        ["Standing",    "",                                                 f"£{dual_standing_charge:.2f}"],
        ["Total",       f"{total_usage:.2f}",                               f"£{dual_total_charge:.2f}"]
    ]

    data_string = f"From {start_time.strftime('%H:%M:%S %d/%m/%Y')}"
    data_string += f"\nTo {end_time.strftime('%H:%M:%S %d/%m/%Y')}"
    data_string += "\n" + tabulate(table, headers=["", "Usage [kWh]", "Charge"])
    data_string += "\n\n" + comparison_string

    blocks: list[Block] = []
    blocks.append(TextBlock(data_string))

    return blocks


if __name__ == "__main__":
    from config import load_config

    cfg = load_config()

    energy_blocks = get_energy_consumption(
        cfg.energy_api_key, cfg.energy_product, cfg.postcode,
        cfg.energy_mpan, cfg.energy_msn
    )

    print("\n\n")
    for block in energy_blocks:
        match block:
            case ImageBlock():
                print("<image>")
            case TextBlock():
                print(block.text)
            case _:
                assert_never(block)
    print("\n\n")
