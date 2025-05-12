package main

import (
	// "context"
	"context"
	"log"
	// "google.golang.org/grpc/metadata"
	"sync"
	// "google.golang.org/grpc/metadata"
	"os"
	firebase "firebase.google.com/go/v4"
	"google.golang.org/api/option"
)

var (
	app  *firebase.App
	once sync.Once
)

// InitializeFirebaseApp initializes the Firebase App only once
func InitializeFirebaseApp() *firebase.App {
    var initErr error
    once.Do(func() {
        // Load environment variables from .env file

        ctx := context.Background()
        credentialsPath := os.Getenv("FIREBASE_CREDENTIALS_PATH")
        if credentialsPath == "" {
            log.Fatal("FIREBASE_CREDENTIALS_PATH environment variable is not set")
        }

        opt := option.WithCredentialsFile(credentialsPath)
        app, initErr = firebase.NewApp(ctx, nil, opt)
        if initErr != nil {
            log.Printf("Error initializing Firebase app: %v\n", initErr)
        }
    })
    return app
}