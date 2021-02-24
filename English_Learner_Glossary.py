# -*- coding: utf-8 -*-
"""
@author: Nowak and Wantuch
"""
#DEPENDENCIES
import eng_to_ipa as ipa #to get IPA conversion
import requests #to request info from SketchEngine and Oxford Dictionary
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

#GET TEXT FROM USER
def get_text(filename):
    file = open(filename, 'r', encoding ='utf8')
    text = file.read()
    file.close()
    return text

#CLEAN TEXT IF NEEDED
def clean(text):
    breaks = "\t\n'ˌ.ˈ,‘’*"
    cleaned_text = ''
    for character in text:
        if character in breaks:
            cleaned_text += ''
        else :
            cleaned_text += character
    return cleaned_text

#GIVE SENTENCES THEIR IPA TRANSCRIPTION
def present_sentences(sentences):
    presented_sentences = []
    for sentence in sentences:
        presented_sentences.append(sentence)
        presented_sentences.append(ipa.convert(sentence))
    return presented_sentences

#GET ALL CONTENT WORDS WITH FREQUENCY FROM ENTENTEN15
def frequency_dic(words):
    stops = set(stopwords.words('english'))
    USERNAME = ''
    API_KEY = 'd8c67247df3543a6802960b483b0e12c'
    base_url = 'https://api.sketchengine.eu/bonito/run.cgi'
    freq_dic = {}
    for word in words:
        if word.isalpha() and word.lower() not in stops:
            d = requests.get(base_url + '/wsketch', auth=(USERNAME, API_KEY), params={
            'lemma': word,
            'corpname': 'preloaded/ententen15_tt31',
            'format': 'json',
            }).json()
            freq = d['freq']
            freq_dic[word] = freq
    return freq_dic

#GET OXFORD DICTIONARY DEFINITION FOR CHOSEN WORD
def get_definition(word):
    app_id = 'b412c50a'
    app_key = '8904dd20fe1c25de363df4fdf592fb35'
    language = 'en-us'
    fields = 'definitions'
    strictMatch = 'false'
    if word.isalpha():
        word_id = word
        url = 'https://od-api.oxforddictionaries.com/api/v2/entries/'  + language + '/'  + word_id.lower() + '?fields=' + fields + '&strictMatch=' + strictMatch;
        r = requests.get(url, headers = {'app_id' : app_id, 'app_key' : app_key})
        y = json.loads(r.text)
        y = y["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"]
    return y

#READABILITY SCORE Flesch-Kincaid
def readability_score(word_count, sentences_count, syllable_count):
    read_score = 206.835 - 1.015 * (word_count/sentences_count) - 84.6 * (syllable_count/word_count)
    if read_score >= 90:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Very easy to read. Easily understood by an average 11-year-old student. (5th GRADE)')
    elif read_score >= 80: 
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Easy to read. Conversational English for consumers. (6th GRADE)')
    elif read_score >= 70:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Fairly easy to read. (7th GRADE)')
    elif read_score >= 60:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Plain English. Easily understood by 13- to 15-year-old students. (8th & 9th GRADE)')
    elif read_score >= 50:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Fairly difficult to read. (10th to 12th GRADE)')
    elif read_score >= 30:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Difficult to read. (College)')   
    elif read_score >= 10:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Very difficult to read. Best understood by university graduates. (College graduate)')
    else:
        return ('Read score: ', round(read_score,2),'Your text is: ' ,'Extremely difficult to read. Best understood by university graduates. (Professional)')

#CHECK PHONETIC DIFFICULTY - COMPONENTS
def check_clusters(word):
    word = ipa.convert(word)
    pattern = '[^iɪeɛæɑouʊʌə\d\W]{2,}'
    match = re.search(pattern,word)
    if match:
        is_there_cluster = True
    else:
        is_there_cluster = False
    return is_there_cluster

def homorganic(word):
    dorsals = 'kŋgxw'
    word = ipa.convert(word)
    print(word)
    i = 0
    for i in range(len(word)-1):
        if word[i] in dorsals and word[i+1] in dorsals:
            homorganic = True
            break
        else:
            homorganic = False
    return homorganic

#CHECK PHONETIC DIFFICULTY - MAIN FUNCTION
def phonetic_difficulty(word):
    word = clean(word)
    word_ipa = ipa.convert(word)
    word_ipa = clean(word_ipa)
    
    vowels = 'iɪeɛæɑouʊʌə'
    dorsals = 'kŋgxw'
    fri_aff_liq = 'rfvszxhθðʃʒlʧʤ'
    rhotic = 'r'

    phon = 0
    i=0
    for i in range(len(word_ipa)):
        if word_ipa[i] in dorsals:
            phon += 1
        if word_ipa[i] in fri_aff_liq:
            phon += 1
        if word_ipa[i] in rhotic:
            phon += 1
    if word_ipa[len(word_ipa)-1] not in vowels:
        phon += 1
    if ipa.syllable_count(word) >= 3:
        phon += 1
    if check_clusters(word_ipa) == True:
        phon += 1
    if homorganic(word_ipa) == True:
        phon += 1
    return phon

#INFORM ABOUT REGRESSIVE VOICING
def regressive(word):
    word = ipa.convert(word)
    word = clean(word)
    
    reg_pre = 'sθptk'
    reg_fol = 'zðbdg'
    i = 0
    while i < (len(word)-1):
        if word[i] in reg_pre and word[i+1] in reg_fol or word[i] in reg_fol and word[i+1] in reg_pre: 
            voicing = True
            trouble = word[i] + ' and ' + word[i+1]
            break
        else:
            voicing = False
            trouble = ''
        i += 1
    return voicing, trouble

title = "🅴🅽🅶🅻🅸🆂🅷 🅻🅴🅰🆁🅽🅴🆁❜🆂 🅶🅻🅾🆂🆂🅰🆁🆈"
print("Hello there, English Learner. This is", title)
x = input("First, what is the name of your file? Write it like this: [name].txt \n")
dirty_text = get_text(x)
words_high = word_tokenize(dirty_text)
words = []
for word in words_high:
    words.append(word.lower())
sentences = sent_tokenize(dirty_text)
print('-----------------------------------------------------------')
print('Thank you, all loaded and ready!\n')
print('-----------------------------------------------------------')
x = input('Now, what do you want to do with it? \n1. Show me IPA transcription.\n2. Show me frequency list.\n3. Show me definition of a word.\n4. Show me how difficult it is to read.\n5. Show me phonetic difficulty.\n6. Quit\n')
while x != '6':
    if x=='1':
        print('-----------------------------------------------------------')
        sentences_ipa = present_sentences(sentences)
        i = 0
        for sentence in sentences_ipa:
            if i % 2 == 0:
                print(sentence)  
            else:
                print(sentence)
                print('\t')
            i += 1
    if x=='2':
        print('-----------------------------------------------------------')
        print('Loading...')
        freq_dic = (frequency_dic(words))
        y = input('How do you want it displayed?\na. A-Z\nb. Z-A\nc. Highest to lowest frequency\nd. Lowest to highest frequency\n')
        if y=='a':
            for x in sorted(freq_dic, key=lambda x: x, reverse=False):
                print('{0:<30}{1:<30}'.format(x, freq_dic[x]))
        if y=='b':
            for x in sorted(freq_dic, key=lambda x: x, reverse=True):
                print('{0:<30}{1:<30}'.format(x, freq_dic[x]))
        if y=='c':
            for x in sorted(freq_dic, key=lambda x: freq_dic[x], reverse=True):
                print('{0:<30}{1:<30}'.format(x, freq_dic[x]))
        if y=='d':
            for x in sorted(freq_dic, key=lambda x: freq_dic[x], reverse=False):
                print('{0:<30}{1:<30}'.format(x, freq_dic[x]))
    if x=='3':
        print('-----------------------------------------------------------')
        y = input('Check definition for word: ')
        definitions = get_definition(y)
        for definition in definitions:
            print(definition)
    if x=='4':
        print('-----------------------------------------------------------')
        syllable_count = 0
        word_count = 0 #nie uzywamy len(words) bo nie chcemy liczyć kropek
        for word in words:
            if word.isalpha():
                word_count += 1
                syllable = ipa.syllable_count(word)
                syllable_count = syllable_count + syllable
        sentences_count = len(sentences)
        scores = readability_score(word_count, sentences_count, syllable_count)
        for score in scores:
            print(score)
    if x=='5':
        print('-----------------------------------------------------------')
        y = input('Check phonetic difficulty for word: ')
        difficulty = phonetic_difficulty(y)
        voicing = regressive(y)
        print('Your word difficulty: ',difficulty)
        if difficulty >= 8:
            print('This word is difficult to pronunce.')
        elif difficulty >= 4:
            print('This word is of average difficulty to pronunce.')
        else:
            print('This word is easy to pronunce')
        if voicing[0] == True:
            print('Be cautious!', voicing[1], 'beside each other can be tricky! \nDo not use regressive voicing assimilation!')
    print('-----------------------------------------------------------')
    x = input('Now what? \n1. Show me IPA transcription.\n2. Show me frequency list.\n3. Show me definition of a word.\n4. Show me how difficult it is to read.\n5. Show me phonetic difficulty.\n6. Quit\n')
    print('-----------------------------------------------------------')
print('Thank you for using our 🅴🅽🅶🅻🅸🆂🅷 🅻🅴🅰🆁🅽🅴🆁❜🆂 🅶🅻🅾🆂🆂🅰🆁🆈. Hope it helped!')
