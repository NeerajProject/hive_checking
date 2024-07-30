$(document).ready(function() {

    $('#company_name_logo').change(function(e) {
//        var file = e.target.files[0];
//        var reader = new FileReader();
//        reader.readAsDataURL(file);
//      reader.onload = function(e) {
//         $('#branding_panel_icons').attr('src', e.target.result);
//           }
$('#btn_confirm_branding_panel').text("Preview")







    });


    $('#company_name_logo').click(function(e) {
//        var file = e.target.files[0];
//        var reader = new FileReader();
//        reader.readAsDataURL(file);
//      reader.onload = function(e) {
//         $('#branding_panel_icons').attr('src', e.target.result);
//           }
$('#btn_confirm_branding_panel').text("Preview")







    });



     $('#company_name_changer').change(function(e) {
            $('#btn_confirm_branding_panel').text("Preview")



    });

   $('.floor_plan_suggestions').click(function(e){

            var filename = $('.upload_name').val().split('\\').pop();
                 $('#field_filename').val(filename)


   })



   $('.floor_plan_suggestions').change(function(e){

            var filename = $('.upload_name').val().split('\\').pop();
                 $('#field_filename').val(filename)


   })


$('#btn_confirm_branding_panel').click(
function(e){
var button_text =  $('#btn_confirm_branding_panel').text();
if (button_text=='Preview'){

$('#btn_confirm_branding_panel').text("Confirm")
var company_name_changer  =$('#company_name_changer').val()
$('#branding_panel_company_id').text(company_name_changer)



        var fileInput =document.getElementById('company_name_logo');
        var file = fileInput.files[0];
        if (file){
                var reader = new FileReader();

        reader.onload = function(e) {
            $('#branding_panel_icons').attr('src', e.target.result);
        }

        reader.readAsDataURL(file);

        }









//var reader = new FileReader();
//
//        reader.readAsDataURL(file);
//      reader.onload = function(e) {
//         $('#branding_panel_icons').attr('src', e.target.result);
//           }
//        reader.readAsDataURL(file);




}
if (button_text=='Confirm'){

$('#attendee_badge_request_form').submit()
}



})



});
