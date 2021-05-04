from . import dynamodbConfig
import boto3


class DynamoDB:
    def __init__(self):
        self.__regionName = dynamodbConfig.regionName
        self.__aws_access_key_id = dynamodbConfig.aws_access_key_id
        self.__aws_secret_access_key = dynamodbConfig.aws_secret_access_key
        self.__dynamoDbResource = boto3.resource(
            'dynamodb', 
            aws_access_key_id=self.__aws_access_key_id, 
            aws_secret_access_key=self.__aws_secret_access_key,
            region_name=self.__regionName
        )
        self.__table = self.__dynamoDbResource.Table(dynamodbConfig.table)

    def updateAiDynamoDbConfig(self,aiDynamoDbConfig):
        self.__table.update_item(
            Key={
                'agent':aiDynamoDbConfig['agent'],

            },
            UpdateExpression='SET aiApps.' + aiDynamoDbConfig['aiApp'] + '.' + aiDynamoDbConfig['key'] + ' = :value',
            ExpressionAttributeValues={
                ':value': aiDynamoDbConfig['value']
            }
        )

    def retrieveAiConfig(self, agent, aiApp):
        response = self.__table.get_item(
            Key={
                'agent': agent,
            }
        )

        item = response['Item']
        aiConfig = item['aiApps'][aiApp]
        print(aiConfig)

        return aiConfig

    def insertConfig(self,config):
        self.__table.put_item(
           Item = config
        )