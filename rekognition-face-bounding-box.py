## LAYER
import cv2
import numpy as np

import json
import boto3
import io
import logging
import argparse
import decimal
logger = logging.getLogger(__name__)

from datetime import datetime

region = "ap-south-1"
s3 = boto3.client("s3")
s3_resource = boto3.resource("s3")
rekognition = boto3.client("rekognition", region)

input_bucket = "face-rekognition-s3-input"
output_bucket = "face-rekognition-output"

def lambda_handler(event, context):
    
    size = event['Records'][0]['s3']['object']['size']
    name = event['Records'][0]['s3']['object']['key']
    
    # checking
    # print(name)
    # print(size)
    
    #current date and time
    now = datetime.now()
    dateAndTime =now.strftime("%Y-%m-%d-%H-%M-%S")
    file = name + dateAndTime + ".jpg"
    
    detectFaceResponse = rekognition.detect_faces(
        Image = {
            'S3Object': {
                'Bucket': input_bucket, 
                'Name': name,
                },
            },
        )

    file_obj = s3.get_object(
        Bucket = input_bucket, 
        Key = name
    )
    
    file_content = file_obj["Body"].read()

    np_array = np.fromstring(file_content, np.uint8)
    imgcv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    origImgHeight, origImgWidth, channels = imgcv.shape
    color = (0, 255, 0)
    
    # check size
    # thresholdSize = 1500
    
    # resizing
    """
    it needs to be resized because we found out that there's issue for lambda to run for images bigger than 1mb
    but now that after giving it some thought, its only configuration issues related with lambda that can be accessed from their configuration tab
    lol oh well
    i assume its at general configuration, under the memory tab. increase that. maybe. hadn't tried
    """
    if size > 10000001: # over 1mb but dunno until what 
        scale_percent = 95
        imgWidth = int(imgcv.shape[1] * scale_percent / 100)
        imgHeight = int(imgcv.shape[0] * scale_percent / 100)
        dim = (imgWidth, imgHeight)
        resized = cv2.resize(imgcv, dim, interpolation = cv2.INTER_AREA)
        
    if size < 10000000: # below 1mb
        scale_percent = 25
        imgWidth = int(imgcv.shape[1] * scale_percent / 100)
        imgHeight = int(imgcv.shape[0] * scale_percent / 100)
        dim = (imgWidth, imgHeight)
        resized = cv2.resize(imgcv, dim, interpolation = cv2.INTER_AREA)
    
    
    for i in range(0,len(detectFaceResponse['FaceDetails'])):
        dimensions = detectFaceResponse['FaceDetails'][i]['BoundingBox']
        boxWidth = dimensions['Width']
        boxHeight = dimensions['Height']
        boxLeft = dimensions['Left']
        boxTop = dimensions['Top']
                                    
        # Plotting points of rectangle
        start_point = (int(boxLeft*imgWidth), int(boxTop*imgHeight)) 
        end_point = (int((boxLeft + boxWidth)*imgWidth), int((boxTop + boxHeight)*imgHeight))
        thickness = 2
        
        # drawing bounding box                    
        # imageRect = cv2.rectangle(imgcv, start_point, end_point, color, thickness) 
        imageRect = cv2.rectangle(resized, start_point, end_point, color, thickness) 
        cv2.imwrite("/tmp/output.jpg", imageRect)

    # upload the opencv file to s3
    s3.put_object(
        Bucket = output_bucket,
        Key = file,
        Body = open("/tmp/output.jpg", "rb").read(),
    )
        
    return{
      "statusCode": 200,
      "body" : json.dumps("Object analysed successfully!")
    }
    
