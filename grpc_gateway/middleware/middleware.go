package middleware

import (
	// "context"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"strings"
	"encoding/json"
	// "google.golang.org/grpc/metadata"

	jwt "github.com/golang-jwt/jwt/v5"
)

var JWT_SECRET = os.Getenv("JWT_SECRET")

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
		log.Println("INFO:",str)
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

// func AuthMiddleware(next http.Handler) http.Handler {
// 	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
// 		authToken := r.Header.Get("Authorization")
// 		if authToken == "" {
// 			http.Error(w, "Authorization header required", http.StatusUnauthorized)
// 			return
// 		}

// 		parts := strings.Split(authToken, " ")
// 		if len(parts) != 2 || parts[0] != "Bearer" {
// 			http.Error(w, "Invalid authorization header format", http.StatusUnauthorized)
// 			return
// 		}

// 		claims, err := VerifyJWTAndGetClaims(parts[1], []byte(JWT_SECRET))
// 		if err != nil {
// 			http.Error(w, "Invalid token", http.StatusUnauthorized)
// 			return
// 		}
// 		fmt.Println(claims)
// 		ctx := context.WithValue(r.Context(),"role",claims["role"])
// 		// You might want to add claims to the request context here
// 		r = r.WithContext(ctx)
// 		next.ServeHTTP(w, r)
// 	})
// }


func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 1. Extract and validate Authorization header
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" {
            respondWithError(w, "Authorization header required", http.StatusUnauthorized)
            return
        }

        // 2. Validate Bearer token format
        parts := strings.Split(authHeader, " ")
        if len(parts) != 2 || parts[0] != "Bearer" {
            respondWithError(w, "Authorization header format must be 'Bearer {token}'", http.StatusUnauthorized)
            return
        }

        tokenString := parts[1]
		if JWT_SECRET == ""{
			JWT_SECRET = "Rahul"
		}
        // 3. Verify JWT and get claims
        claims, err := VerifyJWTAndGetClaims(tokenString, []byte(JWT_SECRET))
        if err != nil {
			//Debug
            respondWithError(w, "Invalid token: "+err.Error(), http.StatusUnauthorized)
			log.Println("ERROR:","Invalid token: "+err.Error())
            return
        }

        // 4. Validate required claims
        if claims["role"] == nil {
            respondWithError(w, "Token missing required claims", http.StatusForbidden)
			log.Println("ERROR:","Token missing required claims")
			return
        }

		// for key, value := range claims {
		// 	fmt.Printf("%s: %v\n", key, value)
		// }
		if claims["role"] == "internal" {
            r.Header.Set("Grpc-Metadata-role",claims["role"].(string))
        }
		if claims["role"] == "user" {
            r.Header.Set("Grpc-Metadata-role",claims["role"].(string))
			r.Header.Set("Grpc-Metadata-user_phone_no", claims["user_phone_no"].(string))
        }
		if claims["role"] == "store" {
			r.Header.Set("Grpc-Metadata-role",claims["role"].(string))
			r.Header.Set("Grpc-Metadata-store_uuid", claims["store_uuid"].(string))
        }
        next.ServeHTTP(w, r)
    })
}

// Helper function for consistent error responses
func respondWithError(w http.ResponseWriter, message string, statusCode int) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(statusCode)
    json.NewEncoder(w).Encode(map[string]string{"error": message})
}



func ChainMiddleware(h http.Handler) http.Handler {

	var middlewares = []func(http.Handler) http.Handler{
		LogRequestMiddleware,
		AuthMiddleware,
		
	}

	for i := len(middlewares) - 1; i >= 0; i-- {
		h = middlewares[i](h)
	}
	return h

}
