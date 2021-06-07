import NullableInputController from './nullable-input.controller.js';


const componentDef = {
    templateUrl: 'components/nullable-input/nullable-input.template.html',
    controller: NullableInputController,
    require: {
        ngModelController: '?ngModel',
    },
};


export default componentDef;
