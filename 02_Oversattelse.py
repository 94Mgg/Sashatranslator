import streamlit as st
import json
import re

# Bredere layout via Streamlit settings og CSS-hack
st.set_page_config(page_title="Multisproget ordbogs-oversætter", layout="wide")

# Bredere kodeblok
st.markdown("""
    <style>
        .stCodeBlock, .stTextArea, .element-container, textarea, .stDownloadButton, .stButton, .stTextInput, .stTextArea {
            max-width: 1200px !important;
            width: 100% !important;
        }
        .stApp {
            max-width: 1200px;
            margin: auto;
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_dictionary():
    with open("dictionary.json", "r", encoding="utf-8") as f:
        return json.load(f)

dictionary = load_dictionary()

# Tillad aliaser pr. sprog (første match, der har en ikke-tom værdi, bruges)
LANGUAGES = {
    "GB": ["en_GB"],
    "DK": ["Danish [DK]"],
    "DE": ["German-DE [DE]"],
    "NO": ["Norwegian [NO]"],
    "SE": ["Swedish [SE]"],
    "FI": ["Finnish [FI]"],
    "PL": ["Polish [PL]"],
    "CZ": ["Czech [CZ]"],
    "HU": ["Hungarian [HU]"],
    "NL": ["Dutch [NL]"],
    "SK": ["Slovak [SK]"],
    "FR": ["French-FR [FR]"],
    "SI": ["Slovenian [SI]"],
    "HR": ["Croatian [HR]"],
    "IT": ["Italian-IT [IT]"],
    "ES": ["Spanish-ES [ES]"],
    "BA": ["Bosnian [BA]"],
    "RS": ["Serbian [RS]"],
    "UA": ["Ukrainian [UA]"],
    "RO": ["Romanian [RO]"],
    "BG": ["Bulgarian [BG]"],
    "GR": ["Greek [GR]"],
    "PT": ["Portuguese-PT [PT]"],
    "RU": ["Russian [RU]"],
    "TR": ["Turkish [TR]"],
    "CN": ["Chinese [CN]"],
    # >>> Her er tricket: accepter begge varianter <<<
    "AR": ["Arabic [AR] UPDATE", "Arabic [AR]"],
}

def tokenize(text, dictionary):
    # Lav en regex der matcher længste nøgle først
    keys_sorted = sorted(dictionary.keys(), key=lambda x: -len(x))
    pattern = '|'.join(re.escape(key) for key in keys_sorted) if keys_sorted else r"(?!x)x"  # tom ordbog guard
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
    # Case-insensitivt opslag mod nøglerne (engelske termer)
    tl = token.lower()
    for key in dictionary:
        if key.lower() == tl:
            return key
    return None

def find_first_lang_value(entry_dict, lang_aliases):
    # Returner første ikke-tomme værdi for de mulige kolonnenavne
    for alias in lang_aliases:
        if alias in entry_dict:
            val = entry_dict[alias]
            if isinstance(val, str) and val.strip():
                return val.strip()
    return None

def translate(tokens, dictionary, languages, original_text):
    translations = {}
    for lang_short, aliases in languages.items():
        translations[lang_short] = []
        if lang_short == "GB":
            # GB = gengiv input tokens som de er
            translations[lang_short] = tokens
        else:
            for token in tokens:
                key = find_match(token, dictionary)
                if key:
                    val = find_first_lang_value(dictionary[key], aliases)
                    if val is not None:
                        translations[lang_short].append(val)
                        continue
                # Behold tegnsætning 1-tegn (.,:;- etc.)
                if re.match(r"^\W$", token):
                    translations[lang_short].append(token)
                else:
                    translations[lang_short].append("UKENDT")
    return translations

def clean_sentence(sentence):
    # Fjern mellemrum før tegn
    sentence = re.sub(r'\s([,.:\-;])', r'\1', sentence)
    # Saml sekvenser af tegn til ét
    sentence = re.sub(r'([.:\-;,]){2,}', r'\1', sentence)
    # Normalisér blandede kombinationer (.::, .:, :., etc.) til kun sidste tegn
    sentence = re.sub(r'([.:\-;,])([.:\-;,])', r'\2', sentence)
    # Fjern evt. yderligere gentagelser
    sentence = re.sub(r'([.:\-;,])\1+', r'\1', sentence)
    # Stram slutningen
    sentence = re.sub(r'([.:\-;,])\s*$', r'\1', sentence)
    sentence = re.sub(r'\s+$', '', sentence)
    return sentence

st.title("Multisproget ordbogs-oversætter")
st.write("Indsæt din tekst. Output vises på alle sprog, én linje pr. sprog – klar til copy-paste.")

default_text = "Lantern. Material: polypropylene, glass. Uses 2 AA batteries. Batteries not included."
input_text = st.text_area("Indtast tekst:", value=default_text, height=120, key="input_text_area")

if st.button("Oversæt"):
    tokens = tokenize(input_text.strip(), dictionary)
    translations = translate(tokens, dictionary, LANGUAGES, input_text)

    result_lines = []
    for lang_short in LANGUAGES.keys():
        sentence = ' '.join(translations[lang_short])
        sentence = clean_sentence(sentence)
        result_lines.append(f"{lang_short}\t{sentence}")

    result_txt = '\n'.join(result_lines)

    st.success("Klar til copy-paste:")
    st.code(result_txt, language="text")

    # Kopier til clipboard-knap (JS)
    import streamlit.components.v1 as components
    st.markdown(
        """
        <button id="copybtn" style="margin-bottom:1em;">Kopier til udklipsholder</button>
        <script>
        const copybtn = document.getElementById('copybtn');
        if (copybtn) {
            copybtn.onclick = () => {
                const text = document.querySelector('pre').innerText;
                navigator.clipboard.writeText(text);
                copybtn.innerText = 'Kopieret!';
                setTimeout(() => {copybtn.innerText = 'Kopier til udklipsholder';}, 1500);
            };
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    st.download_button("Download som TXT", result_txt, file_name="translations.txt")

st.info("Hvis et ord ikke oversættes, vises 'UKENDT'. Tilføj det evt. i ordbogen for at opnå fuld oversættelse.")
