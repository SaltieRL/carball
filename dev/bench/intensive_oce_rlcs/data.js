window.BENCHMARK_DATA = {
  "lastUpdate": 1588441637548,
  "repoUrl": "https://github.com/SaltieRL/carball",
  "entries": {
    "Carball Benchmarks intensive_oce_rlcs": [
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
        "date": 1588441617575,
        "tool": "pytest",
        "benches": [
          {
            "name": "carball/tests/benchmarking/benchmarking.py::test_intensive_oce_rlcs",
            "value": 0.05268577788019987,
            "unit": "iter/sec",
            "range": "stddev: 0.36586274061110863",
            "extra": "mean: 18.980454313000006 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}