import face_recognition
from flask import Flask, jsonify, request, redirect, url_for
import pickle
import mysql.connector
import os
from werkzeug.utils import secure_filename

mydb = mysql.connector.connect(host="localhost", user="shafqat", passwd="7423", database="p_r_system")
mycursor = mydb.cursor()

UPLOAD_FOLDER = './pictures/old'
# allowed Extensions for Images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_url_path="/pictures", static_folder="pictures")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    return '''
    <!doctype html>
    <title>Is this a picture identified?</title>
    <h1>This is home page of PR System</h1>
    <a href="/search">click to goto search page</a><br>
    <a href="/entry">click to goto entry page</a><br>
    <a href="/update">click to goto update page</a><br>

    '''


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'FILE' not in request.files:
            return "no file selected"
            # return redirect(request.url)
        file = request.files['FILE']
        identity = request.form['IDENTITY']
        if file.filename == '':
            return "file name empty"
            # return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], identity + ".jpg"))
            return filename

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Is this a picture identified?</title>
    <h1>Upload a picture and save</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="FILE" accept="image/*"  required="required">
      <input type="text" name="IDENTITY"  required="required">
      <input type="submit" value="Update">
    </form>
    '''


@app.route('/update', methods=['GET', 'POST'])
def update():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'FILE' not in request.files:
            return "no file selected"
            # return redirect(request.url)
        mypicture = request.files['FILE']
        file = request.files['FILE']
        identity = request.form['IDENTITY']

        if file.filename == '':
            return "file name empty"
            # return redirect(request.url)

        if file and allowed_file(file.filename):
            mypicture.save(os.path.join(app.config['UPLOAD_FOLDER'], identity + ".JPG"))
            myreturn = update_image(file, identity)
            if myreturn == 1:
                return "success save in db and memory"
            else:
                return "there was a problem try again"

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Is this a picture identified?</title>
    <h1>Upload a picture and see if it's a picture of a known person or not!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="text" name="IDENTITY" required="required" placeholder="identity">
      <input type="file" name="FILE"  accept="image/*"  required="required">
      <input type="submit" value="Update">
    </form>
    '''


@app.route('/search', methods=['GET', 'POST'])
def search_image():
    message = "Welcome to P.R.SYSTEM"
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            img = face_recognition.load_image_file(file)
            # Get face encodings for any faces in the uploaded image
            if len(str(face_recognition.face_locations(img))) > 20:
                face_encoding = face_recognition.face_encodings(img)[0]
                name = ""
                id = ""
                father_name = ""
                address = ""
                guardian_cell = ""
                blood_group = ""
                recent_diagonised_disease = ""
                face_found_in_image = False
                face_found_in_database = False
                if len(face_encoding) > 0:
                    face_found_in_image = True
                    mycursor.execute("select ID, FACE_ENCODING from persons_data_table")
                    result = mycursor.fetchall()
                    message = "face doesnt found in database"
                    for row in result:
                        tempid = row[0]
                        coding = pickle.loads(row[1])
                        results = face_recognition.compare_faces(coding, face_encoding)
                        if results[0] == True:
                            mycursor.execute(
                                "select IDENTITY, NAME,FATHER_NAME, ADDRESS,GUARDIAN_CELL, BLOOD_GROUP,RDD from persons_data_table where ID = %s",
                                (tempid,))
                            sresults = mycursor.fetchall()
                            face_found_in_database = True
                            for row in sresults:
                                message = True
                                id = row[0]
                                name = row[1]
                                father_name = row[2]
                                address = row[3]
                                guardian_cell = row[4]
                                blood_group = row[5]
                                recent_diagonised_disease = row[6]
                                break
                if message is not True:
                    return '''
                        <!doctype html>
                        <title>Is this a picture identified?</title>
                        <h1>Upload a picture and see if it's a picture of a known person or not!</h1>
                        <p>Face doesnt found in Data Base please Enter details about it</P><a href="./entry">here..</a><p>
                        <form method="POST" enctype="multipart/form-data">
                          <input type="file" name="file" accept="image/*"  required="required" >
                          <input type="submit" value="Upload">
                        </form>
                       '''
                else:
                    return '''
                        <!doctype html>
                        <title>Face Found</title>
                        <h1>{}.</h1>
                        <img src="http://192.168.43.113:5555/pictures/old/{}.jpg" width="200px" height=270px><br>
                        Father Name: {}<br>
                        Address: {}<br>
                        Guardian Cell:{}<br>
                        Blood Group: {}<br>
                        Recent Diagonosed Desease: {}<br>
                        </html>
                        '''.format(name, id, father_name, address, guardian_cell, blood_group, recent_diagonised_disease)
            else:
                return '''
                    <!doctype html>
                    <title>Is this a picture identified?</title>
                    <h1>Upload a picture and see if it's a picture of a known person or not!</h1>
                    <p>please Upload a faced image </P>
                    <form method="POST" enctype="multipart/form-data">
                      <input type="file" name="file" accept="image/*"  required="required" >
                      <input type="submit" value="Upload">
                    </form>
                    '''

    return '''
                        <!doctype html>
                        <title>Is this a picture identified?</title>
                        <h1>Upload a picture and see if it's a picture of a known person or not!</h1>
                        <p>{}</P>
                        <form method="POST" enctype="multipart/form-data">
                          <input type="file" name="file" accept="image/*"  required="required" >
                          <input type="submit" value="Upload">
                        </form>
                        '''.format(message)


@app.route('/entry', methods=['GET', 'POST'])
def entryform():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'PICTURE' not in request.files:
            return redirect(request.url)

        picture = request.files['PICTURE']
        identity = request.form['IDENTITY']
        name = request.form['NAME']
        father_name = request.form['FATHER_NAME']
        gender = request.form['GENDER']
        address = request.form['ADDRESS']
        guardian_cell = request.form['GUARDIAN_CELL']
        blood_group = request.form['BLOOD_GROUP']
        rdd = request.form['RDD']
        message = "request getting data"
        if picture.filename == '':
            message = "image empty"
            return redirect(request.url)

        if picture and allowed_file(picture.filename):
            message = "inserting data"
            returnofentry = enter_data_into_database(picture, identity, name, father_name, gender, address,
                                                     guardian_cell, blood_group, rdd)
            if returnofentry == 'None':
                picture.save(os.path.join(app.config['UPLOAD_FOLDER'], identity + ".JPG"))
                return (returnofentry)
            else:
                return str(returnofentry)

    return '''
        <!doctype html>
        <title>Enter Data for Person?</title>
        <h1>Enter the Data for Person to be stored in database</h1>

        <form method="POST" enctype="multipart/form-data">
          <input type="text" name="IDENTITY" required="required" placeholder="identity"><br>
          <input type="text" name="NAME" required="required" placeholder="complete name"><br>
          <input type="text" name="FATHER_NAME" required="required" placeholder="father name"><br>
          <input type="radio" name="GENDER" value="male" checked> Male
          <input type="radio" name="GENDER" value="female"> Female <br>
          <input type="text" name="ADDRESS" required="required" placeholder="address"><br>
          <input type="text" name="GUARDIAN_CELL" required="required" placeholder="cell number"><br>
          <input type="text" name="BLOOD_GROUP" required="required" placeholder="blood group"><br>
          <input type="text" name="RDD" required="required" placeholder="Recent Diagnosed Disease"><br>
          <input type="file" name="PICTURE" accept="image/*"><br>
          <input type="submit" value="Register"><br>
        </form>
        '''


def enter_data_into_database(picture, identity, name, father_name, gender, address, guardian_cell, blood_group, rdd):
    # successfully saves face_encoding in database
    message = "something wrong happend"
    try:
        pikkle = pickle.dumps(picture)
        mycursor.execute(
            "insert into persons_data_table (IDENTITY,NAME,FATHER_NAME,GENDER,ADDRESS,GUARDIAN_CELL,BLOOD_GROUP,RDD,FACE_ENCODING) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (identity, name, father_name, gender, address, guardian_cell, blood_group, rdd, pikkle,))
        backresult = mydb.commit()
        return str(backresult)
    except Exception as e:
        message = str(e)
        return message


def update_image(file, identity):
    img = face_recognition.load_image_file(file)
    # Get face encodings for any faces in the uploaded image
    face_encoding = face_recognition.face_encodings(img)
    pikkle = pickle.dumps(face_encoding)
    message = "not done"
    try:
        if len(face_encoding) > 0:
            try:
                mycursor.execute("update persons_data_table set FACE_ENCODING = 'null' where IDENTITY = %s",
                                 (identity,))
                # mymsg = str(mycursor.rowcount) +" rows set to null and "
                mydb.commit()
                mycursor.execute("update persons_data_table set FACE_ENCODING = %s where IDENTITY = %s",
                                 (pikkle, identity,))
                # mymsg = mymsg + str(mycursor.rowcount)
                myreturn = mycursor.rowcount
                mydb.commit()
                return myreturn
                # return str(mymsg)+" rows affected"
            except Exception as e:
                return str(e)
        else:
            print("please upload a face image")
            return "please upload a face image"
    except Exception as e:
        return str(e)


# def detect_faces_in_image(file_stream):
# Load the uploaded image file
# img = face_recognition.load_image_file(file_stream)
# # Get face encodings for any faces in the uploaded image
# face_encoding = face_recognition.face_encodings(img)[0]
#
# name = ""
# id = ""
# father_name = ""
# address = ""
# guardian_cell = ""
# blood_group = ""
# recent_diagonised_disease = ""
# face_found = False
# if len(face_encoding) > 0:
#     mycursor.execute("select ID, FACE_ENCODING from persons_data_table")
#     result = mycursor.fetchall()
#     for row in result:
#         tempid = row[0]
#         coding = pickle.loads(row[1])
#         results = face_recognition.compare_faces(coding, face_encoding)
#         if results[0] == True:
#             mycursor.execute(
#                 "select IDENTITY, NAME,FATHER_NAME, ADDRESS,GUARDIAN_CELL, BLOOD_GROUP,RDD from persons_data_table where ID = %s",
#                 (tempid,))
#             sresults = mycursor.fetchall()
#             face_found = True
#             for row in sresults:
#                 id = row[0]
#                 name = row[1]
#                 father_name = row[2]
#                 address = row[3]
#                 guardian_cell = row[4]
#                 blood_group = row[5]
#                 recent_diagonised_disease = row[6]
#                 break
#     # Return the result as json
# endresult = {
#     "face_found": face_found,
#     "ID": id,
#     "Name": name,
#     "Father_Name": father_name,
#     "Address": address,
#     "Guardian_cell": "0" + guardian_cell,
#     "Blood Group": blood_group,
#     "Recent Diagonised Disease": recent_diagonised_disease
# }
# resultwhenfacenotfound = {
#     "face_found": face_found
# }
# if face_found == True:
#     return jsonify(endresult)
# else:
#     return jsonify(resultwhenfacenotfound)
#

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)
