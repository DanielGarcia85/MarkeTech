# backend/demo/management/commands/seed_demo.py

"""
Seed demo — test accounts, offers, applications, favorites, messages, appointments, reviews
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Fill a development database with what the pages need to be looked at: three
candidates with a CV and documents, three employers with their company and
its logo, ten job offers per employer spread over the cities, the
contracts, the salaries and the last two months — eight published, one
draft and one closed each — thirteen applications in every state, with
their history, eight favorites, conversations on the applications that
were taken up: open ones, closed ones, some with unread messages, and six
appointments in every state, past and to come, and the reviews of the
platform by five of the six accounts, from 3 to 5 stars. The two
accounts to show the site with are candidat1@example.com (Léa Martin) and
employeur1@example.com (Marc Rochat, Quorvane SA), between whom most of it
happens (decision of 21.10.2026). Everything is invented, the files included:
one-page PDFs written by the command itself (no library needed for a page
of text), and logos drawn with Pillow (the initials of the company on a
colour), which the image fields need anyway. The addresses are in
example.com, a domain reserved for examples that receives no e-mail, and
the companies have invented names, checked to belong to nobody (decisions
of 22.10.2026).

The public demonstration
────────────────────────
candidat1 and employeur1 are the two demo accounts (is_demo): any visitor
opens them with the buttons of the login page, without password
(demo/views.py), and the server runs this command again every night with
--reset. In development (DEBUG), the six accounts share one password,
printed at the end; elsewhere, none has a usable password, and the four
other accounts are there to be seen, not to be opened.

    python manage.py seed_demo          creates everything, once
    python manage.py seed_demo --reset  deletes the six accounts first (their
                                        profiles, offers, applications,
                                        favorites, messages, appointments,
                                        reviews and files go with them;
                                        the other accounts stay)
    python manage.py seed_demo --force  on a server (DEBUG off)

Why a command and not a fixture
───────────────────────────────
A fixture (loaddata) is a dump of rows: the passwords would be stored
hashed, the verified addresses of allauth would have to be dumped too, and
the dates of publication would be frozen the day of the dump, so that
"published after" would soon find nothing. A command builds the rows with
the code of the application and dates them relative to today.

Safety
──────
With DEBUG off (a server), the command runs only with --force, given on
purpose: it deletes and makes again the six accounts and all that hangs on
them. The accounts get no usable password there, and the output lists no
address: it goes to the journal of the server.
"""

from datetime import timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

from allauth.account.models import EmailAddress
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from accounts.models import User
from applications.models import Attachment, JobApplication
from applications.serializers import copy_of
from appointments.models import Appointment
from favorites.models import Favorite
from messaging.models import Message
from offers.models import JobOffer
from profiles.models import CandidateDocument, CandidateProfile, EmployerProfile
from reviews.models import CRITERIA, Review

# The password of the six accounts in development; none on a server
PASSWORD = "Demo-1234"

# ── The candidates ────────────────────────────────────────────────────
# The account (names), the profile (contact details), the lines of the CV
# and the names of the documents, in one dict each

CANDIDATES = [
    {
        "email": "candidat1@example.com",
        # Open to every visitor, from the login page
        "demo": True,
        "first_name": "Léa",
        "last_name": "Martin",
        "phone": "+41 79 000 00 01",
        "address": "Rue du Lac 12",
        "postal_code": "1207",
        "city": "Genève",
        "country": "CH",
        "cv": [
            "Développeuse full stack",
            "Quatre ans d'expérience en Java Spring et Vue.js",
            "Bachelor en informatique de gestion, HEG Genève",
            "Français, anglais",
        ],
        "documents": ["Diplome_HEG.pdf", "Certificat_travail.pdf"],
    },
    {
        "email": "candidat2@example.com",
        "first_name": "Nicolas",
        "last_name": "Favre",
        "phone": "+41 79 000 00 02",
        "address": "Avenue Cardinal-Mermillod 8",
        "postal_code": "1227",
        "city": "Carouge",
        "country": "CH",
        "cv": [
            "Ingénieur DevOps",
            "Six ans en administration Linux et cloud AWS",
            "CFC d'informaticien, brevet fédéral",
            "Français, anglais, allemand",
        ],
        "documents": ["Certificat_CFC.pdf"],
    },
    {
        "email": "candidat3@example.com",
        "first_name": "Inès",
        "last_name": "Dupont",
        "phone": "+33 6 00 00 00 03",
        "address": "Rue de la Gare 5",
        "postal_code": "74100",
        "city": "Annemasse",
        "country": "FR",
        "cv": [
            "Data scientist junior",
            "Master en science des données, Université de Lyon",
            "Stage de six mois en data engineering",
            "Français, anglais, espagnol",
        ],
        "documents": ["Attestation_stage.pdf"],
    },
]

# ── The employers and their offers ────────────────────────────────────
# One dict per employer: the account, the profile with the company, and
# the offers. An offer: the fields of the model, plus "days_ago", the age
# of its publication (None for a draft).

EMPLOYERS = [
    {
        "email": "employeur1@example.com",
        # Open to every visitor, from the login page
        "demo": True,
        "first_name": "Marc",
        "last_name": "Rochat",
        "phone": "+41 22 000 00 01",
        "address": "Rue de Lausanne 45",
        "postal_code": "1201",
        "city": "Genève",
        "country": "CH",
        "company_name": "Quorvane SA",
        "company_address": "Rue de Lausanne 45",
        "company_postal_code": "1201",
        "company_city": "Genève",
        "company_country": "CH",
        "company_phone": "+41 22 000 00 10",
        "logo": ("QV", "#2d6f91"),
        "offers": [
            {
                "title": "Développeur·euse Java Spring senior",
                "city": "Genève",
                "country": "CH",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": 9000,
                "salary_max": 11000,
                "salary_period": "month",
                "experience_years": 5,
                "status": "published",
                "days_ago": 2,
                "description": (
                    "Nous renforçons l'équipe qui développe notre plateforme de gestion "
                    "documentaire, utilisée par une centaine de fiduciaires romandes.\n\n"
                    "Vos missions :\n"
                    "- concevoir et développer de nouveaux services REST avec Spring Boot ;\n"
                    "- faire évoluer le modèle de données (PostgreSQL, Flyway) ;\n"
                    "- relire le code des collègues et accompagner les juniors.\n\n"
                    "Profil : cinq ans d'expérience Java en production, à l'aise avec les "
                    "tests automatisés et l'intégration continue. Français courant, anglais "
                    "technique."
                ),
            },
            {
                "title": "Développeur·euse Full Stack Vue / Django",
                "city": "Genève",
                "country": "CH",
                "contract": "permanent",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 7500,
                "salary_max": 9000,
                "salary_period": "month",
                "experience_years": 3,
                "status": "published",
                "days_ago": 5,
                "description": (
                    "Pour un nouveau produit interne, nous cherchons une personne capable de "
                    "prendre en charge une fonctionnalité de bout en bout : l'API en Django "
                    "REST Framework, l'interface en Vue 3 et TypeScript, les tests des deux "
                    "côtés.\n\n"
                    "Équipe de six personnes, déploiements continus, revue de code "
                    "systématique. Poste basé à Genève, dans nos bureaux de la rue de "
                    "Lausanne."
                ),
            },
            {
                "title": "Ingénieur·e DevOps",
                "city": "Genève",
                "country": "CH",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": 110000,
                "salary_max": 130000,
                "salary_period": "year",
                "experience_years": 4,
                "status": "published",
                "days_ago": 9,
                "description": (
                    "Vous prenez en main notre chaîne de livraison : GitHub Actions, images "
                    "Docker, déploiements sur des machines virtuelles Linux, supervision et "
                    "sauvegardes.\n\n"
                    "Nous attendons une bonne maîtrise de Linux, de Docker Compose et d'au "
                    "moins un outil d'infrastructure as code. Une expérience de Kubernetes "
                    "est un plus, pas une condition."
                ),
            },
            {
                "title": "Stagiaire développement web",
                "city": "Genève",
                "country": "CH",
                "contract": "internship",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 2500,
                "salary_max": None,
                "salary_period": "month",
                "experience_years": None,
                "status": "published",
                "days_ago": 12,
                "description": (
                    "Stage de six mois pour une personne en fin de Bachelor en informatique. "
                    "Vous participez au développement de l'interface d'administration de "
                    "notre plateforme, encadré·e par un développeur senior.\n\n"
                    "Début possible dès le 1er février. Indemnité de stage de CHF 2 500 par "
                    "mois."
                ),
            },
            {
                "title": "Testeur·euse QA automatisation",
                "city": "Carouge",
                "country": "CH",
                "contract": "fixed_term",
                "remote": "on_site",
                "workload_min": 60,
                "workload_max": 80,
                "salary_min": 6000,
                "salary_max": 7000,
                "salary_period": "month",
                "experience_years": 2,
                "status": "published",
                "days_ago": 18,
                "description": (
                    "Contrat d'un an, renouvelable, pour mettre en place les tests de bout "
                    "en bout de notre application web avec Playwright et les intégrer à "
                    "la chaîne d'intégration continue.\n\n"
                    "Vous avez déjà écrit des tests automatisés sur un produit réel et vous "
                    "savez décrire un défaut de façon reproductible."
                ),
            },
            {
                "title": "Administrateur·trice systèmes Linux",
                "city": "Genève",
                "country": "CH",
                "contract": "permanent",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 7000,
                "salary_max": 8500,
                "salary_period": "month",
                "experience_years": 3,
                "status": "published",
                "days_ago": 25,
                "description": (
                    "Vous administrez une vingtaine de serveurs Debian (web, bases de "
                    "données, messagerie) et le réseau de nos deux sites.\n\n"
                    "Astreinte une semaine sur six, compensée. Permis de conduire "
                    "souhaité pour les déplacements entre Genève et Nyon."
                ),
            },
            {
                "title": "Développeur·euse mobile Android",
                "city": "Nyon",
                "country": "CH",
                "contract": "permanent",
                "remote": "remote",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": None,
                "salary_max": None,
                "salary_period": "month",
                "experience_years": 3,
                "status": "published",
                "days_ago": 33,
                "description": (
                    "Télétravail complet possible depuis la Suisse, avec une journée par "
                    "mois à Nyon. Vous développez en Kotlin l'application mobile de nos "
                    "clients fiduciaires : consultation de documents, signature, "
                    "notifications.\n\n"
                    "Salaire selon expérience, à discuter lors du premier entretien."
                ),
            },
            {
                "title": "Étudiant·e support informatique",
                "city": "Genève",
                "country": "CH",
                "contract": "student",
                "remote": "on_site",
                "workload_min": 40,
                "workload_max": 50,
                "salary_min": 1800,
                "salary_max": 2200,
                "salary_period": "month",
                "experience_years": None,
                "status": "published",
                "days_ago": 41,
                "description": (
                    "Job étudiant, deux à deux jours et demi par semaine, compatible avec "
                    "un horaire de cours. Support de premier niveau pour nos collaborateurs "
                    "(postes Windows et macOS, imprimantes, comptes), préparation des "
                    "machines.\n\n"
                    "Idéal pour une personne en Bachelor en informatique de gestion."
                ),
            },
            {
                "title": "Architecte logiciel",
                "city": "Genève",
                "country": "CH",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 130000,
                "salary_max": 150000,
                "salary_period": "year",
                "experience_years": 8,
                "status": "draft",
                "days_ago": None,
                "description": (
                    "Brouillon : à compléter avec la direction technique avant publication.\n\n"
                    "Responsable de l'architecture de la plateforme et des choix "
                    "technologiques, en lien avec les trois équipes de développement."
                ),
            },
            {
                "title": "Développeur·euse PHP Symfony",
                "city": "Genève",
                "country": "CH",
                "contract": "permanent",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 7000,
                "salary_max": 8000,
                "salary_period": "month",
                "experience_years": 2,
                "status": "closed",
                "days_ago": 55,
                "description": (
                    "Poste pourvu. Maintenance et évolution de notre ancien portail client "
                    "en Symfony, en attendant sa migration."
                ),
            },
        ],
    },
    {
        "email": "employeur2@example.com",
        "first_name": "Sophie",
        "last_name": "Bianchi",
        "phone": "+41 21 000 00 02",
        "address": "Avenue de Rhodanie 30",
        "postal_code": "1007",
        "city": "Lausanne",
        "country": "CH",
        "company_name": "Talmivo Sàrl",
        "company_address": "Avenue de Rhodanie 30",
        "company_postal_code": "1007",
        "company_city": "Lausanne",
        "company_country": "CH",
        "company_phone": "+41 21 000 00 20",
        "logo": ("TM", "#2f855a"),
        "offers": [
            {
                "title": "Data engineer Python",
                "city": "Lausanne",
                "country": "CH",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": 8500,
                "salary_max": 10000,
                "salary_period": "month",
                "experience_years": 3,
                "status": "published",
                "days_ago": 1,
                "description": (
                    "Vous construisez et exploitez les pipelines de données de nos clients "
                    "(Airflow, dbt, PostgreSQL, BigQuery), de l'ingestion jusqu'aux tableaux "
                    "de bord.\n\n"
                    "Trois ans d'expérience en Python et SQL sur des volumes réels. Deux "
                    "jours de télétravail par semaine."
                ),
            },
            {
                "title": "Ingénieur·e cloud AWS",
                "city": "Lausanne",
                "country": "CH",
                "contract": "permanent",
                "remote": "remote",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 120000,
                "salary_max": 140000,
                "salary_period": "year",
                "experience_years": 5,
                "status": "published",
                "days_ago": 4,
                "description": (
                    "Conception et exploitation des environnements AWS de nos clients : "
                    "Terraform, EKS, observabilité, maîtrise des coûts.\n\n"
                    "Poste en télétravail depuis la Suisse, réunions d'équipe à Lausanne "
                    "une fois par mois. Certification AWS appréciée."
                ),
            },
            {
                "title": "Analyste BI / Power BI",
                "city": "Lausanne",
                "country": "CH",
                "contract": "permanent",
                "remote": "on_site",
                "workload_min": 60,
                "workload_max": 100,
                "salary_min": 7000,
                "salary_max": 8500,
                "salary_period": "month",
                "experience_years": 2,
                "status": "published",
                "days_ago": 7,
                "description": (
                    "Vous traduisez les besoins des métiers en modèles de données et en "
                    "rapports Power BI, et vous formez les utilisateurs.\n\n"
                    "Taux d'activité entre 60 et 100 % selon votre disponibilité."
                ),
            },
            {
                "title": "Data scientist junior",
                "city": "Lausanne",
                "country": "CH",
                "contract": "fixed_term",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 6500,
                "salary_max": 7500,
                "salary_period": "month",
                "experience_years": 1,
                "status": "published",
                "days_ago": 11,
                "description": (
                    "Contrat de dix-huit mois sur un projet de prévision de la demande pour "
                    "un distributeur romand : exploration des données, modèles, mise en "
                    "production avec l'équipe data engineering.\n\n"
                    "Master en science des données ou équivalent, Python (pandas, "
                    "scikit-learn), SQL."
                ),
            },
            {
                "title": "Ingénieur·e sécurité informatique",
                "city": "Berne",
                "country": "CH",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": None,
                "salary_max": None,
                "salary_period": "year",
                "experience_years": 4,
                "status": "published",
                "days_ago": 15,
                "description": (
                    "Pour notre bureau de Berne : audits de sécurité des plateformes de "
                    "données de nos clients, durcissement des environnements cloud, "
                    "réponse aux incidents.\n\n"
                    "Allemand et français exigés. Salaire selon profil."
                ),
            },
            {
                "title": "Stage data engineering",
                "city": "Lausanne",
                "country": "CH",
                "contract": "internship",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 2200,
                "salary_max": None,
                "salary_period": "month",
                "experience_years": None,
                "status": "published",
                "days_ago": 21,
                "description": (
                    "Stage de six mois au sein de l'équipe data engineering : qualité des "
                    "données, tests de pipelines, documentation.\n\n"
                    "Ouvert aux étudiant·e·s de dernière année en informatique ou en "
                    "informatique de gestion."
                ),
            },
            {
                "title": "Administrateur·trice bases de données PostgreSQL",
                "city": "Zurich",
                "country": "CH",
                "contract": "permanent",
                "remote": "remote",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 115000,
                "salary_max": 125000,
                "salary_period": "year",
                "experience_years": 5,
                "status": "published",
                "days_ago": 29,
                "description": (
                    "Exploitation, performance et sauvegarde des bases PostgreSQL de nos "
                    "clients (une cinquantaine d'instances), migrations de versions, "
                    "conseil aux équipes de développement.\n\n"
                    "Télétravail complet, rattachement au bureau de Zurich."
                ),
            },
            {
                "title": "Développeur·euse backend Go",
                "city": "Lausanne",
                "country": "CH",
                "contract": "permanent",
                "remote": "remote",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": 8000,
                "salary_max": 9500,
                "salary_period": "month",
                "experience_years": 3,
                "status": "published",
                "days_ago": 38,
                "description": (
                    "Vous développez les services d'ingestion de données à haut débit de "
                    "notre plateforme, en Go, déployés sur Kubernetes.\n\n"
                    "Une expérience d'un autre langage compilé est bienvenue si vous "
                    "souhaitez passer à Go."
                ),
            },
            {
                "title": "Responsable plateforme data",
                "city": "Lausanne",
                "country": "CH",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 140000,
                "salary_max": 160000,
                "salary_period": "year",
                "experience_years": 8,
                "status": "draft",
                "days_ago": None,
                "description": (
                    "Brouillon. Direction de l'équipe plateforme (six personnes), feuille "
                    "de route technique, relation avec les clients clés."
                ),
            },
            {
                "title": "Étudiant·e annotation de données",
                "city": "Lausanne",
                "country": "CH",
                "contract": "student",
                "remote": "remote",
                "workload_min": 20,
                "workload_max": 40,
                "salary_min": 1500,
                "salary_max": 2000,
                "salary_period": "month",
                "experience_years": None,
                "status": "closed",
                "days_ago": 60,
                "description": (
                    "Campagne terminée. Annotation de documents pour l'entraînement d'un "
                    "modèle de classification, en télétravail, horaires libres."
                ),
            },
        ],
    },
    {
        "email": "employeur3@example.com",
        "first_name": "Julien",
        "last_name": "Perrin",
        "phone": "+33 4 00 00 00 03",
        "address": "Cours Lafayette 112",
        "postal_code": "69003",
        "city": "Lyon",
        "country": "FR",
        "company_name": "Ostrelia SAS",
        "company_address": "Cours Lafayette 112",
        "company_postal_code": "69003",
        "company_city": "Lyon",
        "company_country": "FR",
        "company_phone": "+33 4 00 00 00 30",
        "logo": ("OS", "#6b46c1"),
        # The currency of the salaries of its offers (CHF when not given)
        "currency": "EUR",
        "offers": [
            {
                "title": "Développeur·euse front-end Vue.js",
                "city": "Lyon",
                "country": "FR",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 42000,
                "salary_max": 50000,
                "salary_period": "year",
                "experience_years": 3,
                "status": "published",
                "days_ago": 3,
                "description": (
                    "Agence de vingt-cinq personnes à Lyon Part-Dieu, nous réalisons des "
                    "applications web pour des PME et des collectivités.\n\n"
                    "Vous développez les interfaces en Vue 3 et TypeScript, en binôme "
                    "avec un·e designer, et vous veillez à l'accessibilité. Trois jours de "
                    "télétravail par semaine."
                ),
            },
            {
                "title": "Développeur·euse Python Django",
                "city": "Lyon",
                "country": "FR",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 40000,
                "salary_max": 48000,
                "salary_period": "year",
                "experience_years": 2,
                "status": "published",
                "days_ago": 6,
                "description": (
                    "Développement des API et des back-offices de nos clients en Django "
                    "et Django REST Framework, tests, mise en production sur nos "
                    "serveurs.\n\n"
                    "Deux ans d'expérience Django minimum."
                ),
            },
            {
                "title": "Chef·fe de projet technique",
                "city": "Lyon",
                "country": "FR",
                "contract": "permanent",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 48000,
                "salary_max": 58000,
                "salary_period": "year",
                "experience_years": 5,
                "status": "published",
                "days_ago": 10,
                "description": (
                    "Vous pilotez trois à quatre projets web en parallèle : cadrage avec "
                    "le client, planification, suivi de l'équipe, recette.\n\n"
                    "Passé de développeur·euse indispensable pour dialoguer avec l'équipe "
                    "technique."
                ),
            },
            {
                "title": "Développeur·euse Java Spring",
                "city": "Annecy",
                "country": "FR",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 38000,
                "salary_max": 46000,
                "salary_period": "year",
                "experience_years": 2,
                "status": "published",
                "days_ago": 14,
                "description": (
                    "Pour notre antenne d'Annecy, développement de services Spring Boot "
                    "pour un client du secteur de l'énergie.\n\n"
                    "Possible depuis Genève : nombreux frontaliers dans l'équipe."
                ),
            },
            {
                "title": "Alternant·e développement web",
                "city": "Lyon",
                "country": "FR",
                "contract": "student",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": None,
                "salary_max": None,
                "salary_period": "month",
                "experience_years": None,
                "status": "published",
                "days_ago": 19,
                "description": (
                    "Contrat d'alternance de deux ans en Master informatique : vous "
                    "rejoignez une équipe de développement et participez aux projets "
                    "clients dès le premier mois.\n\n"
                    "Rémunération selon la grille légale de l'alternance."
                ),
            },
            {
                "title": "Ingénieur·e QA",
                "city": "Lyon",
                "country": "FR",
                "contract": "fixed_term",
                "remote": "remote",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 36000,
                "salary_max": 42000,
                "salary_period": "year",
                "experience_years": 2,
                "status": "published",
                "days_ago": 24,
                "description": (
                    "CDD de douze mois pour outiller les tests de nos projets : stratégie "
                    "de test, automatisation avec Playwright, intégration continue.\n\n"
                    "Télétravail complet possible depuis la France."
                ),
            },
            {
                "title": "Développeur·euse WordPress",
                "city": "Lyon",
                "country": "FR",
                "contract": "permanent",
                "remote": "on_site",
                "workload_min": 80,
                "workload_max": 100,
                "salary_min": 32000,
                "salary_max": 38000,
                "salary_period": "year",
                "experience_years": 1,
                "status": "published",
                "days_ago": 31,
                "description": (
                    "Réalisation de sites vitrines et de boutiques en ligne pour nos "
                    "clients PME : thèmes sur mesure, extensions, maintenance.\n\n"
                    "Poste ouvert à 80 ou 100 %."
                ),
            },
            {
                "title": "Stage UX / UI design",
                "city": "Lyon",
                "country": "FR",
                "contract": "internship",
                "remote": "on_site",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 1200,
                "salary_max": None,
                "salary_period": "month",
                "experience_years": None,
                "status": "published",
                "days_ago": 45,
                "description": (
                    "Stage de fin d'études de six mois aux côtés de notre designer : "
                    "ateliers avec les clients, maquettes Figma, tests utilisateurs.\n\n"
                    "Portfolio demandé avec la candidature."
                ),
            },
            {
                "title": "Lead developer",
                "city": "Lyon",
                "country": "FR",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 55000,
                "salary_max": 65000,
                "salary_period": "year",
                "experience_years": 7,
                "status": "draft",
                "days_ago": None,
                "description": (
                    "Brouillon. Référent·e technique de l'agence : choix d'architecture, "
                    "revue de code, accompagnement des équipes."
                ),
            },
            {
                "title": "Développeur·euse Angular",
                "city": "Lyon",
                "country": "FR",
                "contract": "permanent",
                "remote": "hybrid",
                "workload_min": 100,
                "workload_max": 100,
                "salary_min": 40000,
                "salary_max": 46000,
                "salary_period": "year",
                "experience_years": 3,
                "status": "closed",
                "days_ago": 50,
                "description": (
                    "Poste pourvu. Développement front-end Angular pour un client du "
                    "secteur bancaire."
                ),
            },
        ],
    },
]

# ── The applications ──────────────────────────────────────────────────
# Who applied to which offer (the employer and the title name it), how
# many days ago, with a cover letter or not, with which documents of their
# profile, and the states it went through since: (state, days ago). An
# application is never older than the publication of its offer.
#
# Its conversation, when it was taken up: (who, days ago, time, text), who
# being "employer" or "candidate", oldest first; the first message comes
# with the move in progress, the last one of a decided application with
# the decision, as the API writes them. The last "unread" messages are left
# unread by the other participant, the others read an hour after they were
# sent.
#
# Its news (decisions of 22.10.2026): every line of its history is seen
# when it happened, except the last one of an application marked "unseen":
# still news for its recipient, the employer for an application just
# received, the candidate for a move.
#
# Its appointments (decisions of 22.10.2026): proposed (days ago, time),
# starting (days ago, time; negative for days to come), their length,
# place and note, their state, the answer and when it came. Each is seen by
# its recipient an hour after its last change, except those marked
# "unseen": a proposal for the candidate, an answer for the employer.

APPLICATIONS = [
    {
        "candidate": "candidat1@example.com",
        "employer": "employeur1@example.com",
        "offer": "Développeur·euse Java Spring senior",
        "days_ago": 1,
        "letter": True,
        "documents": ["Diplome_HEG.pdf"],
        "moves": [],
        "unseen": True,
    },
    {
        "candidate": "candidat1@example.com",
        "employer": "employeur1@example.com",
        "offer": "Ingénieur·e DevOps",
        "days_ago": 8,
        "letter": True,
        "documents": ["Diplome_HEG.pdf", "Certificat_travail.pdf"],
        "moves": [("in_progress", 6), ("accepted", 2)],
        "messages": [
            (
                "employer",
                6,
                "09:00",
                "Bonjour Madame Martin, merci pour votre candidature au poste d'ingénieure "
                "DevOps. Je vous propose un entretien dans nos locaux, à la Rue de Lausanne 45 : "
                "vous trouverez le rendez-vous ci-dessous.",
            ),
            (
                "candidate",
                6,
                "09:45",
                "Bonjour Monsieur Rochat, avec plaisir : je l'accepte tout de suite.",
            ),
            (
                "employer",
                4,
                "17:30",
                "Merci pour l'entretien, l'équipe a beaucoup apprécié. Pourriez-vous "
                "nous indiquer deux références ?",
            ),
            (
                "candidate",
                3,
                "08:50",
                "Bien sûr : mes deux anciens responsables sont d'accord d'être contactés. Je vous"
                " transmets leurs coordonnées par e-mail aujourd'hui.",
            ),
            (
                "employer",
                2,
                "15:00",
                "Bonne nouvelle : nous retenons votre candidature ! Notre service des ressources "
                "humaines vous appelle cette semaine pour le contrat. D'ici là, vous pouvez me "
                "joindre au +41 22 000 00 10.",
            ),
        ],
        "unread": 0,
        "appointments": [
            {
                # The interview of that Tuesday, past
                "created": (6, "09:02"),
                "starts": (4, "10:00"),
                "duration": 60,
                "place": "Quorvane SA, Rue de Lausanne 45, 1201 Genève",
                "note": "Entretien avec moi et la responsable de l'équipe plateforme.",
                "status": "accepted",
                "response": "Avec plaisir, je serai là.",
                "answered": (6, "09:46"),
            },
        ],
    },
    {
        # The liveliest conversation, open, its last two messages unread by
        # the candidate
        "candidate": "candidat1@example.com",
        "employer": "employeur1@example.com",
        "offer": "Développeur·euse Full Stack Vue / Django",
        "days_ago": 5,
        "letter": True,
        "documents": ["Diplome_HEG.pdf"],
        "moves": [("in_progress", 4)],
        "messages": [
            (
                "employer",
                4,
                "09:12",
                "Bonjour Madame Martin, merci pour votre candidature. Votre expérience en Vue.js "
                "et en Java nous intéresse beaucoup. Seriez-vous disponible pour un premier "
                "échange de trente minutes en visioconférence cette semaine ?",
            ),
            (
                "candidate",
                4,
                "11:40",
                "Bonjour Monsieur Rochat, merci pour votre retour. Avec plaisir : je suis "
                "disponible en début d'après-midi, la plupart des jours.",
            ),
            (
                "employer",
                3,
                "08:55",
                "Parfait, je vous propose un créneau ci-dessous et vous envoie le lien la "
                "veille. Sur quel projet Vue avez-vous travaillé en dernier ?",
            ),
            (
                "candidate",
                3,
                "10:05",
                "Une application interne de suivi des demandes, en Vue 3 et TypeScript, avec une "
                "API Django REST. J'y ai repris l'authentification et la pagination des listes. "
                "Je peux vous montrer le code.",
            ),
            (
                "employer",
                2,
                "16:20",
                "Merci pour cet échange très agréable. L'équipe aimerait vous proposer un "
                "exercice technique d'une heure, à faire chez vous : une petite API Django et sa "
                "page Vue. Cela vous convient-il ?",
            ),
            ("candidate", 2, "17:45", "Oui, très volontiers. Puis-je le faire ce week-end ?"),
            (
                "employer",
                1,
                "08:30",
                "Bien sûr, prenez le temps qu'il vous faut. Je vous envoie l'énoncé ici très "
                "prochainement.",
            ),
            (
                "employer",
                1,
                "18:05",
                "Petite précision : l'exercice se fait en Python 3.13 et Vue 3, sans bibliothèque"
                " de composants.",
            ),
        ],
        "unread": 2,
        "appointments": [
            {
                # The first video call, past
                "created": (3, "09:00"),
                "starts": (2, "14:30"),
                "duration": 30,
                "place": "Visioconférence, lien envoyé la veille",
                "note": "Premier échange : votre parcours et le poste.",
                "status": "accepted",
                "response": "Parfait, à bientôt en visio.",
                "answered": (3, "09:30"),
            },
            {
                # The meeting with the team, to come, not answered yet:
                # news for the candidate
                "created": (1, "18:10"),
                "starts": (-4, "10:00"),
                "duration": 90,
                "place": "Quorvane SA, Rue de Lausanne 45, 1201 Genève",
                "note": (
                    "Rencontre avec l'équipe et retour sur votre exercice technique. Prévoyez "
                    "votre ordinateur portable."
                ),
                "status": "pending",
                "unseen": True,
            },
        ],
    },
    {
        # Open, the last two messages of the candidate unread by the employer
        "candidate": "candidat1@example.com",
        "employer": "employeur1@example.com",
        "offer": "Testeur·euse QA automatisation",
        "days_ago": 10,
        "letter": False,
        "documents": [],
        "moves": [("in_progress", 8)],
        "messages": [
            (
                "employer",
                8,
                "14:00",
                "Bonjour, votre profil nous intéresse aussi pour ce poste : l'équipe écrit ses "
                "tests de bout en bout avec Playwright. En avez-vous déjà écrit ?",
            ),
            (
                "candidate",
                8,
                "18:22",
                "Bonjour, oui : une quarantaine de parcours Playwright sur l'application de suivi"
                " dont je parle dans mon CV.",
            ),
            (
                "employer",
                6,
                "10:15",
                "Très bien. Quelles seraient vos prétentions salariales pour ce poste à 80 % ?",
            ),
            (
                "candidate",
                3,
                "09:40",
                "Pour un 80 %, je me situe autour de 6 800 CHF par mois. Je peux commencer dès le"
                " 1er décembre.",
            ),
            (
                "candidate",
                1,
                "12:10",
                "Bonjour, je me permets de revenir vers vous : avez-vous pu avancer sur ma "
                "candidature ?",
            ),
        ],
        "unread": 2,
        "appointments": [
            {
                # Declined: the candidate is not free at that time
                "created": (4, "16:00"),
                "starts": (-6, "09:30"),
                "duration": 45,
                "place": "Par téléphone, je vous appelle",
                "status": "declined",
                "response": (
                    "Merci pour la proposition. Je suis en formation ce matin-là ; l'après-midi du "
                    "même jour me conviendrait très bien."
                ),
                "answered": (3, "09:30"),
            },
            {
                # Proposed again for the afternoon, accepted: news for the employer
                "created": (3, "11:00"),
                "starts": (-6, "16:00"),
                "duration": 45,
                "place": "Par téléphone, je vous appelle",
                "note": "Échange avec le responsable QA sur vos parcours Playwright.",
                "status": "accepted",
                "response": (
                    "16 h me convient très bien, merci. Je reste joignable au numéro de mon "
                    "profil."
                ),
                "answered": (1, "12:05"),
                "unseen": True,
            },
        ],
    },
    {
        # Taken up, nobody has written yet: the conversation is open, empty
        "candidate": "candidat1@example.com",
        "employer": "employeur1@example.com",
        "offer": "Développeur·euse mobile Android",
        "days_ago": 4,
        "letter": True,
        "documents": ["Certificat_travail.pdf"],
        "moves": [("in_progress", 1)],
        "unseen": True,
    },
    {
        # Rejected with a last message: closed, read only
        "candidate": "candidat1@example.com",
        "employer": "employeur1@example.com",
        "offer": "Administrateur·trice systèmes Linux",
        "days_ago": 18,
        "letter": False,
        "documents": [],
        "moves": [("in_progress", 15), ("rejected", 9)],
        "messages": [
            (
                "employer",
                15,
                "10:30",
                "Bonjour, merci pour votre intérêt. Le poste comprend des astreintes le week-end "
                ": est-ce compatible avec votre situation ?",
            ),
            (
                "candidate",
                14,
                "19:05",
                "Bonjour, des astreintes ponctuelles oui, mais pas tous les week-ends.",
            ),
            (
                "employer",
                9,
                "11:00",
                "Merci pour votre franchise. Nous avons retenu un profil davantage orienté "
                "systèmes, disponible pour toutes les astreintes. Votre candidature au poste Full"
                " Stack reste bien sûr ouverte de notre côté.",
            ),
        ],
        "unread": 0,
        "appointments": [
            {
                # Accepted, then cancelled by the employer before the decision
                "created": (14, "19:30"),
                "starts": (11, "14:00"),
                "duration": 60,
                "place": "Quorvane SA, Rue de Lausanne 45, 1201 Genève",
                "status": "cancelled",
                "response": (
                    "Je dois malheureusement annuler notre rendez-vous : nous avançons "
                    "avec un autre profil. Je vous écris plus en détail rapidement."
                ),
                "answered": (12, "08:30"),
            },
        ],
    },
    {
        "candidate": "candidat1@example.com",
        "employer": "employeur3@example.com",
        "offer": "Développeur·euse Java Spring",
        "days_ago": 13,
        "letter": False,
        "documents": [],
        "moves": [("rejected", 9)],
    },
    {
        "candidate": "candidat2@example.com",
        "employer": "employeur1@example.com",
        "offer": "Développeur·euse Java Spring senior",
        "days_ago": 2,
        "letter": True,
        "documents": ["Certificat_CFC.pdf"],
        "moves": [],
        "unseen": True,
    },
    {
        "candidate": "candidat2@example.com",
        "employer": "employeur2@example.com",
        "offer": "Ingénieur·e cloud AWS",
        "days_ago": 3,
        "letter": False,
        "documents": [],
        "moves": [("in_progress", 1)],
        "messages": [
            (
                "employer",
                1,
                "10:20",
                "Bonjour, êtes-vous certifié AWS ? Si oui, laquelle de leurs certifications avez-"
                "vous ?",
            ),
        ],
        "unread": 1,
    },
    {
        "candidate": "candidat2@example.com",
        "employer": "employeur1@example.com",
        "offer": "Administrateur·trice systèmes Linux",
        "days_ago": 20,
        "letter": True,
        "documents": ["Certificat_CFC.pdf"],
        "moves": [("in_progress", 16), ("rejected", 12)],
        "messages": [
            (
                "employer",
                16,
                "09:30",
                "Bonjour, pouvez-vous me préciser votre expérience avec Ansible ?",
            ),
            ("candidate", 15, "20:10", "Bonjour, deux ans, sur une vingtaine de serveurs Debian."),
            (
                "employer",
                12,
                "16:45",
                "Merci pour votre candidature. Nous avons retenu un profil plus expérimenté en "
                "virtualisation. Bonne continuation !",
            ),
        ],
        "unread": 1,
    },
    {
        "candidate": "candidat3@example.com",
        "employer": "employeur3@example.com",
        "offer": "Développeur·euse Python Django",
        "days_ago": 4,
        "letter": True,
        "documents": ["Attestation_stage.pdf"],
        "moves": [],
    },
    {
        "candidate": "candidat3@example.com",
        "employer": "employeur2@example.com",
        "offer": "Data scientist junior",
        "days_ago": 10,
        "letter": False,
        "documents": ["Attestation_stage.pdf"],
        "moves": [("in_progress", 7)],
    },
    {
        # An application accepted on an offer closed since
        "candidate": "candidat3@example.com",
        "employer": "employeur1@example.com",
        "offer": "Développeur·euse PHP Symfony",
        "days_ago": 52,
        "letter": True,
        "documents": [],
        "moves": [("in_progress", 48), ("accepted", 45)],
        "messages": [
            (
                "employer",
                48,
                "11:00",
                "Bonjour, votre candidature nous intéresse. Quand pourriez-vous commencer ?",
            ),
            ("candidate", 47, "08:15", "Bonjour, dès le début du mois prochain."),
            (
                "employer",
                45,
                "14:30",
                "Parfait : bienvenue chez Quorvane ! Le contrat part demain par courrier.",
            ),
        ],
        "unread": 0,
    },
]

# ── The favorites ─────────────────────────────────────────────────────
# Who put which offer aside (the employer and the title name it), how many
# days ago. One is on an offer closed since: a favorite stays until the
# candidate takes it back.

FAVORITES = [
    ("candidat1@example.com", "employeur1@example.com", "Développeur·euse Full Stack Vue / Django", 4),
    ("candidat1@example.com", "employeur2@example.com", "Data engineer Python", 1),
    ("candidat1@example.com", "employeur3@example.com", "Développeur·euse front-end Vue.js", 2),
    ("candidat1@example.com", "employeur1@example.com", "Développeur·euse PHP Symfony", 53),
    ("candidat2@example.com", "employeur2@example.com", "Ingénieur·e cloud AWS", 3),
    ("candidat2@example.com", "employeur1@example.com", "Administrateur·trice systèmes Linux", 21),
    ("candidat3@example.com", "employeur2@example.com", "Data scientist junior", 10),
    ("candidat3@example.com", "employeur3@example.com", "Développeur·euse Python Django", 5),
]

# ── The reviews ───────────────────────────────────────────────────────
# What five of the accounts think of the platform: the overall rating, the
# four detailed scores in the order of CRITERIA, the comment, how many days
# ago it was written and, if so, last changed. Inès Dupont has none. Every
# remark names something the site does, or does not do yet (decisions of
# 23.10.2026); no label "demo": the header of the site already says it is
# one (condition: if that mention leaves the header, these reviews go or
# get a mark).

REVIEWS = [
    {
        "email": "candidat1@example.com",
        "scores": (5, 5, 5, 4, 5),
        "comment": (
            "J'ai trouvé deux offres qui correspondaient à mon profil en quelques minutes, "
            "grâce aux filtres par ville et par contrat. Postuler avec le CV déjà enregistré "
            "dans mon profil est très pratique. J'aimerais être prévenue quand une nouvelle "
            "offre correspond à mes critères, sans devoir relancer la recherche."
        ),
        "written": 12,
    },
    {
        "email": "candidat2@example.com",
        "scores": (4, 4, 4, 4, 3),
        "comment": (
            "Interface claire et rapide. Voir où en est chacune de mes candidatures m'évite "
            "de relancer les recruteurs. Pour les rendez-vous, j'aurais aimé pouvoir proposer "
            "un autre créneau plutôt que seulement accepter ou refuser."
        ),
        "written": 20,
    },
    {
        "email": "employeur1@example.com",
        "scores": (4, 5, 4, 5, 4),
        "comment": (
            "Publier une offre prend cinq minutes, et je garde mes brouillons jusqu'à ce que "
            "le texte soit prêt. Tout l'échange avec un candidat reste au même endroit : sa "
            "candidature, nos messages et le rendez-vous. Il me manque la possibilité de "
            "joindre un document à un message, comme une fiche de poste détaillée."
        ),
        "written": 9,
        "changed": 2,
    },
    {
        "email": "employeur2@example.com",
        "scores": (5, 5, 4, 5, 5),
        "comment": (
            "Le calendrier me montre d'un coup d'œil les entretiens de la semaine, et "
            "j'ajoute chacun à mon agenda avec le fichier proposé. Nos candidats reçoivent "
            "une réponse plus vite qu'avec nos anciens échanges par e-mail."
        ),
        "written": 6,
    },
    {
        "email": "employeur3@example.com",
        "scores": (3, 4, 3, 3, 3),
        "comment": (
            "Simple à prendre en main. Pour l'instant, nos offres en France reçoivent peu de "
            "candidatures ; je reviendrai sur cette note quand nous aurons plus de recul."
        ),
        "written": 3,
    },
]

EMAILS = [person["email"] for person in CANDIDATES + EMPLOYERS]


# ── The files ─────────────────────────────────────────────────────────


def pdf(title, lines):
    """A one-page PDF with a title and a few lines of text, as bytes.

    Written by hand: a PDF is a text file made of numbered objects (the
    catalog, the pages, one page, its content, a font), an index of their
    positions (xref) and a trailer. Helvetica is one of the fonts every
    viewer has; WinAnsi is its encoding with the accented letters."""

    def escaped(text):
        # In a PDF string, backslash and parentheses are escaped; the text
        # is encoded in WinAnsi (cp1252), a character it lacks becomes "?"
        text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return text.encode("cp1252", errors="replace")

    content = [b"BT", b"/F1 18 Tf", b"72 760 Td", b"(" + escaped(title) + b") Tj"]
    content += [b"/F1 12 Tf", b"0 -30 Td"]
    for line in lines:
        content += [b"(" + escaped(line) + b") Tj", b"0 -18 Td"]
    content.append(b"ET")
    stream = b"\n".join(content)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R"
        b" /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1)
    out += b"startxref\n%d\n%%%%EOF\n" % xref
    return bytes(out)


def pdf_file(name, title, lines):
    """The same, as a file Django stores under the path of a model field."""
    return ContentFile(pdf(title, lines), name=name)


# The times of the messages are those of Geneva: the server counts in UTC
# (TIME_ZONE), the pages show the time of the browser
GENEVA = ZoneInfo("Europe/Zurich")


def at(days_ago, time):
    """The time "HH:MM" in Geneva of the day days_ago days before today,
    or after it when days_ago is negative: the start of an appointment.
    Always on a working day, the seed being made again every night: a
    Saturday or a Sunday moves back to the Friday for a day past, on to the
    Monday for a day to come."""
    hour, minute = (int(part) for part in time.split(":"))
    day = timezone.localtime(timezone=GENEVA) - timedelta(days=days_ago)
    while day.weekday() >= 5:
        day += timedelta(days=1 if days_ago < 0 else -1)
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def moment(days_ago, time):
    """The time "HH:MM" in Geneva of the day days_ago days before today,
    never later than a few minutes ago."""
    hour, minute = (int(part) for part in time.split(":"))
    day = timezone.localtime(timezone=GENEVA) - timedelta(days=days_ago)
    when = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return min(when, timezone.now() - timedelta(minutes=5))


def logo(initials, colour):
    """A square PNG logo, as bytes: the initials of the company in white on
    a rounded square of its colour. Pillow's own font, so that nothing has
    to be installed; the text is measured, then placed in the middle."""
    side = 256
    image = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, side - 1, side - 1), radius=48, fill=colour)
    font = ImageFont.load_default(size=112)
    left, top, right, bottom = draw.textbbox((0, 0), initials, font=font)
    position = ((side - (right - left)) / 2 - left, (side - (bottom - top)) / 2 - top)
    draw.text(position, initials, fill="white", font=font)
    buffer = BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


def logo_file(initials, colour):
    """The same, as a file Django stores under the path of the logo field."""
    return ContentFile(logo(initials, colour), name="logo.png")


class Command(BaseCommand):
    help = (
        "Create six test accounts (three candidates, three employers), their job offers, "
        "applications, favorites, conversations, appointments and reviews."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help=(
                "Delete the six test accounts first, with their profiles, offers, applications, "
                "favorites, messages, appointments and reviews."
            ),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run with DEBUG off, on a server: the accounts then get no usable password.",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "DEBUG is off: this is a server; run with --force to replace the demo data."
            )

        # The documents made for the candidates, by address and name, for
        # the applications that join them
        self.documents = {}
        existing = User.objects.filter(email__in=EMAILS)
        if existing.exists():
            if not options["reset"]:
                raise CommandError(
                    "The test accounts already exist: run again with --reset to replace them."
                )

        # All or nothing, the deletion included: a failure half-way brings the
        # previous rows back instead of leaving the demo empty until the next
        # night (decision of 28.10.2026). The files the signals removed with
        # the old accounts do not come back: their pages show no document
        # until the next run
        with transaction.atomic():
            if existing.exists():
                # The profiles, the offers, the applications, the favorites,
                # the messages, the appointments, the reviews, the addresses of
                # allauth and the files (signals) go with the users
                count, _ = existing.delete()
                self.stdout.write(f"Deleted the previous test data ({count} rows).")
            for person in CANDIDATES:
                self.candidate(person)
            offers = sum(self.employer(person) for person in EMPLOYERS)
            for spec in APPLICATIONS:
                self.application(spec)
            for candidate, employer, title, days_ago in FAVORITES:
                self.favorite(candidate, employer, title, days_ago)
            for spec in REVIEWS:
                self.review(spec)

        messages = sum(len(spec.get("messages", [])) for spec in APPLICATIONS)
        appointments = sum(len(spec.get("appointments", [])) for spec in APPLICATIONS)
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(EMAILS)} accounts, {offers} offers, {len(APPLICATIONS)} applications, "
                f"{len(FAVORITES)} favorites, {messages} messages, {appointments} appointments "
                f"and {len(REVIEWS)} reviews."
            )
        )
        # The addresses are listed in development only: on a server, the
        # output goes to the journal of the nightly timer, and the logs hold
        # no e-mail address (fictitious ones included)
        if settings.DEBUG:
            self.stdout.write(f"Password of every account: {PASSWORD}")
            for email in EMAILS:
                self.stdout.write(f"  {email}")
        else:
            self.stdout.write("No usable password: the demo accounts open from the login page.")

    # ── The rows ──────────────────────────────────────────────────────

    def user(self, person, role):
        """The account, with its address verified (allauth lets nobody log
        in before the address is confirmed) and the terms accepted, as a
        sign-up would have left it; marked as a demo account when it is one.
        The password: the known one in development, an unusable one
        elsewhere (None)."""
        user = User.objects.create_user(
            email=person["email"],
            password=PASSWORD if settings.DEBUG else None,
            role=role,
            is_demo=person.get("demo", False),
            first_name=person["first_name"],
            last_name=person["last_name"],
            terms_accepted_at=timezone.now(),
        )
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        return user

    def contact(self, person):
        """The contact details of a person, as the profile models name them."""
        return {key: person[key] for key in ("phone", "address", "postal_code", "city", "country")}

    def candidate(self, person):
        """The account, the profile with its CV, and the documents."""
        user = self.user(person, User.Role.CANDIDATE)
        name = f"{person['first_name']} {person['last_name']}"
        profile = CandidateProfile.objects.create(
            user=user,
            cv=pdf_file(f"CV_{person['last_name']}.pdf", name, person["cv"]),
            **self.contact(person),
        )
        for document in person["documents"]:
            title = document.removesuffix(".pdf").replace("_", " ")
            lines = [f"Document de {name}, pour la démonstration."]
            self.documents[person["email"], document] = CandidateDocument.objects.create(
                candidate=profile, file=pdf_file(document, title, lines)
            )

    def employer(self, person):
        """The account, the profile with its company and its logo, the
        offers; returns how many offers were made."""
        user = self.user(person, User.Role.EMPLOYER)
        company = {key: person[key] for key in person if key.startswith("company_")}
        profile = EmployerProfile.objects.create(
            user=user, logo=logo_file(*person["logo"]), **self.contact(person), **company
        )
        for offer in person["offers"]:
            self.offer(profile, offer, person.get("currency", JobOffer.Currency.CHF))
        return len(person["offers"])

    def offer(self, profile, fields, currency):
        """One offer, in the currency of its employer, dated days_ago days
        before today when it was published (a closed offer was published
        once too)."""
        fields = dict(fields)
        status = fields.pop("status")
        days_ago = fields.pop("days_ago")
        offer = JobOffer.objects.create(
            employer=profile, status=JobOffer.Status.DRAFT, currency=currency, **fields
        )
        if status != JobOffer.Status.DRAFT:
            # Written straight to the row: save() would stamp today
            published_at = timezone.now() - timedelta(days=days_ago)
            JobOffer.objects.filter(pk=offer.pk).update(status=status, published_at=published_at)

    def application(self, spec):
        """One application, its files copied from the profile like the API
        does (the letter written here), dated days_ago days before today,
        then moved through its states, each dated too, its news seen but
        the last one when it is to stay unseen, then its conversation, if
        any."""
        profile = CandidateProfile.objects.get(user__email=spec["candidate"])
        offer = JobOffer.objects.get(employer__user__email=spec["employer"], title=spec["offer"])
        name = profile.user.get_full_name()
        letter = ""
        if spec["letter"]:
            lines = [
                "Madame, Monsieur,",
                f"Votre offre « {offer.title} » correspond à ce que je cherche.",
                "Vous trouverez mon CV ci-joint ; je reste à votre disposition",
                "pour un entretien.",
                name,
            ]
            letter = pdf_file("Lettre_de_motivation.pdf", "Lettre de motivation", lines)
        application = JobApplication.objects.create(
            offer=offer, candidate=profile, cv=copy_of(profile.cv), cover_letter=letter
        )
        for document in spec["documents"]:
            source = self.documents[spec["candidate"], document]
            Attachment.objects.create(application=application, file=copy_of(source.file))
        # The dates, written straight to the rows: the model stamps today.
        # Then read back: save() below writes every field of the instance,
        # and the instance still holds the dates of its creation
        now = timezone.now()
        sent = now - timedelta(days=spec["days_ago"])
        JobApplication.objects.filter(pk=application.pk).update(created_at=sent, updated_at=sent)
        application.history.update(changed_at=sent)
        application.refresh_from_db()
        for status, days_ago in spec["moves"]:
            application.status = status
            application.save()
            when = now - timedelta(days=days_ago)
            JobApplication.objects.filter(pk=application.pk).update(updated_at=when)
            application.history.filter(status=status).update(changed_at=when)
        # The news: seen when they happened, the last one left unseen when
        # the spec says so
        application.history.update(seen_at=F("changed_at"))
        if spec.get("unseen"):
            application.history.filter(pk=application.history.last().pk).update(seen_at=None)
        self.conversation(application, spec.get("messages", []), spec.get("unread", 0))
        for appointment in spec.get("appointments", []):
            self.appointment(application, appointment)

    def conversation(self, application, messages, unread):
        """The messages of an application, dated, read an hour after they
        were sent except the last "unread" ones."""
        now = timezone.now()
        authors = {
            "employer": application.offer.employer.user,
            "candidate": application.candidate.user,
        }
        for index, (who, days_ago, time, body) in enumerate(messages):
            message = Message.objects.create(
                application=application, author=authors[who], body=body
            )
            sent = moment(days_ago, time)
            read = None if index >= len(messages) - unread else min(sent + timedelta(hours=1), now)
            # Written straight to the row: the model stamps today
            Message.objects.filter(pk=message.pk).update(sent_at=sent, read_at=read)

    def appointment(self, application, spec):
        """One appointment of an application, dated, seen by its recipient an
        hour after its last change unless it is to stay unseen."""
        now = timezone.now()
        created = moment(*spec["created"])
        answered = moment(*spec["answered"]) if spec.get("answered") else None
        seen = None if spec.get("unseen") else min((answered or created) + timedelta(hours=1), now)
        appointment = Appointment.objects.create(
            application=application,
            starts_at=at(*spec["starts"]),
            duration=spec["duration"],
            place=spec["place"],
            note=spec.get("note", ""),
            status=spec["status"],
            response=spec.get("response", ""),
            answered_at=answered,
            seen_at=seen,
        )
        # Written straight to the row: the model stamps today
        Appointment.objects.filter(pk=appointment.pk).update(created_at=created)

    def favorite(self, candidate, employer, title, days_ago):
        """One offer put aside by a candidate, days_ago days before today."""
        profile = CandidateProfile.objects.get(user__email=candidate)
        offer = JobOffer.objects.get(employer__user__email=employer, title=title)
        favorite = Favorite.objects.create(candidate=profile, offer=offer)
        # Written straight to the row: the model stamps today
        when = timezone.now() - timedelta(days=days_ago)
        Favorite.objects.filter(pk=favorite.pk).update(created_at=when)

    def review(self, spec):
        """The review of one account, dated days before today: written, and
        last changed if the spec says so."""
        rating, *details = spec["scores"]
        review = Review.objects.create(
            user=User.objects.get(email=spec["email"]),
            rating=rating,
            comment=spec["comment"],
            **dict(zip(CRITERIA, details, strict=True)),
        )
        now = timezone.now()
        written = now - timedelta(days=spec["written"])
        changed = now - timedelta(days=spec.get("changed", spec["written"]))
        # Written straight to the row: the model stamps today
        Review.objects.filter(pk=review.pk).update(created_at=written, updated_at=changed)
