package common

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

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
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount && c.is_running; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		if err := c.createClientSocket(); err != nil {
			log.Errorf("action: create_client_socket | result: fail | error: %v", err)
			return
		}

		// TODO: Modify the send to avoid short-write
		if c.conn != nil {
			_, err := fmt.Fprintf(
				c.conn,
				"[CLIENT %v] Message N°%v\n",
				c.config.ID,
				msgID,
			)
			if err != nil {
				log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
					c.config.ID, err)
				return
			}
		}
		if c.conn != nil {
			msg, err := bufio.NewReader(c.conn).ReadString('\n')
			if c.conn != nil {
				c.conn.Close()
			}
			if err != nil {
				log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err,
				)
				return
			}
			log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
				c.config.ID,
				msg,
			)
		}

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
