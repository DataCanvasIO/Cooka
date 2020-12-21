import pandas as pd
data = pd.DataFrame(data=[ [1,2],[1,2], [1,2],  ], columns=['a', 'b'])
print(data)
series_a: pd.Series = data['a']
series_a.nunique()
series_a.unique()
