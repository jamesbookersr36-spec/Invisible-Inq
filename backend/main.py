# Import platform fix first to avoid Windows multiprocessing issues
import platform_fix

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import time
import logging
from config import Config
from services import get_all_stories, get_graph_data, get_graph_data_by_section_and_country, search_with_ai, get_story_statistics, get_all_node_types, get_calendar_data, get_cluster_data, get_entity_wikidata, search_entity_wikidata
from models import GraphData
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Startup: Initialize database connection
    logger.info("Starting application...")
    try:
        from database import db
        # Test database connection on startup
        try:
            result = db.execute_query("RETURN 1 as test")
            if result and result[0].get("test") == 1:
                logger.info("Database connection verified successfully")
            else:
                logger.warning("Database connection test returned unexpected result")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            logger.warning("Application will continue, but database operations may fail")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Application will continue, but database operations may fail")
    
    yield
    
    # Shutdown: Close database connection
    logger.info("Shutting down application...")
    try:
        from database import db
        db.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.warning(f"Error closing database connection: {e}")

app = FastAPI(
    title="Graph Visualization API",
    description="API for serving graph data from Neo4j database",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Graph Visualization API",
        "version": "1.0.0",
        "endpoints": {
            "stories": "/api/stories",
            "graph_data": "/api/graph/{substory_id} or /api/graph?graph_path=...",
            "calendar": "/api/calendar?section_query=...",
            "ai_search": "/api/ai/search?query=...",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Check the health of the API and database connection"""
    from database import db
    from config import Config
    
    health_status = {
        "api": "healthy",
        "database": "unknown",
        "database_uri": Config.NEO4J_URI,
        "database_user": Config.NEO4J_USER,
        "timestamp": None
    }
    
    try:
        # Try to connect and execute a simple query
        result = db.execute_query("RETURN 1 as test")
        if result and result[0].get("test") == 1:
            health_status["database"] = "connected"
            health_status["timestamp"] = time.time()
        else:
            health_status["database"] = "error: Query returned unexpected result"
            return health_status
    except Exception as e:
        error_msg = str(e)
        health_status["database"] = f"error: {error_msg}"
        health_status["error_details"] = error_msg
        # Don't raise exception, just return the status for diagnostics
        return health_status
    
    return health_status

@app.get("/api/stories", response_model=List[dict])
async def get_stories():
    try:
        stories = get_all_stories()

        return [story.model_dump() for story in stories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stories: {str(e)}")

@app.get("/api/graph/{substory_id}", response_model=dict)
async def get_graph_by_substory_id(substory_id: str):
    try:
        if substory_id.isdigit() or (substory_id.replace('.', '').isdigit()):
            graph_data = get_graph_data(section_gid=substory_id)
        else:
            graph_data = get_graph_data(section_query=substory_id)
        return graph_data.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching graph data for substory {substory_id}: {str(e)}"
        )

@app.get("/api/graph", response_model=dict)
async def get_graph_by_path(graph_path: Optional[str] = None):
    if not graph_path:
        raise HTTPException(status_code=400, detail="graph_path parameter is required")

    try:
        graph_data = get_graph_data(graph_path=graph_path)
        return graph_data.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching graph data for path {graph_path}: {str(e)}"
        )

@app.get("/api/graph/{substory_id}/country/{country_name}", response_model=dict)
async def get_graph_by_substory_and_country(substory_id: str, country_name: str):
    """Get graph data for a section filtered by country"""
    try:
        # First, get the section_query from the substory
        # The substory_id might be a section_query or we need to look it up
        # For now, treat substory_id as section_query (same as get_graph_by_substory_id)
        section_query = substory_id
        
        graph_data = get_graph_data_by_section_and_country(section_query, country_name)
        return graph_data.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching graph data for substory {substory_id} and country {country_name}: {str(e)}"
        )

@app.get("/api/calendar", response_model=dict)
async def get_calendar_by_section(section_query: Optional[str] = None, section_gid: Optional[str] = None, section_title: Optional[str] = None):
    """Get calendar/timeline data for a section based on relationships with all nodes"""
    logger.info(f"Calendar endpoint called with section_query={section_query}, section_gid={section_gid}, section_title={section_title}")
    
    if not section_query and not section_gid and not section_title:
        logger.warning("Calendar endpoint called without any section parameter")
        raise HTTPException(status_code=400, detail="At least one of section_query, section_gid, or section_title must be provided")
    
    try:
        logger.debug(f"Fetching calendar data for section_query={section_query}")
        calendar_data = get_calendar_data(
            section_gid=section_gid,
            section_query=section_query,
            section_title=section_title
        )
        logger.info(f"Successfully retrieved calendar data: {len(calendar_data.get('calendar_items', []))} items")
        return calendar_data
    except ValueError as e:
        logger.warning(f"Validation error in calendar endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching calendar data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching calendar data: {str(e)}"
        )


@app.get("/api/cluster", response_model=dict)
async def get_cluster_endpoint(
    node_type: str,
    property_key: str,
    section_query: Optional[str] = None,
    cluster_limit: int = 5,
    node_limit: int = 10
):
    """
    Get clustered node samples grouped by a property key for a given node type.

    - `node_type`: normalized label from frontend (e.g. "entity", "place_of_performance")
    - `property_key`: Neo4j property name (exact key)
    - `section_query`: optional filter to a section (matches `n.section`)
    """
    try:
        return get_cluster_data(
            node_type=node_type,
            property_key=property_key,
            section_query=section_query,
            cluster_limit=cluster_limit,
            node_limit=node_limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cluster data: {str(e)}")

@app.get("/api/stories/{story_id}/statistics", response_model=dict)
async def get_story_statistics_endpoint(story_id: str):
    """Get statistics for a story (total nodes, entity count, etc.)"""
    try:
        statistics = get_story_statistics(story_id)
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching statistics for story {story_id}: {str(e)}"
        )

@app.get("/api/node-types", response_model=List[str])
async def get_node_types():
    """Get all distinct node types from the database"""
    try:
        node_types = get_all_node_types()
        return node_types
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching node types: {str(e)}"
        )


# ============== Entity Wikidata Endpoints ==============

@app.get("/api/entity/wikidata/{entity_name}")
async def get_entity_wikidata_by_name(entity_name: str):
    """
    Get detailed wikidata information for an entity by name.
    Returns comprehensive information from the entity_wikidata table in the wuhan database.
    """
    try:
        from urllib.parse import unquote
        
        # Decode URL-encoded entity name
        entity_name = unquote(entity_name)
        
        if not entity_name or not entity_name.strip():
            raise HTTPException(status_code=400, detail="Entity name is required")
        
        logger.info(f"API endpoint called - entity_name: '{entity_name}'")
        
        result = get_entity_wikidata(entity_name.strip())
        
        logger.info(f"API response - found: {result.get('found')}, has_data: {bool(result.get('data'))}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error fetching entity wikidata for '{entity_name}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching entity wikidata: {str(e)}"
        )


@app.get("/api/entity/wikidata")
async def search_entity_wikidata_endpoint(name: Optional[str] = None, q: Optional[str] = None, limit: int = 10):
    """
    Search for entities in the wikidata table.
    Supports both 'name' and 'q' query parameters for flexibility.
    
    Args:
        name: Entity name to search for
        q: Alternative query parameter for search
        limit: Maximum number of results (default: 10, max: 50)
    """
    try:
        search_term = name or q
        if not search_term or not search_term.strip():
            raise HTTPException(status_code=400, detail="Search term is required (use 'name' or 'q' parameter)")
        
        # Limit the results to prevent abuse
        actual_limit = min(max(1, limit), 50)
        
        result = search_entity_wikidata(search_term.strip(), actual_limit)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error searching entity wikidata: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching entity wikidata: {str(e)}"
        )


class SearchQuery(BaseModel):
    query: str

class SummaryRequest(BaseModel):
    query: str  # User's question about the graph
    graphData: dict  # The current graph data with nodes and links

@app.post("/api/ai/summary", response_model=dict)
async def generate_ai_summary(request: SummaryRequest):
    """
    Generate an AI summary of graph data with embedded entity markers.
    
    The summary will use [[Entity Name]] markers for entities that exist in the graph,
    allowing the frontend to render them as clickable buttons.
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query is required")
        
        if not request.graphData:
            raise HTTPException(status_code=400, detail="Graph data is required")
        
        from services import generate_graph_summary
        
        summary_data = generate_graph_summary(
            query=request.query.strip(),
            graph_data=request.graphData
        )
        
        return summary_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error generating AI summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating AI summary: {str(e)}"
        )

@app.post("/api/ai/search", response_model=dict)
async def ai_search(search_query: SearchQuery):
    try:
        if not search_query.query or not search_query.query.strip():
            raise HTTPException(status_code=400, detail="Query parameter is required")

        graph_data, generated_query = search_with_ai(search_query.query.strip())
        return {
            "graphData": graph_data.model_dump(),
            "generatedQuery": generated_query
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing AI search: {str(e)}"
        )

@app.get("/api/ai/search", response_model=dict)
async def ai_search_get(query: str):
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query parameter is required")

        graph_data, generated_query = search_with_ai(query.strip())
        return {
            "graphData": graph_data.model_dump(),
            "generatedQuery": generated_query
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing AI search: {str(e)}"
        )

class CypherQuery(BaseModel):
    query: str

class CreateNodeRequest(BaseModel):
    category: str  # Node label/type
    properties: dict  # Node properties

@app.post("/api/cypher/execute", response_model=dict)
async def execute_cypher_query(cypher_query: CypherQuery):
    try:
        if not cypher_query.query or not cypher_query.query.strip():
            raise HTTPException(status_code=400, detail="Cypher query is required")

        query = cypher_query.query.strip()

        from services import extract_graph_data_from_cypher_results
        from database import db

        try:
            results = db.execute_query(query)
            
            
            if results:
                for idx, record in enumerate(results):
                    logger.info(f"[BACKEND]   Record [{idx + 1}]: {record}")
                    logger.info(f"[BACKEND]   Record [{idx + 1}] keys: {list(record.keys()) if isinstance(record, dict) else 'N/A'}")
            else:
                logger.info("[BACKEND] Results: [] (empty)")
            logger.info("=" * 80)
            
        except Exception as db_error:
            error_msg = str(db_error)
            raise HTTPException(
                status_code=400,
                detail=f"Cypher query execution failed: {error_msg}"
            )

        if not results:
            return {
                "graphData": GraphData(nodes=[], links=[]).model_dump(),
                "executedQuery": query,
                "rawResults": []
            }

        # Check if this is a schema query (like CALL db.schema.nodeTypeProperties())
        # Schema queries return simple records, not graph data
        is_schema_query = "CALL db.schema" in query.upper() or "db.schema" in query
        
        # Try to extract graph data first
        graph_data = extract_graph_data_from_cypher_results(results)
        
        # BACKEND LOG: Graph data extraction results
        # Check if we have actual graph data (nodes or links)
        has_graph_data = (graph_data.nodes and len(graph_data.nodes) > 0) or (graph_data.links and len(graph_data.links) > 0)
        
        
        # Check if results look like simple records (not graph data)
        # Simple records typically have keys like nodeType, properties, etc. and don't have gid
        is_simple_record = False
        if results and len(results) > 0:
            first_record = results[0]
            if isinstance(first_record, dict):
                # Check if it has schema-like keys (nodeType, properties) or other non-graph keys
                record_keys = list(first_record.keys())
                schema_keys = ["nodeType", "properties", "propertyName", "mandatory"]
                has_schema_keys = any(key in record_keys for key in schema_keys)
                has_gid = "gid" in record_keys
                # If it has schema keys but no gid, it's likely a simple record
                is_simple_record = has_schema_keys and not has_gid
        
        # If it's a schema query, simple record, or no graph data was extracted, return raw results
        if is_schema_query or is_simple_record or not has_graph_data:
            reason = "schema query" if is_schema_query else ("simple record" if is_simple_record else "no graph data")
            if results and len(results) > 0:
                logger.info(f"[BACKEND] First raw result: {results[0]}")
                logger.info(f"[BACKEND] First raw result type: {type(results[0])}")
                if isinstance(results[0], dict):
                    logger.info(f"[BACKEND] First raw result keys: {list(results[0].keys())}")
            
            # Convert results to JSON-serializable format
            # Neo4j records might contain special types that need conversion
            import json
            def make_serializable(obj):
                """Recursively convert object to JSON-serializable format"""
                if obj is None:
                    return None
                elif isinstance(obj, (str, int, float, bool)):
                    return obj
                elif isinstance(obj, list):
                    return [make_serializable(item) for item in obj]
                elif isinstance(obj, dict):
                    return {key: make_serializable(value) for key, value in obj.items()}
                else:
                    # For any other type, convert to string
                    try:
                        # Try to convert to JSON first
                        json.dumps(obj)
                        return obj
                    except (TypeError, ValueError):
                        return str(obj)
            
            serializable_results = [make_serializable(record) for record in results]
            
            response = {
                "graphData": GraphData(nodes=[], links=[]).model_dump(),
                "executedQuery": query,
                "rawResults": serializable_results  # Return serializable results
            }
            return response
        
        logger.info("[BACKEND] ✅ Returning graphData (graph data detected)")
        response = {
            "graphData": graph_data.model_dump(),
            "executedQuery": query,
            "rawResults": None  # No raw results when graph data is present
        }
        logger.info(f"[BACKEND] 📤 Response being sent to frontend:")
        logger.info(f"[BACKEND]   - graphData nodes: {len(response['graphData']['nodes']) if response['graphData'].get('nodes') else 0}")
        logger.info(f"[BACKEND]   - graphData links: {len(response['graphData']['links']) if response['graphData'].get('links') else 0}")
        logger.info(f"[BACKEND]   - rawResults: {response['rawResults']}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"[BACKEND] ❌ Unexpected error in execute_cypher_query:")
        logger.error(f"[BACKEND] Error type: {type(e).__name__}")
        logger.error(f"[BACKEND] Error message: {str(e)}")
        logger.error(f"[BACKEND] Full traceback:\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing Cypher query: {str(e)}"
        )

@app.post("/api/nodes/create")
async def create_node(node_request: CreateNodeRequest):
    """
    Create a new node in Neo4j with the specified label and properties.
    
    Args:
        node_request: Contains category (node label) and properties (dict of property key-value pairs)
    
    Returns:
        Created node data with generated ID
    """
    try:
        from database import db
        
        # Validate inputs
        if not node_request.category or not node_request.category.strip():
            raise HTTPException(status_code=400, detail="Category (node label) is required")
        
        category = node_request.category.strip()
        properties = node_request.properties or {}
        
        # Clean category label - remove backticks if present, we'll add them properly
        clean_category = category
        if clean_category.startswith(':`'):
            clean_category = clean_category[2:]
        if clean_category.endswith('`'):
            clean_category = clean_category[:-1]
        
        # Build Cypher CREATE query
        # Handle node labels with spaces using backticks
        if ' ' in clean_category or '-' in clean_category:
            node_label = f"`{clean_category}`"
        else:
            node_label = clean_category
        
        # Build property assignments
        # Property names with spaces need backticks in Cypher
        property_assignments = []
        params = {}
        
        for prop_key, prop_value in properties.items():
            if prop_key and prop_key.strip() and prop_value is not None:
                # Clean property key
                clean_prop_key = prop_key.strip()
                
                # Use backticks for property names with spaces
                if ' ' in clean_prop_key or '-' in clean_prop_key:
                    cypher_prop_key = f"`{clean_prop_key}`"
                else:
                    cypher_prop_key = clean_prop_key
                
                # Use parameterized query for values
                param_name = f"prop_{len(params)}"
                property_assignments.append(f"{cypher_prop_key}: ${param_name}")
                params[param_name] = prop_value
        
        # If no properties, create node with just the label
        if not property_assignments:
            query = f"CREATE (n:{node_label}) RETURN n"
        else:
            props_str = ", ".join(property_assignments)
            query = f"CREATE (n:{node_label} {{{props_str}}}) RETURN n"
        
        logger.info(f"[BACKEND] Creating node with label: {node_label}")
        logger.info(f"[BACKEND] Query: {query}")
        logger.info(f"[BACKEND] Parameters: {params}")
        
        # Execute write query
        try:
            results = db.execute_write_query(query, params)
            
            if not results or len(results) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="Node creation failed: No result returned"
                )
            
            # Extract created node data
            # Neo4j returns records as dicts via record.data(), but 'n' might still be a Node object
            result_record = results[0]
            created_node = result_record.get('n', {})
            
            # Convert Neo4j Node object to dict
            # Neo4j Node objects have a _properties attribute
            if hasattr(created_node, '_properties'):
                # It's a Neo4j Node object, extract properties
                node_data = dict(created_node._properties)
                # Add element_id if available (Neo4j 5.x+)
                if hasattr(created_node, 'element_id'):
                    node_data['element_id'] = created_node.element_id
                # Add id if available (Neo4j 4.x)
                if hasattr(created_node, 'id'):
                    node_data['id'] = created_node.id
            elif isinstance(created_node, dict):
                # It's already a dict
                node_data = created_node
            else:
                # Fallback: try to convert to dict
                try:
                    node_data = dict(created_node) if created_node else {}
                except (TypeError, ValueError):
                    # If conversion fails, create empty dict
                    node_data = {}
            
            logger.info(f"[BACKEND] ✅ Node created successfully: {node_data}")
            
            return {
                "success": True,
                "node": node_data,
                "message": f"Node with label '{category}' created successfully"
            }
            
        except Exception as db_error:
            error_msg = str(db_error)
            logger.error(f"[BACKEND] ❌ Database error creating node: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create node: {error_msg}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[BACKEND] ❌ Error creating node: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating node: {str(e)}"
        )

class DeleteNodeRequest(BaseModel):
    node_id: str  # Node ID (gid) to delete

@app.delete("/api/nodes/delete")
async def delete_node(node_request: DeleteNodeRequest):
    """
    Delete a node and all its relationships from Neo4j.
    
    Args:
        node_request: Contains node_id (gid) of the node to delete
    
    Returns:
        Success response with deletion details
    """
    try:
        from database import db
        
        # Validate inputs
        if not node_request.node_id:
            raise HTTPException(status_code=400, detail="Node ID is required")
        
        # Convert to string and strip whitespace
        # Handle both string and numeric IDs
        node_id_str = str(node_request.node_id).strip()
        
        if not node_id_str or node_id_str.lower() in ['none', 'null', 'undefined', '']:
            raise HTTPException(status_code=400, detail="Node ID is required and must be valid")
        
        logger.info(f"[BACKEND] Deleting node with ID: {node_id_str} (type: {type(node_request.node_id)})")
        
        # First, try to find the node to see what properties it has
        # This helps with debugging and ensures we match correctly
        find_query = """
        MATCH (n)
        WHERE n.gid = $node_id 
           OR toString(n.gid) = $node_id
           OR (toFloat($node_id) IS NOT NULL AND n.gid = toFloat($node_id))
           OR (toInteger($node_id) IS NOT NULL AND n.gid = toInteger($node_id))
           OR toString(id(n)) = $node_id
           OR (toFloat($node_id) IS NOT NULL AND id(n) = toInteger(toFloat($node_id)))
        RETURN n, id(n) as internal_id, n.gid as gid_value, toString(n.gid) as gid_string, labels(n) as node_labels
        LIMIT 1
        """
        
        find_params = {"node_id": node_id_str}
        
        logger.info(f"[BACKEND] Finding node with query: {find_query}")
        logger.info(f"[BACKEND] Find parameters: {find_params}")
        
        # Try to find the node first
        try:
            find_results = db.execute_query(find_query, find_params)
            logger.info(f"[BACKEND] Find results: {find_results}")
            
            if find_results and len(find_results) > 0:
                node_info = find_results[0]
                logger.info(f"[BACKEND] Found node - internal_id: {node_info.get('internal_id')}, gid_value: {node_info.get('gid_value')}, gid_string: {node_info.get('gid_string')}, labels: {node_info.get('node_labels')}")
            else:
                logger.warning(f"[BACKEND] Node not found with initial query, trying alternative matching strategies")
        except Exception as find_error:
            logger.warning(f"[BACKEND] Error in find query: {find_error}, proceeding with delete query")
        
        # Build Cypher query to delete node and all its relationships
        # DETACH DELETE removes the node and all its relationships
        # Try multiple matching strategies to handle different ID formats
        # Handle cases where gid might be stored as number or string
        query = """
        MATCH (n)
        WHERE 
           n.gid = $node_id 
           OR toString(n.gid) = $node_id
           OR (toFloat($node_id) IS NOT NULL AND n.gid = toFloat($node_id))
           OR (toInteger($node_id) IS NOT NULL AND n.gid = toInteger($node_id))
           OR toString(id(n)) = $node_id
           OR (toFloat($node_id) IS NOT NULL AND id(n) = toInteger(toFloat($node_id)))
        DETACH DELETE n
        RETURN count(n) as deleted_count
        """
        
        params = {"node_id": node_id_str}
        
        logger.info(f"[BACKEND] Delete query: {query}")
        logger.info(f"[BACKEND] Delete parameters: {params}")
        
        # Execute write query
        try:
            results = db.execute_write_query(query, params)
            
            logger.info(f"[BACKEND] Delete query results: {results}")
            
            if not results or len(results) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Node with ID '{node_id_str}' not found - query returned no results"
                )
            
            deleted_count = results[0].get('deleted_count', 0)
            
            logger.info(f"[BACKEND] Deleted count: {deleted_count}")
            
            if deleted_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"Node with ID '{node_id_str}' not found or already deleted (matched 0 nodes)"
                )
            
            logger.info(f"[BACKEND] ✅ Node deleted successfully. Count: {deleted_count}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "message": f"Node with ID '{node_id_str}' and all its relationships deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as db_error:
            error_msg = str(db_error)
            logger.error(f"[BACKEND] ❌ Database error deleting node: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete node: {error_msg}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[BACKEND] ❌ Error deleting node: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting node: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Check if port is already in use
    def is_port_in_use(host: str, port: int) -> bool:
        """Check if a port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except OSError:
                return True
    
    # Check port availability
    if is_port_in_use(Config.BACKEND_HOST, Config.BACKEND_PORT):
        logger.error(
            f"Port {Config.BACKEND_PORT} is already in use. "
            f"Please stop the existing server or change BACKEND_PORT in your .env file."
        )
        print(f"\n{'='*60}")
        print(f"ERROR: Port {Config.BACKEND_PORT} is already in use!")
        print(f"{'='*60}")
        print(f"Please do one of the following:")
        print(f"1. Stop the existing server using port {Config.BACKEND_PORT}")
        print(f"2. Change BACKEND_PORT in your .env file to a different port")
        print(f"3. Kill the process using: netstat -ano | findstr :{Config.BACKEND_PORT}")
        print(f"{'='*60}\n")
        exit(1)
    
    try:
        logger.info(f"Starting server on {Config.BACKEND_HOST}:{Config.BACKEND_PORT}")
        uvicorn.run(
            "main:app",
            host=Config.BACKEND_HOST,
            port=Config.BACKEND_PORT,
            reload=False,  # Use run.py for development with auto-reload
            log_level="info"
        )
    except OSError as e:
        if "10048" in str(e) or "address already in use" in str(e).lower():
            logger.error(f"Port {Config.BACKEND_PORT} is already in use: {e}")
            print(f"\n{'='*60}")
            print(f"ERROR: Port {Config.BACKEND_PORT} is already in use!")
            print(f"{'='*60}")
            print(f"Please stop the existing server or change BACKEND_PORT in your .env file.")
            print(f"{'='*60}\n")
        else:
            logger.error(f"Failed to start server: {e}")
            raise
    except Exception as e:
        logger.error(f"Unexpected error starting server: {e}")
        raise
