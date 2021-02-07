# HASTE Desktop Agent

Desktop client which watches a directory and streams new/modified files to HASTE. Intended for use with the HASTE Cloud Gateway (https://github.com/HASTE-project/haste-gateway)
Part of the HASTE Toolkit for intelligent stream-processing of life science datasets.

The tool demonstrates a novel approach for smart prioritization of processing tasks for computation at the cloud edge.
Processing is prioritized locally (at the edge) where it is predicted to yield the greatest reduction in message size, with other work left for the cloud.
This yields a mimimum stream-processing makespan in cases where overall throughput is bound by upload bandwidth. 

In its simplest configuration, it simply monitors a directory for new files, then performs a HTTP POST for each new file. The novelty is in smart prioritization of a file-size reducing local operator.

This tool is used in use-cases in microscopy applications, discussed in the following publications:
```
"Rapid development of cloud-native intelligent data pipelines for scientific data streams using the HASTE Toolkit"
https://www.biorxiv.org/content/10.1101/2020.09.13.274779v1
```

```
Resource- and Message Size-Aware Scheduling of Stream Processing at the Edge with application to Realtime Microscopy
https://arxiv.org/abs/1912.09088
```

## Command Line Arguments

```
usage: python3 -u -m haste.desktop-agent [-h] [--include [INCLUDE]]
                                         [--tag [TAG]] [--host [HOST]]
                                         [--username [USERNAME]]
                                         [--password [PASSWORD]]
                                         path

Watch directory and stream new files to HASTE

positional arguments:
  path                  path to watch (e.g. C:/docs/foo

optional arguments:
  -h, --help            show this help message and exit
  --include [INCLUDE]   include only files with this extension
  --tag [TAG]           short ASCII tag to identify this machine (e.g. ben-
                        laptop)
  --host [HOST]         Hostname for HASTE e.g. foo.haste.com:80
  --username [USERNAME]
                        Username for HASTE Cloud Gateway
  --password [PASSWORD]
                        Password for HASTE Cloud Gateway

```

(Known Issue: doesn't work when targeting a mounted dir under a Windows Guest/Mac Host)

# To Reproduce the Paper Results


0. Note on upload bandwidth limiting.
Note that the results will depend on the performance of the machine, and the upload rate, the upload bandwidth needs to be limited if you are attempting to reproduce the results. 
There are a number of utilities to do this, such as: https://apple.stackexchange.com/questions/112329/limit-my-upload-speed-at-os-level
Alternatively, one can enable the 'fake uploads' configuration option, which simulates a limited upload speed (set `FAKE_UPLOAD`to `True` in `config.py`)


0. Clone this repository.
```
git clone git@github.com:HASTE-project/haste-agent.git
```

1. Chekout the version presented in the paper:
```
git checkout 0.1
```

2. Install the HASTE agent:
```
python3 -m pip install -e .
```

3. Deploy the HASTE Gateway according to [the instructions](https://github.com/HASTE-project/haste-gateway) in that repository. Note the credentials.

4. The dataset requires some preparation to reproduce the results in the paper. There are two issues: (a) the published dataset is the original images from the miniTEM, these are greyscale images encoded as 3-channel color images. For the experiment, we use the same images, but correctly encoded as greyscale. (b) one of the cases in the benchmarking run is a baseline where all images are pre-processed with the flood-fill algorithm offline, this offline step needs to be run.

```
# Create a working directory tree, with sub-directories.
mkdir ~/haste_agent_benchmarking_images
mkdir ~/haste_agent_benchmarking_images/orig
mkdir ~/haste_agent_benchmarking_images/greyscale
mkdir ~/haste_agent_benchmarking_images/ffill
mkdir ~/haste_agent_benchmarking_images/target

# Download and unzip v1 of the image set into the 'orig' directory:
cd ~/haste_agent_benchmarking_images/orig
curl -L https://scilifelab.figshare.com/ndownloader/files/24165845 | tar -xz
```

5. Modify the configuration so that the paths are consistent with the above: 
./haste/desktop_agent/benchmarking/benchmarking_config.py

Remember to update the `HASTE_GATEWAY_*` host/credentials settings to match the gateway.

6. Run the dataset preparation:
```
python3 -m haste.desktop_agent.benchmarking.prep
```

This should populate the 'greyscale' and 'ffill' directories with the derived imagesets. 'target' remains empty for now.

7. Run the benchmarking harness (this will repeat the experiment using the various algorithms for prioritizing client-side processing):
```
python3 -m haste.desktop_agent.benchmarking
```

This will generate a set of log files for the multiple runs for their different configurations in the current working directory. 
It will try to run forever generating more data for an average makespan. 40 iterations will be 5 runs for each configuration, enough for a reasonable average.
Create a new subdirectory in `haste/desktop_agent/benchmarking/logs` (e.g. `run0`) and move this collection of log files, so they are kept together.
If you run the benchmarking harness multiple times, you might want to clear out the old log files so that all the data relates to a single 'run' of the benchmarking harness. 

We only need the makespan to generate the boxplots. We use grep to find the lines of log data we need, this file is read by the next Python script.
```
cd ./haste/desktop_agent/benchmarking/logs/run0
grep Queue_is_empty *.log > grepped.txt
``` 

8. Now, the script `results_analysis_benchmark.py` can be used to generate the plots seen in the paper. Set the variable `run` as above.
Figures will be generated in the `./haste/desktop_agent/benchmarking/figures` directory. The 'time_taken' plot will visualize the makespans as a boxplot, as shown in the paper.
`results_analysis_single_run_splines.py` can be used for a more detailed visualization  



# Contact

I'd be keen to hear from you! ben.blamey@it.uu.se