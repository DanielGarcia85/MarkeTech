# MarkeTech

Application web full-stack de gestion de messages, construite avec **Django REST Framework** (backend), **Vue 3** (frontend), **PostgreSQL** (base de donnees) et orchestree via **Docker Compose**. L'architecture inclut un reverse proxy **Nginx**, une authentification **JWT** et un pipeline **CI/CD** GitHub Actions.

---

## Table des matieres

- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequis](#prerequis)
- [Installation](#installation)
  - [Avec Docker (recommande)](#avec-docker-recommande)
  - [En local (developpement)](#en-local-developpement)
- [Variables d'environnement](#variables-denvironnement)
- [Endpoints API](#endpoints-api)
- [Structure du projet](#structure-du-projet)
- [Scripts disponibles](#scripts-disponibles)
- [Deploiement CI/CD](#deploiement-cicd)
- [Licence](#licence)

---

## Architecture

```
                        +-----------------+
                        |    Client       |
                        |   (Navigateur)  |
                        +--------+--------+
                                 |
                                 | :80
                        +--------v--------+
                        |     Nginx       |
                        | (Frontend Vue)  |
                        +--------+--------+
                          /      |      \
                   /static  SPA routes  /api, /admin
                         |              |
                         |     +--------v--------+
                         |     |    Gunicorn      |
                         |     |  (Django API)    |
                         |     +--------+--------+
                         |              |
                         |     +--------v--------+
                         |     |   PostgreSQL     |
                         |     |    (BDD)         |
                         |     +-----------------+
                         |
                  +------v------+
                  | Fichiers    |
                  | statiques   |
                  +-------------+
```

**Reseaux Docker :**
- `internal` : communication PostgreSQL <-> Backend
- `proxy` : communication Backend <-> Frontend (Nginx)

---

## Tech Stack

| Couche       | Technologie                          | Version |
|--------------|--------------------------------------|---------|
| Frontend     | Vue 3 + Vite                         | 3.5 / 7.2 |
| Backend      | Django + Django REST Framework        | 6.0 / 3.16 |
| Auth         | JWT (simplejwt)                      | -       |
| BDD          | PostgreSQL                           | 16      |
| Serveur WSGI | Gunicorn                             | 23.0    |
| Reverse Proxy| Nginx                                | Alpine  |
| Conteneurs   | Docker + Docker Compose              | -       |
| CI/CD        | GitHub Actions (self-hosted runner)   | -       |

---

## Prerequis

- **Docker** >= 20.x et **Docker Compose** >= 2.x
- Ou, pour le developpement local :
  - **Python** >= 3.13
  - **Node.js** >= 20.x
  - **npm** >= 10.x

---

## Installation

### Avec Docker (recommande)

1. **Cloner le depot**

   ```bash
   git clone https://github.com/DanielGarcia85/MarkeTech.git
   cd MarkeTech
   ```

2. **Configurer les variables d'environnement**

   ```bash
   cp .env.example .env
   ```

   Editer le fichier `.env` avec vos valeurs (voir [Variables d'environnement](#variables-denvironnement)).

3. **Lancer les services**

   ```bash
   docker compose up -d --build
   ```

4. **Acceder a l'application**

   - Frontend : [http://localhost](http://localhost)
   - Admin Django : [http://localhost/admin/](http://localhost/admin/)
   - API : [http://localhost/api/](http://localhost/api/)

> Au demarrage, le backend execute automatiquement les migrations, la collecte des fichiers statiques et la creation du superutilisateur (si les variables `DJANGO_SUPERUSER_*` sont definies).

---

### En local (developpement)

#### Backend

```bash
cd backend

# Creer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Installer les dependances
pip install -r requirements.txt

# Configurer les variables d'environnement
export DJANGO_SETTINGS_MODULE=config.settings.dev

# Appliquer les migrations (SQLite en mode dev)
python manage.py migrate

# Creer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Le backend est accessible sur [http://localhost:8000](http://localhost:8000).

#### Frontend

```bash
cd frontend

# Installer les dependances
npm install

# Lancer le serveur de developpement
npm run dev
```

Le frontend est accessible sur [http://localhost:5173](http://localhost:5173).
Vite proxifie automatiquement les appels `/api/*` vers `http://localhost:8000`.

---

## Variables d'environnement

Copier `.env.example` en `.env` et adapter les valeurs :

| Variable                     | Description                                  | Exemple                        |
|------------------------------|----------------------------------------------|--------------------------------|
| `DJANGO_SETTINGS_MODULE`     | Module de settings Django                    | `config.settings.prod`         |
| `DJANGO_SECRET_KEY`          | Cle secrete Django                           | `une-cle-longue-et-aleatoire`  |
| `DJANGO_DEBUG`               | Mode debug (`True` / `False`)                | `False`                        |
| `DJANGO_ALLOWED_HOSTS`       | Hotes autorises (separes par des virgules)   | `mondomaine.com,localhost`     |
| `DJANGO_SUPERUSER_USERNAME`  | Nom d'utilisateur admin                      | `admin`                        |
| `DJANGO_SUPERUSER_PASSWORD`  | Mot de passe admin                           | `motdepasse_securise`          |
| `DJANGO_SUPERUSER_EMAIL`     | Email admin                                  | `admin@example.com`            |
| `POSTGRES_DB`                | Nom de la base de donnees                    | `marketech_db`                 |
| `POSTGRES_USER`              | Utilisateur PostgreSQL                       | `marketech_user`               |
| `POSTGRES_PASSWORD`          | Mot de passe PostgreSQL                      | `motdepasse_securise`          |
| `POSTGRES_HOST`              | Hote PostgreSQL                              | `marketech-db` (Docker) / `localhost` |
| `POSTGRES_PORT`              | Port PostgreSQL                              | `5432`                         |

---

## Endpoints API

### Authentification

| Methode | Endpoint             | Description             | Auth requise |
|---------|----------------------|-------------------------|--------------|
| `POST`  | `/api/token/`        | Obtenir un token JWT    | Non          |
| `POST`  | `/api/token/refresh/` | Rafraichir le token    | Non          |

### Messages (CRUD)

| Methode  | Endpoint              | Description                   | Auth requise |
|----------|-----------------------|-------------------------------|--------------|
| `GET`    | `/api/messages/`      | Lister tous les messages      | Oui          |
| `POST`   | `/api/messages/`      | Creer un nouveau message      | Oui          |
| `GET`    | `/api/messages/{id}/` | Recuperer un message          | Oui          |
| `PATCH`  | `/api/messages/{id}/` | Modifier un message           | Oui          |
| `DELETE` | `/api/messages/{id}/` | Supprimer un message          | Oui          |

### Utilitaires

| Methode | Endpoint        | Description           | Auth requise |
|---------|-----------------|-----------------------|--------------|
| `GET`   | `/api/health/`  | Verification de sante | Non          |

**Authentification :** Ajouter le header `Authorization: Bearer <access_token>` aux requetes protegees.

---

## Structure du projet

```
MarkeTech/
├── docker-compose.yml          # Orchestration des conteneurs
├── .env.example                # Template des variables d'environnement
├── .editorconfig               # Standards de formatage
├── LICENSE                     # Licence MIT
│
├── backend/
│   ├── Dockerfile              # Image Docker du backend
│   ├── entrypoint.sh           # Script de demarrage (migrations, collectstatic)
│   ├── requirements.txt        # Dependances Python
│   ├── manage.py               # Point d'entree Django
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py         # Configuration de base
│   │   │   ├── dev.py          # Settings developpement (SQLite)
│   │   │   └── prod.py         # Settings production (PostgreSQL)
│   │   ├── urls.py             # Routage racine
│   │   └── wsgi.py             # Point d'entree WSGI
│   └── api/
│       ├── models.py           # Modele Message
│       ├── views.py            # Vues API (ViewSet)
│       ├── serializers.py      # Serializers DRF
│       ├── urls.py             # Routes API
│       └── tests.py            # Tests unitaires
│
├── frontend/
│   ├── Dockerfile              # Image Docker multi-stage (build + Nginx)
│   ├── nginx.conf              # Configuration Nginx (SPA + proxy API)
│   ├── package.json            # Dependances Node.js
│   ├── vite.config.js          # Configuration Vite (proxy dev)
│   ├── index.html              # Point d'entree HTML
│   └── src/
│       ├── main.js             # Initialisation Vue
│       ├── App.vue             # Composant racine
│       ├── style.css           # Styles globaux
│       └── components/
│           ├── Status.vue          # Conteneur des cartes
│           ├── ApiHealthCard.vue   # Statut du backend
│           └── MessagesCrudCard.vue # Interface CRUD messages
│
└── .github/
    └── workflows/
        └── deploy.yml          # Pipeline CI/CD GitHub Actions
```

---

## Scripts disponibles

### Docker

```bash
docker compose up -d --build     # Construire et demarrer tous les services
docker compose down              # Arreter tous les services
docker compose ps                # Voir les services en cours
docker compose logs -f backend   # Suivre les logs du backend
docker compose logs -f frontend  # Suivre les logs du frontend
```

### Backend (developpement)

```bash
python manage.py runserver       # Serveur de developpement
python manage.py migrate         # Appliquer les migrations
python manage.py makemigrations  # Creer de nouvelles migrations
python manage.py collectstatic   # Collecter les fichiers statiques
python manage.py createsuperuser # Creer un superutilisateur
python manage.py shell           # Console interactive Python
python manage.py test            # Lancer les tests
```

### Frontend (developpement)

```bash
npm run dev      # Serveur de developpement Vite (hot-reload)
npm run build    # Build de production (dossier dist/)
npm run preview  # Previsualisation du build de production
```

---

## Deploiement CI/CD

Le projet utilise **GitHub Actions** avec un **runner self-hosted** :

- **Declencheur** : push sur la branche `main`
- **Etapes** :
  1. Checkout du code
  2. Copie du fichier `.env` depuis un emplacement securise sur le serveur
  3. Build et demarrage via `docker compose up -d --build`

---

## Licence

Ce projet est distribue sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de details.

Copyright (c) 2026 Daniel Garcia
