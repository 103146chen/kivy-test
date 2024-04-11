import pandas
from 聲母變化 import *
import json
import re
from pathlib import Path

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage

# 設定引用資料
_keys = [['字母', '清濁', '聲母'],['攝', '韻目', '開合等第', '聲調','韻母']]
_exl = pandas.read_excel('廣韻.xlsx')

# 設定聲母與韻母資料
_initial, _vowels = _exl[['字', '字母', '清濁', '聲母']], _exl[['字','攝','韻目','開合等第','聲調','韻母']]
_initial.set_index('字', inplace=True)
_vowels.set_index('字', inplace=True)

def phonology_main(msg):
    
    
    def main_process(msg):
        # 用戶輸入反切，_target[0]為上字、_target[1]為下字
        _target = [char for char in msg]
    
        # 找出上字的類別、轉為list形式，並將其字母、清濁、聲母轉換為字典，方便後續取用
        # 找出下字的類別、轉為list形式，並將其攝、聲調、開合等第、韻母、韻目轉換為字典，方便後續取用
        ini, vow = _initial.loc[_target[0]].values.tolist(), _vowels.loc[_target[1]].values.tolist()
        ini = {key: [lst[i] for lst in ini] for i, key in enumerate(_keys[0])} if type(ini[0])==list else {'字母':[ini[0]],'聲母':[ini[1]],'清濁':[ini[2]]}
        vow = {key: [lst[i] for lst in vow] for i, key in enumerate(_keys[1])} if type(vow[0])==list else {'攝':[vow[0]],'韻目':[vow[1]],'開合等第':[vow[2]],'聲調':[vow[3]],'韻母':[vow[4]]}
        
        # 策略:單獨列舉每個上字搭配不同下字的變化
        
        def initial_process():
            initial_result = []
            all_flags = []
            ini_flags = []
            tmp_initial_result = []
            
            tmp_initial_count = -1
            for tmp_initial in ini['字母']: # 單獨列舉每個字母
                # print(tmp_initial)
                tmp_initial_count += 1 # 計算字母位置
                
                tmp_vowel_count = -1
                for tmp_vowel in vow['韻目']: # 單獨列舉每個韻目(如:東韻)
                    tmp_vowel_count += 1
                    tmp_all_flags = []
                    # print(tmp_vowel)
                    
                    # ======================= 測試是否有語音變化 =======================
                    # 【 測試順序 : 類隔、濁音清化、顎化、零聲母化、捲舌音化、輕脣音化、直接演變 】
                    
                    # _________________________ 演變條例:類隔 _________________________
                    if tmp_initial in ['端','透','定','泥'] and vow['開合等第'][tmp_vowel_count] in ['開2','開3','合2','合3']:
                        tmp_result = ['知','徹','澄','娘'][['端','透','定','泥'].index(tmp_initial)]
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial}聲母只搭配 1、4等韻，此處為文獻資料未能反映及時演變之「類隔」，原應為中古 {tmp_result}聲母')
                        tmp_all_flags.append('類隔')
                        tmp_initial_result = tmp_result
                        #print(tmp_initial_result)
                        # tmp_initial_result.append(['知','徹','澄','娘'][['端','透','定','泥'].index(tmp_initial)])
                        
                    elif tmp_initial in ['知','徹','澄','娘'] and vow['開合等第'][tmp_vowel_count] in ['開1','開4','合1','合4']:
                        tmp_result = ['端','透','定','泥'][['知','徹','澄','娘'].index(tmp_initial)]
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial}聲母只搭配 2、3等韻，此處為文獻資料未能反映及時演變之「類隔」，原應為中古 {tmp_result}聲母')
                        tmp_all_flags.append('類隔')
                        tmp_initial_result = tmp_result
                        # tmp_initial_result.append(['端','透','定','泥'][['知','徹','澄','娘'].index(tmp_initial)])
                    else:
                        tmp_result = tmp_initial # 沒有發生類隔
                        tmp_initial_result = tmp_result
                    
                    # _________________________ 演變條例:清化 _________________________
                    # 說明︰判斷聲母是否存在於五大音變表之濁音清化條目
                    if tmp_result in initial_change_types['濁音清化']:
                        tmp_tone_clue = vow['聲調'][tmp_vowel_count]
                        if tmp_tone_clue != '平':
                            tmp_tone_clue = '仄'
                        tmp_result = initial_changes[tmp_result][tmp_tone_clue]
                        tmp_all_flags.append('濁音清化')
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial_result}聲母發生濁音清化，依據其搭配之 {tmp_tone_clue}聲調，判斷歸入中古 {tmp_result}聲母')
                        tmp_initial_result = tmp_initial
                    tmp_initial_clue = tmp_result # 取得中古字母
                    
                    # _________________________ 演變條例:顎化 _________________________
                    # 說明︰有﹙狀況一﹚見組字搭配細音韻母、﹙狀況二﹚見組字搭配開口二等
                    if tmp_result in initial_change_types['顎化'] and vow['開合等第'][tmp_vowel_count] in ['開2','開3','開4','合3','合4']:
                        tmp_result = initial_changes[tmp_result]['顎化']
                        tmp_all_flags.append('顎化')
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial_result}聲母發生顎化，成為現代 {tmp_result}')
                        initial_result.append(tmp_result)
                    
                    # _______________________ 演變條例:零聲母化 _______________________
                    # 說明︰判斷聲母是否存在於五大音變條例的零聲母化欄位
                    if tmp_result in initial_change_types['零聲母化']:
                        tmp_result = initial_changes[tmp_result]['零聲母化']
                        tmp_all_flags.append('零聲母化')
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial_result}聲母發生零聲母化，成為現代 零聲母')
                        initial_result.append(tmp_result)
                    
                    # _______________________ 演變條例:捲舌音化 _______________________
                    # 說明︰判斷聲母是否存在於五大音變條例的捲舌音化欄位
                    if tmp_result in initial_change_types['捲舌音化']:
                        tmp_result = initial_changes[tmp_result]['捲舌音化']
                        tmp_all_flags.append('捲舌音化')
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial_result}聲母發生捲舌音化，成為現代 {tmp_result}')
                        initial_result.append(tmp_result)
                    
                    # _______________________ 演變條例:輕脣音化 _______________________
                    # 說明︰判斷聲母是否存在於五大音變條例的輕脣音化欄位
                    if tmp_result in initial_change_types['輕脣音化']:
                        tmp_result = initial_changes[tmp_result]['輕脣音化']
                        tmp_all_flags.append('輕脣音化')
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial_result}聲母發生輕脣音化，成為現代 {tmp_result}')
                        initial_result.append(tmp_result)
                    
                    # _______________________ 演變條例:直接變化 _______________________
                    # 說明︰判斷聲母是否存在於五大音變條例的輕脣音化欄位
                    if '直接變化' in initial_changes[tmp_initial_clue].keys() and '顎化' not in tmp_all_flags:
                        tmp_initial_result = tmp_result
                        tmp_result = initial_changes[tmp_initial_clue]['直接變化']
                        tmp_all_flags.append('直接變化')
                        ini_flags.append(f'【{tmp_initial_count}】【{tmp_initial}】【{tmp_vowel}】 中古 {tmp_initial_result}聲母現代讀作 {tmp_result}')
                        initial_result.append(tmp_result)
                    
                    all_flags.append(tmp_all_flags.copy())
            
            tmp_initial_result = []
            for tmp in initial_result:
                if tmp not in tmp_initial_result:
                    tmp_initial_result.append(tmp)
            initial_result = tmp_initial_result.copy()
            
            
            return initial_result,ini_flags,all_flags
            
            #       現今讀音        演變過程   經過演變  現代讀音
            # 要求格式:
            # initial_result = ['ㄍ', 'ㄐ', 'ㄌ', 'Ø']
            # ini_flags      = ['【3】【定】中古...','【4】【幫】中古...'] (同ini_flags)
            # all_flags      = [['濁音清化','顎化'],['直接變化']] (同all_flags)
            # final_initial  = [['ㄍ', 'ㄐ', 'ㄌ', 'Ø']] # 沒用?
        
        initial_dict = {}
        judge = initial_process() # 現今讀音 詳細演變過程 經過演變
        all_flags = judge[2]
        for tmp in judge[1]:
            tmp_num = int(tmp[1])
            try:
                initial_dict[ini['字母'][tmp_num]] += tmp
            except:
                initial_dict[ini['字母'][tmp_num]] = tmp
        del tmp,tmp_num
        
        
        def vowel_process():
            final_vowel = []
            vowel_flags = []
            vow_dict = {}
            
            for tmp_ini in judge[0]:
            
                tmp_vow_count = 0
                for tmp_vow in vow['韻母']:
                    vowel_flags.clear()
                    # print(tmp_vow)
                    all_flags = judge[2]
                    # 策略:細音消失 -> 顎化 -> 由洪轉細 -> 三四等合流 -> 一二等合流
                    # ============================== 介音變化 ==============================
                    if tmp_ini in ['ㄈ','ㄓ','ㄔ','ㄕ'] and vow['開合等第'][tmp_vow_count] in ['開3','合3','開4','合4']:
                        try:
                            tmp_vow_result = tmp_vow.replace('i','',1)
                        except:
                            tmp_vow_result = tmp_vow.replace('j','',1)
                        vowel_flags.append(f'中古 {tmp_vow}韻 因搭配卷舌/輕脣聲母，細音消失為 {tmp_vow_result}韻')
                        # print('細音消失')
                        all_flags.append('細音消失')
                        tmp_vow = tmp_vow_result
                    
                    if tmp_ini in ['ㄅ','ㄆ','ㄇ','ㄈ'] and '合' in vow['開合等第'][tmp_vow_count]:
                        tmp_vow_result = tmp_vow.replace('u','',1)
                        vowel_flags.append(f'中古 {tmp_vow}韻 因搭配脣音聲母，異化為 {tmp_vow_result}韻')
                        tmp_vow = tmp_vow_result
                        # print('異化')
                        all_flags.append('異化')
                    
                    if tmp_ini in ['ㄐ','ㄑ','ㄒ'] and '開2' in vow['開合等第'][tmp_vow_count]:
                        if tmp_vow[0] != 'r':
                            tmp_vow = 'r'+tmp_vow
                        tmp_vow_result = tmp_vow.replace('r','i',1)
                        vowel_flags.append(f'中古 {tmp_vow}韻 因搭配見組字，由洪轉細為 {tmp_vow_result}')
                        # print('由洪轉細')
                        tmp_vow = tmp_vow_result
                        all_flags.append('由洪轉細')
                    
                    if '由洪轉細' not in all_flags and vow['開合等第'][tmp_vow_count] in ['開2','合2']:
                        tmp_vow_result = tmp_vow.replace('r','',1)
                        vowel_flags.append(f'中古 {tmp_vow}韻 經一二等合流，r介音消失為 {tmp_vow_result}韻')
                        # print('一二等合流')
                        tmp_vow = tmp_vow_result
                        all_flags.append('一二等合流')
                    
                    if '細音消失' not in all_flags:
                        if vow['開合等第'][tmp_vow_count] in ['開3','合3']:
                            tmp_vow_result = tmp_vow.replace('j','i',1)
                            vowel_flags.append(f'中古 {tmp_vow}韻 經三四等合流，j介音轉為 {tmp_vow_result}韻')
                            # print('三四等合流')
                            tmp_vow = tmp_vow_result
                            all_flags.append('三四等合流')
                    
                    # ============================== 韻尾變化 ==============================
                    if tmp_vow[-1] in ['p','t','k']:
                        # print('由促轉舒')
                        tmp_vow_result = tmp_vow[:-1]
                        vowel_flags.append(f'中古 {tmp_vow}韻 之入聲韻尾消失，成為 {tmp_vow_result}韻')
                        all_flags.append('由促轉舒')
                        tmp_vow = tmp_vow_result
                    elif tmp_vow[-1] == 'm':
                        # print('雙脣鼻尾轉為舌尖鼻尾')
                        tmp_vow_result = tmp_vow[:-1]+'n'
                        vowel_flags.append(f'中古 {tmp_vow}韻 之雙脣鼻尾轉為舌尖鼻尾，成為 {tmp_vow_result}韻')
                        all_flags.append('雙脣鼻尾轉為舌尖鼻尾')
                        tmp_vow = tmp_vow_result
                    
                    if 'iu' in tmp_vow:
                        # print('iu合併')
                        tmp_vow_result = tmp_vow.replace('iu','y',1)
                        vowel_flags.append(f'中古 {tmp_vow}韻 之iu合併，成為 {tmp_vow_result}韻')
                        all_flags.append('iu合併')
                        tmp_vow = tmp_vow_result
                        
                    if vowel_flags == []:
                        # print('未有變化')
                        all_flags.append('無變化')
                        vowel_flags.append(f'中古 {tmp_vow}韻 為今日之 {tmp_vow}韻')
                        #print('',end='')
                    vow_dict[str(tmp_vow_count)+tmp_ini+vow['韻目'][tmp_vow_count]] = vowel_flags.copy()
                    
                    tmp_vow_count += 1
                    final_vowel.append(tmp_vow)
            return vow_dict, final_vowel
        
        def tone_process():
            tone_changes = []
            final_tone = []
            tone_dict = {}
            tmp_count = 0
            #print(ini,vow)
            for tmp_ini_clue_count, ini_tone_clue in enumerate(ini['聲母']):
                #print(ini,ini['聲母'][0],ini['字母'][0],ini['清濁'][0],end='\n')
                if ini['聲母'][0] in ['全清','次清','全濁','次濁']:
                    #print('a')
                    ini_tone_clue = ini['聲母'][tmp_ini_clue_count]
                elif ini['字母'][0] in ['全清','次清','全濁','次濁']:
                    #print('b')
                    ini_tone_clue = ini['字母'][tmp_ini_clue_count]
                elif ini['清濁'][0] in ['全清','次清','全濁','次濁']:
                    #print('c')
                    ini_tone_clue = ini['清濁'][tmp_ini_clue_count]
                #print(ini_tone_clue)
                '''if ini_tone_clue not in ['平','上','去','入']:
                    ini_tone_clue = ini['清濁'][tmp_ini_clue_count]'''
                tmp_ini = ini['字母'][tmp_ini_clue_count]
                #print(ini_tone_clue)
                
                for tmp_vow_clue_count, vow_tone_clue in enumerate(vow['聲調']):
                    #print(vow,vow_tone_clue)
                    #print(vow_tone_clue)
                    #print(ini_tone_clue,vow_tone_clue)
                    if vow_tone_clue == '去':
                        tmp_tone = '51'
                    
                    elif vow_tone_clue == '上':
                        if ini_tone_clue == '全濁':
                            tmp_tone = '51'
                        else:
                            tmp_tone = '214'
                    
                    elif vow_tone_clue == '平':
                        if ini_tone_clue in ['全清','次清']:
                            tmp_tone = '55'
                        else:
                            tmp_tone = '35'
                    
                    elif vow_tone_clue == '入':
                        if ini_tone_clue == '全濁':
                            tmp_tone = '35 or 51'
                        elif ini_tone_clue == '次濁':
                            tmp_tone = '51'
                        elif ini_tone_clue in ['全清','次清']:
                            tmp_tone = '55 or 35 or 214 or 51'
                    # print(vow_tone_clue,ini_tone_clue)
                    # print(f'中古 {ini_tone_clue}聲母 搭配中古 {vow_tone_clue}聲調 = 現代 {tmp_tone}')
                    tone_changes.append(f'【{tmp_ini}】【{vow["韻目"][tmp_vow_clue_count]}】中古 {ini_tone_clue}聲母 搭配中古 {vow_tone_clue}聲調 = 現代 {tmp_tone}')
                    try:
                        tone_dict[ini['字母'][tmp_count]] += ' or '
                        tone_dict[ini['字母'][tmp_count]] += tmp_tone
                    except:
                        tone_dict[ini['字母'][tmp_count]] = tmp_tone
                    final_tone.append(tmp_tone)
                tmp_count += 1
                
            
            #print('\n\n\n\n')
            #print(tone_dict, final_tone, tone_changes)
            #print('\n\n\n\n')
                
            del tmp_tone, ini_tone_clue, vow_tone_clue, tmp_count
            return tone_dict,final_tone,tone_changes
        
        
        vow_dict = vowel_process()
        tone_dict = tone_process()
        
        return initial_dict, vow_dict, tone_dict
        
    final_tuple = main_process(msg)
    now_ini = final_tuple[0]
    now_vow = final_tuple[1][0]
    now_ton = final_tuple[2][0]
    now_ton_change = final_tuple[2][2]
    return now_ini,now_vow,now_ton,now_ton_change
    
import tkinter as tk
from tkinter import scrolledtext


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

# 加載Kivy檔案
Builder.load_string('''
<RootWidget>:
    orientation: 'vertical'
    canvas:
        Color:
            rgba: 0.86, 0.98, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    GridLayout:
        cols: 1
        Label:
            text: "歡迎使用聲韻學小幫手！"
            color: 0, 0, 0, 1  # 黑色文本
            halign: 'center'  # 水平居中对齐
            valign: 'top'  # 垂直居中对齐
            size_hint_y: None
            height: dp(48)
    
        TextInput:
            id: entry_1
            background_color: 1, 0.93, 0.89, 1
            foreground_color: 0, 0.03, 0.09, 1
            hint_text: '請輸入想搜尋的切語'
            multiline: False
            size_hint_y: None
            height: dp(48)
            halign: 'center'  # 水平居中对齐
            valign: 'top'  # 垂直居中对齐
            padding: dp(10), dp(10), dp(10), dp(10)

        Button:
            height: dp(30)
            size_hint_y: None
            halign: 'center'  # 水平居中对齐
            valign: 'top'  # 垂直居中对齐
            text: "查詢"
            on_release: root.execute()
        
        ScrollView:
            Label:
                id: entry_2
                text: "請輸入想查詢的切語，依次按下搜尋及顯示變化內容。"
                color: 0, 0, 0, 1  # 黑色文本
                halign: 'center'  # 水平居中对齐
                valign: 'middle'  # 垂直居中对齐
                size_hint_y: None
                height: max(self.texture_size[1], root.height)  # 根据内容高度自适应
                text_size: self.width, None  # 自动调整文本大小以适应宽度
    
    GridLayout:
        cols: 4
        size_hint: 1, None
        height: dp(75)
        width: dp(50)
        padding: dp(5), dp(5), dp(5), dp(5)
        spacing: dp(5)

        
        Button:
            text: '顯示所有結果'
            on_release: root.display_all_result()
        
        Button:
            text: '顯示聲調結果'
            on_release: root.display_ton_result()
        
        Button:
            text: '顯示韻母結果'
            on_release: root.display_vow_result()
        
        Button:
            text: '顯示聲母結果'
            on_release: root.display_ini_result()


''')

class RootWidget(BoxLayout):
    now_ini, now_vow, now_ton, now_ton_change = "", "", "", ""

    def execute(self):
        input_text = self.ids.entry_1.text
        result = phonology_main(input_text)
        self.now_ini = result[0]
        self.now_vow = result[1]
        self.now_ton = result[2]
        self.now_ton_change = result[3]
        print(result)

    def display_ini_result(self):
        self.ids.entry_2.text = "==========聲母變化==========\n\n"
        for i in self.now_ini.keys():
            tmp_change_index = self.now_ini[i].replace('【', '').replace('】', '')
            self.ids.entry_2.text += f"【聲母】\n{i}\n\n【變化】\n{tmp_change_index}\n\n"

    def display_vow_result(self):
        self.ids.entry_2.text = "==========韻母變化==========\n\n"
        for i in self.now_vow.keys():
            self.ids.entry_2.text += f"【韻母】\n{i}\n\n【變化】\n{', '.join(self.now_vow[i])}\n\n"

    def display_ton_result(self):
        self.ids.entry_2.text = "==========聲調變化==========\n\n"
        for i in self.now_ton.keys():
            self.ids.entry_2.text += f"【聲調】\n{self.now_ton[i]}\n\n【變化】\n{self.now_ton_change[0]}\n\n"

    def display_all_result(self):
        self.ids.entry_2.text = "==========聲母變化==========\n\n"
        for i in self.now_ini.keys():
            tmp_change_index = self.now_ini[i].replace('【', '').replace('】', '')
            self.ids.entry_2.text += f"【聲母】\n{i}\n\n【變化】\n{tmp_change_index}\n\n"

        self.ids.entry_2.text += "\n\n==========韻母變化==========\n\n"
        for i in self.now_vow.keys():
            self.ids.entry_2.text += f"【韻母】\n{i}\n\n【變化】\n{', '.join(self.now_vow[i])}\n\n"

        self.ids.entry_2.text += "\n\n==========聲調變化==========\n\n"
        for i in self.now_ton.keys():
            self.ids.entry_2.text += f"【聲調】\n{self.now_ton[i]}\n\n【變化】\n{self.now_ton_change[0]}\n\n"

class MyApp(App):
    def build(self):
        return RootWidget()

if __name__ == '__main__':
    MyApp().run()
