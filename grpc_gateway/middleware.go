package main

import (
	// "context"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"strings"

	// "google.golang.org/grpc/metadata"


	jwt "github.com/golang-jwt/jwt/v5"

	// "google.golang.org/grpc/metadata"
	"github.com/rs/cors"
)

// var (
// 	app  *firebase.App
// 	once sync.Once
// )

// // InitializeFirebaseApp initializes the Firebase App only once
// func InitializeFirebaseApp() *firebase.App {
//     once.Do(func() {
//         // Load environment variables from .env file
//         err := godotenv.Load()
//         if err != nil {
//             log.Printf("Error loading .env file: %v\n", err)
//         }

//         ctx := context.Background()
//         credentialsPath := os.Getenv("FIREBASE_CREDENTIALS_PATH")
//         if credentialsPath == "rasoi-auth-firebase-adminsdk-fbsvc-2131b3731f.json" {
//             log.Fatal("FIREBASE_CREDENTIALS_PATH environment variable is not set")
//         }

//         opt := option.WithCredentialsFile(credentialsPath)
//         app, err = firebase.NewApp(ctx, nil, opt)
//         if err != nil {
//             log.Printf("Error initializing Firebase app: %v\n", err)
//             return
//         }
//     })
//     return app
// }
// responseWriter wraps http.ResponseWriter to capture the status code
type responseWriter struct {
	http.ResponseWriter
	statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
	rw.statusCode = code
	rw.ResponseWriter.WriteHeader(code)
}

func getIPAddress(r *http.Request) string {
	// Check X-Forwarded-For
	forwarded := r.Header.Get("X-Forwarded-For")
	if forwarded != "" {
		// Only take the first IP
		ips := strings.Split(forwarded, ",")
		return strings.TrimSpace(ips[0])
	}

	// Check X-Real-IP
	realIP := r.Header.Get("X-Real-Ip")
	if realIP != "" {
		return realIP
	}

	// Fallback to RemoteAddr
	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr // May include port
	}
	return ip
}

func LogRequestMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Create wrapped response writer
		wrappedWriter := &responseWriter{
			ResponseWriter: w,
			statusCode:     200, // Default status code
		}

		// Get IP address
		ipAddress := getIPAddress((r))

		// Get user agent and other request details
		userAgent := r.UserAgent()
		protocol := r.Proto
		host := r.Host
		contentType := r.Header.Get("Content-Type")
		referer := r.Referer()

		// Build initial log string with enhanced information
		str := fmt.Sprintf(
			"%s %s [%s] Host:[%s] Protocol:[%s] UserAgent:[%s] ContentType:[%s] ",
			r.Method,
			r.URL.Path,
			ipAddress,
			host,
			protocol,
			userAgent,
			contentType,
		)

		// Add referer if present
		if referer != "" {
			str += fmt.Sprintf("Referer:[%s] ", referer)
		}

		// Add query parameters
		queryParams := r.URL.Query()
		if len(queryParams) > 0 {
			str += "QueryParams:["
			for key, value := range queryParams {
				str += fmt.Sprintf("%s:%s,", key, value[0])
			}
			str = str[:len(str)-1] + "] " // Remove last comma and close bracket
		}

		// Process the request
		next.ServeHTTP(wrappedWriter, r)

		// Add status code to log after request is processed
		str += fmt.Sprintf("Status:[%d]", wrappedWriter.statusCode)
		log.Println("INFO:", str)
	})
}

func VerifyJWTAndGetClaims(tokenString string, secretKey []byte) (jwt.MapClaims, error) {
	// Parse the token with the provided secret key
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// Validate the signing method is what you expect
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return secretKey, nil
	})

	if err != nil {
		return nil, fmt.Errorf("token verification failed: %w", err)
	}

	// Check if the token is valid
	if !token.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	// Extract the claims
	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, fmt.Errorf("invalid token claims structure")
	}

	return claims, nil
}

func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Skip auth for certain paths (optional)
		if strings.Contains(r.URL.Path, "auth") {
			log.Println("Skipping JWT Auth")
			next.ServeHTTP(w, r)
			return
		}

		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "Authorization header required", http.StatusUnauthorized)
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			http.Error(w, "Authorization header format must be 'Bearer {token}'", http.StatusUnauthorized)
			return
		}
		tokenString := parts[1]

		// Initialize Firebase App
		// app = InitializeFirebaseApp()
		client, err := app.Auth(context.Background())
		if err != nil {
			log.Println("Firebase Auth client initialization failed:", err)
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Verify the ID Token
		token, err := client.VerifyIDToken(context.Background(), tokenString)
		if err != nil {
			log.Println("Token verification failed:", err)
			http.Error(w, "Unauthorized: invalid token", http.StatusUnauthorized)
			return
		}

		// Set common user data into headers
		r.Header.Set("Grpc-Metadata-uid", token.UID)

		// Set custom claims if available
		for key, value := range token.Claims {
			var strVal string

			switch v := value.(type) {
			case []interface{}: // if it's a list
				marshaled, _ := json.Marshal(v)
				strVal = string(marshaled)
			default:
				strVal = fmt.Sprintf("%v", v)
			}
			r.Header.Set("Grpc-Metadata-"+key, strVal)
		}

		log.Println(r.Header)
		// Continue to next handler
		next.ServeHTTP(w, r)
	})
}

func CORSMIddleware(next http.Handler) http.Handler {
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"*"}, // Allow all origins
		AllowedMethods: []string{
			http.MethodGet,
			http.MethodPost,
			http.MethodPut,
			http.MethodDelete,
			http.MethodOptions,
		},
		AllowedHeaders: []string{
			"Accept",
			"Authorization",
			"Content-Type",
			"X-CSRF-Token",
		},
		AllowCredentials: true,
	})

	return c.Handler(next)
}

// Helper function for consistent error responses
func respondWithError(w http.ResponseWriter, message string, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]string{"error": message})
}

func ChainMiddleware(h http.Handler) http.Handler {

	var middlewares = []func(http.Handler) http.Handler{
		CORSMIddleware,
		LogRequestMiddleware,
		AuthMiddleware,
	}

	for i := len(middlewares) - 1; i >= 0; i-- {
		h = middlewares[i](h)
	}
	return h

}
