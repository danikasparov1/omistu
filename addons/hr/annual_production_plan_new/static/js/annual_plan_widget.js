odoo.define('annual_plan.purchase_widget', function (require) {
    "use strict";
    
    var FieldChar = require('web.basic_fields').FieldChar;
    var fieldRegistry = require('web.field_registry');
    
    var AnnualPlanInfoWidget = FieldChar.extend({
        template: 'AnnualPlanInfoWidget',
        events: _.extend({}, FieldChar.prototype.events, {
            'click .o_annual_plan_info': '_onClickAnnualPlan',
        }),
    
        init: function () {
            this._super.apply(this, arguments);
            this.annualPlanInfo = this.nodeOptions.annual_plan_info || false;
        },
    
        _render: function () {
            if (this.annualPlanInfo) {
                var product = this.recordData.product_id;
                if (product && product.data) {
                    this.$el.html(
                        `<div class="o_annual_plan_info" title="${product.data.annual_plan_info}">
                            <small>${product.data.annual_plan_info}</small>
                        </div>`
                    );
                }
            } else {
                this._super();
            }
        },
    
        _onClickAnnualPlan: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.do_action({
                type: 'ir.actions.act_window',
                name: 'Annual Production Plans',
                res_model: 'annual.production.plan',
                views: [[false, 'tree'], [false, 'form']],
                domain: [['product_id', '=', this.recordData.product_id.data.id]],
            });
        },
    });
    
    fieldRegistry.add('annual_plan_info', AnnualPlanInfoWidget);
    
    return {
        AnnualPlanInfoWidget: AnnualPlanInfoWidget,
    };
    
    });