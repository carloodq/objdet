from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import shutil


UPLOAD_FOLDER = r"C:\Users\carlo\Dropbox\big projects dropbox\wecloud\obj count\uploads"
STATIC_FOLDER = r"C:\Users\carlo\Dropbox\big projects dropbox\wecloud\obj count\static\images"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png','jpg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
    

def count_card(img):
    imgr =img = cv.imread(img)
    img_hsv = cv.cvtColor(imgr, cv.COLOR_BGR2HSV)
    # range of interest - hue is the color
    lower_blue = np.array([100,40,0])
    upper_blue = np.array([200,255,255])
    # we detect the blue
    mask = cv.inRange(img_hsv, lower_blue, upper_blue)
    contours, hierarchy = cv.findContours(image=mask, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_NONE)
    # only plot some contours
    cntr = [c for c in contours if cv.contourArea(c) > 30000]
    # draw contours on the original image
    image_copy = imgr.copy()
    cv.drawContours(image=image_copy, contours=cntr, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv.LINE_AA)
    cv.imwrite(os.path.join(app.config['STATIC_FOLDER'], 'contours.png'), image_copy) 
    return  str(len(cntr)) 


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',
            #                         filename=filename))




            count_cards = count_card(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            
            os.chdir(r"C:\Users\carlo\Dropbox\big projects dropbox\wecloud\obj count\yolov5")

            # remove directory so that cards count doesn't accumulate
            shutil.rmtree("../static/images/exp")

            command = f"python detect.py --weights runs/train/yolov5s_results/weights/best.pt --img 416 --conf 0.4 --source ../uploads/{filename} --save-txt --exist-ok"  
            os.system(command)  
            print(os.getcwd())

            labels = ".."+f"/static/images/exp/labels/{filename}".split('.')[-2]+'.txt'

            def count_obj(filename):
                f = open(filename, "r")
                return len(f.readlines())

            obc = count_obj(labels)

            print("****", labels)

            return render_template('index.html', count_cards = count_cards, filename = filename, obc = obc, results = True)


    return render_template('index.html')



from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    