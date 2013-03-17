
$(document).ready(function() {

   $(".login-required").click(function(){
      console.log("you have to be logged in");
   });
   
   $(".follow-project").click(function(){
      modify_project_relation(this, 'follow'); 
   })
   
   $(".unfollow-project").click(function(){
      if (!confirm("Are you sure you want to stop following this project?")){
         return;
      }
      modify_project_relation(this, 'unfollow');
   })   
      
var modify_project_relation = function(elem, action){
   project_id = $(elem).attr("project-id");
   $.ajax({
            url : '/ajax/modify_project_relation',
            data : { 'project_id': project_id, 'action': action},
            success :function(res){
               if (action == 'follow'){
                  alert("You have succesfully followed this project");
               }
               else if(action == 'unfollow'){
                  alert("You have succesfully unfollowed this project");
               }
            },
            error : function(res){
               alert("failure to follow/unfollow");
            }
   });
}
    
   $('.opportunity_container').click(function() {
      window.location.href = '/opportunity/' +  $(this).attr('opportunity_id');
   });
});

