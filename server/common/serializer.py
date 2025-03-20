from common.utils import Bet


def deserializeBet(data_json: str):
    """
    Deserializes a JSON string into a Bet object.
    """
    if not data_json.startswith("{") or not data_json.endswith("}"):
        raise ValueError("Invalid JSON string")
    
    data_trimmed = data_json[1:-1]
    pairs = data_trimmed.split(",")
    bet = {}
    for pair in pairs:
        key, value = pair.split(":")
        # remove quotes
        key = key.strip()[1:-1]
        value = value.strip()[1:-1]
        bet[key] = value
    
    return Bet(bet["agency"], bet["firstName"], bet["lastName"], bet["document"], bet["birthdate"], bet["number"])

