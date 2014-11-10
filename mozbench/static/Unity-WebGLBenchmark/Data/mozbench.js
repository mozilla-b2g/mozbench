var tests = [{
  benchmark: 'Mandelbrot GPU',
  result: -1
}];

function processText(text) {
  if (text.length < 50) {
    var test = text.split(':');            
    if (test.length > 0) {
      if (test[0] === 'Overall') {
        tests.push({
          benchmark: 'Overall',
          result: test[1]
        });

        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open("POST", "/results", true);
        xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlHttp.send("results=" + JSON.stringify(tests));
        return;
      }

      for (var i = 0 ; i < tests.length; i++) {
        if (test[0] === tests[i].benchmark) {
          tests[i].result = test[1];
          break;        
        }
      }
    }
  }
}