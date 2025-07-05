from flask import request, render_template, session
import bcrypt

class AuthRoutes:
  def __init__(self,app,db,s3):
      profiles=db['Profiles']
      
      # Uploads Profile picture to AWS
      def uploadProfilePictureToAWS(fileObj):

        fileName = f"profile_pictures/{fileObj.filename}"
        bucketName = 'learnarc-storageaws'
        s3.upload_fileobj(fileObj, bucketName, fileName, ExtraArgs={'ContentType': fileObj.content_type})

        return f"https://{bucketName}.s3.amazonaws.com/{fileName}"

      # Signup Route
      @app.route('/signUp', methods=['POST'])
      def signUp():

        # Check if username is available
        if(profiles.find_one({"username":request.form['username']}) is not None):
            return render_template('signup.html')

        # Secure Password
        securepassword = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

        # Upload Profile Picture to AWS
        url=None
        file = request.files['profilepicture']
        if file:
            url = uploadProfilePictureToAWS(file)

        profiles.insert_one({"firstname": request.form['firstname'], "lastname":request.form['lastname'],"username": request.form['username'],"age": request.form['age'],"securepassword": securepassword.decode('utf-8'),"profilepictureurl": url,"expertiseIDs":[], "chatUsernames":[]})
        
        session['username']=request.form['username']
        
        return "SUCCESS"
      
      # Login Route
      @app.route('/login',methods=['POST'])
      def logIn():
            # Verify Password
            if(profiles.find_one({"username":request.form['username']}) is not None):

                user=profiles.find_one({"username":request.form['username']})   

                if(user and bcrypt.checkpw(request.form['password'].encode('utf-8'), user.get("securepassword").encode('utf-8'))):
                    
                    session['username']=request.form['username']
                    return "SUCCESS"
                else:
                    return render_template('login.html')

            
                
    
        

  
  
 

