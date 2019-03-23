import boto3
import io
import zipfile
import mimetypes
from botocore.client import Config
 ##first get the files in the build bucket
 ##CodeBuild deploys files with server-side encryption


s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

hughgk_bucket = s3.Bucket('hugh.playgk.com')
build_bucket = s3.Bucket('hughbuild.playgk.com')

## download the zip file file, not to bucket but in-memory container
hughbuild_zip = io.BytesIO()
build_bucket.download_fileobj('hughbuild.zip', hughbuild_zip)

##the destination is a BytesIO object expand the zip file
with zipfile.ZipFile(hughbuild_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        mime_type = mimetypes.guess_type(nm)[0]
##upload the files to the deploy bucket, setting the mime type
        hughgk_bucket.upload_fileobj(obj, nm,
            ExtraArgs={'ContentType': str(mime_type)})
##set the axccess on the deploy bucket as public
        hughgk_bucket.Object(nm).Acl().put(ACL='public-read')
