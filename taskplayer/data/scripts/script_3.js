/* 
*** Function Description Start ***
Description: 
The plot_triangle function uses p5.js to draw a right-angled triangle with sides labeled A, B, and C. The right angle is explicitly shown, and the sides are clearly labeled.

How to use:
1. Call the plot_triangle function with the container ID where you want to draw the triangle.

Example:
plot_triangle('container');
*** Function Description End ***
*/
function plot_triangle(container){
    document.getElementById(container).innerHTML = ""
    var s = function( sketch ) {
        sketch.setup = function() {
            let canvas = sketch.createCanvas(400, 400);
            canvas.parent(container);
            sketch.background(255);
            sketch.stroke(0);
            sketch.strokeWeight(2);
            sketch.fill(255);
            sketch.triangle(100, 300, 300, 300, 100, 100);

            // Label vertices
            sketch.fill(0);
            sketch.textSize(16);
            sketch.text('A', 90, 315);
            sketch.text('B', 310, 315);
            sketch.text('C', 90, 95);

            // Label sides
            sketch.text('a', 200, 320);
            sketch.text('b', 70, 200);
            sketch.text('c', 210, 200);

            // Indicate the right angle
            sketch.noFill();
            sketch.stroke(0);
            sketch.strokeWeight(1);
            sketch.rect(95, 295, 10, 10);
        };
    };

    new p5(s);
};