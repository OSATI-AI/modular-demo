/* 
*** Function Description Start ***
Description: 
The draw_fraction function uses p5.js to draw different shapes (rectangle, circle, bar) divided into any specified number of equal parts. It highlights a specified number of these parts to visually represent a fraction. For example, draw a chocolate bar with 8 pieces, and highlight 3 of them to represent the fraction 3/8, or draw a circle divided into 4 parts and color 1 to represent the fraction 1/4. The function takes as input the shape type, total number of parts, and number of highlighted parts.
How to use:
1. Call the draw_fraction function with the container ID, shape type, total parts, and highlighted parts.
Example:
draw_fraction('container', 'rectangle', 8, 3);
*** Function Description End ***
*/
function drawRectangle(sketch, totalParts, highlightedParts) {
    sketch.background(255);
    let cols = Math.ceil(Math.sqrt(totalParts));
    let rows = Math.ceil(totalParts / cols);
    let cellWidth = sketch.width / cols;
    let cellHeight = sketch.height / rows;

    for (let i = 0; i < totalParts; i++) {
        let col = i % cols;
        let row = Math.floor(i / cols);
        sketch.fill(i < highlightedParts ? 'orange' : 'white');
        sketch.stroke(0);
        sketch.rect(col * cellWidth, row * cellHeight, cellWidth, cellHeight);
    }
}

function drawCircle(sketch, totalParts, highlightedParts) {
    sketch.background(255);
    let angle = sketch.TWO_PI / totalParts;
    let radius = Math.min(sketch.width, sketch.height) / 2;

    sketch.translate(sketch.width / 2, sketch.height / 2);
    for (let i = 0; i < totalParts; i++) {
        sketch.fill(i < highlightedParts ? 'orange' : 'white');
        sketch.stroke(0);
        sketch.beginShape();
        sketch.vertex(0,0);
        for (let a = i * angle; a <= (i + 1) * angle; a += 0.01) {
            sketch.vertex(radius * sketch.cos(a), radius * sketch.sin(a));
        }
        sketch.vertex(0, 0);
        sketch.endShape(sketch.CLOSE);
    }
}

function drawBar(sketch, totalParts, highlightedParts) {
    sketch.background(255);
    let barWidth = sketch.width / totalParts;
    let barHeight = sketch.height / 2;

    for (let i = 0; i < totalParts; i++) {
        sketch.fill(i < highlightedParts ? 'orange' : 'white');
        sketch.stroke(0);
        sketch.rect(i * barWidth, (sketch.height - barHeight) / 2, barWidth, barHeight);
    }
}

function draw_fraction(container, shape, totalParts, highlightedParts) {
    document.getElementById(container).innerHTML = "";
    var s = function (sketch) {
        sketch.setup = function () {
            let canvas = sketch.createCanvas(400, 400);
            canvas.parent(container);
            sketch.noLoop(); // Disable draw loop since we are drawing a static image

            if (shape === 'rectangle') {
                drawRectangle(sketch, totalParts, highlightedParts);
            } else if (shape === 'circle') {
                drawCircle(sketch, totalParts, highlightedParts);
            } else if (shape === 'bar') {
                drawBar(sketch, totalParts, highlightedParts);
            }
        };
    };
    new p5(s);
}