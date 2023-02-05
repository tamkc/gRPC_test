import os
import grpc
import csv
from concurrent import futures
from flask import Flask, request
from csv_pb2 import CSVRequest
from csv_pb2_grpc import CSVServiceStub


app = Flask(__name__)

# Restful request
@app.route('/csv', methods=['GET', 'POST'])
def receive_csv():

#Receive POST request    
    if request.method == 'POST':
        csv_file = request.files['file']
        filename = csv_file.filename
        file_path = os.path.join(os.getcwd(), 'csv', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        csv_file.save(file_path)

#Read and Send gRPC request        
        with open(file_path, 'r') as file:
            csv_data = file.read()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            send_csv(csv_data)
        
        return 'CSV saved to {} and sent through gRPC'.format(file_path)
    else:
        return """ <html>
  <body>
    <form action="/csv" method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
  </body>
</html> """


# Manual Upload
@app.route('/')
def index():
    return """ <html>
<body>
    Welcome to the CSV Uploader!
<form action="/csv" method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="submit" value="Upload">
</form>
</body>
</html> """

#Send CSV gRPC
def send_csv(csv_data):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = CSVServiceStub(channel)
        response = stub.SendCSV(CSVRequest(csv_data=csv_data))
        print(response.message)


if __name__ == '__main__':
    app.run(debug=True)
