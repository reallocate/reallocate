reAllocate = {

    init: function() {
        
        this.setupAddThis();
        
        $('.delegate-file-upload').click(function() {
            
            $('input[type="file"]').trigger('click');
            return false;
        
        });
        
        $('input[type="file"]').on('change', function(){
            // show check mark next to file upload box after file is attached
            
            upload_ok = $(".file-upload-ok");
            if (upload_ok){
                upload_ok.show();
            }
            
        });
        
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

        $('#modal-login').on('submit', function(event) {

            event.preventDefault();
            reAllocate.loginUser($('#modal-username').val(), $('#modal-password').val());

        });

        // init all post update forms
        $('.post-update form').each(function(i, form) {

            $(form).on('submit', function(event) {

                event.preventDefault();
                reAllocate.postUpdate(form);
            });
        });

    },   

    postUpdate: function(form) {

        var form = $(form);
        
        if (form.find('textarea').val().length == 0) {
            alert('Please enter an update');
            return false;
        }
    
        var submit_button = form.find('input[type="submit"]');
        var file = form.find('input[type="file"]').get(0).files[0];
        var xhr = new XMLHttpRequest();
    
        //xhr.ontimeout = function() {
        //  this.abort();
        //  submission_error_cb();
        //  return;
        //}
        //xhr.onerror = submission_error_cb;
        
        xhr.onreadystatechange = function(e) {

            if (this.readyState != 4) { return; }
        
            if (this.status == 200 || this.status == 204) {

                //var response = JSON.parse(this.responseText);

                // hide modal if used/exists else reload page
                if ($('#post-update-modal').length) {
                    $('#post-update-modal').modal('hide');
                    console.log('modal');
                } else {
                    console.log('no modal');
                    window.location.assign('#updates');
                    window.location.reload();
                }
    
            } else if (this.status == 500 || this.status == 503) {

                alert('An error occurred uploading file');
            }
        };

        xhr.timeout = 90000;
        xhr.open('post', '/ajax/add-update?' + form.serialize(), true);
        xhr.setRequestHeader("Content-Type", "application/octet-stream");
        if (file) xhr.setRequestHeader("X-Mime-Type", file.type);

        xhr.send(file);
    
        return false;
    },

    loginUser: function(username, password) {

        $.ajax({
            url: '/ajax/login',
            method: 'POST',
            data : {'username': username, 'password': password},
            success: function(json) {

                reAllocate.user = json.user;

                $(".bad-username-or-password").addClass('is-invisible');
                $('#login-modal').modal('hide');

                if (json.next) {
                    location.href = json.next;
                } else if (reAllocate.follow) {
                    reAllocate.followProject(reAllocate.follow.e, reAllocate.follow.pid);
                }

                $('#user-email').text(json.user.email);
                $('.user').css('display', 'block');
                $('.anon').css('display', 'none');

            },
            error: function(res) {
                $('#modal-username').parent('.form-group').addClass('has-error');
                $('#modal-password').parent('.form-group').addClass('has-error');
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
    engageOpportunity: function(message, pid, oid) {

        // make sure user is logged in
        if (!reAllocate.user) {

            $('#login-modal').modal('show');

            return;
        }

        $.ajax({
            url : '/ajax/engage-opportunity',
            data : {'projectId': pid, 'opportunityId': oid, 'message': message},
            success: function(res) {
                window.location.reload();
            },
            error: function(res) {
                alert("failed to engage opportunity");
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
