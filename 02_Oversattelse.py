import streamlit as st
import json
import re

@st.cache_data
def load_dictionary():
    with open("dictionary.json", "r", encoding="utf-8") as f:
        return json.load(f)

dictionary = load_dictionary()

LANGUAGES = [
    ("GB", "en_GB"),
    ("DK", "Danish [DK]"),
    ("DE", "German-DE [DE]"),
    ("NO", "Norwegian [NO]"),
    ("SE", "Swedish [SE]"),
    ("FI", "Finnish [FI]"),
    ("PL", "Polish [PL]"),
    ("CZ", "Czech [CZ]"),
    ("HU", "Hungarian [HU]"),
    ("NL", "Dutch [NL]"),
    ("SK", "Slovak [SK]"),
    ("FR", "French-FR [FR]"),
    ("SI", "Slovenian [SI]"),
    ("HR", "Croatian [HR]"),
    ("IT", "Italian-IT [IT]"),
    ("ES", "Spanish-ES [ES]"),
    ("BA", "Bosnian [BA]"),
    ("RS", "Serbian [RS]"),
    ("UA", "Ukrainian [UA]"),
    ("RO", "Romanian [RO]"),
    ("BG", "Bulgarian [BG]"),
    ("GR", "Greek [GR]"),
    ("PT", "Portuguese-PT [PT]"),
    ("RU", "Russian [RU]"),
    ("TR", "Turkish [TR]"),
    ("CN", "Chinese [CN]"),
    ("AR", "Arabic [AR] UPDATE"),
]

def tokenize(text, dictionary):
    keys_sorted = sorted(dictionary.keys(), key=lambda x: -len(x))
    pattern = '|'.join(re.escape(key) for key in keys_sorted)
    regex = re.compile(f"({pattern})", re.IGNORECASE)
    tokens = []
    pos = 0
    while pos < len(text):
        match = regex.search(text, pos)
        if match:
            if match.start() != pos:
                tokens.extend(re.findall(r'\w+|\S', text[pos:match.start()]))
            tokens.append(match.group())
            pos = match.end()
        else:
            tokens.extend(re.findall(r'\w+|\S', text[pos:]))
            break
    return tokens

def find_match(token, dictionary):
    for key in dictionary:
        if key.lower() == token.lower():
            return key
    return None

def translate(tokens, dictionary, languages, original_text):
    translations = {}
    for lang_short, lang_code in languages:
        translations[lang_short] = []
        if lang_short == "GB":
            translations[lang_short] = tokens
        else:
            for token in tokens:
                key = find_match(token, dictionary)
                if key and lang_code in dictionary[key]:
                    translations[lang_short].append(dictionary[key][lang_code])
                elif re.match(r"^\W$", token):
                    translations[lang_short].append(token)
                else:
                    translations[lang_short].append("UKENDT")
    return translations

st.set_page_config(page_title="Multisproget ordbogs-oversætter", layout="centered")

st.title("Multisproget ordbogs-oversætter")
st.write("Indsæt din tekst. Output vises på alle sprog, én linje pr. sprog – klar til copy-paste.")

default_text = "Lantern. Material: polypropylene, glass. Uses 2 AA batteries. Batteries not included."
input_text = st.text_area("Indtast tekst:", value=default_text, height=120)

if st.button("Oversæt"):
    tokens = tokenize(input_text.strip(), dictionary)
    translations = translate(tokens, dictionary, LANGUAGES, input_text)

    result_lines = []
    for lang_short, _ in LANGUAGES:
        sentence = ' '.join(translations[lang_short])
        sentence = re.sub(r'\s([,.:\-;])', r'\1', sentence)
        result_lines.append(f"{lang_short}\t{sentence}")

    st.success("Klar til copy-paste:")
    st.code('\n'.join(result_lines), language="text")
    st.download_button("Download som TXT", '\n'.join(result_lines), file_name="translations.txt")

st.info("Hvis et ord ikke oversættes, vises 'UKENDT'. Tilføj det evt. i ordbogen for at opnå fuld oversættelse.")
