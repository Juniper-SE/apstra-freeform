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

3. Copy AOS SDK Python3 wheel into the ./thirdparty directory (contact Apstra
   support to get a copy)
```
$ ls -al thirdparty/
..
-rw-r--r--   1 acarpi  staff      72 Sep  5 23:36 README
-rw-r--r--   1 acarpi  staff  383747 Sep  5 12:43 aos_sdk-0.1.0-py3-none-any.whl
```
4. Build the runtime container
```bash
$ docker build -t demo-runtime:0.1 .
```
If this command fails because you don't have access to Apstra jenkins,
please contact us so we can provide the AOS SDK file locally

5. Run the dev container. Notice this will mount the source code folder inside the container
  so that you can run your tests locally.
```bash
$ docker run -it -d --name tfl-demo --mount type=bind,source=$(pwd),target=/project demo-runtime:0.1
```

6. Enter the dev container and run the pytest-based testsuite
```bash
$ docker exec -it tfl-demo bash
root@f647a4f0374c:/# source /demo-venv/bin/activate
(demo-venv) root@f647a4f0374c:/# cd /project/
(demo-venv) root@f647a4f0374c:/# pip install -r requirements.txt
(demo-venv) root@f647a4f0374c:/# PYTHONPATH=. py.test -s -v -p no:logging --pdb --config-path=config.yaml tests/test_tfl_demo.py
```
