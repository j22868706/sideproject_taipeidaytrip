#!/bin/bash

# Start Gunicorn in daemon mode with Eventlet worker, access and error logs, and bind to 0.0.0.0:3000
gunicorn -D -w 1 --worker-class eventlet --access-logfile gunicorn_access.log --error-logfile gunicorn_error.log -b 0.0.0.0:3000 app:app 

# Start Nginx in foreground mode (no daemon)
nginx -g 'daemon off;'