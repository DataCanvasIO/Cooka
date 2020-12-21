class Uploader(object):
    def __init__(self, **kwargs):
        pass
        # self.store_file_path = store_file_path

    def get_file_name(self):
        raise NotImplemented

    def upload(self, store_file_path):
        raise NotImplemented


class TornadoUploader(Uploader):

    def __init__(self, file_object):
        self.file_object = file_object
        super().__init__()

    def upload(self, store_file_path):
        with open(store_file_path, 'wb') as f:
            f.write(self.file_object['body'])

    def get_file_name(self):
        return self.file_object['filename']
