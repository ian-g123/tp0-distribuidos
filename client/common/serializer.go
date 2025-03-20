package common

import "fmt"

func SerializeBet(bet *Bet) string {
	return fmt.Sprintf(
		`{"firstName":"%s","lastName":"%s","document":"%s","birthdate":"%s","number":"%s","agency":"%s"}`,
		bet.firstName, bet.lastName, bet.Document, bet.birthdate, bet.Number, bet.agency,
	)
}
