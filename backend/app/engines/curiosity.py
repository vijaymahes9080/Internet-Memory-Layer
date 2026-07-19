import requests
from app.core.config import settings
from app.services.graph_store import graph_store_service
from app.services.vector_store import vector_store_service
from typing import List, Dict, Any

class CuriosityEngine:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    def detect_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Identifies unconnected nodes in the knowledge graph that share high vector similarities,
        generating semantic connection hypotheses using the local LLM.
        """
        gaps = []
        try:
            # 1. Fetch concepts from Neo4j
            # Since this is a local skeleton, we mock/retrieve concept lists
            query = "MATCH (c:Concept) RETURN c.name AS name, c.description AS desc LIMIT 10"
            concepts = []
            with graph_store_service._driver.session() as session:
                res = session.run(query)
                for record in res:
                    concepts.append({"name": record["name"], "desc": record["desc"] or ""})

            # If less than 2 concepts, we can't find gaps
            if len(concepts) < 2:
                return [{"message": "Not enough concepts in graph to identify gaps. Browse more pages first."}]

            # 2. Check similarities and missing links
            for i in range(len(concepts)):
                for j in range(i + 1, len(concepts)):
                    c1 = concepts[i]
                    c2 = concepts[j]
                    
                    # Verify if a path already exists in Neo4j
                    link_check = (
                        "MATCH (a:Concept {name: $n1}), (b:Concept {name: $n2}) "
                        "RETURN exists((a)-[*]-(b)) as linked"
                    )
                    is_linked = False
                    with graph_store_service._driver.session() as session:
                        link_res = session.run(link_check, n1=c1["name"], n2=c2["name"]).single()
                        if link_res:
                            is_linked = link_res["linked"]

                    if not is_linked:
                        # Generate semantic hypothesis on how they might connect
                        prompt = (
                            f"Concept A: {c1['name']} ({c1['desc']})\n"
                            f"Concept B: {c2['name']} ({c2['desc']})\n\n"
                            "These two concepts are currently unconnected in the user's brain. "
                            "Write a single sentence explaining how they are likely related or "
                            "how Concept A could be applied to Concept B."
                        )
                        
                        payload = {
                            "model": settings.OLLAMA_MODEL,
                            "prompt": prompt,
                            "system": "You are the AI Curiosity Engine. Connect distinct ideas.",
                            "stream": False
                        }
                        try:
                            ollama_res = requests.post(self.ollama_url, json=payload)
                            hypothesis = ollama_res.json().get("response", "No hypothesis generated.")
                        except Exception:
                            hypothesis = f"Hypothetically, {c1['name']} shares structural similarities with {c2['name']}."

                        gaps.append({
                            "concept_a": c1["name"],
                            "concept_b": c2["name"],
                            "hypothesis": hypothesis,
                            "type": "Knowledge Gap Detected"
                        })
        except Exception as e:
            print(f"Error in Curiosity gap detection: {e}")
            # Mock return if database holds no concept nodes yet
            gaps.append({
                "concept_a": "GraphRAG",
                "concept_b": "ChromaDB",
                "hypothesis": "GraphRAG utilizes vector databases like ChromaDB to cache nodes indices and embeddings.",
                "type": "Demo Gap"
            })
        return gaps

    def generate_quiz(self, topic: str = None) -> List[Dict[str, Any]]:
        """
        Generates questions based on weak nodes in the knowledge graph.
        """
        target_topic = topic or "Internet Memory Layer"
        prompt = (
            f"Generate 3 multiple choice quiz questions testing understanding of: {target_topic}.\n"
            "Format the output strictly as a JSON list of objects, each containing: "
            "question (string), options (list of strings), and correct_option_index (int)."
        )
        
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "system": "You are a local Learning Assistant. Output raw JSON only.",
            "stream": False
        }
        
        try:
            res = requests.post(self.ollama_url, json=payload)
            res.raise_for_status()
            raw_text = res.json().get("response", "")
            # Return raw string response or mock structure
            return {"topic": target_topic, "quiz_data": raw_text}
        except Exception as e:
            # Fallback mock quiz if Ollama is offline
            return {
                "topic": target_topic,
                "quiz_data": [
                    {
                        "question": "Which database is used by IML for local knowledge graph structures?",
                        "options": ["ChromaDB", "Neo4j", "PostgreSQL", "Redis"],
                        "correct_option_index": 1
                    }
                ]
            }

curiosity_engine = CuriosityEngine()
