const path = require('path');


function filterFn() { return url => path.basename(url); }


export default filterFn;
