# FindIt — Smart Lost & Found System

An AI-powered lost and found system built with Flask, MySQL, FAISS, and React. Uses semantic search and RAG (Retrieval-Augmented Generation) to intelligently match lost items with found ones — going far beyond simple keyword search.

---

## Features

- **Semantic Search** — Powered by Sentence Transformers. "black wallet near library" matches "dark leather purse found by VIT library" even with different wording.
- **Auto-Matching** — When a found item is reported, the system automatically checks all lost items for similarity and saves matches above a confidence threshold.
- **Vector Database** — FAISS index persisted to disk so data survives server restarts.
- **REST API** — Flask backend with clean endpoints for adding items, searching, and viewing matches.
- **React Frontend** — Clean UI with report form, semantic search, matches dashboard, and admin panel.
- **JWT Authentication** — Secure login and registration with role-based access (user / admin).
- **Admin Dashboard** — Live stats, hotspot locations, recent items, and average match confidence.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | MySQL |
| AI / Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Store | FAISS |
| Auth | JWT (flask-jwt-extended) + bcrypt |
| Frontend | React |

---

## Project Structure

```
lost_found_ai/
│
├── backend/
│   ├── app.py               # Main Flask app, all routes
│   ├── auth.py              # Register / Login / JWT
│   ├── db.py                # MySQL connection
│   ├── services/
│   │   ├── embedding.py     # Sentence Transformer wrapper
│   │   ├── vector_store.py  # FAISS index (load, save, search)
│   │   └── __init__.py
│   └── requirements.txt
│
├── data/
│   └── faiss_index/
│       ├── index.bin        # Persisted FAISS index
│       └── id_map.json      # Maps FAISS index → MySQL item ID
│
└── frontend/
    ├── src/
    │   ├── App.js           # Full React SPA
    │   └── index.css        # All styles
    └── public/
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/lost_found_ai.git
cd lost_found_ai
```

### 2. Set up Python environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 3. Set up MySQL

```sql
CREATE DATABASE lost_found;
USE lost_found;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255) NOT NULL DEFAULT '',
    role ENUM('user', 'admin') DEFAULT 'user'
);

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('lost', 'found'),
    title VARCHAR(255),
    description TEXT,
    location VARCHAR(255),
    date DATE,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lost_item_id INT,
    found_item_id INT,
    similarity FLOAT,
    status ENUM('pending', 'confirmed', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lost_item_id) REFERENCES items(id),
    FOREIGN KEY (found_item_id) REFERENCES items(id)
);
```

### 4. Configure database credentials

Edit `backend/db.py`:

```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",   # change this
        database="lost_found",
        autocommit=True
    )
```

### 5. Run the backend

```bash
cd backend
python app.py
```

API runs at `http://127.0.0.1:5000`

### 6. Run the frontend

```bash
cd frontend
npm install
npm start
```

UI runs at `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/register` | Register a new user |
| POST | `/login` | Login, returns JWT token |
| GET | `/me` | Get current user (JWT required) |
| POST | `/add_item` | Report a lost or found item |
| POST | `/search` | Semantic search across all items |
| GET | `/matches` | View all AI-generated matches |
| GET | `/admin/stats` | Admin dashboard stats |

---

## How Matching Works

1. User reports a lost or found item
2. Description is converted to a 384-dimensional embedding using `all-MiniLM-L6-v2`
3. Embedding is stored in a FAISS index (persisted to disk)
4. System searches FAISS for similar items of the opposite type
5. Matches above the similarity threshold (0.4) are saved to MySQL
6. Admin and users can view matches with confidence scores

---

## Requirements

```
flask
flask-cors
flask-jwt-extended
mysql-connector-python
sentence-transformers
faiss-cpu
numpy
bcrypt
```

---

## Future Improvements

- Email / WhatsApp notifications on match
- Image-based matching using CLIP model
- QR code tagging for physical items
- Map view showing item hotspots
- Mobile app

---

## Author

Built by Ojas Hirolikar — VIT Pune
