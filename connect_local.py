import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',  # No password
    database='smf_local'
)

cursor = conn.cursor(dictionary=True)

cursor.execute("""
    SELECT m.id_msg, m.subject, m.body, m.id_member, m.id_topic, m.poster_time, t.id_board
    FROM bottleheadsmf_messages m
    JOIN bottleheadsmf_topics t ON m.id_topic = t.id_topic
    WHERE m.body IS NOT NULL AND m.body != ''
    ORDER BY m.poster_time DESC
    LIMIT 10
""")

rows = cursor.fetchall()

for row in rows:
    print(f"{row['subject']}:\n{row['body'][:200]}...\n---\n")