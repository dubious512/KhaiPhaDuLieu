import os
import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)
model = None

def initialize_model():
    global model
    model_path = 'my_model.pt'  # Đường dẫn trực tiếp đến tệp mô hình
    if not os.path.exists(model_path):
        print('ERROR: Model path is invalid or model was not found.')
        sys.exit(0)
    model = YOLO(model_path, task='detect')

def process_uploaded_image(image_bytes, model):
    np_array = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    frame = cv2.resize(frame, (640, 640))

    results = model(frame, verbose=False)
    detections = results[0].boxes
    output = []

    confidence_threshold = 0.5  # Định nghĩa ngưỡng độ tin cậy
    bbox_colors = [(164, 120, 87), (68, 148, 228), (93, 97, 209), 
                   (178, 182, 133), (88, 159, 106), (96, 202, 231), 
                   (159, 124, 168), (169, 162, 241), (98, 118, 150), 
                   (172, 176, 184)]

    for i in range(len(detections)):
        xyxy_tensor = detections[i].xyxy.cpu()
        xyxy = xyxy_tensor.numpy().squeeze().astype(int)
        xmin, ymin, xmax, ymax = xyxy

        classidx = int(detections[i].cls.item())
        classname = model.names[classidx]
        conf = detections[i].conf.item()

        if conf > confidence_threshold:
            output.append({
                'box': [int(xmin), int(ymin), int(xmax), int(ymax)],
                'class': classname,
                'confidence': float(conf)
            })

            # Vẽ hộp bao quanh đối tượng
            color = bbox_colors[classidx % len(bbox_colors)]
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

            # Tạo nhãn cho đối tượng
            label = f'{classname}: {int(conf * 100)}%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), 
                          (xmin + labelSize[0], label_ymin + baseLine - 10), 
                          color, cv2.FILLED)
            cv2.putText(frame, label, (xmin, label_ymin - 7), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return output, frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Lưu tệp hình ảnh tạm thời
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    # Đọc tệp hình ảnh đã lưu
    with open(file_path, 'rb') as f:
        image_bytes = f.read()

    results, processed_frame = process_uploaded_image(image_bytes, model)

    # Tạo thư mục output nếu chưa tồn tại
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Xóa tệp hình ảnh cũ nếu tồn tại
    output_image_path = os.path.join(output_dir, 'output.png')
    if os.path.exists(output_image_path):
        os.remove(output_image_path)

    # Lưu khung hình đã xử lý vào tệp output
    cv2.imwrite(output_image_path, processed_frame)

    # Trả về kết quả JSON và URL hình ảnh đã xử lý
    return jsonify(results=results, output_image_url=request.host_url + output_image_path)

@app.route('/output_image')
def output_image():
    return send_file('output/output.png', mimetype='image/png')

if __name__ == '__main__':
    initialize_model()
    app.run(debug=True)