from pathlib import Path
import requests
import pandas as pd

# Folder where raw API data will be saved
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Mutual fund schemes from the assignment
schemes = {
    "HDFC Top 100 Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841,
}


def fetch_nav(scheme_name, scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"

    print("\n" + "=" * 60)
    print(f"Fetching: {scheme_name}")
    print(f"Scheme Code: {scheme_code}")
    print("=" * 60)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        json_data = response.json()

        # Scheme information
        meta = json_data.get("meta", {})
        nav_data = json_data.get("data", [])

        if not nav_data:
            print("No NAV data returned.")
            return None

        # Convert NAV history to DataFrame
        df = pd.DataFrame(nav_data)

        # Add scheme details
        df["scheme_code"] = scheme_code
        df["scheme_name"] = meta.get(
            "scheme_name",
            scheme_name
        )
        df["fund_house"] = meta.get(
            "fund_house",
            ""
        )
        df["scheme_category"] = meta.get(
            "scheme_category",
            ""
        )

        # Reorder columns
        preferred_columns = [
            "scheme_code",
            "scheme_name",
            "fund_house",
            "scheme_category",
            "date",
            "nav",
        ]

        df = df[
            [col for col in preferred_columns if col in df.columns]
        ]

        # Safe filename
        safe_name = (
            scheme_name.lower()
            .replace(" ", "_")
            .replace("/", "_")
        )

        output_file = (
            RAW_DIR /
            f"live_nav_{scheme_code}_{safe_name}.csv"
        )

        df.to_csv(output_file, index=False)

        print(f"Records fetched: {len(df)}")

        # API normally returns newest NAV first
        print("\nLatest NAV:")
        print(f"Date: {df.iloc[0]['date']}")
        print(f"NAV: {df.iloc[0]['nav']}")

        print(f"\nSaved to: {output_file}")

        return df

    except requests.exceptions.RequestException as error:
        print(f"API request failed: {error}")
        return None

    except ValueError as error:
        print(f"JSON parsing failed: {error}")
        return None

    except Exception as error:
        print(f"Unexpected error: {error}")
        return None


print("=" * 60)
print("LIVE MUTUAL FUND NAV FETCH")
print("=" * 60)

successful = 0

for scheme_name, scheme_code in schemes.items():

    result = fetch_nav(
        scheme_name,
        scheme_code
    )

    if result is not None:
        successful += 1


print("\n" + "=" * 60)
print("NAV FETCH SUMMARY")
print("=" * 60)

print(f"Successful schemes: {successful}/{len(schemes)}")

if successful == len(schemes):
    print("All NAV datasets fetched successfully.")
else:
    print("Some NAV requests failed. Check the messages above.")

print("\nLive NAV fetch completed.")