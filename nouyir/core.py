import datetime

from pathlib import Path
from pprint import pformat

import colorlog
import requests
import yaml


logger = colorlog.getLogger(__name__)

def failed(request, message, current_time, test_name, user="", ignore_failed=False):
    """
    En cas d'erreur, affiche un message de log,
    sauvegarde le contenu de la requete et exit
    """
    logger.critical(message)
    if request != None:
        errors_folder = Path("errors/" + current_time)
        if not errors_folder.is_dir():
            errors_folder.mkdir(parents=True)
        error_file = errors_folder/f"{test_name}_{user}.html"
        with open(error_file, "wb") as out:
            out.write(request.content)
            logger.critical(f"Error saved under {error_file.resolve().as_uri()}")
            try:    
                logger.error(pformat(request.json()))
            except:
                pass
    if ignore_failed:
        logger.debug("Ignoring error")
    else:
        exit(1)

def l1_in_l2(l1, l2):
    success_values = True
    invalid_values = list()
    for i1 in l1:
        for i2 in l2:
            if i2 == i1:
                i1_found = True
                break
            elif isinstance(i1, dict):
                i1_found, _ = d1_in_d2(i1, i2)
            elif isinstance(i1, list):
                i1_found, _ = l1_in_l2(i1, i2)
        if not i1_found:
            success_values = False
            invalid_values.append(f"{l1} not found in {l2}")
    return success_values, invalid_values

def d1_in_d2(d1, d2):
    success_values = True
    invalid_values = dict()
    if isinstance(d1, list):
        return l1_in_l2(d1, d2)
    for k, v in d1.items():
        if isinstance(v, dict):
            success_values_d, invalid_values_d = d1_in_d2(v, d2.get(k, {}))
            success_values = success_values and success_values_d
            invalid_values[k] = invalid_values_d
        elif isinstance(v, list):
            success_values_l, invalid_values_l = l1_in_l2(v, d2.get(k, []))
            success_values = success_values and success_values_l
            invalid_values[k] = invalid_values_l
        else:
            if v != d2.get(k):
                invalid_values[k] = f"got {d2.get(k)} instead of {v}"
                success_values = False
    return success_values, invalid_values





class Tester:
    def __init__(self, config_file):
        self.current_time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        self.errors_folder = Path("errors/" + self.current_time)
        if not self.errors_folder.is_dir():
            self.errors_folder.mkdir(parents=True)

        with open(config_file) as f:
            logger.info("Loading config file")
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        logger.info("Loading base urls")
        self.base_urls = self.config.get("base_urls", [])
        logger.info("Generating auth tokens")
        self._get_tokens()

        self.saved = dict()
        self.done = list()



    def _failed_request(self, request):
        file_name = request.url.strip("/").replace("/", ".").replace(":",".").replace("?", ".")
        error_file = self.errors_folder/f"{file_name}.html"
        with open(error_file, "wb") as out:
            out.write(request.content)
            logger.critical(f"Error saved under {error_file.resolve().as_uri()}")

    def _handle_request(self, request, required_codes):
        if not isinstance(required_codes, list):
            if required_codes is None: required_codes = []
            else: required_codes = [required_codes]
        if not(
            (required_codes and request.status_code in required_codes) or 
            (not required_codes and request.ok)):
            logger.error(f"Invalid response with code {request.status_code}")
            self._failed_request(request)
            return None
        logger.info(f"Valid response with code {request.status_code}")
        try:
            return request.json()
        except:
            logger.error("Invalid json in response")
            #TODO: erreur pas de json
            return request.content

    def _post(self, required_codes=None, url="", *args, **kwargs):
        r = requests.post(url, *args, **kwargs)
        return self._handle_request(r, required_codes)
    
    def _get(self, required_codes=None, url="", *args, **kwargs):
        r = requests.get(url, *args, **kwargs)
        return self._handle_request(r, required_codes)
    
    def _put(self, required_codes=None, url="", *args, **kwargs):
        r = requests.put(url, *args, **kwargs)
        return self._handle_request(r, required_codes)

    def _delete(self, required_codes=None, url="", *args, **kwargs):
        r = requests.delete(url, *args, **kwargs)
        return self._handle_request(r, required_codes)

    def _request(self, type):
        if type == "GET": return self._get
        elif type == "POST": return self._post
        elif type == "PUT": return self._put
        elif type == "DELETE": return self._delete
        else:
            logger.critical(f"Unsupported request type {type}")
            exit(1)

    def _get_token(self, user):
        """
        Récupère le token d'authentification avec les credentials spécifiés
        """
        headers = user.get("headers")
        username = user.get("username")
        password = user.get("password")
        logger.info(f"Requesting token for {user.get('name')}")
        content = self._request("POST")(
            url=self._get_url(user),
            data = { "username": username, "password": password },
            headers=headers,
        )
        if isinstance(content, dict):
            return content.get(user.get("token_name"), "access_token_jwt")
        else:
            #TODO: erreur
            pass

    def _get_tokens(self):
        credentials = self.config.get("credentials", [])
        self.users = dict()
        for user in credentials:
            self.users[user.get("name")] = self._get_token(user)
        self.tokens = self.config.get("tokens", {})


    def _get_url(self, point):
        endpoint = point.get("endpoint")
        try:
            if "{" in endpoint:
                endpoint = endpoint.format(**self.saved)
        except KeyError as e:
            logger.error(str(e))
            return None
        return self.base_urls.get(point.get("base")) + endpoint

    def _run_query(self, test, user=None, token=None):
        if user:
            headers = {"Authorization": f"JWT {self.users.get(user)}"} 
        elif token:
            tk = self.tokens.get(token)
            headers = {tk.get("header"): tk.get("value")}
        else:
            headers = dict()
        content = test.get("content", {})
        headers.update(test.get("headers", {}))
        for s in test.get("saved_content", {}):
            try:
                content[s] = self.saved[test.get("saved_content")[s]]
            except KeyError as e:
                logger.error(str(e))
                return
        url = self._get_url(test)
        if url is None: return
        logger.debug(f"Running query to {url} for user {user} with content {content} and headers {headers}")
        required_code = test.get("required_code")
        response = self._request(test["request"])(
            required_code,
            url,
            json=content,
            headers=headers
        )
        if response is None:
            return
        if response != b"":
            logger.debug(pformat(response))
            success_values, invalid_values = d1_in_d2(test.get("required_values", {}), response)
            if not success_values:
                failed(response, f"Request failed with invalid_values {invalid_values}", self.current_time, test.get("name").replace(" ", "_"), user, test.get("ignore_failed", False))
            else:
                for to_save in test.get("save", {}):
                    self.saved[test["save"][to_save]] = response[to_save]
                    logger.debug(f"Saved {to_save}: {self.saved[test['save'][to_save]]} as {test['save'][to_save]}")
                self.done.append(test["name"])
            


    def _run_test(self, test):
        # on vérifie que les tests requis ont été validés
        logger.info(f"Running {test.get('name')}")
        if t_required := test.get("tests_required"):
            missing_requirements = list()
            for t in t_required:
                if t not in self.done:
                    missing_requirements.append(t)
            if missing_requirements:
                logger.error("Missing requirements")
                return
        for token in test.get("tokens", []):
            self._run_query(test, token=token)
        for user in test.get("users", [None]):
            self._run_query(test, user=user)

    def run(self):
        for test in self.config.get("tests"):
            self._run_test(test)
