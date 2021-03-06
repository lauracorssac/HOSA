import numpy as np
import tensorflow as tf
import time
import io

class ImageRecognitionManager(object):

    def __init__(self, model, threshold):
      self.threshold = threshold
      self.interpreter = tf.lite.Interpreter(model)
      self.interpreter.allocate_tensors()
      _, self.input_height, self.input_width, _ = self.interpreter.get_input_details()[0]['shape']

    def personWasDetected(self, results):
      for result in results:
        if result['class_id'] == 0:
            return True
      return False

    def set_input_tensor(self, image):
      """Sets the input tensor."""
      tensor_index = self.interpreter.get_input_details()[0]['index']
      input_tensor = self.interpreter.tensor(tensor_index)()[0]
      input_tensor[:, :] = image

    def get_output_tensor(self, index):
      """Returns the output tensor at the given index."""
      output_details = self.interpreter.get_output_details()[index]
      tensor = np.squeeze(self.interpreter.get_tensor(output_details['index']))
      return tensor

    def detect_objects(self, image):
      """Returns a list of detection results, each a dictionary of object info."""
      self.set_input_tensor(image)
      self.interpreter.invoke()

      # Get all output details
      boxes = self.get_output_tensor(0)
      classes = self.get_output_tensor(1)
      scores = self.get_output_tensor(2)
      count = int(self.get_output_tensor(3))

      results = []
      for i in range(count):
        if scores[i] >= self.threshold:
          result = {
              'bounding_box': boxes[i],
              'class_id': classes[i],
              'score': scores[i]
          }
          results.append(result)
      return results

    def analize_image(self, image):
      results = self.detect_objects(image)
      return self.personWasDetected(results)
