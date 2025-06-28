from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import google.generativeai as genai
from neo4j import GraphDatabase
import os

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    context: Optional[str] = None

class RAGContext:
    def __init__(self):
        self.neo4j_uri = "bolt://neo4j:7687"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "password"
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )

    def get_relevant_context(self, query: str) -> str:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                WHERE toLower(n.text) CONTAINS toLower($query)
                RETURN n.text
                LIMIT 5
                """,
                query=query
            )
            return "\n".join([record[0] for record in result])

# Initialize Gemini
os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    try:
        # Get relevant context from Neo4j
        rag_context = RAGContext()
        context = rag_context.get_relevant_context(message.message)

        # Prepare prompt for Gemini
        prompt = f"""
        Based on the following context:
        {context}

        Please answer the question:
        {message.message}
        """

        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        return ChatResponse(
            response=str(response.text),
            context=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
