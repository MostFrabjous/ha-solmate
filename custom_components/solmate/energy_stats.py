"""Historical energy statistics injected from the SolMate logs route."""
import logging
from datetime import datetime, timedelta, timezone

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SolmateCoordinator

_LOGGER = logging.getLogger(__name__)

BACKFILL_DAYS = 30

# statistic_key -> (display name, unit)
ENERGY_STATS: dict[str, tuple[str, str]] = {
    "pv_energy": ("SolMate PV Energy", "kWh"),
    "inject_energy": ("SolMate Injection Energy", "kWh"),
    "battery_charge_energy": ("SolMate Battery Charge", "kWh"),
    "battery_discharge_energy": ("SolMate Battery Discharge", "kWh"),
}

REF_STAT_ID = f"{DOMAIN}:pv_energy"


def _logs_to_energy(logs: list[dict]) -> dict[str, list[tuple[datetime, float]]]:
    result: dict[str, list] = {k: [] for k in ENERGY_STATS}
    for entry in logs:
        start_str = entry.get("start")
        if not start_str:
            continue
        dt = datetime.fromisoformat(start_str).replace(tzinfo=timezone.utc)

        def avg(key: str) -> float:
            vals = entry.get(key) or [0]
            return sum(vals) / len(vals)

        flow = avg("battery_flow")
        result["pv_energy"].append((dt, max(0.0, avg("pv_power")) / 1000))
        result["inject_energy"].append((dt, max(0.0, avg("inject_power")) / 1000))
        result["battery_charge_energy"].append((dt, max(0.0, flow) / 1000))
        result["battery_discharge_energy"].append((dt, max(0.0, -flow) / 1000))
    return result


async def async_update_energy_stats(
    hass: HomeAssistant, coordinator: SolmateCoordinator
) -> None:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    ref_last = await get_instance(hass).async_add_executor_job(
        get_last_statistics, hass, 1, REF_STAT_ID, True, {"sum"}
    )

    if ref_last and REF_STAT_ID in ref_last:
        last_start = datetime.fromtimestamp(
            ref_last[REF_STAT_ID][0]["start"], tz=timezone.utc
        )
        fetch_start = last_start + timedelta(hours=1)
    else:
        fetch_start = now - timedelta(days=BACKFILL_DAYS)

    if fetch_start >= now:
        _LOGGER.debug("SolMate energy stats are up to date")
        return

    _LOGGER.debug("Fetching SolMate logs %s → %s", fetch_start, now)
    try:
        logs = await coordinator.async_fetch_logs(fetch_start, now)
    except Exception as err:
        _LOGGER.error("Failed to fetch SolMate logs: %s", err)
        return

    per_metric = _logs_to_energy(logs)

    for stat_key, (stat_name, unit) in ENERGY_STATS.items():
        statistic_id = f"{DOMAIN}:{stat_key}"

        last = await get_instance(hass).async_add_executor_job(
            get_last_statistics, hass, 1, statistic_id, True, {"sum"}
        )
        running_sum = 0.0
        if last and statistic_id in last:
            running_sum = last[statistic_id][0].get("sum") or 0.0

        entries = sorted(per_metric.get(stat_key, []))
        if not entries:
            continue

        stats = []
        for dt, kwh in entries:
            running_sum += kwh
            stats.append(StatisticData(start=dt, sum=running_sum, state=kwh))

        metadata = StatisticMetaData(
            has_mean=False,
            has_sum=True,
            name=stat_name,
            source=DOMAIN,
            statistic_id=statistic_id,
            unit_of_measurement=unit,
        )
        async_add_external_statistics(hass, metadata, stats)
        _LOGGER.debug("Injected %d entries for %s", len(stats), stat_key)
