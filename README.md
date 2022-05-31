# CICDFuzzBench - Benchmarking Continuous Fuzzing

CometFuzz is a toolset that provides benchmarking for fuzzing in continuous integration practices. Several experiments are included that investigate the effectiveness and scalability of continuous fuzzing, by answering the following questions:

1. Is fuzzing all of the fuzz targets for every commit necessary, or is it sufficient to only fuzz the targets of which the code was changed by the latest commit? 
2. What is the optimal fuzzing duration that is compatible with CI/CD testing timelines, while maintaining the effectiveness of fuzzing?

This repository contains source code adapted from [Magma](https://hexhive.epfl.ch/magma/), a ground-truth fuzzing benchmark suite based on real programs with real bugs. The Magma project is maintained by the [HexHive](https://hexhive.epfl.ch/) group. The original repository can be found [here](https://github.com/HexHive/magma), and the corresponding paper [here](https://hexhive.epfl.ch/publications/files/21SIGMETRICS.pdf).



## Structure 

This repository contains the following subdirectories:

| Directory | Description |
| ----------- | ----------- |
| [experiments](experiments) | Contains the source code, logs, and visualizations of the experiments. |
| [fuzz-duration-data](experiments/fuzz%20duration/data/) | Contains the collected data of the fuzz duration experiment. |
| [target-selection-data](experiments/target%20selection/logs/) | Contains the collected data of the target selection experiment. |
| [fuzzers](fuzzers) | Contains the available fuzzers that can be used in the benchmark.  |
| [magma](magma) | Contains the actual Magma benchmark source code. |
| [targets](targets) | Contains the available target libraries that can be used in the benchmark.  |
| [tools](tools) | Contains Magma tools for configuring and running the benchmark. |



## Requirements 

In order to run the Magma benchmark adapted for CI-fuzzing, there are several requirements.

### Dependencies

There are several dependencies that are required to run the benchmark and the experiments:
- docker (the installation of which is system-dependent)
- git, patch (e.g. `apt install git patch`)
- python3, pip3 (e.g. `apt install python3.8 python3-pip`)
- pandas, plotly, kaleido (e.g. `pip3 install pandas plotly kaleido`)

### Superuser rights

In order to allow fuzzing campaigns to utilize a temporary filesystem (instead of the disk) for better performance, superuser rights are required to mount such a filesystem.
In order to set the core pattern for AFL-based fuzzers, superuser rights are required as well.

### AFL core pattern

The core pattern for AFL-based fuzzers should be set:
```
echo core | sudo tee /proc/sys/kernel/core_pattern
```

### Preparing the benchmark

There are several preparation steps that have to be done:

1. Initialize results directory (to store results properly)
2. Download seed corpora (to start fuzzing campaigns using a seed corpus)
3. Set up target libraries (to have a specific version of the libraries to fuzz)
4. Inject Magma bugs (to introduce bugs in the libraries for fuzzers to find)
5. Download fuzzers (to lower the download overhead of running multiple trials)
6. Prepare fuzz duration experiment (to copy needed files in the correct directory)

Which are all taken care of by the `prepare_benchmark.sh` script in the root of this repository.
Note that this script will create multiple directories in `../` (relative to the root of this repo)!



## Usage 

While the experiments can be replicated using the scripts provided here, the benchmark can be run independently as well:

### Running the benchmark

After having satisfied all the requirements from the previous section, the benchmark can be started with a specific library (e.g. openssl) like so:
```
python3 fuzz-duration.py openssl
```
Where configuration changes can (for now) only be done through editing this Python script.
The number of repeated trials can be configured along with the fuzzing campaing durations to include in the benchmark.
The target library can be specified on the command line directly, by replacing openssl by one of the other libraries that are avialable.

### Replicating the experiments

Running the fuzz duration experiment can be done by invoking:
```
./run_fuzz-duration.sh
```

Running the target selection experiment requires some extra work.
The experiments (for now) expect the cloned repository for the target libraries at `/home/ubuntu/targsel/{library_name}`.
So this path most probably has to be changed, according to the machine on which it will be running.
Additionally, the repository has to be cloned manually and the commit you want to start from has to be checked out before starting the experiment.
Individual target selection experiments (e.g. for openssl) can be started like so:
```
cd "./experiments/target selection/" && python3 targsel.py openssl
```

Running the target selection experiment for all libraries can be done by invoking:
```
cd "./experiments/target selection/" && ./run_experiments.sh
```
