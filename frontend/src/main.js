import Graph from "graphology";
import Sigma from "sigma";

// form element
const form = document.getElementById("source-destination-form");

let nodes;
let edges;

function showDirections(paths) {
  const directionsList = document.getElementById('directions-list');
  directionsList.innerHTML = ''; // clear old list

  paths.forEach(step => {
    const li = document.createElement('li');
    li.textContent = step;
    directionsList.appendChild(li);
  });
}

function drawGraph() {
  // Clear the previous graph
  const container = document.getElementById("container");
  
  if (container) {
    container.innerHTML = ""; // brute-force clearing
  }

  // Create a new graph
  const graph = new Graph();

  // making the nodes in [key, value] format and loop through each one of them
  // key is an integer and value is an object
  const nodes_array = Object.entries(nodes);  
  // looping through each [key, value] format and adding it to the graph
  nodes_array.forEach(function(each_array) {
    // getting id and attributes 
    // id is an integer and attribute_object is an object
    let id = each_array[0];
    /*
      Example:
      attribute_object = {
        "label": "University Library",
        "x": 60, 
        "y": 37, 
        "size": 25, 
        "color": "#1E90FF"
      }
    */
    let attribute_object = each_array[1]; 
    
    // addNode function takes in two value 
    // first one is unique identifier and second one is object with various attributes
    // the second parameters will have label, x, y, size, color
    graph.addNode(id, {
      label: attribute_object.label,
      x: attribute_object.x,
      y: attribute_object.y,
      size: 5,
      color: attribute_object.color
    });
  })


  // Add edges to the graph
  edges.forEach(edge => {
    let keys = Object.keys(edge);
    let colorEdge = "#666";  // Default edge color
    let sizeEdge = 1; // Default edge size

    if (keys.includes("color")){
      colorEdge = edge.color;
    }

    if (keys.includes("size")) {
      sizeEdge = edge.size 
    }

    graph.addEdge(edge.pointA, edge.pointB, {
      size: sizeEdge,
      color: colorEdge, 
      label: edge.street,
      distance: edge.distance
    });
  });

  // Render the graph
  if (container) {
    new Sigma(graph, container, {
      renderEdgeLabels: true,  
      edgeLabelSize: 8,        
      edgeLabelColor: { attribute: "color" },
      defaultEdgeColor: "#666"
    });
  }
}

/* 
  When the page loads we want to call the the '/' endpoint from the backend
*/
document.addEventListener("DOMContentLoaded", async () => {
  try {
      const response = await fetch("http://localhost:8000/");

      // handling the messages here
      const data = await response.json();
      const graph = data.graph;
      nodes = graph.nodes;
      edges = graph.edges;
      drawGraph();
  }
  catch(err) {
      console.log("Error", err);
  }
})

// handles the path 
async function handlePath(starting, destination) {
  try {
    const response = await fetch(`http://localhost:8000/route/${starting}/${destination}`, {method: 'POST'});

    // handling the messages here
    const data = await response.json();
    const graph = data.graph;
    nodes = graph.nodes;
    edges = graph.edges;
    drawGraph();
    showDirections(data.paths);
  }
  catch(err) {
      console.log("Error", err);
  }
}

// Add event listener to handle form submission
form.addEventListener("submit", (event) => {
  event.preventDefault(); // Prevents the default form submission behavior

  // Get the values from the input fields
  const startingInput = form.querySelector('input[name="starting"]');
  const destinationInput = form.querySelector('input[name="destination"]');
  const startingValue = startingInput.value;
  const destinationValue = destinationInput.value;  

  // calling the function 
  handlePath(startingValue, destinationValue);
});
