package main

import (
	// "context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"regexp"
	"strings"

	jwt "github.com/golang-jwt/jwt/v5"
	"github.com/rs/cors"
)

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

		// Get IP address and request metadata
		ipAddress := getIPAddress(r)
		userAgent := r.UserAgent()
		protocol := r.Proto
		host := r.Host
		contentType := r.Header.Get("Content-Type")
		referer := r.Referer()

		// Read and save the request body
		// var bodyBytes []byte
		// if r.Body != nil {
		// 	bodyBytes, _ = io.ReadAll(r.Body)
		// }
		// bodyString := string(bodyBytes)

		// // Restore body so it can be read again
		// r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

		// Build initial log string
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

		if referer != "" {
			str += fmt.Sprintf("Referer:[%s] ", referer)
		}

		queryParams := r.URL.Query()
		if len(queryParams) > 0 {
			str += "QueryParams:["
			for key, value := range queryParams {
				str += fmt.Sprintf("%s:%s,", key, value[0])
			}
			str = str[:len(str)-1] + "] "
		}

		next.ServeHTTP(wrappedWriter, r)

		// Append status code
		str += fmt.Sprintf("Status:[%d]", wrappedWriter.statusCode)
		log.Println("INFO:", str)

	})
}


func VerifyJWTAndGetClaims(tokenString string, secretKey string, algorithm string) (jwt.MapClaims, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// Ensure the token uses the expected algorithm
		if token.Method.Alg() != algorithm {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(secretKey), nil
	})

	if err != nil || !token.Valid {
		return nil, fmt.Errorf("invalid or failed to parse token: %w", err)
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, fmt.Errorf("invalid claims format")
	}

	return claims, nil
}


func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		markInternal := func() {
			r.Header.Set("Grpc-Metadata-type", "internal")
			log.Println("Public/internal access granted:", r.URL.Path)
			next.ServeHTTP(w, r)
		}

		JWT_SECRET_KEY := os.Getenv("JWT_SECRET_KEY")
		JWT_ALGO := os.Getenv("JWT_ALGO")
		// Allow public GET requests to specific endpoints
		storeUuidRegex := regexp.MustCompile(`^/v1/store/[a-fA-F0-9\-]+$`)
		path := r.URL.Path

		if r.Method == http.MethodGet &&
			(strings.HasPrefix(path, "/v1/store/") &&
				(strings.Contains(path, "/category/") ||
					strings.Contains(path, "/product/") ||
					strings.Contains(path, "/add_on/") ||
					strings.Contains(path, "/dietpref") ||
					storeUuidRegex.MatchString(path))) {
			log.Println("Skipping JWT Auth for public GET:", path)
			markInternal()
			return
		}

		// Allow unauthenticated /auth routes
		if strings.Contains(path, "/auth") {
			markInternal()
			return
		}

		// Expect Authorization: Bearer <token>
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			http.Error(w, "Authorization header required", http.StatusUnauthorized)
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			http.Error(w, "Authorization header must be 'Bearer <token>'", http.StatusUnauthorized)
			return
		}

		tokenString := parts[1]
		claims, err := VerifyJWTAndGetClaims(tokenString, JWT_SECRET_KEY,JWT_ALGO)
		if err != nil {
			log.Println("JWT verification failed:", err)
			http.Error(w, "Unauthorized: invalid token", http.StatusUnauthorized)
			return
		}

		// Set gRPC metadata headers
		for key, val := range claims {
			strVal := fmt.Sprintf("%v", val)
			r.Header.Set("Grpc-Metadata-"+key, strVal)
		}

		// Optional: mark the source
		r.Header.Set("Grpc-Metadata-auth-source", "custom")

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
			http.MethodPatch,
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
