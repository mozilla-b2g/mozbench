
var Module;
if (typeof Module === 'undefined') Module = eval('(function() { try { return Module || {} } catch(e) { return {} } })()');
if (!Module.expectedDataFileDownloads) {
  Module.expectedDataFileDownloads = 0;
  Module.finishedDataFileDownloads = 0;
}
Module.expectedDataFileDownloads++;
(function() {

    var PACKAGE_PATH;
    if (typeof window === 'object') {
      PACKAGE_PATH = window['encodeURIComponent'](window.location.pathname.toString().substring(0, window.location.pathname.toString().lastIndexOf('/')) + '/');
    } else {
      // worker
      PACKAGE_PATH = encodeURIComponent(location.pathname.toString().substring(0, location.pathname.toString().lastIndexOf('/')) + '/');
    }
    var PACKAGE_NAME = 'WebGLBenchmark.data';
    var REMOTE_PACKAGE_BASE = 'WebGLBenchmark.data';
    if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
      Module['locateFile'] = Module['locateFilePackage'];
      Module.printErr('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
    }
    var REMOTE_PACKAGE_NAME = typeof Module['locateFile'] === 'function' ?
                              Module['locateFile'](REMOTE_PACKAGE_BASE) :
                              ((Module['filePackagePrefixURL'] || '') + REMOTE_PACKAGE_BASE);
    var REMOTE_PACKAGE_SIZE = 55533664;
    var PACKAGE_UUID = '167de1d9-91f9-4c0d-8a8c-92b4b8aa2c93';
  
    function fetchRemotePackage(packageName, packageSize, callback, errback) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', packageName, true);
      xhr.responseType = 'arraybuffer';
      xhr.onprogress = function(event) {
        var url = packageName;
        var size = packageSize;
        if (event.total) size = event.total;
        if (event.loaded) {
          if (!xhr.addedTotal) {
            xhr.addedTotal = true;
            if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
            Module.dataFileDownloads[url] = {
              loaded: event.loaded,
              total: size
            };
          } else {
            Module.dataFileDownloads[url].loaded = event.loaded;
          }
          var total = 0;
          var loaded = 0;
          var num = 0;
          for (var download in Module.dataFileDownloads) {
          var data = Module.dataFileDownloads[download];
            total += data.total;
            loaded += data.loaded;
            num++;
          }
          total = Math.ceil(total * Module.expectedDataFileDownloads/num);
          if (Module['setStatus']) Module['setStatus']('Downloading data... (' + loaded + '/' + total + ')');
        } else if (!Module.dataFileDownloads) {
          if (Module['setStatus']) Module['setStatus']('Downloading data...');
        }
      };
      xhr.onload = function(event) {
        var packageData = xhr.response;
        callback(packageData);
      };
      xhr.send(null);
    };

    function handleError(error) {
      console.error('package error:', error);
    };
  
      var fetched = null, fetchedCallback = null;
      fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, function(data) {
        if (fetchedCallback) {
          fetchedCallback(data);
          fetchedCallback = null;
        } else {
          fetched = data;
        }
      }, handleError);
    
  function runWithFS() {

function assert(check, msg) {
  if (!check) throw msg + new Error().stack;
}
Module['FS_createPath']('/', 'Resources', true, true);

    function DataRequest(start, end, crunched, audio) {
      this.start = start;
      this.end = end;
      this.crunched = crunched;
      this.audio = audio;
    }
    DataRequest.prototype = {
      requests: {},
      open: function(mode, name) {
        this.name = name;
        this.requests[name] = this;
        Module['addRunDependency']('fp ' + this.name);
      },
      send: function() {},
      onload: function() {
        var byteArray = this.byteArray.subarray(this.start, this.end);

          this.finish(byteArray);

      },
      finish: function(byteArray) {
        var that = this;
        Module['FS_createPreloadedFile'](this.name, null, byteArray, true, true, function() {
          Module['removeRunDependency']('fp ' + that.name);
        }, function() {
          if (that.audio) {
            Module['removeRunDependency']('fp ' + that.name); // workaround for chromium bug 124926 (still no audio with this, but at least we don't hang)
          } else {
            Module.printErr('Preloading file ' + that.name + ' failed');
          }
        }, false, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change
        this.requests[this.name] = null;
      },
    };
      new DataRequest(0, 6792, 0, 0).open('GET', '/level0');
    new DataRequest(6792, 13676, 0, 0).open('GET', '/level1');
    new DataRequest(13676, 20316, 0, 0).open('GET', '/level10');
    new DataRequest(20316, 26956, 0, 0).open('GET', '/level11');
    new DataRequest(26956, 3078116, 0, 0).open('GET', '/level12');
    new DataRequest(3078116, 3085136, 0, 0).open('GET', '/level2');
    new DataRequest(3085136, 3092268, 0, 0).open('GET', '/level3');
    new DataRequest(3092268, 3099124, 0, 0).open('GET', '/level4');
    new DataRequest(3099124, 3106244, 0, 0).open('GET', '/level5');
    new DataRequest(3106244, 3116788, 0, 0).open('GET', '/level6');
    new DataRequest(3116788, 3126860, 0, 0).open('GET', '/level7');
    new DataRequest(3126860, 3136932, 0, 0).open('GET', '/level8');
    new DataRequest(3136932, 3147004, 0, 0).open('GET', '/level9');
    new DataRequest(3147004, 3181284, 0, 0).open('GET', '/mainData');
    new DataRequest(3181284, 7834672, 0, 0).open('GET', '/sharedassets0.assets');
    new DataRequest(7834672, 11469680, 0, 0).open('GET', '/sharedassets1.assets');
    new DataRequest(11469680, 11474624, 0, 0).open('GET', '/sharedassets10.assets');
    new DataRequest(11474624, 11791296, 0, 0).open('GET', '/sharedassets11.assets');
    new DataRequest(11791296, 11861904, 0, 0).open('GET', '/sharedassets12.assets');
    new DataRequest(11861904, 37552456, 0, 0).open('GET', '/sharedassets13.assets');
    new DataRequest(37552456, 37580804, 0, 0).open('GET', '/sharedassets2.assets');
    new DataRequest(37580804, 41779588, 0, 0).open('GET', '/sharedassets3.assets');
    new DataRequest(41779588, 41784020, 0, 0).open('GET', '/sharedassets4.assets');
    new DataRequest(41784020, 41801420, 0, 0).open('GET', '/sharedassets5.assets');
    new DataRequest(41801420, 44125980, 0, 0).open('GET', '/sharedassets6.assets');
    new DataRequest(44125980, 50350612, 0, 0).open('GET', '/sharedassets7.assets');
    new DataRequest(50350612, 53921668, 0, 0).open('GET', '/sharedassets8.assets');
    new DataRequest(53921668, 53926620, 0, 0).open('GET', '/sharedassets9.assets');
    new DataRequest(53926620, 54489300, 0, 0).open('GET', '/Resources/unity_default_resources');
    new DataRequest(54489300, 55533664, 0, 0).open('GET', '/Resources/unity_builtin_extra');

    function processPackageData(arrayBuffer) {
      Module.finishedDataFileDownloads++;
      assert(arrayBuffer, 'Loading data file failed.');
      var byteArray = new Uint8Array(arrayBuffer);
      var curr;
      
      // Reuse the bytearray from the XHR as the source for file reads.
      DataRequest.prototype.byteArray = byteArray;
          DataRequest.prototype.requests["/level0"].onload();
          DataRequest.prototype.requests["/level1"].onload();
          DataRequest.prototype.requests["/level10"].onload();
          DataRequest.prototype.requests["/level11"].onload();
          DataRequest.prototype.requests["/level12"].onload();
          DataRequest.prototype.requests["/level2"].onload();
          DataRequest.prototype.requests["/level3"].onload();
          DataRequest.prototype.requests["/level4"].onload();
          DataRequest.prototype.requests["/level5"].onload();
          DataRequest.prototype.requests["/level6"].onload();
          DataRequest.prototype.requests["/level7"].onload();
          DataRequest.prototype.requests["/level8"].onload();
          DataRequest.prototype.requests["/level9"].onload();
          DataRequest.prototype.requests["/mainData"].onload();
          DataRequest.prototype.requests["/sharedassets0.assets"].onload();
          DataRequest.prototype.requests["/sharedassets1.assets"].onload();
          DataRequest.prototype.requests["/sharedassets10.assets"].onload();
          DataRequest.prototype.requests["/sharedassets11.assets"].onload();
          DataRequest.prototype.requests["/sharedassets12.assets"].onload();
          DataRequest.prototype.requests["/sharedassets13.assets"].onload();
          DataRequest.prototype.requests["/sharedassets2.assets"].onload();
          DataRequest.prototype.requests["/sharedassets3.assets"].onload();
          DataRequest.prototype.requests["/sharedassets4.assets"].onload();
          DataRequest.prototype.requests["/sharedassets5.assets"].onload();
          DataRequest.prototype.requests["/sharedassets6.assets"].onload();
          DataRequest.prototype.requests["/sharedassets7.assets"].onload();
          DataRequest.prototype.requests["/sharedassets8.assets"].onload();
          DataRequest.prototype.requests["/sharedassets9.assets"].onload();
          DataRequest.prototype.requests["/Resources/unity_default_resources"].onload();
          DataRequest.prototype.requests["/Resources/unity_builtin_extra"].onload();
          Module['removeRunDependency']('datafile_WebGLBenchmark.data');

    };
    Module['addRunDependency']('datafile_WebGLBenchmark.data');
  
    if (!Module.preloadResults) Module.preloadResults = {};
  
      Module.preloadResults[PACKAGE_NAME] = {fromCache: false};
      if (fetched) {
        processPackageData(fetched);
        fetched = null;
      } else {
        fetchedCallback = processPackageData;
      }
    
  }
  if (Module['calledRun']) {
    runWithFS();
  } else {
    if (!Module['preRun']) Module['preRun'] = [];
    Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
  }

})();
