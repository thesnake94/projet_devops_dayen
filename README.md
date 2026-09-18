[![CI](https://github.com/thesnake94/projet_devops_dayen/actions/workflows/ci.yml/badge.svg)](https://github.com/thesnake94/projet_devops_dayen/actions/workflows/ci.yml)

# Atelier Git avancé

## Stratégie de branches

J’utilise une stratégie trunk-based.

La branche principale est :

- `main`

Chaque modification doit être réalisée dans une branche courte.

## Convention de nommage

Les branches utilisent les conventions suivantes :

- `feature/nom-feature`
- `fix/nom-correctif`
- `docs/nom-documentation`
- `chore/nom-tache`

Exemples :

- `feature/login`
- `fix/calcul-total`
- `docs/update-readme`

## Règle de merge

Aucun push direct sur `main`.

Les modifications passent par une Pull Request.

Une Pull Request doit être revue avant d'être fusionnée.

Les branches sont fusionnées avec Squash and Merge afin de conserver un historique linéaire et lisible.

## Conventional Commits

Les commits utilisent le format :

`type(scope): description`

Exemples :

- `feat(app): add welcome message`
- `fix(app): correct calculation`
- `docs(readme): document branch strategy`

## Résolution de conflit

Un conflit Git a été provoqué entre `conflict/version-a` et `conflict/version-b`.
Les deux branches modifiaient la même ligne de `src/config.txt`.
La résolution retenue combine les deux versions.


## Intégration continue

Ce projet utilise GitHub Actions pour vérifier automatiquement que le code fonctionne correctement.

Les vérifications se lancent :

quand du code est envoyé sur la branche `main` ;
quand une Pull Request est créée ou modifiée.

GitHub vérifie d’abord le code avec flake8, puis lance les tests avec pytest.

Les tests sont effectués avec Python 3.10, 3.11 et 3.12.

GitHub garde aussi les dépendances en cache pour aller plus vite et génère un rapport de couverture des tests.

Enfin, il n’est pas possible de fusionner du code dans `main` si les vérifications de la CI échouent.






# Séance 3 — Conteneurisation Docker

## Build de l'image

Se placer dans le dossier de l'application :

cd starter-app2

Construire l'image :

sudo docker build -t projet-devops:latest .

## Lancer l'application seule

sudo docker run --rm -d \
  --name projet-devops \
  -p 5000:5000 \
  projet-devops:latest

Tester l'application :

curl http://localhost:5000/health
curl http://localhost:5000/status

## Vérification utilisateur non-root

sudo docker exec projet-devops whoami

Résultat attendu :

appuser

## Docker Compose

La stack contient deux services :

- web : application Flask
- redis : stockage persistant du compteur de visites

Lancer la stack complète :

sudo docker-compose up -d --build

Vérifier l'état des services :

sudo docker-compose ps

Les services web et redis doivent être en état healthy.

## Endpoints disponibles

GET /health
GET /status
GET /visits

Tester le compteur de visites :

curl http://localhost:5000/visits

Chaque appel incrémente le compteur stocké dans Redis.

## Persistance Redis

Le compteur /visits est stocké dans Redis avec un volume Docker nommé.

Pour vérifier que le compteur survit au redémarrage du conteneur web :

sudo docker-compose restart web
curl http://localhost:5000/visits

Le compteur doit continuer à augmenter et ne pas repartir à 1.

## Comparaison des tailles des images

Les tailles ont été mesurées avec :

sudo docker images | grep projet-devops

Résultats :

- Image naïve : 1.13 GB
- Image multi-stage : 154 MB

L'image multi-stage est donc nettement plus légère que l'image naïve.

## Image publiée sur le registry

Image latest :

thesnake94/projet-devops:latest

Image versionnée :

thesnake94/projet-devops:v1.0.0

Téléchargement de l'image :

sudo docker pull thesnake94/projet-devops:v1.0.0
