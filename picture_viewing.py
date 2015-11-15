__author__ = 'christoph'

import zipfile
import os.path
import uuid

UUID_NAMESPACE=uuid.UUID('5893b09e-587e-418c-9f1b-142d0bdb7fde')


def create_zipfile(picture_dir, pictures, session_key):
    print session_key
    print UUID_NAMESPACE
    file_name = "zipfiles/%s" % str(uuid.uuid3(UUID_NAMESPACE, "test"))
    file_path = os.path.join(picture_dir, file_name)
    try:
        path, _ = os.path.split(file_path)
        os.makedirs(path)
    except:
        pass
    zip = zipfile.ZipFile(file_path, "w")
    for pic in pictures:
        pic_path = os.path.join(picture_dir, pic["filename"])
        zip.write(pic_path, pic["filename"])
    zip.close()
    return os.path.split(file_path)

def create_picture_list(pictures):
    ret_list = []
    for pic in pictures:
        pic_dic = dict(name=pic["filename"])
        ret_list.append(pic_dic)
    return ret_list