import pandas as pd
import numpy as np

df = pd.DataFrame({
    0: [np.nan]*61 + [
        "Ing. José Esteban Garcia Monrroy.",
        "Gerencia Técnica."
    ]
})

print(df.info())
is_string = df[0].apply(lambda x: isinstance(x, str))

starts = is_string & ~is_string.shift(fill_value=False)
ends = is_string & ~is_string.shift(-1, fill_value=False)
print(f"starts: {starts} ends: {ends}")

start_indices = df.index[starts]
end_indices = df.index[ends]
ranges = list(zip(start_indices, end_indices))
print(ranges)
