from flask import Flask, render_template, session, request, redirect, url_for,jsonify,Response
import json
import boto3
from module import ConfigController
from module import agentConfig


application = Flask(__name__)



agent = agentConfig.agent


configController = ConfigController.ConfigController()
@application.route("/",methods = ['GET'])
def getMenu():
    if request.method == 'GET':
        return render_template('amsMenu.html' , agent =agent )


@application.route("/config",methods = ['GET'])
def getConfigMenu():
    if request.method == 'GET':
        return render_template('configMenu.html' , agent = agent)


@application.route("/config/objectDetect/update",methods = ['GET'])
def getConfigObject():
    if request.method == 'GET':
        aiConfig = configController.retrieveAiConfig('objectDetection')
        return render_template('configObject.html', aiConfig = aiConfig)

@application.route("/config/memberRecognition/update",methods = ['GET'])
def getConfigFace():
    if request.method == 'GET':
        aiConfig = configController.retrieveAiConfig('faceRecognition')
        return render_template('configFace.html', aiConfig = aiConfig)

@application.route("/config/ppeDetect/update",methods = ['GET'])
def getConfigPpe():
    if request.method == 'GET':
        aiConfig = configController.retrieveAiConfig('ppeValidation')
        return render_template('configPpe.html', aiConfig = aiConfig)

@application.route("/config/fraudDetect/update",methods = ['GET'])
def getConfigAnomaly():
    if request.method == 'GET':
        aiConfig = configController.retrieveAiConfig('anomalyDetection')
        print(aiConfig)
        return render_template('configAnomaly.html', aiConfig = aiConfig)

@application.route("/config/forecast/update",methods = ['GET'])
def getConfigForecast():
    if request.method == 'GET':
        aiConfig = configController.retrieveAiConfig('forecast')
        return render_template('configForecast.html', aiConfig = aiConfig)


@application.route("/updateAiConfig",methods = ['POST'])
def updateAiConfig():
    aiConfig = json.loads(request.get_data())
    configController.updateAiConfig(aiConfig)

    return jsonify('ok')

    
if __name__ == '__main__':
    application.run( debug=True)