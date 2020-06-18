window.BENCHMARK_DATA = {
  "lastUpdate": 1592507552763,
  "repoUrl": "https://github.com/SaltieRL/carball",
  "entries": {
    "Carball Benchmarks oce_rlcs": [
      {
        "commit": {
          "author": {
            "email": "DivvyCr@users.noreply.github.com",
            "name": "DivvyCr",
            "username": "DivvyCr"
          },
          "committer": {
            "email": "DivvyCr@users.noreply.github.com",
            "name": "DivvyCr",
            "username": "DivvyCr"
          },
          "distinct": true,
          "id": "bcc1a8cee5f096035713ca264410c4d69dc08aec",
          "message": "Final touches?",
          "timestamp": "2020-05-01T18:28:05+01:00",
          "tree_id": "9e35341b9c327b42b51b45f418e4f9065ce8fe35",
          "url": "https://github.com/SaltieRL/carball/commit/bcc1a8cee5f096035713ca264410c4d69dc08aec"
        },
        "date": 1588355208822,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.054604254911294156,
            "unit": "iter/sec",
            "range": "stddev: 0.19284145756466925",
            "extra": "mean: 18.313591159233336 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs_intensive",
            "value": 0.04855320417160526,
            "unit": "iter/sec",
            "range": "stddev: 0.05870499237634016",
            "extra": "mean: 20.595963069000028 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "54956345+DivvyCr@users.noreply.github.com",
            "name": "Divvy",
            "username": "DivvyCr"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "454cfd65360a1ef1ed05fef48d8789b1e6e692db",
          "message": "Support benchmarking reports and lower the benching time. (#242)\n\n* Support benchmarking reports and lower the benching time.\r\n\r\n* Support benchmarking reports and lower the benching time.\r\n\r\n* Use appropriate GH token.\r\n\r\n* split up files to increase performance\r\n\r\n* Final touches?\r\n\r\n* Only push on master\r\n\r\nComment all the time\r\n\r\n* fix invalid file\r\n\r\n* only run oce_rlcs\r\n\r\nintensive is skipped\r\n\r\n* make it run intensive as a separate only test\r\n\r\n* switch to using gh edit token for now\r\n\r\n* Split benchmarking action into 2 - one comments on all pushes, and the second uploads benchmarking data from pushes to master.\r\n\r\n* try to use the intensive version\r\n\r\nCo-authored-by: DivvyCr <DivvyCr@users.noreply.github.com>\r\nCo-authored-by: dtracers <dtracers@gmail.com>",
          "timestamp": "2020-05-02T10:39:36-07:00",
          "tree_id": "9804315e3662313d233f94e5050e03bf136f404f",
          "url": "https://github.com/SaltieRL/carball/commit/454cfd65360a1ef1ed05fef48d8789b1e6e692db"
        },
        "date": 1588442094031,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.055540758648192336,
            "unit": "iter/sec",
            "range": "stddev: 0.30932987465593165",
            "extra": "mean: 18.004795475233333 sec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "54956345+DivvyCr@users.noreply.github.com",
            "name": "Divvy",
            "username": "DivvyCr"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7f188c8f134394063801047625db8f21fdd83833",
          "message": "Update README.md (#243)\n\n* Update README.md\r\n\r\nExtensive development information. Benchmarking websites included!\r\n\r\n* Remove GitHub section.\r\n\r\nAlso add DataFrame link to wiki.\r\n\r\n* Small update to README.md\r\n\r\nReadded, but rephrased the GitHub section.\r\nAdded the tip to compile proto files for testing.",
          "timestamp": "2020-05-02T13:22:05-07:00",
          "tree_id": "e4449818026e41ccb80f9f62a048da964224b9c8",
          "url": "https://github.com/SaltieRL/carball/commit/7f188c8f134394063801047625db8f21fdd83833"
        },
        "date": 1588451775127,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.06239892238499711,
            "unit": "iter/sec",
            "range": "stddev: 0.5863510863501828",
            "extra": "mean: 16.025917784766666 sec\nrounds: 10"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "lngtrn94@gmail.com",
            "name": "Long Tran",
            "username": "Longi94"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5d4385d0964537f6df955de62c85c4993e5075f4",
          "message": "Integrate boxcars (#225)\n\n* decompile replay with boxcars\r\n\r\n* refactor header parsing to boxcars format\r\n\r\n* refactor frame parsing to boxcars format 1\r\n\r\n* update boxcars-py\r\n\r\n* readd flagged attribute handling\r\n\r\n* workaround for checking invalid actor ids\r\n\r\n* temp json file no longer needed\r\n\r\n* dropshot fixes\r\n\r\n* fix rotation on old replays\r\n\r\n* fix party leader parsing\r\n\r\n* fix error test\r\n\r\n* fix more tests\r\n\r\n* fix rest of the tests\r\n\r\n* clean up rattletrap\r\n\r\n* Added benchmarking to this pr\r\n\r\n* Add boxcars-py==0.1.1 to setup.py\r\n\r\n* Update benchmarking.yml\r\n\r\n* Update unsigned check for Engine.PlayerReplicationInfo:Team\r\n\r\n* Add safety check to GameEventHandler\r\n\r\n* add safety check for player team coming in at 4294967295\r\n\r\n* update boxcars-py to 0.1.2\r\n\r\n* handle new boxcars actor id format\r\n\r\n* update boxcars-py to 0.1.3\r\n\r\n* fix camera settings\r\n\r\n* Update version number\r\n\r\nCo-authored-by: dtracers <dtracers@gmail.com>\r\nCo-authored-by: Paul Seelman <paul_seelman@comcast.com>\r\nCo-authored-by: Sciguymjm <sciguymjm@gmail.com>",
          "timestamp": "2020-06-18T14:59:06-04:00",
          "tree_id": "e254184902743f058813b9d2d16dfc964ca0a0bc",
          "url": "https://github.com/SaltieRL/carball/commit/5d4385d0964537f6df955de62c85c4993e5075f4"
        },
        "date": 1592507535786,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.07423787066788361,
            "unit": "iter/sec",
            "range": "stddev: 0.1263874045242509",
            "extra": "mean: 13.470213935333339 sec\nrounds: 10"
          }
        ]
      }
    ]
  }
}