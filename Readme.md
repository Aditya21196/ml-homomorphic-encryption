## Description

This repository describes a prototype for building a consumer facing privacy preserving machine learning application using homomorphic encryption. This means that the user can send encrypted data to the ML model for prediction. The model will be able to produce an encrypted output back to user after passing the aforementioned input through the model. 

The novel technology which is the basis for this capability is the homomorphic encryption which allows computation over encrypted data to give an encrypted output. The encryption is done by the client/user and then sent to server. Once server performs the computation and produces an encrypted output, it is sent back to user. Only the user can decrypt this data thus preserving the user's privacy.

This solves the modern day problem of users being able to fully utilize Machine Learning capabilities to improve their lives without compromising their personal information.

## Setup

Right now, pyfhel is not supported on mac OS. We carried out all our experiments on a rented GCP server and/or repl.it (a website which provides isolated containerized environments to collaborate)

**This setup is valid for a linux machine/server which has latest version of C++ and cmake installed.**

Please run:
> pip install -r requirements.txt

Then, to run the server, open a terminal in server_code folder and run:
> python3 main.py

To run client code, go to root of this repo and run:
> jupyter notebook

and navigate to "Client Code.ipynb". Change the IP address to whichever IP the server is hosted. If server is running on the same machine as "Client Code.ipynb" then let it remain "localhost"

## Presentation Links

Gdrive Link of Presentation: https://drive.google.com/file/d/1vZ96CziVmSu1oUSKbk4_rGThANvHuQ74/view?ts=627878a4 

Powerpoint Presentation: https://docs.google.com/presentation/d/1LJ--jKKHA7krFzwI4rQlGuk7HTRGzBw-t0OdSIiBgVs/edit#slide=id.p 
