#!/bin/sh

cat <<EOF
HTTP/1.0 200 OK
Content-Type: text/plain

EOF

env | sort
