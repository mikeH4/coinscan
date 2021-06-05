# coinscan

Main Coin Scan repository that contains code for the api, and main processes of the coinscan backend

## Clone

1. Navigate into this dir

2. Create a virtual env
`python3 -m venv env`

3. Activate virtual env
`source env/bin/activate`

4. Install Dependencies
`pip3 install -r requirements.txt`

5. Run `python3 cmd.py` optionally specifiying a script after, for example: `python3 cmd.py service`

6. Run API using `uvicorn api:app --reload`