Readme


# How to install Docker?

There are 2 different ways to install docker to our system. 
* docker desktop
* docker-engine 

1. Docker Desktop  -  Windows-MacOS-Linux

    You can download and install docker desktop using the link:
    https://www.docker.com/products/docker-desktop/

    - For windows systems, you need to activate Hardware virtualization. Usually you can activate it using below option 
    Advanced --> CPU configuration --> Intel Virtualization Technology --> Enabled --> Exit --> Save Changes & Reset --> OK
    but it depends on bios model and version so for some bios models menu can change.


2. Ubuntu - Docker Engine

    You can follow instructions on this link 
    https://docs.docker.com/engine/install/ubuntu/

    Or follow these steps

        * sudo apt-get remove docker docker-engine docker.io containerd runc
        * sudo apt-get update
        * sudo apt-get install \
          ca-certificates \
          curl \
          gnupg \
          lsb-release
        * sudo mkdir -p /etc/apt/keyrings
        * curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        * echo \
         "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
         $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        *  sudo apt-get update
        *  sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

    Test Docker installation

        * sudo docker --version


# How to Run Project 

1. First, you need to set variables in '.devenv' file.
    Variables that we used for this project;<br /><br />

        export postgre_connection_string = postgresql+psycopg2://username:password@databasename/tablename
        export access_token_expire_minutes = 1440
        export algorithm = HS256
        export test_api_address = http://test_api:8000
        export smtp_tls = False
        export smtp_port = 587
        export smtp_host = smtp-mail.outlook.com
        export smtp_user = email@email.com
        export smtp_password = password
        export emails_from_email = email@email.com
        export emails_from_name = Unopad
        export email_reset_token_expire_hours = 1400
        export email_templates_dir = /email-templates/build
        export server_name = UNOPAD
        export server_host = http://unopad.com
        export project_name = unopad
        export hubspot_api_key = hubspotkey

2. If you have installed Postgres, you can use docker build and docker run commands<br />
    Example:<br />
        When you are in the same directory with Dockerfile

        Docker build -t test:v1 .
        Docker run —env-file PATH-TO-ENV-FILE -p 80:8000 test:v1

3. If you don’t have Postgres on your setup. You can use docker-compose command. It will setup and run Postgres and API projects automatically
    For this way, you have to change env-file path inside docker-compose.yml file. Also, you can change ports and volumes.<br />

    Example:<br />
    When you are in the same directory with docker-compose.yml file.

    Docker-compose build
    Docker-compose up

    Or build and up together

        Docker-compose up --build

# How to Run Tests

1. First of all, as running a project, you have to set environment variables which are inside .testenv
Go to the same directory with docker-compose-test.yaml and write the below command

        docker-compose -f docker-compose-test.yaml up --build 

    -f parameter is to show your docker-compose test yaml. If you don't write '-f' parameter it will automatically look for docker-compose.yaml<br />
    --build parameter is to build docker before start.<br />
    'up' means create containers and start<br />

2. After you run the docker, it will create and start postgres, Fastapi and tests. When it finishes, you will see the results of the tests on your console. After that, you can stop containers using 'ctrl + c' keyboard combination.

3. Delete test docker files.

        docker-compose -f docker-compose-test.yaml down --volumes

    'down' means stop and delete containers, networks<br />
    --volumes parameter is to delete also volumes which are used for this docker

# How to Run Graylog

1. Go to the same directory with docker-compose-graylog.yaml and write the below command

        docker-compose -f docker-compose-graylog.yaml up --build 

    -f parameter is to show your docker-compose graylog yaml. If you don't write '-f' parameter it will automatically look for docker-compose.yaml<br />
    --build parameter is to build docker before start.<br />
    'up' means create containers and start (if you already built the container, you don't need to write '--build')<br />

2. After you run the docker, it will create and start elastic search, mongodb and graylog.

3. Delete test docker files.

        docker-compose -f docker-compose-graylog.yaml down --volumes

    'down' means stop and delete containers, networks<br />
    --volumes parameter is to delete also volumes which are used for this docker

# How to Install Nginx

1. Update the Debian repository information:

        sudo apt-get update

2. Install the NGINX Open Source package:

        sudo apt-get install nginx

3. Verify the installation:

        sudo nginx -v

4. Start, Stop and Restart Nginx

        service nginx start
        service nginx stop
        service nginx restart

5. Disable the Default Virtual Host
Once you have installed Nginx, follow the below command to disable virtual host:

        sudo unlink /etc/nginx/sites-enabled/default

6. Create the Nginx Reverse Proxy
After disabling the virtual host, we need to create a file called reverse-proxy.conf within the 'etc/nginx/sites-available directory' to keep reverse proxy information.

For this, we should first access the directory using the cd command:

        cd etc/nginx/sites-available/

Then we can create the file using the vi or nano editor:

        vi reverse-proxy.conf
        nano reverse-proxy.conf

In the file we need to paste in these strings:

        server {

            listen 80 default_server;
            listen [::]:80 default_server;
            server_name dev.unopad.com;

            return 301 https://dev.unopad.com;
        }

        server {

            listen 443 ssl default_server;
            listen [::]:443 ssl default_server;
            server_name dev.unopad.com;

            ssl_certificate /etc/nginx/ssl/unopad.com.crt.pem;
            ssl_certificate_key /etc/nginx/ssl/unopad.com.key.pem;
            ssl_session_cache builtin:1000 shared:SSL:10m;
            ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
            ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
            ssl_prefer_server_ciphers on;
            access_log /var/log/nginx/example.com.access.log;

            location / {
                proxy_set_header Host $host; 
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_pass http://localhost:3000 ; proxy_read_timeout 90;
            }
            location /api/ {
                proxy_set_header    X-Real-IP  $remote_addr;
                proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header    Host $http_host;
                proxy_redirect      off;
                proxy_pass          http://localhost:4000/;
            }
            location /api {
                return 301 /app1/;
            }
            location /graylog {
                proxy_set_header    X-Real-IP  $remote_addr;
                proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header    Host $http_host;
                proxy_redirect      off;
                proxy_pass          http://localhost:9000/;
            }
        }

In the above command, the considerable point is the proxy pass is allowing the requests coming through the Nginx reverse proxy to pass along to localhost:port, which works in docker container. Thus, both the web servers – Nginx and Dockers share the content.

Once completed, simply save the file and exit the editor.

7. Now, activate the directives by linking to /sites-enabled/ using the following command:

        sudo ln -s /etc/nginx/sites-available/reverse-proxy.conf /etc/nginx/sites-enabled/reverse-proxy.conf

8. Test Nginx and the Nginx Reverse Proxy
Lastly, we need to run an Nginx configuration test and restart Nginx to check its performance. Type the below command to verify the Nginx functioning on the Linux terminal:

        service nginx configtest
        service nginx restart
