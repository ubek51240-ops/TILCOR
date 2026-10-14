import re, sys
sys.stdout.reconfigure(encoding='utf-8')

s = "Chol dengizda o\u2018z qayig\u2018ida suzib yurardi. Bu ma\u2019lum va mashhur san\u2019at edi. Don\u2019t do that, o`g`il! \u00abO\u02bbzbekiston\u00bb, G\u02bbalaba, ma\u02bcno."

APOSTROPHE_CHARS = "'’‘`ʻʼ´ʹ՚′‵ˈ"
# Note: we need to be careful with leading/trailing punctuation or quotes.
# E.g. in 'o‘z', '‘' is inside. In '«Oʻzbekiston»', 'ʻ' is inside.
# If single quotes are used as quotation marks like 'salom', we don't want the outer quotes attached to the word.
# In Uzbek words, apostrophe is either:
# 1) after o/g (o', g', O', G')
# 2) between letters (tutuq belgisi: ma'no, san'at)
# 3) or inside contractions: don't

pattern = re.compile(rf"[a-zA-Z\u0400-\u04FF]+(?:[{APOSTROPHE_CHARS}-][a-zA-Z\u0400-\u04FF]+)*")
tokens = pattern.findall(s)
print("Tokens extracted:")
for t in tokens:
    print(" ", t)
