import typing
from fastapi import UploadFile

import logging 
import os
import shutil

logger = logging.getLogger("rest_form_logger")
file_handler = logging.FileHandler(filename='rest_form.log')
logger.addHandler(file_handler)


def unzip_archive(
    unpack_path: str,
    zipped_path: str
) -> None:
    """
    Function unpacks file into local path
    specified at 'unpack_path' argument

    Args:
        unpack_path: str - file path to unpack incoming files 
        zipped_path: str - zippe path to parse files from
    """
    shutil.unpack_archive(
        filename=zipped_path,
        extract_dir=unpack_path
    )

    # removing zip file
    os.remove(path=zipped_path)

async def get_image_file_paths(
    uuid_key_string: str,
    archive: UploadFile) -> typing.List:
    """
    Function returns file paths of images,
    extracted from given archive file
    
    Args:
        uuid_key_string - (unique key string) for identifying client's request
        archive (file) - zip file, containing images to process

    Returns:
        List 
    """
    try:
        zipped_path = "photos/zips/zip_%s.zip" % uuid_key_string
        save_image_path = "photos/images/images_%s" % uuid_key_string

        content = await archive.read()

        # Uploading file 
        with open(zipped_path, mode='wb') as zipfile:
            zipfile.write(content)

        zipfile.close() 

        unzip_archive(
            zipped_path=zipped_path,
            unpack_path=save_image_path
        )

        images = os.listdir(path=save_image_path + "/images/")
        
        return [
            os.path.join(save_image_path + "/images/", filename)
            for filename in images
        ]

    except Exception as err:
        logger.error(err)
        raise RuntimeError(
            "Failed to unpack and upload files to cache."
        )
