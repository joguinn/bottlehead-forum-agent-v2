import mysql.connector
import pandas as pd
import json
from collections import defaultdict

# === Configuration ===

# Board ID → Product mapping
BOARD_TO_PRODUCT = {
    65: "Pipette",
    66: "Subette",
    59: "Jager",
    62: "Moreplay",
    34: "BeePre",
    69: "Moreplay Upgrade",
    35: "BeeQuiet",
    52: "Stereomour",
    57: "Kaiju",
    24: "Crack",
    39: "Mainline",
    6:  "Eros",
    26: "Power Cord",
    67: "Sublime",
    8:  "SEX"
}

STAFF_IDS = {1, 35, 90}
TARGET_BOARDS = tuple(BOARD_TO_PRODUCT.keys())

# === Connect to local MySQL ===

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',  # Leave blank if you didn't set a MySQL password
    database='bottleheadsmf'
)

cursor = conn.cursor(dictionary=True)

# === Query all messages in target boards ===

cursor.execute(f"""
    SELECT m.id_msg, m.id_topic, t.id_board, m.id_member, m.body, m.poster_time
    FROM bottleheadsmf_messages m
    JOIN bottleheadsmf_topics t ON m.id_topic = t.id_topic
    WHERE t.id_board IN {TARGET_BOARDS}
    ORDER BY m.id_topic, m.poster_time
""")

rows = cursor.fetchall()

# === Group messages by topic ===

topics = defaultdict(list)
for row in rows:
    topics[row['id_topic']].append(row)

# === Extract Q&A pairs ===

qna_pairs = []

for topic_id, messages in topics.items():
    board_id = messages[0]['id_board']
    product = BOARD_TO_PRODUCT.get(board_id, "Unknown")

    # Find first non-staff question and first staff answer
    question = next((m for m in messages if m['id_member'] not in STAFF_IDS), None)
    answer = next((m for m in messages if m['id_member'] in STAFF_IDS and m['poster_time'] > question['poster_time']), None) if question else None

    if question and answer:
        qna_pairs.append({
            "topic_id": topic_id,
            "url": f"https://forum.bottlehead.com/index.php?topic={topic_id}",
            "product": product,
            "question_author": question['id_member'],
            "question": question['body'],
            "answer_author": answer['id_member'],
            "answer": answer['body']
        })

# === Save to CSV ===

csv_path = "bottlehead_qna.csv"
pd.DataFrame(qna_pairs).to_csv(csv_path, index=False)
print(f"✅ Saved {len(qna_pairs)} Q&A pairs to {csv_path}")

# === Save to JSONL ===

jsonl_path = "bottlehead_qna.jsonl"
with open(jsonl_path, "w") as f:
    for item in qna_pairs:
        f.write(json.dumps(item) + "\n")

print(f"✅ Also saved to {jsonl_path}")