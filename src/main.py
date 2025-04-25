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


def color_edges(color: str, size: int, paths: dict, destination_node: int) -> None:
    # trying to add the color and size in the edges 
    # brute force O(E)
    for edge in app.state.edges:  #type:ignore
        if edge["pointA"] in paths[destination_node] and edge["pointB"] in paths[destination_node]:
            edge["color"] = color 
            edge["size"] = size 


@app.get("/")
def home_page() -> dict:
    # making a graph object and adding all the edges in this graph
    app.state.g = Graph() 
    for edge in app.state.edges:
        app.state.g.add_edge(edge["pointA"], edge["pointB"], edge["distance"], edge["street"])

    # returning data to frontend that will be used to render graph
    return {"graph": app.state.graph_data} 

# converts the user string into int nodes and returns it to the user
# also returns a bool value true if we found the value false 
# even if one of them is not in the graph
def search_node(starting: str, destination: str) -> tuple:
    startingFound = False 
    destinationFound = False 
    starting_node = None 
    destination_node = None 

     # searching for node 
    for node_id, value in app.state.nodes.items(): #type:ignore
        if value["label"].lower() == starting.lower():
            starting_node = int(node_id)
            startingFound = True 
        
        if value["label"].lower() == destination.lower():
            destination_node = int(node_id)
            destinationFound = True 
    
    return (startingFound, destinationFound, starting_node, destination_node)


# returns the shortest_path by calling dijsktra algorithm from algorithms 
def get_shorest_path(starting_node: int):
    return dijsktra_shortest_path(app.state.g.get_graph(), starting_node)


# starting and destination 
@app.post("/route/{starting}/{destination}")
async def shortest_path(starting: str, destination: str) -> dict: 
    # cleaning up the graph before adding another one.
    clean_up_graph_edges()

    # calling the search_node function
    startingFound, destinationFound, starting_node, destination_node = search_node(starting, destination)
    if not startingFound:
        return {
            "graph": app.state.graph_data,
            "message": "Starting node not found in the graph.",
            "path_found": False 
        }
    elif not destinationFound:
        return {
            "graph": app.state.graph_data,
            "message": "Destination node not found in the graph.",
            "path_found": False 
        }

    # using dijstra algorithm start is starting node that user provided
    distances, paths, streets = get_shorest_path(starting_node) #type:ignore
    
    # colors edges with a color and a size to denote the shortest path
    color_edges("blue", 5, paths, destination_node)

    # returning data to frontend for rendering graph
    return {
        "graph": app.state.graph_data,
        "path_found": True,
        "message": "Paths Found",
        "distance": distances,
        "streets": streets[destination_node]
    } 
        