:: Note: Use cmd.exe calls so that one failure doesn't stop generation completely
set "MISSIONS_DIR=C:\Users\DCSServerUser\Saved Games\DCS.openbeta_server\Missions"
set "SEC_MISSIONS_DIR=C:\Users\DCSServerUser\Saved Games\DCS.openbeta_server_mod\Missions"

cd "C:\Users\DCSServerUser\Documents\dcs-mission-buzzer\"

timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --donotbuzz "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_FullMap_StaticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --clearweather "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_FullMap_ClearWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --weatherreport "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_FullMap_RealisticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --limitmap --donotbuzz "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_LimitedMap_StaticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --limitmap --clearweather "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_LimitedMap_ClearWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --limitmap "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_LimitedMap_RealisticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --donotbuzz --forcenight "%MISSIONS_DIR%\MA_Training_CA.miz" "%MISSIONS_DIR%\MA_Training_CA_Night.miz"

timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --donotbuzz "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_FullMap_StaticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --clearweather "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_FullMap_ClearWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --weatherreport "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_FullMap_RealisticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --limitmap --donotbuzz "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_LimitedMap_StaticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --limitmap --clearweather "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_LimitedMap_ClearWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --limitmap "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_LimitedMap_RealisticWX.miz"
timeout /t 1
cmd.exe /c dcs_mission_buzzer.exe --donotbuzz --forcenight "%MISSIONS_DIR%\MA_Training_SY.miz" "%MISSIONS_DIR%\MA_Training_SY_Night.miz"
timeout /t 1

cmd.exe /c xcopy "%MISSIONS_DIR%\MA_Training_CA_*.miz" "%SEC_MISSIONS_DIR%" /y
cmd.exe /c xcopy "%MISSIONS_DIR%\MA_Training_SY_*.miz" "%SEC_MISSIONS_DIR%" /y

timeout /t 5
