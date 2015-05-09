[![Build Status](https://api.travis-ci.org/abutcher/juicer.png)](https://travis-ci.org/abutcher/juicer/)

Juicer
------
```
usage: juicer [-h] [-v] [-V] {cart,rpm,repo,role,user,hello} ...

Manage release carts

optional arguments:
  -h, --help            show this help message and exit
  -v                    show verbose output
  -V, --version         show program's version number and exit

Commands:
  'juicer COMMAND -h' for individual help topics

  {cart,rpm,repo,role,user,hello}
   cart                cart operations
   rpm                 rpm operations
   repo                repo operations
   role                role operations
   user                user operations
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
cart_seeds: localhost:27017

[re]
hostname: HOSTNAME
promotes_to: qa

[qa]
hostname: HOSTNAME
```
