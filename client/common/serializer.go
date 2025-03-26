package common

import "fmt"

func SerializeBet(bet *Bet) string {
	return fmt.Sprintf(
		`%s,%s,%s,%s,%s,%s`,
		bet.agency, bet.firstName, bet.lastName, bet.Document, bet.birthdate, bet.Number,
	)
}
