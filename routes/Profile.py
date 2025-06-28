from flask import request, jsonify

class ProfileRoutes:
    def __init__(self, app, db):
        profiles = db['Profiles']
        expertises = db['Expertises']

        @app.route('/profile', methods=['GET'])
        def getProfile():
            
            username = request.args.get('username')
            user = profiles.find_one({"username": username})

            del user['securepassword']
            del user['_id']

            issideprofile = request.args.get('isSideProfile', 'false').lower() == 'true'

            if (not issideprofile):
                
                expertise_ids = user.get("expertiseIDs", [])

                expertise_list = list(expertises.find({"_id": {"$in": expertise_ids}}))

                del user['expertiseIDs']

                for exp in expertise_list:
                    exp['_id']=str(exp['_id'])

                return jsonify({
                    "user": user,
                    "expertiseList": expertise_list
                })

            return jsonify(user)
