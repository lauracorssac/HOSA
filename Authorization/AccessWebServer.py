from http.server import HTTPServer, BaseHTTPRequestHandler
import jwt
from datetime import datetime
import os
import json
from urllib.parse import urlparse, parse_qs
from collections import namedtuple
TokenStruct = namedtuple("TokenStruct", "encoded_token date")

SECRET_KEY = "SECRET_KEY"

codes_dict = {
"Live View": "video",
"System Control": "control",
"Token Generation": "generation"
}

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY)
    except:
        return None

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

class AccessWebServer(BaseHTTPRequestHandler):

    def validate_token(self, token):
        with open("tokens.json", 'r') as f:
            tokens_json = json.load(f)
            if token not in tokens_json or tokens_json[token]["valid"] != 1:
                return False
            else:
                return True
        return False

    def respond_with_empty_message(self, code):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b'')

    def respond_with_json(self, code, json_string):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        json_data = json_string.encode("utf-8")
        self.wfile.write(json_data)

    def get_token_from_url(self):
        url_parsed = urlparse(self.path)
        token = parse_qs(url_parsed.query).get('token', None)
        if len(token) > 0:
            return token[0]
        return None

    def get_path(self):
        url_parsed = urlparse(self.path)
        path = url_parsed.path[1:]
        return path

    def is_valid_token(self, token, json_dic):
        return token in json_dic and "valid" in json_dic[token] and json_dic[token]["valid"] == 1

    def as_token_struct(self, token, json_dic):
        if token in json_dic and "date" in json_dic[token]:
            return TokenStruct(encoded_token=token, date=json_dic[token]["date"])
        else:
            return None

    def as_json(self, token_struct):
        return {"encoded_token": token_struct.encoded_token, "date": token_struct.date}

    def do_GET(self):

        path = self.get_path()
        if path.endswith("apple-app-site-association"):

            f = open(".well-known/apple-app-site-association", 'rb')
            file_data = f.read()
            f.close()
            self.send_response(200)
            self.send_header('Content-Type', 'application/pkcs7-mime')
            self.end_headers()
            self.wfile.write(file_data)
            return

        elif path == "get_generated_tokens":

            token = self.get_token_from_url()
            if not token:
                self.respond_with_empty_message(404)
                return

            with open("tokens.json", 'r') as f:

                 json_string = f.read()
                 json_dic = json.loads(json_string)
                 if token in json_dic and "tokens" in json_dic[token]:
                     generated_tokens = json_dic[token]["tokens"]

                     valid_tokens = list(filter(lambda x: self.is_valid_token(x, json_dic), generated_tokens))
                     token_list = list(map(lambda x: self.as_token_struct(x, json_dic), valid_tokens))
                     response_json = list(map(self.as_json, token_list))

                     response_json_string = json.dumps(response_json)

                     self.send_response(200)
                     self.send_header('Content-Type', 'application/json')
                     self.end_headers()
                     self.wfile.write(response_json_string.encode("utf-8"))
                     return
                 else:
                    self.respond_with_empty_message(500)

        elif path.startswith("validate_token"):

            token = self.get_token_from_url()

            if not self.validate_token(token):
                error = '{"error": "invalid", "status": "fail"}'
                self.respond_with_json(403, error)
                return

            try:
                payload = jwt.decode(token, SECRET_KEY)
                path_comp = path.rsplit("_", 1)

                if len(path_comp) < 2:
                    self.respond_with_empty_message(501)
                    return

                elif len(payload["permissions"]) != 0 and (path_comp[1] in payload["permissions"] or path_comp[1] == "general"):

                    msg = '{"error": "None", "status": "success"}'
                    self.respond_with_json(200, msg)
                    return

                else:
                    error = '{"error": "permission_not_granted", "status": "fail"}'
                    self.respond_with_json(403, error)
                    return


            except jwt.ExpiredSignatureError:
                error = '{"error": "expired", "status": "fail"}'
                self.respond_with_json(403, error)
                return

            except jwt.InvalidTokenError:
                error = '{"error": "invalid", "status": "fail"}'
                self.respond_with_json(403, error)
                return

        else:
            self.respond_with_empty_message(404)


    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len).decode(encoding='UTF-8')
        json_dict = json.loads(post_body)
        path = self.get_path()

        token = self.get_token_from_url()

        if not token or not self.validate_token(token):
            self.respond_with_empty_message(403)
            return

        payload = decode_token(token)
        if not payload:
            self.respond_with_empty_message(403)
            return

        if "generation" not in payload["permissions"]:
            self.respond_with_empty_message(403)
            return

        if path == "delete_token":
            if "token" not in json_dict:
                self.respond_with_empty_message(403)
                return
            token_to_delete = json_dict["token"]
            with open("tokens.json", 'r+') as f:
                tokens_json = json.load(f)

                if token in tokens_json and token_to_delete in tokens_json[token]["tokens"] and token_to_delete in tokens_json:
                    token_list = tokens_json[token]["tokens"]
                    token_list.remove(token_to_delete)
                    tokens_json[token]["tokens"] = token_list
                    tokens_json[token_to_delete]["valid"] = 0
                    json_string = json.dumps(tokens_json)
                    f.seek(0)
                    f.write(json_string)
                    f.truncate()
                else:
                    self.respond_with_empty_message(400)
                    return

            self.respond_with_empty_message(200)
            return

        elif path == "get_token":

            if "permissions" not in json_dict:
                error = '{"error": "no permissions", "status": "fail"}'
                self.respond_with_json(400, error)
                return

            permissions = json_dict["permissions"]
            new_token = encode_auth_token(permissions)
            new_token_string = new_token.encoded_token.decode()

            responseObject = {
                'status': 'success',
                'code': new_token_string
            }

            with open("tokens.json", 'r+') as f:
                tokens_json = json.load(f)

                if token not in tokens_json:
                    self.respond_with_empty_message(500)

                token_list = tokens_json[token]["tokens"]
                token_list.append(new_token_string)
                tokens_json[token]["tokens"] = token_list
                tokens_json[new_token_string] = {'valid': 1, 'tokens': [], 'date': new_token.date }
                json_string = json.dumps(tokens_json)
                f.seek(0)
                f.write(json_string)
                f.truncate()

            json_string = json.dumps(responseObject)
            self.respond_with_json(200, json_string)

        else:
            self.respond_with_empty_message(404)
            return

port = int(os.environ.get('PORT', 8084))
server = HTTPServer(('', port), AccessWebServer)
server.serve_forever()
