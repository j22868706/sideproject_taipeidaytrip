#!/bin/bash

# Start Gunicorn in daemon mode with Eventlet worker, access and error logs, and bind to 0.0.0.0:3000
gunicorn -w 2 --worker-class sync --log-level info -b 0.0.0.0:3000 app:app &

# Start Nginx in foreground mode (no daemon)
nginx -g 'daemon off;'