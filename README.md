# PapagoAPI
### Language Detection(LD), Translate with papagoapi (python)

## Requirements 
```python 
attrdict
```
```python
client.json file
config.json file
```

* Can customize & create client, config json file using create_jsons.ipynb **

## Setting config.json 



## How to Run 
```bash
$ python Papago-Translate.py --task {$TASK_NAME} --config-dir {$CONFIG_DIR} --config-file {$CONFIG_FILE}   
```

```bash
$ python Papago-Translate.py --task translate --config-dir config --config-file translate_config.json
$ python Papago-LD.py --task LD --config-dir config --config-file LD_config.json
```

Information config.json 
Task: translate, LD
source (translate config):  

   
## Reference  
- [Papago API Document](https://developers.naver.com/docs/papago/README.md) 
- [Python Error Document](https://docs.python.org/3/tutorial/errors.html)
- [UrlLib Error Document](https://github.com/python/cpython/blob/3.11/Lib/urllib/error.py)
- [Structure of code, KoELECTRA](https://github.com/monologg/KoELECTRA)
