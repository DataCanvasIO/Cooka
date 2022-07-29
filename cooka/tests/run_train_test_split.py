from sklearn.datasets import species_distributions

import numpy as np
from sklearn.model_selection import train_test_split
import random

data = [int(random.random() * 100) for i in list(range(100))]

import pandas as pd

df = pd.DataFrame(data=data, columns=['num'])


# print(df)

df1 = df.sort_values(axis=0, by='num')
print(df1.values.tolist())
# train_test_split

