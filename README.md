[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/bknTyRar)
# Event Planner using Django & Heroku

__Name (Computing id):__ Paul Rosa (pir3sw), Owen Badgley (thm9hh), Austin Mo(utw3ey), Sebastian Shirazi (byr5uk), Davis Wang (bqe6ue)

### When running locally
run `python -m venv .venv` to make virtual env, then `source .venv/bin/activate` to use it.
After that run `pip install -r requirements.txt` to get the requirements in the venv and do `pip install --upgrade pip` if needed.
For google login, create a superuser, go to .../admin, and then click add a site. Name it 'http://127.0.0.1:8000/'. After that, go to the add social application page.
Add a new one, with the provider being google. Also make the name google. Then set the client id and the secret key respectively using the json in discord.
Move the site you created into the right hand box at the bottom, and move example.com to the left. That should be it.