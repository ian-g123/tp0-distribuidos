from common.utils import Bet
from datetime import date


def deserializeBet(data_csv: str):
    """
    Deserializes csv data into a Bet object
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
