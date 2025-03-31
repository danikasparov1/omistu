odoo.define('quality.confirmation', function (require) {
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    
    var confirmTest = function() {
        // Call the server method to proceed to next step
        var self = this;
        self._rpc({
            model: 'quality.product.test',
            method: 'proceed_to_next_step_with_confirmation',
            args: [],
        }).then(function(result){
            self.do_notify('Success', 'The production has passed the test and moved to the next step.');
        });
    };

    var cancelTest = function() {
        // Close dialog or handle cancellation
        console.log('Test stage transition cancelled');
    };

    return {
        show: function() {
            Dialog.confirm(this, 'Are you sure you want to pass this stage and proceed to the next step?', {
                confirm_callback: confirmTest,
                cancel_callback: cancelTest,
            });
        }
    }
});
