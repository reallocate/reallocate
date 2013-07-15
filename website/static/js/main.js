reAllocate = {

    init: function() {
        
        
        this.setup_addthis();
        
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
            url: '/ajax/login',
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
    },
    
    // setup default sharing messages with overrides from calling page
    setup_addthis: function(twitter, title, description) {
        // to setup different shares on different buttons on the same page use markup explained in this article
        // http://support.addthis.com/customer/portal/articles/381242-url-title
        // currently only twitter uses the templates
        // title + description appear to only work on linkedin ?
        var default_twitter_msg = "Check out the work going on @reallocate http://reallocate.org";
        var default_title = "Reallocate";
        var default_description = "Check out the work going on @reallocate. http://reallocate.org";
        
        var final_title = (title) ? title: default_title;
        var final_description = (description) ? description: default_description;
        var twitter_msg = (twitter) ? twitter: default_twitter_msg;
    
        // sets global settings for included addthis_js
        addthis_share = {
            title: final_title,
            description: final_description,
            templates: {
                twitter: twitter_msg,
            }
        } 
    }
};

// init page
$(document).ready(function(){
    reAllocate.init();
    var addthis_share = {};
});
