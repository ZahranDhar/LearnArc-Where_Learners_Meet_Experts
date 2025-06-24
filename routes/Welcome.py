from flask import render_template

class WelcomeRoutes:
  def __init__(self,app):
    
    # Welcome Page Route
    @app.route('/',methods=['POST'])
    def welcome():
      return render_template('welcome.html')