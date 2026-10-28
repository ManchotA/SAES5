@echo off
rem Lance le projet en développement : le back et le front, chacun dans sa fenêtre.
rem À utiliser après installer.bat. Pour arrêter, fermer les deux fenêtres.
chcp 65001 >nul
cd /d "%~dp0"
set "NG_CLI_ANALYTICS=false"

if not exist front\node_modules (
    echo Le front n'est pas installé : lance d'abord installer.bat.
    goto fin
)
if not exist back\.venv\Scripts\python.exe (
    echo Le back n'est pas installé : lance d'abord installer.bat.
    goto fin
)

rem Back : serveur FastAPI sur le port 8000, relancé automatiquement à chaque modification du code
if exist back\app\main.py (
    start "Back - port 8000" /d back cmd /k .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
    echo Back lancé sur http://localhost:8000
) else (
    echo Le back n'a pas encore de serveur : il sera lancé ici dès que back\app\main.py existera.
)

rem Front : serveur Angular sur le port 4200, qui redirige /api et /ws vers le back
start "Front - port 4200" /d front cmd /k npm start -- --open
echo Front lancé : le navigateur va s'ouvrir sur http://localhost:4200 une fois la compilation finie.
echo.
echo Pour arrêter : ferme les fenêtres « Back » et « Front ».

:fin
echo.
pause
