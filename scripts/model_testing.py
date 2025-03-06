import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO


model = YOLO("/Users/satvikchaudhary/PycharmProjects/ProjectIR/models/best_100epochs.pt")
img_path = "/Users/satvikchaudhary/PycharmProjects/ProjectIR/data/archive/SKU110K_fixed/dataset_yolo/test/images/test_0.jpg"
results = model(img_path)

def show_with_labels():
    results[0].show()

def show_without_labels():
    img = cv2.imread(img_path)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf[0].item()
            class_id = int(box.cls[0].item())
            label = f"SKU {confidence:.2f}"


            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)


    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()


# show_without_labels()
show_with_labels()
