import requests
import duckdb
import pandas as pd
from time import sleep

# connect to duckdb
con = duckdb.connect("../transform/restore/random_people.duckdb") 

# get all names we've already retrieved from random people api - those are the ones we want to enrich
first_names = con.execute("SELECT DISTINCT first_name FROM people_raw limit 1").fetchall()
first_names = [name[0] for name in first_names]


# except block for first run. once table is created, then we can get existing names that have already been predicted on, and avoid duplication of requests
try:
    existing_names = con.execute("SELECT DISTINCT name FROM predicted_age").fetchall()
    existing_names = {name[0] for name in existing_names}
except duckdb.CatalogException:
    existing_names = set()

# filter to just names we haven't predicted on yet
names_to_predict = [name for name in first_names if name not in existing_names]

# query agify in batches - allows 10 names per request
age_predictions = []
base_url = "https://api.agify.io"

for i in range(0, len(names_to_predict), 10):
    batch = names_to_predict[i:i+10]
    params = [('name[]', name) for name in batch]
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        age_predictions.extend(data)
        print(f"Batch succeeded: {batch}")
    else:
        print(f"Error in batch: {response.text}")

# save predictions to duckdb
if age_predictions:
    age_df = pd.DataFrame(age_predictions)

    # created table if it doesn't exist (first run)
    con.execute("""
        CREATE TABLE IF NOT EXISTS predicted_age (
            name TEXT,
            age INTEGER,
            count INTEGER
        )
    """)

    # insert new records otherwise
    con.register("age_df_view", age_df)
    con.execute("INSERT INTO predicted_age SELECT * FROM age_df_view")

    print(f"Inserted new predictions into predicted_age.")
else:
    print("No new records to insert.")