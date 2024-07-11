/* 
*** Function Description Start ***
Description: 
The plot_graph function uses p5.js to plot any arbitrary mathematical function. It takes in the x and y range in which the function should be displayed and a callback function to determine the function term for the graph.

How to use:
1. Define a mathematical function as a callback.
2. Call the plot_graph function with the container ID, the callback function, and the x and y ranges.

Example:
function quadraticFunction(x) {
    return x * x;
}

plot_graph('container', quadraticFunction, [-10, 10], [-10, 100]);
*** Function Description End ***
*/

function drawGrid(sketch, xRange, yRange) {
    sketch.stroke(200); // Light grey color for grid lines
    sketch.strokeWeight(1);

    // Draw vertical grid lines
    for (let x = 0; x < sketch.width; x += sketch.width / (xRange[1] - xRange[0])) {
        sketch.line(x, 0, x, sketch.height);
    }

    // Draw horizontal grid lines
    for (let y = 0; y < sketch.height; y += sketch.height / (yRange[1] - yRange[0])) {
        sketch.line(0, y, sketch.width, y);
    }
}

function drawAxes(sketch) {
    sketch.stroke(0); // Black color for axes
    sketch.strokeWeight(3);
    // Draw X axis
    sketch.line(0, sketch.height / 2, sketch.width, sketch.height / 2);
    // Draw Y axis
    sketch.line(sketch.width / 2, 0, sketch.width / 2, sketch.height);
}

function drawFunction(sketch, func, xRange, yRange) {
    sketch.stroke(255, 0, 0); // Red color for the function line
    sketch.strokeWeight(2);
    sketch.noFill();
    sketch.beginShape();
    for (let x = xRange[0]; x <= xRange[1]; x += 0.1) {
        let y = func(x);
        let canvasX = sketch.map(x, xRange[0], xRange[1], 0, sketch.width);
        let canvasY = sketch.map(y, yRange[0], yRange[1], sketch.height, 0);
        sketch.vertex(canvasX, canvasY);
    }
    sketch.endShape();
}

function plot_graph(container, func, xRange, yRange){
    document.getElementById(container).innerHTML = ""
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(400, 400);
            canvas.parent(container);
            sketch.background(255);
            drawGrid(sketch, xRange, yRange);
            drawAxes(sketch);
            drawFunction(sketch, func, xRange, yRange);
        };
      };

    new p5(s);
};
