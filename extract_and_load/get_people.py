# ingest from random person api

# requirements
import requests
import pandas as pd
import duckdb
from datetime import datetime
import os
import boto3
import io
from dotenv import load_dotenv

# load environment variables for aws keys
load_dotenv()

# grab 50 people at a time to build up a dataset
base_url = 'https://randomuser.me/api/?results=50'

response = requests.get(base_url)
people_data = response.json()

person_dicts = []

# person = people_data['results'][0]

for person in people_data['results']:
    person_dict = {
        'gender': person['gender'],
        'title': person['name']['title'],
        'first_name': person['name']['first'],
        'last_name': person['name']['last'],
        'address_street_number': person['location']['street']['number'],
        'address_street_name': person['location']['street']['name'],
        'address_city': person['location']['city'],
        'address_state': person['location']['state'],
        'address_country': person['location']['country'],
        'address_postcode': person['location']['postcode'],
        'address_latitude': person['location']['coordinates']['latitude'],
        'address_longitude': person['location']['coordinates']['longitude'],
        'timezone_offset': person['location']['timezone']['offset'],
        'timezone_description': person['location']['timezone']['description'],
        'email': person['email'],
        'uuid': person['login']['uuid'],
        'username': person['login']['username'],
        'password': person['login']['password'],
        'password_salt': person['login']['salt'],
        'md5': person['login']['md5'],
        'sha1': person['login']['sha1'],
        'sha256': person['login']['sha256'],
        'dob': person['dob']['date'],
        'age': person['dob']['age'],
        'registered_date': person['registered']['date'],
        'registered_age': person['registered']['age'],
        'phone': person['phone'],
        'cell': person['cell'],
        'ssn_type': person['id']['name'],
        'ssn': person['id']['value'],
        'picture_large': person['picture']['large'],
        'picture_medium': person['picture']['medium'],
        'picture_thumbnail': person['picture']['thumbnail'],
        'nationality': person['nat'],
        'processed_ts': datetime.utcnow().isoformat()
    }

    person_dicts.append(person_dict)

people_df = pd.DataFrame(person_dicts)

# make address_postcode a string for when double quoted numbers/alphanumeric characters appear
people_df['address_postcode'] = people_df['address_postcode'].astype(str)



# load section
# write to parquet files
buffer = io.BytesIO()
people_df.to_parquet(buffer, index=False, engine='pyarrow')
buffer.seek(0)

# intialize to interact with s3
s3 = boto3.client('s3')
bucket_name = 'restore-lions'
s3_key = f"raw/people/person_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"

s3.upload_fileobj(buffer, bucket_name, s3_key)

print(f"Uploaded to s3://{bucket_name}/{s3_key}")



# create duckdb connection and read from s3
con = duckdb.connect("/Users/adambeaudet/Github/restore/transform/restore/random_people.duckdb")

con.execute(f"""
    SET s3_region='{os.environ['AWS_REGION']}';
    SET s3_access_key_id='{os.environ['AWS_ACCESS_KEY_ID']}';
    SET s3_secret_access_key='{os.environ['AWS_SECRET_ACCESS_KEY']}';
""")

con.execute("""
    CREATE OR REPLACE TABLE people_raw AS
    SELECT * FROM read_parquet('s3://restore-lions/raw/people/*.parquet',
    union_by_name=True) 
""")

print("DuckDB external table 'people_raw' created successfully.")