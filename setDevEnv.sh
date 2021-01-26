#!/bin/bash
# server should be running on port 5000 for Github callback
export DEBUG=True
export TESTING=True

export OAUTHLIB_INSECURE_TRANSPORT=1
export OAUTHLIB_RELAX_TOKEN_SCOPE=1
export DATABASE_URL=postgresql://postgres:postgres@localhost/rink-scheduler
export SECRET_KEY=someSecret
export GITHUB_OAUTH_CLIENT_ID=68b9633366c7e9ceb502
export GITHUB_OAUTH_CLIENT_SECRET=0eebbf24bb4cb3365f99232c985241dde683b425

