from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "Amiya_8458"

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as sess:
    before = {
        'engines': sess.run("MATCH (e:Engine) RETURN count(e) as c").single().value(),
        'readings': sess.run("MATCH (r:SensorReading) RETURN count(r) as c").single().value(),
        'failures': sess.run("MATCH (f:FailureEvent) RETURN count(f) as c").single().value(),
        'windows': sess.run("MATCH (w:FeatureWindow) RETURN count(w) as c").single().value()
    }
    print("Counts before cleanup:", before)

    sess.run("MATCH (r:SensorReading) DETACH DELETE r")
    sess.run("MATCH (f:FailureEvent) DETACH DELETE f")
    sess.run("MATCH (w:FeatureWindow) DETACH DELETE w")

    after = {
        'engines': sess.run("MATCH (e:Engine) RETURN count(e) as c").single().value(),
        'readings': sess.run("MATCH (r:SensorReading) RETURN count(r) as c").single().value(),
        'failures': sess.run("MATCH (f:FailureEvent) RETURN count(f) as c").single().value(),
        'windows': sess.run("MATCH (w:FeatureWindow) RETURN count(w) as c").single().value()
    }
    print("Counts after cleanup:", after)

driver.close()
