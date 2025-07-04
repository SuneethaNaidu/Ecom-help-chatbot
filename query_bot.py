from neo4j import GraphDatabase

# === Neo4j Config ===
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "chinnu137"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_product_features(product_name):
    query = """
    MATCH (p:Product)-[:hasFeature]->(f:Feature)
    WHERE toLower(p.name) CONTAINS toLower($name)
    RETURN p.name AS product, collect(f.name) AS features
    """
    with driver.session() as session:
        result = session.run(query, name=product_name)
        record = result.single()
        if record:
            return f"{record['product']} has features: {', '.join(record['features'])}"
        else:
            return "No product found with that name."


def get_faq_answer(user_question):
    query = """
    MATCH (q:FAQ)-[:hasAnswer]->(a:Answer)
    WHERE toLower(q.question) CONTAINS toLower($question)
    RETURN a.text AS answer
    """
    with driver.session() as session:
        result = session.run(query, question=user_question)
        record = result.single()
        return record["answer"] if record else "Sorry, I couldn't find an answer for that."


def main():
    print("🤖 Ask me something (type 'exit' to quit):")
    while True:
        q = input("You: ")
        if q.lower() == "exit":
            break

        # Simple keyword-based routing
        if "feature" in q.lower() or "spec" in q.lower():
            # Try product feature query
            product_name = q.replace("features of", "").strip()
            print("Bot:", get_product_features(product_name))
        else:
            # Try FAQ
            print("Bot:", get_faq_answer(q))


if __name__ == "__main__":
    main()
