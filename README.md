# KVS-Rekognition-Lambda
## Intro
This is for a system that recognises cars using AWS Rekognition. The images of cars are passed from AWS Kinesis into AWS Rekognition that is invoked using AWS Lambda when images entered AWS S3.

## Done
1. Lambda is invoked when images are saved inside S3.

## Issues/Problems
1. Couldn't output the bounding box by using Lambda.
2. Couldn't add layers into Lambda.

## Try
1. Using ECS(?)



# References
1. [AWS Documentation](https://docs.aws.amazon.com/rekognition/latest/dg/labels-detect-labels-image.html)
