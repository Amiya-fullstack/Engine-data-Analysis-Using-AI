def ingest_sensor_csv(csv_path: str):
    """Read sensor CSV and prepare for graph insertion."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    return df
