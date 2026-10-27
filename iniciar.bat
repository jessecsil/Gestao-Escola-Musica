@echo off
cd /d "D:\faculdade 5 periodo\trilha gelter\app_gestao"

echo Abrindo o Visual Studio Code...
code .

echo Iniciando o Streamlit no navegador...
python -m streamlit run app.py
pause