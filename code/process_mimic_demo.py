import pandas as pd
from pathlib import Path

# Paths 
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data" / "mimic_demo"

ADMISSIONS_F = DATA_DIR / "ADMISSIONS.csv"
DIAGNOSES_F = DATA_DIR / "DIAGNOSES_ICD.csv"
OUT_F = DATA_DIR / "medical_data.csv"

def load_csv_lower(path, **kwargs):
    """Load a CSV and lowercase column names."""
    df = pd.read_csv(path, low_memory=False, **kwargs)
    df.columns = [c.lower() for c in df.columns]
    return df

def main():
    # 1) Load CSVs
    admissions = load_csv_lower(ADMISSIONS_F, parse_dates=['admittime', 'dischtime'])
    diagnoses = load_csv_lower(DIAGNOSES_F, dtype=str)  # ICD codes as strings

    # 2) Check required columns
    for col in ['hadm_id', 'admittime']:
        if col not in admissions.columns:
            raise SystemExit(f"ADMISSIONS.csv missing {col} column")

    for col in ['hadm_id', 'icd9_code']:
        if col not in diagnoses.columns:
            raise SystemExit(f"DIAGNOSES_ICD.csv missing {col} column")

    # 3) Flag conditions of interest
    diagnoses = diagnoses[['hadm_id', 'icd9_code']].dropna()
    diagnoses['icd9_code'] = diagnoses['icd9_code'].str.strip().str.replace("'", "", regex=False)
    diagnoses['is_asthma'] = diagnoses['icd9_code'].str.startswith('493')
    diagnoses['is_stroke'] = diagnoses['icd9_code'].str.startswith('434')

    # 4) Collapse diagnoses to one row per admission
    diag_flags = diagnoses.groupby('hadm_id', as_index=False).agg({
        'is_asthma': 'max',
        'is_stroke': 'max'
    }).astype({'is_asthma': 'int64', 'is_stroke': 'int64'})

    # 5) Merge with admissions (ensure hadm_id is same type)
    admissions_small = admissions[['hadm_id', 'admittime']].drop_duplicates()
    admissions_small['hadm_id'] = admissions_small['hadm_id'].astype(str)
    diag_flags['hadm_id'] = diag_flags['hadm_id'].astype(str)

    merged = admissions_small.merge(diag_flags, on='hadm_id', how='left').fillna(0)
    merged['is_asthma'] = merged['is_asthma'].astype(int)
    merged['is_stroke'] = merged['is_stroke'].astype(int)

    # 6) Convert admittime to date
    merged['record_date'] = merged['admittime'].dt.date

    # 7) Aggregate daily counts (NO admissions_total)
    daily = merged.groupby('record_date').agg(
        asthma_cases=('is_asthma', 'sum'),
        stroke_cases=('is_stroke', 'sum')
    ).reset_index()

    # 8) Save CSV
    daily.to_csv(OUT_F, index=False)
    print(f"✅ Wrote {OUT_F} with {len(daily)} rows")

if __name__ == '__main__':
    main()
