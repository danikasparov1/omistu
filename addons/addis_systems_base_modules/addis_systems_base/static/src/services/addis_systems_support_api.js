/** @odoo-module **/

import { Notification } from "@mail/core/common/notification_model";
import { Transition } from "@web/core/transition";
// const { Component, onWillStart, onMounted } = owl

import { Component, xml, useState, onMounted , onWillStart} from "@odoo/owl";

export class MyComponent extends Component {
    setup() {
        console.log()
        const { myValue, incrementValue, decrementValue } = this.useMyCustomLogic(0); // Initial value
      
        // Use the returned values and functions in your component
        return {
          myValue,
          incrementValue,
          decrementValue,
        };
      }
  
    useMyCustomLogic(initialValue) {
      const [myValue, setMyValue] = useState(initialValue);
  
      // Logic specific to your custom hook
      const incrementValue = () => setMyValue(myValue + 1);
      const decrementValue = () => setMyValue(myValue - 1);
  
      return { myValue, incrementValue, decrementValue };
    }
  }