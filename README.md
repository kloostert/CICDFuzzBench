# CometFuzz - Benchmarking Continuous Fuzzing

CometFuzz is a toolset that provides benchmarking for fuzzing in continuous integration practices. Several experiments are included that investigate the effectiveness and scalability of continuous fuzzing, by answering the following questions:

1. Is fuzzing all of the fuzz targets for every commit necessary, or is it sufficient to only fuzz the targets of which the code was changed by the latest commit? 
2. What is the optimal fuzzing duration that is compatible with CI/CD testing timelines, while maintaining the effectiveness of fuzzing?

This repository contains source code adapted from [Magma](https://hexhive.epfl.ch/magma/), a ground-truth fuzzing benchmark suite based on real programs with real bugs. The Magma project is maintained by the [HexHive](https://hexhive.epfl.ch/) group. The original repository can be found [here](https://github.com/HexHive/magma), and the corresponding paper [here](https://hexhive.epfl.ch/publications/files/21SIGMETRICS.pdf).



## Structure 
---

This repository contains the following subdirectories:

| Directory | Description |
| ----------- | ----------- |
| [experiments](experiments) | Contains the source code, logs, and visualizations of the experiments. |
| [fuzzers](fuzzers) | Contains the available fuzzers that can be used in the benchmark.  |
| [magma](magma) | Contains the actual Magma benchmark source code. |
| [targets](targets) | Contains the available target libraries that can be used in the benchmark.  |
| [tools](tools) | Contains Magma tools for configuring and running the benchmark. |



## Requirements 
---

In order to run the Magma benchmark adapted for CI-fuzzing, there are several requirements. This section shows how to set up the benchmark properly.

### Install dependencies
- git
- patch
- docker
- python3
- pip3
- pandas
- plotly

### Superuser rights
- sudo (to mount temporary filesystem for faster execution)

### AFL core pattern
```
echo core >/proc/sys/kernel/core_pattern
```

### Initialize results directory
```
mkdir -p results/{TARGET}/artificial/0000
```

### Download corpora
- clone CometFuzz (experiments and metrics)
- clone magma (bugs and corpora)

### Clone target libraries
(For more efficient benchmarking...)
- clone libpng (target library)
- clone libsndfile (target library)
- clone libtiff (target library)
- clone libxml2 (target library)
- clone lua (target library)
- clone openssl (target library)
- clone php (target library)
- clone poppler (target library)
- clone sqlite3 (target library)
- clone freetype2 (poppler addition)

### Set up target libraries
Checkout base commits and execute the additional fetch steps!

### Inject bugs
Inject bugs into the target libraries!

### Clone fuzzers
(For more efficient benchmarking...)
- clone aflplusplus
- clone honggfuzz
- clone libfuzzer

### Set up fuzzers
Checkout base commits and execute the additional fetch steps!



## Usage 
---

- How to run the benchmark?
- How to run the experiments?
