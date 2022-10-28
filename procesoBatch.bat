@echo off
cmd /k "cd /d C:\practicas_2022\05Bimestre\ComputacionNube\Proyecto\2158_proyecto\venv\Scripts & activate & cd /d    C:\practicas_2022\05Bimestre\ComputacionNube\Proyecto\2158_proyecto\ConversorAudios\micro1_batch & python app.py

taskkill /F /IM cmd.exe


exit /B