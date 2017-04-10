set /p bfres="BFRES Filename: "
quickbms.exe BFRES_Textures.bms %bfres% Convert
cp -a ./Convert/%bfres%/. ./Convert/
rm -rf ./Convert/%bfres%