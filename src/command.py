def development (): 
    params = {

        "wine_type_ids[]": ["1"], 
        "country_codes[]":["it"],

        "min_rating" : "4.2",
        "price_range_max": "9",

        } 
    languageList = ["it"]
    return params, languageList

def production (): 
    params = {

        "wine_type_ids[]": ["4"],
        "country_codes[]": ["it"],

        "price_range_max": "200",
        } 

    languageList = ["it"]

    return params, languageList

if __name__ == "__main__":
    raise ImportError("This is not an executable program: run searcher.py")
