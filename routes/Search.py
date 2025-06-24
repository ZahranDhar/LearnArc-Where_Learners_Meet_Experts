from flask import request, render_template, jsonify

class SearchRoutes:
  def __init__(self,app,db):
    expertises=db['Expertises']

    # Search Route
    @app.route('/search',methods=['GET'])
    def displaySearch():
      iscourse=request.args['isCourse'].lower()=='true'

      if(iscourse):
          expertiseList=list(expertises.find({"course":request.args.get('courseName')}))
      else:
          titlesplit= [word.strip().lower() for word in request.args.get('expertiseTitle').split(',') if word.strip()]

          expertiseList=list(expertises.find({"tags":{"$in":titlesplit}}))

      for expertise in expertiseList:
        expertise['_id'] = str(expertise['_id'])

      return jsonify(expertiseList)