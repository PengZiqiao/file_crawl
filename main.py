from argparse import ArgumentParser

import requests
from lxml import etree
from tqdm import tqdm


def build_parser():
    parser = ArgumentParser(description='----一个简单爬虫，用于下载页面上的指定格式文件----')
    parser.add_argument('--url', type=str, required=True,
                        help='需要下载的页面地址')
    parser.add_argument('--file_type', type=str, default='zip',
                        help='需要下载的文件类型')
    parser.add_argument('--save', type=str, default='.',
                        help='需要保存的路径')
    return parser

class Crawl:
    def __init__(self, url, save):
        self.url = url
        self.save = save
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }

    def get_html(self):
        # 
        response = requests.get(self.url, headers=self.headers)
        return response.text

    def get_file_url(self, html):
        tree = etree.HTML(html)
        file_url = tree.xpath('//*[contains(lower-case(@href), "zip")]/@href')
        return file_url
        
    def run(self):
        html = self.get_html()
        file_url = self.get_file_url(html)
        for url in file_url:
           self.download(url, self.save)

    def download(self, url, save):

        # 拼接网址，根据网址中../出现次数，确定base_url所在层级
        cnt = url.count('../')
        base_url = '/'.join(self.url.split('/')[:-cnt])
        url = f'{base_url}/{url.replace("../", "")}'

        save = f'{self.save}/{url.split("/")[-1]}'

        response = requests.get(url, headers=self.headers, stream=True)
        total=int(response.headers['Content-Length'])

        with open(save, 'wb') as f, tqdm(desc=save, total = total) as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))
                

if __name__ == '__main__':
    args = build_parser()
    crawl = Crawl(args.url, args.save)
    crawl.run()
