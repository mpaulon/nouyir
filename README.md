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







# Features non implémentées

 * utiliser du jinja dans la configuration (cf ansible)
   * par défaut un sauvegarde le résultat de toutes les requetes et on peut ensuite y accéder via un dictionnaire dans les templates jinja

 * meilleure gestion des utilisateurs multiples
   * sauvegarde des variables par user
 * possibilité de sauvegarder des variables à n'importe quel niveau (pour l'instant on ne peut sauvegarder que des variables qui sont des clefs d'un dictionnaire renvoyé)
 * meilleure gestion des paramètres dans l'url
 * génération d'un compte rendu de tests à la fin
 * gestion du niveau de logs
 * génération des tests à partir d'une spécification de l'api (voir standards existant)
   * vérification de la couverture des tests à partir d'une spécification de l'api
 * génération de documentation/exemples au format html à partir du yaml de tests
 * support de backends de stockage des mots de passe/login (fichiers gpg, pass ...)
 * refactor des fichiers de configuration
 * support des loops (cf ansible)
 * support de l'upload/download de fichiers
 * support d'autres systèmes d'authentification