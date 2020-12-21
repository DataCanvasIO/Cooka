from cooka.common.serializer import *


class Company(Bean):
    name = StringField()


class Employee(Bean):
    name = StringField()
    age = IntegerField()
    company = ListBeanField(Company)


class Book(Bean):
    publisher = ListObjectField()


class TestSerializer:

    def test_serializer(self):
        e = Employee(name='zhangwuji', age=18, company=[Company(name='MingJiao'), Company(name='WuDangPai')])
        dict_data = e.to_dict()
        assert dict_data['name'] == 'zhangwuji'
        assert dict_data['age'] == 18
        assert dict_data['company'][0]['name'] == 'MingJiao'
        assert dict_data['company'][1]['name'] == 'WuDangPai'

        new_e = Employee.load_dict(dict_data)
        assert new_e.name == 'zhangwuji'
        assert new_e.company[0].name == 'MingJiao'
        assert new_e.company[1].name == 'WuDangPai'
        assert new_e.age == 18

    def test_list_object_serializer(self):

        b = Book(publisher=["ZhongXin", "GongYe"])
        dict_b = b.to_dict()
        assert dict_b['publisher'] == ["ZhongXin", "GongYe"]

        b1 = Book.load_dict(dict_b)
        assert b1.publisher == ["ZhongXin", "GongYe"]

