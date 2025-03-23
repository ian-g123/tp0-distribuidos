package common

import "fmt"

// Bet Entity that encapsulates the information of a bet
type Bet struct {
	firstName string
	lastName  string
	Document  string
	birthdate string
	Number    string
	agency    string
}

func NewBet(firstName, lastName, document, birthdate, number, agency string) *Bet {
	return &Bet{
		firstName: firstName,
		lastName:  lastName,
		Document:  document,
		birthdate: birthdate,
		Number:    number,
		agency:    agency,
	}
}

func (bet *Bet) Serialize() string {
	return fmt.Sprintf(
		`{"firstName":"%s","lastName":"%s","document":"%s","birthdate":"%s","number":"%s","agency":"%s"}`,
		bet.firstName, bet.lastName, bet.Document, bet.birthdate, bet.Number, bet.agency,
	)
}
