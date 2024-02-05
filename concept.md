### DoS attack detection


## Image building
`./build` - buduje obraz z nginx i nprobe


nprobe start:
nprobe -i lo -n host.docker.internal:5005

tcpdump -i lo

## Commands:
Below are listed commands available from `./run` script.
* build image: `./run build <tag>`
* run container  based on img: `./run container <tag>`
* start detector app: `./run detector`
* client traffix simulation: `./run client-sim`
* DOS attack: `./run attack --count 10 --threads 5`

command inside the container:
* start nprobe: `nprobe /etc/nprobe/nprobe.conf`
