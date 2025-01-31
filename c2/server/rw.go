package server

import (
	"net/http"
)

// rw is a mock of http.ResponseWriter
// although this is not ideal, I don't want to change the Forwarder API just to aline with this project
type rw struct {
	data []byte
	err  any
}

type mockResponseWriter interface {
	http.ResponseWriter
	Data() []byte
	Error() any
}

func NewResponseWriter() mockResponseWriter {
	return &rw{}
}

func (r *rw) Data() []byte { return r.data }
func (r *rw) Error() any   { return r.err }

func (r *rw) Header() http.Header {
	return http.Header{}
}

func (r *rw) Write(data []byte) (int, error) {
	r.data = data
	if r.err == -1 {
		r.err = r.data
	}
	return len(data), nil
}

func (r *rw) WriteHeader(statusCode int) {
	if statusCode < 200 || statusCode > 204 {
		r.err = -1 // sentinel
	}
}
