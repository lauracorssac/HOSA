import jwt
import json
from datetime import datetime
from collections import namedtuple
TokenStruct = namedtuple("TokenStruct", "encoded_token date")

SECRET_KEY = "SECRET_KEY"

codes_dict = {
"Live View": "video",
"System Control": "control",
"Token Generation": "generation"
}

def transform_token(token):
    if token in codes_dict:
        return codes_dict[token]
    return ""

def encode_auth_token(permissions):

    permissions_mapped = list(map(transform_token, permissions))
    filtered_list = list(filter(lambda x: x != "", permissions_mapped))
    date = datetime.now()

    payload = {
        'permissions': filtered_list,
        'iat': date
    }

    encoded_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )
    date_time_string = date.strftime("%m/%d/%Y, %H:%M:%S")

    return TokenStruct(encoded_token= encoded_token, date= date_time_string)

def generate_first_token():
    token = encode_auth_token(codes_dict.keys())
    new_token_string = token.encoded_token.decode()
    with open("tokens.json", 'w') as f:
        tokens_json = { new_token_string: { "tokens": [], "valid": 1, "date": token.date} }
        json_string = json.dumps(tokens_json)
        f.seek(0)
        f.write(json_string)

generate_first_token()
