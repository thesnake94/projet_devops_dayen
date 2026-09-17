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
