import streamlit as st
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig
from fpdf import FPDF
import base64

import smtplib
from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

DATA_URL=("/Users/gaponce/Documents/StreamlitF/NotasP1.csv")

def read_template(filename):
 with open(filename, 'r', encoding='utf-8') as template_file:
  template_file_content = template_file.read()
  return Template(template_file_content)

session_state= {
    "button_clicked1": False, "button_clicked2": False, "button_clicked3": False }


#Inicialize state
if "button_clicked1" not in st.session_state:    
    st.session_state.button_clicked1 = False

if "button_clicked2" not in st.session_state:    
    st.session_state.button_clicked2 = False

if "button_clicked3" not in st.session_state:    
    st.session_state.button_clicked3 = False


def callback1():
    #Button was clicked
    st.session_state.button_clicked1=True

def callback2():
    #Button was clicked
    st.session_state.button_clicked2=True

def callback3():
    #Button was clicked
    st.session_state.button_clicked3=True


def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'


st.title("RA - Relatório de Avaliação ")
st.markdown("Este web app foi desenvolvido pelo professor Gabriel Ponce do IMECC-UNICAMP. \
             Seu objetivo principal é gerar relatórios simples sobre o rendimento da turma \
             e enviar emails com os rendimentos individuais aos estudantes. \
             Selecione um arquivo de notas (.csv) e marque na coluna da esquerda sobre quais informações \
             você deseja que sejam gerados histogramas de rendimento. Depois você pode exportar os gráficos \
             em .pdf e enviar emails aos estudantes contendo informações sobre o rendimento de cada um.")


upload_file= st.file_uploader('Selecione o arquivo de notas', type=['.csv'],
                              help='Selecione um arquivo .csv . \
                              É importante que as colunas \
                              sigam a ordem Nome, RA, 1, 2, ....')



    
if upload_file is not None:
 NOTASdata=pd.read_csv(upload_file, delimiter=';')
 ver_documento=st.button("Ver arquivo selecionado.", on_click=callback1)
 if (ver_documento or st.session_state.button_clicked1):
  st.write(NOTASdata)
  for indice in NOTASdata.columns[~NOTASdata.columns.isin(['Nome','RA','Obs'])]:
      NOTASdata[indice]=pd.to_numeric(NOTASdata[indice])

  NoT=NOTASdata[NOTASdata.columns[~NOTASdata.columns.isin(['Nome','RA','Obs'])]]
  cols = list(NoT.columns)
  st.sidebar.write('### Gerar gráfico das colunas:')
  check_boxes = [st.sidebar.checkbox(col, key=col) for col in cols]
  col1 = [col for col, checked in zip(cols, check_boxes) if checked]
  for i in col1:
    st.write('###',i)
    figs, ax = plt.subplots(figsize = (6,4))
    NOTASdata[i].plot(kind='hist',alpha=0.5,bins=10)
    st.pyplot(figs)

if upload_file is not None:
  export_as_pdf = st.button("Gerar Relatório",on_click=callback2)
  if (export_as_pdf or st.session_state.button_clicked2):
   report_text_title = st.text_input("Título do documento.")
   report_text_description = st.text_input("Descrição breve.")
   pdf = FPDF()
   pdf.add_page()
   pdf.set_font('Arial', 'B', 24)
   pdf.cell(40, 10, report_text_title)
   pdf.set_font('Helvetica', '', 12)
   pdf.cell(50,15, report_text_description)
   html = create_download_link(pdf.output(dest="S").encode("latin-1"), "Relatório de Rendimento da Turma")
   st.markdown(html, unsafe_allow_html=True)

   Send_emails=st.button("Send Emails", on_click=callback3)
   if (Send_emails or st.session_state.button_clicked3):
 #organizando SMTP server
      MY_ADDRESS = 'gabriel.ponc@gmail.com'  #your gmail account address
      PASSWORD = 'rofdfnqifenlvqgu'          #your password
      s = smtplib.SMTP(host="smtp.gmail.com", port=587)
      s.starttls()
      s.login(MY_ADDRESS, PASSWORD)
     
     #with open(upload_file) as csv_file:
      #csv_reader = csv.reader(upload_file, delimiter=';')
      #st.write(csv_reader)
      #next(csv_reader)
      #print(csv_reader)
      #Função para ler o arquivo


      message_template=read_template('templateNotasProvinha1.txt')
      for lines in NOTASdata.itertuples():
                 msg=MIMEMultipart() # Create a message
                 #if pd.isna(lines[11]):
                  #   Observ = '-'
                 #else:
                  #   Observ = lines[11]
                 message= message_template.substitute(PERSON_NAME=lines[1],questaouma=lines[3], questaoumb=lines[4], \
                                                      questaodois=lines[5],total=lines[6], \
                                                      Comentarios=lines[7])
                 

                 #Prints out the message body for our sake
                 #print(msg)

                 #setup the parameters of the message
                 msg['From']= MY_ADDRESS
                 msg['To']= lines[1].lower()[0]+str(lines[2])+'@dac.unicamp.br'
                 msg['Subject']="Notas Provinha 1 - MA507 Turma Z."

                 #add in the message body
                 msg.attach(MIMEText(message,'plain'))
                 #attach_file_name = 'RelatórioDeRendimento.pdf'
                 #attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
                 #payload = MIMEBase('application', 'octate-stream', Name=attach_file_name)
                 #payload.set_payload((attach_file).read())
                 #encoders.encode_base64(payload) #encode the attachment
                #####add payload header with filename
                 #payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
                 #msg.attach(payload)

                 #send the message via the server set up earlier
                 s.send_message(msg)
                 del msg

                 print('Message sent')
      st.write("Emails Enviados Com Sucesso!")
      s.quit()









  #Terminate the SMTP session and close


