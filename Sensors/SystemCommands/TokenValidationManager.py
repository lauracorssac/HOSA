import requests

YOUR_HEROKU_URL = ""

class TokenValidationManager(object):

    def local_validation(self, token):
        # invalid received token
        if not token or len(token) == 0:
            return False
        else:
            return True


    def validate_token(self, token):

        if not self.local_validation(token):
            return (400, b'bad-formatted')

        token = token[0]

        url = YOUR_HEROKU_URL + '/validate_token_control'
        headers = {'Content-Type': 'application/json'}
        PARAMS = {'token': token}
        response = requests.get(url = url, headers= headers, params = PARAMS)

        try:
            json_response = response.json()

            if response.status_code == 200 and "status" in json_response and json_response["status"] == "success":
                return (200, b'')
            elif "error" in json_response:
                return (403, json_response["error"].encode())
            else:
                return (500, b'internal-server-error')

        except:
            #invalid received response from the server
            return (500, b'internal-server-error')
