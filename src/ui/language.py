import os

#多语言标签内容
g_language_data = {}

def load_language(dirname):
    path = os.path.join(os.path.abspath("."), dirname)
    # {model_name, [chsname, chtname, enuname]}
    global g_language_data

    for file in os.listdir(path):
        model_name = file[12:-4]
        data = None
        with open(os.path.join(path, file), "r", encoding="utf-8") as f:
            data = f.read().split('\n')
        g_language_data[model_name] = []
        for line in data:
            line = line.split(",\"")
            line = [d.replace("\"", "") for d in line]
            g_language_data[model_name].append(line)

class Language(object):
    '''Every model has one langeage'''
    def __init__(self, model_name, lg = 'CHS'):
        self.language_data = g_language_data[model_name]

        self.language_index = self._get_index(lg)

    def _get_index(self, lg):
        #id,chsname,chtname,enuname
        index = 1
        if lg == 'CHT':
            index = 2
        elif lg == 'ENU':
            index = 3
        return index

    def set_language(self, lg):
        self.language_index = self._get_index(lg)

    def get_text(self, id):
        return self.language_data[id][self.language_index]


