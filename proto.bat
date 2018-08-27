echo "Creating proto files"

for /f %%i in ('dir /a:d /s /b api') do "%CD%"\replay_analysis\generated\protoc.exe --proto_path="%CD%" --python_out="%CD%"\replay_analysis\generated %%i\*.proto
"%CD%"\replay_analysis\generated\protoc.exe --proto_path="%CD%" --python_out="%CD%"\replay_analysis\generated "%CD%"\api\*.proto

echo "Proto files are created"

echo "Fixing protobuf relative imports dumbness"

python ./import_fixer.py

echo "Protobuf imports are now fixed"
