import carball
import os
import gzip
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager


# _json is a JSON game object (from decompile_replay)
_json = carball.decompile_replay('626419D211E9452756B6A5B7AFE7DA87.replay',
	output_path='626419D211E9452756B6A5B7AFE7DA87.json',
	overwrite=True)

game = Game()
game.initialize(loaded_json=_json)

analysis = AnalysisManager(game)
analysis.create_analysis()

# Convert to CSV
df=analysis.get_data_frame()['Adriandro']
csvFile=df.to_csv(None, ',', "NaN", index=False)

# Write to csv
fd = open("Adriandro.csv", "w")
fd.write(csvFile)



# write proto out to a file
# read api/*.proto for info on the object properties
# with open(os.path.join('output.pts'), 'wb') as fo:
# 	analysis.write_proto_out_to_file(fo)
	
# # write pandas dataframe out as a gzipped numpy array
# with gzip.open(os.path.join('output.gzip'), 'wb') as fo:
# 	analysis.write_pandas_out_to_file(fo)