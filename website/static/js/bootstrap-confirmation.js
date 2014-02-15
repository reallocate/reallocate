/* ========================================================================
 * bootstrap3-confirmation.js v1.0.1
 * Adaptation of bootstrap-confirmation.js 
 * from Nimit Suwannagate <ethaizone@hotmail.com>
 * http://ethaizone.github.io/Bootstrap-Confirmation/
 * ========================================================================
 * Copyright 2013 Thomas Jacquart <thomas.jacquart@gmail.com>.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ======================================================================== */


+function ($) { "use strict";

	// COMFIRMATION PUBLIC CLASS DEFINITION
	// ===============================

	//var for check event at body can have only one.
	var event_body = false;

  	var Confirmation = function (element, options) {

    	var that = this;

	    // remove href attribute of button
	    $(element).removeAttr('href')

	    this.init('confirmation', element, options)

	    $(element).on('show.bs.confirmation', function(e) {
			var options = that.options;
	      	var all = options.all_selector;
	      	if (options.singleton) {
	        	$(all).not(that.$element).confirmation('hide');
	      	}
	    });

	    $(element).on('shown.bs.confirmation', function(e) {
	    	var options = that.options;
	    	var all = options.all_selector;
	      	$(this).next('.popover').on('click.dismiss.confirmation', '[data-dismiss="confirmation"]', $.proxy(that.hide, that))
	      	if (that.isPopout()) {
	    		if (!event_body) {
	      			event_body = $('html').on('click', function (e) {
	        			if ($(all).is(e.target)) return;
	        			if ($(all).next('div').has(e.target).length) return;

	        			$(all).confirmation('hide');
	        			$('html').unbind(e);
	        			event_body = false;

	        			return;
	      			});
	    		}
	      	}
	    });
	}

	if (!$.fn.tooltip) throw new Error('Confirmation requires popover.js and tooltip.js')

  	Confirmation.DEFAULTS = $.extend({} , $.fn.popover.Constructor.DEFAULTS, {

	    placement: 'top'
	    , trigger: 'click'
	    , target : '_self'
	    , href   : '#'
	    , title: 'Are you sure?'
	    , template: '<div class="popover">' +
	            '<div class="arrow"></div>' +
	            '<h3 class="popover-title"></h3>' +
	            '<div class="popover-content text-center">' +
	            '<div class="input-group">' +
	            '<a class="btn btn-xs" href="" target=""></a>&nbsp;&nbsp;' +
	            '<a class="btn btn-xs" data-dismiss="confirmation"></a>' +
	            '</div>' +
	            '</div>' +
	            '</div>'
	    , btnOkClass:  'btn-primary'
	    , btnCancelClass:  'btn-default'
	    , btnOkLabel: '<i class="glyphicon glyphicon-ok"></i>&nbsp;&nbsp;Yes'
	    , btnCancelLabel: '<i class="glyphicon glyphicon-remove"></i>&nbsp;&nbsp;No'
	    , singleton: true
	    , popout: true
	    , onConfirm: function(){}
	    , onCancel: function(){}
  	})


  	// NOTE: CONFIRMATION EXTENDS popover.js
  	// ================================

  	Confirmation.prototype = $.extend({}, $.fn.popover.Constructor.prototype)

  	Confirmation.prototype.constructor = Confirmation

  	Confirmation.prototype.getDefaults = function () {
    	return Confirmation.DEFAULTS
  	}

  	Confirmation.prototype.setContent = function () {

    	var $tip = this.tip()
    	var title = this.getTitle()
	    var href = this.getHref()
	    var target = this.getTarget()
	    var $e = this.$element
	    var btnOkClass = this.getBtnOkClass()
	    var btnCancelClass = this.getBtnCancelClass()
	    var btnOkLabel = this.getBtnOkLabel()
	    var btnCancelLabel = this.getBtnCancelLabel()
	    var o = this.options

    	$tip.find('.popover-title').text(title);

    	var btnOk = $tip.find('.popover-content > div > a:not([data-dismiss="confirmation"])');
    	var btnCancel = $tip.find('.popover-content > div > a[data-dismiss="confirmation"]');

    	btnOk.addClass(btnOkClass).html(btnOkLabel).attr('href', href).attr('target', target).on('click', o.onConfirm);
    	btnCancel.addClass(btnCancelClass).html(btnCancelLabel).on('click', o.onCancel);

    	$tip.removeClass('fade top bottom left right in')

	    // IE8 doesn't accept hiding via the `:empty` pseudo selector, we have to do
	    // this manually by checking the contents.
	    if (!$tip.find('.popover-title').html()) $tip.find('.popover-title').hide()

		//var $tip    = this.tip()
		//var title   = this.getTitle()
		//var content = this.getContent()
		//
		//$tip.find('.popover-title')[this.options.html ? 'html' : 'text'](title)
		//$tip.find('.popover-content')[this.options.html ? 'html' : 'text'](content)
		//
		//$tip.removeClass('fade top bottom left right in')
  	}

  	Confirmation.prototype.isPopout = function () {

	    var popout, $e = this.$element, o = this.options

    	popout = $e.attr('data-popout') || (typeof o.popout == 'function' ? o.popout.call($e[0]) :  o.popout)

    	if (popout == 'false') popout = false;

    	return popout
  	}

  	Confirmation.prototype.getHref = function () {

    	var href, $e = this.$element, o = this.options

    	href = $e.attr('data-href') || (typeof o.href == 'function' ? o.href.call($e[0]) :  o.href)

    	return href
  	}

  	Confirmation.prototype.getTarget = function () {

    	var target, $e = this.$element, o = this.options

    	target = $e.attr('data-target') || (typeof o.target == 'function' ? o.target.call($e[0]) :  o.target)

    	return target
  	}

  	Confirmation.prototype.getBtnOkClass = function () {
    
    	var btnOkClass, $e = this.$element, o = this.options

    	btnOkClass = $e.attr('data-btnOkClass') || (typeof o.btnOkClass == 'function' ? o.btnOkClass.call($e[0]) :  o.btnOkClass)

    	return btnOkClass
  	}

  	Confirmation.prototype.getBtnCancelClass = function () {

    	var btnCancelClass, $e = this.$element, o = this.options

    	btnCancelClass = $e.attr('data-btnCancelClass') || (typeof o.btnCancelClass == 'function' ? o.btnCancelClass.call($e[0]) :  o.btnCancelClass)

    	return btnCancelClass
  	}

  	Confirmation.prototype.getBtnOkLabel = function () {

    	var btnOkLabel, $e = this.$element, o = this.options

    	btnOkLabel = $e.attr('data-btnOkLabel') || (typeof o.btnOkLabel == 'function' ? o.btnOkLabel.call($e[0]) :  o.btnOkLabel)

    	return btnOkLabel
  	}

  	Confirmation.prototype.getBtnCancelLabel = function () {
    
    	var btnCancelLabel, $e = this.$element, o = this.options

    	btnCancelLabel = $e.attr('data-btnCancelLabel') || (typeof o.btnCancelLabel == 'function' ? o.btnCancelLabel.call($e[0]) :  o.btnCancelLabel)

    	return btnCancelLabel
  	}

  	Confirmation.prototype.tip = function () {
    
    	if (!this.$tip) this.$tip = $(this.options.template)

    	return this.$tip
  	}


	// Confirmation PLUGIN DEFINITION

  	var old = $.fn.confirmation

  	$.fn.confirmation = function (option) {

    	var that = this

    	return this.each(function () {

      		var $this   = $(this);
      		var data    = $this.data('bs.confirmation');
      		var options = typeof option == 'object' && option;
      		options = options || {};
      		options.all_selector = that.selector;

      		if (!data) $this.data('bs.confirmation', (data = new Confirmation(this, options)));
      		if (typeof option == 'string') data[option]();
    	});
  	}

  	$.fn.confirmation.Constructor = Confirmation;

  	// CONFIRMATION NO CONFLICT

  	$.fn.confirmation.noConflict = function () {

    	$.fn.confirmation = old;

    	return this;
  	}

}(jQuery);