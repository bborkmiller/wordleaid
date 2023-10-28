from wordleaid import WordleAid

wa = WordleAid()

info = {
  ('slate', '?_?__'),
  ('marsh', 'YY_?_'),
}

c = wa.find_candidates(info)
print(c)
