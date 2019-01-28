
rem git clone https://github.com/HASTE-project/desktop-agent

rem git pull

C:/users/IEUSer/AppData/Local/Programs/Python/Python37-32/python.exe -m pip install -e .

C:/users/IEUSer/AppData/Local/Programs/Python/Python37-32/python.exe -m haste.desktop_agent --include .tif --tag vironova --username haste --password letmein %tmp%\foo


pause
