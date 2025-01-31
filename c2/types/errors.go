package types

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"
)

var (
	// Database Errors
	ErrMustBePointer   = errors.New("must be a pointer")
	ErrNotFound        = errors.New("no matches found")
	ErrFilterCollision = errors.New("collision on filter")

	// HTTP Errors
	ErrNotJSON       = errors.New("not json")
	ErrCantProccess  = errors.New("can't proccess")
	ErrInvalidDump   = errors.New("invalid dump")
	ErrNotPaid       = errors.New("not paid")
	ErrNoLongerValid = errors.New("no longer valid")
	ErrInvalidRSA    = errors.New("invalid rsa")
	ErrHashesExist   = errors.New("hashes exist")

	ProperErrors = map[error]string{
		ErrNotFound:        "No matches found in database.",
		ErrFilterCollision: "Collision on filter query.",
		ErrNotJSON:         "Request contains invalid JSON. Please use application/json.",
		ErrCantProccess:    "Cannot process successful callback.",
		ErrInvalidDump:     "Invalid indentifier information, please try again.",
		ErrNotPaid:         "Ransom has not been paid yet.",
		ErrNoLongerValid:   "Ransom has expired and is no longer valid. Goodbye.",
		ErrInvalidRSA:      "Invalid RSA data, please try again.",
		ErrHashesExist:     "Hashes already exist in database. Resolve the pending ransom.",
	}
)

type ErrorResponse struct {
	Success bool   `json:"success"`
	Status  int    `json:"status"`
	Message string `json:"message"`
}

func GetProperError(err error) string {
	if err == nil {
		return ""
	}
	if v, ok := ProperErrors[err]; ok {
		return v
	}
	return err.Error()
}

func HandleError(w http.ResponseWriter, status int, reason error) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	errorResponse := ErrorResponse{
		Success: false,
		Status:  status,
		Message: GetProperError(reason),
	}

	if err := json.NewEncoder(w).Encode(errorResponse); err != nil {
		log.Printf("Error encoding response: %v", err)
	}
}

func BadRequest(w http.ResponseWriter, reason error) {
	HandleError(w, http.StatusBadRequest, reason)
}

func InternalServerError(w http.ResponseWriter, reason error) {
	HandleError(w, http.StatusInternalServerError, reason)
}

func GInternalServerError(w http.ResponseWriter) {
	HandleError(w, http.StatusInternalServerError, errors.New("internal server error"))
}

func NotFound(w http.ResponseWriter, reason error) {
	HandleError(w, http.StatusNotFound, reason)
}

func Unauthorized(w http.ResponseWriter, reason error) {
	HandleError(w, http.StatusUnauthorized, reason)
}

func GUnauthorized(w http.ResponseWriter) {
	HandleError(w, http.StatusUnauthorized, errors.New("unauthorized"))
}

func Forbidden(w http.ResponseWriter, reason error) {
	HandleError(w, http.StatusForbidden, reason)
}
