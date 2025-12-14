from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "Amiya_8458"

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as sess:
    counts = sess.run("MATCH (n) RETURN count(n) as total").single().value()
    engines = sess.run("MATCH (e:Engine) RETURN count(e) as c").single().value()
    readings = sess.run("MATCH (r:SensorReading) RETURN count(r) as c").single().value()
    failures = sess.run("MATCH (f:FailureEvent) RETURN count(f) as c").single().value()
    windows = sess.run("MATCH (w:FeatureWindow) RETURN count(w) as c").single().value()

print(f"Total nodes: {counts}")
print(f"Engine nodes: {engines}")
print(f"SensorReading nodes: {readings}")
print(f"FailureEvent nodes: {failures}")
print(f"FeatureWindow nodes: {windows}")

driver.close()