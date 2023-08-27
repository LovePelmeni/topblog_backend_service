import typing
from fastapi import UploadFile

import logging 
import os
import shutil
import io

logger = logging.getLogger("rest_form_logger")
file_handler = logging.FileHandler(filename='rest_form.log')
logger.addHandler(file_handler)

def folder_contains_png(folder_path):
    for _, _, files in os.walk(folder_path):
        for file in files:
            if (file.lower().endswith('.png')
            ) or (file.lower().endswith('.jpg')
            ) or (file.lower().endswith('.jpeg')):
                return True
    return False

def find_folder_with_image_files(root_path: str):

    queue = [root_path]
    image_paths = []

    while queue:
        currDir = queue.pop(0)
        for _, dirs, files in os.walk(currDir):

            if len(dirs) == 0 and len(files) > 0: 
                if folder_contains_png(currDir):
                    image_paths.append(currDir)
            else:
                for directory in dirs: 
                    full_path = os.path.join(currDir, directory)
                    queue.append(full_path)
    return image_paths 

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


async def save_validation_box(
    file_content: bytes, 
    unique_key_string: str,
    image_name_with_ext: str
) -> str:
    """
    Function saves given image with analytics to specific
    folder for storing images with bound boxes
    """

    validation_path = "photos/images/validation_boxes/boxes_%s/%s" % (
        unique_key_string,
        image_name_with_ext
    )

    with open(validation_path, mode='wb') as val_box:
        val_box.write(io.BytesIO(file_content))
    val_box.close()
    return validation_path

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

        found_paths = find_folder_with_image_files(
        root_path=save_image_path)

        images = []
        image_exts = ["jpeg", "jpg", "png"]
        
        for path in found_paths:
            image_files = os.listdir(path=path)
            images.extend(
                [
                    os.path.join(path, image_name) for image_name
                    in image_files if os.path.isfile(
                    path=os.path.join(path, image_name)) and (
                    image_name.split(".")[-1].lower() in image_exts)
                ]
            )
        return images

    except Exception as err:
        logger.error(err)
        raise RuntimeError(
            "Failed to unpack and upload files to cache."
        )
