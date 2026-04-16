from neo4j import GraphDatabase

class Neo4jLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def insert_triples(self, triples):
        with self.driver.session() as session:
            for s, r, o in triples:
                query = f"""
                MERGE (a:Entity {{name: $s}})
                MERGE (b:Entity {{name: $o}})
                MERGE (a)-[:{r.upper()}]->(b)
                """
                session.run(query, s=s, o=o)