# 测试pandas 类型转换
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from cooka.common import dataset_util

# 1. 构建带有int32, int64, float32,float64, object(时间样式) 类型数据的数据集
df = pd.read_csv('cooka/test/dataset/iris.csv')

df['label_int_64_1'] = LabelEncoder().fit_transform(df['Species'])  # int32
df['label_int_64_2'] = df['label_int_64_1']

df['label_int_32_1'] = df['label_int_64_1'].astype('int32')
df['label_int_32_2'] = df['label_int_32_1']
df['label_int_32_3'] = df['label_int_32_1']

df['x0_float32'] = df['SepalLengthCm'].astype('float32')
df['date'] = ["2019-10-10 10:10:10"] * 150

print("带有label_int_32列 int32,label_int_64列 int64, x0列 float32,x1列 float64,date列 object(时间样式) 类型数据的数据集预览:")
print(df.dtypes)

print("测试int32列label_int_32_1转int64; int32列label_int_32_2转float32; int32列label_int_32_3转float64; "
      "int64列label_int_64_1转float32; int64列label_int_64_2转float64;  float32列x0_float32转float64; float64列x1转float32;"
      "object列date转datetime64[ns]")


class Field:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def to_dict(self):
        d = \
            {
                "name": self.name,
                "data_type": self.age
            }
        return d


features = [Field('label_int_32_1', 'int64').to_dict(),
            Field('label_int_32_2', 'float32').to_dict(),
            Field('label_int_32_3', 'float64').to_dict(),
            Field('label_int_64_1', 'float32').to_dict(),
            Field('label_int_64_2', 'float64').to_dict(),
            Field('x0_float32', 'float64').to_dict(),
            # Field('SepalWidthCm', 'float64').to_dict(),
            Field('date', 'datetime64[ns]').to_dict()]

casted_df = dataset_util.cast_df(df, features)

print("转换完毕的数据预览：")
print(casted_df.dtypes)
