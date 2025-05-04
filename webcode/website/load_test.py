import sqlite3, random, time
from faker import Faker

DB = "database.db"  
fake = Faker()

def seed_data():
    conn = sqlite3.connect(DB)
    cur  = conn.cursor()
    start = time.time()
    for _ in range(10000):
        title = fake.sentence(nb_words=6)
        uid   = random.randint(1, 10)
        cur.execute("INSERT INTO notes (title, user_id, likes, dislikes) VALUES (?, ?, 0, 0)", [title, uid])
    conn.commit()
    t1 = time.time()
    print(f"10k notes inserted in {t1-start:.2f}s")

    for _ in range(50000):
        note_id = random.randint(1, 10000)
        uid     = random.randint(1, 10)
        content = fake.paragraph(nb_sentences=2)
        cur.execute("INSERT INTO messages (content, user_id, note_id) VALUES (?, ?, ?)", [content, uid, note_id])
    conn.commit()
    t2 = time.time()
    print(f"50k replies inserted in {t2-t1:.2f}s")
    conn.close()

if __name__ == "__main__":
    seed_data()

#10k notes inserted in 3.45s
#50k replies inserted in 7.82s