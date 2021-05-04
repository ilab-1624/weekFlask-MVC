from . import DynamoDB
from . import agentConfig


class ConfigController:
    def __init__(self):
        self.__agent = agentConfig.agent
        self.__dynamodb = DynamoDB.DynamoDB()

    def updateAiConfig(self,aiConfig):
        aiDynamoDbConfig = {
            "agent":self.__agent,
            "aiApp":aiConfig['aiApp'],
            "key":aiConfig['key'],
            "value":aiConfig['value']
        }

        self.__dynamodb.updateAiDynamoDbConfig(aiDynamoDbConfig)

    def retrieveAiConfig(self,aiApp):
        aiConfig = self.__dynamodb.retrieveAiConfig(self.__agent, aiApp)
        return aiConfig