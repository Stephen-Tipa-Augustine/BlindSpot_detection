#!/usr/bin/env python
# coding: utf-8
import collections
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
import cv2
import numpy as np
import tarfile
import urllib.request

import six
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

tf.get_logger().setLevel('ERROR')  # Suppress TensorFlow logging (2)
DATA_DIR = os.path.join(os.getcwd(), 'tmp_data')
MODELS_DIR = os.path.join(DATA_DIR, 'models')
for dir in [DATA_DIR, MODELS_DIR]:
    if not os.path.exists(dir):
        os.mkdir(dir)

# Download and extract model
MODEL_DATE = '20200711'
MODEL_NAME = 'ssd_resnet101_v1_fpn_640x640_coco17_tpu-8'
MODEL_TAR_FILENAME = MODEL_NAME + '.tar.gz'
MODELS_DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/tf2/'
MODEL_DOWNLOAD_LINK = MODELS_DOWNLOAD_BASE + MODEL_DATE + '/' + MODEL_TAR_FILENAME
PATH_TO_MODEL_TAR = os.path.join(MODELS_DIR, MODEL_TAR_FILENAME)
PATH_TO_CKPT = os.path.join(MODELS_DIR, os.path.join(MODEL_NAME, 'checkpoint/'))
PATH_TO_CFG = os.path.join(MODELS_DIR, os.path.join(MODEL_NAME, 'pipeline.config'))
if not os.path.exists(PATH_TO_CKPT):
    print('Downloading model. This may take a while... ', end='')
    urllib.request.urlretrieve(MODEL_DOWNLOAD_LINK, PATH_TO_MODEL_TAR)
    tar_file = tarfile.open(PATH_TO_MODEL_TAR)
    tar_file.extractall(MODELS_DIR)
    tar_file.close()
    os.remove(PATH_TO_MODEL_TAR)
    print('Done')

# Download labels file
LABEL_FILENAME = 'mscoco_label_map.pbtxt'
LABELS_DOWNLOAD_BASE = \
    'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/'
PATH_TO_LABELS = os.path.join(MODELS_DIR, os.path.join(MODEL_NAME, LABEL_FILENAME))
if not os.path.exists(PATH_TO_LABELS):
    print('Downloading label file... ', end='')
    urllib.request.urlretrieve(LABELS_DOWNLOAD_BASE + LABEL_FILENAME, PATH_TO_LABELS)
    print('Done')

# Next we load the downloaded model


class ObjectDetectionModel:

    def __init__(self, *args, **kwargs):
        # Enable GPU dynamic memory allocation
        gpus = tf.config.experimental.list_physical_devices('GPU')
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)

        # Load pipeline config and build a detection model
        configs = config_util.get_configs_from_pipeline_file(PATH_TO_CFG)
        model_config = configs['model']
        self.detection_model = model_builder.build(model_config=model_config, is_training=False)

        # Restore checkpoint
        ckpt = tf.compat.v2.train.Checkpoint(model=self.detection_model)
        ckpt.restore(os.path.join(PATH_TO_CKPT, 'ckpt-0')).expect_partial()

        self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,
                                                                            use_display_name=True)

    @tf.function
    def detect_fn(self, image):
        """Detect objects in image."""

        image, shapes = self.detection_model.preprocess(image)
        prediction_dict = self.detection_model.predict(image, shapes)
        detections = self.detection_model.postprocess(prediction_dict, shapes)

        return detections, prediction_dict, tf.reshape(shapes, [-1])

    @staticmethod
    def get_object_names(
            boxes,
            classes,
            scores,
            category_index,
            instance_masks=None,
            instance_boundaries=None,
            keypoints=None,
            keypoint_scores=None,
            track_ids=None,
            max_boxes_to_draw=20,
            min_score_thresh=.5,
            agnostic_mode=False,
            groundtruth_box_visualization_color='black',
            skip_scores=False,
            skip_labels=False,
            skip_track_ids=False):
        # Create a display string (and color) for every box location, group any boxes
        # that correspond to the same location.
        box_to_display_str_map = collections.defaultdict(list)
        box_to_color_map = collections.defaultdict(str)
        box_to_instance_masks_map = {}
        box_to_instance_boundaries_map = {}
        box_to_keypoints_map = collections.defaultdict(list)
        box_to_keypoint_scores_map = collections.defaultdict(list)
        box_to_track_ids_map = {}
        if not max_boxes_to_draw:
            max_boxes_to_draw = boxes.shape[0]
        for i in range(boxes.shape[0]):
            if max_boxes_to_draw == len(box_to_color_map):
                break
            if scores is None or scores[i] > min_score_thresh:
                box = tuple(boxes[i].tolist())
                if instance_masks is not None:
                    box_to_instance_masks_map[box] = instance_masks[i]
                if instance_boundaries is not None:
                    box_to_instance_boundaries_map[box] = instance_boundaries[i]
                if keypoints is not None:
                    box_to_keypoints_map[box].extend(keypoints[i])
                if keypoint_scores is not None:
                    box_to_keypoint_scores_map[box].extend(keypoint_scores[i])
                if track_ids is not None:
                    box_to_track_ids_map[box] = track_ids[i]
                if scores is None:
                    box_to_color_map[box] = groundtruth_box_visualization_color
                else:
                    display_str = ''
                    if not skip_labels:
                        if not agnostic_mode:
                            if classes[i] in six.viewkeys(category_index):
                                class_name = category_index[classes[i]]['name']
                            else:
                                class_name = 'N/A'
                            display_str = str(class_name)
                    if not skip_scores:
                        if not display_str:
                            display_str = '{}%'.format(round(100 * scores[i]))
                        else:
                            display_str = '{}: {}%'.format(display_str, round(100 * scores[i]))
                    if not skip_track_ids and track_ids is not None:
                        if not display_str:
                            display_str = 'ID {}'.format(track_ids[i])
                        else:
                            display_str = '{}: ID {}'.format(display_str, track_ids[i])
                    box_to_display_str_map[box].append(display_str)
                    if agnostic_mode:
                        box_to_color_map[box] = 'DarkOrange'
                    elif track_ids is not None:
                        prime_multipler = viz_utils._get_multiplier_for_color_randomness()
                        box_to_color_map[box] = viz_utils.STANDARD_COLORS[
                            (prime_multipler * track_ids[i]) % len(viz_utils.STANDARD_COLORS)]
                    else:
                        box_to_color_map[box] = viz_utils.STANDARD_COLORS[
                            classes[i] % len(viz_utils.STANDARD_COLORS)]

        return [box_to_display_str_map[box] for box, color in box_to_color_map.items()]

    def run(self, q=None):
        cap = cv2.VideoCapture(0)

        while True:
            # Read frame from camera
            ret, image_np = cap.read()

            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)

            input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
            detections, prediction_dic, shape = self.detect_fn(input_tensor)
            label_id_offset = 1
            detected_objects = self.get_object_names(
                detections['detection_boxes'][0].numpy(),
                (detections['detection_classes'][0].numpy() + label_id_offset).astype(int),
                detections['detection_scores'][0].numpy(),
                self.category_index,
            )

            # Display output
            if q:
                q.put(detected_objects)
            print('Objects: ', detected_objects)


if __name__ == '__main__':
    ObjectDetectionModel().run()
