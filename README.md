if you try running the docker container for the server and it doesn't work because it failed to connect to the database, then you'd have to enable IPv6 from within your Docker Desktop:

1. go to Docker Desktop
2. click settings -> Docker Engine
3. add this to the config: `"ipv6": true, "fixed-cidr-v6": "2001:db8:1::/64"`

to build the docker container locally, `do docker build -t "bldr-battle-server" .`

now when you run docker locally, you should do `docker run --rm -it -p 8000:8000 -e "<VALUE_OF_CONNECTION_STRING>" "bldr-battle-server"`. note that you would have to copy the value of the connection string from the .env file into the command.

the reason we are doing the above steps is because we don't want to put the actual .env values inside the file system of the container. if we forget about it then publish the image to docker hub, then that's not good.

also, when running terraform, make sure to do `terraform apply -var="db_connection_string=VALUE"`. this basically tells the ec2 instance what the value of the connection string is, which is passed down to the docker container after installing via the `user_data` attribute.
