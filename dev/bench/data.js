window.BENCHMARK_DATA = {
  "lastUpdate": 1588349287737,
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
      }
    ]
  }
}