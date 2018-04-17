import os
import shutil
import jieba
import jieba.analyse
import jieba.posseg as pseg
import configparser
import requests
from bs4 import BeautifulSoup

global url
global prepath_no_segment
global prepath_has_segment
global prearticles_pos_tags
global prearticles_keywords


def ReadConfig():
    global url
    global prepath_no_segment
    global prepath_has_segment
    global prearticles_pos_tags
    global prearticles_keywords
    conf = configparser.ConfigParser()
    conf.read("config.ini")
    url = conf['SECTION']['url']
    prepath_no_segment = conf['SECTION']['prepath_no_segment']
    prepath_has_segment = conf['SECTION']['prepath_has_segment']
    prearticles_pos_tags = conf['SECTION']['prearticles_pos_tags']
    prearticles_keywords = conf['SECTION']['prearticles_keywords']

def Crawler():
    #声明全局变量
    global url
    global prepath_no_segment
    global prepath_has_segment
    global prearticles_pos_tags
    global prearticles_keywords

    #清空文件夹
    shutil.rmtree(prepath_no_segment)
    os.mkdir(prepath_no_segment)
    shutil.rmtree(prepath_has_segment)
    os.mkdir(prepath_has_segment)
    shutil.rmtree(prearticles_pos_tags)
    os.mkdir(prearticles_pos_tags)
    shutil.rmtree(prearticles_keywords)
    os.mkdir(prearticles_keywords)

    res = requests.get(url)
    # 使用gb18030编码
    res.encoding = 'gb18030'
    # 使用剖析器为html.parser
    soup = BeautifulSoup(res.text, 'lxml')
    #遍历每一个class=h2_tit的节点
    for h2 in soup.select('.h2_tit'):
        print(h2.a.text, h2.a['href'])
        article = requests.get(h2.a['href'])
        article.encoding = 'gb2312'
        eachsoup = BeautifulSoup(article.text,'lxml')
        tex = eachsoup.select('.main')[0].p.text
        print(tex)#此处打印输出可以关闭

        path_no_segment   = prepath_no_segment + h2.a.text + '.txt'
        path_has_segment  = prepath_has_segment + h2.a.text + '.txt'
        articles_pos_tags = prearticles_pos_tags + h2.a.text + '.txt'
        articles_keywords = prearticles_keywords + h2.a.text + '.txt'


        file_no_segment  = open(path_no_segment, 'w+', encoding='utf-8')
        file_has_segment = open(path_has_segment, 'w+', encoding='utf-8')
        file_pos_tags    = open(articles_pos_tags, 'w+', encoding='utf-8')
        file_keywords    = open(articles_keywords, 'w+', encoding='utf-8')

        #原始文章
        file_no_segment.write(tex)

        #中文分词
        seg_list = jieba.cut(tex, cut_all=False)
        file_has_segment.write("/ ".join(seg_list))

        #词性标注
        words = pseg.cut(tex)
        for w in words:
            file_pos_tags.write(w.word + "/" + w.flag + " ")

        #关键词抽取
        # 基于TF-IDF算法的关键词抽取
        tags = jieba.analyse.extract_tags(tex, topK=10, withWeight=True, allowPOS=())

        # 基于TextRank算法的关
        #tags = jieba.analyse.textrank(tex, topK=10, withWeight=True)

        for t in tags:
            file_keywords.write(t[0] + " ")
            file_keywords.write(str(t[1]) + '\n')

        file_no_segment.close()
        file_has_segment.close()
        file_pos_tags.close()
        file_keywords.close()

if __name__ == "__main__":
    ReadConfig()
    Crawler()
