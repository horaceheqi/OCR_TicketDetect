import os
import cv2
import fitz
import glob
import json
import time
import shutil
from PIL import Image
from PJ import constant
from datetime import timedelta
from werkzeug.utils import secure_filename
from PJ.recognize.code.Recognizer import Recognizer
# from PJ.classify.code.Classify import Classify
# from PJ.preprocess.code.PositionAdjuster import PositionAdjuster
from PJ.detect.code.ContextDetector import Detector
from flask import Flask, request, jsonify
from flask_cors import CORS


# 设置允许upload的文件格式
ALLOWED_EXTENSIONS = {'png', 'PNG', 'jpg', 'JPG', 'bmp', 'pdf', 'PDF'}
ALLOWED_PDF = {'pdf', 'PDF'}


# 判断图片格式
def allow_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def pdf_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_PDF


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS  支持跨域请求
CORS(app)

# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)

# 加载检测分类识别所需的模型,并设置中间文件保存路径
# print("load rp_dector")
# rp_detector = ReferPointDetector(pb_path=constant.rp_detector_pb_path)
print("load detector...")
detector = Detector(constant.detect_usually)
# print("load context_classify")
# context_classify = Classify(constant.classify_usually)
print("load context_recognizer")
recognize = Recognizer(constant.recognizer_usually)
# recognizer_ancient_amount = Recognizer(constant.recognizer_amount)
# recognizer_id = Recognizer(constant.recognizer_id)
# print("init RP")
# position_adjuster = PositionAdjuster(constant.rp_mask_txt, rp_detector, recognizer)


def run_detect(project_path, image_path, image_type):
    _, _image = os.path.split(image_path)
    _name = _image.split('.')[0]
    # image = cv2.imread(image_path)
    image = cv2.imread(image_path, cv2.COLOR_BGR2RGB)
    start_total_time = time.time()
    detect_out_path = os.path.join(project_path, "static/image_process")  # detect_out_path 存放供识别图片路径
    draw_box_path = os.path.join(project_path, "static/image_result")  # draw_box_path 存放画好框的图,供最终前台显示

    res_path = os.path.join(detect_out_path, _name)  # 创建存放裁剪图片的目录
    if os.path.exists(res_path):
        shutil.rmtree(res_path)
    os.makedirs(res_path)

    # start_position_time = time.time()
    # save_image_name = image_name.split('.')[0]
    # position_adjuster.run(image, save_image_name)  # 对图像进行一次摆正
    # end_position_time = time.time()
    # print("预处理(摆正)所需时间：%f s" % (end_position_time - start_position_time))
    # image_path = os.path.join(project_path, "static/image_process", image_name)
    # image = cv2.imread(image_path)

    detect_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    start_context_time = time.time()

    res_img = detector.run(detect_img, _name, image_type, res_path, draw_box_path)  # 检测文本行
    end_context_time = time.time()
    print("检测所需时间：%f s" % (end_context_time - start_context_time))
    image_file_list = glob.glob(res_path + "/*.*")
    res_data = {}
    start_recognize_time = time.time()
    for image_file in image_file_list:
        _, name_ext = os.path.split(image_file)
        name, extension = os.path.splitext(name_ext)
        # 分类
    #     image_type = context_classify.run(image_file)
    #     if image_type == 'ancient_amount':
    #         result = recognizer_ancient_amount.run(image_file)
    #     elif image_type == 'id':
    #         result = recognizer_id.run(image_file)
    #     else:
    #         result = recognizer.run(image_file)
        result = recognize.run(image_file)
        res_data[name] = result
    end_recognize_time = time.time()
    print("识别所需时间：%f s" % (end_recognize_time - start_recognize_time))
    end_total_time = time.time()
    print("总体所需时间：%f s" % (end_total_time - start_total_time))
    # shutil.rmtree(detect_out_path)
    return res_data, res_img


# 上传文件
@app.route('/upload', methods=['POST', 'GET'])
def self_upload():
    if request.method == 'POST':
        f = request.files['imageName']
        print('上传图片：', f.filename)
        # 检查文件upload的类型
        if not (f and allow_file(f.filename)):
            return jsonify({"status": 404, "msg": "请检查上传的图片类型,仅限于png,jpg,bmp,pdf"})
        file_name = secure_filename(f.filename)
        upload_path = os.path.join(constant.FRONTEND_PATH, 'static/image_upload', file_name)
        f.save(upload_path)
        if pdf_file(f.filename):  # 将pdf转png
            pdf_path = os.path.join(constant.FRONTEND_PATH, 'static/image_upload', file_name)
            pdf_doc = fitz.open(pdf_path)
            page = pdf_doc[0]
            rotate = int(0)
            zoom_x = 2.0
            zoom_y = 2.0
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            file_name = "{}.{}".format(f.filename.split(".")[0], "jpg")
            upload_path = os.path.join(constant.FRONTEND_PATH, 'static/image_upload', file_name)
            pm = page.getPixmap(matrix=trans, alpha=False)
            pm.writeImage(upload_path)
            pdf_doc.close()
            os.remove(pdf_path)
        return jsonify({'status': 200, 'data': {'fileName': file_name}})
    return jsonify({'status': 500, 'data': {'fileName': ''}})


# 检测/识别
@app.route('/detect', methods=['POST', 'GET'])
def self_detect():
    if request.method == 'POST':
        # 项目路径
        data = json.loads(request.get_data())
        image_name = data['image_name']
        image_type = data['image_type']
        image_path = os.path.join(constant.FRONTEND_PATH, 'static/image_upload', image_name)
        _data, _img = run_detect(constant.FRONTEND_PATH, image_path, image_type)
        # result = run_detect()
        return jsonify({'status': 200, 'fileData': _data, 'fileName': _img})
    return jsonify({'status': 500, 'fileData': {'result': 'Error'}, 'fileName': ''})


if __name__ == '__main__':
    app.run()
