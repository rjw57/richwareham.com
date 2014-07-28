var http = require('http'),
    fs = require('fs');

// List of URLs to grab
var PUB_URLS = [
    'http://publications.eng.cam.ac.uk/cgi/exportview/creators/Wareham=3ARJ=3A=3A/JSON/Wareham=3ARJ=3A=3A.js',
    'http://publications.eng.cam.ac.uk/cgi/exportview/creators/Wareham=3AR=3A=3A/JSON/Wareham=3AR=3A=3A.js',
]

var processUrls = function(urls, cb) {
  var pubs = [];
  var processEntry = function(idx) {
    if(idx >= urls.length) { return; }
    var url = urls[idx];
    console.log('GET-ing', url);
    http.get(url, function(res) {
      var json_data = '';
      res.on('data', function(chunk) { json_data += chunk; });
      res.on('end', function() {
        pubs = pubs.concat(eval(json_data));
        console.log('Got ' + pubs.length + ' publication(s)');
        if(idx+1 < PUB_URLS.length) {
          processEntry(idx+1);
        } else {
          if(cb) { cb(pubs); }
        }
      });
    });
  };

  processEntry(0);
}
// We use naked evals because the CUED database has some naked unescape-s in them :(

processUrls(PUB_URLS, function(pubs) {
  fs.writeFile('publications.json', JSON.stringify(pubs), function() {
    console.log('Wrote ' + pubs.length + ' publications');
  });
});
