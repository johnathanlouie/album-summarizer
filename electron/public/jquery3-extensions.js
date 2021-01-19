jQuery.fn.extend({
    number(value) {
        if (value === undefined) {
            return Number(this.val());
        } else {
            return this.val(value);
        }
    }
});