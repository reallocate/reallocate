$(".login-required").click(function(){
   console.log("you have to be logged in");
});

$(".follow-project").click(function(){
    project_id = $(this).attr("project-id");
    $.ajax({
            url : '/ajax/follow_project?project_id=' + project_id,
            data : { 'project_id': project_id },
            success :function(res){
                console.log("success - add message reminder to this");
            },
            error : function(res){
            }
    });
});
