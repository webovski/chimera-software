echo off

pyinstaller main.py --add-data "web;web" --add-data "electron;electron" --add-data "main.js;electron/resources/app" --add-data "preloader.js;electron/resources/app" --add-data "splash.html;electron/resources/app" --add-data "async_eel;async_eel" --add-data "app.ico;electron/resources/app" --add-data "package.json;electron/resources/app" --onefile --windowed --icon=app.ico --noconsole --hidden-import xlsxwriter;bottle_websocket --debug=bootloader

:cmd
pause null