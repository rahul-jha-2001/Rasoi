package middleware
import (
	"log"
	"net/http"
	"io"
	"fmt"
)

// """
// Things i wanna log

// request
// url
// query param
// time 
// success code
// error message if any 
// """

func LogRequestMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Check for query parameters
	var str string = fmt.Sprintf("%s %s ",r.Method,r.URL.Path)
	queryParams := r.URL.Query()
	if len(queryParams) > 0 {
		for key, value := range queryParams {
			str += fmt.Sprintf("%s:%s ",key,value[0])
		}
	}

	// Check for body (Content-Length > 0)
	if r.ContentLength > 0{
		body, err := io.ReadAll(r.Body)
		if err  != nil{
			str += "Error Reading The Body"
		}
		str += fmt.Sprintf("Body:%s",string(body))
	}
	log.Println((str))
	next.ServeHTTP(w, r)
	})
}
