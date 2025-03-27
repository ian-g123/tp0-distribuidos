package common

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const MAX_BATCH_SIZE = 8000 - 4 // Max kB size of a batch of bets (4 bytes for the size itself)
const FINISH_MESSAGE = "finish"

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	MaxBatchSize  int
	BetsCsvPath   string
}

// Client Entity that encapsulates how
type Client struct {
	config     ClientConfig
	conn       net.Conn
	is_running bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:     config,
		is_running: true,
	}

	// Handle system signals to gracefully shutdown the client
	shutdownSignalChannel := make(chan os.Signal, 1)
	signal.Notify(shutdownSignalChannel, os.Interrupt, syscall.SIGTERM)
	go client.gracefulShutdown(shutdownSignalChannel)
	return client
}

func (c *Client) gracefulShutdown(shutdownSignalChannel chan os.Signal) {
	log.Debug("action: start_graceful_shutdown | result: success")
	<-shutdownSignalChannel
	c.is_running = false
	if c.conn != nil {
		c.conn.Close()
		log.Infof("action: close_client_socket | result: success")
	}
	log.Infof("action: shutdown | result: success")
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	c.conn = conn
	return nil
}

// SendBet Sends a bet to the server and waits for an ACK from the server.
func (c *Client) SubmitBets() error {
	err := c.createClientSocket()
	if err != nil {
		log.Errorf("action: create_client_socket | result: fail | client_id: %v | error: %v", c.config.ID, err)
		return err
	}
	defer c.conn.Close()
	return c.sendBets()
}

func (c *Client) sendBets() error {
	betsFile, err := os.Open(c.config.BetsCsvPath)
	if err != nil {
		log.Errorf("action: read_bets_from_csv | result: fail | error: %v", c.config.ID, err)
		return err
	}
	defer betsFile.Close()
	defer func() {
		if err != nil {
			log.Errorf("action: send_bets | result: fail | error: %v", err)
		}
	}()

	scanner := bufio.NewScanner(betsFile)
	var batch strings.Builder
	batchSize := 0
	outgoingBetsCount := 0

	for scanner.Scan() {
		var serializedBet string
		if serializedBet, err = c.processBetLine(scanner.Text()); err != nil {
			continue
		}
		outgoingBetsCount++
		serializedSize := len(serializedBet)

		if batchSize+serializedSize >= MAX_BATCH_SIZE || outgoingBetsCount >= c.config.MaxBatchSize {
			if err := c.sendAndResetBatch(&batch, &batchSize, outgoingBetsCount); err != nil {
				return err
			}
			outgoingBetsCount = 0
		}

		if batch.Len() > 0 {
			batch.WriteString(";")
			batchSize++
		}
		batch.WriteString(serializedBet)
		batchSize += serializedSize
	}
	if batch.Len() > 0 {
		if err := c.sendAndResetBatch(&batch, &batchSize, outgoingBetsCount); err != nil {
			return err
		}
	}
	if err := c.notifyEndOfProcessAndWaitStats(); err != nil {
		return err
	}
	if err := scanner.Err(); err != nil {
		return err
	}
	return nil
}

// processBetLine Parses and serializes a single line from the CSV
func (c *Client) processBetLine(line string) (string, error) {
	betData := strings.Split(line, ",")
	betData = append(betData, c.config.ID)
	if len(betData) != 6 {
		log.Errorf("action: process_bet_line | result: fail | error: invalid_bet_format: ", betData)
		return "", fmt.Errorf("invalid bet format in CSV")
	}
	bet := NewBet(betData[0], betData[1], betData[2], betData[3], betData[4], betData[5])
	return bet.Serialize(), nil
}

// sendAndResetBatch Sends the current batch and resets it
func (c *Client) sendAndResetBatch(batch *strings.Builder, batchSize *int, outgoingBetsCount int) error {
	log.Debugf("action: send_batch | batch size: %v | bets_sent: %v", *batchSize, outgoingBetsCount)
	if err := WriteInSocket(c.conn, batch.String()); err != nil {
		log.Errorf("action: send_batch | result: fail | error: %v", c.config.ID, err)
		return err
	}
	batch.Reset()
	*batchSize = 0
	return nil
}

func (c *Client) notifyEndOfProcessAndWaitStats() error {
	if err := WriteInSocket(c.conn, FINISH_MESSAGE); err != nil {
		log.Errorf("action: notify_end_of_process | result: fail | error: %v", err)
		return err
	}

	message, err := ReadFromSocket(c.conn)
	if err != nil {
		log.Errorf("action: wait_for_stats | result: fail | error: %v", err)
		return err
	}
	log.Infof("action: bets sent | result: success | stats: %v", message)

	log.Debugf("action: consulta_ganadores | result: in_progress")
	var document_winners []string
	message, err = ReadFromSocket(c.conn)
	if err != nil {
		log.Errorf("action: consulta_ganadores | result: fail | error: %v", err)
		return err
	}
	if message != "" {
		document_winners = strings.Split(message, ",")
	}
	log.Debugf("action: consulta_ganadores | result: success | ganadores: %v", document_winners)
	log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(document_winners))
	return nil
}
