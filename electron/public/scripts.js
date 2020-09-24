class LwdFilesReader {
    constructor() {
        this.fileInputIds = Array.from(arguments);
    }

    /**
     * For internal use only.
     * @param {type} fileId
     * @param {type} callback
     * @returns {undefined}
     */
    static readFile(fileId, callback) {
        let f = $(fileId).prop("files")[0];
        let fr = new FileReader();
        fr.onload = callback;
        fr.readAsText(f);
    }

    /**
     * For internal use only.
     * @param {type} arr
     * @returns {Boolean}
     */
    isLoaded(arr) {
        for (let i = 0; i < this.fileInputIds.length; i++) {
            if (!Array.isArray(arr[i])) {
                return false;
            }
        }
        return true;
    }

    /**
     * Checks if every array has the same length. For internal use only.
     * @param {string[][]} arr - An array of arrays.
     * @returns {boolean} True if all equal.
     */
    static sameLength(arr) {
        return arr.every((val, i, arr) => val.length === arr[0].length);
    }

    read(callback) {
        let data = [];
        let self = this;
        for (let i in this.fileInputIds) {
            function onLoad(e) {
                data[i] = e.target.result.split("\n");
                if (!self.isLoaded(data)) {
                    // multiple file inputs trigger this block
                } else if (!self.constructor.sameLength(data)) {
                    throw "Array lengths are not equal.";
                } else {
                    callback(data);
                }
            }
            this.constructor.readFile(this.fileInputIds[i], onLoad);
        }
    }
}

/**
 * Shuffles array in place.
 * @param {Array} a items An array containing the items.
 */
function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

function nArray(n) {
    let arr = [];
    for (let i = 0; i < n; i++) {
        arr[i] = i;
    }
    return arr;
}