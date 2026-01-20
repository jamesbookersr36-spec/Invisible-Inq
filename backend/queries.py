from typing import Optional, Tuple

def get_all_stories_query():
    """Query to fetch all stories with their chapters and sections.

    Updated for the new Neo4j schema:
    - Nodes: :story, :chapter, :section
    - Relationships: :story_chapter, :chapter_section
    """
    return """
    MATCH (story:story)
    OPTIONAL MATCH (story)-[:story_chapter]-(chapter:chapter)
    OPTIONAL MATCH (chapter)-[:chapter_section]-(section:section)
    WITH story, chapter, section,
         toInteger(coalesce(toFloat(story.`Story Number_new`), toFloat(story.`Story Number`), 0)) AS story_number,
         toInteger(coalesce(toFloat(chapter.`Chapter Number_new`), toFloat(chapter.`Chapter Number`), 0)) AS chapter_number,
         toInteger(coalesce(toFloat(section.`Section Number`), 0)) AS section_num
    ORDER BY story_number, chapter_number, section_num
    WITH story, story_number, chapter, chapter_number,
         COLLECT(DISTINCT {
             gid: section.gid,
             section_title: coalesce(section.`Section Name`, section.`graph name`, toString(section.gid)),
             section_num: section_num,
             // For the frontend, we keep using a "section_query" field. In the new DB, gid is the most reliable identifier.
             section_query: toString(section.gid),
             brief: coalesce(section.summary, section.`Summary`, ""),
             chapter_number: chapter_number,
             chapter_title: coalesce(chapter.`Chapter Name`, toString(chapter.gid))
         }) AS sections
    WITH story, story_number,
         COLLECT(DISTINCT {
             gid: chapter.gid,
             chapter_number: chapter_number,
             chapter_title: coalesce(chapter.`Chapter Name`, toString(chapter.gid)),
             sections: sections,
             total_nodes: 0
         }) AS chapters_raw
    WITH story, story_number,
         [c IN chapters_raw WHERE c.gid IS NOT NULL | c] AS chapters_filtered
    WITH story, story_number,
         [c IN chapters_filtered | {
             gid: c.gid,
             chapter_number: c.chapter_number,
             chapter_title: c.chapter_title,
             sections: [s IN c.sections WHERE s.gid IS NOT NULL | s],
             total_nodes: c.total_nodes
         }] AS chapters
    RETURN {
        story_title: coalesce(story.`Story Name`, toString(story.gid)),
        story_gid: story.gid,
        story_brief: "",
        chapters: chapters
    } AS story
    ORDER BY story_number, story.gid
    """

def get_story_by_id_query(story_id: str):
    """Query to fetch a specific story by ID (using Story Name/Number or gid).

    Updated for the new Neo4j schema:
    - Nodes: :story, :chapter, :section
    - Relationships: :story_chapter, :chapter_section
    """
    return """
    MATCH (story:story)
    WHERE toString(story.gid) = $story_id
       OR story.`Story Name` = $story_id
       OR toString(story.`Story Number`) = $story_id
       OR toString(story.`Story Number_new`) = $story_id
    OPTIONAL MATCH (story)-[:story_chapter]-(chapter:chapter)
    OPTIONAL MATCH (chapter)-[:chapter_section]-(section:section)
    WITH story, chapter, section,
         toInteger(coalesce(toFloat(chapter.`Chapter Number_new`), toFloat(chapter.`Chapter Number`), 0)) AS chapter_number,
         toInteger(coalesce(toFloat(section.`Section Number`), 0)) AS section_num
    ORDER BY chapter_number, section_num
    WITH story, chapter, chapter_number,
         COLLECT(DISTINCT {
             gid: section.gid,
             section_title: coalesce(section.`Section Name`, section.`graph name`, toString(section.gid)),
             section_num: section_num,
             section_query: toString(section.gid),
             brief: coalesce(section.summary, section.`Summary`, "")
         }) AS sections
    WITH story,
         COLLECT(DISTINCT {
             gid: chapter.gid,
             chapter_number: chapter_number,
             chapter_title: coalesce(chapter.`Chapter Name`, toString(chapter.gid)),
             sections: [s IN sections WHERE s.gid IS NOT NULL | s],
             total_nodes: 0
         }) AS chapters
    RETURN {
        story_title: coalesce(story.`Story Name`, toString(story.gid)),
        story_gid: story.gid,
        story_brief: "",
        chapters: [c IN chapters WHERE c.gid IS NOT NULL ORDER BY c.chapter_number]
    } AS story
    """, {"story_id": story_id}

def get_graph_data_by_section_query(section_gid: Optional[str] = None, section_query: Optional[str] = None, section_title: Optional[str] = None) -> Tuple[str, dict]:
    """
    Query to fetch graph data (nodes and links) for a section.

    Updated for the new Neo4j schema:
    - Section identity: `(:section {gid})` → `section.gr_id`
    - Graph membership: nodes/relationships where `toString(gr_id)` matches the section's `gr_id`
    - Node labels/types are not hardcoded; we include all nodes except `story/chapter/section`
    """
    
    # Build the match clause based on what parameter was provided
    if section_gid:
        # URL supplies gid as string; compare via toString() for type safety.
        match_clause = "MATCH (section:section) WHERE toString(section.gid) = toString($section_gid)"
        params = {"section_gid": section_gid}
    elif section_query:
        # Backwards/compat: treat section_query as section.gid (string), or try matching common section name fields.
        match_clause = """
        MATCH (section:section)
        WHERE toString(section.gid) = toString($section_query)
           OR section.`Section Name` = $section_query
           OR section.`graph name` = $section_query
        """
        params = {"section_query": section_query}
    elif section_title:
        # New DB uses `Section Name` / `graph name` instead of Section_Title
        match_clause = """
        MATCH (section:section)
        WHERE section.`Section Name` = $section_title
           OR section.`graph name` = $section_title
        """
        params = {"section_title": section_title}
    else:
        raise ValueError("At least one of section_gid, section_query, or section_title must be provided")
    
    query = f"""
    {match_clause}
    WITH section, toString(section.gr_id) AS gr_id

    // Collect all nodes in this section by gr_id (exclude story/chapter/section hierarchy nodes)
    MATCH (node)
    WHERE toString(node.gr_id) = gr_id
      AND NONE(l IN labels(node) WHERE toLower(l) IN ['story','chapter','section'])
    WITH section, gr_id, COLLECT(DISTINCT node) AS all_nodes

    // Collect all relationships fully inside this section (by endpoints' gr_id)
    MATCH (a)-[rel]-(b)
    WHERE toString(a.gr_id) = gr_id
      AND toString(b.gr_id) = gr_id
      AND NONE(l IN labels(a) WHERE toLower(l) IN ['story','chapter','section'])
      AND NONE(l IN labels(b) WHERE toLower(l) IN ['story','chapter','section'])
    WITH section, all_nodes,
         COLLECT(DISTINCT {{
           rel: rel,
           from: a,
           to: b,
           type: type(rel)
         }}) AS all_rels

    RETURN {{
      nodes: [n IN all_nodes | n {{
        .*,
        elementId: elementId(n),
        labels: labels(n),
        node_type: head(labels(n))
      }}],
      links: [rd IN all_rels | {{
        gid: coalesce(toString(rd.rel.gid), elementId(rd.rel)),
        elementId: elementId(rd.rel),
        type: rd.type,
        from_gid: rd.from.gid,
        to_gid: rd.to.gid,
        from_labels: labels(rd.from),
        to_labels: labels(rd.to),
        // Common fields consumed by the frontend
        relationship_summary: coalesce(rd.rel.summary, rd.rel.`Relationship Summary`, rd.rel.name, rd.rel.text),
        article_title: coalesce(rd.rel.title, rd.rel.`Article Title`),
        article_url: coalesce(rd.rel.url, rd.rel.`Article URL`, rd.rel.`article URL`),
        relationship_date: coalesce(rd.rel.date, rd.rel.`Date`, rd.rel.`Relationship Date`),
        properties: rd.rel {{ .* }}
      }}]
    }} AS graphData
    """
    
    return query, params


def get_cluster_data_query(
    node_type: str,
    property_key: str,
    section_query: Optional[str] = None,
    cluster_limit: int = 5,
    node_limit: int = 10
) -> Tuple[str, dict]:
    """
    Query to fetch clustered node samples grouped by a given property key.

    - `node_type` is expected to be a frontend normalized label (e.g. "place_of_performance", "entity", "action").
      We match it against actual Neo4j labels using a normalized comparison:
        replace(toLower(label), ' ', '_') == node_type  OR  toLower(label) == node_type
    - `property_key` is the Neo4j property name to cluster by.
    - Optionally filters to a section via `n.section = section_query` if provided.

    Returns a dict shape:
      {
        node_type, property_key, section_query,
        clusters: [{ value, count, nodes: [{id,name}, ...] }, ...]
      }
    """

    query = """
    // Resolve section filter to a gr_id (new DB) if provided.
    WITH $section_query AS section_query
    OPTIONAL MATCH (sec:section)
    WHERE section_query IS NOT NULL
      AND (
        toString(sec.gid) = toString(section_query)
        OR sec.`Section Name` = section_query
        OR sec.`graph name` = section_query
      )
    WITH section_query, toString(sec.gr_id) AS section_gr_id

    MATCH (n)
    WHERE ANY(l IN labels(n) WHERE replace(toLower(l), ' ', '_') = $node_type OR toLower(l) = $node_type)
      AND n[$property_key] IS NOT NULL
      AND (
        section_query IS NULL
        OR toString(n.gr_id) = coalesce(section_gr_id, toString(section_query))
        OR n.section = section_query
        OR section_query IN coalesce(n.sections, [])
      )
    WITH n, toString(n[$property_key]) AS propVal
    WITH propVal,
         collect(DISTINCT {
            id: coalesce(toString(n.gid), toString(n.id), toString(id(n))),
            name: coalesce(
              n.name,
              n.`Entity Name`,
              n.`Action Text`,
              n.`Result Name`,
              n.`Process Name`,
              n.`Relationship NAME`,
              n.`Country Name`,
              toString(n.gid),
              toString(id(n))
            )
         }) AS nodes,
         count(DISTINCT n) AS count
    ORDER BY count DESC, propVal ASC
    WITH collect({
      value: propVal,
      count: count,
      nodes: nodes[0..$node_limit]
    })[0..$cluster_limit] AS clusters
    RETURN {
      node_type: $node_type,
      property_key: $property_key,
      section_query: $section_query,
      clusters: clusters
    } AS clusterData
    """

    params = {
        "node_type": node_type,
        "property_key": property_key,
        "section_query": section_query,
        "cluster_limit": cluster_limit,
        "node_limit": node_limit,
    }

    return query, params

def get_section_by_id_query(section_gid: str):
    """Get section details by gid"""
    return """
    MATCH (section:Section {gid: $section_gid})
    OPTIONAL MATCH (chapter:Chapter)-[:Chapter_Section]->(section)
    RETURN {
        gid: section.gid,
        section_title: section.Section_Title,
        section_num: section.Section_Num,
        section_query: section.section_query,
        brief: section.brief,
        chapter: {
            gid: chapter.gid,
            chapter_number: chapter.`Chapter Number`,
            chapter_title: chapter.`Chapter Title`
        }
    } AS section
    """, {"section_gid": section_gid}

def get_graph_data_by_section_and_country_query(section_query: str, country_name: str) -> Tuple[str, dict]:
    """
    Query to fetch graph data (nodes and links) for a section filtered by country.

    Updated for the new Neo4j schema:
    - `section_query` is treated as the section `gid` (string), consistent with the homepage mapping.
    - We resolve `section.gr_id`, then find a Country node within that gr_id by name, then include nodes within 2 hops.
    """
    
    query = """
    MATCH (section:section)
    WHERE toString(section.gid) = toString($section_query)
       OR section.`Section Name` = $section_query
       OR section.`graph name` = $section_query
    WITH section, toString(section.gr_id) AS gr_id

    // Find the country node(s) matching the country name in this section
    MATCH (country)
    WHERE toString(country.gr_id) = gr_id
      AND ANY(l IN labels(country) WHERE toLower(l) = 'country')
      AND toLower(coalesce(country.name, country.`Country Name`, country.`Country Name_new`, '')) = toLower($country_name)

    // Collect nodes within 2 hops of the country (inside the same gr_id)
    MATCH (country)-[*0..2]-(n)
    WHERE toString(n.gr_id) = gr_id
      AND NONE(l IN labels(n) WHERE toLower(l) IN ['story','chapter','section'])
    WITH gr_id, COLLECT(DISTINCT n.gid) AS node_gids
    WITH gr_id, [gid IN node_gids WHERE gid IS NOT NULL] AS node_gids

    MATCH (node)
    WHERE node.gid IN node_gids
      AND toString(node.gr_id) = gr_id
      AND NONE(l IN labels(node) WHERE toLower(l) IN ['story','chapter','section'])
    WITH gr_id, COLLECT(DISTINCT node) AS all_nodes, node_gids

    MATCH (a)-[rel]-(b)
    WHERE a.gid IN node_gids
      AND b.gid IN node_gids
      AND toString(a.gr_id) = gr_id
      AND toString(b.gr_id) = gr_id
    WITH all_nodes,
         COLLECT(DISTINCT {
           rel: rel,
           from: a,
           to: b,
           type: type(rel)
         }) AS all_rels

    RETURN {
      nodes: [n IN all_nodes | n {
        .*,
        elementId: elementId(n),
        labels: labels(n),
        node_type: head(labels(n))
      }],
      links: [rd IN all_rels | {
        gid: coalesce(toString(rd.rel.gid), elementId(rd.rel)),
        elementId: elementId(rd.rel),
        type: rd.type,
        from_gid: rd.from.gid,
        to_gid: rd.to.gid,
        relationship_summary: coalesce(rd.rel.summary, rd.rel.`Relationship Summary`, rd.rel.name, rd.rel.text),
        article_title: coalesce(rd.rel.title, rd.rel.`Article Title`),
        article_url: coalesce(rd.rel.url, rd.rel.`Article URL`, rd.rel.`article URL`),
        relationship_date: coalesce(rd.rel.date, rd.rel.`Date`, rd.rel.`Relationship Date`),
        properties: rd.rel { .* }
      }]
    } AS graphData
    """

    params = {"section_query": section_query, "country_name": country_name}
    return query, params

def get_calendar_data_by_section_query(section_gid: Optional[str] = None, section_query: Optional[str] = None, section_title: Optional[str] = None) -> Tuple[str, dict]:
    """
    Query to fetch calendar/timeline data for a section with distinct timeline and free-floating items.
    
    Timeline items (Milestone, Result, Incident, Action) are sorted by:
    1. Date (chronological)
    2. Type priority: Milestone (1) → Result/Incident (2) → Action (3)
    
    Free-floating items (Entity, Location, Event, etc.) are returned with their connections
    to timeline items, allowing frontend to position them dynamically based on viewport.
    """
    
    # Build the match clause based on what parameter was provided
    if section_gid:
        match_clause = "MATCH (section:Section {gid: $section_gid})"
        params = {"section_gid": section_gid}
    elif section_query:
        match_clause = "MATCH (section:Section {section_query: $section_query})"
        params = {"section_query": section_query}
    elif section_title:
        match_clause = "MATCH (section:Section {Section_Title: $section_title})"
        params = {"section_title": section_title}
    else:
        raise ValueError("At least one of section_gid, section_query, or section_title must be provided")
    
    query = f"""
    {match_clause}
    WITH section

    // ========== TIMELINE ITEMS: Milestone, Result, Incident (mapped as Result), Action ==========
    OPTIONAL MATCH (timeline_node)
    WHERE timeline_node.section = section.section_query
      AND (timeline_node:Result OR timeline_node:Action)
      AND timeline_node.Date IS NOT NULL

    WITH section, timeline_node,
         labels(timeline_node)[0] as node_label,
         CASE
             WHEN timeline_node:Result THEN COALESCE(timeline_node.`Result Name`, timeline_node.`Process Result`, 'Result')
             WHEN timeline_node:Action THEN COALESCE(timeline_node.`Action Text`, timeline_node.`Action Summary`, 'Action')
             ELSE toString(timeline_node.gid)
         END as node_name,
         CASE
             WHEN timeline_node:Result THEN COALESCE(timeline_node.`Process Summary`, timeline_node.brief, '')
             WHEN timeline_node:Action THEN COALESCE(timeline_node.`Action Summary`, timeline_node.brief, '')
             ELSE ''
         END as node_description,
         CASE
             WHEN timeline_node:Result THEN 2
             WHEN timeline_node:Action THEN 3
             ELSE 4
         END as type_priority
    WHERE timeline_node IS NOT NULL
    
    // Sort timeline items by date DESC, then by type priority ASC
    WITH section, timeline_node, node_label, node_name, node_description, type_priority
    ORDER BY timeline_node.Date DESC, type_priority ASC
    
    WITH section,
         COLLECT(DISTINCT {{
             gid: timeline_node.gid,
             node_type: node_label,
             date: timeline_node.Date,
             name: node_name,
             description: node_description,
             properties: timeline_node {{
                 .gid, .Date, .section, .degree,
                 .`Process Date`, .`Article URL`, .`Article Text`, .`Process Result`, 
                 .`Process Summary`, .`Process Target`, .`Action Text`, .`Action Summary`,
                 .`Article Title`, .`Result Name`
             }},
             type_priority: type_priority
         }}) as timeline_items

    // ========== FREE-FLOATING ITEMS: Entity, Location, Event, Country, etc. ==========
    OPTIONAL MATCH (floating_node)
    WHERE floating_node.section = section.section_query
      AND (floating_node:Entity OR floating_node:Location OR floating_node:Country 
           OR floating_node:Recipient OR floating_node:Region OR floating_node:Agency
           OR floating_node:`Place Of Performance` OR floating_node:Process)

    WITH section, timeline_items,
         COLLECT(DISTINCT {{
             gid: floating_node.gid,
             node_type: labels(floating_node)[0],
             name: CASE
                 WHEN floating_node:Entity THEN COALESCE(floating_node.`Entity Name`, 'Entity')
                 WHEN floating_node:Location THEN COALESCE(floating_node.`Performance Location`, 'Location')
                 WHEN floating_node:Country THEN COALESCE(floating_node.`Country Name`, 'Country')
                 WHEN floating_node:Recipient THEN COALESCE(floating_node.`Recipient Name`, 'Recipient')
                 WHEN floating_node:Region THEN COALESCE(floating_node.`Global Region`, 'Region')
                 WHEN floating_node:Agency THEN COALESCE(floating_node.`Awarding Agency`, 'Agency')
                 WHEN floating_node:`Place Of Performance` THEN COALESCE(floating_node.primary_place_of_performance_country_name, 'Place')
                 WHEN floating_node:Process THEN COALESCE(floating_node.Process, floating_node.`Process Summary`, 'Process')
                 ELSE toString(floating_node.gid)
             END,
             properties: floating_node {{
                 .gid, .section, .degree,
                 .`Entity Name`, .`Performance Location`, .`Country Name`,
                 .`Recipient Name`, .`Global Region`, .`Awarding Agency`,
                 .primary_place_of_performance_country_name, .Process, .`Process Summary`
             }}
         }}) as floating_items

    // ========== RELATIONSHIPS: connections between ALL items ==========
    OPTIONAL MATCH (source)-[rel]->(target)
    WHERE source.section = section.section_query
      AND target.section = section.section_query
      AND (source:Entity OR source:Relationship OR source:Action OR source:Result OR source:Country 
           OR source:Location OR source:Recipient OR source:Region OR source:Agency 
           OR source:`Place Of Performance` OR source:Process)
      AND (target:Entity OR target:Relationship OR target:Action OR target:Result OR target:Country 
           OR target:Location OR target:Recipient OR target:Region OR target:Agency 
           OR target:`Place Of Performance` OR target:Process)

    WITH section, timeline_items, floating_items,
         COLLECT(DISTINCT {{
             gid: id(rel),
             type: type(rel),
             source_gid: source.gid,
             target_gid: target.gid,
             source_type: labels(source)[0],
             target_type: labels(target)[0],
             date: rel.`Relationship Date`,
             properties: rel {{
                 .`Relationship Summary`, .`Article Title`, .`article URL`, .`Relationship Date`
             }}
         }}) as relationships

    RETURN {{
        section_query: section.section_query,
        section_title: section.Section_Title,
        timeline_items: timeline_items,
        floating_items: floating_items,
        relationships: relationships
    }} AS calendarData
    """
    
    return query, params

def get_story_statistics_query(story_gid: Optional[str] = None, story_title: Optional[str] = None):
    """Get statistics for a story: total nodes, entity count, etc."""
    if story_gid:
        match_clause = "MATCH (story:Story {gid: $story_gid})"
        params = {"story_gid": story_gid}
    elif story_title:
        match_clause = "MATCH (story:Story {Story_Title: $story_title})"
        params = {"story_title": story_title}
    else:
        raise ValueError("Either story_gid or story_title must be provided")
    
    query = f"""
    {match_clause}
    OPTIONAL MATCH (story)-[:Story_Chapter]->(chapter:Chapter)
    OPTIONAL MATCH (chapter)-[:Chapter_Section]->(section:Section)
    
    // Get all section queries for this story
    WITH story, COLLECT(DISTINCT section.section_query) as section_queries
    
    // Count all nodes across all sections in this story
    MATCH (n)
    WHERE (n:Entity OR n:Relationship OR n:Amount OR n:Agency OR n:Action OR n:Country OR n:DBA OR n:Description OR n:Location OR n:`Place Of Performance` OR n:Process OR n:Recipient OR n:Region OR n:Result OR n:Purpose OR n:Transaction OR n:`Sub Agency` OR n:`USAID Program Region`)
      AND n.section IN section_queries
    
    // Count total nodes, entities, and highlighted nodes separately
    WITH story, section_queries, 
         COUNT(DISTINCT n) as total_nodes,
         COLLECT(DISTINCT CASE WHEN n:Entity THEN n.gid ELSE null END) as entity_gids,
         COUNT(DISTINCT CASE WHEN n.highlight = true THEN n.gid ELSE null END) as highlighted_nodes
    
    WITH story, total_nodes, highlighted_nodes,
         SIZE([gid IN entity_gids WHERE gid IS NOT NULL]) as entity_count
    
    RETURN {{
        story_gid: story.gid,
        story_brief: story.brief,
        story_title: story.Story_Title,
        total_nodes: total_nodes,
        entity_count: entity_count,
        highlighted_nodes: highlighted_nodes,
        updated_date: COALESCE(story.updated_date, story.created_date, story.date, datetime())
    }} AS statistics
    """
    
    return query, params

def get_all_node_types_query():
    """Query to fetch all distinct node types (labels) from the database"""
    # Use a query that finds all distinct labels by checking actual nodes
    # This is more reliable than CALL db.labels() which may not work in all Neo4j versions
    query = """
    // New DB: return normalized label names for nodes that participate in graphs (by gr_id).
    MATCH (n)
    WHERE n.gr_id IS NOT NULL
      AND NONE(l IN labels(n) WHERE toLower(l) IN ['story','chapter','section'])
    WITH labels(n) AS nodeLabels
    UNWIND nodeLabels AS label
    WITH label
    WHERE toLower(label) NOT IN ['story','chapter','section']
    RETURN DISTINCT replace(toLower(label), ' ', '_') AS node_type
    ORDER BY node_type
    """
    return query, {}
