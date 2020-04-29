# SI507FINALPROJ
Repository for SI 507 Final Project

# Repository Intro
The repository contains 
the main python file, final_proj.py, to run the program
cache file, spot_crime_cache, to show the usage of cache and to expedite the running speed when necessary
database file, Spotcrime.sqlite, to show the usage of database
templates folder including inputs.html and response.html for flask
also .ignore to ignore pycache files

# Instruction
This program is designed to crawl and scrap information from spotcrim.com, help user to obtain criminal activity faster and more intuitively. With instructions in program, users are prompted to input state, city, and which type of info they need, respectively. With different options, different data presentation will pop up. Users are allowed to exit the program or back to upper level at any step in the program.

# Required Package
from bs4 import BeautifulSoup
import requests
import json
import webbrowser
import time
import sqlite3
from flask import Flask, render_template, request
import sys
import plotly.graph_objs as go

