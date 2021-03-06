jQuery( function($) {
$(document).ready(function(){

	function portalMessage(message){
		str = "<dl class='portalMessage error'>"+
			"<dt i18n:translate='error'>Error</dt>"+
			"<dd><ul>" + message +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}

	// a reference definition is selected from the dropdown
	// see referenceresultswidget.js
	$('#ReferenceDefinition\\:list').change(function(){
		ref_def_uid = $(this).val();

		// clear out tbody
		$('tbody.analysisservices').empty();
		// set initial so manual expansion fires
		$('tr[class~="expanded"]').removeClass("expanded").addClass("initial");

		if (ref_def_uid == '') {
			// No reference definition selected; reset widget.
			return;
		}

		$.ajax({
			url: 'get_reference_definition_info',
			dataType: 'json',
			data: {uid: ref_def_uid},
			beforeSubmit: function(formData, jqForm, options) {
				$('#ReferenceDefinition\\:list').attr('disabled',true);
			},
			success: function(responseText, statusText, xhr, $form) {
				if (responseText['results'] != undefined) {
					// Got correct values from server
					results = $.parseJSON(responseText['success']);
					// select Blank if it's specified in the definition
					if(responseText['blank']){
						$("#Blank").attr("checked", true);
					}
					if(!responseText['blank']){
						$("#Blank").attr("checked", false);
					}
					// select Hazardous the same way
					if(responseText['hazardous']){
						$("#Hazardous").attr("checked", true);
					}
					if(!responseText['hazardous']){
						$("#Hazardous").attr("checked", false);
					}
					// expand categories
					$.each(responseText['categories'], function(i, cat_uid){
						tr = $('tr[name="'+cat_uid+'"]');
						if (tr.hasClass('collapsed') | tr.hasClass('initial')){ tr.click(); }
					});
					// insert result values
					$.each(responseText['results'], function(i, result){
						$($($('#'+result.uid).children()[1]).children()[0]).val(result['result']);
						$($($('#'+result.uid).children()[2]).children()[0]).val(result['error']);
						$($($('#'+result.uid).children()[3]).children()[0]).val(result['min']);
						$($($('#'+result.uid).children()[4]).children()[0]).val(result['max']);
					});
				}
				else {
					portalMessage(responseText['errors'].join("<br/>"));
					window.scroll(0, 0);
					$('#ReferenceDefinition\\:list').removeAttr('disabled');
				}
			},
			error: function(XMLHttpRequest, statusText, errorThrown) {
				portalMessage(statusText);
				window.scroll(0, 0);
				$('#ReferenceDefinition\\:list').removeAttr('disabled');
			},
		});
	});

	//$('#ReferenceDefinition\\:list').change();
});
});
