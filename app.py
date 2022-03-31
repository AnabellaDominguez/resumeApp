import os
# import os.path

from flask import Flask, render_template, request, abort, redirect
from flask_bootstrap5 import Bootstrap
import PyPDF2
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']
app.config['UPLOAD_PATH'] = 'uploads'
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'development key'

bootstrap = Bootstrap(app)

user = {}


@app.route('/')
def index():  # put application's code here
    return render_template("index.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            pdfFileObj = open('uploads/' + filename, 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            pages = pdfReader.numPages
            for i in range(pages):
                pageObj = pdfReader.getPage(i)
                print("Page No: ", i + 1)
                text = pageObj.extractText().split('\n')
                user['firstName'] = text[5].split(' ')[0]
                user['middleInitial'] = text[5].split(' ')[1]
                user['lastName'] = text[8].split(' ')[0]
                user['suffix'] = text[8].split(' ')[1]
                user['address'] = text[10]
                user['city'] = text[12].split(' ')[0].strip(',')
                user['state'] = text[12].split(' ')[1]
                user['zipcode'] = text[12].split(' ')[2]
                user['phoneNumber'] = text[14].split(' ')[0] + text[14].split(' ')[1] + text[15] + text[16]
                user['email'] = text[18]
        return redirect('/display')

@app.route('/display', methods=['GET', 'POST'])
def display():
    if request.method == 'GET':
        return render_template('display.html', user=user)
    else:
        userInfo = request.form
        submit = True
        if os.path.exists('uploads/application.txt'):
            os.remove('uploads/application.txt')
        fileOut = open('uploads/application.txt', 'at')
        fileOut.write("Applicant Information:\n")
        fileOut.write("First Name: ")
        fileOut.write(userInfo['fname'] + "\n")
        fileOut.write("Last Name: ")
        fileOut.write(userInfo['lname'] + "\n")
        fileOut.write("Address: ")
        fileOut.write(userInfo['address'] + "\n")
        fileOut.write("City: ")
        fileOut.write(userInfo['city'] + "\n")
        fileOut.write("State: ")
        fileOut.write(userInfo['state'] + "\n")
        fileOut.write("Zipcode: ")
        fileOut.write(userInfo['zipcode'] + "\n")
        fileOut.write("Phone Number: ")
        fileOut.write(userInfo['pnumber'] + "\n")
        fileOut.write("Email: ")
        fileOut.write(userInfo['email'] + "\n")
        fileOut.close()
        return render_template('display.html', user=user, submit=submit)

if __name__ == '__main__':
    app.run()
