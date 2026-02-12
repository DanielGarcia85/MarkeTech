# 02_RUNBOOK-COMMANDES_MarkeTech.md

## 0) Objectif de ce document

Ce document est le **runbook opérationnel** du projet MarkeTech.

Il contient :

- Toutes les commandes utiles en **développement local**
- Toutes les commandes utiles en **Docker**
- Les workflows standards (rebuild partiel, reset total, nettoyage)
- Les explications claires de `--build`, `--force-recreate`, etc.
- Les procédures de debug
- Les procédures de reset propre
- Les bonnes pratiques de manipulation Docker

⚠️ Ce document ne contient PAS la théorie ni l’architecture.

---

# 1) Backend – Développement local (sans Docker)

## 1.1 Initialisation du projet (Windows PowerShell)

```powershell
cd MarkeTech
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
```

## 1.2 Lancer le backend Django

```powershell
cd backend
python manage.py runserver
```

Le serveur démarre en général sur :

```cpp
http://127.0.0.1:8000/
```

⚠️ runserver = serveur de développement uniquement.
Jamais utilisé en production.
En production → Gunicorn derrière Nginx.

## 1.3 Appliquer les migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

## 1.4 Créer un superuser

```powershell
python manage.py createsuperuser
```

Admin accessible sur :

```arduino
http://127.0.0.1:8000/admin/
```

## 1.5 Tester l’API

Health endpoint :

```ruby
http://127.0.0.1:8000/api/health/
```

Test via curl :

```powershell
curl http://127.0.0.1:8000/api/health/
```

---

# 2) Frontend – Développement local (sans Docker)

## 2.1 Installation

```powershell
cd frontend
npm install
```

## 2.2 Lancer Vite

```powershell
npm run dev
```

Frontend accessible sur :

```arduino
http://localhost:5173
```

## 2.3 Vérifier connexion API via gateway

Dans DevTools → Network :

```bash
GET /api/health/ → 200
```

---

# 3) Docker – Commandes standard

## 3.1 Démarrer la stack complète

```powershell
docker compose up -d --build
```

Explication :

- -d = detached
- --build = rebuild images si nécessaire

## 3.2 Voir les logs

```powershell
docker compose logs -f
```

Backend seulement :

```powershell
docker compose logs -f backend
```

## 3.3 Stopper la stack

```powershell
docker compose down
```

## 3.4 Stopper + supprimer volumes (⚠️ RESET DB)

```powershell
docker compose down -v
```

⚠️ Supprime la base Postgres et tous volumes liés.

---

# 4) Workflow propre en développement

## 4.1 Modifier code backend

Rebuild backend uniquement :

```powershell
docker compose up -d --build backend
```

## 4.2 Modifier frontend

```powershell
docker compose up -d --build frontend
```

## 4.3 Modifier uniquement nginx.conf (proxy)

Pas besoin de rebuild image.

Reload nginx :

```powershell
docker exec -it reverse-proxy nginx -t
docker exec -it reverse-proxy nginx -s reload
```

Ou :

```powershell
docker compose -f .\infra\proxy\docker-compose.proxy.yml up -d --force-recreate
```

---

# 5) Reset complet propre (Stack + Proxy)

## 5.1 Stopper tout

```powershell
docker compose -f .\infra\proxy\docker-compose.proxy.yml down
docker compose down
```

## 5.2 Reset complet avec suppression volumes

```powershell
docker compose -f .\infra\proxy\docker-compose.proxy.yml down -v
docker compose down -v
```

## 5.3 Supprimer images du projet

```powershell
docker image rm -f marketech-backend marketech-frontend 2>$null
```

## 5.4 Nettoyer cache build

```powershell
docker image prune -f
docker builder prune -f
```

Reset agressif :

```powershell
docker system prune -af
docker builder prune -af
```

## 5.5 Recréer network proxy

```powershell
docker network rm proxy 2>$null
docker network create proxy
```

## 5.6 Rebuild complet

```powershell
docker compose up -d --build
docker compose -f .\infra\proxy\docker-compose.proxy.yml up -d #proxy
```

---

# 6) One-liner reset total (PowerShell)

```powershell
docker compose -f .\infra\proxy\docker-compose.proxy.yml down; docker compose down; docker image rm -f marketech-backend marketech-frontend 2>$null; docker image prune -f; docker builder prune -f; docker compose up -d --build; docker compose -f .\infra\proxy\docker-compose.proxy.yml up -d
```

Avec suppression volumes :

```powershell
docker compose -f .\infra\proxy\docker-compose.proxy.yml down -v; docker compose down -v; docker image rm -f marketech-backend marketech-frontend 2>$null; docker image prune -f; docker builder prune -f; docker compose up -d --build; docker compose -f .\infra\proxy\docker-compose.proxy.yml up -d
```

---

# 7) Comprendre `--build` vs `--force-recreate`

## 7.1 `--build`

Rebuild image avant démarrage.

Utiliser si :

- code changé
- requirements.txt changé
- package-lock.json changé

## 7.2 `--force-recreate`

Recrée conteneur même si image inchangée.

Utiliser si :

- .env modifié
- variables env changées
- networks changés
- config mount modifiée

## 7.3 Combo “bulldozer propre”

```powershell
docker compose up -d --build --force-recreate
Rebuild + recrée conteneurs.
```

---

# 8) Nettoyage régulier recommandé

Pour éviter accumulation BuildKit :

```powershell
docker builder prune -f
```

---

# 9) Vérifications production readiness (local Docker)

Checklist :

```powershell
docker compose logs -f
```

Tester :

```ruby
http://marketech.local/api/health/
```

Vérifier :

- ALLOWED_HOSTS OK
- DEBUG=False en prod
- migrations appliquées
- pas d’erreurs 500
- secrets absents du repo

---

# 10) Déploiement VPS (manuel simplifié)

Sur VPS :

```bash
docker compose pull
docker compose up -d
```

Plus tard via CI/CD automatisé.

---

# 11) Commandes Git essentielles

Commit propre :

```bash
git status
git add .
git commit -m "feat: description claire"
git push
```

---

# 12) Commandes utiles Debug

Lister conteneurs :

```powershell
docker ps
```

Entrer dans backend :

```powershell
docker exec -it marketech-backend sh
```

Tester DB :

```powershell
docker exec -it marketech-db psql -U postgres
```

---

# 13) Stratégie recommandée (vu ton style “reset propre”)

En dev normal :

```powershell
docker compose up -d --build
```

Si env modifié :

```powershell
docker compose up -d --build --force-recreate backend
```

Nettoyage régulier :

```powershell
docker builder prune -f
```

Reset total occasionnel : utiliser le one-liner.

---

# 14) Rappel important

- runserver = DEV ONLY
- Prod = Gunicorn + Nginx
- / sera servi par frontend Vue via Nginx
- /api/ servi par Django
- HTTPS géré par reverse proxy frontal (Traefik ou Nginx + certbot) plus tard
