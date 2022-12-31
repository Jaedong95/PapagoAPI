import urllib.request
import json
import os 
import pickle
import argparse 
from src import Papago
from attrdict import AttrDict
from urllib.error import HTTPError

class PapagoTranslate(Papago):
    def __init__(self, args):
        super().__init__(args)

    def language_translate(self, cli, text):
        '''
        지정한 cli를 이용하여 text (1 sentence)에 대해 번역 수행 
        '''
        encQuery = urllib.parse.quote(text)
        url = "https://openapi.naver.com/v1/papago/n2mt"
        data = "source=" + self.args.source + "&target=" + self.args.target + "&text=" + encQuery
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", cli[0])
        request.add_header("X-Naver-Client-Secret", cli[1])
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        
        return res['message']['result']['translatedText']
    
    def client_ld(self, s_idx, cli, papago_df):
        self.trans_idx = []
        self.trans_txt = []
        self.error_idx = []
        
        for idx in range(s_idx, len(papago_df)):
            try:
                translated = self.language_translate(cli, papago_df[self.args.col][idx])
                self.trans_idx.append(idx) 
                self.trans_txt.append(translated)
 
            except TypeError as te:
                print(f'{idx}에서 TypeError 발생 ! 해당 데이터 건너뜀')
                self.error_idx.append(idx)
                continue
            except HTTPError as he:
                print(f'HTTPError 발생 ! {idx}: {papago_df[self.args.col][idx]}')
                if he.code == 429:
                    print('오류 내용: 일일 번역 한도 초과', end='\n\n')
                    break
                
                if he.code == 500:
                    print('오류 내용: HTTP 통신 오류', end='\n\n')       
                    self.error_idx.append(idx)
                    continue 
            
        print(f'해당 Application 번역 종료 !')

    def load_log(self):
        print(f'이전 작업 기록들을 로드합니다.')
        with open(os.path.join(self.args.log_path, self.args.task, 'trans_idx.pickle'), 'rb') as f:
            trans_idx = pickle.load(f)

        with open(os.path.join(self.args.log_path, self.args.task, 'trans_txt.pickle'), 'rb') as f:
            trans_txt = pickle.load(f)
            
        with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'rb') as f:
            error_idx = pickle.load(f)
            
        return trans_idx, trans_txt, error_idx
        
    def save_log(self, trans_idx, trans_txt, error_idx):
        print(f'번역 작업 로그를 저장합니다.', end='\n\n')
        try:   # 이전 작업 기록이 있으면
            with open(os.path.join(self.args.log_path, self.args.task, 'trans_idx.pickle'), 'rb') as f:
                prev_trans_idx = pickle.load(f)
            prev_trans_idx.extend(trans_idx)
            with open(os.path.join(self.args.log_path, self.args.task, 'trans_idx.pickle'), 'wb') as f:
                pickle.dump(prev_trans_idx, f, pickle.HIGHEST_PROTOCOL)         
        except:   # 신규 기록이면 
            with open(os.path.join(self.args.log_path, self.args.task, 'trans_idx.pickle'), 'wb') as f:
                pickle.dump(trans_idx, f, pickle.HIGHEST_PROTOCOL)
                
        try:    
            with open(os.path.join(self.args.log_path, self.args.task, 'trans_txt.pickle'), 'rb') as f:
                prev_trans_txt = pickle.load(f)
            prev_trans_txt.extend(trans_txt)
            with open(os.path.join(self.args.log_path, self.args.task, 'trans_txt.pickle'), 'wb') as f:
                pickle.dump(prev_trans_txt, f, pickle.HIGHEST_PROTOCOL)         
        except:
            with open(os.path.join(self.args.log_path, self.args.task, 'trans_txt.pickle'), 'wb') as f:
                pickle.dump(trans_txt, f, pickle.HIGHEST_PROTOCOL)
        
        try:
            with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'rb') as f:
                prev_error_idx = pickle.load(f)
            prev_error_idx.extend(error_idx)
            with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'wb') as f:
                pickle.dump(prev_error_idx, f, pickle.HIGHEST_PROTOCOL)         
        except:
            with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'wb') as f:
                pickle.dump(error_idx, f, pickle.HIGHEST_PROTOCOL)
    

def main(cli_argse):
    print(cli_argse)
    with open(os.path.join(cli_argse.config_path, cli_argse.task, cli_argse.config_file)) as f:
        args = AttrDict(json.load(f))
    
    args.flag = 0  # 해당 파일을 처음 작업하는 경우: 0, 이어서 작업하는 경우: 1  
    papago = PapagoTranslate(args)
    papago.set_client()
    papago.load_data()
    client = papago.client
    data = papago.data
    
    s_idx = 0
    if args.flag == 1:
        trans_idx, trans_txt, error_idx = papago.load_log() 
        print(f'번역 시작 지점: {trans_idx[-1]}, 번역 데이터 개수: {len(trans_txt)}, 오류 개수: {len(error_idx)}')
        s_idx = trans_idx[-1] + 1 
        
    print(f'번역 작업 준비 완료 !', end='\n\n')

    for cls in client:
        print(f'{cls} 번역 작업중 ..')
        papago.client_ld(s_idx, client[cls], data)
        trans_idx = papago.trans_idx
        trans_txt = papago.trans_txt 
        error_idx = papago.error_idx
        papago.save_log(trans_idx, trans_txt, error_idx)
        trans_idx, trans_txt, error_idx = papago.load_log()
        try: 
            assert trans_idx[-1]   # trans_idx = []인 경우 오류 발생 
            if trans_idx[-1] == len(data) - 1:
                print(f'{args.file_name} 파일에 대한 번역 작업이 모두 종료되었습니다.')
                papago.save_data(args.save_file, trans_idx=trans_idx, trans_txt=trans_txt)
                break
            s_idx = trans_idx[-1] + 1 
        except:
            s_idx = 0
        try:
            assert trans_idx[-1]
            print(len(trans_idx), len(trans_txt), len(error_idx), trans_idx[-1], end='\n\n')
        except:
            print('번역된 데이터 없음 !')

if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    
    cli_parser.add_argument("--task", type=str, default='translate')
    cli_parser.add_argument("--config_path", type=str, default='config')
    cli_parser.add_argument("--config_file", type=str, default='translate_config.json')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)