#
#  _____                      _      _____                          _ _
# |  __ \                    | |    / ____|                        (_) |
# | |  | | ___    _ __   ___ | |_  | |     ___  _ __ ___  _ __ ___  _| |_
# | |  | |/ _ \  | '_ \ / _ \| __| | |    / _ \| '_ ` _ \| '_ ` _ \| | __|
# | |__| | (_) | | | | | (_) | |_  | |___| (_) | | | | | | | | | | | | |_
# |_____/ \___/  |_| |_|\___/ \__|  \_____\___/|_| |_| |_|_| |_| |_|_|\__|
#
#

# Heroku Settings

heroku config:add S3_KEY=xxxxxxxxxx
heroku config:add S3_SECRET=xxxxxxxxxx
heroku config:add FACEBOOK_APP_ID=xxxxxxxxxx
heroku config:add FACEBOOK_API_SECRET=xxxxxxxxxx
heroku config:add GOOGLE_OAUTH2_CLIENT_ID=xxxxxxxxxx
heroku config:add GOOGLE_OAUTH2_CLIENT_SECRET=xxxxxxxxxx
heroku config:add DEPLOY_ENV=prod
