# PapagoAPI
### using papagoapi with python

#### Requirements 
1. attrdict library   
    `pip install attrdict`   
    
2. client.json file 
3. config.json file 

* If you do not have json files, you can use create_jsons.ipynb to create them **

#### about config.json 


#### Translate tutorial
    $ python Papago-Translate.py --task {$TASK_NAME} --config-dir {$CONFIG_DIR} --config-file {$CONFIG_FILE}   
    $ python Papago-Translate.py --task translate --config-dir config --config-file translate_config.json
    $ python Papago-LD.py --task ld --config-dir config --config-file ld_config.json
   
**Reference**   
https://developers.naver.com/docs/papago/README.md   
https://docs.python.org/3/tutorial/errors.html   
https://github.com/python/cpython/blob/3.11/Lib/urllib/error.py
