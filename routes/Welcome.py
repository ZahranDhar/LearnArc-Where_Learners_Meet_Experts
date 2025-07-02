from flask import render_template

class WelcomeRoutes:
  def __init__(self,app):
    
    # Welcome Page Route
    @app.route('/',methods=['GET'])
    def welcome():
      return render_template('login.html')