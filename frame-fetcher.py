# notes
# only runs for videos below 144p, not sure why
# https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

## LAYER
import cv2

import json
import math
import boto3
import os
import uuid

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

#hard code s3 buckets
input_bucket = "frame-fetcher"
output_bucket = "frame-fetcher-output"

def lambda_handler(event, context):
    
    try:
        file_obj = event["Records"][0]
        # input_bucket = str(file_obj["s3"]["bucket"]["name"])
        
        # extract file name from event data on trigger
        file_name = str(file_obj["s3"]["object"]["key"])
        print(f"Bucket Name: {input_bucket}\nFileName: {file_name}")

        # temporary path to save video file
        tmp_file_path = "/tmp/{}".format(file_name)
        print(f"Temporary Path: {tmp_file_path}")
        
        # downloading file to the tmp path in lambda, max is 500mb
        s3_resource.meta.client.download_file(
            input_bucket, # bucket
            file_name, # key
            tmp_file_path # location of file name
        )

        # loading video source
        capture = cv2.VideoCapture(tmp_file_path)
        
        frameCount = 0
        # frameRate = math.floor(capture.get(cv2.CAP_PROP_FPS))
        # gets the framerate one per 10 seconds
        frameRate = math.floor(capture.set(cv2.CAP_PROP_POS_MSEC, (frameCount*1000)))

        while capture.isOpened():
            # extracting frame
            # frame = [ ]
            ret, frame = capture.read()
            frameCount += 1
            # checking if video frames are empty or not
            # print(frame)
            if ret != True:
                break
            
            # capturing frame every 10 seconds
            if frameCount % (10 * frameRate) == 0:
                res, im_jpg = cv2.imencode(".jpg", frame)
                print(frame)
                print(frameRate)
                print("Read a new frame: ", frameCount) # to check if its saving each frames or not
                
                # saving frame to s3
                s3_client.put_object(
                    Bucket = output_bucket,
                    Key = "{}.jpg".format(uuid.uuid4()),
                    Body = im_jpg.tobytes(),
                )

    except Exception as e:
        print("Unable to extract frames : {}".format(e))
        return "Unable to extract frames"
