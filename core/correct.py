import cv2
import numpy as np

def crop_and_pad(image, target_shape=(780, 780)):
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    non_zero_indices = np.argwhere(image_gray != 0)
    y_min, x_min = non_zero_indices.min(axis=0)
    y_max, x_max = non_zero_indices.max(axis=0)
    img = image[y_min:y_max + 1, x_min:x_max + 1]
    current_shape = img.shape[:2]
    pad_height = max(0, target_shape[0] - current_shape[0])
    pad_width = max(0, target_shape[1] - current_shape[1])
    top, bottom = pad_height // 2, pad_height - (pad_height // 2)
    left, right = pad_width // 2, pad_width - (pad_width // 2)
    return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

def mean_non_zero_with_threshold(array, channel, threshold):
    mask = channel <= threshold
    valid_pixels = array[(array != 0) & mask]
    return np.mean(valid_pixels) if len(valid_pixels) > 0 else 0

def correct_image(image, panel):
    image = crop_and_pad(image)
    rf = {"r": 0.178, "g": 0.175, "b": 0.166}
    b_panel = mean_non_zero_with_threshold(panel[:, :, 0], panel[:, :, 0], 223)
    g_panel = mean_non_zero_with_threshold(panel[:, :, 1], panel[:, :, 1], 211)
    r_panel = mean_non_zero_with_threshold(panel[:, :, 2], panel[:, :, 2], 206)
    b_plant = np.clip((image[:, :, 0] / b_panel) * rf["b"] * 255, 0, 255).astype(np.uint8)
    g_plant = np.clip((image[:, :, 1] / g_panel) * rf["g"] * 255, 0, 255).astype(np.uint8)
    r_plant = np.clip((image[:, :, 2] / r_panel) * rf["r"] * 255, 0, 255).astype(np.uint8)
    return cv2.merge([r_plant, g_plant, b_plant])