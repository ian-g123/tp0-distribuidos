import logging
from common.utils import Bet
from datetime import date


def deserializeBets(data_csv: str) -> tuple[list[Bet], int]:
    """
    Deserializes csv data into a Bet object
    """
    bets = []
    errors = 0
    for bet_csv in data_csv.split(";"):
        try:
            bet = deserializeBet(bet_csv)
            bets.append(bet)
        except ValueError as e:
            logging.error(f"Error deserializing bet: {e}")
            errors += 1
    return bets, errors


def deserializeBet(data_csv: str) -> Bet:
    """
    Deserialize a CSV string into a Bet object.
    Args:
        data_csv (str): A string containing bet attributes separated by commas.
                        The expected format is:
                        "agency,first_name,last_name,document,birthdate,number"
    Returns:
        Bet: A Bet object initialized with the provided attributes.
    """
    bet_attributes = data_csv.split(",")
    if len(bet_attributes) != 6:
        raise ValueError("Each bet must have 6 attributes")
    if not bet_attributes[0].isdigit() or not bet_attributes[5].isdigit():
        raise ValueError("agency and bet number must be integers")
    try:
        date.fromisoformat(bet_attributes[4])
    except ValueError:
        raise ValueError("birthdate must be in the format 'YYYY-MM-DD'")

    return Bet(*bet_attributes)
