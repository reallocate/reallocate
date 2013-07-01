reAllocate = {

    init: function() {

        $(".login-required").click(function(e) {
            if (!reAllocate.user) {
                e.preventDefault();
                $('#login-modal').modal('show');
                
                return False;
            }
        });
       
        $(".follow-project").click(function() {
            reAllocate.modify_project_relation(this, 'follow'); 
        });
   
        $(".unfollow-project").click(function() {
            if (!confirm("Are you sure you want to stop following this project?")) { 
                return;
            }
            reAllocate.modify_project_relation(this, 'unfollow');
        }); 

        $('.thumbnail_container').click(function() {
            if ($(this).attr('type') == 'opportunity') {
                window.location.href = '/opportunity/' +  $(this).attr('opportunity_id');
            } else if ($(this).attr('type') == 'project') {
                window.location.href = '/project/' +  $(this).attr('project_id');
            }
        });

        $('#modal-login').on('submit', function(e) {

            e.preventDefault();
            reAllocate.login_user($('#modal-username').val(), $('#modal-password').val());

        });
    },   

    login_user: function(username, password) {

        $.ajax({
            url : '/ajax/login',
            method: 'POST',
            data : {'username': username, 'password': password},
            success: function(res) {
                location.reload();
            },
            error: function(res) {

                $('#modal-username').parent('.control-group').addClass('error');
                $('#modal-password').parent('.control-group').addClass('error');
            }
       });
    },

    // aka follow | unfollow
    modify_project_relation: function(elem, action) {

        project_id = $(elem).attr("project-id");

        $.ajax({
            url : '/ajax/modify-project-relation',
            data : {'project_id': project_id, 'action': action},
            success: function(res) {
                if (action == 'follow') {
                    console.log("You have succesfully followed this project");
                } else if (action == 'unfollow') {
                    console.log("You have succesfully unfollowed this project");
                }
            },
            error: function(res) {
                console.log("failure to follow/unfollow");
            }
       });
    }
};

// init page
$(document).ready(function(){ reAllocate.init(); });
