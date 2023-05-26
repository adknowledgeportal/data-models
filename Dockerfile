FROM python:3.10

# install develop branch of schematic
RUN pip install git+https://github.com/Sage-Bionetworks/schematic.git@develop
