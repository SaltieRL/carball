echo "Creating proto files"
./replay_analysis/generated/protoc --proto_path=. --python_out=./replay_analysis/generated ./**/*.proto
./replay_analysis/generated/protoc --proto_path=. --python_out=./replay_analysis/generated ./api/**/*.proto

echo "Proto files are created"

echo "Fixing protobuf relative imports dumbness"

python3 ./import_fixer.py

echo "Protobuf imports are now fixed"
