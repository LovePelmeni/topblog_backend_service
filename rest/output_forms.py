import pydantic
import typing

class SocialMediaAnalysisUnit(pydantic.BaseModel):
    """
    Standard Class for 'get_image_file_paths' REST Endpoint
    """
    file_path: str
    predicted_target_value: typing.Any
    social_media_type: typing.Literal['yt1', 'yt2', 'vk', 'tg', 'zn']




