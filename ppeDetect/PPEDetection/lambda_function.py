import json
from ppeDetection import PpeDetect
import config

def lambda_handler(event, context):
    print(event)
    dataModel = event
    ppeDetection =  PpeDetect(dataModel, config.aws_access_key_id, config.aws_secret_access_key, config.region_name,config.table)
    ppeDetection.query_config()
    ppeDetection.storeImage()
    ppeDetection.ppeDetect()
    ppeDetection.redshiftInject()
    
    return ppeDetection.getModel()