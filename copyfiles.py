# import boto3
# import os
# from flask import Flask, send_file, render_template, request
# from io import BytesIO
# import botocore
# from botocore.exceptions import NoCredentialsError


# AWS_ACCESS_KEY_ID = 'AKIA2E7FAZMVEOBLDJVG'
# AWS_SECRET_ACCESS_KEY = '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'
# BUCKET_NAME = 'fcsm-files'
# app = Flask(__name__)

# s3 = boto3.client('s3', 
#                   region_name='eu-north-1', 
#                   aws_access_key_id=AWS_ACCESS_KEY_ID, 
#                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# def get_s3_image(bucket_name, file_name):
#     obj = s3.get_object(Bucket=bucket_name, Key=file_name)
#     return obj['Body'].read()

# @app.route('/display_image')
# def display_image():
#     bucket_name = BUCKET_NAME
#     file_name = '355244734_10219319449090479_1136688913142605109_n.jpg'
#     img = get_s3_image(bucket_name, file_name)
#     if not img:
#         return render_template('index.html')
#     return send_file(BytesIO(img), mimetype='image/jpeg')