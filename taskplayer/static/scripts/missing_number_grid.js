
function plot_missing_number_grid(missing_number, container){
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(400, 400);
            canvas.parent(container);
            sketch.background(255);

            let cols = 10;
            let rows = 10;
            let cellWidth = sketch.width / cols;
            let cellHeight = sketch.height / rows;
            let currentNumber = 1;
        
            sketch.textSize(16);
            sketch.textAlign(sketch.CENTER, sketch.CENTER);
            sketch.stroke(0);
            sketch.noFill();
        
            for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                let xPos = x * cellWidth;
                let yPos = y * cellHeight;
        
                if (currentNumber !== missing_number) {
                    sketch.fill(0);
                    sketch.text(currentNumber, xPos + cellWidth / 2, yPos + cellHeight / 2);
                } else {
                    sketch.fill(255); // Make the blank cell fill white so it appears blank
                }
        
                sketch.stroke(0);
                sketch.noFill();
                sketch.rect(xPos, yPos, cellWidth, cellHeight);
        
                currentNumber++;
            }
        }
    }
        
    }
    new p5(s);
}