import os
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import random

cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
api_key = os.environ.get('CLOUDINARY_API_KEY')
api_secret = os.environ.get('CLOUDINARY_API_SECRET')

cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)

#TODO: move to config property
ALLOWED_EXTENSIONS = ['jpg', 'jpeg',]
def allowed_formats(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_image(name, file):
    try:
        pubname = str(name) + '_' + str(random.randrange(1, 1000000))
        resp = upload(file, public_id=pubname)
        return (pubname, resp)
    except Exception:
        #TODO: Add Logging statment here
        return False