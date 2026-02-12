# 01_SPEC-TECH_MarkeTech.md

## 0) Objet du document

Ce document est la **spécification technique de référence** du projet **MarkeTech**.

But :

- Décrire **l’architecture cible** (dev + prod)
- Décrire la **stack**, les **composants**, les **conventions**
- Décrire la **roadmap technique** par phases
- Décrire la stratégie **Docker**, **Nginx**, **CI/CD**, **déploiement VPS**
- Décrire les choix **sécurité** (API, auth, secrets, HTTPS)
- Servir de “source of truth” pour maintenir le projet propre et cohérent

---

## 1) Contexte & objectifs

### 1.1 Contexte

MarkeTech est une application full-stack :

- **Backend API** : Django + Django REST Framework (DRF)
- **Frontend SPA** : Vue 3 + Vite
- **Reverse proxy** : Nginx (SPA + proxy `/api/`)
- **Base de données** : PostgreSQL
- **Conteneurisation** : Docker + Docker Compose
- **Livraison** : CI/CD (GitHub Actions) vers un **VPS Infomaniak** (Docker installé)
- **Domaine** : `danielgarcia.it` et sous-domaine `marketech.danielgarcia.it` (multi-services sur le même VPS via reverse proxy)

### 1.2 Objectifs

- **Reproductibilité** : environnement de dev identique pour toutes les machines
- **Lisibilité** : structure minimale mais pro (scalable)
- **Industrialisation** : build d’images propres, déploiement automatisé
- **Sécurité** : séparation admin/session vs API/JWT, secrets hors repo, HTTPS, permissions DRF strictes
- **Multi-services** : héberger plusieurs apps sur un seul VPS sans conflits de ports (routage hostname)

## 2) Stack technique (source of truth)

### 2.1 Backend

- **Python**
- **Django**
- **Django REST Framework**
- `python-dotenv` pour charger `.env` localement
- WSGI server en production : **Gunicorn** (pas `runserver`)

### 2.2 Frontend

- **Vue 3**
- **Vite**
- Appels API en **URL relative** via gateway Nginx : `fetch("/api/...")` (évite de gérer des domaines différents en prod)

### 2.3 Reverse proxy / Web server

- **Nginx**
  - sert le frontend build (fichiers statiques)
  - reverse proxy `/api/` vers backend
  - fallback SPA (index.html)
  - optionnel : sert `/media/`

### 2.4 Base de données

- **PostgreSQL** (container)
- Volume persistant
- Variables d’environnement injectées via docker-compose

### 2.5 Conteneurisation

- Dockerfiles distincts :
  - `backend/Dockerfile`
  - `frontend/Dockerfile` (multi-stage : build Vite → runtime Nginx)
- `docker-compose.yml` :
  - backend
  - frontend
  - db
  - (nginx gateway si séparé)

---

## 3) Décisions d’architecture (non négociables)

### 3.1 Option B : SPA séparée (choix acté)

- Django sert : `/api/` (et `/admin/`)
- La racine `/` et le routing SPA sont servis par Nginx (frontend Vue)
- Un 404 sur `/` côté Django en dev est **normal** tant que le frontend n’est pas branché via Nginx

### 3.2 Couplage frontend/backend

- Le frontend **ne doit pas** appeler `http://backend:8000` ou une URL absolue.
- Le frontend appelle toujours `/api/...` :
  - en dev via le gateway local
  - en prod via Nginx/TLS

### 3.3 Progression pédagogique (ordre recommandé)

1) Backend : API minimale **réelle** (CRUD, DB)
2) Industrialisation backend (admin, .env.example, requirements figé)
3) Dockeriser backend + Postgres
4) Dockeriser frontend + Nginx
5) CI/CD + déploiement VPS

---

## 4) Architecture cible – Vue d’ensemble

### 4.1 Schéma logique

Client navigateur → Nginx (gateway) →

- `/` → frontend (static build)
- `/api/` → backend Django (gunicorn)
  ↓
  PostgreSQL

### 4.2 Environnements

- **Dev local**
  - backend : Django `runserver`
  - frontend : Vite dev server
  - ou dev full Docker + gateway Nginx
- **Prod**
  - backend : Gunicorn (WSGI)
  - frontend : build Vite servi par Nginx
  - reverse proxy central TLS (Nginx) en frontal du VPS

---

## 5) Backend – structure, conventions et exigences

### 5.1 Organisation Django (settings pro)

Organisation attendue (déjà mise en place dans la reprise) :

- `backend/config/settings/base.py`
- `backend/config/settings/dev.py`
- `backend/config/settings/prod.py`

Principes :

- `base.py` : commun (apps, middleware, DRF, time zone, static)
- `dev.py` : `DEBUG=True`, permissif local
- `prod.py` : `DEBUG=False`, hosts stricts, DB postgres via env, security toggles

### 5.2 Routing backend

- `/api/...` : routes DRF
- `/admin/` : administration
- `/` : pas géré par Django (SPA)

### 5.3 API minimale requise (socle)

Obligation : API DRF “réelle” (pas uniquement des endpoints statiques)

- `Message` model
- serializer
- viewset
- router DRF (DefaultRouter)
- endpoints :
  - `GET /api/messages/`
  - `POST /api/messages/`
  - `DELETE /api/messages/{id}/`
- health endpoint :
  - `GET /api/health/` → `{ "status": "ok" }`

### 5.4 Logging

- Doit être lisible en Docker (`docker compose logs -f`)
- En prod : privilégier stdout/stderr (12-factor) + format structuré si possible (JSON ou format standard)

### 5.5 Static / media

- Décider clairement :
  - static build Django (admin, DRF browsable) vs Nginx
  - media uploads via volume + Nginx `location /media/`
- Objectif : que ce soit cohérent en Docker (volumes + chemins)

---

## 6) Frontend – structure, conventions et exigences

### 6.1 Vue 3 + Vite

- SPA minimaliste
- Routage si besoin (Vue Router)
- Un composant “Status” ou page de test qui affiche l’état API :
  `fetch("/api/health/")` → affichage `status: ok`

### 6.2 Couche API (recommandé)

- Créer un petit module `src/api/client.ts` (ou `.js`) :
  - base URL = `""` (donc relatif)
  - timeouts
  - gestion d’erreurs
- Si axios : config centralisée (mais fetch suffit au départ)

### 6.3 Build & déploiement

- En prod : build Vite → `dist/`
- `dist/` est servi par Nginx
- SPA fallback obligatoire : `try_files ... /index.html`

---

## 7) Nginx – exigences & design

### 7.1 Rôle

Nginx est le point d’entrée HTTP de la stack MarkeTech (au moins en local docker / en prod stack).
Il :

- sert le frontend (static)
- proxy `/api/` vers backend
- (optionnel) sert `/media/` depuis volume partagé

### 7.2 Reverse proxy `/api/`

Exigences :

- Passer les headers :
  - `Host`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`
- Garder une config “simple, lisible, stable”

### 7.3 SPA fallback

Obligatoire :

- Si l’URL n’est pas un fichier statique réel, renvoyer `index.html`
- Sinon le refresh sur `/route` casse

### 7.4 Nginx “gateway séparé” vs “nginx dans frontend”

Deux approches valides :

1) **Nginx dans l’image frontend** (souvent le plus simple)
   - frontend Dockerfile : build Vue → runtime Nginx avec conf
   - Nginx sert `dist/` + proxy `/api/`
2) **Nginx gateway séparé** (utile en prod multi-services)
   - un Nginx “gateway” dédié à la stack MarkeTech

Le choix peut dépendre du reverse proxy central (Traefik/Nginx) sur VPS.

---

## 8) Docker – architecture et standards

### 8.1 Objectifs Docker

- `docker compose up -d --build` doit démarrer l’app complète
- Les conteneurs doivent être **déclaratifs**, pas “bidouillés”
- Les builds doivent être **reproductibles** (versions figées)

### 8.2 Services attendus

- `db` : postgres officiel + volume persistant
- `backend` : image Python + gunicorn en prod
- `frontend` : build Vue + Nginx
- (optionnel) `proxy` : reverse proxy central multi-stacks sur VPS

### 8.3 Variables d’environnement (12-factor)

- `.env` local non committé
- `.env.example` committé
- En CI/CD : secrets gérés dans le provider (GitHub/GitLab)
- En prod VPS : env fournis via :
  - `.env` sur le serveur (hors repo)
  - ou secrets de compose (si besoin)

### 8.4 Healthchecks

Recommandé :

- backend : GET `/api/health/`
- frontend/nginx : GET `/` (ou endpoint static)
- db : healthcheck postgres

### 8.5 Migration strategy

Stratégie simple (phase initiale) :

- migrations manuelles via commande
  Puis (phase prod) :
- entrypoint backend qui applique migrations (optionnel)
- ou job “migrate” séparé dans compose

---

## 9) CI/CD – design cible

### 9.1 Pipeline (minimum pro)

1) Lint / format
2) Tests (backend)
3) Build images Docker
4) Push vers registry (GHCR ou GitLab Registry)
5) Deploy VPS (SSH) :
   - pull images
   - `docker compose up -d`
   - smoke test health endpoint

### 9.2 Tagging & rollback

- Tag image : `latest` + tag commit (SHA) ou version semver
- Rollback : redeploy un tag précédent (simple et fiable)

### 9.3 Secrets

- SSH private key (deploy)
- Registry token
- `DJANGO_SECRET_KEY`, DB password, etc.
- Aucun secret dans repo (`.env` ignoré, `*.key` ignoré)

---

## 10) Déploiement VPS Infomaniak & multi-services

### 10.1 Objectif

Sur un **seul VPS** :

- `danielgarcia.it` → site web
- `marketech.danielgarcia.it` → stack MarkeTech
- + possibilité d’ajouter `N` autres services plus tard

### 10.2 Stratégie recommandée

Mettre un **reverse proxy frontal unique** sur le VPS (écoute 80/443) :

- Traefik (souvent le plus simple pour Let’s Encrypt auto)
- ou Nginx + certbot (plus manuel)

Il route par hostname vers des stacks Docker internes :

- stack website
- stack marketech

Important :

- seules les instances proxy exposent 80/443 au monde
- les stacks internes exposent leurs ports uniquement sur réseau docker

---

## 11) Sécurité – spécification

> Résumé “non négociable” : admin Django = session + CSRF, API = JWT, HTTPS obligatoire en prod, permissions explicites, secrets hors repo.

### 11.1 Auth : séparation des responsabilités

- **Admin Django**
  - session cookie
  - protection CSRF native Django
- **API DRF**
  - JWT access + refresh
  - refresh rotation obligatoire
- **Frontend**
  - access token : mémoire uniquement (jamais localStorage)
  - `Authorization: Bearer <token>` sur endpoints protégés :contentReference[oaicite:31]{index=31}

### 11.2 Endpoints & permissions

- Endpoints publics : `/api/health`, `/api/login`, `/api/signup` (selon implémentation)
- Endpoints protégés : permissions DRF explicites (deny-by-default)
- Interdit : `@csrf_exempt` non justifié :contentReference[oaicite:32]{index=32}

### 11.3 Transport & configuration prod

- HTTPS obligatoire
- `DEBUG=False`
- `ALLOWED_HOSTS` strict via env
- cookies sécurisés si besoin (Secure, HttpOnly, SameSite)
- CORS strict (quand nécessaire)
- security headers (HSTS, X-Content-Type-Options, etc.) — phase hardening

---

## 12) Roadmap technique (phases)

### Phase 0 — Base technique (socle)

- Docker multi-container
- Reverse proxy
- Health endpoint
- CRUD message + DB validation
- SPA connectée

### Phase 1 — Auth & Sécurité (en cours / à implémenter)

- JWT (access + refresh)
- séparation admin session vs API JWT
- permissions DRF strictes
- login endpoint
- refresh rotation

### Phase 2 — User system SaaS

- signup
- email verification
- password reset
- profil user
- RBAC simple si besoin

### Phase 3 — Production hardening

- HTTPS (Let’s Encrypt)
- secure cookies
- CORS strict
- security headers
- logging structuré
- rate limiting

### Phase 4 — SaaS readiness

- subscriptions
- roles avancés
- versioning API
- CI/CD complet / mature

---

## 13) Règles de qualité du projet (standard pro)

- Repo clean (pas de secrets, pas de dumps, pas de fichiers générés)
- `.env.example` obligatoire
- Versions dépendances figées à terme (requirements + package-lock)
- README technique maintenu
- Chaque étape doit être reproductible via :
  - run local
  - ou docker compose
- Aucun “workaround” non documenté

---

## 14) Points “plus tard” à garder en tête

- Auth utilisateur : possibilité `django-allauth` (à décider au moment du design auth)
- Certificats TLS : Let’s Encrypt (Traefik recommandé)
- Optimisations Docker : non-root, multi-stage, images slim
- Observabilité : logs structurés, metrics basiques si besoin

---
