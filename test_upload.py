import requests

url = "http://127.0.0.1:8000/upload-pdf/"
file_path = "data/Natco .pdf"

with open(file_path, "rb") as f:
    files = {"file": ("Natco .pdf", f, "application/pdf")}
    data = {"company": "Natco", "quarter": "Q1"}
    response = requests.post(url, files=files, data=data)

print(response.status_code)
print(response.json())
