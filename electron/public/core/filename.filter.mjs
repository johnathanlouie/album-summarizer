const path = require('path');


function f(url) { return path.basename(url); }


function filter() { return f; }


export default filter;
