from neo4j import GraphDatabase
from app.core.config import settings
from typing import List, Dict, Any

class GraphStoreService:
    def __init__(self):
        self._driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self._driver.close()

    def create_concept_node(self, name: str, category: str, description: str):
        """
        Creates a concept node in Neo4j if it doesn't already exist.
        """
        query = (
            "MERGE (c:Concept {name: $name}) "
            "SET c.category = $category, c.description = $description, c.updated_at = timestamp() "
            "RETURN c"
        )
        with self._driver.session() as session:
            session.run(query, name=name, category=category, description=description)

    def create_relationship(self, source_name: str, target_name: str, relationship_type: str, confidence: float):
        """
        Creates a directed semantic edge between two concepts.
        """
        # Sanitise relationship type to avoid Cypher injection
        allowed_types = {
            "REFERENCES", "DEPENDS_ON", "INSPIRED_BY", "COMPETES_WITH", 
            "EXPLAINS", "USES", "ALTERNATIVE_TO", "CONTRADICTS", "SUPPORTS"
        }
        rel_type = relationship_type.upper().strip()
        if rel_type not in allowed_types:
            rel_type = "REFERENCES"
            
        query = (
            f"MATCH (a:Concept {{name: $source_name}}), (b:Concept {{name: $target_name}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "SET r.confidence = $confidence, r.created_at = timestamp() "
            "RETURN r"
        )
        with self._driver.session() as session:
            session.run(query, source_name=source_name, target_name=target_name, confidence=confidence)

    def query_subgraph(self, center_node: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Retrieves the neighborhood of a node for rendering graphs in frontend.
        """
        query = (
            "MATCH path = (n:Concept {name: $center_node})-[r*1..2]-(m:Concept) "
            "RETURN path LIMIT 50"
        )
        nodes = {}
        edges = []
        
        with self._driver.session() as session:
            result = session.run(query, center_node=center_node)
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    nodes[node["name"]] = {
                        "id": node["name"],
                        "category": node.get("category", "Concept"),
                        "description": node.get("description", "")
                    }
                for rel in path.relationships:
                    edges.append({
                        "source": rel.start_node["name"],
                        "target": rel.end_node["name"],
                        "type": rel.type,
                        "confidence": rel.get("confidence", 1.0)
                    })
        return {"nodes": list(nodes.values()), "edges": edges}

# Driver handles connection pooling automatically
graph_store_service = GraphStoreService()
