import argparse
import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import signal
import sys

from crawio import * 
from checkCrawler import *

def signalHandler(sig, frame):
    
    print("Ctrl+C received; starting storage procedures\n")
    
    timing = datetime.now().strftime("%H.%M")
    message = "SH recovered" + " " + timing
    exportCSV ("wine", mainwine_dataframe, message)
    exportCSV ("style", mainstyle_dataframe, message)
    # exportCSV ("reviews", mainratings_dataframe, message)
    checkWineTz(4, message)

    sys.exit(0)

def getWine(wine_id, year, page):
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        }

        api_url = f"https://www.vivino.com/api/wines/{wine_id}/reviews?per_page=25&year={year}&page={page}"
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data

    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")

    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error: {json_err}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None
  
def wineCrawler (verbose, wineParameters): 

    try: 
        if verbose: 
            print ("Wine parameters loaded for scraping process:")
            printParameters(wineParameters, [None])

        # First request (reading number of matches obtained)
        req = requests.get(
                "https://www.vivino.com/api/explore/explore",
                params = wineParameters, 
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
                },
        )

        matches = req.json()['explore_vintage']['records_matched']
    
        print ("]Matches obtained: ", matches)
        checkWineTz(3, [matches,wineParameters])

        wineStyleID = set ()
    
        mainwine_dataframe = pd.DataFrame(columns=["ID", "Winery", "Name", "Year", "StyleID", "Rating", "Rates count", "Type", "Price"]) 
        mainstyle_dataframe = pd.DataFrame(columns=["ID", "Region", "Description", "Nation"]) 

        if verbose: 
            print ("___ START SCRAPING ___")

        if not verbose: 
            iteraBar = matches
            progress_bar = tqdm(total=iteraBar, desc="]drinking", unit="wine", position=0, dynamic_ncols=True)


        for i in range(1, max(1, int(matches / 25)) + 1):
            wineParameters ['page'] = i

            if verbose: 
                print (f"Scraping from {i}")

            rew = requests.get (
                "https://www.vivino.com/api/explore/explore",
                params = wineParameters, 
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
                },
            )

            #!TODO getting alchol gradation

            # To print the json structure:
            """"
            all_wines_data = rew.json()["explore_vintage"]["matches"]
            print (json.dumps(all_wines_data[0], indent=4))
            for i in range (len(all_wines_data)): 
                print(json.dumps(all_wines_data[i], indent=4))
            
            quit()
            """

            for t in rew.json()["explore_vintage"]["matches"]: 
                
                if "vintage" in t and t["vintage"]:
                    if "wine" in t["vintage"] and t["vintage"]["wine"]:
                        if "style" in t["vintage"]["wine"] and t["vintage"]["wine"]["style"]:
                            
                            # Acquisition of wine style:
                            styleID = t["vintage"]["wine"]["style"]["id"]
                            if styleID not in wineStyleID: 
                                wineStyleID.add(styleID)

                                styleData = [(
                                    t["vintage"]["wine"]["style"]["id"],
                                    t["vintage"]["wine"]["style"]["regional_name"],
                                    t["vintage"]["wine"]["style"]["description"],
                                    t["vintage"]["wine"]["style"]["country"]["code"]
                                    )
                                ]
                                styleDataframe = pd.DataFrame(
                                    styleData,
                                    columns=["ID", "Region", "Description", "Nation"]
                                ) 
                                mainstyle_dataframe = pd.concat([mainstyle_dataframe, styleDataframe], ignore_index=True)

                            # Wine data acquisition:
                            wineData = [ (
                                    t["vintage"]["wine"]["id"],
                                    t["vintage"]["wine"]["winery"]["name"],
                                    t["vintage"]["wine"]["name"],
                                    t["vintage"]["year"],
                                    t["vintage"]["wine"]["style"]["id"],
                                    t["vintage"]["statistics"]["ratings_average"],
                                    t["vintage"]["statistics"]["ratings_count"],
                                    t["vintage"]["wine"]["type_id"],
                                    t["price"]["amount"]
                                    # alchol gradation
                                    )
                            ]
                            wineData = pd.DataFrame(
                                wineData,
                                columns=["ID", "Winery", "Name", "Year", "Style", "Rating", "Rates count", "Type", "Price"],
                            )

                            if not mainwine_dataframe.empty:
                                mainwine_dataframe = pd.concat([mainwine_dataframe, wineData], ignore_index=True)
                            else:
                                mainwine_dataframe = wineData.copy()
                    
                            if verbose: 
                                print(f"Size of main dataframe after page {i}: {len(mainwine_dataframe)}")

                            if not verbose: 
                                progress_bar.update(1)

                        else:
                            continue
                    else:
                        continue
                else:
                    continue

        if not verbose: 
            progress_bar.close()

        mainwine_dataframe = mainwine_dataframe.drop_duplicates(subset="ID")
        
        if verbose:
            print ("___ END SCRAPING ___")

    except Exception as e: 
        
        print ("Relative exception: ", e)

        if not verbose: 
            progress_bar.close()

        print ("saving with exception...")
        mainwine_dataframe = mainwine_dataframe.drop_duplicates(subset="ID")
        timing = datetime.now().strftime("%H.%M")
        message = "recovered" + " " + timing
        exportCSV ("wine", mainwine_dataframe, message)
        exportCSV ("style", mainstyle_dataframe, message)

        checkWineTz(4, message)
    
    return mainwine_dataframe, mainstyle_dataframe
    
def reviewsCrawler (verbose, wineDF, selectedLanguages): 
    
    if verbose: 
        print ("Start reviews crawling...\n")
    
    mainratings_dataframe = pd.DataFrame(columns=["idRev", "Language", "idWine", "User Rating", "Note", "CreatedAt"])

    if not verbose: 
        iteraBar = len (wineDF)
        progress_bar = tqdm(total=iteraBar, desc="]singing: ", unit="wine", position=0, dynamic_ncols=True, bar_format="{desc}{percentage:3.0f}%|{bar}  {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {postfix}]")
    try: 
        for _, row in wineDF.iterrows():
            page = 1
            while True:
            
                if verbose: 
                    print(f'Getting info about wine {row["ID"]}-{row["Year"]} Page {page}')

                d = getWine(row["ID"], row["Year"], page)

                if d is None: 

                    print ("] ERRROR occurred while downloading reviews; data should have been stored.")
                    
                    timing = datetime.now().strftime("%H.%M")
                    message = "recovered" + " " + timing
                    exportCSV ("reviews", mainratings_dataframe, message)
                    checkWineTz(4, message)

                if not d["reviews"]:
                    
                    if not verbose:
                        progress_bar.set_description(f"]singing") 
                    
                    break

                for r in d["reviews"]:
                    
                    if r["language"] not in selectedLanguages:
                        continue

                    if r['note']:
                        if len(r['note']) < 100:
                            continue
                
                    reviewsData = [
                        (   
                            r["id"],
                            r["language"],
                            row["ID"],
                            r["rating"],
                            r["note"],
                            r["created_at"],
                        )
                    ]
                    
                    reviewsData = pd.DataFrame(
                        reviewsData, 
                        columns=["idRev", "Language", "idWine", "User Rating", "Note", "CreatedAt"]
                    )

                    if not mainratings_dataframe.empty:
                        mainratings_dataframe = pd.concat([mainratings_dataframe, reviewsData], ignore_index=True)
                    else:
                        mainratings_dataframe = reviewsData.copy()
                page += 1
            
            if not verbose: 
                progress_bar.update(1)
                progress_bar.set_postfix(rev = len(mainratings_dataframe), refresh=True)

        
        if not verbose: 
            progress_bar.close()
    
    except Exception as e:

        print ("Relative exception: ", e)

        if not verbose: 
            progress_bar.close()
        
        print ("saving with exception...")
        timing = datetime.now().strftime("%H.%M")
        message = "recovered" + " " + timing
        exportCSV ("reviews", mainratings_dataframe, message)
        checkWineTz(4, message)

    return mainratings_dataframe

def main (verbose, reset, specify, development, production, file): 

    if reset: 
        resetInfo()

    currentTime = datetime.now().strftime("%H.%M")
    
    (wineParameters, selectedLanguages) = inputParameters (verbose, specify, development, production, file)
    exportParameters(wineParameters, selectedLanguages, currentTime, verbose)

    wineDF, styleDF = wineCrawler (verbose, wineParameters)

    checkWineTz(2, ["wine", wineDF])
    exportCSV ("wine", wineDF, currentTime)
    
    checkWineTz(2, ["style", styleDF])
    exportCSV ("style", styleDF, currentTime)

    reviewsDF = reviewsCrawler (verbose, wineDF, selectedLanguages)
    checkWineTz(2, ["reviews", reviewsDF])

    exportCSV ("reviews", reviewsDF, currentTime)

    print ("]datasets exported successfully")

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, signalHandler)

    parser = argparse.ArgumentParser(description="WineTz Crawler v.2")
    parser.add_argument("-d", "--development", action="store_true", help="debug function for developer")
    parser.add_argument("-s", "--specify", action="store_true", help="specify filter for wine search")
    parser.add_argument("-f", "--file", action="store_true", help="load filter for wine search from file")
    parser.add_argument("-p", "--production", action="store_true", help="production")
    parser.add_argument("-v", "--verbose", action="store_true", help="additional prints")
    parser.add_argument("-r", "--reset", action="store_true", help="reset directory out/")

    args = parser.parse_args()

    if not (args.development or args.specify or args.production or args.reset or args.file):
        parser.print_help()
        checkWineTz(0, "options")

    main(args.verbose, args.reset, args.specify, args.development, args.production, args.file)