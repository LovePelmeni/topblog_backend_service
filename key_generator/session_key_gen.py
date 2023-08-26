import uuid

def generate_unique_key():
    return str(uuid.uuid4()).strip(" ") + "456"