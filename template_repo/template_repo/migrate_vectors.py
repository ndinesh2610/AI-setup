import psycopg
from sentence_transformers import SentenceTransformer

# PostgreSQL connection
DATABASE_URL = "postgresql://parcel_user:parcel_dev_password@localhost:5432/parcels_db"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample policy documents
documents = [
    "Employees receive 20 days of annual leave.",
    "Leave requests must be approved by managers.",
    "Employees can work remotely two days per week.",
    "Employees must use strong passwords.",
    "Confidential company information must not be shared.",
]

# Generate embeddings
embeddings = model.encode(documents)

# Sample metadata for this exercise.
# These are demonstration values, not real authenticated users.
tenant_id = "company_a"
allowed_roles = ["employee", "manager"]
source = "company_policies"

# Connect and insert documents
with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
    for content, embedding in zip(documents, embeddings, strict=True):
        cur.execute(
            """
                INSERT INTO documents
                    (content, embedding, tenant_id, allowed_roles, source)
                VALUES
                    (%s, %s, %s, %s, %s)
                """,
            (
                content,
                embedding.tolist(),
                tenant_id,
                allowed_roles,
                source,
            ),
        )

print(f"Successfully inserted {len(documents)} documents.")  # noqa: T201
