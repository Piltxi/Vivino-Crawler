import os
import subprocess
    
def resetInfo (): 
    
    if os.path.exists("../out"):
        try:
            subprocess.run(["rm", "-fr", "../out"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error in removing the existing directory: {e}")

    print ("reset dataset and ./out folder")
    quit()
    
def checkWineTz (arg, data): 
    
    match arg: 

        case 0: 
            print ("\nERROR 00 - WineTz crashed.\n You must specify filtering options.")
            quit()

        case 1: 
            if float(data[0]) > float(data[1]): 
                print (f"ERROR 01 - Loading Price {data[0]} > {data[1]} .\n")
                quit()
        
        case 2: 
            if data[1].empty: 
                print (f"ERROR 02 - {data[0]} Dataframe")
                quit()

        case 3: 
            
            if data[0] == 0:
                print (f"ERROR 03 - No results match your search criteria:\n")

                print ("Wine parameters loaded for scraping process:")
                for key, value in data[1].items():
                    print(f"{key}: {value}")

                quit()

        case 4: 

            print (f"\nyou turned off WineTz. emergency export and shutdown: check on /out/dataset {data}\nthe directory may be overwritten. if you need the exported data, make a backup of the dataset.")
            quit()

        case _: 
            print ("\nUNKNOW ERROR XY")
            quit ()
