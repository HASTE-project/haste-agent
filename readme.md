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

0. Clone this repository.
0. Deploy the HASTE Gateway according to (the instructions)[https://github.com/HASTE-project/haste-gateway] in that repository. Note the credentials.
1. Download the dataset.'
2. Modify ./haste/desktop_agent/config.py so that the source dir points to the directory containing the source images, and that the target dir maps to an empty directory.
3. Install the HASTE agent:
```
python3 -m pip install -e .
```
4. Run the benchmarking harness (this will repeat the experiment using the various algorithms for prioritizing client-side processing):
```
python3 -m haste.desktop_agent.benchmarking
```
5. Afterwards, the script `results_analysis_benchmark.py` can be used to generate the plots seen in the paper!


Note that the results will depend on the performance of the machine, and the upload rate, the upload bandwidth needs to be limited if you are attempting to reproduce the results. 
There are a number of utilities to do this, such as: https://apple.stackexchange.com/questions/112329/limit-my-upload-speed-at-os-level

# Contact

I'd be keen to hear from you! ben.blamey@it.uu.se