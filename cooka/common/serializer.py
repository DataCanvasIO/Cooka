import json
from datetime import datetime


class BeanMeta(type):
    """
    Validate class fit Bean style
    """
    def __new__(cls, name, bases, attrs, **kwargs):

        if name == 'Bean':
            return super().__new__(cls, name, bases, attrs, **kwargs)
        else:

            # meta_define_class = attrs.get('Meta')

            # assert meta_define_class is not None, "Did you make a internal Meta class in '%s' ?" % name
            # assert hasattr(meta_define_class, 'attrs'), "Meta class must has 'attr' "

            _fields_name = []
            for k, v in attrs.items():  # ensure all attr
                if isinstance(v, Field):
                    _fields_name.append(k)

            attrs['_fields_name'] = _fields_name

            return super().__new__(cls, name, bases, attrs, **kwargs)


class Bean(metaclass=BeanMeta):
    """
    todo update doc
    Specification for serialize and deserialize between json string and object.
    A bean should has a meta class like:
    >>> class Person(Bean):
    >>>     class Meta:
    >>>         attrs = ('name', 'phone_num')
    that equals define python class:
    >>> class Person:
    >>>     def __init__(self, name=None, phone_num=None):
    >>>         self.name = name
    >>>         self.phone_num = phone_num
    item of `attrs` may be a string to define property name or a tuple for more detail:

    >>> attrs = ('name', ('phone_num', list, ['13000000000']))
    when it's tuple, format is (property_name, property_type, default_value)， It's worth a question that if your
    property is a custom type object, must specify it's type to help convert to that type from a dict.

    About the class type:
        1. if your custom object in a list, the ListType may help.
        2. if it's None, means any type

    More usage see: cooka/core/test/test_serializer.py

    """

    def __init__(self, *args, **kwargs):

        fields_name = self.__class__._fields_name
        for k, v in kwargs.items():
            if k in fields_name:
                setattr(self, k, v)
            else:
                raise KeyError('Unknown argument: %s' % k)

        # set default value
        for name in fields_name:
            if name not in kwargs:
                field = getattr(self.__class__, name)
                setattr(self, name, field.default)

    @property
    def _fields_name(self):
        return self.__class__._fields_name

    def dumps(self):
        dict_data = self.to_dict()
        return json.dumps(dict_data, ensure_ascii=False, indent=4)

    def to_dict(self):
        # fast than json.loads
        result_dict = {}
        cls = self.__class__
        for field_name in cls._fields_name:
            value = getattr(self, field_name, None)
            field = getattr(cls, field_name)
            if value is not None:
                if not isinstance(value, field.type):  # check value and type match
                    raise ValueError(f"Class={self.__class__} ,attr name={field_name}, value={value} not instance of {field.type}")

                if isinstance(field, ListBeanField):  # value a list
                    generic_bean_cls = field.bean_cls
                    items_dict = []
                    for item in value:
                        if isinstance(item, generic_bean_cls):  # all item in list should as same
                            items_dict.append(item.to_dict())  # serialize every item
                        else:
                            raise ValueError(f"Attr name={field_name} is a list, but item value={item} not instance of {generic_bean_cls}")
                    result_dict[field_name] = items_dict
                elif isinstance(field, Field):
                    if isinstance(field, BeanField):
                        result_dict[field_name] = value.to_dict()
                    else:
                        result_dict[field_name] = value
                else:
                    raise ValueError(f"Unknown field={field_name}, not a Field")
            else:
                result_dict[field_name] = None

        return result_dict

    @classmethod
    def loads(cls, s):
        d = json.loads(s)
        return cls.load_dict(d)

    @classmethod
    def load_dict(cls, d):
        """ Loads from string as object
        """
        # find value in dict use property in cls

        if d is None:
            return None

        construct_args = {}

        for field_name in cls._fields_name:
            value = d.get(field_name)
            field = getattr(cls, field_name)
            if value is None:
                construct_args[field_name] = None
            else:
                if isinstance(field, ListBeanField):  # is a list
                    if not isinstance(value, list):
                        raise ValueError("Key =%s of dict is not a list but you specify ListType. " % field)
                    construct_args[field_name] = [field.bean_cls.load_dict(v) for v in value]  # deserialize every item
                elif isinstance(field, BeanField):
                    construct_args[field_name] = field.bean_cls.load_dict(value)
                else:
                    construct_args[field_name] = value  # Basic Field or unknown type

        return cls(**construct_args)

    @classmethod
    def load_dict_list(cls, dict_list):
        if dict_list is None:
            return None
        else:
            return [cls.load_dict(d) for d in dict_list]

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_json(self):
        return json.dumps(self.to_dict())

# class FieldType:
#     def __new__(cls, _class, *args, **kwargs):
#         """ A bean field
#         Args:
#             _class: to validate value is match Bean Define
#         """
#         cls._class = _class
#         super(FieldType, cls).__new__(_class, *args, **kwargs)

#
# class StringType(FieldType):
#
#     def __new__(cls, *args, **kwargs):
#         super(FieldType, cls).__new__(str, *args, **kwargs)
#
#
# class IntegerType(FieldType):
#
#     def __new__(cls, *args, **kwargs):
#         super(FieldType, cls).__new__(int, *args, **kwargs)
#
#
# class BeanType(FieldType):
#
#     def __new__(cls, *args, **kwargs):
#         super(FieldType, cls).__new__(Bean, *args, **kwargs)
#

# class ListType(FieldType):
#
#     def __new__(cls, *args, **kwargs):
#         super(FieldType, cls).__new__(list, *args, **kwargs)


class Field:

    def __init__(self, type, default=None):
        self.type = type
        self.default = default


class StringField(Field):
    def __init__(self, default=None):
        super(StringField, self).__init__(str, default)


class ObjectField(Field):
    def __init__(self, default=None):
        super(ObjectField, self).__init__(object, default)


class IntegerField(Field):
    def __init__(self, default=None):
        super(IntegerField, self).__init__(int, default)


class FloatField(Field):
    def __init__(self, default=None):
        super(FloatField, self).__init__(float, default)


class BooleanField(Field):
    def __init__(self, default=None):
        super(BooleanField, self).__init__(bool, default)


class DatetimeField(Field):
    def __init__(self, default=None):
        super(DatetimeField, self).__init__(datetime, default)


class DictField(Field):
    def __init__(self, default=None):
        super(DictField, self).__init__(dict, default)


class BeanField(Field):
    def __init__(self, bean_cls,  default=None):
        if not issubclass(bean_cls, Bean):  # check extends from Bean
            raise ValueError(f"bean_cls={bean_cls} is not extend from 'Bean'")

        self.bean_cls = bean_cls
        super(BeanField, self).__init__(bean_cls, default)


class ListBeanField(Field):

    def __init__(self, bean_cls, default=None):
        self.bean_cls = bean_cls
        super(ListBeanField, self).__init__(list, default)


class ListObjectField(Field):

    def __init__(self, default=None):
        super(ListObjectField, self).__init__(list, default)
