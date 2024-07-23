
#  Answers: "What is the assayed/measured entity?"
MEASURED_ENTITIES = """
MATCH (p:SDPanel)-[:has_tag]->(t:SDTag)
WHERE t.role = 'assayed' AND t.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     apoc.coll.toSet(collect(t.text)) AS assayed_entities
RETURN plain_text_caption AS caption, 
       apoc.text.join(assayed_entities, ', ') AS answer
"""

# Answers:  "What was the intervention/controlled variable in this experiment?"
CONTROLLED_ENTITIES = """
MATCH (p:SDPanel)-[:has_tag]->(t:SDTag)
WHERE t.role = 'intervention' AND t.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     apoc.coll.toSet(collect(t.text)) AS intervention_entities
RETURN plain_text_caption AS caption, 
       apoc.text.join(intervention_entities, ', ') AS answer
"""

# Answers: "In what kind of cell/tissue/organism/subcellular component was the experiment performed?"§
WHERE_WAS_THE_EXPERIMENT_TESTED = """
MATCH (p:SDPanel)-[:has_tag]->(t:SDTag)
WHERE t.category = 'entity' AND t.type IN ['cell', 'cell_line', 'cell_type', 'tissue', 'organism', 'subcellular'] AND t.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     collect(distinct t) AS tags
WITH plain_text_caption,
     apoc.coll.toSet([t IN tags WHERE t.type = 'cell_type' | t.text]) AS cell_types,
     apoc.coll.toSet([t IN tags WHERE t.type = 'organism' | t.text]) AS organisms,
     apoc.coll.toSet([t IN tags WHERE t.type = 'tissue' | t.text]) AS tissues,
     apoc.coll.toSet([t IN tags WHERE t.type = 'cell_line' | t.text]) AS cell_lines,
     apoc.coll.toSet([t IN tags WHERE t.type = 'subcellular' | t.text]) AS subcellular_components
RETURN plain_text_caption AS caption,
       CASE WHEN size(cell_types) > 0 THEN 'cell_type: ' + apoc.text.join(cell_types, ', ') ELSE 'cell_type: None' END +
       '\n' +
       CASE WHEN size(organisms) > 0 THEN 'organism: ' + apoc.text.join(organisms, ', ') ELSE 'organism: None' END +
       '\n' +
       CASE WHEN size(tissues) > 0 THEN 'tissue: ' + apoc.text.join(tissues, ', ') ELSE 'tissue: None' END +
       '\n' +
       CASE WHEN size(cell_lines) > 0 THEN 'cell_line: ' + apoc.text.join(cell_lines, ', ') ELSE 'cell_line: None' END +
       '\n' +
       CASE WHEN size(subcellular_components) > 0 THEN 'subcellular: ' + apoc.text.join(subcellular_components, ', ') ELSE 'subcellular: None' END AS answer
"""

# Answers "What kind of experimental assay was used for this experiment?"
EXPERIMENTAL_ASSAY = """

MATCH (p:SDPanel)-[:has_tag]->(t:SDTag)
WHERE t.category = 'assay' AND t.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     apoc.coll.toSet(collect(t.text)) AS assay_entities
RETURN plain_text_caption AS caption, 
       CASE 
           WHEN size(assay_entities) > 0 THEN apoc.text.join(assay_entities, ', ') 
           ELSE 'None' 
       END AS answer
"""

# Answers : Can you link the identified genes to their NCBI gene identifiers?
NCBI_GENE_LINKING = """
WHERE t.type = 'gene' AND t.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     collect(distinct {gene: t.text, ncbi_id: t.ext_ids}) AS gene_info
WITH plain_text_caption, gene_info,
     [gene IN gene_info | gene.gene + ': ' + gene.ncbi_id] AS formatted_genes
RETURN plain_text_caption AS caption,
       CASE 
           WHEN size(formatted_genes) > 0 THEN apoc.text.join(formatted_genes, '\n') 
           ELSE 'None' 
       END AS ncbi_link

"""

# Answers: "Can you formulate the hypothesis that this experiment has tested."
HYPOTHESIS_TESTED = """
MATCH (p:SDPanel)-[:has_tag]->(assayed:SDTag), (p)-[:has_tag]->(intervention:SDTag)
WHERE assayed.role = 'assayed' AND intervention.role = 'intervention' AND assayed.in_caption = true AND intervention.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     collect(distinct intervention.text + ' --> ' + assayed.text) AS hypotheses
RETURN plain_text_caption AS caption,
       CASE 
           WHEN size(hypotheses) > 0 THEN apoc.text.join(hypotheses, '\n') 
           ELSE 'None' 
       END AS hypothesis

"""

# Answers: Is there any disease term mentioned, or can be infered, in the figure legend?
DISEASES = """
MATCH (p:SDPanel)-[:has_tag]->(t:SDTag)
WHERE t.category = 'disease' AND t.in_caption = true
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     apoc.coll.toSet(collect(t.text)) AS disease_terms
RETURN plain_text_caption AS caption,
       CASE 
           WHEN size(disease_terms) > 0 THEN apoc.text.join(disease_terms, ', ') 
           ELSE 'None' 
       END AS diseases
"""

# Answers: Is there any disease term mentioned, or can be infered, in the figure legend?
IS_EXPERIMENT = """
MATCH (p:SDPanel)
OPTIONAL MATCH (p)-[:has_tag]->(t:SDTag)
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     collect(t) AS tags,
     count(t) AS tag_count
WITH plain_text_caption, tag_count
WHERE NOT (tag_count = 0 AND NOT (plain_text_caption CONTAINS 'schema' OR plain_text_caption CONTAINS 'Schema' OR plain_text_caption CONTAINS 'schematic' OR plain_text_caption CONTAINS 'Schematic'))
RETURN plain_text_caption AS caption,
       CASE 
           WHEN tag_count = 0 AND (plain_text_caption CONTAINS 'schema' OR plain_text_caption CONTAINS 'Schema' OR plain_text_caption CONTAINS 'schematic' OR plain_text_caption CONTAINS 'Schematic') THEN 'No'
           ELSE 'Yes'
       END AS experiment_present

"""

# Answers: Are there any chemical compounds or small molecules mentioned?
CHEMICALS = """
MATCH (p:SDPanel)
OPTIONAL MATCH (p)-[:has_tag]->(t:SDTag)
WITH p, 
     apoc.text.replace(p.caption, '</?[^>]+>', '') AS plain_text_caption, 
     collect(t) AS tags,
     count(t) AS tag_count
WITH plain_text_caption, tag_count
WHERE NOT (tag_count = 0 AND NOT (plain_text_caption CONTAINS 'schema' OR plain_text_caption CONTAINS 'Schema' OR plain_text_caption CONTAINS 'schematic' OR plain_text_caption CONTAINS 'Schematic'))
RETURN plain_text_caption AS caption,
       CASE 
           WHEN tag_count = 0 AND (plain_text_caption CONTAINS 'schema' OR plain_text_caption CONTAINS 'Schema' OR plain_text_caption CONTAINS 'schematic' OR plain_text_caption CONTAINS 'Schematic') THEN 'No'
           ELSE 'Yes'
       END AS experiment_present

"""