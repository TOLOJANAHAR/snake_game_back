# Snake Évolution

Un jeu Snake revisité avec des power-ups, un mode labyrinthe progressif et un système d'évolution du serpent. Backend REST API en Python/FastAPI, frontend en React + GSAP (en cours).

---

## Aperçu

Le serpent évolue visuellement et en capacités selon sa taille :

| Stade | Longueur | Apparence |
|---|---|---|
| Larve | 1 – 7 segments | Vert clair |
| Serpent | 8 – 14 segments | Vert vif |
| Dragon | 15+ segments | Or/Rouge |

### Power-ups

| Item | Effet |
|---|---|
| Pomme | +1 segment, +10 pts |
| Pomme dorée | +1 segment, +30 pts, boost de vitesse 5s |
| Pomme bleue | +1 segment, +20 pts, slow-motion GSAP 5s |
| Pomme rouge | +1 segment, +25 pts, traverser 1 mur |
| Crâne | −3 segments, −15 pts (game over si trop petit) |

### Mode Labyrinthe

Des obstacles apparaissent progressivement à chaque niveau. L'algorithme BFS garantit que la grille reste toujours traversable — impossible de générer un labyrinthe sans issue.

---

## Stack technique

**Backend**
- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- Pydantic v2
- Pytest (58 tests)

**Frontend** *(en cours)*
- React 18 + Vite
- GSAP 3
- Tailwind CSS
- Zustand

---


---

## Installation (Arch Linux)

### 1. Prérequis

```bash
sudo pacman -S python python-pip sqlite
```

### 2. Cloner et préparer

```bash
git clone <url-du-repo>
cd snakegame/back
```

### 3. Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Dépendances

```bash
pip install -r requirements.txt
```

---

## Lancement

```bash
# Venv actif obligatoire
source venv/bin/activate

# Démarrer le serveur (la DB est créée automatiquement au premier lancement)
PYTHONPATH=. uvicorn main:app --reload --port 8000
```

Le fichier `snake_evolution.db` est créé automatiquement avec :
- toutes les tables (players, scores, levels)
- les 10 premiers niveaux pré-générés

**Documentation interactive** → [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Tests

```bash
# Lancer tous les tests (58 tests)
PYTHONPATH=. pytest tests/ -v

# Un fichier spécifique
PYTHONPATH=. pytest tests/test_game_logic.py -v
PYTHONPATH=. pytest tests/test_api.py -v

# Avec couverture de code
pip install pytest-cov
PYTHONPATH=. pytest tests/ --cov=app --cov-report=term-missing
```
