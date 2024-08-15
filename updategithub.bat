@echo off
REM Navigate to the project directory
cd /d "G:\Meu Drive\felquinhas.py\.venv\Random-Video-Splitter"

REM Install pipreqs if not already installed
pip install pipreqs

REM Generate the requirements.txt file
pipreqs . --force

REM Add all changes to the staging area
git add .

REM Commit the changes with a message
git commit -m "Update files and regenerate requirements.txt"

REM Push the changes to the remote repository
git push

REM Pause to see the results
pause
