class FileInput {

    #parse;
    restrict = 'A';

    static $inject = ['$parse'];
    constructor($parse) {
        this.#parse = $parse;
    }

    link(scope, element, attrs) {
        element.on('change', () => {
            this.#parse(attrs.fileInput).assign(scope, element.prop('files'));
            scope.$apply();
        });
    }

}


export default FileInput;
