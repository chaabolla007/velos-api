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

## 3. Jalon 1 · Git

**Ce que j'ai fait :**  
J'ai initialisé le dépôt local `velos-api` puis configuré mon identité Git avec mon nom et mon adresse e-mail.  
J'ai créé un `.gitignore` adapté à Python afin d'exclure notamment les environnements virtuels, les fichiers compilés et les fichiers contenant des secrets.  
J'ai construit un historique de plus de six commits avec des messages explicites et j'ai travaillé sur plusieurs branches plutôt que directement sur `main`.  
Le dépôt distant GitHub utilise SSH. J'ai également utilisé des Pull Requests, ajouté un commentaire de revue, fusionné les changements et protégé la branche `main`.  
J'ai vérifié qu'un push direct sur `main` était refusé.

**Le conflit :**  
J'ai provoqué volontairement un conflit dans `README.md`.  
La branche `docs/description` avait comme titre `velos-api · Ressources fournies`, tandis que la branche `docs/objectif` avait comme titre `velos-api · API de stations de velos`.  
Git ne pouvait pas choisir automatiquement entre ces deux modifications de la même ligne.  
J'ai résolu le conflit en conservant le titre `velos-api · API de stations de velos`, car il décrit mieux le rôle réel du projet, puis j'ai validé la résolution avec un commit de merge.

**Ce que je retiens :**  
Une branche permet d'isoler un changement avant de l'intégrer à la branche principale.  
Un conflit apparaît lorsque Git ne peut pas déterminer automatiquement quelle version conserver. Il faut alors lire les deux versions, choisir ou combiner le contenu, puis valider manuellement la résolution.  
Les Pull Requests et la protection de `main` permettent de contrôler les changements avant leur intégration.  
Les secrets ne doivent jamais entrer dans l'historique Git, même s'ils sont supprimés ensuite.

## 4. Jalon 2 · Docker

**Mesure du cache de construction**

| Situation | Durée mesurée |
| --- | --- |
| Construction avec les dépendances copiées après le code | environ 6,0 s |
| Construction avec les dépendances installées avant le code |  0m2.3s |

Dans la version naïve du Dockerfile, `COPY . .` était exécuté avant l'installation des dépendances. Une simple modification de `app.py` invalidait donc le cache et relançait `pip install`, qui prenait environ 4,9 secondes.

Dans la version optimisée, `requirements.txt` est copié et les dépendances sont installées avant la copie de `app.py`. Une modification du code permet donc de réutiliser le cache des dépendances.

**Taille de l'image**

| Version | Taille |
| --- | --- |
| Version naïve, un seul étage | 209 MB de Disk Usage, 51.4 MB de Content Size |
| Version finale, plusieurs étages |  0m2.3s |

**Ce que le fichier d'exclusion de construction évite d'envoyer :**  
Le fichier `.dockerignore` empêche Docker d'envoyer dans le contexte de construction des éléments inutiles ou sensibles, notamment `.git`, les environnements virtuels Python, les fichiers compilés, les fichiers `.env`, les clés, les fichiers des éditeurs et les métadonnées Windows.

**Comment j'ai prouvé la persistance :**  
J'ai ajouté une station nommée `Station Test` directement dans PostgreSQL. J'ai ensuite arrêté et supprimé les conteneurs avec `docker compose down`, sans supprimer le volume. Après avoir redémarré la pile, la station était toujours présente. Cela montre que les données vivent dans le volume Docker et non dans le conteneur PostgreSQL.

**Ce que je retiens :**  
L'ordre des instructions dans un Dockerfile influence directement l'efficacité du cache. Une construction multi-stage permet également de séparer la construction de l'image réellement exécutée. L'application finale s'exécute avec l'utilisateur `appli` et non avec `root`. Docker Compose permet de décrire dans un seul fichier l'API, PostgreSQL, leur réseau, le volume persistant et l'ordre de démarrage basé sur la santé de la base.

❯ docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep velos-api
chaabollla/velos-api                            4             195MB
chaabollla/velos-api                            latest        195MB
velos-api                                       test-4        228MB
chaabollla/velos-api                            2             195MB
velos-api                                       test-2        228MB
chaabollla/velos-api                            1             195MB
velos-api                                       test-1        228MB
chaabollla/velos-api                            2.0           195MB
velos-api                                       2.0           195MB
chaabollla/velos-api                            1.0           195MB
velos-api                                       1.0           195MB
velos-api-api                                   latest        195MB
velos-api                                       naif          209MB

## 5. Jalon 3 · Kubernetes

**Comment j'ai obtenu le port 8081 vers le cluster :**  
J'ai créé un nouveau cluster kind nommé `velos` avec trois nœuds. Dans `k8s/kind-cluster.yaml`, j'ai ajouté un `extraPortMappings` qui relie le port `8081` de ma machine au port `30081` du nœud control-plane. Le Service `velos-api` est de type `NodePort` et utilise également le port `30081`. Le trajet est donc : machine `8081` → nœud kind `30081` → Service Kubernetes → pods `velos-api`.

**Où vit le mot de passe, et pourquoi ce n'est pas un coffre-fort :**  
Le mot de passe PostgreSQL vit dans le Secret Kubernetes `velos-db-secret`. Je l'ai créé directement avec `kubectl` sans créer de fichier contenant le mot de passe dans le dépôt Git. Un Secret Kubernetes n'est cependant pas un coffre-fort : les valeurs sont principalement encodées et leur protection dépend notamment des droits d'accès au cluster. Un utilisateur disposant des permissions nécessaires peut lire le Secret.

**Ce que j'ai observé en supprimant un exemplaire sous trafic :**  
J'ai monté le Deployment `velos-api` à quatre replicas puis lancé des requêtes vers `/sante` en boucle. Pendant ce trafic, j'ai supprimé un pod. Les requêtes ont continué à recevoir des réponses car le Service envoyait le trafic vers les autres pods disponibles. Le Deployment a détecté qu'il ne restait plus que trois exemplaires alors que l'état désiré était de quatre et a automatiquement créé un nouveau pod.

**La mise à jour vers la version 2 :**  
J'ai ajouté la route `/alertes`, qui retourne uniquement les stations ayant deux vélos disponibles ou moins. J'ai construit et publié l'image `chaabollla/velos-api:2.0`, puis réalisé une mise à jour progressive du Deployment avec `kubectl set image`. Pendant le rollout, une boucle de requêtes continuait à interroger `/sante` et je n'ai pas constaté de coupure côté client. Une fois la mise à jour terminée, `/alertes` répondait avec `"source":"postgres"`.

**Le retour arrière :**  
J'ai consulté les révisions avec `kubectl rollout history deployment/velos-api`, puis exécuté `kubectl rollout undo deployment/velos-api`. Kubernetes a progressivement restauré l'image précédente. J'ai ensuite utilisé `kubectl rollout status` pour attendre la fin réelle du retour arrière et vérifié que l'image `chaabollla/velos-api:1.0` était de nouveau utilisée.

**Ce que je retiens :**  
Un Deployment décrit un état désiré et Kubernetes travaille en permanence pour le maintenir. Les Services offrent un point d'accès stable même lorsque les pods sont remplacés. Les readiness probes évitent d'envoyer du trafic à un pod qui n'est pas encore prêt. Les rolling updates permettent de changer de version sans interrompre le service et l'historique des révisions permet de revenir rapidement à une version précédente.


---

## 6. Jalon 4 · Jenkins

**Mes tests :**  
J'ai écrit deux tests automatisés dans `tests/test_app.py`.  
Le premier vérifie que la route `/sante` répond avec un code HTTP 200 et un statut `ok`.  
Le second vérifie la route `/alertes` sans base de données. Pour cela, le test supprime `DATABASE_URL` afin que l'application utilise son jeu de données en mémoire. Il vérifie ensuite que seules les stations ayant deux vélos disponibles ou moins sont retournées.  
Ces tests n'ont donc besoin d'aucune base PostgreSQL pour fonctionner.

**Les quatre étapes de mon pipeline :**  
Le pipeline Jenkins suit cet ordre :
1. `Tester` : construction de l'étage Docker `test` et exécution de pytest.
2. `Construire` : construction de l'image finale.
3. `Publier` : connexion à Docker Hub avec les identifiants Jenkins puis publication de l'image.
4. `Deployer` : mise à jour du Deployment Kubernetes puis attente de la fin du rollout.

**Comment mes images sont étiquetées, et pourquoi :**  
Le pipeline utilise `${BUILD_NUMBER}` comme étiquette.  
Chaque exécution produit donc une image unique, par exemple `chaabollla/velos-api:4`.  
Cela permet de relier directement une image Docker à l'exécution Jenkins qui l'a construite.

**La ligne qui rend mon pipeline honnête :**

`kubectl rollout status deployment/velos-api --timeout=180s`

Cette ligne oblige Jenkins à attendre que Kubernetes ait réellement terminé le déploiement.  
Sans elle, Jenkins pourrait afficher un pipeline vert juste après `kubectl set image`, même si les nouveaux pods échouaient ensuite à démarrer.

**Le rouge utile :**  
J'ai volontairement modifié le test de la route `/sante` pour qu'il attende `"ko"` alors que l'application renvoie `"ok"`.  
L'étape `Tester` a échoué. Les étapes `Construire`, `Publier` et `Deployer` n'ont donc pas été exécutées.  
Pendant ce temps, l'ancienne image déjà déployée dans Kubernetes est restée en service et l'application continuait à fonctionner.  
J'ai ensuite corrigé le test, poussé la correction et Jenkins a automatiquement exécuté un nouveau pipeline qui est redevenu vert.

**L'extrait de journal qui donne la cause :**

FAILED tests/test_app.py::test_sante_repond_ok
assert 'ok' == 'ko'

## 7. Mes trois difficultés

| # | Symptôme observé | Cause réelle | Correction apportée |
| --- | --- | --- | --- |
| 1 | La commande `docker` était introuvable dans WSL | L'intégration WSL de Docker Desktop n'était pas active | J'ai activé l'intégration de ma distribution Ubuntu dans Docker Desktop puis redémarré Docker |
| 2 | PostgreSQL redémarrait en `CrashLoopBackOff` avec le message indiquant qu'aucun mot de passe superutilisateur n'était défini | Le Secret Kubernetes existait mais la valeur `POSTGRES_PASSWORD` était vide | J'ai recréé le Secret avec un mot de passe non vide puis redémarré le Deployment |
| 3 | PostgreSQL continuait à planter avec `invalid checkpoint record` et `could not locate a valid checkpoint record` | Le premier démarrage raté avait laissé le volume PostgreSQL dans un état d'initialisation incomplet | Comme aucune donnée importante n'était encore présente, j'ai supprimé le PVC corrompu et laissé Kubernetes recréer la base à partir du manifeste et de `init.sql` |

---

## 8. Ce qui n'est pas fait

À ce stade, toutes les exigences techniques principales que j'ai identifiées dans le cahier des charges ont été réalisées.

Les éléments de rendu restants sont la vérification finale des captures, la finalisation du QCM et la vérification du dépôt avant l'envoi.

---

## 9. Assistance utilisée

J'ai utilisé ChatGPT comme assistant pendant le projet pour m'aider à comprendre certaines commandes, analyser les messages d'erreur et structurer les étapes de débogage.

J'ai exécuté moi-même les commandes, observé leurs résultats et appliqué les corrections sur mon environnement. L'assistance m'a notamment aidé à interpréter les erreurs Docker, Kubernetes/PostgreSQL et Jenkins.

J'ai également utilisé les TP réalisés pendant la formation comme référence pour retrouver les commandes et la structure des fichiers de configuration.

---

## 10. Si j'avais deux jours de plus

J'ajouterais en priorité une sonde de vivacité (`livenessProbe`) en complément de la sonde de disponibilité, ainsi que des limites et demandes de ressources CPU et mémoire pour les conteneurs Kubernetes.

J'améliorerais également la traçabilité des images Docker en ajoutant le hash du commit Git dans leur étiquette au lieu d'utiliser uniquement le numéro de build Jenkins.
