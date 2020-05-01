window.BENCHMARK_DATA = {
  "lastUpdate": 1588353316788,
  "repoUrl": "https://github.com/SaltieRL/carball",
  "entries": {
    "Carball Benchmarks": [
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
          "id": "be2a4c30a17e56e626771b65f40f464fb436c617",
          "message": "Support benchmarking reports and lower the benching time.",
          "timestamp": "2020-05-01T16:42:15+01:00",
          "tree_id": "38bd5aab1289a86adae2847de632bca7606199db",
          "url": "https://github.com/SaltieRL/carball/commit/be2a4c30a17e56e626771b65f40f464fb436c617"
        },
        "date": 1588349280521,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.897876357689665,
            "unit": "iter/sec",
            "range": "stddev: 0.024073217233087665",
            "extra": "mean: 1.1137390927333362 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_dropshot",
            "value": 0.6458686769909995,
            "unit": "iter/sec",
            "range": "stddev: 0.02215070504542632",
            "extra": "mean: 1.5483023649000018 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_full_rumble",
            "value": 0.06117835886108377,
            "unit": "iter/sec",
            "range": "stddev: 0.6033252347967283",
            "extra": "mean: 16.34564932136666 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.06108185246140247,
            "unit": "iter/sec",
            "range": "stddev: 0.24623270792862642",
            "extra": "mean: 16.371474663966662 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs_intensive",
            "value": 0.054039699082174666,
            "unit": "iter/sec",
            "range": "stddev: 0.16454681343406521",
            "extra": "mean: 18.50491429419999 sec\nrounds: 5"
          }
        ]
      },
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
          "id": "cf2162ed3d19aa299ed9b41ddf7e354297cdea95",
          "message": "Use appropriate GH token.",
          "timestamp": "2020-05-01T17:17:51+01:00",
          "tree_id": "11d2c84290a56278d723fc101aa79665d08ca523",
          "url": "https://github.com/SaltieRL/carball/commit/cf2162ed3d19aa299ed9b41ddf7e354297cdea95"
        },
        "date": 1588351757157,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.7050307330806994,
            "unit": "iter/sec",
            "range": "stddev: 0.03022050037056977",
            "extra": "mean: 1.418377884933333 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_dropshot",
            "value": 0.539799091882344,
            "unit": "iter/sec",
            "range": "stddev: 0.024505116076094523",
            "extra": "mean: 1.852541093599992 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_full_rumble",
            "value": 0.04811986639941799,
            "unit": "iter/sec",
            "range": "stddev: 0.08466977021111999",
            "extra": "mean: 20.781437581299997 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.049629694764698605,
            "unit": "iter/sec",
            "range": "stddev: 0.19747096100517594",
            "extra": "mean: 20.149227287033327 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs_intensive",
            "value": 0.0440867988409029,
            "unit": "iter/sec",
            "range": "stddev: 0.0924475456060933",
            "extra": "mean: 22.682526885399966 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "dtracers@gmail.com",
            "name": "dtracers",
            "username": "dtracers"
          },
          "committer": {
            "email": "dtracers@gmail.com",
            "name": "dtracers",
            "username": "dtracers"
          },
          "distinct": true,
          "id": "bb898cbc84dc99828202f9c97f30eca0e4e63e76",
          "message": "split up files to increase performance",
          "timestamp": "2020-05-01T09:46:47-07:00",
          "tree_id": "828397188c5a0e2da6c80d287af425b5a52e5b6a",
          "url": "https://github.com/SaltieRL/carball/commit/bb898cbc84dc99828202f9c97f30eca0e4e63e76"
        },
        "date": 1588353199713,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.8383283438001359,
            "unit": "iter/sec",
            "range": "stddev: 0.013969634230780553",
            "extra": "mean: 1.19285004186666 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_dropshot",
            "value": 0.6217107609612925,
            "unit": "iter/sec",
            "range": "stddev: 0.01135094999661696",
            "extra": "mean: 1.6084650013999995 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_full_rumble",
            "value": 0.05796918422604314,
            "unit": "iter/sec",
            "range": "stddev: 0.25200401513316373",
            "extra": "mean: 17.250544635933334 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.05985297152522901,
            "unit": "iter/sec",
            "range": "stddev: 0.23491063558600092",
            "extra": "mean: 16.70760823593334 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs_intensive",
            "value": 0.05388653570993536,
            "unit": "iter/sec",
            "range": "stddev: 0.1618768112757941",
            "extra": "mean: 18.55751138620003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "dtracers@gmail.com",
            "name": "dtracers",
            "username": "dtracers"
          },
          "committer": {
            "email": "dtracers@gmail.com",
            "name": "dtracers",
            "username": "dtracers"
          },
          "distinct": true,
          "id": "bb898cbc84dc99828202f9c97f30eca0e4e63e76",
          "message": "split up files to increase performance",
          "timestamp": "2020-05-01T09:46:47-07:00",
          "tree_id": "828397188c5a0e2da6c80d287af425b5a52e5b6a",
          "url": "https://github.com/SaltieRL/carball/commit/bb898cbc84dc99828202f9c97f30eca0e4e63e76"
        },
        "date": 1588353309566,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_sample",
            "value": 0.8092248827435573,
            "unit": "iter/sec",
            "range": "stddev: 0.02560887716276641",
            "extra": "mean: 1.2357504339333312 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_short_dropshot",
            "value": 0.6202283358507448,
            "unit": "iter/sec",
            "range": "stddev: 0.05242622686216543",
            "extra": "mean: 1.612309438633332 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_full_rumble",
            "value": 0.0551705689537067,
            "unit": "iter/sec",
            "range": "stddev: 0.15628066262601348",
            "extra": "mean: 18.125606078833336 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs",
            "value": 0.05387415278186126,
            "unit": "iter/sec",
            "range": "stddev: 0.8068972204097657",
            "extra": "mean: 18.561776814366674 sec\nrounds: 10"
          },
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_oce_rlcs_intensive",
            "value": 0.04638585276300204,
            "unit": "iter/sec",
            "range": "stddev: 0.5018478207891238",
            "extra": "mean: 21.558297205600002 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}