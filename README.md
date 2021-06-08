# How to run
`nouyir [-h] [--pad PAD] [--config CONFIG] [--level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]`

You can use a local yaml config file or a etherpad-lite url.

# Setup

```
python3 -m venv env
source env/bin/activate
pip install git+https://github.com/mpaulon/nouyir
```


# Configuration
## API base urls
```yml
base_urls:
  <site name>: "<site url>"
```

## Tokens
```yml
tokens:
  <token name>: <token>
```

## Credentials
```yml
credentials:
  - name: <local name>
    username: <login on the api>
    password: <password on the api>
    base: <site name to use for login>
    endpoint: <endpoint to append at the end of site url>
    token_name: <name of the token field in the api response>
```

## Tests
```yml
tests:
  - name: <test name>
    request: <request type {GET, POST, PUT, DELETE}>
    tokens:
      - <token_name>
    users:
      - <credential name 1>
      - ...
      - <credentia name N>
    base: <site name to use for login>
    endpoint: <endpoint to append at the end of site url> # can contain a local variable with {<variable name>}
    # all the previous fields are mandatory, you can add one or more optional fields too:
    content: <content for a POST/PUT request>
    saved: # save a field of the request in a local variable
      <response field>: <local variable>
    saved_content: # use a local variable in the request
      <request field>: <local variable>
    required_code: <http response code required to consider this request as valid (by default all 2XX codes are considered valid)>
```

# TODO
  * use "real" jinja in config file (maybe use each statement as jinja template ?!)
  * better handling of multiple users (maybe with things similar to host_vars/group_vars in ansible)
    * by default save variables under user namespace ?
  * handle saving nested values in responses -> best way: save the whole response and access the variables needed in jinja template later
  * handling pagination
  * generate summary (maybe INFO level logs in a file + line with "x tests passed, y tests failed ...")
  * generate tests based on openAPI or other kind of api specifications 
    * use API spec to check tests coverage
  * generate documentation based on tests (maybe add a field comment/docstring in the tests, need to find a way to merge tests on the same endpoints)
  * add support for password storage backends (maybe add a "password_command" in the users declaration)
  * refactor config files (separate users, variables, tokens, and tests) -> how to handle this with pads ? maybe use delimiters in a single pad ?
  * add upload/download support to allow testing on file handling by the API
  * refactor auth management (we only support one kind of header for users and one kind for tokens, maybe add a field to specify the header format ?)
  * support things like loops in ansible, to be able to test the same endpoint with multiple parameters