window.BENCHMARK_DATA = {
  "lastUpdate": 1596301041827,
  "repoUrl": "https://github.com/SaltieRL/carball",
  "entries": {
    "Carball Benchmarks short_sample": [
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
        "date": 1588354600711,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.7970441034287731,
            "unit": "iter/sec",
            "range": "stddev: 0.014330996697547907",
            "extra": "mean: 1.2546357167666617 sec\nrounds: 10"
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
        "date": 1588441556522,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.8334493276479993,
            "unit": "iter/sec",
            "range": "stddev: 0.018728356055060735",
            "extra": "mean: 1.1998329914333339 sec\nrounds: 10"
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
        "date": 1588451296416,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.8930344604838997,
            "unit": "iter/sec",
            "range": "stddev: 0.010219842775693095",
            "extra": "mean: 1.1197776169333262 sec\nrounds: 10"
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
        "date": 1592507168428,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.899917375607017,
            "unit": "iter/sec",
            "range": "stddev: 0.007431821317809326",
            "extra": "mean: 1.1112131259000022 sec\nrounds: 10"
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
          "id": "07297fe677daa4227af8f9ffecc5b088818d5217",
          "message": "Revert benchmarking.yml python version. (#249)\n\n* Revert benchmarking.yml python version.\r\n\r\n3.6.10 > 3.7 (Integrate Boxcars commit changed this for some reason)\r\n\r\n* Update benchmarking.yml",
          "timestamp": "2020-08-01T10:50:37-06:00",
          "tree_id": "93f57b62e7dd2d4a4394e491422f73f85b272208",
          "url": "https://github.com/SaltieRL/carball/commit/07297fe677daa4227af8f9ffecc5b088818d5217"
        },
        "date": 1596301024400,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.8667843933942438,
            "unit": "iter/sec",
            "range": "stddev: 0.033132074823376975",
            "extra": "mean: 1.15368943836667 sec\nrounds: 10"
          }
        ]
      }
    ]
  }
}