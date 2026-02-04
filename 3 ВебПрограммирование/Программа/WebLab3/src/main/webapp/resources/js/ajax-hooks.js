'use strict';

let jsfHooksRegistered = false;

function setupJsfAjaxHooks() {
    if (jsfHooksRegistered) return;
    if (typeof jsf === 'undefined' || !jsf.ajax) return;

    jsfHooksRegistered = true;

    jsf.ajax.addOnError(function(data) {
        if (window.console && console.error) {
            console.error("JSF AJAX error", data);
        }
    });

    jsf.ajax.addOnEvent(function(data) {
        if (data.status === 'success') {
            setTimeout(function() {
                initializePage();
                attachObserver();
            }, 50);
        }
    });
}
