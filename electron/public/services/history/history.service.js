'use strict';

const history = {
  _history: [],
  _future: [],
  _current: undefined,
  get hasBack() { return this._history.length === 0; },
  get hasNext() { return this._future.length === 0; },
  get current() { return this._current; },

  push(dir) {
    dir = path.normalize(dir);
    if (this._current !== dir) {
      this._future = [];
      if (this._current !== undefined) { this._history.push(this._current); }
      this._current = dir;
    }
    return this._current;
  },

  goBack() {
    this._future.push(this._current);
    this._current = this._history.pop();
    return this._current;
  },

  goForward() {
    this._history.push(this._current);
    this._current = this._future.pop();
    return this._current;
  }
};

angular.module('services').factory('History', () => history);
