import csv
import mysql.connector
from concurrent import futures
import time
import grpc

import csv_pb2
import csv_pb2_grpc


class CSVService(csv_pb2_grpc.CSVServiceServicer):
    
    
    def SendCSV(self, request,**kwargs):
        # Connect to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='test_db'
        )

        cursor = connection.cursor()

        # Parse the CSV data
        csv_reader = csv.reader([request.csv_data])
        rows = [row for row in csv_reader]

        # Save the data in the database (Insert / Update)
        table_name = 'csv_data'

        for i, row in enumerate(rows):
            if i == 0:
                # First row is the header, use it to create the table
                columns = ','.join(row)
                create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})'
                cursor.execute(create_table_query)
            else:
                # Insert the data into the table
                placeholders = ','.join(['%s' for val in row])
                insert_query = f'INSERT INTO {table_name} VALUES ({placeholders})'
                cursor.execute(insert_query, row)

        connection.commit()
        cursor.close()
        connection.close()


        return csv_pb2.CSVResponse(rows=rows)




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    csv_pb2_grpc.add_CSVServiceServicer_to_server(CSVService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:

        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()