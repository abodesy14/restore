# restore

Welcome to my ELT project

<strong>Tools/Languages used:</strong>
- Python, SQL, dbt, AWS S3, DuckDB, Git, Jupyter notebooks

<strong>Setup:</strong><br>
Clone my repository with this command in your terminal: `git clone https://github.com/abodesy14/restore.git`

Once cloned, run this to install the packages used in the project: `pip install -r requirements.txt` 

My project writes results from the Random People API to AWS S3. I chose this architecture to make migration to another warehouse (if moving off DuckDB in the future) easier and to get additional experience with a cloud environment. 
To run `get_people.py`, I'll need to securely send over my AWS creds from my .env file. However, you should be able to run `agify.py` without any extra setup, as long as you’ve cloned the repo and installed the requirements.

<strong>General ELT Pipeline:</strong><br>
- Create AWS bucket
- Python script to hit random people api
- Write results to S3
- Load from S3 to duckdb
- Run `agify.py` for data enrichment

To fully automate this, I would have created a step function to run the `get_people.py` script, followed by the `agify.py` script. That was a bit of a manual process when building this out. It was easy for my age prediction table to fall behind since I could only pass in 100 names per day, while that wasn't a limitation with the random people api. 

<strong>Viewing Analysis Section:</strong><br>
To view the Analysis section of my project, go to restore -> analysis -> people_analysis.ipynb

The notebook should be pre-loaded on open. If not, click `Run All` at the top to run the entire notebook, or `ctrl+Enter` in an individual cell to run just one query. If it asks for kernel, say virtual environment (if you set one up).
