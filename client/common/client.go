// merge 5 con 4

package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

const BET_ACKNOWLEDGED = "Bet received"

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
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

// gracefulShutdown waits for a message to shutdown the client
// and cleans up the resources
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
func (c *Client) SendBet(bet *Bet) error {
	err := c.createClientSocket()
	if err != nil {
		log.Errorf("action: create_client_socket | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	defer c.conn.Close()
	if err := c.sendToServer(bet); err != nil {
		return err
	}
	if err := c.waitForAck(); err != nil {
		return err
	}
	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
		bet.Document,
		bet.Number,
	)

	return nil
}

// sendToServer Sends a bet to the server
func (c *Client) sendToServer(bet *Bet) error {
	serializedBet := SerializeBet(bet)
	if err := WriteInSocket(c.conn, serializedBet); err != nil {
		log.Errorf("action: write_in_socket | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	log.Debugf("action: send_bet | result: success | client_id: %v | bet: %v",
		c.config.ID,
		serializedBet,
	)
	return nil
}

// waitForAck Waits for the server to acknowledge the bet
func (c *Client) waitForAck() error {
	message, err := ReadFromSocket(c.conn)
	if err != nil {
		log.Errorf("action: wait_for_ack | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return err
	}
	if message != BET_ACKNOWLEDGED {
		log.Errorf("action: wait_for_ack | result: fail | client_id: %v | message: %v",
			c.config.ID,
			message,
		)
		return err
	}
	return nil
}
