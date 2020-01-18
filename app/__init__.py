# creates a package called app
# __init__.py is called from start to initalize all variable that will be used by the package at a high level

from flask import Flask

# creates an application object using the class Flask
app = Flask(__name__)
#__name__ is a predifined python var, it ensures that flask will always be set up correctly
# flask will use the var passed in (in this case __name__) as a starting point to load resources like template files

from app import routes
# two entities named app. app the object and app the directory/package
# import always refers to the package or directory
# import is done after the object declartion to prevent circular referencing



