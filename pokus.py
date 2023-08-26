import boto3

s3=boto3.resource('s3')
BUCKET_NAME = 'fcsm-files'
allFiles = s3.Bucket(BUCKET_NAME).objects.all()
for file in allFiles:
    print(file.key)