import os
import json

import requests
import torch
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
IMAGE_RESOLUTION = 256.0

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def model_predict(file_name):
    # Возвращает ошибку: ModuleNotFoundError: No module named 'models'.
    # Сохранение модели после загрузки из репозитория поблему не решило.
    # Разобраться позже.
    # model = torch.load('model.pth')

    model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)

    model.eval()

    results = model([file_name])

    return results.xyxy


def get_coords(predict, max_lat, max_lon, min_lat, min_lon):
    bboxes = []

    for img in predict:
        for bbox in img:
            bboxes.append(list(map(float, list(bbox))))

    lat_dpp = (max_lat - min_lat) / IMAGE_RESOLUTION
    lon_dpp = (max_lon - min_lon) / IMAGE_RESOLUTION

    obj_coords = []
    for bbox in bboxes:
        lat = max_lat - ((bbox[1] + bbox[3]) / 2) * lat_dpp
        lon = min_lon + ((bbox[0] + bbox[2]) / 2) * lon_dpp
        obj_coords.append({
            'coords': [lat, lon],
            'bbox': bbox,
        })

    return obj_coords


def get_rosreestr_data(coords):
    url = "https://pkk.rosreestr.ru/api/features/?text=" + str(coords[0]) + "+" + str(coords[1]) + \
          "&tolerance=8&types=[2,3,4,1,21,5]"

    response = requests.get(url, verify=False)
    return response.content


def get_buildings(coords, y=1):
    try:
        response = json.loads(get_rosreestr_data(coords))
    except requests.exceptions.ConnectionError:
        y += 1
        if y < 5:
            response = get_buildings(coords)
        else:
            response = json.loads('{"results": {"error": "Не удалось подключится к кадастровой карте росреестра. '
                                  'Попыток ' + str(y) + '"}}')

    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        res = {}
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(filePath)

            min_lat = float(request.form.get('min-lat'))
            if min_lat:
                res['min-lat'] = min_lat
            min_lon = float(request.form.get('min-lon'))
            if min_lon:
                res['min-lon'] = min_lon
            max_lat = float(request.form.get('max-lat'))
            if max_lat:
                res['max-lat'] = max_lat
            max_lon = float(request.form.get('max-lon'))
            if max_lon:
                res['max-lon'] = max_lon

            predict = model_predict(filePath)

            res['coords'] = get_coords(predict, max_lat, max_lon, min_lat, min_lon)

            for i, latlon in enumerate(res['coords']):
                answer = get_buildings(latlon['coords'])

                res['coords'][i]['rosreestr'] = answer['results']

        return json.dumps(res)

    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
