README
------

This tool requires Docker to be installed on your laptop, please refer to:
https://docs.docker.com/get-docker/

How to run:

1. Clone the present repo into your workspace
```bash 
$ git clone https://github.com/Juniper-SE/apstra-freeform.git
$ cd apstra-freeform/nfd-tfl-demo
```
2. Edit the file config.yaml to point to your Apstra VM IP address
```
---
url: https://10.28.236.3/api
```

3. Build dev container 
```bash
$ docker build -t demo-runtime:0.1 .
```
If this command fails because you don't have access to Apstra jenkins,
please contact us so we can provide the AOS SDK file locally

4. Run the dev container. Notice this will mount the source code folder inside the container
  so that you can run your tests locally.
```bash
$ docker run -i -d --name tfl-demo -v $(pwd):/project demo-runtime:0.1
7710e330872b0ddec2b8246abae0c6d4087306a1b43ece6a40aaebe878330f6b
```

5. Enter the dev container and run the pytest-based testsuite
```bash
docker exec -it tfl-demo bash   
$ cd /project
$ source /demo-venv/bin/activate
$ pip install -r requirements.txt
$ PYTHONPATH=. py.test -s -v -p no:logging --alluredir allurereport --pdb --config-path=config.yaml tests/test_tfl_demo.py
```
