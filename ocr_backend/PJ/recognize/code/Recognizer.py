import numpy as np
from PIL import Image
import tensorflow as tf
import PJ.recognize.code.keys_5990 as keys


class Recognizer:
    def __init__(self, pb_path):
        with open(pb_path, 'rb') as f:
            serialized = f.read()
        tf.reset_default_graph()
        output_graph_def = tf.GraphDef()
        output_graph_def.ParseFromString(serialized)
        tf.import_graph_def(output_graph_def, name='')
        self.sess = tf.Session()
        tf.global_variables_initializer().run(session=self.sess)

        input_tensor_name = 'the_input:0'
        output_tensor_name = 'out/truediv:0'
        self.input_images = self.sess.graph.get_tensor_by_name(input_tensor_name)
        self.output_context = self.sess.graph.get_tensor_by_name(output_tensor_name)

    @staticmethod
    def __decode__(pred):
        characters = keys.alphabet[:]
        characters = characters[1:] + u'卍'
        n_class = len(characters)
        char_list = []
        pred_text = pred.argmax(axis=2)[0]
        for i in range(len(pred_text)):
            if pred_text[i] != n_class - 1 and (
                    (not (i > 0 and pred_text[i] == pred_text[i - 1])) or (i > 1 and pred_text[i] == pred_text[i - 2])):
                char_list.append(characters[pred_text[i]])
        return u''.join(char_list)

    def __predict__(self, img):
        width, height = img.size[0], img.size[1]
        scale = height * 1.0 / 32
        width = int(width / scale)
        img = img.resize([width, 32], Image.ANTIALIAS)
        img = np.array(img).astype(np.float32) / 255.0 - 0.5
        x = img.reshape([1, 32, width, 1])
        y_pred = self.sess.run([self.output_context], feed_dict={self.input_images: x})
        y_pred = y_pred[0]
        out = Recognizer.__decode__(y_pred)
        return out

    def run(self, image_path):
        img_src = Image.open(image_path)
        img = img_src.convert("L")
        predict_text = self.__predict__(img)
        return predict_text


if __name__ == '__main__':
    recognizer = Recognizer(r"G:\PyCharm\Code\OCR_2\ocr_backend\PJ\recognize\model\weights_densenet_id_0116.pb")
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\011.jpg")
    print("011:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\013.jpg")
    print("013:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\014.jpg")
    print("014:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\015.jpg")
    print("015:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\016.jpg")
    print("016:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\018.jpg")
    print("018:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\019.jpg")
    print("019:\n", result)
    result = recognizer.run(r"G:\PyCharm\Code\GenerateData\out\Segment\020.jpg")
    print("020:\n", result)
