import fastapi.responses as resp
from fastapi import UploadFile, File
import fastapi
import logging
import shutil

from rest.output_forms import SocialMediaAnalysisUnit
from key_generator import session_key_gen
from rest import preprocessing

from models import models as ml_models

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename='rest_controllers.log')
logger.addHandler(logger)

async def analyze_social_media_acrhive(
    # social_media_type: str,
    # image_zip_file: UploadFile = File(...)
    ) -> resp.JSONResponse:

    """
    Main REST Controller Endpoint
    for processing Social Media Analysis Requests
    """

    try:
        social_media_type = 'zn'
        image_zip_file = UploadFile(
            file=open("./rest/images.zip", mode='rb')
        )

        if not social_media_type in ['yt', 'tg', 'zn', 'vk']:
            return fastapi.exceptions.HTTPException(
                status_code=400,
                detail="Invalid social media type"
            )

        if getattr(image_zip_file, 'filename') is not None:
            if not image_zip_file.filename.endswith(".zip"):
                return fastapi.exceptions.HTTPException(
                    status_code=400,
                    detail="Invalid File Format"
                )

        unique_clients_key = session_key_gen.generate_unique_key()
        
        # preprocessing image files
        input_image_tuples = await preprocessing.get_image_file_paths(
            uuid_key_string=unique_clients_key,
            archive=image_zip_file
        )
        
        input_image_tuples = input_image_tuples[:5]
        image_predictions = [] 
        model = ml_models.TextDetectionModel()
        
    
        for file_path in input_image_tuples:
            print(file_path)
            try:
                predicted_value = model.process_image(
                    path=file_path,
                    type_of_social=social_media_type,
                    show=False
                )
            except(AttributeError):
                predicted_value = None

            # filling prediction form
            prediction_form = SocialMediaAnalysisUnit(
                filename=file_path.split("/")[-1],
                social_media_type=social_media_type,
                predicted_target_value=predicted_value
            )
            # adding to the general output
            image_predictions.append(prediction_form.dict())

        # removing directory with loaded photos
        shutil.rmtree("photos/images/images_%s/images/" % unique_clients_key)

        return fastapi.responses.JSONResponse(
            status_code=201,
            content=image_predictions
        )

    except Exception as err:
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