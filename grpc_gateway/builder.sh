#!/bin/bash

# set -e  # Exit immediately if a command exits with a non-zero status

# Checking if the Proto Files directory exists
PROTO_DIR="./Proto"

if [ -d "$PROTO_DIR" ]; then
  echo "Proto Files Directory Present"
else
  echo "Proto Files Directory does not exist"
  exit 1
fi

# Compiling grpc-gateway files
# for file in "$PROTO_DIR"/*.proto; do
#   if [ -f "$file" ]; then
#     filename=$(basename "$file")  # Get the base file name
#     echo "Compiling $filename"

#     # Compile using protoc and check for errors
#     if protoc -I="$PROTO_DIR" --go-grpc_out=. --go_out=. --grpc-gateway_out=. "$file"; then
#       echo "$filename Compiled Successfully"
#     else
#       echo "Error: Could Not Compile $filename"
#       exit 1
#     fi
#   else
#     echo "Error: $file is not a valid file"
#     exit 1
#   fi
# done




# Checking for the main.go file
echo "Starting build process..."

# Check if main.go exists
if [ ! -f "main.go" ]; then
    echo "Error: main.go not found!"
    exit 1
fi

echo "main.go found. Proceeding with build..."

# Download dependencies
echo "Running go mod tidy..."
go mod tidy
echo "Go packages downloaded successfully."

if protoc -I="$PROTO_DIR" --go-grpc_out=. --go_out=. --grpc-gateway_out=. product.proto; then
      echo "$filename Compiled Successfully"
    else
      echo "Error: Could Not Compile $filename"
      exit 1
fi
if protoc -I="$PROTO_DIR" --go-grpc_out=. --go_out=. --grpc-gateway_out=. cart.proto; then
      echo "$filename Compiled Successfully"
    else
      echo "Error: Could Not Compile $filename"
      exit 1
fi
if protoc -I="$PROTO_DIR" --go-grpc_out=. --go_out=. --grpc-gateway_out=. order.proto; then
      echo "$filename Compiled Successfully"
    else
      echo "Error: Could Not Compile $filename"
      exit 1
fi
if protoc -I="$PROTO_DIR" --go-grpc_out=. --go_out=. --grpc-gateway_out=. user_auth.proto; then
      echo "$filename Compiled Successfully"
    else
      echo "Error: Could Not Compile $filename"
      exit 1
fi
# Build the Go program
echo "Building Go program..."
go build -ldflags "-s -w" -o server .
echo "GO Program built successfully."

# Check if server binary was created
if [ ! -f "./server" ]; then
    echo "Error: Server binary not found after build!"
    exit 1
fi

echo "Build completed successfully."

# Run the server if executed in an interactive session

# echo "Starting server..."
# ./server  # Use exec to replace script process with server process
