jQuery.fn.extend({
    number(value) {
        if (value === undefined) {
            return Number(this.val());
        } else {
            return this.val(value);
        }
    },
    readText() {
        const fileList = this.prop('files');
        const promises = [];
        for (let file of fileList) {
            promises.push(new Promise((resolve, reject) => {
                let reader = new FileReader();
                reader.onload = (event) => resolve(event.target.result);
                reader.onerror = reject;
                reader.readAsText(file);
            }));
        }
        return Promise.all(promises);
    }
});