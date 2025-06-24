from flask import request,jsonify, render_template

class ProfileRoutes:
  def __init__(self,app,db):
    profiles=db['Profiles']
    expertises=db['Expertises']

    # Get Profile Route
    @app.route('/profile',methods=['POST'])
    def getProfile():

      # Retrieve user data from MongoDB
      user=profiles.find_one({"username":request.args.get('username')})
      user['_id']=str(user['_id'])
      
      del user['securepassword']
      del user['chatUsernames']

      issideprofile=request.args.get('isSideProfile').lower()=='true'
      if(issideprofile==False):
          expertiseIDs=user.get("expertiseIDs",[])
          expertiseList=list(expertises.find({"_id":{"$in":expertiseIDs}}))

          for expertise in expertiseList:
              expertise['_id'] = str(expertise['_id'])

          del user['expertiseIDs']
          return jsonify({
          "expertiseList": expertiseList,
          "user": user
          })
      return jsonify(user)
      