[![Build Status](https://travis-ci.org/SaltieRL/carball.svg?branch=master)](https://travis-ci.org/SaltieRL/carball)
[![PyPI version](https://badge.fury.io/py/carball.svg)](https://badge.fury.io/py/carball)
[![codecov](https://codecov.io/gh/SaltieRL/carball/branch/master/graph/badge.svg)](https://codecov.io/gh/SaltieRL/carball)
[![Build status](https://ci.appveyor.com/api/projects/status/jxsa56l11fxv4jn4/branch/master?svg=true)](https://ci.appveyor.com/project/SaltieRL/carball/branch/master)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/SaltieRL/carball.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/SaltieRL/carball/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/SaltieRL/carball.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/SaltieRL/carball/alerts/)


# carball
Carball is an open-source project that combines multiple tools for decompiling Rocket League replays and then analysing them.

## Requirements

- Python 3.6.7+ (3.7 and 3.8 included)
- Windows, Mac or Linux

## Install

#### Install from pip:

`pip install carball`

#### Clone for development

##### Windows
```
git clone https://github.com/SaltieRL/carball
cd carball/
python init.py
```

##### Linux
```
git clone https://github.com/SaltieRL/carball
cd carball/
./_travis/install-protoc.sh
python init.py
```

## Examples / Usage
One of the main data structures used in carball is the pandas.DataFrame, to learn more, see [its wiki page](https://github.com/SaltieRL/carball/wiki/data_frame "DataFrame").

### Decompile a Replay
```Python
from carball import decompile_replay

# This is the path to your replay file (.replay file extension)
# On Windows, by default, Rocket League saves replays in C:\Users\%USER%\Documents\My Games\Rocket League\TAGame\Demos
replay_path = 'path/to/your/replayID.replay'

# This is the path where the replay's JSON file will be stored. It is recommended to use the replay ID as the file name.
output_path = 'path/to/desired/location/replayID.json'

# Returns the JSON object for the given replay.
_json = decompile_replay(replay_path, output_path=output_path,overwrite=True)
```

### Analyse a Replay
If you haven't manually decompiled the replay, use the following:
```Python
from carball import analyze_replay_file

# This is the path to your replay file (.replay extension)
# On Windows, by default, Rocket League saves replays in C:\Users\%USER%\Documents\My Games\Rocket League\TAGame\Demos
replay_path = 'path/to/your/replayID.replay'

# This is the path where the replay's JSON file will be stored. 
output_path = 'path/to/desired/location/replayID.json'

# The analyze_replay_file() method creates an instance of AnalysisManager and also runs the analysis.
analysis_manager = analyze_replay_file(replay_path, output_path=output_path,overwrite=True)
```

If you have a decompiled replay, as a JSON file (e.g. ```_json```), use the following:
```Python
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager

# Create and intialise the Game object.
game = Game()
game.initialize(loaded_json=_json)

# Create an AnalysisManager object and run the analysis.
analysis_manager = AnalysisManager(game)
analysis_manager.create_analysis()
```

### Retrieve Analysis Data
Once you have created and ran the analysis, you can retrieve each of the data types by using the following methods:
```Python
# Returns the Protobuf object
proto_object = analysis_manager.get_protobuf_data()

# Returns the Protobuf object as a json object
json_object = analysis_manager.get_json_data()

# Returns the DataFrame object
data_frame = analysis_manager.get_data_frame()
```

You may also choose to write the analysed replay data into a file, so that you don't have to wait for all of the processes to run again:
```Python
import os
import gzip

# Writes the Protobuf data out to the given file. The file mode is 'wb' for 'write bytes'.
# See api/*.proto for all fields and properties.
with open(os.path.join('output.pts'), 'wb') as file:
    analysis_manager.write_proto_out_to_file(file)
    
# Writes the pandas.DataFrame data out to the given file, as a gzipped numpy array. The file mode is 'wb' for 'write bytes'.
with gzip.open(os.path.join('output.gzip'), 'wb') as file:
    analysis_manager.write_pandas_out_to_file(file)
```


### Command Line

Carball comes with a command line tool to analyze replays. To use carball from the command line:

```bash
carball -i 9EB5E5814D73F55B51A1BD9664D4CBF3.replay --json analysis.json
```

To get the analysis in both json and protobuf and also the compressed replay frame data frame:

```bash
carball -i 9EB5E5814D73F55B51A1BD9664D4CBF3.replay --json analysis.json --proto analysis.pts --gzip frames.gzip
```

#### Command Line Arguments

```
usage: carball [-h] -i INPUT [--proto PROTO] [--json JSON] [--gzip GZIP] [-sd]
               [-v] [-s]

Rocket League replay parsing and analysis.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path to replay file that will be analyzed. Carball
                        expects a raw replay file unless --skip-decompile is
                        provided.
  --proto PROTO         The result of the analysis will be saved to this file
                        in protocol buffers format.
  --json JSON           The result of the analysis will be saved to this file
                        in json file format. This is not the decompiled replay
                        json from rattletrap.
  --gzip GZIP           The pandas dataframe will be saved to this file in a
                        compressed gzip format.
  -sd, --skip-decompile
                        If set, carball will treat the input file as a json
                        file that Rattletrap outputs.
  -v, --verbose         Set the logging level to INFO. To set the logging
                        level to DEBUG use -vv.
  -s, --silent          Disable logging altogether.
```

## Pipeline
![pipeline is in Parserformat.png](Parser%20format.png)

If you want to add a new stat it is best to do it in the advanced stats section of the pipeline.
You should look at:

[Stat base classes](carball/analysis/stats/stats.py)

[Where you add a new stat](carball/analysis/stats/stats_list.py)

If you want to see the output format of the stats created you can look [here](api)

Compile the proto files by running in this directory
`setup.bat` (Windows) or `setup.sh` (Linux/mac)

[![Build Status](https://travis-ci.org/SaltieRL/carball.svg?branch=master)](https://travis-ci.org/SaltieRL/carball)
[![codecov](https://codecov.io/gh/SaltieRL/carball/branch/master/graph/badge.svg)](https://codecov.io/gh/SaltieRL/carball)


## Tips

Linux set `python3.6` as `python`:
```Python3
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1
```
This assumes you already have 3.6 installed.

Linux Error (Potential):
`PermissionError: [Errno 13] Permission denied: 'carball/rattletrap/rattletrap-6.2.2-linux'`
Fix:
`chmod +x "carball/rattletrap/rattletrap-6.2.2-linux"`


## Developing
Everyone is welcome to join the carball (and calculated.gg) project! Even if you are a beginner, this can be used as an opportunity to learn more - you just need to be willing to learn and contribute.

### Usage of GitHub
All contributions end up on the carball repository.  If you are new to the project you are required to use your own fork for first changes. If you do not have any previous git / github experience that is completely fine - we can help with it.
If we believe that you are comitted to working on the project and have experience in git we may give you write access so that you no longer have to use a fork. Nonetheless, please wait until your contrubtion is ready for a review to make the pull request because that will save resources for our tests and reduce spam.
For testing you should use your own fork, but take note that some carball tests may fail on a fork

### Learning about carball
Currently, there is active creation of the carball wiki on GitHub - it aims to provide all relevant information about carball and development, so if you are a beginner, definitely have a look there. If you can't find information that you were looking for, your next option is the calculated.gg Discord server, where you may send a message to the #help channel.

The carball code is also documented, although sparsely. However, you still may find information there, too.

### Testing
The main requirement is to run PyTest. If you are using an IDE that supports integrated testing (e.g. PyCharm), you should enable PyTest there. The secondary requirement (to compile the proto files) is to run the appropriate `setup` file (setup.bat for Windows, setup.sh for Linux/Mac).

If you've never tested your code before, it is a good idea to learn that skill with PyTest! Have a look at their official documentation, or any other tutorials. 

### carball Performance
Carball powers calculated.gg, which analyses tens of thousands of replays per day. Therefore, performance is very important, and it is monitored and controlled using PyTest-Benchmarking, which is implemented via GitHub Actions. However, you may see your contribution's performance locally - look into PyTest-Benchmarking documentation. If your contribution is very inefficient - it will fail automatically.

If you wish to see the current carball analysis performance, it is split into 5 replay categories, and can be accessed below:
* [Short Sample](https://saltierl.github.io/carball/dev/bench/short_sample/)
  * A very short soccar replay - for fast benchmarking.
* [Short Dropshot](https://saltierl.github.io/carball/dev/bench/short_dropshot/)
  * A very short dropshot replay - to test dropshot performance.
* [Rumble](https://saltierl.github.io/carball/dev/bench/full_rumble/)
  * A full game of rumble - to test rumble performance.
* [RLCS](https://saltierl.github.io/carball/dev/bench/oce_rlcs/)
  * A full soccar RLCS game.
* [RLCS (Intensive)](https://saltierl.github.io/carball/dev/bench/oce_rlcs_intensive/)
  * A full soccar RLCS game, but run with the intense analysis flag.
