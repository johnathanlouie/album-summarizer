/* global Promise */

/**
 * Reads a single text file.
 * @param {String} id - ID of a file type input element
 * @returns {Promise} File contents
 */
function readFile(id) {
    const file = document.getElementById(id).files[0];
    const reader = new FileReader();
    return new Promise((resolve, reject) => {
        reader.onload = (event) => resolve(event.target.result);
        reader.onerror = reject;
        reader.readAsText(file);
    });
}

function readFiles(...ids) {
    const promises = [];
    for (let i of ids) {
        promises.push(readFile(i));
    }
    return Promise.all(promises);
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

jQuery.fn.extend({
    number: function () {
        return Number(this.val());
    }
});