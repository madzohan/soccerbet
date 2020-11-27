# Soccerbet

### Install
    pipenv install
    pipenv shell

#### Setup Selenoid
- using selenoid to launch specific browser in docker container


        SELENOID_HOST=localhost
        SELENOID_PORT=4444

        cd soccerbet_project_where_`browsers.json`_located
        docker run
            -p $SELENOID_PORT:4444
            -v /var/run/docker.sock:/var/run/docker.sock
            -v /home/tyoma/dev/python/soccerbet:/etc/selenoid/
            --name selenoid_chrome
            aerokube/selenoid:latest-release

### Run
    python -m odds_controller.run
