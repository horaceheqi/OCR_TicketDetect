import os

# 设置前后端路径
BACKEND_PATH = "D:/UMPAY/Project/Coding/OCR_4/ocr_backend"
FRONTEND_PATH = "D:/UMPAY/Project/Coding/OCR_4/ocr_frontend"

# 预处理模型(摆正)路径
rp_detector_pb_path = os.path.join(BACKEND_PATH, "PJ/detect/model", "MobileNet_rp_0103.pb")
# 预处理参考点坐标路径
rp_mask_txt = os.path.join(FRONTEND_PATH, "static/image_mask", "invoice_electronic_adjust.txt")

# 检测模型(通用模型)路径
detect_usually = os.path.join(BACKEND_PATH, "PJ/detect/model", "weight_detect_0304.pb")
# 分类模型(通用模型)路径
classify_usually = os.path.join(BACKEND_PATH, "PJ/classify/model", "")
# 识别模型(通用模型)路径
recognizer_usually = os.path.join(BACKEND_PATH, "PJ/recognize/model", "weights_densenet_else_0116.pb")
# 识别模型(大写金额)路径
recognizer_amount = os.path.join(BACKEND_PATH, "PJ/recognize/model", "weights_densenet-amountmax_0116.pb")
# 识别模型(数字、小写金额)路径
recognizer_id = os.path.join(BACKEND_PATH, "PJ/recognize/model", "weights_densenet_id_0116.pb")