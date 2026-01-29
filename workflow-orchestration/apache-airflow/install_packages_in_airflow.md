### 1. If wants to install the depenencies in docker-step
Follow the link [How to install packages in Airflow (docker-compose)](https://stackoverflow.com/questions/67887138/how-to-install-packages-in-airflow-docker-compose) in case to install any libraries/Packages
- Put `Dockerfile`, `docker-compose.yaml` and `requirements.txt' (having all the packages to install) files to the project directory
- Put command to load all the libaraies from requirements.txt in **Dockefile** as specified in the mentioned link
- Modify the `docker-compose.yaml` code as specified in the link
- Run `docker-compose` up to start Airflow, `docker-compose` should build your image automatically from `Dockerfile`. Run `docker-compose build` to rebuild the image and update dependencies

### 2. Without docker set-up
Just do `pip install <<ANY LIBRARY>>` in terminal
