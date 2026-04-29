from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import get_db
from services.embedding import get_embedding
from services.vector_store import add_vector, search_vector
from auth import auth

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "lost_found_secret_key_2026"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

jwt = JWTManager(app)
app.register_blueprint(auth)


@app.route('/')
def home():
    return "Lost & Found API Running 🚀"


@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.json
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        insert_query = """
        INSERT INTO items (type, title, description, location, date, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data['type'], data['title'], data['description'],
            data['location'], data['date'], data['user_id']
        )
        cursor.execute(insert_query, values)
        db.commit()
        item_id = cursor.lastrowid

        text = f"{data['title']} {data['description']} {data['location']}"
        vector = get_embedding(text)
        add_vector(vector, item_id)

        opposite_type = 'found' if data['type'] == 'lost' else 'lost'
        cursor.execute("SELECT id FROM items WHERE type = %s", (opposite_type,))
        opposite_items = cursor.fetchall()

        raw_matches = search_vector(vector)
        opposite_ids = {item['id'] for item in opposite_items}

        filtered_matches = [
            r for r in raw_matches
            if r['item_id'] in opposite_ids and r['similarity'] >= 0.4
        ]

        saved_matches = []
        for match in filtered_matches:
            if data['type'] == 'lost':
                lost_id, found_id = item_id, match['item_id']
            else:
                lost_id, found_id = match['item_id'], item_id

            cursor.execute("""
                INSERT INTO matches (lost_item_id, found_item_id, similarity)
                VALUES (%s, %s, %s)
            """, (lost_id, found_id, match['similarity']))
            db.commit()

            saved_matches.append({
                "lost_item_id": lost_id,
                "found_item_id": found_id,
                "similarity": match['similarity']
            })

        return jsonify({
            "message": "Item added successfully",
            "item_id": item_id,
            "auto_matches": saved_matches
        })

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        db.close()


@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query_text = data['query']

    query_vector = get_embedding(query_text)
    results = search_vector(query_vector)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        final_results = []
        for r in results:
            cursor.execute("SELECT * FROM items WHERE id = %s", (r['item_id'],))
            item = cursor.fetchone()
            if item:
                item['similarity'] = r['similarity']
                final_results.append(item)

        return jsonify({"query": query_text, "results": final_results})

    finally:
        cursor.close()
        db.close()


@app.route('/matches', methods=['GET'])
def get_matches():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                m.id, m.similarity, m.status, m.created_at,
                l.title AS lost_title, l.description AS lost_description, l.location AS lost_location,
                f.title AS found_title, f.description AS found_description, f.location AS found_location
            FROM matches m
            JOIN items l ON m.lost_item_id = l.id
            JOIN items f ON m.found_item_id = f.id
            ORDER BY m.similarity DESC
        """)
        return jsonify({"matches": cursor.fetchall()})

    finally:
        cursor.close()
        db.close()


@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) as total FROM items WHERE type='lost'")
        lost = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM items WHERE type='found'")
        found = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM matches")
        matches = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM users")
        users = cursor.fetchone()['total']

        cursor.execute("""
            SELECT location, COUNT(*) as count 
            FROM items GROUP BY location ORDER BY count DESC LIMIT 5
        """)
        hotspots = cursor.fetchall()

        cursor.execute("""
            SELECT type, title, description, location, date 
            FROM items ORDER BY id DESC LIMIT 5
        """)
        recent = cursor.fetchall()

        cursor.execute("SELECT AVG(similarity) as avg_sim FROM matches")
        avg = cursor.fetchone()['avg_sim']

        return jsonify({
            "lost_count": lost,
            "found_count": found,
            "match_count": matches,
            "user_count": users,
            "hotspots": hotspots,
            "recent_items": recent,
            "avg_similarity": round(float(avg), 2) if avg else 0
        })

    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    app.run(debug=True)