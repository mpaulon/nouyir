# Prérequis
 * `python` >= 3.9
 * `requests`
 * `pyyaml`
 * `colorlog`
 # Fichier de configuration

## Sites de l'api à query
```yml
base_urls:
  <site_name>: <site_url>
```
## Credentials
```yml
credentials: # liste des utilisateurs pour lesquels on récupère des tokens
  - name: <nom de l'user à utiliser dans les tests>
    username: <username>
    password: <password>
    base: <base_url à query pour récupérer un token jwt>
    endpoint: <endpoint à query>
    token_name: <attribut de la réponse contenant le token>
```
## Tests
```yml
tests:
  - name: <nom du test>
    users: # liste des utilisateurs pour lesquels on effectue la requête
      - <nom de l'user>
    request: <type de requete (GET, POST, PUT, DELETE)
    base: <base_url à query>
    endpoint: <endpoint à query, peut contenir des variables sauvegardées entre {} si on veut ajouter des  { ou } il faut les échapper avec le format {{ = { et }} = }>
    content: <dictionaire à passer sous format json à l'endpoint>
    save: # variables à sauvegarder pour d'autres tests au format suivant
      <clef dans la réponse>: <nom de la variable">
    required_code: <code http requis pour considérer la requête comme réussie, par défaut, on valid si 2XX>
    required_values: <valide si ce dictionnaire ou cette liste est inclu.se au même "niveau" dans la réponse>
    ignore_failed: <continue l'execution des tests même si celui-ci fail>
    tests_required: <liste des noms des tests qui doivent avoir réussi pour lancer ce test>
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