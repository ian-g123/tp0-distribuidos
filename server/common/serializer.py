import logging
from common.utils import Bet

REQUIRED_KEYS = {"agency", "firstName",
                 "lastName", "document", "birthdate", "number"}


def deserializeBets(data_json: str) -> tuple[list[Bet], int]:
    """
    Deserializes a JSON string into a Bet object.
    """
    if not data_json.startswith("{") or not data_json.endswith("}"):
        raise ValueError("Invalid JSON string")
    serialized_bets = data_json.split("}{")

    bets = []
    bet_errors = 0

    for serialized_bet in serialized_bets:
        if serialized_bet.startswith("{"):
            serialized_bet = serialized_bet[1:]
        if serialized_bet.endswith("}"):
            serialized_bet = serialized_bet[:-1]
        bet = {}
        for key_value_pair in serialized_bet.split(","):
            key, value = key_value_pair.split(":")
            # remove quotes
            key = key.strip()[1:-1]
            value = value.strip()[1:-1]
            bet[key] = value

        if not REQUIRED_KEYS.issubset(bet.keys()) or not bet["agency"].isdigit() or not bet["number"].isdigit():
            bet_errors += 1
            continue

        bets.append(Bet(bet["agency"], bet["firstName"], bet["lastName"],
                    bet["document"], bet["birthdate"], bet["number"]))
    return bets, bet_errors
