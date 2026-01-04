if you try running the docker container for the server and it doesn't work because it failed to connect to the database, then you'd have to enable IPv6 from within your Docker Desktop:

1. go to Docker Desktop
2. click settings -> Docker Engine
3. add this to the config: `"ipv6": true, "fixed-cidr-v6": "2001:db8:1::/64"`

also make sure to have the .env set up
