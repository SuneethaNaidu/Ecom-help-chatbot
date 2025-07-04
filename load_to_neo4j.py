from neo4j import GraphDatabase
import json
import os

# === Neo4j Database Config ===
URI = "bolt://localhost:7687"  # Use Neo4j Aura bolt URL if cloud
USER = "neo4j"
PASSWORD = "chinnu137"  # <- Replace with your actual password

# === Connect to Neo4j ===
driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def load_product(tx, product, category_cache):
    category = product["category"]

    # Create Category node (if not already created)
    if category not in category_cache:
        tx.run("MERGE (:Category {name: $name})", name=category)
        category_cache.add(category)

    # Create Product node + link to Category
    tx.run("""
        MERGE (p:Product {id: $id})
        SET p.name = $name, p.price = $price
        MERGE (c:Category {name: $category})
        WITH p,c
        MERGE (p)-[:belongsTo]->(c)
    """, id=product["id"], name=product["name"], price=product["price"], category=category)

    # Create Feature nodes + relationships
    for feature in product["features"]:
        tx.run("""
            MERGE (f:Feature {name: $feature})
            WITH f
            MATCH (p:Product {id: $id})
            MERGE (p)-[:hasFeature]->(f)
        """, feature=feature, id=product["id"])


def load_faq(tx, faq):
    # Create FAQ question and answer nodes + link
    tx.run("""
        MERGE (q:FAQ {question: $question})
        MERGE (a:Answer {text: $answer})
        MERGE (q)-[:hasAnswer]->(a)
    """, question=faq["question"], answer=faq["answer"])


def main():
    # Open Neo4j session
    with driver.session() as session:

        # === Load Product Data ===
        print("📦 Loading products...")
        with open(os.path.join("C:/ecom-chatbot/data/large_sample_products.json")) as f:
            products = json.load(f)
        category_cache = set()
        for product in products:
            session.execute_write(load_product, product, category_cache)

        # === Load FAQ Data ===
        print("📄 Loading FAQs...")
        with open(os.path.join("C:/ecom-chatbot/data/large_sample_faqs.json")) as f:
            faqs = json.load(f)
        for faq in faqs:
            session.execute_write(load_faq, faq)

    print("✅ All data loaded successfully into Neo4j!")


if __name__ == "__main__":
    main()
