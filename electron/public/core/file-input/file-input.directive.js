function fileInputFn($parse) {
    return {
        restrict: 'A',
        link(scope, element, attrs) {
            element.on('change', function (event) {
                $parse(attrs.fileInput).assign(scope, element.prop('files'));
                scope.$apply();
            });
        },
    };
}

fileInputFn.$inject = ['$parse'];


export default fileInputFn;
