import boto3
import base64
import copy
from datetime import datetime
import json
import psycopg2

class PpeDetect:
    def __init__(self, dataModel, aws_access_key_id, aws_secret_access_key, region_name,table):
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__region_name = region_name
        self.__dynamoDbResource = boto3.resource(
            'dynamodb', 
            aws_access_key_id=self.__aws_access_key_id, 
            aws_secret_access_key=self.__aws_secret_access_key,
            region_name=self.__region_name
        )
        self.__dataModel = dataModel
        self.__table = self.__dynamoDbResource.Table(table)
        
        self.__outputModel = {
            "capture":{
                "frameId": dataModel["frame"]["captureResult"]["id"],
                "timestamp": dataModel["frame"]["captureResult"]["timestamp"],
                "sourceImageUrl":""
            },
            "ppeDetection":{
                "personCount":0,
                "validPpeCount":0
            },
            "personList":[],
            "config":{
                "maskDetection":None,
                "helmetDetection":None,
                "glovesDetection":None
            }
        }
    
    def storeImage(self):
        client = boto3.client('s3', aws_access_key_id=self.__aws_access_key_id, aws_secret_access_key=self.__aws_secret_access_key,region_name=self.__region_name)
        image = self.__dataModel["frame"]["openCV"]["imageBase64"]
        image = base64.b64decode(image)
        fileName = self.__dataModel["frame"]["captureResult"]["id"]
        bucketName = "face-images-t3"
        client.put_object(ACL='public-read',Body=image, Bucket=bucketName, Key=fileName ,ContentEncoding='base64',ContentType='image/jpeg')
        self.__outputModel["capture"]["sourceImageUrl"] = 'https://' + bucketName + '.s3-' + self.__region_name + '.amazonaws.com/' + fileName
    
    def ppeDetect(self):
        image = self.__dataModel["frame"]["openCV"]["imageBase64"]
        self.__client = boto3.client('rekognition',aws_access_key_id=self.__aws_access_key_id, aws_secret_access_key=self.__aws_secret_access_key,region_name=self.__region_name)
        response = self.__client.detect_protective_equipment(Image={'S3Object':{'Bucket':"face-images-t3",'Name':self.__dataModel["frame"]["captureResult"]["id"]}},
                                                            SummarizationAttributes={'MinConfidence':70, 'RequiredEquipmentTypes':['FACE_COVER', 'HAND_COVER', 'HEAD_COVER']}
        )
        emptyModel = {}
        self.__outputModel["ppeDetection"]["personCount"] = len(response["Persons"])
        for person in response["Persons"]:
            personModel = copy.deepcopy(emptyModel)
            personModel["location"] = {
                "X": person["BoundingBox"]["Left"] + 0.5 *  person["BoundingBox"]["Width"],
                "Y": person["BoundingBox"]["Top"] + 0.5 *  person["BoundingBox"]["Height"]
            }
            personModel["confidence"] = person["Confidence"]
            personModel["ppeResult"] = {
                "face":{
                    "face_cover":False,
                    "face_cover_confidence":0
                },
                "head":{
                    "head_cover":False,
                    "head_cover_confidence":0
                },
                "left_hand":{
                    "left_hand_cover":False,
                    "left_hand_cover_confidence":0
                },
                "right_hand":{
                    "right_hand_cover":False,
                    "right_hand_cover_confidence":0
                }
            }
            
            for bodyPart in person["BodyParts"]:
                if (bodyPart["Name"] == "FACE") and (len(bodyPart["EquipmentDetections"])!=0):
                    personModel["ppeResult"]["face"]["face_cover"] = True
                    personModel["ppeResult"]["face"]["face_cover_confidence"] = bodyPart["EquipmentDetections"][0]["Confidence"]
                    
                if (bodyPart["Name"] == "HEAD") and (len(bodyPart["EquipmentDetections"])!=0):
                    personModel["ppeResult"]["head"]["head_cover"] = True
                    personModel["ppeResult"]["head"]["head_cover_confidence"] = bodyPart["EquipmentDetections"][0]["Confidence"]
                    
                if (bodyPart["Name"] == "LEFT_HAND") and (len(bodyPart["EquipmentDetections"])!=0):
                    personModel["ppeResult"]["left_hand"]["left_hand_cover"] = True
                    personModel["ppeResult"]["left_hand"]["left_hand_cover_confidence"] = bodyPart["EquipmentDetections"][0]["Confidence"]
                    
                if (bodyPart["Name"] == "RIGHT_HAND") and (len(bodyPart["EquipmentDetections"])!=0):
                    personModel["ppeResult"]["right_hand"]["right_hand_cover"] = True
                    personModel["ppeResult"]["right_hand"]["right_hand_cover_confidence"] = bodyPart["EquipmentDetections"][0]["Confidence"]
                        
            personModel["validPpe"] = True
            if ((self.__dataModel["config"]["maskDetection"]==True)and(personModel["ppeResult"]["face"]["face_cover"]==False)
            or (self.__dataModel["config"]["helmetDetection"]==True)and(personModel["ppeResult"]["head"]["head_cover"]==False)
            or (self.__dataModel["config"]["glovesDetection"]==True)and(personModel["ppeResult"]["left_hand"]["left_hand_cover"]==False)
            or (self.__dataModel["config"]["glovesDetection"]==True)and(personModel["ppeResult"]["right_hand"]["right_hand_cover"]==False)):
                personModel["validPpe"] = False
                
            if personModel["validPpe"] == True:
                self.__outputModel["ppeDetection"]["validPpeCount"] = self.__outputModel["ppeDetection"]["validPpeCount"] +1
            
            self.__outputModel["personList"].append(personModel)
    def query_config(self):
        response = self.__table.get_item(
            Key={
                'agent': self.__dataModel["agent"],
            }
        )

        item = response['Item']
        #print(item)
        aiConfig = item['aiApps']['ppeValidation']
        self.__dataModel["config"] = aiConfig
        #print(aiConfig)

    def getModel(self):
        self.__outputModel["config"]["maskDetection"] = self.__dataModel["config"]["maskDetection"]
        self.__outputModel["config"]["helmetDetection"] = self.__dataModel["config"]["helmetDetection"]
        self.__outputModel["config"]["glovesDetection"] = self.__dataModel["config"]["glovesDetection"]
        return self.__outputModel
    
    def redshiftInject(self):
        
        # model = json.loads(event)
        conn = psycopg2.connect(dbname='dev', host="demo0206.cec0m4zxpcqk.us-west-2.redshift.amazonaws.com", port='5439', user='awsuser', password='Ilab1624taipeitech')
        cur = conn.cursor();    
        
        for i in range(self.__outputModel['ppeDetection']['personCount']):
         
              
            cur.execute("insert into ppeAnalytics ("+
            "frameid,"+
            "frametimestamp,"+
            "sourceImageurl,"+
            "personcount,"+
            "validppecount,"+
            
            "facecover,"+
            "facecoverconfidence,"+
            "headcover,"+
            "headcoverconfidence,"+
            
            "lefthandcover,"+
            "lefthandconfidence,"+
            "righthandcover,"+
            "righthandconfidence,"+
            
            
            "isPass)"+
            
            "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                self.__outputModel['capture']['frameId'],
                datetime.utcfromtimestamp(int(self.__outputModel['capture']['timestamp'])+ 28800),
                self.__outputModel['capture']['sourceImageUrl'],
                self.__outputModel['ppeDetection']['personCount'],
                self.__outputModel['ppeDetection']['validPpeCount'],
                
                self.__outputModel['personList'][i]['ppeResult']['face']['face_cover'],
                ((round(self.__outputModel['personList'][i]['ppeResult']['face']['face_cover_confidence'],2))/100),
                self.__outputModel['personList'][i]['ppeResult']['head']['head_cover'],
                ((round(self.__outputModel['personList'][i]['ppeResult']['head']['head_cover_confidence'],2))/100),
                
                self.__outputModel['personList'][i]['ppeResult']['left_hand']['left_hand_cover'],
                ((round(self.__outputModel['personList'][i]['ppeResult']['left_hand']['left_hand_cover_confidence'],2))/100),
                self.__outputModel['personList'][i]['ppeResult']['right_hand']['right_hand_cover'],
                ((round(self.__outputModel['personList'][i]['ppeResult']['right_hand']['right_hand_cover_confidence'],2))/100),
                self.__outputModel['personList'][i]['validPpe']
                
                ))
        
            conn.commit()
