# 03_SECURITY-API_MarkeTech.md

## 0) Objet du document

Ce document définit la **stratégie complète de sécurité applicative** pour le projet **MarkeTech**.

Il couvre :

- L’architecture d’authentification (Admin vs API)
- La gestion des JWT (access + refresh + rotation)
- La protection des endpoints DRF
- La gestion des tokens côté frontend Vue
- La gestion des secrets
- La configuration sécurité Django (dev vs prod)
- HTTPS / reverse proxy / TLS
- CORS, CSRF, cookies sécurisés
- Hardening production
- Bonnes pratiques DevOps liées à la sécurité

Ce document est une **référence normative**.
Tout nouveau développement doit respecter ces règles.

---

# 1) Principes fondamentaux

---

## 1.1 Séparation des responsabilités

MarkeTech distingue clairement :

| Composant     | Authentification       | Usage                      |
| ------------- | ---------------------- | -------------------------- |
| Admin Django  | Session + CSRF         | Back-office interne        |
| API REST      | JWT (access + refresh) | SPA Vue / clients externes |
| Reverse proxy | TLS / HTTPS            | Chiffrement transport      |

⚠️ On ne mélange jamais session auth admin et JWT API.

---

## 1.2 Approche “Security by Layers”

La sécurité repose sur une superposition cohérente de couches :

1. HTTPS (transport sécurisé)
2. Authentification (JWT / session)
3. Permissions DRF (contrôle d’accès)
4. Rotation de tokens
5. Absence de secrets dans le repo
6. Configuration prod stricte (DEBUG=False)
7. Headers de sécurité
8. CORS strict
9. Isolation Docker

Aucune couche ne suffit seule.

---

# 2) Architecture d’authentification

---

## 2.1 Admin Django (Back-office)

### Mécanisme

- Authentification par **session**
- Protection native **CSRF**
- Cookies HttpOnly

### Règles

- Aucune désactivation de CSRF
- Jamais de `@csrf_exempt` non justifié
- Accessible uniquement via HTTPS en production
- Accès restreint par `ALLOWED_HOSTS`

---

## 2.2 API REST – JWT

### Type d’authentification

- JWT access token (courte durée)
- JWT refresh token (longue durée)
- Rotation obligatoire des refresh tokens

### Flux normal

1. Login → renvoie :
   - access_token
   - refresh_token
2. Frontend stocke :
   - access en mémoire uniquement
   - refresh de manière contrôlée (jamais localStorage)
3. Chaque requête protégée :
   - Authorization: Bearer <access_token>
4. Si access expiré :
   - appel endpoint refresh
   - nouveau access token émis
   - rotation du refresh token

---

## 2.3 Durées recommandées

| Token    | Durée recommandée |
| -------- | ------------------- |
| Access   | 5–15 minutes       |
| Refresh  | 7–14 jours         |
| Rotation | Oui, obligatoire    |

---

## 2.4 Implémentation recommandée

Utiliser :

djangorestframework-simplejwt

Configuration stricte :

- BLACKLIST activée
- ROTATE_REFRESH_TOKENS = True
- UPDATE_LAST_LOGIN = True

---

# 3) Gestion des tokens côté Frontend Vue

---

## 3.1 Stockage sécurisé

### Access token

- Stocké **uniquement en mémoire**
- Jamais dans localStorage
- Jamais dans sessionStorage

Pourquoi ?

- localStorage est vulnérable en cas de XSS

---

## 3.2 Refresh token

Deux approches possibles :

### Option A (recommandée)

Refresh token en **cookie HttpOnly sécurisé**

- HttpOnly
- Secure
- SameSite=Strict
- Accessible uniquement via HTTPS

Avantage :

- Non accessible via JavaScript
- Protégé contre XSS

---

## 3.3 Gestion Axios / Fetch

Intercepteur :

- Ajoute Authorization header
- Gère automatiquement 401
- Tente refresh
- Retry requête originale

---

# 4) Sécurité des endpoints DRF

---

## 4.1 Règle par défaut

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ]
}
```

Tout endpoint est protégé par défaut.

---

# 4.2 Endpoints publics autorisés

Exemples :

- /api/health/
- /api/login/
- /api/signup/

Ils doivent explicitement définir :

```python
permission_classes = [AllowAny]
```

---

# 4.3 Interdictions

- Pas de AllowAny sans justification
- Pas de @csrf_exempt pour simplifier
- Pas de endpoints admin exposés publiquement
- Pas de DEBUG=True en prod

---

# 5) Configuration Django – Sécurité Prod

---

## 5.1 DEBUG

```python
DEBUG = False
```

Obligatoire en production.

---

# 5.2 ALLOWED_HOSTS

Doit être défini via variable d’environnement :

``ìni
DJANGO_ALLOWED_HOSTS=marketech.danielgarcia.it

```

Jamais "*" en prod.

---

# 5.3 SECRET_KEY

- Jamais commitée
- Stockée en variable d’environnement
- Minimum 50 caractères
- Générée aléatoirement

---

# 5.4 Cookies sécurisés

En production :

```python
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

---

# 5.5 HSTS

```python
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

# 5.6 Proxy SSL header

Si reverse proxy TLS :

```phyton
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

# 6) HTTPS & Reverse Proxy

---

## 6.1 HTTPS obligatoire

Toutes les communications doivent être chiffrées.

- Let’s Encrypt
- Certificats automatiques via Traefik ou Nginx + certbot

---

# 6.2 Reverse proxy frontal

Architecture recommandée :

- Un reverse proxy central
- Route par hostname :
  - danielgarcia.it
  - marketech.danielgarcia.it

Seul le proxy expose 80/443.

---

# 7) CORS

---

## 7.1 Règle

En production :

```pyhton
CORS_ALLOWED_ORIGINS = [
    "https://marketech.danielgarcia.it",
]
```

Pas de :

```phyton
CORS_ALLOW_ALL_ORIGINS = True
```

---

# 8) Protection contre attaques courantes

---

## 8.1 XSS

- Pas de tokens dans localStorage
- Sanitisation input frontend
- HttpOnly cookies

---

# 8.2 CSRF

- Admin protégé par CSRF
- API JWT non vulnérable aux CSRF classiques

---

# 8.3 Bruteforce login

Recommandé :

- Rate limiting
- django-axes (optionnel)

---

# 8.4 Rate limiting API

Implémentation possible :

```pyhton
DEFAULT_THROTTLE_CLASSES
DEFAULT_THROTTLE_RATES
```

Exemple :

- anon: 100/day
- user: 1000/day

---

# 9) Sécurité Docker

---

## 9.1 Secrets

- Pas de .env dans repo
- .env.example versionné
- Variables prod injectées via VPS

---

# 9.2 Non-root containers

Dockerfile backend :

- Créer user non-root
- USER appuser

---

# 9.3 Isolation réseau

- DB non exposée publiquement
- Backend non exposé publiquement
- Seul proxy expose 80/443

---

# 10) Logging & Audit

---

# 10.1 Logs sécurité

- Log login
- Log échecs login
- Log accès admin
- Log erreurs 401/403

---

# 10.2 Format logs

Préférer format JSON en prod.

---

11) Checklist Sécurité Production

Avant mise en ligne :

- DEBUG=False
- ALLOWED_HOSTS correct
- SECRET_KEY sécurisée
- HTTPS actif
- Certificat valide
- JWT rotation activée
- Cookies sécurisés
- CORS strict
- Aucun secret dans repo
- DB non exposée
- Proxy correctement configuré
- Health endpoint fonctionnel

---

# 12) Évolution future (Phase 2–4)

- Email verification
- Password reset sécurisé
- RBAC avancé
- Subscription system
- Audit trail
- API versioning
- Monitoring sécurité
- WAF éventuel

---

# 13) Conclusion

- La sécurité de MarkeTech repose sur :
- Une séparation claire admin / API
- JWT avec rotation
- HTTPS obligatoire
- Permissions strictes
- Secrets hors repo
- Isolation Docker
- Configuration prod rigoureuse

Aucune dérogation ne doit être faite sans justification explicite.
