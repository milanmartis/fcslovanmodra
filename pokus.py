import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import boto3
import io

s3 = boto3.resource('s3', region_name='eu-north-1')
bucket = s3.Bucket('fcsm-files')
object = bucket.Object('355244734_10219319449090479_1136688913142605109_n.jpg')

file_stream = io.StringIO()
object.download_fileobj(file_stream)
img = mpimg.imread(file_stream)
# whatever you need to do