# Inici.py

import streamlit as st

import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import json
import os
import streamlit as st
from openai import OpenAI
import app_component as au
import sys
import speech_recognition as sr
import random
import mysql.connector
import requests
import ftplib
import time




db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name =  st.secrets["DB_NAME"]
db_user =  st.secrets["DB_USER"]
db_password =  st.secrets["DB_PASSWORD"]

client = OpenAI(api_key=st.secrets["auto_pau"])

def main():
    import app_component as au

    st.set_page_config(
        page_title="rurAIctive ",
        page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"  #
    )

    st.markdown(
        "<style>#MainMenu{visibility:hidden;}</style>",
        unsafe_allow_html=True
    )

    au.render_cta()

    # st.markdown("---")
    #au.robo_avatar_component()

    with open('pwd.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    #print(config['cookie']['name'])
    # can be main or sidebar
    name, authentication_status, username = authenticator.login("Welcome to rurAIctive, an AI tool for Dynamo's and Technical Partners", "main")

    parlantTema =''

    for key,value in config['credentials']['usernames'].items():
        if key == username:
            parlantTema = value['tema']

    if authentication_status == False:
        st.error("L'usuari o contrasenya és incorrecte")

    if authentication_status == None:
        st.warning("Introdueix el teu usuari i contrasenya")

    if authentication_status:
        # Main Streamlit app starts here
        st.markdown("#### Descriu una imatge....")
        with st.expander("Descriu...", expanded=True):
            st.markdown(
                "'Descriu...', és una eina col·laborativa on els teus textos cobren vida en forma d'imatges'. Aquí, la teva imaginació és el límit: descriu escenes, personatges i diàlegs, i nosaltres els convertirem en impressionants còmics visuals.")

        # ---- Logout ----
        authenticator.logout("Tancar Sessió", "sidebar")


if __name__ == '__main__':
        main()