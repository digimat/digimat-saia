# -*- coding: utf-8 -*-


import re
import unicodedata


class Test(object):

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except:
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return str(text)

    def text_to_id(self, text):
        text = self.strip_accents(text.lower())
        text = re.sub('[ ]+', '_', text)
        text = re.sub('[^0-9a-zA-Z_-]', '', text)
        return text

    def normalizeTag(self, tag):
        try:
            tag=self.text_to_id(text)
            tag=tag.strip(' _')
            tag=tag.replace('.', '_')
            tag=tag.replace('__', '_')
            tag=tag.strip('_')
            return tag
        finally:
            return tag


t=Test()


text=u'_____hello les 2ème amis     ___'
print t.strip_accents(text)
print t.text_to_id(text)
print ".", t.normalizeTag(text), "."
