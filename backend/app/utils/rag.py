from neo4j import GraphDatabase
import os

class RAGStore:
    def __init__(self):
        self.neo4j_uri = "bolt://neo4j:7687"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "password"
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

    def add_document(self, content: str, metadata: dict = None):
        """Add a document to the RAG store"""
        with self.driver.session() as session:
            session.run(
                """
                CREATE (d:Document {
                    text: $content,
                    created_at: datetime(),
                    metadata: $metadata
                })
                """,
                content=content,
                metadata=metadata or {}
            )

    def add_chunk(self, content: str, document_id: str, metadata: dict = None):
        """Add a chunk of text to the RAG store"""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (d:Document {id: $document_id})
                CREATE (c:Chunk {
                    text: $content,
                    created_at: datetime(),
                    metadata: $metadata
                })
                CREATE (d)-[:HAS_CHUNK]->(c)
                """,
                document_id=document_id,
                content=content,
                metadata=metadata or {}
            )

    def search(self, query: str, limit: int = 5):
        """Search for relevant chunks based on query"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Chunk)
                WHERE toLower(c.text) CONTAINS toLower($query)
                RETURN c.text, c.metadata
                LIMIT $limit
                """,
                query=query,
                limit=limit
            )
            return [{"text": record[0], "metadata": record[1]} for record in result]

# Example usage
if __name__ == "__main__":
    rag = RAGStore()
    # Example of adding a document
    rag.add_document(
        """
        Finance management is crucial for personal and business success.
        Key aspects include budgeting, expense tracking, and investment planning.
        """,
        metadata={"source": "finance_overview"}
    )
