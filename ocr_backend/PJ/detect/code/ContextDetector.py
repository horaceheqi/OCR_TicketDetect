import os
import cv2
import time
import numpy as np
import tensorflow as tf
import PJ.detect.code.cfg as cfg
from PIL import Image, ImageDraw
from PJ.detect.code.nms import nms
from keras.models import load_model
from keras.preprocessing import image
from PJ.detect.code.preprocess import resize_image
from keras.applications.vgg16 import preprocess_input


class Detector:
    @staticmethod
    def cut_text_line(geo, im_array, save_path, img_names, s):
        res_path = os.path.join(save_path, img_names)
        p_min = np.amin(geo, axis=0)
        p_max = np.amax(geo, axis=0)
        min_xy = p_min.astype(int) - 2
        max_xy = p_max.astype(int) + 2
        sub_im_arr = im_array[min_xy[1]:max_xy[1], min_xy[0]:max_xy[0], :]
        sub_im = image.array_to_img(sub_im_arr, scale=False)
        sub_im.save(os.path.join(save_path, '%d.jpg' % s))

    @staticmethod
    def sigmoid(x):
        """`y = 1 / (1 + exp(-x))`"""
        return 1 / (1 + np.exp(-x))

    def __init__(self, _path):
        # 加载h5
        # self.model = load_model(_path)
        # 加载pb
        with open(_path, 'rb') as f:
            serialized = f.read()
        tf.reset_default_graph()
        # tf.get_default_graph()
        output_graph_def = tf.GraphDef()
        output_graph_def.ParseFromString(serialized)
        tf.import_graph_def(output_graph_def, name="")
        self.sess = tf.Session()
        tf.global_variables_initializer().run(session=self.sess)
        input_tensor_name = 'input_img:0'
        output_tensor_name = 'east_detect/concat:0'
        self.input_images = self.sess.graph.get_tensor_by_name(input_tensor_name)
        self.output = self.sess.graph.get_tensor_by_name(output_tensor_name)

    def run(self, img, _name, output_path, output_path2):
        """
            :param img: 图片矩阵，RGB
            :param _name: 图片名字
            :param output_path:	 裁剪的文本行的保存位置
            :param output_path2: 检测结果示意大图保存位置
        """
        start_run_time = time.time()
        ori_wight, ori_height = img.size
        d_wight, d_height = resize_image(img, cfg.max_predict_img_size)
        scale_ratio_w = d_wight / ori_wight
        scale_ratio_h = d_height / ori_height
        img_resize = img.resize((d_wight, d_height), Image.BILINEAR).convert('RGB')
        img_resize_array = image.img_to_array(img_resize)
        img_ori_array_copy = image.img_to_array(img).copy()

        '''网络输入'''
        img_input_array = preprocess_input(img_resize_array, mode='tf')  # suit tf tensor
        x = np.zeros((1, d_height, d_wight, 3))
        x[0] = img_input_array  # img_ori的尺寸736*736
        '''执行网络'''
        y_pred = self.sess.run(self.output, feed_dict={self.input_images: x})
        # y_pred = self.model.predict(x)
        '''网络后处理'''
        y = y_pred[0]
        y[:, :, :3] = Detector.sigmoid(y[:, :, :3])
        cond = np.greater_equal(y[:, :, 0], cfg.pixel_threshold)
        activation_pixels = np.where(cond)  # fixme 返回元祖tuple类型 a[0]保存了纵坐标 a[1]保存横坐标
        end_run_time = time.time()
        print("检测-网络所需时间：%f s" % (end_run_time - start_run_time))

        start_nms_time = time.time()
        quad_scores, quad_after_nms = nms(y, activation_pixels)
        end_nms_time = time.time()
        print("检测-nms所需时间：%f s" % (end_nms_time - start_nms_time))

        start_filter_time = time.time()
        x[0] = np.uint8(x[0])
        with image.array_to_img(x[0]) as im:  # Image.fromarray(x[n]) error ?
            quad_im = im.copy()
            # 过滤掉score小于零的
            score_list = []
            quad_after_nms_list = []
            for score, geo, s in zip(quad_scores, quad_after_nms, range(len(quad_scores))):
                if np.amin(score) > 0:
                    score_list.append(score)
                    quad_after_nms_list.append(geo)
            # 计算y轴的分布区间,水平投影
            y_aixes = np.zeros([quad_im.size[1]])
            for bbox in quad_after_nms_list:
                bbox_top_y = int(bbox[0][1])
                bbox_bottom_y = int(bbox[1][1])
                y_aixes[bbox_top_y:bbox_bottom_y + 1] = y_aixes[bbox_top_y:bbox_bottom_y + 1] + 1
            # 计算水平投影的起始位置
            text_lines_top = []
            for i in range(len(y_aixes) - 1):
                if y_aixes[i] == 0 and y_aixes[i + 1] > 0:
                    text_lines_top.append(i)
            # 计算水平投影的终止位置
            text_lines_bottom = []
            for i in range(1, len(y_aixes)):
                if y_aixes[i] == 0 and y_aixes[i - 1] > 0:
                    text_lines_bottom.append(i)
            # 根据上一条终止位置和下一条的起始位置计算水平分割线
            if len(text_lines_top) != len(text_lines_bottom):
                print("投影计算错误")
            divide_lines = []
            divide_lines.append((0 + text_lines_top[0]) / 2)
            for i in range(len(text_lines_bottom) - 1):
                divide_lines.append((text_lines_bottom[i] + text_lines_top[i + 1]) / 2)
            divide_lines.append((quad_im.size[1] + text_lines_bottom[-1]) / 2)
            # 根据devide_lines得到同一区域内的文本框
            quad_after_nms_divided_list = []
            for i in range(len(divide_lines) - 1):
                quad_after_nms_divided_list.append([])
            for quad in quad_after_nms_list:
                for i in range(len(divide_lines) - 1):
                    if divide_lines[i] < quad[0][1] < divide_lines[i + 1]:
                        quad_after_nms_divided_list[i].append(quad)
                        break
            # 将同一区域内的文本框按照从左到右排序
            quad_after_nms_sorted_list = []
            for quad_after_nms_divided in quad_after_nms_divided_list:
                temp = []
                for bbox in quad_after_nms_divided:
                    temp.append(bbox[0][0])
                index_sorted = sorted(range(len(temp)), key=lambda k: temp[k])
                temp1 = []
                for index in index_sorted:
                    temp1.append(quad_after_nms_divided[index])
                quad_after_nms_sorted_list.append(temp1)

            quad_draw = ImageDraw.Draw(img)
            s = 100
            with open(output_path2 + "/{}.{}".format(_name, "txt"), mode='w', encoding='utf8') as f:
                for quad_after_nms_in_one_line in quad_after_nms_sorted_list:
                    for geo, i in zip(quad_after_nms_in_one_line, range(len(quad_after_nms_in_one_line))):
                        geo /= [scale_ratio_w, scale_ratio_h]
                        quad_draw.line([tuple(geo[0]),
                                        tuple(geo[1]),
                                        tuple(geo[2]),
                                        tuple(geo[3]),
                                        tuple(geo[0])], width=2, fill='blue')
                        # 裁剪文本行并保存文本行图片
                        Detector.cut_text_line(geo, img_ori_array_copy, output_path, _name, s + i + 1)
                        f.write(str(s + i + 1) + ".jpg,"
                                + str(int(geo[0][0])) + ',' + str(int(geo[0][1])) + ','
                                + str(int(geo[1][0])) + ',' + str(int(geo[1][1])) + ','
                                + str(int(geo[2][0])) + ',' + str(int(geo[2][1])) + ','
                                + str(int(geo[3][0])) + ',' + str(int(geo[3][1])) + '\n')
                    s = s + 100
            # 保存画框的检测结果图
            img.save(os.path.join(output_path2, "{}.{}".format(_name, "jpg")))
        end_filter_time = time.time()
        print("检测-筛选画框所需时间：%f s" % (end_filter_time - start_filter_time))
        return "{}.{}".format(_name, "jpg")


if __name__ == '__main__':
    # model_path = "../model/20200227.h5"
    model_path = "../model/weight_detect.pb"
    detector = Detector(model_path=model_path)
    image_path = r"D:\UMPAY\Project\Coding\OCR_4\ocr_frontend\static\image_upload\train.jpg"
    # img = image.load_img(image_path).convert('RGB')
    # img = Image.open(image_path)	#PIL
    images = cv2.imread(image_path, cv2.COLOR_BGR2RGB)
    images = Image.fromarray(cv2.cvtColor(images, cv2.COLOR_BGR2RGB))
    detector.run(images, 'train.jpg', '../result_train', '../result_train')
    print("succeed!!!")
