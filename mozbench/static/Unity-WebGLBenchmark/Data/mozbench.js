
var benchmarks = ['Mandelbrot GPU', 'Mandelbrot Script',
  'Instantiate & Destroy', 'CryptoHash Script', 'Animation & Skinning',
  'Asteroid Field', 'Particles', 'Physics Meshes', 'Physics Cubes',
  'Physics Spheres', '2D Physics Spheres', '2D Physics Boxes', 'AI Agents'];

var results = [];

function processText(text) {
  /** 
    This function is being used with all kinds of text being sent to 'print'.
    Limit the size of texts to analyse or else we will break the benchmark.
  */
  if (text.length < 50) {

    var test = text.split(':');            
    if (test.length > 0) {
      if (test[0] === 'Overall') {
        // Add Overall result to results
        results.push({
          benchmark: 'Overall',
          result: test[1]
        });

        // Post results back to Mozbench
        postResults();
        return;
      }

      // We haven't reach the end. Let's check if we have a possibel result.
      for (var i = 0 ; i < benchmarks.length; i++) {
        if (test[0] === benchmarks[i]) {
          // Add benchmark result to results
          results.push({
            benchmark: test[0],
            result: test[1]
          });
          break;        
        }
      }
    }
  }
}

function postResults() {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("POST", "/results", true);
  xmlHttp.setRequestHeader("Content-type", 
                            "application/x-www-form-urlencoded");
  // We need to use encodeURIComponent because of the '&' in benchmark names.
  xmlHttp.send("results=" + encodeURIComponent(JSON.stringify(results)));        
}

function startBenchmark() {  
  var canvas = document.getElementById("canvas");
  var event = new Event("touchstart");
  canvas.dispatchEvent(event);
}
