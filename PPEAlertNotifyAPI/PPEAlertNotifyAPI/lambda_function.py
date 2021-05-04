import json
import time

import config
from notification import SourceImageMessage, ValidationResultMessage, AlertNotify


def lambda_handler(event, context):
    dataModel = json.loads(event)
    '''
    s3_client = boto3.client(
                    's3', 
                    aws_access_key_id=config.awsAccessKey,
                    aws_secret_access_key=config.awsSecretKey
                )
    
    csv_obj = s3_client.get_object(Bucket=config.awsS3Bucket, Key=config.awsS3FileKey)
    body = csv_obj['Body']
    json_string = body.read().decode('utf-8')
    history_data = json.loads(json_string)
    body.close()
    
    if (dataModel['ppeDetection']['personCount'] == 0 or time.time() - history_data['ppeLastPushTimestamp'] > 10):
        history_data['ppeCanPush'] = True
        s3_client.put_object(
            Bucket=config.awsS3Bucket,
            Key=config.awsS3FileKey, 
            Body=json.dumps(history_data), 
            ACL='public-read', 
            ContentType = 'text/json'
        )
    '''
    
    if (dataModel['ppeDetection']['personCount'] > 0):
        # declare classes
        sourceImageMessage = SourceImageMessage(dataModel)
        validationResultMessage = ValidationResultMessage(dataModel)
        alertNotify = AlertNotify(sourceImageMessage, validationResultMessage)
        
        # send messages to receiver
        pushResult = alertNotify.pushMessages()
        
        '''
        history_data['ppeCanPush'] = False
        history_data['ppeLastPushTimestamp'] = time.time()
        s3_client.put_object(
            Bucket=config.awsS3Bucket,
            Key=config.awsS3FileKey, 
            Body=json.dumps(history_data), 
            ACL='public-read', 
            ContentType = 'text/json'
        )
        '''
    
    else:
        pushResult = 'Not push'
    
        print(pushResult)
    
    return pushResult