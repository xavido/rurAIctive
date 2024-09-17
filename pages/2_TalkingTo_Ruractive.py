import os
import streamlit as st
from openai import OpenAI
import app_component as au
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import sys
import speech_recognition as sr
import random
import mysql.connector
import requests
import ftplib
import time
import base64


db_host = st.secrets["DB_HOST"]
db_port = st.secrets["DB_PORT"]
db_name = st.secrets["DB_NAME"]
db_user = st.secrets["DB_USER"]
db_password = st.secrets["DB_PASSWORD"]

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )

# Define the function to process messages with citations
def process_message_with_citations(message):
    """Extract content and annotations from the message and format citations as footnotes."""
    message_content = message.content[0].text
    annotations = message_content.annotations if hasattr(message_content, 'annotations') else []
    citations = []

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citations based on annotation attributes
        if (file_citation := getattr(annotation, 'file_citation', None)):
            # Retrieve the cited file details (dummy response here since we can't call OpenAI)
            cited_file = {
                'filename': "Informació de l'Escola"}  # This should be replaced with actual file retrieval
            citations.append(f'[{index + 1}] {file_citation.quote} from {cited_file["filename"]}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            # Placeholder for file download citation
            cited_file = {
                'filename': "Informació de l'Escola"}  # This should be replaced with actual file retrieval
            citations.append(
                f'[{index + 1}] Click [here](#) to download {cited_file["filename"]}')  # The download link should be replaced with the actual download path

    # Add footnotes to the end of the message content
    full_response = message_content.value  # + '\n\n' + '\n'.join(citations)
    return full_response



# Set up the Streamlit page with a title and icon
st.set_page_config(page_title="Parlant Amb...", page_icon=":speech_balloon:")

def parlant_amb():

    # Initialize client
    client = OpenAI(api_key=st.secrets["auto_pau"])
    with open('pwd.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    # print(config['credentials'])
    # print(config['cookie']['name'])
    # can be main or sidebar
    name, authentication_status, username = authenticator.login("Benvingut/da a PARLANT AMB! - Inicia Sessió", "main")
    parlantTema = ''
    parlantCrea = ''
    parlantID = 0
    parlantTemaID = 0
    parlantPregunta = ''
    parlantNivell = ''
    parlantIdioma = ''
    count = 0
    for key, value in config['credentials']['usernames'].items():
        if key == username:
            parlantTema = value['tema']
            parlantID = value['id']
            parlantTemaID = value['temaID']
            parlantCrea = value['crea']
            parlantParlant = value['parlant']
            parlantPregunta = value['pregunta']
            parlantAdditional = value['additional']
            parlantNivell = value['nivell']
            parlantIdioma = value['idioma']

    if authentication_status == False:
        st.error("L'usuari o contrasenya és incorrecte")

    if authentication_status == None:
        st.warning("Introdueix el teu usuari i contrasenya")

    if authentication_status:
        # ---- Logout ----
        authenticator.logout("Tancar Sessió", "sidebar")
        st.markdown(
            "<style>#MainMenu{visibility:hidden;}</style>",
            unsafe_allow_html=True
        )

        #au.render_cta()
        match parlantTemaID:
            case 1:  # Assistant Cos Humà
                OPENAI_ASSISTANT = st.secrets["OPENAI_ASSISTANT1"]
            case 2:  # Assistant Antiga Roma
                OPENAI_ASSISTANT = st.secrets["OPENAI_ASSISTANT2"]
            case 3:  # Cicle de l'Aigua
                OPENAI_ASSISTANT = st.secrets["OPENAI_ASSISTANT3"]
            case 4:  # Historia ESO
                OPENAI_ASSISTANT = st.secrets["OPENAI_ASSISTANT4"]
            case 0:
                OPENAI_ASSISTANT = "assistant_0"

        assistant_id = OPENAI_ASSISTANT

        st.title("Parlant Amb..."+parlantParlant)
        missatge = "Pregunta el que vulguis sobre..."+parlantTema
        #print(missatge)
        st.markdown(missatge)
        # st.image(image_url, caption='Test')
        if "start_chat" not in st.session_state:
            st.session_state.start_chat = True

        if "thread_id" not in st.session_state:
            print("Creem un thread")
            thread = client.beta.threads.create(messages=[{"role": "user", "content": "Et faré una pregunta:"}])
            st.session_state.thread_id = thread.id
            xivato = ":"
        else:
            xivato = "__"

        elthreadid = st.session_state.thread_id

        # Only show the chat interface if the chat has been started
        if st.session_state.start_chat:
            # Initialize the model and messages list if not already in session state
            #st.session_state.messages = []
            if "messages" not in st.session_state:
                st.session_state.messages = []

            if prompt := st.chat_input("Escriu aquí la teva pregunta"+xivato):

                try:
                    elmissatge = prompt
                    # Add user message to the state and display it

                    #st.session_state.messages.append({"role": "user", "content": prompt})

                    with st.chat_message("user"):
                        st.markdown(prompt)
                        xivato = "**"
                        if parlantNivell == 1:
                            additionalInstructions = "Si la pregunta no està relacionada amb:"+parlantTema+",no contestis.Respon només en CATALÀ.Contesta només preguntes relaciones amb " + parlantTema + " . Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon només 3 línies, cada frase en 1 linea, com si tingués 10 anys i anés a cinqué de primària. Afegeix també un exemple pràctic."
                        elif parlantNivell == 2:
                            additionalInstructions = "Si la pregunta no està relacionada amb:"+parlantTema+",no contestis.Respon en dos idiomes:"+parlantIdioma+"i CATALÀ.Contesta només preguntes relaciones amb " + parlantTema + ". Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon només 1 frase com si tingués 5 anys i anés a tercer de primària. Afegeix també un exemple pràctic i la resposta també en:"+ parlantIdioma
                        elif parlantNivell == 11:
                            additionalInstructions = "Si la pregunta no està relacionada amb:"+parlantTema+",no contestis.Respon en dos idiomes: CATALÀ i després fes la traducció de la resposta al " + parlantIdioma + " .Contesta només preguntes relaciones amb " + parlantTema + ". Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon només 1 frase com si tingués 9 anys i anés a cinquè de primària. Afegeix també un exemple pràctic."
                        elif parlantNivell == 4:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon en dos idiomes:" + parlantIdioma + "i CATALÀ.Contesta només preguntes relaciones amb " + parlantTema + ". Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon només 2 frases com si tingués 5 anys i anés a tercer de primària. Afegeix també un exemple pràctic i la resposta també en:" + parlantIdioma
                        elif parlantNivell == 5:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon només en català.Contesta només preguntes relaciones amb " + parlantTema + ". Contesta amb màxim 3 frases curtes.Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon com si tingués 5 anys i anés a tercer de primària."
                        elif parlantNivell == 6:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon només en català i urdú.Contesta només preguntes relaciones amb " + parlantTema + ". Contesta amb màxim 3 frases curtes.Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon com si tingués 5 anys i anés a tercer de primària."
                        elif parlantNivell == 7:
                            additionalInstructions = "Contesta siempre relacionando la pregunta con:" + parlantTema +".Para cada pregunta que realice, por favor proporciona la respuesta inicialmente en catalan. Luego, traduce esa respuesta al rumano. Si hay términos específicos o conceptos que no tienen un equivalente directo en rumano, por favor, indica esto y proporciona una explicación adecuada en ambos idiomas. Contesta con un màximo de 3 frases cortas.Al final, indica siempre que esta información la tienes que validar con la profesora. Responde como si tuviera 5 años y fuera a tercero de primaria."
                        elif parlantNivell == 8:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon només en català i xines.Contesta només preguntes relaciones amb " + parlantTema + ". Contesta amb màxim 3 frases curtes.Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon com si tingués 5 anys i anés a tercer de primària."
                        elif parlantNivell == 9:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon només en català i georgià.Contesta només preguntes relaciones amb " + parlantTema + ". Contesta amb màxim 3 frases curtes.Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon com si tingués 5 anys i anés a tercer de primària."
                        elif parlantNivell == 10:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon només en català i punjabí.Contesta només preguntes relaciones amb " + parlantTema + ". Contesta amb màxim 3 frases curtes.Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon com si tingués 5 anys i anés a tercer de primària."
                        elif parlantNivell == 11:
                            additionalInstructions = "Si la pregunta no està relacionada amb:" + parlantTema + ",no contestis.Respon només en català i francés.Contesta només preguntes relaciones amb " + parlantTema + ". Contesta amb màxim 3 frases curtes.Al final, digues sempre que aquesta info l'ha de validar amb la profesora. Respon com si tingués 5 anys i anés a tercer de primària."

                    #prompt = prompt + additionalInstructions
                    #st.markdown(prompt + parlantAdditional)
                    # Chat input for the user

                    message = client.beta.threads.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=prompt
                    )

                    # Create a run with additional instructions
                    run = client.beta.threads.runs.create(
                        thread_id=st.session_state.thread_id,
                        instructions=additionalInstructions,
                        assistant_id=assistant_id
                    )
                    
                    # Poll for the run to complete and retrieve the assistant's messages
                    while run.status != 'completed':
                        time.sleep(1)
                        run = client.beta.threads.runs.retrieve(
                            thread_id=st.session_state.thread_id,
                            run_id=run.id
                        )
                        xivato = "+++"


                    # Retrieve messages added by the assistant
                    messages = client.beta.threads.messages.list(
                        thread_id=st.session_state.thread_id
                    )

                    # Process and display assistant messages
                    assistant_messages_for_run = [
                        message for message in messages
                        if message.run_id == run.id and message.role == "assistant"
                    ]

                    print('4')
                    xivato = "==="
                    full_response = ''
                    for message in assistant_messages_for_run:
                        full_response = process_message_with_citations(message)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})

                    with st.chat_message("assistant"):
                        st.markdown(full_response, unsafe_allow_html=True)

                    with st.chat_message("assistant"):
                        response = ''
                        response = client.audio.speech.create(
                            model="tts-1",
                            voice="alloy",
                            input=full_response,
                        )
                        elaudio = st.empty()
                        nomfitxer = "output_"+str(count)+"_"+str(parlantID)+"_"+username+"_.mp3"
                        count +=1
                        response.stream_to_file(nomfitxer)
                        with elaudio.container():
                            autoplay_audio(nomfitxer)

                        #st.session_state.messages.append({"role": "assistant", "content": autoplay_audio(nomfitxer)})
                        if os.path.exists(nomfitxer):
                            print('removed!')
                            os.remove(nomfitxer)
                        #st.markdown(autoplay_audio("output.mp3"), unsafe_allow_html=True)
                        #st.audio(autoplay_audio("output.mp3"))


                    with st.chat_message("assistant"):
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt="Fes una imatge realista i amb finalitats educatives a partir d'aquesta descripció:" + full_response + ". Si surten persones que siguin de diversitat etnica.",
                            size="1024x1024",
                            quality="standard",
                            n=1
                        )
                        st.image(response.data[0].url, caption='')

                        # Crea una conexión con la base de datos
                        conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                                       password=db_password)

                        # Crea un cursor para ejecutar comandos SQL
                        cur = conn.cursor()

                        # Ejecuta una consulta SQL
                        sql = "INSERT INTO teclaPREGUNTES (id,pregunta, resposta,infografia,tema) VALUES (%s,%s,%s,%s,%s)"

                        valores = (parlantID, elmissatge, full_response, response.data[0].url, parlantTemaID)
                        cur.execute(sql, valores)

                        # Obtiene los resultados de la consulta
                        results_database = cur.fetchall()
                        conn.commit()

                        # Cierra la conexión con la base de datos
                        cur.close()
                        conn.close()
                        
                except Exception as e:
                    st.error(f"An error occurred while retrieving the run: {e}")
                    # Crea una conexión con la base de datos
                    conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,
                                                   password=db_password)

                    # Crea un cursor para ejecutar comandos SQL
                    cur = conn.cursor()

                    # Ejecuta una consulta SQL
                    sql = "INSERT INTO teclaPREGUNTES (id,pregunta, resposta,infografia,tema) VALUES (%s,%s,%s,%s,%s)"

                    valores = (parlantID, elmissatge, f"VIGILA:{e}", "VIGILA", parlantTemaID)
                    cur.execute(sql, valores)

                    # Obtiene los resultados de la consulta
                    results_database = cur.fetchall()
                    conn.commit()

                    # Cierra la conexión con la base de datos
                    cur.close()
                    conn.close()




if __name__ == '__main__':
    parlant_amb()
