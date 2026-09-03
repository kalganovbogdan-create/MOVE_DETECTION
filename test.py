import yaml
from pathlib import Path
import pandas as pd
path = Path(r'C:\Users\Bogdan1\Desktop\data_rtsp.csv')
df  = pd.read_csv(path)
print(list(df.columns))