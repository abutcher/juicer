[![Build Status](https://api.travis-ci.org/abutcher/juicer.png)](https://travis-ci.org/abutcher/juicer/)


Juicer
------
```
usage: juicer [-h] [-v] [-V] {repo,rpm,hello,cart} ...

Manage release carts

optional arguments:
-h, --help            show this help message and exit
-v                    increase the verbosity (up to 3x)
-V, --version         show program's version number and exit

Commands:
'juicer COMMAND -h' for individual help topics

{repo,rpm,hello,cart}
cart                cart operations
rpm                 rpm operations
repo                repo operations
hello               test your connection to the pulp server
```

Config
------
```
[DEFAULT]
username: USERNAME
password: PASSWORD
port: 443
verify_ssl: False
ca_path: PATH_TO_CA
cert_filename: PATH_TO_CERT
start_in: re

[re]
hostname: HOSTNAME
promotes_to: qa

[qa]
hostname: HOSTNAME
```
