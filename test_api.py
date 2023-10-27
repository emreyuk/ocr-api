import requests
import base64


url = "http://localhost:8888"

# Encode an example image file into base64 (you can use the path to a real image)
with open('image.jpg', 'rb') as image_file:
    # Encode the image in base64 and convert it to text format
    base64_image = base64.b64encode(image_file.read()).decode()

# Create JSON data for the POST request
data = {'service_img': base64_image}

# Send a POST request to the server
response = requests.post(f'{url}/save_image', json=data)

# Display the HTTP status code of the server response
print(response.status_code)
try:
    # Display the server response in JSON format
    print(response.json())
except:
    # If a JSON response cannot be obtained, display the response text
    print(response.text)

# Get OCR results obtained from the server response
ocr_results = response.json()['extracted_text']
