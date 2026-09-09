"""
Fetch venue data for Vienna districts from OpenStreetMap via the Overpass API.

Usage:
    pip install requests pandas
    python fetch_osm_vienna.py

Output:
    data/raw/vienna_venues_raw.json   (raw Overpass response)
    data/processed/vienna_venues.csv  (flattened, ready for KG loading)
"""

import json
import time
from pathlib import Path

import requests
import pandas as pd

# The main overpass-api.de endpoint has been aggressively rejecting
# programmatic/bot-shaped traffic with 406 errors throughout 2025-2026.
# Try mirrors first; keep the primary as a last-resort fallback.
OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",  # last resort, often bot-blocked
]

# Vienna districts (Bezirke) to start with. Vienna districts are admin_level=9 in OSM.
# Start small - expand this list once the pipeline works end to end.
DISTRICTS = [
    "Innere Stadt",
    "Leopoldstadt",
    "Neubau",
]

# Venue categories relevant to "tourist trap vs hidden gem"
AMENITY_TYPES = ["cafe", "restaurant", "bar", "fast_food", "pub"]
TOURISM_TYPES = ["attraction", "museum", "viewpoint", "gallery", "artwork"]


# Bounding boxes (south, west, north, east) for each district.
# Get these ONCE per district via the Nominatim UI (https://nominatim.openstreetmap.org/ui/search.html),
# search "<District>, Vienna, Austria", click "details" on the correct (Administrative) result,
# and copy the "boundingbox" field from there - it comes as [south, north, west, east], so reorder
# to (south, west, north, east) before pasting in here.
#
# Values below are best-effort placeholders - VERIFY each one via the UI before trusting the data.
DISTRICT_BBOXES = {
    "Innere Stadt": (48.1962, 16.3610, 48.2183, 16.3844),
    "Leopoldstadt": (48.1980, 16.3700, 48.2460, 16.4420),
    "Neubau": (48.1975, 16.3395, 48.2070, 16.3550),
}


def build_amenity_query(bbox: tuple[float, float, float, float]) -> str:
    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"
    amenity_filter = "|".join(AMENITY_TYPES)
    return f"""
    [out:json][timeout:60];
    (
      node["amenity"~"^({amenity_filter})$"]({bbox_str});
      way["amenity"~"^({amenity_filter})$"]({bbox_str});
    );
    out center tags;
    """


def build_tourism_query(bbox: tuple[float, float, float, float]) -> str:
    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"
    tourism_filter = "|".join(TOURISM_TYPES)
    return f"""
    [out:json][timeout:60];
    (
      node["tourism"~"^({tourism_filter})$"]({bbox_str});
      way["tourism"~"^({tourism_filter})$"]({bbox_str});
    );
    out center tags;
    """


HEADERS = {
    # These specific headers are what the primary endpoint's bot-filter checks.
    "User-Agent": "KG-Urban-Discoveries-TUWien/0.1 (student project; contact: your-email@example.com)",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
}


def run_query(query: str, label: str, rounds: int = 2) -> list[dict] | None:
    """
    Try each endpoint, with retries per endpoint on transient 504s, and
    optionally repeat the whole endpoint list a couple of times with a
    longer pause - congestion tends to come and go in waves.
    Returns None (never raises) if every attempt across every round fails,
    so callers can decide whether to continue with partial data.
    """
    last_error = None
    for round_num in range(1, rounds + 1):
        for endpoint in OVERPASS_ENDPOINTS:
            for attempt in (1, 2, 3):
                try:
                    resp = requests.post(endpoint, data={"data": query}, headers=HEADERS, timeout=90)
                    if resp.ok:
                        data = resp.json()
                        elements = data.get("elements", [])
                        print(f"  [{label}] {endpoint} -> HTTP 200, {len(elements)} raw elements")
                        return elements
                    print(f"  [{label}] {endpoint} returned {resp.status_code} (round {round_num}, attempt {attempt})")
                    last_error = resp.text[:300]
                    if resp.status_code == 504 and attempt < 3:
                        time.sleep(5)
                        continue
                    break
                except requests.RequestException as e:
                    print(f"  [{label}] {endpoint} failed (round {round_num}, attempt {attempt}): {e}")
                    last_error = str(e)
                    if attempt < 3:
                        time.sleep(5)
                        continue
                    break
        if round_num < rounds:
            print(f"  [{label}] all endpoints failed in round {round_num}, waiting 30s before next round...")
            time.sleep(30)
    print(f"  [{label}] gave up after {rounds} rounds. Last error: {last_error}")
    return None


def fetch_district(district: str) -> list[dict]:
    if district not in DISTRICT_BBOXES:
        raise KeyError(f"No bbox defined for '{district}' - add it to DISTRICT_BBOXES")
    bbox = DISTRICT_BBOXES[district]
    print(f"  using bbox: {bbox}")

    amenity_elements = run_query(build_amenity_query(bbox), "amenity") or []
    time.sleep(1)
    tourism_elements = run_query(build_tourism_query(bbox), "tourism") or []

    if not amenity_elements and not tourism_elements:
        print(f"  WARNING: both amenity and tourism failed for {district} - 0 venues collected")

    all_elements = amenity_elements + tourism_elements
    for el in all_elements:
        el["district"] = district
    return all_elements


def flatten(elements: list[dict]) -> pd.DataFrame:
    rows = []
    for el in elements:
        tags = el.get("tags", {})
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        rows.append({
            "osm_id": el.get("id"),
            "osm_type": el.get("type"),
            "district": el.get("district"),
            "name": tags.get("name"),
            "amenity": tags.get("amenity"),
            "tourism": tags.get("tourism"),
            "cuisine": tags.get("cuisine"),
            "opening_hours": tags.get("opening_hours"),
            "website": tags.get("website"),
            "lat": lat,
            "lon": lon,
        })
    return pd.DataFrame(rows)


def save_progress(all_elements: list[dict], raw_dir: Path, processed_dir: Path):
    with open(raw_dir / "vienna_venues_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_elements, f, ensure_ascii=False, indent=2)
    df = flatten(all_elements)
    df = df[df["name"].notna()]  # drop unnamed venues
    df.to_csv(processed_dir / "vienna_venues.csv", index=False)
    return df


def main():
    base_dir = Path(__file__).resolve().parent.parent  # project root, one level up from scripts/
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    all_elements = []
    for district in DISTRICTS:
        print(f"Fetching {district}...")
        try:
            elements = fetch_district(district)
        except Exception as e:
            print(f"  ERROR fetching {district}, skipping: {e}")
            elements = []
        print(f"  -> {len(elements)} venues")
        all_elements.extend(elements)
        save_progress(all_elements, raw_dir, processed_dir)  # save after every district
        time.sleep(2)  # be polite to the shared Overpass endpoints

    df = save_progress(all_elements, raw_dir, processed_dir)
    print(f"\nSaved {len(df)} named venues to data/processed/vienna_venues.csv")
    print(df["amenity"].value_counts(dropna=True))
    print(df["tourism"].value_counts(dropna=True))


if __name__ == "__main__":
    main()