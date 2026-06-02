# HASTE Desktop Agent

Desktop client which watches a directory and streams new/modified files to HASTE. Intended for use with the HASTE Cloud Gateway (https://github.com/HASTE-project/haste-gateway)
Part of the HASTE Toolkit for intelligent stream-processing of life science datasets.

The tool demonstrates a novel approach for smart prioritization of processing tasks for computation at the cloud edge.
Processing is prioritized locally (at the edge) where it is predicted to yield the greatest reduction in message size, with other work left for the cloud.
This yields a mimimum stream-processing makespan in cases where overall throughput is bound by upload bandwidth. 

In its simplest configuration, it simply monitors a directory for new files, then performs a HTTP POST for each new file. The novelty is in smart prioritization of a file-size reducing local operator.


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

# To Run Benchmarking

Please follow the steps [instructions on the benchmarking-results branch](https://github.com/HASTE-project/haste-agent/tree/benchmarking-results), which was used to generate the results for the paper.


# Contact

I'd be keen to hear from you! (myfirstname).(mylastname)@mau.se
