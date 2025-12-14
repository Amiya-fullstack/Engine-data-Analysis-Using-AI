import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # add project root to import path
import pandas as pd
from data_pipeline.Load_Engn_Data import make_windows_for_unit

if __name__ == '__main__':
    df = pd.read_csv('data_sources/synthetic_engine_data.csv', parse_dates=['time'])
    df_unit = df[df['unit_id'] == 'unit_1'].reset_index(drop=True)
    wins = make_windows_for_unit(df_unit, 'unit_1', window_size=10, stride=5)
    print(f"Generated {len(wins)} windows")
    if wins:
        print(wins[0])
