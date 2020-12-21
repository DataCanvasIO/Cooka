from cooka.common import consts


class ServiceException(Exception):

    def __init__(self,code, hint, cause=None):
        self.code = code
        self.hint = hint
        self.cause = cause


class IllegalParamException(ServiceException):

    def __init__(self, name, value, reason=None):
        hint = f"Illegal param={name}, value={value}, reason: {reason}"
        super(IllegalParamException, self).__init__(consts.CODE_ILLEGAL_PARAM, hint, self)


class MissingParamException(ServiceException):

    def __init__(self, param):
        hint = f"Missing param {param} ."
        super(MissingParamException, self).__init__(consts.CODE_MISSING_PARAM, hint, self)


class EntityNotExistsException(ServiceException):

    def __init__(self, _type, name):
        if isinstance(_type, str):
            _type_name = _type
        else:
            _type_name = _type.__name__

        hint = f" Entity={name}, type={_type} not exists ."
        super(EntityNotExistsException, self).__init__(consts.ENTITY_NOT_EXISTS, hint, self)

    class Entities:
        Dataset = 'Dataset'
