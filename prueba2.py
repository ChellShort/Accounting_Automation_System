import pandas as pd
import numpy as np

# Sample DataFrame
data = {'1': [10, 20, 30],
        '2': [40, "total", 60],
        '3': [70, 80, 90]}
df = pd.DataFrame(data, index=['1', '2', '3'])

# Value to find
value_to_find = 20

# Find the location(s)
locations = df.stack()[df.stack() == value_to_find].index.tolist()

print(f"DataFrame:\n{df}\n")
print(f"Value '{value_to_find}' found at location(s): {locations}")
