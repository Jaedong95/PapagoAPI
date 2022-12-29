import os
import pandas as pd
import json
import argparse 

class Papago():
    def __init__(self, args):
        self.args = args
    
    def set_client(self):
        with open(os.path.join(self.args.client_path, self.args.client_file), 'r') as f:
            self.client = json.load(f)

    def load_data(self):
        self.data = pd.read_csv(os.path.join(self.args.data_path, self.args.task, self.args.file_name))
    
    def get_mean_length(self):
        return int(self.data[self.args.col].str.len().mean())  
    
    def save_data(self, file_name, lang_idx = None, nlang_idx = None, nlang_name=None, trans_idx=None, trans_txt=None):
        if self.args.task == 'translate':
            save_file = self.data.loc[trans_idx]
            save_file['translated'] = trans_txt
            save_file.reset_index(inplace=True, drop=True)
            save_file.to_csv(os.path.join(self.args.data_path, self.args.task, file_name), index=None)
        elif self.args.task == 'ld':
            save_file = self.data.loc[lang_idx]
            save_file.reset_index(inplace=True, drop=True)
            save_file.to_csv(os.path.join(self.args.data_path, self.args.task, file_name), index=None)
            save_file2 = self.data.loc[nlang_idx]
            save_file2.reset_index(inplace=True, drop=True)
            save_file2.to_csv(os.path.join(self.args.data_path, self.args.task, nlang_name), index=None)
        
        print(f'파일 저장 완료')
    