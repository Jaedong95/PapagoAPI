import urllib.request
import json
import os 
import pickle
import argparse 
from src import Papago
from attrdict import AttrDict

class PapagoLD(Papago):
    def __init__(self, args):
        super().__init__(args)
    
    def language_detect(self, cli, text):
        '''
        지정한 Cli를 이용하여 text (1 sentence)에 대해 언어 감지 진행
        '''
        encQuery = urllib.parse.quote(text)
        url = "https://openapi.naver.com/v1/papago/detectLangs"
        data = "query=" + encQuery
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", cli[0])
        request.add_header("X-Naver-Client-Secret", cli[1])
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        
        return res['langCode']
    
    def client_ld(self, s_idx, cli, papago_df):
        self.lang_idx = []
        self.nlang_idx = []
        self.error_idx = []
        self.s_idx = 0 
                
        for idx in range(s_idx, len(papago_df)):
            try:
                language = self.language_detect(cli, papago_df[self.args.col][idx])
                if language == self.args.lang:
                    self.lang_idx.append(idx) 
                elif language != self.args.lang:
                    self.nlang_idx.append(idx) 
            except Exception as e:
                print(f'오류 발생 ! {idx}: {papago_df[self.args.col][idx]}')
                if e.code == 429:
                    print('오류 내용: 일일 언어 감지 한도 초과', end='\n\n')
                    self.s_idx = idx
                    break
                
                if e.code == 500:
                    print('오류 내용: HTTP 통신 오류', end='\n\n')
                    self.error_idx.append(idx)
                    continue 
            
        print(f'언어 감지 종료 !')
    
    def load_log(self):
        print(f'이전 작업 기록들을 로드합니다.')
        with open(os.path.join(self.args.log_path, self.args.task, 'lang_idx.pickle'), 'rb') as f:
            lang_idx = pickle.load(f)

        with open(os.path.join(self.args.log_path, self.args.task, 'nlang_idx.pickle'), 'rb') as f:
            nlang_idx = pickle.load(f)
            
        with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'rb') as f:
            error_idx = pickle.load(f)
            
        with open(os.path.join(self.args.log_path, self.args.task, 's_idx.pickle'), 'rb') as f:
            s_idx = pickle.load(f)
            
        return lang_idx, nlang_idx, error_idx, s_idx

    def save_log(self, lang_idx, nlang_idx, error_idx, e_idx):
        try: 
            with open(os.path.join(self.args.log_path, self.args.task, 'lang_idx.pickle'), 'rb') as f:
                prev_lang_idx = pickle.load(f)
            prev_lang_idx.extend(lang_idx)
            with open(os.path.join(self.args.log_path, self.args.task, 'lang_idx.pickle'), 'wb') as f:
                pickle.dump(prev_lang_idx, f, pickle.HIGHEST_PROTOCOL)         
        except:
            with open(os.path.join(self.args.log_path, self.args.task, 'lang_idx.pickle'), 'wb') as f:
                pickle.dump(lang_idx, f, pickle.HIGHEST_PROTOCOL)
        
        try: 
            with open(os.path.join(self.args.log_path, self.args.task, 'nlang_idx.pickle'), 'rb') as f:
                prev_nlang_idx = pickle.load(f)
            prev_nlang_idx.extend(nlang_idx)
            with open(os.path.join(self.args.log_path, self.args.task, 'nlang_idx.pickle'), 'wb') as f:
                pickle.dump(prev_nlang_idx, f, pickle.HIGHEST_PROTOCOL)         
        except:
            with open(os.path.join(self.args.log_path, self.args.task, 'nlang_idx.pickle'), 'wb') as f:
                pickle.dump(nlang_idx, f, pickle.HIGHEST_PROTOCOL)
        
        try:
            with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'rb') as f:
                prev_error_idx = pickle.load(f)
            prev_error_idx.extend(error_idx)
            with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'wb') as f:
                pickle.dump(prev_error_idx, f, pickle.HIGHEST_PROTOCOL)         
        except:
            with open(os.path.join(self.args.log_path, self.args.task, 'error_idx.pickle'), 'wb') as f:
                pickle.dump(error_idx, f, pickle.HIGHEST_PROTOCOL)

        with open(os.path.join(self.args.log_path, self.args.task, 's_idx.pickle'), 'wb') as f:
            pickle.dump(e_idx, f, pickle.HIGHEST_PROTOCOL)


def main(cli_argse):
    print(cli_argse)
    with open(os.path.join(cli_argse.config_path, cli_argse.task, cli_argse.config_file)) as f:
        args = AttrDict(json.load(f))

    # args.flag = 0   # 해당 파일을 처음 작업하는 경우: 0, 이어서 작업하는 경우: 1 
    papago = PapagoLD(args)
    papago.set_client()
    papago.load_data()
    client = papago.client
    data = papago.data

    s_idx = 0
    if args.flag == 1:
        lang_idx, nlang_idx, error_idx, s_idx = papago.load_log()
        print(f'언어 감지 시작 지점: {s_idx}')

    print(f'언어 감지 작업 준비 완료')
    
    for cls in client:
        print(f'{cls} 언어 감지 작업중 ..')
        papago.client_ld(s_idx, client[cls], data)
        lang_idx = papago.lang_idx   
        nlang_idx = papago.nlang_idx
        error_idx = papago.error_idx
        e_idx = papago.s_idx
        papago.save_log(lang_idx, nlang_idx, error_idx, e_idx)
        lang_idx, nlang_idx, error_idx, s_idx = papago.load_log()        
        if s_idx == 0:
            print(f'{args.file_name} 파일에 대한 언어 감지 작업이 모두 종료되었습니다.')
            papago.save_data(args.save_file, nlang_name=args.save_file2, lang_idx=lang_idx, nlang_idx=nlang_idx)
            break
        print(len(lang_idx), len(nlang_idx), len(error_idx), s_idx, end='\n\n')


if __name__ == '__main__':
    cli_parser = argparse.ArgumentParser()
    
    cli_parser.add_argument("--task", type=str, default='LD')
    cli_parser.add_argument("--config_path", type=str, default='config')
    cli_parser.add_argument("--config_file", type=str, default='LD_config.json')
    
    cli_argse = cli_parser.parse_args()
    main(cli_argse)