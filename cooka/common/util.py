import datetime
import time
import six
from uuid import uuid4
import json
from json import JSONEncoder
import math
import re
from cooka.common import consts
from os import path as P

MAX_BUFFER_SIZE = 1024

UUID_CHARS = ("a", "b", "c", "d", "e", "f",
              "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
              "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
              "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
              "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
              "W", "X", "Y", "Z")


def short_uuid():
    uuid = str(uuid4()).replace('-', '')
    result = ''
    for i in range(0, 8):
        sub = uuid[i * 4: i * 4 + 4]
        x = int(sub, 16)
        result += UUID_CHARS[x % 0x3E]
    return result


def human_datetime(date=None):
    if date is None:
        date = datetime.datetime.now()
    return date.strftime("%Y%m%d%H%M%S%f")


def human_std_datetime(date=None):
    if date is None:
        date = datetime.datetime.now()
    return date.strftime("%Y-%m-%d %H:%M:%S")


def cut_suffix(file_name):
    last_position = file_name.rfind('.')
    if last_position > -1:
        return file_name[:last_position]
    else:
        return file_name


def analyze_data_job_name(file_name, _datetime=None):
    d = human_datetime(_datetime)
    return f'job_analyze_{cut_suffix(file_name)}_{d}'


def predict_job_name(dataset_name, _datetime=None):
    d = human_datetime(_datetime)
    return f'job_predict_{cut_suffix(dataset_name)}_{d}'


def temporary_upload_file_path(filename):
    return f'{consts.PATH_TMP_UPLOAD}/{short_uuid()}/{filename}'


def get_file_suffix(file_name):
    last_position = file_name.rfind('.')
    if last_position > -1:
        return file_name[last_position:]
    else:
        raise NameError(f"File {file_name} has no suffix. ")


def human_data_size(value):
    def r(v, unit):
        return "%s%s" % (round(v, 2), unit)

    if value < 1024 * 1024:
        return r(value / 1024, "KB")
    elif 1024 * 1024 < value <= 1024 * 1024 * 1024:
        return r(value / 1024 / 1024, "MB")
    else:
        return r(value / 1024 / 1024 / 1024, "GB")


def get_now_datetime():
    return datetime.datetime.now()


def get_now_long():
    return round(time.time() * 1000)


def to_timestamp(d):
    return round(d.timestamp()*1000)


class NaNEncoder(JSONEncoder):
    def default(self, obj):
        try:
            _ = iter(obj)
        except TypeError:
            if isinstance(obj, float) and math.isnan(obj):
                return "null"
            elif isinstance(obj, datetime.datetime):
                return to_timestamp(obj)
        return JSONEncoder.default(self, obj)


def dumps(d, indent=4):
    """
    防止生成Unicode
    :param d:
    :return:
    """
    import six
    if six.PY2:
        return json.dumps(d, ensure_ascii=False, encoding='utf-8', indent=indent, cls=NaNEncoder)
    else:
        return json.dumps(d, ensure_ascii=False, indent=indent, cls=NaNEncoder)


def dumps_bytes(d):
    """
    防止生成Unicode
    :param d:
    :return:
    """
    str_data = dumps(d)
    return to_bytes(str_data)


def loads(s):
    """
    防止生成Unicode
    :param s:
    :return:
    """
    d = json.loads(s)
    return byteify(d)


def to_str(sv):
    """将unicode和python3中的字节转换成字符串。

    Args:
        sv(Union(bytes, unicode, object)): 字节、unicode或者其他类型的数据转换为字符串；

    Returns:
        str: 字符串数据。
    """
    if six.PY2:
        if isinstance(sv, unicode):
            return sv.encode('utf-8')
        else:
            return str(sv)
    else:  # 在py3以及更高的版本中
        if isinstance(sv, bytes):
            return str(sv, encoding='utf-8')
        else:
            return str(sv)


def to_bytes(s):
    """将字符串转换为字节数组。

    Args:
        s (Union(str, unicode)): 需要转换为字节的数据，在python2中支持类型str和unicode；在py3中支持str。

    Returns:
        字节数据。
    """
    if six.PY2:
        # 在python2中字符串就是字节数组
        if isinstance(s, unicode):
            return s.encode('utf-8')
        elif isinstance(s, str):
            return s
        else:
            raise Exception("无法将类型%s转换为字节" % type(s).__name__)
    else:  # 在py3以及更高的版本中
        if isinstance(s, str):
            return bytes(s, encoding="utf-8")
        elif isinstance(s, bytes):
            return s
        else:
            raise Exception("无法将类型%s转换为字节" % type(s).__name__)


def byteify(s, encoding='utf-8'):
    """
    把Dict中的Unicode转换为字符串
    :param s:
    :param encoding:
    :return:
    """
    if isinstance(s, dict):
        r = {}
        for k in s:
            r[byteify(k)] = byteify(s[k])
        return r
    elif isinstance(s, list):
        return [byteify(element) for element in s]
    elif type(s).__name__ == 'unicode':
        return s.encode(encoding)
    else:
        return s


def datetime_diff(end, start):
    return round((end - start).total_seconds(), 2)   # in seconds


def _divide(n1, n2):
    r1 = int(n1 / n2)
    r2 = n1 % n2
    return r1, r2


def human_format_by_minute(seconds):
    unit_day = 3600 * 24
    unit_hour = 3600
    unit_minute = 60

    if seconds >= unit_day:  # by hour
        n_days, remain_seconds = _divide(seconds, unit_day)
        n_hours, remain_seconds = _divide(remain_seconds, unit_hour)
        n_minutes, remain_seconds = _divide(remain_seconds, unit_minute)
        return f"{n_days}d {n_hours}h {n_minutes}m"
    if seconds >= unit_hour:  # by hour
        n_hour, remain_seconds = _divide(seconds, unit_hour)
        n_minutes, remain_seconds = _divide(remain_seconds, unit_minute)
        return f"{n_hour}h {n_minutes}m"
    elif seconds >= unit_minute:
        n_minutes, remain_seconds = _divide(seconds, unit_minute)
        return f"{n_minutes}m"
    else:
        return "<1m"


def datetime_diff_human_format_by_minute(end, start):
    seconds = round((end - start).total_seconds(), 2)  # in seconds
    return human_format_by_minute(seconds)


def time_diff(end, start):
    delta = end - start
    return round(delta, 2)  # in seconds


def tail(file_path, n=100):
    """ Tail file.
        Read file from tail using seek. Read 1024 chars every time and find .

    Args:
        file_path: a text file only
        n:
    Returns:

    Known Issues:
    1. n=1 may see nothing, please check is the file end with a ''

    """
    with open(file_path, 'r') as f:
        file_size = f.seek(0, 2)  # seek tail
        current_position = file_size

        line_count = 0
        first_line_position = 0
        while current_position > 0:
            if current_position < MAX_BUFFER_SIZE:
                f.seek(0)
                buffer_size = current_position
                current_position = 0
            else:
                current_position = current_position - MAX_BUFFER_SIZE
                f.seek(current_position)
                buffer_size = MAX_BUFFER_SIZE

            data = f.read(buffer_size)
            data_len = len(data)
            for i in range(data_len):
                p = data_len - i - 1
                if data[p] == '':
                    line_count = line_count + 1

                if line_count == n:
                    first_line_position = current_position + p + 1  # does not include break

        f.seek(first_line_position)

        while True:
            _d = f.readline()
            if _d is not None and len(_d) > 0:
                yield _d
            else:
                break


def readall(p):
    with open(p, 'r') as f:
        return f.read()


def read_text(p):
    with open(p, 'r' , encoding='utf-8') as f:
        return f.read()


def load(p):
    return loads(readall(p))


def make_dataset_name(name):
    """Dataset name contains "letters, numbers, -, _" only, any other content will be replaced with "-"
    """

    def may_replace(c):
        if re.match("\w", c) is None:
            if c == '-':
                return c
            else:
                return "_"
        else:
            return c

    return "".join([may_replace(c) for c in name])


def require_type(name, o, t):
    if o is not None:
        if not isinstance(o, t):
            raise Exception("'%s'需要%s类型。" % (name, t.__name__))


def require_attr_not_none(o, name):
    """校验对象中的属性不能为空。
    Args:
        o:
        name: 属性的名称。
    Returns:
    """
    if o is not None:
        if getattr(o, name, None) is None:
            raise Exception("对象=%s的属性'%s'不能为空。" % (str(o), name))


def require_list_non_empty(name, o):
    """校验数组不能为空。
    Args:
        name: 提示对象名称。
        o: 数组对象。
    Returns:
    """
    if is_non_empty_list(o):
        pass
    else:
        raise Exception("'%s' 不能为空。" % name)


def require_str_non_empty(str_obj, tips):
    """校验数组不能为空。
    Args:
        str_obj: 字符串对象。
        tips: 为空时的提示信息。
    Returns:
    """
    if str_obj is None or len(str_obj) == 0:
        raise Exception("'%s' 不能为空。" % tips)


def cast_type(o, _type):
    if o is None:
        return o
    else:
        if _type == int:
            if not isinstance(o, int):
                return int(o)  # may raise error
            else:
                return o
        if _type == float:
            if not isinstance(o, float):
                return float(o)  # may raise error
            else:
                return o
        elif _type == str:
            return str(o)
        else:
            raise ValueError(f"Not supported convert type: {_type}")


def require_in_dict(_dict, key, _type=int, default=None):
    v = _dict.get(key, default)
    if v is None:
        raise ValueError(f"Key={key} can not be None.")
    else:
        if isinstance(v, _type):
            return v
        else:
            return cast_type(v, _type)


def get_from_dict(_dict, key, _type=int, default=None):
    v = _dict.get(key, default)
    if v is None:
        return v
    else:
        if isinstance(v, _type):
            return v
        else:
            return cast_type(v, _type)




def is_non_empty_list(o):
    return o is not None and len(o) > 0


def is_empty_list(o):
    return o is None or len(o) == 0


def is_non_empty_str(o):
    return o is not None and isinstance(o, str) and len(o) > 0


def revert_to_dict_from_dict(d, key):
    v = d.get(key)
    if v is not None and len(v) > 0 and isinstance(v, str):
        d[key] = loads(v)


def revert_to_dict_from_object(obj, *keys):
    for key in keys:
        v = getattr(obj, key)
        if v is not None and len(v) > 0 and isinstance(v, str):
            setattr(obj, key, loads(v))


def sqlalchemy_obj_to_dict(entity_instance):
    return {attr.key: getattr(entity_instance, attr.key) for attr in entity_instance._sa_instance_state.attrs}



# s = datetime_diff_human_format_by_minute(get_now_datetime(), datetime.datetime(2019,9,29,10,10,10,10) )
# print(s)

def temporary_dataset_dir(dataset_name):
    return P.join(consts.PATH_TEMPORARY_DATASET, dataset_name)


def dataset_dir(dataset_name):
    return P.join(consts.PATH_DATASET, dataset_name)


def model_name(dataset_name, no_experiment):
    return str("%s_%s" % (dataset_name, no_experiment))


def model_dir(dataset_name, model_name):
    return P.join(dataset_dir(dataset_name), consts.FIELD_EXPERIMENT, model_name)


def read_csv(csv_file, has_header, default_headers=None):
    import pandas as pd  # took a lot of time(0.4s)
    if has_header:
        return pd.read_csv(csv_file)  # read it all
    else:
        if default_headers is None:
            raise ValueError("When has_header is False, param default_headers is required.")
        df = pd.read_csv(csv_file, header=None)
        df.columns = default_headers
        return df


def relative_path(p: str, prefix=consts.DATA_DIR):
    if p.startswith(prefix):
        return p[len(prefix)+1:]  # Fix: should not start with '/'
    else:
        raise ValueError(f"Path is not start with {prefix}.")


import pickle
ENCODING_LIST = ["iso-8859-1", "ascii", 'utf-8', "gbk", "gb2312", "gb18030"]

PICKLE_PROTOCOL = 2
if six.PY2:
    PICKLE_PROTOCOL = 2
elif six.PY3:
    PICKLE_PROTOCOL = 3


def serialize_with_ignore_variables(obj, variables):
    """
    序列化对象时忽略部分属性。
    :param obj:
    :param variables:
    :return:
    """
    if variables is None:
        variables = []
    cache_map = {}
    # 1. 忽略对象
    for v_name in variables:
        if hasattr(obj, v_name):
            value = getattr(obj, v_name)
            cache_map[v_name] = value
            setattr(obj, v_name, None)
    # 2. 导出数据
    bytes_value = pickle.dumps(obj, protocol=PICKLE_PROTOCOL)

    # 3. 还原对象
    for k in cache_map:
        setattr(obj, k, cache_map[k])

    return bytes_value


def deserialize(data):
    if six.PY2:
        return pickle.loads(data)
    else:
        _e = None
        for encoding in ENCODING_LIST:
            try:
                obj = pickle.loads(data, encoding=encoding)
                return obj
            except Exception as e:
                _e = e
                print("使用编码%s加载对象失败， 原因 %s。" % (encoding, str(e)))
        raise _e


def load_pkl(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        return deserialize(data)


def serialize2bytes(obj):
    return serialize_with_ignore_variables(obj, None)


def serialize2file(obj, path):
    data = serialize_with_ignore_variables(obj, None)
    with open(path, 'wb') as f:
        f.write(data)


def script_path(script):
    return f"{consts.PATH_INSTALL_HOME}/cooka/core/{script}"


def abs_path(p):
    return P.join(consts.DATA_DIR, p)


def validate_sample_conf(sample_conf):
    from cooka.common.model import SampleConf  # fix import error
    if sample_conf.sample_strategy == SampleConf.Strategy.Percentage:
        if sample_conf.percentage <= 0 or sample_conf.percentage > 100:
            raise ValueError(f"Param sample_conf.percentage should in (0, 100] but is {sample_conf.percentage}")
    elif sample_conf.sample_strategy == SampleConf.Strategy.RandomRows:
        if sample_conf.n_rows <= 0:
            raise ValueError(f"Param sample_conf.n_rows should bigger than 0 but is {sample_conf.n_rows}")
    elif sample_conf.sample_strategy == SampleConf.Strategy.WholeData:
        pass
    else:
        raise ValueError(f"Unknown sample strategy: {sample_conf.sample_strategy}")
