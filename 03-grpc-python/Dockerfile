FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Generate Python gRPC stubs inside the image (simple for classroom)
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. todo.proto

EXPOSE 50051
CMD ["python", "server.py"]
