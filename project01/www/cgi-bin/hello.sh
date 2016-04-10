#!/bin/sh

cat <<EOF
HTTP/1.0 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>Hello, World!</title>
<link href="http://www3.nd.edu/~pbui/static/css/blugold.css" rel="stylesheet">
</head>
<body>
<div class="container">
<div class="page-header">
<h2>Hello</h2>
</div>
<form class="form-inline">
<label class="control-label">Name:</label>
<input name="name" type="text" class="form-control">
<button class="btn btn-success">Submit</button>
</form>
<br>
EOF

qsdecode() {
    sed 's@+@ @g;s@%@\\x@g' | xargs -0 printf "%b"
}

name=$(echo $QUERY_STRING | sed -nr 's/name=([^&]*).*/\1/p' | qsdecode)

if [ -n "$name" ]; then
    cat << EOF
<div class="alert alert-success"><h4>Hello, $name!</h4></div>
EOF
fi

cat <<EOF
</div>
</body>
</html>
EOF
