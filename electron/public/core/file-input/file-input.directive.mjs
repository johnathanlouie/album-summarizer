function fileInput($parse) {
    return {
        restrict: 'A',
        link(scope, element, attrs) {
            function onChange(event) {
                $parse(attrs.fileInput).assign(scope, element.prop('files'));
                scope.$apply();
            }

            element.on('change', onChange);
        },
    };
}

fileInput.$inject = ['$parse'];


export default fileInput;
