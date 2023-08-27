import fastapi.responses as resp
from fastapi import (
    UploadFile, 
    File, 
    Form
)

import os
import fastapi
import logging

from typing import Annotated
import shutil

from rest.output_forms import SocialMediaAnalysisUnit
from key_generator import session_key_gen
from rest import preprocessing

from models import models as ml_models

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename='rest_controllers.log')
logger.addHandler(file_handler)


async def analyze_social_media_acrhive(
    social_media_type: Annotated[str, Form()],
    validation: Annotated[int, Form()],
    file: UploadFile = File(...),
    ) -> resp.JSONResponse:

    """
    Main REST Controller Endpoint
    for processing Social Media Analysis Requests
    """
    
    try:
        if not social_media_type in ['yt1', 'yt2', 'tg', 'zn', 'vk']:
            return fastapi.exceptions.HTTPException(
                status_code=400,
                detail="Invalid social media type"
            )

        if hasattr(file, 'filename') and getattr(file, 'filename') is not None:
            if not file.filename.endswith(".zip"):
                return fastapi.exceptions.HTTPException(
                    status_code=400,
                    detail="Invalid File Format"
                )

        unique_clients_key = session_key_gen.generate_unique_key()
        
        # preprocessing image files
        input_image_tuples = await preprocessing.get_image_file_paths(
            uuid_key_string=unique_clients_key,
            archive=file
        )
        image_predictions = [] 
        model = ml_models.TextDetectionModel()

        for file_path in input_image_tuples:
            try:
                if validation == 0:
                    predicted_value = model.process_image(
                        path=file_path,
                        type_of_social=social_media_type,
                        show=False
                    )
                    image_path = os.path.abspath(path=file_path)
                    
                elif validation == 1:
                    predicted_value, file_content = model.process_image(
                        path=file_path,
                        type_of_social=social_media_type,
                        show=True
                    )
                    validation_path = await preprocessing.save_validation_box(
                        file_content=file_content,
                        unique_key_string=unique_clients_key,
                        image_name_with_ext=file_path.split("/")[-1]
                    )
                    image_path = os.path.abspath(path=validation_path)
                    
            except(AttributeError):
                predicted_value = None
                image_path = "invalid-path"

            # filling prediction form
            prediction_form = SocialMediaAnalysisUnit(
                file_path=image_path,
                social_media_type=social_media_type,
                predicted_target_value=predicted_value
            )
            # adding to the general output
            image_predictions.append(prediction_form.dict())

        # removing directory with loaded photos
        shutil.rmtree("photos/images/images_%s/" % unique_clients_key)

        return fastapi.responses.JSONResponse(
            status_code=201,
            content=image_predictions
        )

    except Exception as err:
        logger.error(err)
        raise err
        raise fastapi.exceptions.HTTPException(
            status_code=500,
            detail="Internal Server Error"
        ) 

def healthcheck():
    """
    Standard heatlhcheck endpoint for
    pinpointing web application health state

    Do not accept any internal arguments
    """
    return resp.Response(
        status_code=200
    )