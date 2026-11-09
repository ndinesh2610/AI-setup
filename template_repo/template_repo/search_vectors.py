import psycopg
from sentence_transformers import SentenceTransformer

DATABASE_URL = "postgresql://parcel_user:parcel_dev_password@localhost:5432/parcels_db"

model = SentenceTransformer("all-MiniLM-L6-v2")

# Simulated authenticated-user claims for this exercise.
# In production, obtain these only from a validated JWT.
user_tenant = "company_a"
user_role = "employee"

question = input("Ask a question: ")
query_embedding = model.encode(question).tolist()
vector_text = "[" + ",".join(map(str, query_embedding)) + "]"

sql = """
WITH authorized_docs AS MATERIALIZED (
    SELECT id, content, embedding
    FROM documents
    WHERE tenant_id = %s
      AND %s = ANY(allowed_roles)
)
SELECT
    id,
    content,
    embedding <=> %s::vector AS distance
FROM authorized_docs
ORDER BY distance
LIMIT 3;
"""

with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
    cur.execute(
        sql,
        (user_tenant, user_role, vector_text),
    )
    results = cur.fetchall()

print("\nAuthorized search results:")  # noqa: T201

if not results:
    print("No accessible documents found.")  # noqa: T201
else:
    for doc_id, content, distance in results:
        print(f"\nID: {doc_id}")  # noqa: T201
        print(f"Document: {content}")  # noqa: T201
        print(f"Cosine distance: {distance:.4f}")  # noqa: T201
