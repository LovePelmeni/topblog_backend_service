import fastapi.responses

def healthcheck():
    """
    Standard heatlhcheck endpoint for
    pinpointing web application health state

    Do not accept any internal arguments
    """
    return fastapi.responses.Response(
        status_code=200
    )