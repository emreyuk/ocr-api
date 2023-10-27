from flask import Flask, jsonify,request, g
import cv2
import numpy as np
import base64
from paddleocr import PaddleOCR




app = Flask(__name__)
ocr = PaddleOCR(lang='en')


def calculate_average_line_height(boxes):
                heights = [box[2][1] - box[0][1] for box in boxes]
                return sum(heights) / len(boxes)

            # Define a function to check if two bounding boxes are on the same line
def on_same_line(box1, box2, average_height, tolerance_factor=0.5):
    y1 = (box1[0][1] + box1[2][1]) / 2  # Calculate the vertical center of box1
    y2 = (box2[0][1] + box2[2][1]) / 2  # Calculate the vertical center of box2
    tolerance = average_height * tolerance_factor
    return abs(y1 - y2) < tolerance




def convert_base64_to_image(b64_string):
    print("converting base64 to image..")
    nparr = None
    npimg = None

    try:
        nparr = np.fromstring(base64.b64decode(b64_string), np.uint8)
        npimg = cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
    except Exception as e:
        print(f"unable to convert base64 (image).. {e}")
    return npimg



@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        data = request.json
        
        if 'service_img' in data:
            base64_image = data['service_img']
            # Base64 encoded image data is received from the request
            
            # Decode base64 image to a NumPy array
            image = convert_base64_to_image(base64_image)
            
            # Convert the image to grayscale
            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Enhance contrast (optional)
            enhanced_image = cv2.equalizeHist(grayscale_image)
            
            # Optical Character Recognition (OCR) to extract text from the image
            results = ocr.ocr(enhanced_image)
            
            # Process PaddleOCR results and extract text
            extracted_text = []
            for result in results[0]:
                output = (result[1][0], result[0])
                extracted_text.append(output)
                print(output)
            
            # Group the extracted text information into lines
            lines = []
            
            # Calculate the average line height to group text on the same line
            average_height = calculate_average_line_height([box for _, box in extracted_text])
            
            for text, box in extracted_text:
                line_found = False
                for line in lines:
                    if any(on_same_line(box, existing_box, average_height) for _, existing_box in line):
                        line.append((text, box))
                        line_found = True
                        break
                if not line_found:
                    lines.append([(text, box)])
            
            # Sort the lines by x-coordinate for better readability
            for line in lines:
                line.sort(key=lambda item: item[1][0][0])
            
            # Display the grouped information by lines
            for i, line in enumerate(lines):
                print(f'Line {i + 1}:')
                for text, _ in line:
                    print(text)
            
            # Return the extracted text and grouped lines as a JSON response
            return jsonify({
                "extracted_text": extracted_text, "lines": lines
            }), 200
        else:
            return jsonify({"message": "Missing 'service_img' data in the request"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Error: " + str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True, threaded=False)
