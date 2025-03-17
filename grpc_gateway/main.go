package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"



	"github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	Productgw "Gateway/product"
	Middleware "Gateway/middleware"
)


func main() {
	// Read configuration from environment variables
	productServiceAddr := os.Getenv("PRODUCT_SERVICE_ADDR")
	if productServiceAddr == "" {
		productServiceAddr = "localhost:50052" // Default address
	}

	gatewayAddr := os.Getenv("GATEWAY_ADDR")
	if gatewayAddr == "" {
		gatewayAddr = "localhost:8090" // Default address
	}

	// Create a client connection to the existing Product gRPC server
	conn, err := grpc.NewClient(
		productServiceAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("Failed to dial Product gRPC server at %s: %v", productServiceAddr, err)
	}
	defer conn.Close()
	log.Printf("gRPC server present at %s", productServiceAddr)

	// Create a new gRPC Gateway mux
	gwmux := runtime.NewServeMux()

	// Register the Product service with the gRPC Gateway
	if err := Productgw.RegisterProductServiceHandler(context.Background(), gwmux, conn); err != nil {
		log.Fatalf("Failed to register Product gateway: %v", err)
	}

	// Create an HTTP server for the gRPC Gateway
	gwServer := &http.Server{
		Addr:    gatewayAddr,
		Handler: Middleware.LogRequestMiddleware(gwmux),
	}

	// Start the gRPC Gateway server in a goroutine so we can gracefully shut it down
	go func() {
		log.Printf("Serving gRPC-Gateway for Product on http://%s", gatewayAddr)
		if err := gwServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to serve Product gRPC-Gateway: %v", err)
		}
	}()

	// Wait for a termination signal (Ctrl+C)
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt)

	// Block until we receive a signal
	<-sigChan

	// Graceful shutdown
	log.Println("Shutting down the server...")

	// Set a timeout for graceful shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := gwServer.Shutdown(ctx); err != nil {
		log.Fatalf("Server Shutdown Failed: %v", err)
	}

	log.Println("Server gracefully stopped")
}
