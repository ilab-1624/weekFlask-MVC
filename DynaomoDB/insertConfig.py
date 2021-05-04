from module import DynamoDB
from module import agentConfig

dynamodb = DynamoDB.DynamoDB()

config = {
    "agent": agentConfig.agent,
    "sites":[],
    "aiApps":{
        "objectDetection":{
            "cameraObscuredThreshold":30,
            "cameraOffsetThreshold":30,
            "cameraOffsetMaxAngle":30,
            "anomalyObjectThreshold":30,
            "backgroundObjectThreshold":30
        },
        "faceRecognition":{
            "similarityThreshold":60
        },
        "ppeValidation":{
            "maskDetection":True,
            "helmetDetection":True,
            "glovesDetection":False
        },
        "anomalyDetection":{
            "memberDetection":True,
            "nonMemberDetection":True,
            "crossLeftLineAlert":False,
            "crossRightLineAlert":False
        },
        "forecast":{
            "confidence":80
        }
    }
}


dynamodb.insertConfig(config)