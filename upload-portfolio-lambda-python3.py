import boto3
import io
import zipfile
import mimetypes
from botocore.client import Config

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:538156793309:deployPortfolio_Topic')

    location = {
        "bucketName": 'hughbuild.playgk.com',
        "objectKey": 'hughbuild.zip'
    }

    try:
        job = event.get("CodePipeline.job")


        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "hughbuild":
                    location = artifact["location"]["s3Location"]

        print ("Building portfolio from" +str(location))
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        hughgk_bucket = s3.Bucket('hugh.playgk.com')
        build_bucket = s3.Bucket(location["bucketName"])

        ## download the zip file file, not to bucket but in-memory container
        hughbuild_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], hughbuild_zip)

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

        print ("Job Done")
        topic.publish(Subject="Porfolio Deployment", Message="Portfolio deployed successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject="Porfolio Deployment Failed", Message="Portfolio deploy failed")
        raise
    return 'Hello hugh'
