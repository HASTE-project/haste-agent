Desktop client which watches a directory and streams new/modified files to HASTE.


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
                        Username for HASTE
  --password [PASSWORD]
                        Password for HASTE

```

(Known Issue: doesn't work when targeting a mounted dir under a Windows Guest/Mac Host)