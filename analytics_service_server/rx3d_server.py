
from flask import Flask, request, jsonify, send_file, render_template, redirect
from flask_cors import CORS

from flask_jwt_extended import (
    JWTManager, jwt_required, jwt_optional, create_access_token,
    get_jwt_identity
)

import json
import datetime
import requests
import secrets

import numpy as np

productionServer = True

app = Flask(__name__,  template_folder='./templates')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if not productionServer:
    CORS(app)  # cross-domain access for testing purposes (not in production!)

apiPrefix = "/api"

@app.route(apiPrefix + "/tags/", methods=['GET'])
def getAvailableTags():
  ans = "s2"
  response = app.response_class(
        response=ans,
        status=200,
        mimetype='application/json'
  )
  return response

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

@app.route(apiPrefix + "/treatmants-risks/", methods=['POST'])
def analyseAgeCondition():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    caseList = request.json["data"]

    Hstay = np.zeros(len(caseList), dtype=np.integer)
    ICUstay = np.zeros(len(caseList), dtype=np.integer)
    ICUindex = 0
    deaths = 0
    for i, patient in enumerate(caseList):
        Hstay[i] = (patient["hospitalRelease"] - patient["hospitalAdmission"]) \
            /(60*60*24*1000) # conver miliseconds to days
        if ("icuAdmission" in patient) and  patient["icuAdmission"] is not None:
            ICUstay[ICUindex] = (patient["icuRelease"] - patient["icuAdmission"]) \
                /(60*60*24*1000) # conver miliseconds to days
            ICUindex += 1
        if patient["outcomeType"] == 1:  # patient died
            deaths += 1

    MeanICU = ICUindex / len(caseList)
    ICUstay = ICUstay[:ICUindex]

    # CALCULATE AND DISPLAY STATISTICS FOR THE WHOLE DATASET
    MeanHstay = np.mean(Hstay)
    StdHstay = np.std(Hstay)

    # CALCULATE AND DISPLAY STATISTICS FOR THE WHOLE DATASET
    MeanICUstay = np.mean(ICUstay)
    StdICUstay = np.std(ICUstay)

    DeathRate = deaths / len(caseList)

    ICUstay = ICUstay.tolist()

    # DRUG list

    drugs_died = {}
    drugs_survived = {}

    for patient in caseList:
        drugList = set()
        for drug in patient["existingTherapyDrugs"]:
            if drug["name"] not in drugList:
                drugList.add(drug["name"])
        for day in patient["detailsOnProgression"]:
            for drug in day["drugs"]:
                if drug["name"] not in drugList:
                    drugList.add(drug["name"])

        for d in drugList:
            if d not in drugs_died:
                drugs_died[d] = 0
                drugs_survived[d] = 0
            if patient["outcomeType"]==0:
                drugs_survived[d] += 1
            else:
                drugs_died[d] += 1

    drugs_survival = {}

    for key in drugs_died:
        totalCases = drugs_survived[key] + drugs_died[key]
        drugs_survival[key] = [drugs_survived[key] / totalCases, totalCases]

    # SORT RESULTS
    drugs_survival = {k: v for k, v in sorted(drugs_survival.items(), key=lambda item: item[1],reverse=True)}

    # COMPLICATION list


    complicationList = {}

    for patient in caseList:
        complications = set()

        for day in patient["detailsOnProgression"]:
            for condition in day["conditions"]:
                if condition not in complications:
                    complications.add(condition)

        for c in complications:
            if c in complicationList:
                complicationList[c] += 1
            else:
                complicationList[c] = 1.

    totalCases = len(caseList)
    sortedComplicationList = {k: v/totalCases for k, v in sorted(complicationList.items(), key=lambda item: item[1],reverse=True)}

    ICUhistogram = np.zeros(100, dtype=np.integer)
    HstayHistogram = np.zeros(100, dtype=np.integer)
    for v in ICUstay:
        ICUhistogram[v] += 1
    for v in Hstay:
        HstayHistogram[v] += 1

    ExportData = {"Hospitalization" : {"Hospital_Stays_DURATIONS":HstayHistogram,
                                        "Mean_Hospital_Stay":MeanHstay,
                                        "SandDev_Hospital_Stays":StdHstay},
                   "ICU" : {"ICU_Rate":MeanICU,
                            "ICU_Stays_DURATIONS":ICUhistogram,
                            "Mean_ICU_Stay":MeanICUstay,
                            "SandDev_ICU_Stays":StdICUstay},
                   "Survival_Rate":{"Survival":(1.0-DeathRate)},
                   "Treatmant_List":drugs_survival,
                   "Complication_List":sortedComplicationList
                   }


    response = app.response_class(
        response=json.dumps(ExportData,indent=4, cls=NumpyEncoder),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route(apiPrefix + "/drug-dose/", methods=['POST'])
def analyseTreatmant():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    caseList = request.json["data"]
    commonDrug = request.json["commonDrugs"][0]

    Hstay = np.zeros(len(caseList), dtype=np.integer)
    ICUstay = np.zeros(len(caseList), dtype=np.integer)
    ICUindex = 0
    deaths = 0
    for i, patient in enumerate(caseList):
        Hstay[i] = (patient["hospitalRelease"] - patient["hospitalAdmission"]) \
            /(60*60*24*1000) # conver miliseconds to days
        if ("icuAdmission" in patient) and  patient["icuAdmission"] is not None:
            ICUstay[ICUindex] = (patient["icuRelease"] - patient["icuAdmission"]) \
                /(60*60*24*1000) # conver miliseconds to days
            ICUindex += 1
        if patient["outcomeType"] == 1:  # patient died
            deaths += 1

    MeanICU = ICUindex / len(caseList)
    ICUstay = ICUstay[:ICUindex]

    # CALCULATE AND DISPLAY STATISTICS FOR THE WHOLE DATASET
    MeanHstay = np.mean(Hstay)
    StdHstay = np.std(Hstay)

    # CALCULATE AND DISPLAY STATISTICS FOR THE WHOLE DATASET
    MeanICUstay = np.mean(ICUstay)
    StdICUstay = np.std(ICUstay)

    DeathRate = deaths / len(caseList)

    ICUstay = ICUstay.tolist()

    print(ICUstay)

    # DRUG COMBINATIONS AND DOSES

    ## NOTE: only one drug can be correlated in this version

    drugs_died = {}
    drugs_survived = {}

    for patient in caseList:
        print(patient["yearOfBirth"])
        drugList = set()
        fulfilledDrug = False
        nameFullfiled = ""
        for drug in patient["existingTherapyDrugs"]:
            name = drug["name"] + " " + drug["doses"]
            if drug["name"]==commonDrug:
                fulfilledDrug = True
                nameFullfiled = name
            if name not in drugList:
                drugList.add(name)

        if fulfilledDrug:
            for day in patient["detailsOnProgression"]:
                for drug in day["drugs"]:
                    name = nameFullfiled + " + "+ drug["name"] + " " + drug["doses"]
                    if name not in drugList:
                        drugList.add(name)
        else:
            for day in patient["detailsOnProgression"]:
                for i, drug in enumerate(day["drugs"]):
                    if drug["name"]==commonDrug:
                        name = drug["name"] + drug["dose"]
                        if name not in drugList:
                            drugList.add(name)
                        for j, drug2 in enumerate(day["drugs"]):
                            if i!=j:
                                name = drug["name"] +" "+ drug["dose"] +\
                                " + " +drug2["name"] +" "+ drug2["dose"]
                                if name not in drugList:
                                    drugList.add(name)

        for d in drugList:
            if d not in drugs_died:
                drugs_died[d] = 0
                drugs_survived[d] = 0
            if patient["outcomeType"]==0:
                drugs_survived[d] += 1
            else:
                drugs_died[d] += 1


    print(drugs_died)
    print(drugs_survived)

    drugs_survival = {}

    for key in drugs_died:
        totalCases = drugs_survived[key] + drugs_died[key]
        drugs_survival[key] = [drugs_survived[key] / totalCases, totalCases]

    # SORT RESULTS
    drugs_survival = {k: v for k, v in sorted(drugs_survival.items(), key=lambda item: item[1],reverse=True)}

    # COMPLICATION list

    complicationList = {}

    for patient in caseList:
        complications = set()

        for day in patient["detailsOnProgression"]:
            for condition in day["conditions"]:
                if condition not in complications:
                    complications.add(condition)

        for c in complications:
            if c in complicationList:
                complicationList[c] += 1
            else:
                complicationList[c] = 1.

    totalCases = len(caseList)
    sortedComplicationList = {k: v/totalCases for k, v in sorted(complicationList.items(), key=lambda item: item[1],reverse=True)}

    ICUhistogram = np.zeros(100, dtype=np.integer)
    HstayHistogram = np.zeros(100, dtype=np.integer)
    for v in ICUstay:
        ICUhistogram[v] += 1
    for v in Hstay:
        HstayHistogram[v] += 1

    ExportData = {"Hospitalization" : {"Hospital_Stays_DURATIONS":HstayHistogram,
                                        "Mean_Hospital_Stay":MeanHstay,
                                        "SandDev_Hospital_Stays":StdHstay},
                   "ICU" : {"ICU_Rate":MeanICU,
                            "ICU_Stays_DURATIONS":ICUhistogram,
                            "Mean_ICU_Stay":MeanICUstay,
                            "SandDev_ICU_Stays":StdICUstay},
                   "Survival_Rate":{"Survival":(1.0-DeathRate)},
                   "Treatmant_List":drugs_survival,
                   "Complication_List":sortedComplicationList
                   }

    print(ExportData)

    response = app.response_class(
        response=json.dumps(ExportData,indent=4, cls=NumpyEncoder),
        status=200,
        mimetype='application/json'
    )
    return response
