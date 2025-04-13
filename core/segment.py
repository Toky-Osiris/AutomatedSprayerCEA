# This module is designed to be run as an Azure Function.
from ultralytics import YOLO
import cv2
import numpy as np
from collections import defaultdict
from skimage.transform import resize
import supervision as sv

class SegmentIt:
    def __init__(self, image, model_path):
        """
        Initialize the segmenter with an image and a YOLO model path.
        """
        self.image = image
        self.model = YOLO(model_path)
        self.H, self.W, _ = self.image.shape
        self.reference_points = [
            (1507, 817), (980, 809), (442, 794),
            (1531, 271), (997, 286), (463, 235)
        ]
        self.class_names = {0: "plant", 1: "reference_panel"}
        self.masked_images_dict = defaultdict(list)
        self.results = None

    def run_inference(self):
        """Run YOLO model inference on the image."""
        self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.results = self.model(self.image_rgb)

    def classify_masks(self):
        results = self.model(self.image)
        plant_masks = []
        reference_panel_masks = []
        target_classes = {"plant": plant_masks, "reference_panel": reference_panel_masks}
        for result in results:
            if result.masks is not None and result.boxes is not None:
                masks = result.masks.data.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                class_names = result.names
                for i, mask in enumerate(masks):
                    class_id = int(class_ids[i])
                    class_name = class_names[class_id]
                    if class_name in target_classes:
                        target_classes[class_name].append(mask)
        return target_classes

    def get_panel(self):
        masks = self.classify_masks()
        panel = masks.get("reference_panel", [])
        if not panel:
            raise ValueError("No reference panel detected in the image.")
    
        reference_mask = cv2.resize(panel[0].astype(np.uint8), (self.W, self.H))
        reference_mask_3ch = np.repeat(np.expand_dims(reference_mask, axis=-1), 3, axis=-1)
        return self.image * reference_mask_3ch


    def get_scaled_centroid(self, mask):
        y_idx, x_idx = np.where(mask == 1)
        return np.mean(x_idx) * (self.W / mask.shape[1]), np.mean(y_idx) * (self.H / mask.shape[0])

    def euclidean_distance(self, p1, p2):
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def generate_masks(self):
        for result in self.results:
            if result.masks is not None and result.boxes is not None:
                masks = result.masks.data.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy().astype(int)
                for i, mask in enumerate(masks):
                    if self.class_names.get(class_ids[i]) != "plant" or np.all(mask == 0):
                        continue
                    centroid_x, centroid_y = self.get_scaled_centroid(mask)
                    distances = [self.euclidean_distance((centroid_x, centroid_y), rp) for rp in self.reference_points]
                    label = f"plant {np.argmin(distances) + 1}"
                    resized_mask = (resize(mask, (self.H, self.W)) > 0.5).astype(np.uint8)
                    masked_image = np.zeros_like(self.image)
                    masked_image[resized_mask == 1] = self.image[resized_mask == 1]
                    self.masked_images_dict[label].append(masked_image)
        return self.masked_images_dict
