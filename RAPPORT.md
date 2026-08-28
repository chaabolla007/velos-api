# Projet DevOps · velos-api

**Nom et prénom :** Ahmed Chaabani

**Dépôt :** https://github.com/chaabolla007/velos-api

**Image publiée :** chaabollla/velos-api

**Date de rendu :** 28/08/2026

---

## 1. Ce que j'ai construit, en cinq lignes

J'ai repris l'application Python Flask velos-api et je l'ai placée sous gestion de versions avec Git et GitHub.
J'ai construit une image Docker optimisée et une pile Docker Compose comprenant l'API et PostgreSQL avec persistance des données.
J'ai déployé l'application dans un cluster Kubernetes kind multi-nœuds avec plusieurs replicas, des Services, une sonde de disponibilité et un Secret.
J'ai ajouté la route /alertes puis réalisé une mise à jour progressive vers la version 2.0 et un retour arrière.
Enfin, j'ai automatisé les tests, la construction, la publication et le déploiement avec un pipeline Jenkins déclenché automatiquement.

## 2. Le trajet d'une requête

Dans le cluster Kubernetes, une requête envoyée depuis ma machine vers http://localhost:8081 arrive sur le port exposé par le cluster kind.
Elle est transmise au Service Kubernetes velos-api de type NodePort.
Le Service répartit ensuite la requête vers l'un des pods du Deployment velos-api qui est prêt.
L'application Flask utilise la variable DATABASE_URL pour joindre le Service interne velos-db.
Le Service velos-db transmet enfin la requête au pod PostgreSQL, qui lit ou écrit les données persistées dans son volume.