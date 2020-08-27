#!/usr/bin/env python3

import sys
from itertools import permutations
import re
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os.path

if len(sys.argv) < 4:
  print("Usage: \nwords.py yandex|google|filename|none alphabet mask\n")
  sys.exit()

search  = sys.argv[1]
alphabet = sys.argv[2]
pattern = sys.argv[3]

yandex = 'https://yandex.ru/search/?noreask=1&text='
google = 'https://www.google.ru/search?ie=UTF-8&hl=ru&spell=0&nfpr=1&q='

ua = UserAgent()
myheaders = {'User-Agent': str(ua.random), 'referer': 'https://www.google.ru'}

# все варианты перестановок
allwords = permutations(alphabet, len(pattern))

# выкидываем дубликаты
words = list(set(allwords))

# склеиваем 2-мерный список в одномерный
words2 = []
for word in words:
  str = ''.join(word)
  words2.append(str)

# проходим регекспом
obj = re.compile(pattern)
words = list(filter(lambda str: obj.search(str), words2))

print('Всего вариантов %d' % len(words))

output = []
wordlist = []

if os.path.exists(search):
  f = open(search, 'r', encoding = 'utf-8')
  wordlist = [line.strip() for line in f]
  f.close()
  print('Размер словаря %d' % len(wordlist))

for word in words:
  if search == 'google':
    r = requests.get(google + word, headers=myheaders)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html5lib')
    stat = soup.find('div', id='resultStats')
    if stat is not None:
      qty = re.search('Результатов:\sпримерно\s(.*)\s\(\d+,\d+\sсек.\)', stat.text)
      x = qty.group(1)
      x = x.split()
      x = ''.join(x)
      output.append([word, int(x)])
      print("%s - %s" % (word, x))
    else:
      output.append([word, 0])

  elif search == 'yandex':
    r = requests.get(yandex + word, headers=myheaders)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html5lib')
    stat = soup.find('div', {'class': 'serp-adv__found'})
    if stat is not None:
      qty = re.search('Нашлось\s(.*)\sрезультатов', stat.text)
      x = qty.group(1)
      output.append([word, x])
      print("%s - %s" % (word, x))
    else:
      output.append([word, 0])
      
  elif os.path.exists(search):
    if word in wordlist:
      output.append([word, 0])
    
  else:
    output.append([word, 0])

print('Отфильтрованно с помощью %s' % search)

output.sort(key=lambda x: x[1], reverse=True)

for str in output:
  print(str[0])
