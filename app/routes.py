from app import app
from flask import redirect, url_for, request, render_template, send_from_directory, flash
import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
import os
import time
import random
import tensorflow as tf
import tensorflow.keras as ks

#app.config["UPLOAD_FOLDER"] = "app/images/"
app.config["UPLOAD_FOLDER"] = "app/static/"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
npaffine = None

# from app package import app object

# routes is the file that manages all the urls app will implement/use
@app.route('/')

# @app is a decorater. decorator modifes the function that follows it
# @app.route() links the url provided and the functions
# @app.route(/index) for ex has creates a link between the function index() and the url /index
# /index references the function index()
@app.route('/index')
def index():
    return render_template('base.html', title = "Home")#"hello world"

@app.route('/getimg', methods = ['POST', 'GET']) # if the function has inputs
def getimg():
    if (request.method == 'POST'):
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print("file: ",file.filename)
        if file.filename == '':
            flash("no file selected")
            return redirect(request.url)
        if file:
            file.save(app.config["UPLOAD_FOLDER"] + file.filename)
            return redirect(url_for('sent', name=file.filename))



@app.route('/sent/<name>')
def sent(name):
    image = nb.load(app.config['UPLOAD_FOLDER'] + name)
    imagedat = nb.Nifti1Image(image.dataobj, image.affine)
    # temporary
    npaffine = image.affine
    shift = 20
    bshift = 75

    file = imagedat.get_fdata()
    file = np.transpose(file, (0,2,1))

    data = np.zeros((256 - (shift + bshift), 256, 192), dtype = np.float16)
    counter = 0

    print(data.shape)
    for i in range(shift, file.shape[2] - bshift):
        h2 = file[:,:,i]
        if np.max(h2) > 0:
            h2 = h2 / np.max(h2)
        else:
            h2 = h2 * 0
        data[counter, :, :] = np.expand_dims(h2, axis = 0)
        counter += 1
        #plt.imshow(h2)
        #plt.show()

    print(data[90, :, :].shape)

    h2 = None
    os.remove(app.config['UPLOAD_FOLDER'] + name)

    img = None
    img = "img"+str(random.randint(0,1))+".png"
    dname = "data"+str(random.randint(0,1))
    plt.imsave(app.config['UPLOAD_FOLDER'] + img, data[100,:,:])
    np.save(app.config['UPLOAD_FOLDER'] + dname, data)
    return redirect(url_for("process", img = img, data = (dname + ".npy")))#render_template("imgshow.html", fname = img),

@app.route('/process/<img>/<data>')
def process(img, data):
    data = np.load(app.config['UPLOAD_FOLDER'] + data)#"data.npy")
    #os.remove(app.config['UPLOAD_FOLDER'] + "data.npy")
    print(data.shape)

    #make model a global constant
    model_file = open(app.config['UPLOAD_FOLDER'] + "model.json")
    loaded_model = model_file.read()
    model_file.close()
    model = tf.keras.models.model_from_json(loaded_model)
    model.load_weights(app.config['UPLOAD_FOLDER'] + "model.h5")
    pred = model.predict(x = np.expand_dims(data, axis = -1), batch_size = 1)
    print(pred.shape)
    #model.summary()
    pred = np.squeeze(pred, axis = -1)

    img2 = None
    img2 = "img2" + str(random.randint(0, 1)) + ".png"
    pred[pred >= 0.5] = 1
    pred[pred < 0.5] = 0
    save = (pred[100, :, :] * data[100,:,:])
    #nb.save(data, app.config['UPLOAD_FOLDER'] + "newimg.nii.gz")
    #nb.save(pred, app.config['UPLOAD_FOLDER'] + "predmask.nii.gz")
    plt.imsave(app.config['UPLOAD_FOLDER'] + img2, (pred[100, :, :] * data[100,:,:]))
    pred = None
    return render_template("imgshow.html", fname = img, fname2 = img2)

@app.route("/send_image/<filename>")
def send_image(filename):
    return send_from_directory('static', filename)

@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    app.run(debug=True)