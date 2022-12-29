# PapagoAPI
## Language Detection(LD), Translate using PapagoApi (python)

### Requirements 
```python 
attrdict
```
```python
client.json file
config.json file
```

*Can customize & create client.json, config.json using __create_jsons.ipynb__*


### About config.json 
##### 0) common 
- file_name - source file that you want to work with (type should be .csv)
- flag - 0 if task is the first (don't have log) else 1 (load previous log)
- col - column name containing the text you want to work with

##### 1) translate_config.json
- source - the original language
- target - the target language
- save_file - source file + translated result (column: 'translated', .csv)

##### 2) LD_config.json
- lang - language you want to detect
- save_file - files corresponding to the lang
- save_file2 - files not corresponding to the lang

##### 3) Language Code

Code | Language 
--|--
ko | Korean
en | English
ja | Japanese
zh-CN | Chinese
zh-TW | Chinese traditional
es | Spanish
fr | French
vi | Vietnamese
th | Thai
id | Indonesia

### How to Run 
*before run, you should delete all log files (log/LD/.pickle, log/translate/.pickle)*

```bash
$ python Papago-Translate.py --task {$TASK_NAME} --config-dir {$CONFIG_DIR} --config-file {$CONFIG_FILE}   
```

```bash
$ python Papago-Translate.py --task translate --config-dir config --config-file translate_config.json
$ python Papago-LD.py --task LD --config-dir config --config-file LD_config.json
```

   
### Reference  
- [Papago API Document](https://developers.naver.com/docs/papago/README.md) 
- [Python Error Document](https://docs.python.org/3/tutorial/errors.html)
- [UrlLib Error Document](https://github.com/python/cpython/blob/3.11/Lib/urllib/error.py)
- [Structure of code, KoELECTRA](https://github.com/monologg/KoELECTRA)
