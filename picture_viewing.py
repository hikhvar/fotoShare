__author__ = 'christoph'

import zipfile
import os.path
import uuid

def create_zipfile(picture_dir, pictures):
    file_name = "/tmp/%s" % uuid.uuid4()
    zip = zipfile.ZipFile(file_name, "a")
    for pic in pictures:
        pic_path = os.path.join(picture_dir, pic["filename"])
        zip.write(pic_path, pic["filename"])
    zip.close()
    return file_name

def create_picture_list(pictures):
    ret_list = []
    for pic in pictures:
        pic_dic = dict(name=pic["filename"])
        ret_list.append(pic_dic)
    return ret_list