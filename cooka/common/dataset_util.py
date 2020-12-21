# -*- encoding: utf-8 -*-
import pandas as pd


def _convert_df_data_type(df, col_name, output_col_type):
    df[col_name] = df[[col_name]].astype(output_col_type)
    return df


def _convert_object_to_datetime(df, col_name, output_col_type):
    df[col_name] = pd.to_datetime(df[col_name], errors="coerce")
    return df


convert_rules = \
    {
        "int32": (["int64", "float32", "float64"], _convert_df_data_type),
        "int64": (["int32", "float32", "float64"], _convert_df_data_type),
        "float32": (["float64"], _convert_df_data_type),
        "object": (["datetime64[ns]"], _convert_object_to_datetime)
    }


def cast_df(input_df, schema, remove_unnecessary_cols=False):
    """schema: [{"name": "age", "type": "float64"}]"""
    # 1. validate input data
    if not isinstance(input_df, pd.DataFrame):
        raise Exception("Input data type should be pd.DataFrame, but is: %s" % str(type(input_df)))

    # 2. validate schema
    dtypes_dict = input_df.dtypes.to_dict()
    input_data_name_type_dict = {}
    for c in dtypes_dict:
        input_data_name_type_dict[c] = dtypes_dict[c].name.lower()  # 处理pd.Int32Dtype() 类型

    # 3. cut unnecessary cols
    if remove_unnecessary_cols is True:
        feature_names = set([f['name'] for f in schema])
        unnecessary_cols = set(dtypes_dict.keys()) - feature_names
        if unnecessary_cols is not None and len(unnecessary_cols) > 0:
            print("Unnecessary_cols: %s" % ",".join(list(unnecessary_cols)))
        input_df = input_df[list(feature_names)]

    # 4. cast type
    for f in schema:
        # 4.1. check feature exists
        feature_name = f['name']
        if feature_name not in input_data_name_type_dict:
            raise Exception("Missing input feature: %s" % feature_name)

        data_type_name = input_data_name_type_dict[feature_name]
        feature_type_name = f['data_type']

        # 4.2. try to convert type if not match
        if feature_type_name.lower() != data_type_name:
            converter_tuple = convert_rules.get(data_type_name)
            if converter_tuple is not None:
                matched_cols = converter_tuple[0]
                if feature_type_name in matched_cols:  # do convert
                    converter_tuple[1](input_df, feature_name, feature_type_name)
                else:
                    raise Exception(f"For feature {feature_name} in input data type is {data_type_name}, cat only convert to {','. join(matched_cols) }, but target type is: {feature_type_name} .")
            else:
                raise Exception(f"There no convert for feature {feature_name} and  type is: {data_type_name}, but target type is {feature_type_name}")
    return input_df
