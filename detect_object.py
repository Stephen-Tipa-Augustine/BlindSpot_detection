import collections
import os
import six

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
tf.get_logger().setLevel('ERROR')
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

PATH_TO_LABELS = 'mscoco_label_map.pbtxt'

COCO17_HUMAN_POSE_KEYPOINTS = [(0, 1),
 (0, 2),
 (1, 3),
 (2, 4),
 (0, 5),
 (0, 6),
 (5, 7),
 (7, 9),
 (6, 8),
 (8, 10),
 (5, 6),
 (5, 11),
 (6, 12),
 (11, 12),
 (11, 13),
 (13, 15),
 (12, 14),
 (14, 16)]


class DetectionModel:
    category_index = None

    def __init__(self):
        self.hub_model = None
        self.detect = True
        self.cap = None

    def run(self, q=None):
        self.category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
        print('loading model...')
        self.hub_model = hub.load('ssd_mobilenet_v2_fpnlite_320x320_1')
        print('model loaded!')
        self.cap = cv2.VideoCapture(0)
        label_id_offset = 0

        while self.detect:
            # Read frame from camera
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            input_tensor = tf.convert_to_tensor(np.expand_dims(frame, 0), dtype=tf.uint8)
            # running inference
            results = self.hub_model(input_tensor)
            result = {key: value.numpy() for key, value in results.items()}

            detected_objects = self.get_object_names(
                result['detection_boxes'][0],
                (result['detection_classes'][0] + label_id_offset).astype(int),
                result['detection_scores'][0],
                self.category_index,
            )

            # Display output
            if q:
                q.put(detected_objects)
            else:
                print('Detected: ', detected_objects)

            image_np_with_detections = frame.copy()

            # Use keypoints if available in detections
            keypoints, keypoint_scores = None, None
            if 'detection_keypoints' in result:
                keypoints = result['detection_keypoints'][0]
                keypoint_scores = result['detection_keypoint_scores'][0]

            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                result['detection_boxes'][0],
                (result['detection_classes'][0] + label_id_offset).astype(int),
                result['detection_scores'][0],
                self.category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=200,
                min_score_thresh=.30,
                agnostic_mode=False,
                keypoints=keypoints,
                keypoint_scores=keypoint_scores,
                keypoint_edges=COCO17_HUMAN_POSE_KEYPOINTS)

            cv2.imshow('frame', image_np_with_detections)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def cleanup(self):
        self.cap.release()
        # cv2.destroyAllWindows()

    @staticmethod
    def get_object_names(
            boxes,
            classes,
            scores,
            category_index,
            track_ids=None,
            max_boxes_to_draw=20,
            min_score_thresh=.5,
            agnostic_mode=False,
            skip_scores=False,
            skip_labels=False,
            skip_track_ids=False):
        # Create a display string (and color) for every box location, group any boxes
        # that correspond to the same location.
        box_to_display_str_map = collections.defaultdict(list)
        box_to_color_map = collections.defaultdict(str)
        if not max_boxes_to_draw:
            max_boxes_to_draw = boxes.shape[0]
        for i in range(boxes.shape[0]):
            if max_boxes_to_draw == len(box_to_color_map):
                break
            if scores is None or scores[i] > min_score_thresh:
                box = tuple(boxes[i].tolist())
                if scores is not None:
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

        result = [box_to_display_str_map[box] for box in box_to_display_str_map]

        return [i[0] for i in result]


if __name__ == '__main__':
    obj = DetectionModel()
    obj.run()

