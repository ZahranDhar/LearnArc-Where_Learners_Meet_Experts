from flask import request, render_template, session

class ExpertiseRoutes:
  def __init__(self,app,db):
   profiles=db['Profiles']
   expertises=db['Expertises']
   
   # Add Expertise Route
   @app.route('/add', methods=['POST'])
   def addExpertise():

      tags = [tag.strip().lower() for tag in request.form['tags'].split(',') if tag.strip()]
      result=expertises.insert_one({"username":session.get('username'),"course":request.form['course'],"title":request.form['title'],"description":request.form['description'],"tags":tags})
      profiles.update_one({"username":session.get('username')},{"$push":{"expertiseIDs":result.inserted_id}})
      
      return render_template('Home.html')