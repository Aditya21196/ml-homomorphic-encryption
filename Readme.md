## Setup

Right now, pyfhel is not supported on mac OS. We carried out all our experiments on a rented GCP server and/or repl.it (a website which provides isolated containerized environments to collaborate)

This setup is valid for a linux machine/server which has latest version of C++ and cmake installed.

Please run:
> pip install -r requirements.txt

Then, to run the server, open a terminal in server_code folder and run:
> python3 main.py

To run client code, go to root of this repo and run:
> jupyter notebook

and navigate to "Client Code.ipynb". Change the IP address to whichever IP the server is hosted. If server is running on the same machine as "Client Code.ipynb" then let it remain "localhost"

# Presentation Links

Gdrive Link of Presentation: https://drive.google.com/file/d/1vZ96CziVmSu1oUSKbk4_rGThANvHuQ74/view?ts=627878a4 

Main Presentation on NYU Stream:   https://stream.nyu.edu/media/Running+Multi-Layer+Perceptron+Models+on+Homomorphically-Encrypted+Data/1_1xy8fn3z

Bonus Content on NYU Stream:  https://stream.nyu.edu/media/Running+Multi-Layer+Perceptron+Models+on+Homomorphicall[…]Data+-+Bonus+Material++-+What+is+a+Lattice++++RLWE/1_l1o7fqrp