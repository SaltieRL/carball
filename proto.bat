echo "Creating proto files"

%CD%\replay_analysis\generated\protoc.exe --proto_path=%CD% --python_out=%CD%\replay_analysis\generated %CD%\**\*.proto
%CD%\replay_analysis\generated\protoc.exe --proto_path=%CD% --python_out=%CD%\replay_analysis\generated %CD%\api\**\*.proto

echo "Proto files are created"

echo "Fixing protobuf relative imports dumbness"

python ./import_fixer.py

echo "Protobuf imports are now fixed"
