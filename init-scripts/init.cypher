
// Exemplo de estrutura inicial
CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Pergunta) REQUIRE p.text IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (r:Resposta) REQUIRE r.text IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Contexto) REQUIRE c.hash IS UNIQUE;

MERGE (u:User {id: "lucas", nome: "Lucas Florentino"})
MERGE (c:Contexto {hash: "ctx-001", descricao: "Consulta financeira"})
MERGE (u)-[:FEZ_PERGUNTA]->(c);
