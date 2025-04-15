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
	"google.golang.org/grpc/metadata"

	Cartgw "Gateway/cart"
	Middleware "Gateway/middleware"
	Ordergw "Gateway/order"
	Productgw "Gateway/product"
)


func main() {
	// Read configuration from environment variables
	productServiceAddr := os.Getenv("PRODUCT_SERVICE_ADDR")
	if productServiceAddr == "" {
		productServiceAddr = "localhost:50052" // Default address
	}
	cartServiceAddr := os.Getenv("CART_SERVICE_ADDR")
	if cartServiceAddr == "" {
		cartServiceAddr = "localhost:50051" // Default address
	}
	orderServiceAddr := os.Getenv("ORDER_SERVICE_ADDR")
	if orderServiceAddr == "" {
		orderServiceAddr = "localhost:50053" // Default address
	}

	gatewayAddr := os.Getenv("GATEWAY_ADDR")
	if gatewayAddr == "" {
		gatewayAddr = "localhost:8090" // Default address
	}

	// Create a client connection to the existing Product gRPC server
	productConn, err := grpc.NewClient(
		productServiceAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("Failed to dial Product gRPC server at %s: %v", productServiceAddr, err)
	}

	// Create a client connection to the existing Cart gRPC server
	cartConn, err := grpc.NewClient(
		cartServiceAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("Failed to dial Cart gRPC server at %s: %v", cartServiceAddr, err)
	}
	// Create a client connection to the existing Order gRPC server
	orderConn, err := grpc.NewClient(
		orderServiceAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("Failed to dial Order gRPC server at %s: %v", orderServiceAddr, err)
	}

	defer productConn.Close()
	defer cartConn.Close()
	defer orderConn.Close()
	log.Printf("Product_service server present at %s", productServiceAddr)
	log.Printf("Cart_service server present at %s", cartServiceAddr)


	// Create a new gRPC Gateway mux
	gwmux := runtime.NewServeMux(
        runtime.WithMetadata(func(ctx context.Context, req *http.Request) metadata.MD {
            return metadata.Pairs("authorization", req.Header.Get("Authorization"))
        }),
    )

	// Register the Product service with the gRPC Gateway
	if err := Productgw.RegisterProductServiceHandler(context.Background(), gwmux, productConn); err != nil {
		log.Fatalf("Failed to register Product gateway: %v", err)
	}

	if err := Cartgw.RegisterCartServiceHandler(context.Background(), gwmux, cartConn); err != nil {
		log.Fatalf("Failed to register Cart gateway: %v", err)
	}	
	if err := Ordergw.RegisterOrderServiceHandler(context.Background(), gwmux, orderConn); err != nil {
		log.Fatalf("Failed to register Order gateway: %v", err)
	}

	// Create an HTTP server for the gRPC Gateway
	gwServer := &http.Server{
		Addr:    gatewayAddr,
		Handler: Middleware.ChainMiddleware(gwmux),
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
