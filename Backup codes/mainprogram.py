from _ctypes import sizeof

import mysql.connector
from PIL import Image, ImageDraw
import numpy as np
import face_recognition
import pickle
import array

mydb = mysql.connector.connect(host="localhost",user="shafqat",passwd="7423",database="p_r_system")
mycursor = mydb.cursor()

# mycursor.execute("""insert into persons_data_table values('02','Sht','BSCSF15LC111')""")
# mydb.commit()


# recieved = mycursor.fetchall()
#
# for i in recieved:
#     print(recieved)

# mycursor.execute("insert into persons_data_table(id) values()")
#

image = face_recognition.load_image_file('shafqat.jpg')
face_encoding = face_recognition.face_encodings(image)[0]
pikkle = face_encoding.dumps()



# successfully saves face_encoding in database
# mycursor.execute("insert into persons_data_table (IDENTITY,NAME,FATHER_NAME,ADDRESS,GUARDIAN_CELL,BLOOD_GROUP,RDD,FACE_ENCODING) values('bscsf15','shafqat','aw nadeem','dhigana','0300000','b+','typhod',%s)",(pikkle,))
# mydb.commit()
# print("data saved!")


# print(face_encoding)
# print("space here\n")
# myarray = np.array2string(face_encoding)

# # comments
# # # for searching
# # mycursor.execute("select FACE_ENCODING from persons_data_table where FACE_ENCODING = %s",(pikkle,))
# # result = mycursor.fetchall()
# # result = pickle.loads(result)
# # matches = face_recognition.compare_faces(result, face_encoding)
# # if matches:
# #     print(result)
# comments


# # for searching
mycursor.execute("select ID, FACE_ENCODING from persons_data_table")
result = mycursor.fetchall()

for row in result:
    coding = pickle.loads(row[1])
    results = face_recognition.compare_faces(coding, face_encoding)
    if results[0] == True:
        print("It's a picture of me!")
    else:
        print("It's not a picture of me!")
#

# print("unpickling done!")
#
# results = face_recognition.compare_faces([coding], face_encoding)
# if results[0] == True:
#     print("It's a picture of me!")
# else:
#     print("It's not a picture of me!")


#
# matches = face_recognition.compare_faces(result, face_encoding)
# if matches:
#     print(result)



#  # for show all data
# mycursor.execute("select ID, FACE_ENCODING from persons_data_table")
# result = mycursor.fetchall()
# for row in result:
#     id = row[0]
#     data = row[1]
#     print(pickle.loads(data))
#     print(id)
#
#