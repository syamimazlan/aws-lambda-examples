## LAYER
# must add layer via s3 bucket
import cv2
import numpy as np

import json
import boto3
import io
import logging
import argparse
logger = logging.getLogger(__name__)

from datetime import datetime

img_formats = ["jpg", "jpeg", "png"]
# change your input/output bucket
input_bucket = "kvs-rekognitionbucket"
output_bucket = "kvs-rekognition-output"

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")

# lambda main code        
def lambda_handler(event, context):
        
    size = event['Records'][0]['s3']['object']['size']
    name = event['Records'][0]['s3']['object']['key']
    creation_date = event['Records'][0]['eventTime']
        
    #current date and time
    now = datetime.now()
    dateAndTime =now.strftime("%Y-%m-%d-%H-%M-%S")
    file = name + dateAndTime + ".jpg"
    
    # if the input object is not an image, do not attempt processing
    if not any(format in name.lower() for format in img_formats):
        print("Unprocessable Entity: input object must be a jpg or png.")
        return {
            "statusCode": 422,
            "body" : json.dumps("Unprocessable Entity: input object must be a jpg or png.")
        }
    
    # if the input object is an image, prepare response
    else:
        detectLabelsResponse = rekognition.detect_labels(
            Image = {
                'S3Object': {
                    'Bucket': input_bucket,
                    'Name': name,
                }
            },
            MaxLabels = 7,
            MinConfidence = 90
        )
        
        file_obj = s3.get_object(
            Bucket = input_bucket, 
            Key = name
        )
        file_content = file_obj["Body"].read()
            
        np_array = np.fromstring(file_content, np.uint8)
        imgcv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        imgHeight, imgWidth, channels = imgcv.shape
        color = (0,255,0)
        
        # print(imgHeight)
        
        # To get the dimensions of the bounding box
        # colors = [(247, 202, 201),(146, 168, 209),(0,128, 0)]
        for i in range(0,5):
            # print(detectLabelsResponse['Labels'][i]["Instances"])
            if (len(detectLabelsResponse['Labels'][i]["Instances"]) != 0):
                noOfBoundingBox = len(detectLabelsResponse['Labels'][i]["Instances"])
                # print(noOfBoundingBox)
                
                for j in range(0, noOfBoundingBox):
                    dimensions = (detectLabelsResponse['Labels'][i]["Instances"][j]["BoundingBox"])
                    # Storing them in variables       
                    boxWidth = dimensions['Width']
                    boxHeight = dimensions['Height']
                    boxLeft = dimensions['Left']
                    boxTop = dimensions['Top']
                    
                    # Plotting points of rectangle
                    start_point = (int(boxLeft*imgWidth), int(boxTop*imgHeight)) 
                    end_point = (int((boxLeft + boxWidth)*imgWidth),int((boxTop + boxHeight)*imgHeight))
                    # Drawing Bounding Box on the coordinates
                    # color = colors[i]
                    thickness = 2
                    
                    imageRect = cv2.rectangle(imgcv, start_point, end_point, color, thickness) 
                    cv2.imwrite("/tmp/output.jpg", imageRect)
        
        # upload the opencv file to s3
        s3.put_object(
            Bucket = output_bucket,
            Key = file,
            Body = open("/tmp/output.jpg", "rb").read(),
        )
        
        return{
          "statusCode": 200,
          "body" : json.dumps("Object analyzed successfully!")
        }
