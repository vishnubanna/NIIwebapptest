from app import app

# to run app in bash term run :: export FLASK_APP = NiiWebsite.py
#using .flaskeven meany you dont have to type in export FLASK_APP = NiiWebsite.py every time you test
if __name__ == "__main__":
    app.run(debug = True)