import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):

    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

    hughgk_bucket = s3.Bucket('hugh.playgk.com')
    build_bucket = s3.Bucket('hughbuild.playgk.com')

    hughbuild_zip = StringIO.StringIO()
    build_bucket.download_fileobj('hughbuild.zip', hughbuild_zip)

    with zipfile.ZipFile(hughbuild_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            hughgk_bucket.upload_fileobj(obj, nm,
             ExtraArgs={'ContentType': 'basestring'})
            hughgk_bucket.Object(nm).Acl().put(ACL='public-read')
    return 'Hello from Lambda'
