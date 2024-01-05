import csv
import os
import subprocess
from datetime import datetime
import json

import command

def printParameters (wineParameters, languages): 
    
    print ("Wine Parameters:")
    for key, value in wineParameters.items():
            print(f"{key}: {value}")
        
    print ("Loaded Languages: ", end='')
    for item in languages: 
        print (f"{item} ", end='')
    print ("\n")
    
def inputParameters (verbose, specify, development, production, file): 

    if file:
        return loadParamFromFile(verbose)
        
    if production: 
        return command.production()

    if development: 
        return command.development()

    info_requested = ['countries', 'minimum rating', 'maximum price', 'minimum price', 'type']
    wine_info = {}
    languageList = []

    if specify: 
        print ("Enter the following parameters (press Enter to skip):")
        for item in info_requested:
            
            user_input = input(f"Type wine {item}> ").strip()
            wine_info[item] = user_input

        selectedLanguages = input(f"Type the language codes for retrieving reviews> ").strip()
        languageList = selectedLanguages.split()


    params = {

        "wine_type_ids[]": wine_info.get('type', '').split() if wine_info.get('type') else "1",
        "country_codes[]": wine_info.get('countries', '').split() if wine_info.get('countries') else "it",

        "min_rating" :  wine_info.get('minimum ratinge') or "1",
        "price_range_min": wine_info.get('minimum price') or "10",
        "price_range_max": wine_info.get('maximum price') or "250",
    }

    checkWineTz (1, [params["price_range_min"], params["price_range_max"]])

    if languageList is None: 
        languageList.append ["en", "it"]

    if verbose: 
        printParameters(params, languageList)

    return (params, languageList)
    
def exportCSV (data, dataframe, message): 

    #* path directory definition
    directory_name = "../out"

    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except subprocess.CalledProcessError as e:
            print(f"Error in creating the directory: {e}")

    currentData = datetime.now().strftime("%d.%m")
    directory_name = f"../out/out {currentData}"

    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except subprocess.CalledProcessError as e:
            print(f"Error in creating second directory: {e}")

    directory_name = f"../out/out {currentData}/dataset {message}"

    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except subprocess.CalledProcessError as e:
            print(f"Error in creating second directory: {e}")

    name = f"../out/{directory_name}/{data}.csv"

    dataframe.to_csv (name, index=False,encoding='utf-8')

def exportParameters (wineParameters, selectedLanguages, currentTime, verbose):
    
    #* path directory definition
    directory_name = "../out"

    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except subprocess.CalledProcessError as e:
            print(f"Error in creating the directory: {e}")

    currentData = datetime.now().strftime("%d.%m")
    directory_name = f"../out/out {currentData}"

    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except subprocess.CalledProcessError as e:
            print(f"Error in creating second directory: {e}")

    directory_name = f"../out/out {currentData}/dataset {currentTime}"

    if not os.path.exists(directory_name):
        try:
            os.makedirs(directory_name)
        except subprocess.CalledProcessError as e:
            print(f"Error in creating second directory: {e}")

    name = f"../out/{directory_name}/parameters.json"
   
    with open(name, 'w') as file:
        data = {"wine_parameters": wineParameters, "languages": selectedLanguages}
        json.dump(data, file, indent=4)


def loadParamFromFile (verbose): 

    parametersUser = input("Type the name of the text file with parameters (press Enter for default): /crawler/input/")
    nameFile = "../input/" + parametersUser if parametersUser else "../input/parameters.json"

    if verbose:
        print (f"opening file: {nameFile}") 

    data = {"wine_parameters": {}, "languages": []}
    
    try:
        with open(nameFile, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File not found: {name_file}")

    wineParameters = {}
    languages = []

    wineParameters = data.get("wine_parameters", {})
    languages = data.get("languages", [])

    if verbose:
        printParameters (wineParameters, languages)

    return wineParameters, languages
