
function drawTriangle(parent, size) {
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(size, size);
            canvas.parent(parent);
            sketch.background(255);
            let c = sketch.color(sketch.random(255), sketch.random(255), sketch.random(255));

            sketch.fill(c);
            let x1 = 2;
            let y1 = 50;
            let x2, y2, x3, y3;
            let minDistance = 30;
          
            do {
              x2 = x1 + sketch.random(50, 100);
              y2 = y1 + sketch.random(-50, 50);
            } while (sketch.dist(x1, y1, x2, y2) < minDistance);
          
            do {
              x3 = x1 + sketch.random(50, 100);
              y3 = y1 + sketch.random(-50, 50);
            } while (pointLineDistance(sketch, x3, y3, x1, y1, x2, y2) < minDistance);
          
            sketch.triangle(x1, y1, x2, y2, x3, y3);
        }}
        new p5(s);
  }
  
  function drawRectangle(parent, size) {
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(size, size);
            canvas.parent(parent);
            sketch.background(255);
            let c = sketch.color(sketch.random(255), sketch.random(255), sketch.random(255));

            sketch.fill(c);
            let w = 0
            let h = 0
            do{
                w = sketch.random(30, 70);
                h = sketch.random(30, 70)
            }while(sketch.abs(w-h)<10)
            let x = size/2 - w/2;
            let y = size/2 - h/2;
            sketch.rect(x, y, w, h);
        }}
        new p5(s);
  }
  
  function drawQuadrangle(parent, size) {
    
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(size, size);
            canvas.parent(parent);
            sketch.background(255);
            let c = sketch.color(sketch.random(255), sketch.random(255), sketch.random(255));

            sketch.fill(c);
        
            let points = [];
            let minDistance = 30;
            let maxSize = 80;  // Maximum size for the quadrangle
        
            let startX = 5;
            let startY = 5;
        
            while (points.length < 4) {
            let x = startX + sketch.random(maxSize);
            let y = startY + sketch.random(maxSize);
            let valid = true;
            for (let i = 0; i < points.length; i++) {
                if (sketch.dist(x, y, points[i].x, points[i].y) < minDistance) {
                valid = false;
                break;
                }
            }
            if (valid) {
                points.push(sketch.createVector(x, y));
            }
            }
        
            points = sortPoints(sketch, points);
        
            sketch.beginShape();
            for (let i = 0; i < points.length; i++) {
                sketch.vertex(points[i].x, points[i].y);
            }
            sketch.endShape(sketch.CLOSE);
        }}
        new p5(s);
  }


  
  function drawPentagon(parent, size) {
    
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(size, size);
            canvas.parent(parent);
            sketch.background(255);
            let c = sketch.color(sketch.random(255), sketch.random(255), sketch.random(255));

    
            sketch.fill(c);
            let x = 40;
            let y = 40;
            let radius = sketch.random(20, 40);
            sketch.beginShape();
            for (let i = 0; i < 5; i++) {
            let angle = sketch.TWO_PI / 5 * i - sketch.HALF_PI;
            let xOffset = sketch.cos(angle) * radius + sketch.random(-10, 10);
            let yOffset = sketch.sin(angle) * radius + sketch.random(-10, 10);
            sketch.vertex(x + xOffset, y + yOffset);
            }
            sketch.endShape(sketch.CLOSE);
        }}
        new p5(s);
  }
  

  function drawCircle(parent, size) {

    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(size, size);
            canvas.parent(parent);
            sketch.background(255);
            let c = sketch.color(sketch.random(255), sketch.random(255), sketch.random(255));


            sketch.fill(c);
            
            let diameter = sketch.random(30, 70);
            let x = size/2
            let y = size/2
            sketch.ellipse(x, y, diameter, diameter);

        }}
        new p5(s); 
  }
  
  function drawEllipse(parent, size) {
    var s = function( sketch ) {
        sketch.setup = function() {
            canvas = sketch.createCanvas(size, size);
            canvas.parent(parent);
            sketch.background(255);
            let c = sketch.color(sketch.random(255), sketch.random(255), sketch.random(255));

            sketch.fill(c);
            let x = size/2;
            let y = size/2;
            let w = sketch.random(30, 60);
            let sign = Math.random() < 0.5 ? -1 : 1;
            let h = w + sketch.random(20,30) * sign;
            sketch.ellipse(x, y, w, h);

        }}
        new p5(s); 
  }
  

  
  // Function to sort points in a consistent order (counter-clockwise)
  function sortPoints(sketch, points) {
    let center = sketch.createVector(0, 0);
    for (let i = 0; i < points.length; i++) {
      center.add(points[i]);
    }
    center.div(points.length);
  
    points.sort((a, b) => {
      let angleA = sketch.atan2(a.y - center.y, a.x - center.x);
      let angleB = sketch.atan2(b.y - center.y, b.x - center.x);
      return angleA - angleB;
    });
  
    return points;
  }
  
  // Function to calculate the distance from a point to a line defined by two other points
  function pointLineDistance(sketch, px, py, x1, y1, x2, y2) {
    return sketch.abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / sketch.dist(x1, y1, x2, y2);
  }
  
  
  