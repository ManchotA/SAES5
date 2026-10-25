@echo off
rem Installe tout ce qu'il faut après un clone ou un pull, puis lance le front.
rem On peut le relancer sans risque, par exemple après un pull qui change les dépendances.
chcp 65001 >nul
cd /d "%~dp0"
set "NG_CLI_ANALYTICS=false"

echo === 1/4 Vérification des prérequis
where node >nul 2>&1
if errorlevel 1 (
    echo Node.js est introuvable : installe la version 24 LTS depuis https://nodejs.org puis relance.
    goto erreur
)
rem Versions acceptées par Angular 22 : 22.22.3+, 24.15+ ou 26+
node -e "const [a,b,c]=process.versions.node.split('.').map(Number); process.exit((a===22&&(b>22||(b===22&&c>=3)))||(a===24&&b>=15)||a>=26?0:1)"
if errorlevel 1 (
    for /f %%v in ('node --version') do echo Node.js %%v n'est pas supporté par Angular 22 : installe la version 24 LTS depuis https://nodejs.org
    goto erreur
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    echo Python 3.12 ou plus est introuvable : installe-le depuis https://www.python.org
    echo en cochant "Add python.exe to PATH", puis relance.
    goto erreur
)
echo OK

echo.
echo === 2/4 Installation du front
cd front
call npm ci --no-fund --no-audit
if errorlevel 1 (
    echo L'installation du front a échoué. Si le front tourne dans une autre fenêtre, ferme-la et relance.
    goto erreur
)
cd ..

echo.
echo === 3/4 Installation du back, peut prendre une minute
if not exist back\.venv\Scripts\python.exe (
    python -m venv back\.venv
    if errorlevel 1 (
        echo La création de l'environnement Python a échoué.
        goto erreur
    )
)
back\.venv\Scripts\python.exe -m pip install -q --disable-pip-version-check -r back\requirements-dev.txt
if errorlevel 1 (
    echo L'installation des dépendances Python a échoué.
    echo Si le dossier du projet a été déplacé, supprime back\.venv et relance.
    goto erreur
)
echo OK

echo.
echo === 4/4 Lancement du front
echo Le navigateur va s'ouvrir sur http://localhost:4200 une fois la compilation finie.
echo Pour arrêter : Ctrl+C dans cette fenêtre.
echo.
cd front
call npm start -- --open
goto fin

:erreur
echo.
echo Installation interrompue.

:fin
pause
