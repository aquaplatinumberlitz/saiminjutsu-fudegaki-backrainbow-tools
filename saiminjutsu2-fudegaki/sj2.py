from blackrb_spt import ScriptSpt, wrap

sj2_names = {
    '村越\u3000進太': 'Shinta Murakoshi',
    '桜井\u3000進': 'Susumu Sakurai', '桜井\u3000佐和': 'Sawa Sakurai',
    '高瀬\u3000志乃': 'Shino Takase', '高瀬\u3000則子': 'Noriko Takase', '高瀬\u3000良行': 'Yoshiyuki Takase',
    '笠谷\u3000理枝': 'Rie Kasatani', '笠谷\u3000葉子': 'Youko Kasatani',
    '館山\u3000ゆうき': 'Yuuki Tateyama', '館山\u3000和子': 'Aiko Tateyama',
     'サトウ': 'Satou', 'スドウ': 'Sudou', 'サトウ＆スドウ': 'Satou & Sudou',
    '保坂\u3000ゆきこ': 'Yukiko Hosaka', '鴻池\u3000弓子': 'Yumiko Kounoike', '香野\u3000タカコ': 'Takako Kono',
    '弓子＆ゆきこ': 'Yumiko & Yukiko', '遠峰\u3000誠': 'Makoto Toumine', '遠峰\u3000葉子': 'Youko Toumine',
    '霧島\u3000さゆり': 'Sayuri Kirishima', '霧島\u3000まなみ': 'Manami Kirishima', '霧島\u3000せつこ': 'Setsuko Kirishima',

    'ゆうきの父親': "Yuuki's Father", '村越\u3000神父': 'Father Murakoshi',
    '神父': 'Father', 'ＯＬたち': 'Office Ladies', '英語教師': 'English Teacher',

    # '門倉\u3000真理子': 30, '里見\u3000亜矢子': 39, '森本\u3000知香': 35, '杉田＆保坂': 1, '杉田\u3000加世': 16,
    # '長谷川＆鴻池': 1,  '長谷川\u3000祥子': 18, '辻内＆田村': 1, '田村\u3000ゆま': 23, '辻内\u3000まき': 15,
    # '赤ちゃん': 3,  '四ノ宮\u3000マリ': 19,

    '男子生徒Ａ': 'Schoolboy A', '男子生徒Ｂ': 'Schoolboy B',  '男子生徒Ｃ': 'Schoolboy C', '生徒たち': 'Students',
    '女子生徒Ａ': 'Schoolgirl A', '女子生徒Ｂ': 'Schoolgirl B', '女子生徒': 'Schoolgirl',
    '男子学生Ａ': 'Male Student A', '男子学生Ｂ': 'Male Student B', '男子学生Ｃ': 'Male Student C',
    '女子学生Ａ': 'Female Student A', '女子学生Ｂ': 'Female Student B',
    '参列者Ａ': 'Attendee A', '参列者Ｂ': 'Attendee B', '参列者Ｃ': 'Attendee C', '参列者Ｄ': 'Attendee D', '参列者たち': 'Attendees',
    '女性社員Ａ': 'Female Employee A', '女性社員Ｂ': 'Female Employee B',
    '男性社員Ａ': 'Male Employee A', '男性社員Ｂ': 'Male Employee B',

    '司会者': 'Chairman',
}

sj2_choices = {
    '志乃さんの胸は…': "Aunt's boobs...", '母さんの眼鏡は…': "Mom's glasses...",
    '特に髪の毛が': 'Specially her long hair', '特にその胸が': 'Specially her boobs',
    '５００円のでいいや': '500 yen is fine', '１０００円のにしよう': 'Settle on 1000 yen',
}

sj2_t2_dic = {
    'プロローグ': 'Prologue', '諦観の日々': 'Days of resignation', 'お隣さん': 'Neighbors', 'サトウとスドウ': 'Satou Sudou',
    '安らぎの場所': 'Place of peace', 'ゆうき': 'Yuuki', 'ＥＸＴＲＡ': 'Extra',
    '朝の自己嫌悪': 'Morning self-loathing', '引っ越してきた人': 'Moved in guy', '難しい問題': 'Difficult problem',
    '臆病と優しさ': 'Timid or kind', 'ゆうきの情報': 'Yuuki\'s information', '消し飛んだ気持ち': 'Gone feeling',
    'お金の管理': 'Money management', 'ささやかな幸せ': 'Meager happiness', '本屋にて': 'At bookstore',
    '則子ちゃんに出会う': 'Meating Noriko', '酷い悪夢': 'Terrible nightmare', '救世主': 'Messiah', '村越さんの提案': 'Proposal',
    '朝食': 'Breakfast', '母さんへの布石': 'Mom\'s groundwork', '高瀬家へ': 'To Takase\'s', '『口実』': 'Pretext',
    '志乃さんへのお願い': 'Request from Shino', '『約束』': 'Promise',
    'いつもの朝': 'Usual morning', 'いつもと違う日': 'Unusual day', 'へつらう二人': 'Boot lickers', '学校を早退': 'Leaving early',
    '高瀬志乃': 'Shino Takase', '～催眠導入': 'Hypnosis induction', '『約束』の変更': 'Modified promise',
}


class Saimin2(ScriptSpt):
    def __init__(self, bf, tr_path):
        ScriptSpt.__init__(self, bf, sj2_names, sj2_choices, tr_path)

    def t1_tr(self, t):
        if t == '－－－－－':
            return t
        elif t.endswith('曜日'):
            month = 'Oct' if t.startswith('１０月') else 'Nov'
            week = {
                '日曜日': 'Sunday', '月曜日': 'Monday', '火曜日': 'Tuesday', '水曜日': 'Wednesday',
                '木曜日': 'Thursday', '金曜日': 'Friday', '土曜日': 'Saturday'
            }[t[-3:]]
            day = t.find('日')
            day = t[3:day]
            return '%s %s, %s' % (month, int(day), week)

        print('Title 1: %s' % t)
        return t

    def t2_tr(self, t):
        tr = t.split('\\n')
        for i in range(len(tr)):
            try:
                x = sj2_t2_dic[tr[i]]
                if len(x) > 22:
                    print('too long: %s' % x)
                    x = x[:22]
                tr[i] = x
            except KeyError:
                print('Title 2: %s' % tr[i])
        return '\\n'.join(tr)

    def process_message(self, msg):
        tr = self.translation[self.counter]
        self.counter += 1
        if tr.startswith('[N]'):
            return tr[3:]
        jap, quoted, quoted2 = msg, False, False
        if jap.startswith('「') and jap.endswith('」'):
            quoted = True
        elif jap.startswith('『') and jap.endswith('』'):
            quoted2 = True
        else:
            if jap.find('\r\n\u3000') != -1:
                print('++++++++++++++ %s' % msg.msg)
        if quoted:
            test = '"%s"' % tr
        elif quoted2:
            test = "'%s'" % tr
        else:
            test = None

        if test:
            wr = wrap(test)
            if len(wr) > 2:
                wr = wrap(tr)
        else:
            wr = wrap(tr)

        if len(wr) == 1:
            tr = wr[0]
        else:
            if len(wr) > 2:
                print('too long: %s' % tr)
                wr = wr[:2]
            tr = '\r\n'.join(wr)
        return tr


class UraSaimin(Saimin2):
    def __init__(self, bf, tr_path):
        ScriptSpt.__init__(self, bf, sj2_names, {}, tr_path)

    titles_dic = {
        '葉子の生活': 'Youko\'s life', '婚約者！？': 'Fiance!?',
        '村越先生の催眠学院': 'Murakushi\'s academy',
        '相談役': 'Advisor', '選ばれた相談役': 'Chosen advisor', 'スキンシップを': 'Skinship',
    }

    def t1_tr(self, t):
        try:
            x = self.titles_dic[t]
            if len(x) > 22:
                print('too long: %s' % x)
                x = x[:22]
            return x
        except KeyError:
            print('Title: %s' % t)
        return t

    def t2_tr(self, t):
        return self.t1_tr(t)
