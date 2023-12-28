## Create Virtual Environment for Python3 (in Ubuntu)

### 1. Check for Python version
    $ python -V

### 2. Install the `python3-venv` package 
It provides the `venv` module for creating a virtual environment

    $ sudo apt install python3-venv

### 3. Create virtual environment
Once the module is installed we are ready to create virtual environments for Python 3.

Switch to the directory where you would like to store your Python 3 virtual environments. Within the directory run the following command to create your new virtual environment:

    $ python3 -m venv my-project-env
The command above creates a directory called `my-project-env`, which contains a copy of the Python binary, the Pip package manager, the standard Python library and other supporting files.

### 4. Activate virtual environment
To start using this virtual environment, you need to activate it by running the `activate` script:

    $ source my-project-env/bin/activate

### 5. Check for virtual environment activation
Shell’s prompt will change and it will show the name of the virtual environment you’re currently using. In our case that is `my-project-env`

    output
    $ source my-project-env/bin/activate
    (my-project-env) $

### 6. Install python modules (e.g. pandas)

    (my-project-env) $ pip install pandas

### 7. Deactivate the virtual environment

    $ deactivate

## Create Deployment package for AWS Lambda (in Ubuntu)

### 8. Create a zip file
with the dependencies and your lambda function code. First, navigate to the site-packages directory in your virtual environment, which is where pip installs your libraries:

    $ cd my-project-env/lib/pythonX.X/site-packages

Replace `X.X` with your Python version. Then, create a zip file with all the packages in the current directory (site-packages) and your lambda function code. Assuming your lambda function code is in `/path_to_your_lambda/lambda_function.py`, run:

    $ zip -r9 /path_to_your_lambda/deployment_package.zip .

### 9.  Add your lambda function code to the zip file

    $ cd /path_to_your_lambda
    $ zip -g deployment_package.zip lambda_function.py

