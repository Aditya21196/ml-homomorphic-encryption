## Setup

Right now, pyfhel support is not supported on mac OS. We carried out all our experiments on a rented GCP server and/or repl.it (a website which provides isolated containerized environments to collaborate)

This setup is valid for a linux machine/server which has latest version of C++ and cmake installed.

Please run:
> pip install -r requirements.txt

Then, to run the server, open a terminal in server_code folder and run:
> python3 main.py

To run client code, go to root of this repo and run:
> jupyter notebook

and navigate to "Client Code.ipynb". Change the IP address to whichever IP the server is hosted. If server is running on the same machine as "Client Code.ipynb" then let it remain "localhost"