'use strict';

class History {
    #history = [];
    #future = [];
    #current = undefined;

    get hasBack() { return this.#history.length === 0; }
    get hasNext() { return this.#future.length === 0; }
    get current() { return this.#current; }

    push(dir) {
        dir = path.normalize(dir);
        if (this.#current !== dir) {
            this.#future = [];
            if (this.#current !== undefined) { this.#history.push(this.#current); }
            this.#current = dir;
        }
        return this.#current;
    }

    goBack() {
        this.#future.push(this.#current);
        this.#current = this.#history.pop();
        return this.#current;
    }

    goForward() {
        this.#history.push(this.#current);
        this.#current = this.#future.pop();
        return this.#current;
    }
}

angular.module('services').factory('History', History);
