package common

import (
	"encoding/binary"
	"net"
)

func WriteInSocket(conn net.Conn, message string) error {
	messageLength := int32(len(message))
	packet := make([]byte, 4+len(message))
	binary.BigEndian.PutUint32(packet[:4], uint32(messageLength))
	copy(packet[4:], message)
	if err := writeFully(conn, packet); err != nil {
		log.Errorf("action: write_in_socket | result: fail | error: %v", err)
		return err
	}
	return nil
}

func writeFully(conn net.Conn, data []byte) error {
	for len(data) > 0 {
		n, err := conn.Write(data)
		if err != nil {
			return err
		}
		data = data[n:]
	}
	return nil
}

func ReadFromSocket(conn net.Conn) (string, error) {
	lengthBuffer := make([]byte, 4)
	if err := readFully(conn, lengthBuffer); err != nil {
		log.Errorf("action: read_from_socket | result: fail | error: %v", err)
		return "", err
	}

	messageLength := binary.BigEndian.Uint32(lengthBuffer)
	messageBuffer := make([]byte, messageLength)
	if err := readFully(conn, messageBuffer); err != nil {
		log.Errorf("action: read_from_socket | result: fail | error: %v", err)
		return "", err
	}

	return string(messageBuffer), nil
}

func readFully(conn net.Conn, data []byte) error {
	for len(data) > 0 {
		n, err := conn.Read(data)
		if err != nil {
			return err
		}
		data = data[n:]
	}
	return nil
}
