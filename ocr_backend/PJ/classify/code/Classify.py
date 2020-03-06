import tensorflow as tf
from PIL import Image
import numpy as np


class Classify:

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
    def run(image_path):
        predict_text = image_path
        return predict_text
