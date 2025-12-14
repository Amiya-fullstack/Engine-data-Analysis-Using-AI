// Minimal graph schema for engines and readings
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Engine) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (fw:FeatureWindow) REQUIRE fw.window_id IS UNIQUE;

// Example nodes and relationships
// (Engine)-[:HAS_READING]->(SensorReading)
