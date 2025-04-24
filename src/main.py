from fastapi import FastAPI # type:ignore
from fastapi.middleware.cors import CORSMiddleware # type:ignore
from loader import load_data
from algorithms import Graph, dijsktra_shortest_path
import os 

app = FastAPI()

# Allow CORS for all domains (you can restrict this if you need to)
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],  # Allows all origins (use specific URLs in production)
   allow_credentials=True,
   allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
   allow_headers=["*"],  # Allows all headers
)

# loads the data into the app instances that is going to be used in later sections
@app.on_event("startup")
async def startup_event() -> None:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "src", "all_data.json")
    data = load_data(data_path)

	# loading nodes and edges in app.state
    app.state.graph_data = data 
    app.state.nodes = data["nodes"]
    app.state.edges = data["edges"]

# cleaning up edges
# removing all the edge's color and size that are present in edges
def clean_up_graph_edges() -> None:
    for edge in app.state.edges: 
        keys = edge.keys()
        if "color" in keys:
            del edge["color"]

        if "size" in keys:
            del edge["size"] 

@app.get("/")
def home_page() -> dict:
    # making a graph object and adding all the edges in this graph
    app.state.g = Graph() 
    for edge in app.state.edges:
        app.state.g.add_edge(edge["pointA"], edge["pointB"], edge["distance"], edge["street"])

    # returning data to frontend that will be used to render graph
    return {"graph": app.state.graph_data} 

# starting and destination 
@app.post("/route/{starting}/{destination}")
async def shortest_path(starting: str, destination: str) -> dict: 
    # cleaning up the graph before adding another one.
    clean_up_graph_edges()

    # searching for node 
    for node_id, value in app.state.nodes.items(): #type:ignore
        if value["label"].lower() == starting.lower():
            starting_node = int(node_id)
        
        if value["label"].lower() == destination.lower():
            destination_node = int(node_id)


    # using dijstra algorithm start is starting node that user provided
    distances, paths = dijsktra_shortest_path(app.state.g.get_graph(), starting_node) #type:ignore
    
	# trying to add the color and size in the edges 
    # brute force O(E)
    for edge in app.state.edges:  #type:ignore
        if edge["pointA"] in paths[destination_node] and edge["pointB"] in paths[destination_node]:
            edge["color"] = "blue"
            edge["size"] = 5

    # returning data to frontend for rendering graph
    return {
        "graph": app.state.graph_data,
        "distance": distances,
        "paths": paths[destination_node]
    } 
        