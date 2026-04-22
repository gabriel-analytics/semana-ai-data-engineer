"""
generate_doordash.py
--------------------
Generates a synthetic DoorDash A/B test dataset with intentional
data quality issues for analytical exercises.

Output: doordash_raw.csv (same directory as this script)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

RNG = np.random.default_rng(42)
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doordash_raw.csv")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
N_ORDERS = 10_000
N_CUSTOMERS = 2_000
N_RESTAURANTS = 150
N_DASHERS = 500

CITIES = [
    "São Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Porto Alegre",
    "Brasília",
]

RESTAURANT_CATEGORIES = [
    "Pizza", "Burger", "Japanese", "Brazilian", "Mexican",
    "Italian", "Chinese", "Healthy", "Dessert", "Seafood",
]

RESTAURANT_NAMES_POOL = [
    "Gourmet Express", "Sabor & Arte", "Urban Kitchen", "Bella Napoli",
    "Tokyo Garden", "Burger Lab", "Verde & Co", "Cantina do Chef",
    "Mar e Terra", "Doce Vida", "Spice Route", "Casa Portuguesa",
    "Forno di Pietra", "Street Eats", "Nikkei House",
]

CUSTOMER_SEGMENTS = ["new", "returning", "vip"]
SEGMENT_WEIGHTS = [0.25, 0.55, 0.20]

# Delivery duration base parameters (minutes)
BASE_MEAN_A = 38.0
AB_MULTIPLIER_B = 0.94  # Group B is ~6% faster


# ---------------------------------------------------------------------------
# Helper generators
# ---------------------------------------------------------------------------

def generate_restaurants(n: int) -> pd.DataFrame:
    """Create a reference table for restaurants."""
    rng = np.random.default_rng(42)
    restaurant_ids = [f"REST_{str(i).zfill(4)}" for i in range(1, n + 1)]
    names = [
        f"{rng.choice(RESTAURANT_NAMES_POOL)} {rng.integers(1, 50)}"
        for _ in range(n)
    ]
    categories = rng.choice(RESTAURANT_CATEGORIES, size=n)
    cities = rng.choice(CITIES, size=n)
    return pd.DataFrame({
        "restaurant_id": restaurant_ids,
        "restaurant_name": names,
        "restaurant_category": categories,
        "restaurant_city": cities,
    })


def generate_customers(n: int) -> pd.DataFrame:
    """Create a reference table for customers."""
    rng = np.random.default_rng(42)
    customer_ids = [f"CUST_{str(i).zfill(5)}" for i in range(1, n + 1)]
    cities = rng.choice(CITIES, size=n)
    segments = rng.choice(CUSTOMER_SEGMENTS, size=n, p=SEGMENT_WEIGHTS)
    return pd.DataFrame({
        "customer_id": customer_ids,
        "customer_city": cities,
        "customer_segment": segments,
    })


def sample_created_at(n_per_month: list[int]) -> list[datetime]:
    """
    Generate timestamps with intentional downward trend across months.
    n_per_month: [jan_count, feb_count, mar_count]
    """
    rng = np.random.default_rng(42)
    timestamps = []
    month_starts = [
        datetime(2025, 1, 1),
        datetime(2025, 2, 1),
        datetime(2025, 3, 1),
    ]
    month_days = [31, 28, 31]  # 2025 is not a leap year

    for month_idx, count in enumerate(n_per_month):
        start = month_starts[month_idx]
        days = month_days[month_idx]
        # Random seconds within the month
        seconds_in_month = days * 24 * 3600
        offsets = rng.integers(0, seconds_in_month, size=count)
        for offset in offsets:
            timestamps.append(start + timedelta(seconds=int(offset)))

    return timestamps


def assign_statuses(created_ats: list[datetime]) -> list[str]:
    """
    Assign order statuses with cancellation rate increasing month to month.
    Jan ~5%, Feb ~8%, Mar ~12%. Remaining: ~2% in_progress, rest delivered.
    """
    rng = np.random.default_rng(42)
    cancel_rates = {1: 0.05, 2: 0.08, 3: 0.12}
    in_progress_rate = 0.02
    statuses = []
    for ts in created_ats:
        month = ts.month
        cancel_rate = cancel_rates[month]
        roll = rng.random()
        if roll < cancel_rate:
            statuses.append("cancelled")
        elif roll < cancel_rate + in_progress_rate:
            statuses.append("in_progress")
        else:
            statuses.append("delivered")
    return statuses


def generate_delivery_duration(ab_group: str, rng: np.random.Generator) -> float:
    """Sample base delivery duration in minutes (log-normal distribution)."""
    mean = BASE_MEAN_A if ab_group == "A" else BASE_MEAN_A * AB_MULTIPLIER_B
    sigma = 8.0  # std deviation in minutes
    # log-normal params
    mu = np.log(mean**2 / np.sqrt(sigma**2 + mean**2))
    s = np.sqrt(np.log(1 + sigma**2 / mean**2))
    duration = rng.lognormal(mean=mu, sigma=s)
    return round(float(np.clip(duration, 10, 90)), 1)


def build_delivery_timestamps(
    created_at: datetime,
    duration_minutes: float,
    status: str,
) -> dict:
    """
    Build the 7 delivery stage timestamps for a single order.
    Returns dict with stage columns and pickup/assigned/delivered fields.
    """
    if status == "cancelled":
        # Cancelled orders: only first 1-2 stages populated
        stage1 = created_at
        stage2 = stage1 + timedelta(seconds=int(RNG.integers(30, 180)))
        return {
            "stage_1_order_placed_at": stage1,
            "stage_2_restaurant_confirmed_at": stage2,
            "stage_3_dasher_assigned_at": None,
            "stage_4_dasher_arrived_restaurant_at": None,
            "stage_5_order_picked_up_at": None,
            "stage_6_dasher_near_customer_at": None,
            "stage_7_delivered_at": None,
            "dasher_assigned_at": None,
            "pickup_at": None,
            "delivered_at": None,
        }

    total_seconds = duration_minutes * 60

    # Proportional time splits across 7 stages (approximate real-world splits)
    splits = np.array([0.0, 0.08, 0.20, 0.38, 0.50, 0.85, 0.97, 1.0])
    # Add small jitter
    jitter = RNG.uniform(-0.01, 0.01, size=len(splits))
    jitter[0] = 0.0
    jitter[-1] = 0.0
    splits = np.clip(splits + jitter, 0.0, 1.0)
    splits = np.sort(splits)

    stage_times = [
        created_at + timedelta(seconds=int(splits[i] * total_seconds))
        for i in range(8)
    ]

    return {
        "stage_1_order_placed_at": stage_times[0],
        "stage_2_restaurant_confirmed_at": stage_times[1],
        "stage_3_dasher_assigned_at": stage_times[2],
        "stage_4_dasher_arrived_restaurant_at": stage_times[3],
        "stage_5_order_picked_up_at": stage_times[4],
        "stage_6_dasher_near_customer_at": stage_times[5],
        "stage_7_delivered_at": stage_times[6],
        "dasher_assigned_at": stage_times[2],
        "pickup_at": stage_times[4],
        "delivered_at": stage_times[6],
    }


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating DoorDash synthetic dataset...")

    # --- Reference tables ---
    restaurants_df = generate_restaurants(N_RESTAURANTS)
    customers_df = generate_customers(N_CUSTOMERS)

    # --- Order volume with downward trend ---
    # Jan: ~4200, Feb: ~3500, Mar: ~2300 (total = 10000)
    n_jan, n_feb, n_mar = 4200, 3500, 2300
    assert n_jan + n_feb + n_mar == N_ORDERS

    created_ats = sample_created_at([n_jan, n_feb, n_mar])

    # Sort by timestamp (natural ordering)
    created_ats.sort()

    # --- Order IDs ---
    order_ids = [f"ORD_{str(i).zfill(6)}" for i in range(1, N_ORDERS + 1)]

    # --- A/B group 50/50 ---
    ab_groups = RNG.choice(["A", "B"], size=N_ORDERS, p=[0.5, 0.5])

    # --- Statuses ---
    statuses = assign_statuses(created_ats)

    # --- Customer and restaurant sampling ---
    customer_indices = RNG.integers(0, N_CUSTOMERS, size=N_ORDERS)
    restaurant_indices = RNG.integers(0, N_RESTAURANTS, size=N_ORDERS)
    dasher_ids_pool = [f"DASH_{str(i).zfill(4)}" for i in range(1, N_DASHERS + 1)]

    # --- Build row by row ---
    rows = []
    for i in range(N_ORDERS):
        order_id = order_ids[i]
        created_at = created_ats[i]
        status = statuses[i]
        ab_group = ab_groups[i]

        cust = customers_df.iloc[customer_indices[i]]
        rest = restaurants_df.iloc[restaurant_indices[i]]

        duration = generate_delivery_duration(ab_group, RNG) if status == "delivered" else None
        stages = build_delivery_timestamps(created_at, duration or 0, status)

        # Dasher assignment (only for delivered/in_progress)
        if status in ("delivered", "in_progress"):
            dasher_id = RNG.choice(dasher_ids_pool)
            delivery_id = f"DEL_{str(i).zfill(6)}"
        else:
            dasher_id = RNG.choice(dasher_ids_pool)  # even cancelled may have been assigned briefly
            delivery_id = f"DEL_{str(i).zfill(6)}"

        total_amount = round(float(RNG.uniform(8.0, 85.0)), 2)

        row = {
            # orders
            "order_id": order_id,
            "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "customer_id": cust["customer_id"],
            "restaurant_id": rest["restaurant_id"],
            "ab_group": ab_group,
            "status": status,
            "total_amount_usd": total_amount,
            # customers
            "customer_city": cust["customer_city"],
            "customer_segment": cust["customer_segment"],
            # restaurants
            "restaurant_name": rest["restaurant_name"],
            "restaurant_category": rest["restaurant_category"],
            "restaurant_city": rest["restaurant_city"],
            # deliveries
            "delivery_id": delivery_id,
            "dasher_id": dasher_id,
            "dasher_assigned_at": stages["dasher_assigned_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["dasher_assigned_at"] else None,
            "pickup_at": stages["pickup_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["pickup_at"] else None,
            "delivered_at": stages["delivered_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["delivered_at"] else None,
            "delivery_duration_minutes": duration,
            # delivery stages
            "stage_1_order_placed_at": stages["stage_1_order_placed_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_1_order_placed_at"] else None,
            "stage_2_restaurant_confirmed_at": stages["stage_2_restaurant_confirmed_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_2_restaurant_confirmed_at"] else None,
            "stage_3_dasher_assigned_at": stages["stage_3_dasher_assigned_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_3_dasher_assigned_at"] else None,
            "stage_4_dasher_arrived_restaurant_at": stages["stage_4_dasher_arrived_restaurant_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_4_dasher_arrived_restaurant_at"] else None,
            "stage_5_order_picked_up_at": stages["stage_5_order_picked_up_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_5_order_picked_up_at"] else None,
            "stage_6_dasher_near_customer_at": stages["stage_6_dasher_near_customer_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_6_dasher_near_customer_at"] else None,
            "stage_7_delivered_at": stages["stage_7_delivered_at"].strftime("%Y-%m-%dT%H:%M:%S") if stages["stage_7_delivered_at"] else None,
            # quality flags (default clean)
            "has_duplicate_flag": False,
            "has_timestamp_issue_flag": False,
            "has_missing_dasher_flag": False,
            "has_outlier_flag": False,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # ---------------------------------------------------------------------------
    # Inject data quality issues
    # ---------------------------------------------------------------------------
    print("Injecting data quality issues...")

    n_total = len(df)

    # 1. Missing dasher (1%) — for delivered orders only to be realistic
    delivered_mask = df["status"] == "delivered"
    delivered_idx = df[delivered_mask].index.tolist()
    n_missing_dasher = int(n_total * 0.01)
    missing_dasher_idx = RNG.choice(delivered_idx, size=n_missing_dasher, replace=False)
    df.loc[missing_dasher_idx, "dasher_id"] = None
    df.loc[missing_dasher_idx, "dasher_assigned_at"] = None
    df.loc[missing_dasher_idx, "stage_3_dasher_assigned_at"] = None
    df.loc[missing_dasher_idx, "has_missing_dasher_flag"] = True

    # 2. Outliers (1%) — delivery_duration_minutes > 120
    n_outliers = int(n_total * 0.01)
    outlier_idx = RNG.choice(delivered_idx, size=n_outliers, replace=False)
    outlier_durations = RNG.integers(121, 181, size=n_outliers).astype(float)
    df.loc[outlier_idx, "delivery_duration_minutes"] = outlier_durations
    df.loc[outlier_idx, "has_outlier_flag"] = True

    # 3. Timestamp issues (1%) — swap two adjacent stage timestamps
    n_ts_issues = int(n_total * 0.01)
    ts_issue_idx = RNG.choice(delivered_idx, size=n_ts_issues, replace=False)
    for idx in ts_issue_idx:
        # Swap stage 4 (arrived restaurant) and stage 5 (picked up) — most common real issue
        s4 = df.at[idx, "stage_4_dasher_arrived_restaurant_at"]
        s5 = df.at[idx, "stage_5_order_picked_up_at"]
        df.at[idx, "stage_4_dasher_arrived_restaurant_at"] = s5
        df.at[idx, "stage_5_order_picked_up_at"] = s4
        # Also swap pickup_at to match
        df.at[idx, "pickup_at"] = s4  # now pickup < arrived (wrong)
        df.at[idx, "has_timestamp_issue_flag"] = True

    # 4. Duplicates (2%) — duplicate full rows
    n_dupes = int(n_total * 0.02)
    dupe_idx = RNG.choice(df.index, size=n_dupes, replace=False)
    dupes = df.loc[dupe_idx].copy()
    dupes["has_duplicate_flag"] = True
    # Mark originals as duplicated too
    df.loc[dupe_idx, "has_duplicate_flag"] = True

    df = pd.concat([df, dupes], ignore_index=True)

    # ---------------------------------------------------------------------------
    # Final column ordering
    # ---------------------------------------------------------------------------
    FINAL_COLUMNS = [
        "order_id", "created_at", "customer_id", "restaurant_id", "ab_group",
        "status", "total_amount_usd",
        "customer_city", "customer_segment",
        "restaurant_name", "restaurant_category", "restaurant_city",
        "delivery_id", "dasher_id", "dasher_assigned_at", "pickup_at",
        "delivered_at", "delivery_duration_minutes",
        "stage_1_order_placed_at", "stage_2_restaurant_confirmed_at",
        "stage_3_dasher_assigned_at", "stage_4_dasher_arrived_restaurant_at",
        "stage_5_order_picked_up_at", "stage_6_dasher_near_customer_at",
        "stage_7_delivered_at",
        "has_duplicate_flag", "has_timestamp_issue_flag",
        "has_missing_dasher_flag", "has_outlier_flag",
    ]
    df = df[FINAL_COLUMNS]

    # ---------------------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------------------
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to: {OUTPUT_PATH}")

    # ---------------------------------------------------------------------------
    # Summary report
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    print(f"\nTotal rows (with duplicates) : {len(df):,}")
    print(f"Unique order_ids             : {df['order_id'].nunique():,}")

    # Month distribution (use created_at of unique orders)
    df_unique = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    df_unique["month"] = pd.to_datetime(df_unique["created_at"]).dt.month
    month_map = {1: "January", 2: "February", 3: "March"}
    print("\nOrders by month (unique):")
    for m, label in month_map.items():
        count = (df_unique["month"] == m).sum()
        pct = count / len(df_unique) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")

    print("\nA/B group distribution (unique orders):")
    ab_counts = df_unique["ab_group"].value_counts().sort_index()
    for grp, count in ab_counts.items():
        pct = count / len(df_unique) * 100
        print(f"  Group {grp}: {count:,} ({pct:.1f}%)")

    print("\nStatus distribution (unique orders):")
    status_counts = df_unique["status"].value_counts()
    for status, count in status_counts.items():
        pct = count / len(df_unique) * 100
        print(f"  {status}: {count:,} ({pct:.1f}%)")

    print("\nCancellation rate by month:")
    for m, label in month_map.items():
        month_orders = df_unique[df_unique["month"] == m]
        cancel_rate = (month_orders["status"] == "cancelled").mean() * 100
        print(f"  {label}: {cancel_rate:.1f}%")

    print("\nData quality flags (total rows including duplicates):")
    flags = [
        "has_duplicate_flag", "has_timestamp_issue_flag",
        "has_missing_dasher_flag", "has_outlier_flag"
    ]
    for flag in flags:
        count = df[flag].sum()
        pct = count / len(df) * 100
        print(f"  {flag}: {count:,} ({pct:.1f}%)")

    print("\nDelivery duration by A/B group (delivered orders, unique, clean):")
    clean_delivered = df_unique[
        (df_unique["status"] == "delivered") &
        (df_unique["has_outlier_flag"] == False) &
        (df_unique["delivery_duration_minutes"].notna())
    ]
    for grp in ["A", "B"]:
        grp_data = clean_delivered[clean_delivered["ab_group"] == grp]["delivery_duration_minutes"]
        print(f"  Group {grp}: mean={grp_data.mean():.2f} min | "
              f"median={grp_data.median():.2f} min | "
              f"std={grp_data.std():.2f} | n={len(grp_data):,}")

    delta = (
        clean_delivered[clean_delivered["ab_group"] == "B"]["delivery_duration_minutes"].mean() -
        clean_delivered[clean_delivered["ab_group"] == "A"]["delivery_duration_minutes"].mean()
    )
    delta_pct = delta / clean_delivered[clean_delivered["ab_group"] == "A"]["delivery_duration_minutes"].mean()
    print(f"\n  Delta B vs A: {delta:+.2f} min ({delta_pct:+.1%})")
    print("=" * 60)


if __name__ == "__main__":
    main()
