reAllocate = {

    init: function() {
        
        this.setupAddThis();
        
        $(".login-required").click(function(e) {

            if (!reAllocate.user) {

                e.preventDefault();
                $('#login-modal').modal('show');
                
                return;
            }
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
            reAllocate.loginUser($('#modal-username').val(), $('#modal-password').val());

        });
    },   

    loginUser: function(username, password) {

        $.ajax({
            url: '/ajax/login',
            method: 'POST',
            data : {'username': username, 'password': password},
            success: function(res) {

                $('#login-modal').modal('hide');

                if (res.next) {
                    location.href = res.next;
                } else if (reAllocate.follow) {
                    reAllocate.followProject(reAllocate.follow.e, reAllocate.follow.pid);
                }
                console.log(res);
            },
            error: function(res) {

                $('#modal-username').parent('.control-group').addClass('error');
                $('#modal-password').parent('.control-group').addClass('error');
            }
       });
    },

    // toggles follow/unfollow
    followProject: function(e, pid) {

        var action = $(e).text().toLowerCase();

        // make sure user is logged in
        if (!reAllocate.user) {

            reAllocate.follow = {'e': e, 'pid': pid};
            $('#login-modal').modal('show');

            return;
        }

        $.ajax({
            url : '/ajax/modify-project-relation',
            data : {'project_id': pid, 'action': action},
            success: function(res) {
                if (action == 'follow') {
                    $(e).text('Unfollow');
                } else if (action == 'unfollow') {
                    $(e).text('Follow');
                }
            },
            error: function(res) {
                console.log("failure to follow/unfollow");
            }
       });
    },

    // sends engagement request for an opportunity
    engageOpportunity: function(e, pid, oid) {

        // make sure user is logged in
        if (!reAllocate.user) {

            $('#login-modal').modal('show');

            return;
        }

        $.ajax({
            url : '/ajax/engage-opportunity',
            data : {'projectId': pid, 'opportunityId': oid},
            success: function(res) {
                $(e).attr('disabled', 'disabled');
             },
            error: function(res) {
                console.log("failure to engage opportunity");
            }
       });
    },
    
    // setup default sharing messages with overrides from calling page
    setupAddThis: function(twitter, title, description) {
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
$(document).ready(function() {
    reAllocate.init();
    var addthis_share = {};
});
