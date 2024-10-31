# pip install scikit-learn
# pip install tensorflow
# pip install matplotlib
# pip install paho-mqtt
# pip install paho-mqtt flask

import datetime
import json
from time import timezone
from flask import Flask
import google.generativeai as genai
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import numpy as np
import paho.mqtt.client as mqtt


# Chave da API
genai.configure(api_key="AIzaSyChtbxglA_gwNop0FmeUrirEwxrE71dQXQ")


generative_model = genai.GenerativeModel('gemini-1.5-flash')