#!/usr/bin/env python3
"""
Password Variant Tool PRO v5.0 - CLI version
Multi-Stage Mutation (25 groups, 160+ rules) + User Clone Engine + Advanced Chaining
Ported from JS source v5.0 by @teddyvrp
Usage: python3 password_variant.py --mode mutate|clone --input combo.txt --output result.txt
"""
import argparse, re, json, time, sys
from itertools import product

# ========== RULE DEFINITIONS (25 groups from source) ==========

def r_1a(p, u): return [p.lower()]
def r_1b(p, u): return [p.upper()]
def r_1c(p, u):
    for i, c in enumerate(p):
        if c.isalpha(): return [p[:i] + c.upper() + p[i+1:].lower()]
    return []
def r_1d(p, u):
    for i in range(len(p)-1, -1, -1):
        if p[i].isalpha(): return [p[:i] + p[i].upper() + p[i+1:]]
    return []
def r_1e(p, u): return [''.join(c.upper() if i%2==0 else c.lower() for i, c in enumerate(p))]
def r_1f(p, u): return [p.title()]

# Group 2: Numbers
def r_2a(p, u): return [p+"123"]
def r_2b(p, u): return [p+"1234"]
def r_2c(p, u): return [p+"12345"]
def r_2d(p, u): return [p+"123456"]
def r_2e(p, u): return [p+"1234567"]
def r_2f(p, u): return [p+"12345678"]
def r_2g(p, u): return [p+"123456789"]
def r_2h(p, u): return [p+"111"]
def r_2i(p, u): return [p+"999"]
def r_2j(p, u): return [p+"666"]
def r_2k(p, u): return [p+"000"]
def r_2l(p, u): return [p+"777"]
def r_2m(p, u): return [p+"88"]
def r_2n(p, u): return [p+"69"]

# Group 3: Years
def r_3a(p, u): return [p+"1990"]
def r_3b(p, u): return [p+"2000"]
def r_3c(p, u): return [p+"2010"]
def r_3d(p, u): return [p+"2020"]
def r_3e(p, u): return [p+"2024"]
def r_3f(p, u): return [p+"2025"]
def r_3g(p, u): return [p+"2026"]
def r_3h(p, u): return [p+"90"]
def r_3i(p, u): return [p+"95"]
def r_3j(p, u): return [p+"99"]
def r_3k(p, u): return [p+"2023"]
def r_3l(p, u): return [p+"2015"]
def r_3m(p, u): return [p+"2005"]
def r_3n(p, u): return [p+y for y in ["1985","1988","1992","1995","1998","2001","2003","2008","2012","2018"]]

# Group 4: Special chars
def r_4a(p, u): return [p+"@"]
def r_4b(p, u): return [p+"@@"]
def r_4c(p, u): return [p+"!"]
def r_4d(p, u): return [p+"!!"]
def r_4e(p, u): return [p+"#"]
def r_4f(p, u): return [p+"$"]
def r_4g(p, u): return [p+"."]
def r_4h(p, u): return [p+"*"]
def r_4i(p, u): return [p+"&"]
def r_4j(p, u): return [p+"^"]
def r_4k(p, u): return [p+"~"]
def r_4l(p, u): return [p+"%"]
def r_4m(p, u): return [p+"?"]
def r_4n(p, u): return [p+"!!@"]

# Group 5: VN suffixes
def r_5a(p, u): return [p+"vip"]
def r_5b(p, u): return [p+"pro"]
def r_5c(p, u): return [p+"cute"]
def r_5d(p, u): return [p+"love"]
def r_5e(p, u): return [p+"baby"]
def r_5f(p, u): return [p+"hihi"]
def r_5g(p, u): return [p+"kaka"]
def r_5h(p, u): return [p+"ok"]
def r_5i(p, u): return [p+"123ok"]
def r_5j(p, u): return [p+"abc"]
def r_5k(p, u): return [p+"xyz"]
def r_5l(p, u): return [p+"qwerty"]
def r_5m(p, u): return [p+"depzai"]
def r_5n(p, u): return [p+"xinh"]
def r_5o(p, u): return [p+"yeu"]

# Group 6: Leet
def r_6a(p, u): return [re.sub(r'[aA]', '@', p)]
def r_6b(p, u): return [re.sub(r'[oO]', '0', p)]
def r_6c(p, u): return [re.sub(r'[iI]', '1', p)]
def r_6d(p, u): return [re.sub(r'[eE]', '3', p)]
def r_6e(p, u): return [re.sub(r'[sS]', '$', p)]
def r_6f(p, u): return [re.sub(r'[tT]', '7', p)]
def r_6g(p, u): return [re.sub(r'[gG]', '9', p)]
def r_6h(p, u): return [re.sub(r'[bB]', '8', p)]
def r_6i(p, u):
    leet_map = [('aA','@'),('oO','0'),('eE','3'),('iI','1'),('sS','$'),('tT','7'),('gG','9'),('bB','8'),('lL','1')]
    r = p
    for chars, rep in leet_map:
        r = re.sub(r'['+chars+']', rep, r)
    return [r] if r != p else []
def r_6j(p, u): return [re.sub(r'[lL]', '1', p)]

# Group 7: Separators
def _sep(p, sep):
    m = re.match(r'^([A-Za-z]+)(\d+)$', p) or re.match(r'^(\d+)([A-Za-z]+)$', p)
    if m:
        letters = m.group(1) if m.group(1).isalpha() else m.group(2)
        digits = m.group(1) if m.group(1).isdigit() else m.group(2)
        return [letters + sep + digits]
    return []
def r_7a(p, u): return _sep(p, '_')
def r_7b(p, u): return _sep(p, '-')
def r_7c(p, u): return _sep(p, '.')
def r_7d(p, u): return _sep(p, '#')
def r_7e(p, u): return _sep(p, '@')
def r_7f(p, u): return _sep(p, '|')
def r_7g(p, u): return _sep(p, ':')
def r_7h(p, u): return _sep(p, '~')

# Group 8: Reverse & transform
def r_8a(p, u): return [p[::-1]]
def r_8b(p, u):
    letters = re.findall(r'[A-Za-z]', p)
    non_letters = re.findall(r'[^A-Za-z]', p)
    return [''.join(reversed(letters)) + ''.join(non_letters)] if letters else []
def r_8c(p, u):
    nums = re.findall(r'\d+', p)
    if nums: return [p.replace(nums[0], nums[0][::-1], 1)]
    return []
def r_8d(p, u): return [''.join(c.swapcase() for c in p)]
def r_8e(p, u): return [p[-1] + p[:-1]] if len(p) > 1 else []
def r_8f(p, u): return [p[1:] + p[0]] if len(p) > 1 else []
def r_8g(p, u):
    rev = p[::-1]
    return [rev[0].upper() + rev[1:].lower()] if rev else []

# Group 9: Double & repeat
def r_9a(p, u): return [p+p] if len(p)*2 <= 64 else []
def r_9b(p, u): return [p+p+p] if len(p)*3 <= 64 else []
def r_9c(p, u):
    letters = re.findall(r'[A-Za-z]', p)
    return [p + letters[0]*3] if letters and len(p)+3 <= 64 else []
def r_9d(p, u): return [p + p[-1]] if p and len(p)+1 <= 64 else []
def r_9e(p, u): return [p[0] + p] if p and len(p)+1 <= 64 else []
def r_9f(p, u): return [p + p[:3]] if len(p) >= 3 and len(p)+3 <= 64 else []
def r_9g(p, u): return [p + p[-2:]] if len(p) >= 2 and len(p)+2 <= 64 else []

# Group 10: From username
def r_10a(p, u): return [u+"123"] if u else []
def r_10b(p, u): return [u+"@"] if u else []
def r_10c(p, u): return [u+"1999"] if u else []
def r_10d(p, u): return [u+"@123"] if u else []
def r_10e(p, u): return [u+p] if u and p else []
def r_10f(p, u): return [u[0].upper()+u[1:]] if u else []
def r_10g(p, u): return [u+p+"123"] if u and p else []
def r_10h(p, u): return [p+u] if u and p else []
def r_10i(p, u): return [u+"_"+p] if u and p else []
def r_10j(p, u): return [u+"."+p] if u and p else []

# Group 11: Join & transform
def r_11a(p, u):
    m = re.search(r'(\d+)$', p)
    if m: return [p + m.group(1)[0]]
    return []
def r_11b(p, u):
    m = re.match(r'^(\d+)', p)
    if m: return [m.group(1)[0] + p]
    return []
def r_11c(p, u): return [p[0].upper() + p[1:].lower()] if p else []
def r_11d(p, u): return [re.sub(r'[^a-z0-9]+', '_', p.lower())]
def r_11e(p, u): return [re.sub(r'[^a-z0-9]+', '-', p.lower())]
def r_11f(p, u): return [re.sub(r'[^A-Za-z0-9]', '', p)]

# Group 12: Phone
def _is_phone(s): return bool(re.match(r'^0\d{9,10}$', s) or re.match(r'^84\d{9,10}$', s))
def r_12a(p, u): return [p+"@"] if _is_phone(p) else []
def r_12b(p, u): return [p+"123"] if _is_phone(p) else []
def r_12c(p, u): return [p+"vip"] if _is_phone(p) else []
def r_12d(p, u): return [p[1:]] if _is_phone(p) and p.startswith('0') else []
def r_12e(p, u): return ["+84"+p[1:]] if _is_phone(p) and p.startswith('0') else []
def r_12f(p, u): return [p+"ok"] if _is_phone(p) else []

# Group 13: Common words
def r_13a(p, u): return [p+"pass"]
def r_13b(p, u): return [p+"pwd"]
def r_13c(p, u): return [p+"admin"]
def r_13d(p, u): return [p+"root"]
def r_13e(p, u): return [p+"test"]
def r_13f(p, u): return [p+"user"]
def r_13g(p, u): return [p+"login"]
def r_13h(p, u): return [p+"123pass"]
def r_13i(p, u): return [p+"matkhau"]

# Group 14: Language
def r_14a(p, u): return [p+"vn"]
def r_14b(p, u): return [p+"123vn"]
def r_14c(p, u): return [p+"sg"]
def r_14d(p, u): return ["vn_"+p]
def r_14e(p, u): return [p+"asia"]
def r_14f(p, u): return [p+"vn2026"]
def r_14g(p, u): return ["sg_"+p]

# Group 15: Number to letter
def r_15a(p, u): return [p.replace('0', 'o')]
def r_15b(p, u): return [p.replace('1', 'i')]
def r_15c(p, u): return [p.replace('5', 's')]
def r_15d(p, u): return [p.replace('0','o').replace('1','i').replace('5','s').replace('8','B')]
def r_15e(p, u): return [p.replace('8', 'B')]
def r_15f(p, u): return [p.replace('3', 'E')]

# Group 16: Security prefix
def r_16a(p, u): return ["secure"+p]
def r_16b(p, u): return ["secret"+p]
def r_16c(p, u): return ["private"+p]
def r_16d(p, u): return ["hidden"+p]
def r_16e(p, u): return ["my"+p]
def r_16f(p, u): return ["super"+p]

# Group 17: Insert mid
def _insert_mid(p, s):
    if len(p) > 1: return [p[:len(p)//2] + s + p[len(p)//2:]]
    return []
def r_17a(p, u): return _insert_mid(p, '@')
def r_17b(p, u): return _insert_mid(p, '#')
def r_17c(p, u): return _insert_mid(p, '!')
def r_17d(p, u): return _insert_mid(p, '$')
def r_17e(p, u): return _insert_mid(p, '_')
def r_17f(p, u): return _insert_mid(p, '.')

# Group 18: Dates
def r_18a(p, u): return [p+"010101"]
def r_18b(p, u): return [p+"120101"]
def r_18c(p, u): return [p+"150101"]
def r_18d(p, u): return [p+"311201"]
def r_18e(p, u): return [p+"01012000"]
def r_18f(p, u): return [p+d for d in ["01012000","15052000","20092000","31122000","01011995","01012005"]]

# Group 19: Basic numbers
def r_19a(p, u): return [p+"12345"]
def r_19b(p, u): return ["1"+p]
def r_19c(p, u): return [p+"99"]
def r_19d(p, u): return [p+"99999"]
def r_19e(p, u): return [p+"123321"]

# Group 20: Advanced combos
def r_20a(p, u): return [u+p+"2026"] if u and p else []
def r_20b(p, u): return [p+"123vip"]
def r_20c(p, u): return [p.lower()+"123@"]
def r_20d(p, u): return [p.upper()+"123"]
def r_20e(p, u): return [p+"@2026"]
def r_20f(p, u): return [u+"2026!"] if u else []

# Group 21: Game VN
def r_21a(p, u): return [p+"ff"]
def r_21b(p, u): return [p+"mlbb"]
def r_21c(p, u): return [p+"lienquan"]
def r_21d(p, u): return [p+"garena"]
def r_21e(p, u): return [p+"pubg"]
def r_21f(p, u): return [p+"tiktok"]
def r_21g(p, u): return [p+"zalo"]
def r_21h(p, u): return [p+"fb"]
def r_21i(p, u): return [p+"roblox"]
def r_21j(p, u): return [p+"genshin"]

# Group 22: Keyboard
def r_22a(p, u): return [p+"qwerty"]
def r_22b(p, u): return [p+"asdfgh"]
def r_22c(p, u): return [p+"zxcvbn"]
def r_22d(p, u): return [p+"123qwe"]
def r_22e(p, u): return [p+"ytrewq"]
def r_22f(p, u): return [p+"1qaz2wsx"]

# Group 23: Remove chars
def r_23a(p, u): return [re.sub(r'[aeiouAEIOU]', '', p)]
def r_23b(p, u): return [re.sub(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]', '', p)]
def r_23c(p, u): return [re.sub(r'[^A-Za-z]', '', p)]
def r_23d(p, u): return [re.sub(r'[^0-9]', '', p)]
def r_23e(p, u): return [re.sub(r'[0-9]', '', p)]
def r_23f(p, u): return [p[0]*2 + p[1:]] if p else []

# Group 24: Insert mid strings
def r_24a(p, u): return _insert_mid(p, '123')
def r_24b(p, u): return _insert_mid(p, '@')
def r_24c(p, u): return _insert_mid(p, '_')
def r_24d(p, u): return _insert_mid(p, '2026')
def r_24e(p, u): return _insert_mid(p, '!')
def r_24f(p, u): return _insert_mid(p, 'vip')

# Group 25: Extra strong
def r_25a(p, u): return [p + str(time.localtime().tm_year) + "!"]
def r_25b(p, u): return [p.lower() + "123@"]
def r_25c(p, u): return [p.upper() + str(time.localtime().tm_year)]
def r_25d(p, u): return [p.capitalize() + "vip123"]
def r_25e(p, u): return [p + "_" + str(time.localtime().tm_year)]
def r_25f(p, u):
    if len(p) >= 3:
        mid = p[len(p)//2]
        return [p[:len(p)//2] + mid + p[:len(p)//2][::-1]]
    return []

# ========== RULE REGISTRY ==========

ALL_RULES = {
    # Group 1: Case (6 rules)
    '1a': r_1a, '1b': r_1b, '1c': r_1c, '1d': r_1d, '1e': r_1e, '1f': r_1f,
    # Group 2: Numbers (14 rules)
    '2a': r_2a, '2b': r_2b, '2c': r_2c, '2d': r_2d, '2e': r_2e, '2f': r_2f, '2g': r_2g,
    '2h': r_2h, '2i': r_2i, '2j': r_2j, '2k': r_2k, '2l': r_2l, '2m': r_2m, '2n': r_2n,
    # Group 3: Years (14 rules)
    '3a': r_3a, '3b': r_3b, '3c': r_3c, '3d': r_3d, '3e': r_3e, '3f': r_3f, '3g': r_3g,
    '3h': r_3h, '3i': r_3i, '3j': r_3j, '3k': r_3k, '3l': r_3l, '3m': r_3m, '3n': r_3n,
    # Group 4: Special (14 rules)
    '4a': r_4a, '4b': r_4b, '4c': r_4c, '4d': r_4d, '4e': r_4e, '4f': r_4f, '4g': r_4g,
    '4h': r_4h, '4i': r_4i, '4j': r_4j, '4k': r_4k, '4l': r_4l, '4m': r_4m, '4n': r_4n,
    # Group 5: VN suffix (15 rules)
    '5a': r_5a, '5b': r_5b, '5c': r_5c, '5d': r_5d, '5e': r_5e, '5f': r_5f, '5g': r_5g,
    '5h': r_5h, '5i': r_5i, '5j': r_5j, '5k': r_5k, '5l': r_5l, '5m': r_5m, '5n': r_5n, '5o': r_5o,
    # Group 6: Leet (10 rules)
    '6a': r_6a, '6b': r_6b, '6c': r_6c, '6d': r_6d, '6e': r_6e, '6f': r_6f, '6g': r_6g, '6h': r_6h, '6i': r_6i, '6j': r_6j,
    # Group 7: Separators (8 rules)
    '7a': r_7a, '7b': r_7b, '7c': r_7c, '7d': r_7d, '7e': r_7e, '7f': r_7f, '7g': r_7g, '7h': r_7h,
    # Group 8: Reverse (7 rules)
    '8a': r_8a, '8b': r_8b, '8c': r_8c, '8d': r_8d, '8e': r_8e, '8f': r_8f, '8g': r_8g,
    # Group 9: Double (7 rules)
    '9a': r_9a, '9b': r_9b, '9c': r_9c, '9d': r_9d, '9e': r_9e, '9f': r_9f, '9g': r_9g,
    # Group 10: Username (10 rules)
    '10a': r_10a, '10b': r_10b, '10c': r_10c, '10d': r_10d, '10e': r_10e,
    '10f': r_10f, '10g': r_10g, '10h': r_10h, '10i': r_10i, '10j': r_10j,
    # Group 11: Join (6 rules)
    '11a': r_11a, '11b': r_11b, '11c': r_11c, '11d': r_11d, '11e': r_11e, '11f': r_11f,
    # Group 12: Phone (6 rules)
    '12a': r_12a, '12b': r_12b, '12c': r_12c, '12d': r_12d, '12e': r_12e, '12f': r_12f,
    # Group 13: Common (9 rules)
    '13a': r_13a, '13b': r_13b, '13c': r_13c, '13d': r_13d, '13e': r_13e,
    '13f': r_13f, '13g': r_13g, '13h': r_13h, '13i': r_13i,
    # Group 14: Language (7 rules)
    '14a': r_14a, '14b': r_14b, '14c': r_14c, '14d': r_14d, '14e': r_14e, '14f': r_14f, '14g': r_14g,
    # Group 15: Num2Letter (6 rules)
    '15a': r_15a, '15b': r_15b, '15c': r_15c, '15d': r_15d, '15e': r_15e, '15f': r_15f,
    # Group 16: Prefix (6 rules)
    '16a': r_16a, '16b': r_16b, '16c': r_16c, '16d': r_16d, '16e': r_16e, '16f': r_16f,
    # Group 17: Insert mid (6 rules)
    '17a': r_17a, '17b': r_17b, '17c': r_17c, '17d': r_17d, '17e': r_17e, '17f': r_17f,
    # Group 18: Dates (6 rules)
    '18a': r_18a, '18b': r_18b, '18c': r_18c, '18d': r_18d, '18e': r_18e, '18f': r_18f,
    # Group 19: Numbers basic (5 rules)
    '19a': r_19a, '19b': r_19b, '19c': r_19c, '19d': r_19d, '19e': r_19e,
    # Group 20: Advanced (6 rules)
    '20a': r_20a, '20b': r_20b, '20c': r_20c, '20d': r_20d, '20e': r_20e, '20f': r_20f,
    # Group 21: Game VN (10 rules)
    '21a': r_21a, '21b': r_21b, '21c': r_21c, '21d': r_21d, '21e': r_21e,
    '21f': r_21f, '21g': r_21g, '21h': r_21h, '21i': r_21i, '21j': r_21j,
    # Group 22: Keyboard (6 rules)
    '22a': r_22a, '22b': r_22b, '22c': r_22c, '22d': r_22d, '22e': r_22e, '22f': r_22f,
    # Group 23: Remove (6 rules)
    '23a': r_23a, '23b': r_23b, '23c': r_23c, '23d': r_23d, '23e': r_23e, '23f': r_23f,
    # Group 24: Insert mid strings (6 rules)
    '24a': r_24a, '24b': r_24b, '24c': r_24c, '24d': r_24d, '24e': r_24e, '24f': r_24f,
    # Group 25: Extra (6 rules)
    '25a': r_25a, '25b': r_25b, '25c': r_25c, '25d': r_25d, '25e': r_25e, '25f': r_25f,
}

RULE_GROUPS = {
    'case': ['1a','1b','1c','1d','1e','1f'],
    'numbers': ['2a','2b','2c','2d','2e','2f','2g','2h','2i','2j','2k','2l','2m','2n'],
    'years': ['3a','3b','3c','3d','3e','3f','3g','3h','3i','3j','3k','3l','3m','3n'],
    'special': ['4a','4b','4c','4d','4e','4f','4g','4h','4i','4j','4k','4l','4m','4n'],
    'vn_suffix': ['5a','5b','5c','5d','5e','5f','5g','5h','5i','5j','5k','5l','5m','5n','5o'],
    'leet': ['6a','6b','6c','6d','6e','6f','6g','6h','6i','6j'],
    'separator': ['7a','7b','7c','7d','7e','7f','7g','7h'],
    'reverse': ['8a','8b','8c','8d','8e','8f','8g'],
    'double': ['9a','9b','9c','9d','9e','9f','9g'],
    'username': ['10a','10b','10c','10d','10e','10f','10g','10h','10i','10j'],
    'join': ['11a','11b','11c','11d','11e','11f'],
    'phone': ['12a','12b','12c','12d','12e','12f'],
    'common': ['13a','13b','13c','13d','13e','13f','13g','13h','13i'],
    'language': ['14a','14b','14c','14d','14e','14f','14g'],
    'num2letter': ['15a','15b','15c','15d','15e','15f'],
    'prefix': ['16a','16b','16c','16d','16e','16f'],
    'insert_mid': ['17a','17b','17c','17d','17e','17f'],
    'dates': ['18a','18b','18c','18d','18e','18f'],
    'basic_num': ['19a','19b','19c','19d','19e'],
    'advanced': ['20a','20b','20c','20d','20e','20f'],
    'game_vn': ['21a','21b','21c','21d','21e','21f','21g','21h','21i','21j'],
    'keyboard': ['22a','22b','22c','22d','22e','22f'],
    'remove': ['23a','23b','23c','23d','23e','23f'],
    'insert_str': ['24a','24b','24c','24d','24e','24f'],
    'extra': ['25a','25b','25c','25d','25e','25f'],
}

GROUP_NAMES = {
    'case': 'Case & Capitalize', 'numbers': 'Numbers', 'years': 'Years', 'special': 'Special Chars',
    'vn_suffix': 'VN Suffixes', 'leet': 'Leet Speak', 'separator': 'Separators',
    'reverse': 'Reverse & Transform', 'double': 'Double & Repeat', 'username': 'From Username',
    'join': 'Join & Transform', 'phone': 'Phone', 'common': 'Common Words',
    'language': 'Language', 'num2letter': 'Num to Letter', 'prefix': 'Security Prefix',
    'insert_mid': 'Insert Mid', 'dates': 'Dates', 'basic_num': 'Basic Numbers',
    'advanced': 'Advanced Combos', 'game_vn': 'Game VN', 'keyboard': 'Keyboard',
    'remove': 'Remove Chars', 'insert_str': 'Insert Strings', 'extra': 'Extra Strong',
}

def parse_user_pass(line):
    line = line.strip()
    if not line:
        return None
    for sep in [':', '|', ';', '\t', ',']:
        if sep in line:
            parts = line.split(sep, 1)
            if len(parts) == 2:
                u, pwd = parts[0].strip(), parts[1].strip()
                if u and pwd: return (u, pwd)
    return None

def has_entropy_issue(s):
    if re.match(r'^(.)\1{4,}$', s): return True
    for ln in range(1, min(5, len(s)//2 + 1)):
        pat = s[:ln]
        if len(s) >= ln * 3:
            expected = (pat * (len(s)//ln + 1))[:len(s)]
            if s == expected: return True
    return False

def is_valid(v, original, max_len):
    if not v or v == original: return False
    if len(v) < 3 or len(v) > max_len: return False
    if has_entropy_issue(v): return False
    return True

def apply_basic_rules(password, username, rule_ids, max_len, max_per_line):
    variants = set()
    for rid in rule_ids:
        fn = ALL_RULES.get(rid)
        if not fn: continue
        try:
            results = fn(password, username) or []
            for r in results:
                if is_valid(r, password, max_len):
                    variants.add(r)
        except Exception:
            continue
        if len(variants) >= max_per_line:
            break
    return variants

def apply_advanced_chain(password, username, rule_ids, max_len, max_per_line, depth):
    current = {password}
    all_results = set()
    for d in range(depth):
        new_batch = set()
        for pwd in current:
            for rid in rule_ids:
                fn = ALL_RULES.get(rid)
                if not fn: continue
                try:
                    results = fn(pwd, username) or []
                    for r in results:
                        if is_valid(r, password, max_len) and r != password:
                            new_batch.add(r)
                            all_results.add(r)
                except Exception:
                    continue
                if len(all_results) >= max_per_line:
                    break
            if len(all_results) >= max_per_line:
                break
        current = new_batch
        if not current:
            break
        if len(all_results) >= max_per_line:
            break
    return all_results

def apply_custom(password, username, suffixes, prefixes, separators, max_len, max_per_line):
    variants = set()
    for s in suffixes:
        v = password + s
        if is_valid(v, password, max_len): variants.add(v)
    for pr in prefixes:
        v = pr + password
        if is_valid(v, password, max_len): variants.add(v)
    for sep in separators:
        if len(password) > 1:
            mid = len(password) // 2
            v = password[:mid] + sep + password[mid:]
            if is_valid(v, password, max_len): variants.add(v)
    return variants

# ========== USER CLONE ==========

def parse_user_number(user):
    """Return (base, number, pad_width). pad_width = length of the trailing digit string so zero-padding is preserved."""
    m = re.match(r'^(.*?)(\d+)$', user)
    if m:
        num_str = m.group(2)
        return m.group(1), int(num_str), len(num_str)
    return user, 0, 0

def build_clone(base, num, sep, pad):
    ns = str(num).zfill(pad) if pad > 0 else str(num)
    return f"{base}{sep}{ns}" if sep else f"{base}{ns}"

def generate_clones(lines, target, sep, pad, max_results):
    results = []
    seen = set()
    for line in lines:
        parsed = parse_user_pass(line)
        if not parsed: continue
        user, pwd = parsed
        base, current, detected_pad = parse_user_number(user)
        # Use explicit --clone-pad if > 0, otherwise auto-detect from original number width
        use_pad = pad if pad > 0 else detected_pad
        start = current + 1
        if start > target: continue
        for n in range(start, target + 1):
            nu = build_clone(base, n, sep, use_pad)
            key = f"{nu}:{pwd}"
            if key not in seen:
                seen.add(key)
                results.append(key)
                if len(results) >= max_results:
                    return results
    return results

# ========== MAIN PROCESSING ==========

def process_mutation(input_file, output_file, rule_ids, custom_suffixes, custom_prefixes, custom_seps,
                     max_len, max_per_line, max_total, mode, depth):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l for l in f if l.strip()]

    out = []
    t0 = time.time()

    for line in lines:
        parsed = parse_user_pass(line)
        if not parsed: continue
        user, pwd = parsed

        if mode == 'custom' and (custom_suffixes or custom_prefixes or custom_seps):
            variants = apply_custom(pwd, user, custom_suffixes, custom_prefixes, custom_seps, max_len, max_per_line)
        elif mode == 'advanced':
            variants = apply_advanced_chain(pwd, user, rule_ids, max_len, max_per_line, depth)
        else:
            variants = apply_basic_rules(pwd, user, rule_ids, max_len, max_per_line)

        for v in variants:
            out.append(f"{user}:{v}")

        if len(out) >= max_total:
            break

    elapsed = time.time() - t0
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')

    return {
        'ok': True,
        'total_lines': len(lines),
        'output_lines': len(out),
        'time': round(elapsed, 2),
        'output_file': output_file,
    }

def process_clone(input_file, output_file, target, sep, pad, max_results):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l for l in f if l.strip()]

    t0 = time.time()
    clones = generate_clones(lines, target, sep, pad, max_results)
    elapsed = time.time() - t0

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(clones) + '\n')

    return {
        'ok': True,
        'total_lines': len(lines),
        'output_lines': len(clones),
        'time': round(elapsed, 2),
        'output_file': output_file,
    }

# ========== CLI ==========

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Password Variant Tool PRO v5.0')
    p.add_argument('--mode', required=True, choices=['mutate', 'clone', 'custom'])
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--rules', default='', help='Comma-separated rule IDs (e.g., 2a,2b,3a)')
    p.add_argument('--groups', default='', help='Comma-separated group names (e.g., numbers,years,leet)')
    p.add_argument('--max-len', type=int, default=24)
    p.add_argument('--max-per-line', type=int, default=200)
    p.add_argument('--max-total', type=int, default=100000)
    p.add_argument('--depth', type=int, default=2, help='Advanced chaining depth (1-5)')
    p.add_argument('--clone-target', type=int, default=999)
    p.add_argument('--clone-sep', default='')
    p.add_argument('--clone-pad', type=int, default=0)
    p.add_argument('--clone-max', type=int, default=50000)
    p.add_argument('--custom-suffixes', default='', help='Newline-separated custom suffixes')
    p.add_argument('--custom-prefixes', default='', help='Newline-separated custom prefixes')
    p.add_argument('--custom-separators', default='', help='Newline-separated custom separators')
    p.add_argument('--list-rules', action='store_true', help='List all available rules and exit')
    args = p.parse_args()

    if args.list_rules:
        print("=== Password Variant Tool PRO v5.0 - Available Rules ===\n")
        for gid, rids in RULE_GROUPS.items():
            name = GROUP_NAMES.get(gid, gid)
            print(f"Group: {name} ({gid})")
            for rid in rids:
                print(f"  {rid}")
            print()
        sys.exit(0)

    if args.mode == 'clone':
        result = process_clone(args.input, args.output, args.clone_target, args.clone_sep, args.clone_pad, args.clone_max)
    else:
        rule_ids = []
        if args.rules:
            rule_ids = [r.strip() for r in args.rules.split(',') if r.strip() in ALL_RULES]
        if args.groups:
            for g in args.groups.split(','):
                g = g.strip()
                if g in RULE_GROUPS:
                    rule_ids.extend(RULE_GROUPS[g])
        if not rule_ids:
            # Default: numbers + years + special + vn_suffix
            rule_ids = RULE_GROUPS['numbers'][:7] + RULE_GROUPS['years'][:7] + RULE_GROUPS['special'][:7]

        suffixes = [s.strip() for s in args.custom_suffixes.split('\n') if s.strip()] if args.custom_suffixes else []
        prefixes = [s.strip() for s in args.custom_prefixes.split('\n') if s.strip()] if args.custom_prefixes else []
        seps = [s.strip() for s in args.custom_separators.split('\n') if s.strip()] if args.custom_separators else []

        result = process_mutation(
            args.input, args.output, rule_ids, suffixes, prefixes, seps,
            args.max_len, args.max_per_line, args.max_total, args.mode, args.depth
        )

    print(json.dumps(result, ensure_ascii=False))
