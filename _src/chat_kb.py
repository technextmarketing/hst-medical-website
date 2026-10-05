"""
Ask HST knowledge base (owned separately from build.py).

    chat_kb.build(...)  ->  assets/data/chat-kb.json        (called once, at the end of _src/build.py)

The "Ask HST" assistant (assets/js/chat.js) runs entirely in the browser: no backend, no API key, no external AI
service. Everything it knows is generated here, on every build, from the same data the pages are built from:
PRODUCTS (variants, prices, codes, usage, ingredients, origin), CATS + CAT_ORDER, GUIDES (category FAQs), the
need tags, POSTS (health notes), the stockist list (_src/where_data.json), the flipbook index
(_src/catalogue_index.json) and the text of the built About / Brands / Trade / Contact / Privacy pages.

What is curated here (and nowhere else): vocabulary the catalogue itself does not contain, i.e. product aliases
and misspellings, symptom words mapped to the catalogue's own benefit lines, and a small area gazetteer so a
shopper can ask for a store "near Tampines". Nothing here states a medical claim of its own: every "why this
product" sentence is picked from that product's own catalogue text at build time (see _why()).
"""
import html as _html
import json
import os
import re
import unicodedata
from html.parser import HTMLParser

import page_about

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- text helpers
def fold(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.replace("®", "").replace("™", "").replace("©", "").lower()


def words(s):
    s = fold(s).replace("&", " and ").replace("’", "").replace("'", "")
    return re.sub(r"[^a-z0-9.$]+", " ", s).split()


def plain(s):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", str(s)))).strip()


def clip(s, n):
    s = re.sub(r"\s+", " ", str(s)).strip()
    if len(s) <= n:
        return s
    cut = s[:n]
    k = max(cut.rfind(". "), cut.rfind("; "))
    if k > n * 0.55:
        return cut[:k + 1].strip()
    return cut[:cut.rfind(" ")].rstrip(",;:") + "..."


# ---------------------------------------------------------------- curated product vocabulary
# Short names for chips and one-line lists.
SHORT = {
    "rheuma-salve-balm": "Rheuma-Salve Balm", "rheuma-salve-creme": "Rheuma-Salve Creme", "rheuma-salve-liniment": "Rheuma-Salve Liniment",
    "rheuma-salve-pain-relief-patch-cool": "Rheuma-Salve Patch (Cool)", "rheuma-salve-medi-stick": "Rheuma-Salve Medi-Stick",
    "zoo-vite-elderberry-gummies": "Zoo-Vite Elderberry Gummies", "zoo-vite-lutein-jelly": "Zoo-Vite Lutein Jelly",
    "zoo-vite-multivitamin-gummies": "Zoo-Vite Multivitamin Gummies", "zoo-vite-immune-jelly": "Zoo-Vite Immune Jelly",
    "zoo-vite-dha-jelly": "Zoo-Vite DHA Jelly", "cough-alievaid-herbal-lintus": "Cough Alievaid Lintus", "flu-gard": "Flu Gard",
    "sinus-clear-2-in-1": "Sinus Clear 2-in-1", "neuro-gard": "Neuro Gard", "arthro-gard": "Arthro Gard", "curqmax": "CurQmax",
    "fish-oil-minigels": "Fish Oil Minigels", "max-omega": "Max-Omega", "boost-immune": "Boost Immune", "c-rosehips": "C+ Rosehips",
    "therra-m": "Therra-M", "synbioten": "Synbioten", "uri-gard": "Uri Gard", "liver-gard-forte": "Liver Gard Forte",
    "pearl-powder": "Pearl Powder", "age-defying-nmn": "Age-Defying NMN", "safflower-red-flower-oil": "Safflower Red Flower Oil",
    "sleep-fast-melatonin-gummies": "Sleep Fast Melatonin Gummies", "sleep-aid-melatonin-10mg": "Sleep Aid Melatonin 10mg",
    "melatonin-5mg": "Melatonin 5mg", "korean-red-ginseng": "Korean Red Ginseng", "american-ginseng": "American Ginseng",
    "lingzhi-cracked-spores": "Lingzhi Cracked Spores", "womens-choice": "Women's Choice", "algaomega": "AlgaOmega",
}

# What each product IS, in the shopper's words (also drives the compare answer and the "formats" chips).
FORMAT = {
    "rheuma-salve-balm": "balm", "rheuma-salve-creme": "creme", "rheuma-salve-liniment": "roll-on liniment",
    "rheuma-salve-pain-relief-patch-cool": "patch", "rheuma-salve-medi-stick": "medi-stick",
}

# Curated aliases: how people actually say it. Name n-grams are generated on top of these.
ALIASES = {
    "rheuma-salve-balm": ["balm", "balms", "pain balm", "pain relief balm", "rheuma balm", "rs balm", "salve balm", "white balm", "snowy white balm",
                          "extra strength balm", "ointment", "muscle rub", "pain rub", "tiger balm style", "the jar", "50g balm", "rheuma salve balm"],
    "rheuma-salve-creme": ["creme", "cremes", "cream", "creams", "rheuma cream", "pain cream", "muscle cream", "rs cream", "rs creme", "rheuma creme", "salve cream", "salve creme"],
    "rheuma-salve-liniment": ["liniment", "liniments", "linament", "roll on", "rollon", "roll-on", "roller", "roll on oil", "headache oil", "headache roll on",
                              "motion sickness oil", "rs liniment", "rheuma liniment", "salve liniment", "headache roller"],
    "rheuma-salve-pain-relief-patch-cool": ["patch", "patches", "plaster", "plasters", "cool patch", "cooling patch", "pain patch", "pain relief patch", "rs patch",
                                            "patch cool", "back patch", "muscle patch", "rheuma patch", "salve patch", "pain plaster"],
    "rheuma-salve-medi-stick": ["stick", "medi stick", "medistick", "medi-stick", "on the go stick", "on the go", "pocket stick", "pain stick", "rs stick", "rheuma stick", "salve stick", "balm stick"],
    "american-ginseng": ["american ginseng", "usa ginseng", "us ginseng", "xi yang shen"],
    "cordyceps-cs-4": ["cordyceps", "cordyceps cs4", "cs4", "cs 4", "cordyceps cs 4"],
    "deer-antler": ["deer antler", "deer antlers", "antler", "antlers"],
    "korean-red-ginseng": ["korean red ginseng", "red ginseng", "korean ginseng", "gao li shen", "korea ginseng"],
    "lingzhi-cracked-spores": ["lingzhi", "ling zhi", "reishi", "ganoderma", "cracked spores", "lingzhi spores", "lingzhi plus", "lingzhi cracked spores plus"],
    "deep-sea-squalene": ["squalene", "deep sea squalene", "shark liver oil", "shark oil", "shark squalene", "squalane"],
    "pearl-powder": ["pearl powder", "pearl", "medicinal pearl", "pearl capsules", "pearl supplement", "pure pearl powder", "pure medicinal pearl powder"],
    "shou-wu-hair-plus": ["shou wu", "shouwu", "shou wu hair", "he shou wu", "hair plus", "hair supplement", "hair vitamin", "hair vitamins", "hair tonic", "shou wu plus", "shouwu plus", "shouwu hair"],
    "crocodile-pure-skin-oil": ["crocodile oil", "crocodile", "skin oil", "croc oil", "crocodile skin oil", "pure skin oil", "crocodile pure skin oil"],
    "age-defying-nmn": ["nmn", "age defying", "age defying nmn", "nmn pearl collagen", "collagen", "nmn sachets", "nmn collagen", "nmn pearl"],
    "gold-lion-rheumatic-oil": ["gold lion", "gold lion oil", "golden lion", "gold lion rheumatic", "rheumatic oil", "lion oil", "gold lion rheumatic oil"],
    "safflower-red-flower-oil": ["safflower", "red flower oil", "hung far oil", "hong hua you", "hung far", "red oil", "safflower oil", "red flower", "safflower red flower oil"],
    "qian-li-zhui-feng-oil": ["qian li", "qian li zhui feng", "qianli", "qian li oil", "zhui feng", "qianlizhuifeng", "qian li zhui feng oil", "orange oil"],
    "zoo-vite-elderberry-gummies": ["elderberry", "elderberry gummies", "elderberry gummy", "perky penguin", "penguin", "kids elderberry"],
    "zoo-vite-lutein-jelly": ["lutein", "lutein jelly", "inspector charley", "charley", "kids eye jelly", "eye jelly"],
    "zoo-vite-multivitamin-gummies": ["safari buddies", "safari", "kids multivitamin", "multivitamin gummies", "multivitamin gummy", "children multivitamin", "zoo vite multivitamin"],
    "zoo-vite-immune-jelly": ["super panda", "panda", "immune jelly", "kids immune jelly", "zoo vite immune"],
    "zoo-vite-dha-jelly": ["professor skippy", "skippy", "dha jelly", "kids dha jelly", "zoo vite dha"],
    "alievaid-herbal-drops": ["alievaid herbal drops", "alievaid drops", "alievaid", "herbal drops", "herbal lozenge", "herbal lozenges", "throat lozenge", "throat lozenges",
                              "throat sweets", "throat candy", "loquat drops", "alievaid lozenge", "alievaid lozenges"],
    "cough-alievaid-herbal-lintus": ["lintus", "linctus", "cough alievaid", "alievaid lintus", "alievaid syrup", "alievaid cough syrup", "herbal lintus", "cough lintus",
                                     "alievaid cough", "cough syrup", "cough medicine", "cough liquid", "cough bottle"],
    "flu-gard": ["flu gard", "flugard", "flu guard", "fluguard", "flu remedy", "flu capsules", "flu herbal remedy", "flu medicine", "flu gard herbal remedy"],
    "ivy-leaf-cough-syrup": ["ivy leaf syrup", "ivy syrup", "ivy leaf cough syrup", "ivy cough syrup", "sachet syrup", "cough syrup sachets", "syrup sachets",
                             "ivy leaf sachet", "ivy leaf sachets", "cough syrup", "cough medicine", "cough sachets"],
    "ivy-leaf-drops": ["ivy leaf drops", "ivy drops", "ivy leaf lozenge", "ivy lozenge", "ivy leaf lozenges", "ivy sweets"],
    "sinus-clear-2-in-1": ["sinus clear", "sinus", "sinusclear", "nasal inhaler", "inhaler", "nose inhaler", "sinus inhaler", "2 in 1 inhaler", "sinus clear 2 in 1", "nasal stick"],
    "arthro-gard": ["arthro gard", "arthrogard", "arthro guard", "arthro", "arthro gard advanced formula"],
    "curqmax": ["curqmax", "curq max", "curcumax", "curqmax turmeric", "turmeric", "boswellia", "turmeric boswellia", "curcumin", "cur q max"],
    "maxi-cal": ["maxi cal", "maxical", "max cal", "coral calcium", "calcium", "calcium softgel", "calcium softgels"],
    "vitamin-d3-k2": ["vitamin d3 k2", "d3 k2", "d3k2", "vitamin d", "vitamin d3", "vit d", "vit d3", "vit d3 k2", "k2", "vitamin k2", "d3"],
    "algaomega": ["algaomega", "alga omega", "algae omega", "algae omega 3", "algal omega", "plant based omega", "vegan omega", "vegan omega 3", "algae dha"],
    "clear-eyes-plus": ["clear eyes plus", "clear eyes", "clear eye plus", "clear eye", "eye supplement", "eye vitamins"],
    "dha-600": ["dha 600", "dha600", "dha", "dha 600mg", "baby dha", "dha softgels"],
    "fish-oil-minigels": ["fish oil", "fishoil", "fish oil minigels", "minigels", "mini gels", "omega 3 fish oil", "high strength omega 3", "fish oil softgels"],
    "max-omega": ["max omega", "maxomega", "max-omega", "omega 3 d3", "omega 3 with d3", "omega d3", "high potency omega 3"],
    "neuro-gard": ["neuro gard", "neurogard", "neuro guard", "ginkgo", "ginkgo biloba", "gingko", "ginko", "neuro gard ginkgo"],
    "magnesium-glycinate": ["magnesium", "magnesium glycinate", "mag glycinate", "magnesium glycine", "magnesium supplement", "magnesium capsules"],
    "melatonin-5mg": ["melatonin 5mg", "melatonin 5 mg", "5mg melatonin", "5 mg melatonin", "melatonin 5", "melatonin five mg", "melatonin capsules"],
    "sleep-aid-melatonin-10mg": ["sleep aid", "sleep aid melatonin", "melatonin 10mg", "melatonin 10 mg", "10mg melatonin", "10 mg melatonin", "melatonin 10", "sleepaid", "sleep aid 10mg"],
    "sleep-fast-melatonin-gummies": ["sleep fast", "sleepfast", "melatonin gummies", "melatonin gummy", "sleep gummies", "sleep gummy", "sleep fast gummies", "sleep fast melatonin"],
    "boost-immune": ["boost immune", "boost immunity", "boostimmune", "effervescent vitamin c", "effervescent", "vitamin c tablets", "vitamin c effervescent", "c1000", "vitamin c 1000",
                     "vit c 1000mg", "fizzy vitamin c", "vitamin c fizzy", "immune c", "vitamin c", "vit c"],
    "c-rosehips": ["c rosehips", "c+ rosehips", "rosehips", "rose hips", "rosehip", "time release c", "time release vitamin c", "timed release vitamin c", "vitamin c rosehips",
                   "c plus rosehips", "slow release vitamin c", "vitamin c", "vit c"],
    "therra-m": ["therra m", "therram", "therra", "terra m", "thera m", "theram", "multi vitamin", "multivitamin", "multivitamins", "multi vitamin with minerals", "a to z vitamins", "adult multivitamin"],
    "synbioten": ["synbioten", "symbioten", "synbiotin", "probiotic", "probiotics", "prebiotic", "gut supplement", "synbiotic", "pre and probiotics"],
    "libi-max": ["libi max", "libimax", "libi-max", "libido max", "male supplement"],
    "liver-gard-forte": ["liver gard", "livergard", "liver guard", "liver gard forte", "liver forte", "liver supplement", "milk thistle"],
    "uri-gard": ["uri gard", "urigard", "uri guard", "uri gard herbal", "uri gard herbal formula"],
    "womens-choice": ["womens choice", "women choice", "womens", "woman choice", "ladies choice"],
}

# Tokens that may stand alone as a product reference (people do say "add 2 balms", "gummies please").
SINGLE_OK = {"balm", "creme", "cream", "liniment", "patch", "plaster", "stick", "drops", "lozenge", "lozenges", "syrup", "linctus", "lintus", "gummies", "gummy", "jelly",
             "oil", "ginseng", "melatonin", "omega", "inhaler", "sinus", "cordyceps", "lingzhi", "squalene", "elderberry", "lutein", "nmn", "collagen", "pearl", "antler",
             "magnesium", "calcium", "turmeric", "ginkgo", "probiotic", "probiotics", "multivitamin", "rosehips", "alievaid", "salve", "dha", "reishi", "ointment", "plasters", "patches", "rheuma", "lintus", "curqmax", "algaomega", "synbioten", "neuro", "arthro"}
# Name words that are also symptom words: never a product reference on their own.
NEED_ONLY = {"rheumatic", "glycinate", "circulation", "stamina", "immunity", "endurance", "vitality"}
# Words that never carry a product on their own (they are needs or filler).
GENERIC = set("a an the of and for with in on to by plus formula advanced high strength potency pure herbal remedy medicinal complex time release daily health pain relief "
              "cough cold flu vitamin vitamins supplement supplements original extra capsules softgels vegicaps tablets tablet sachets sachet pack single twin triple "
              "value travel bundle gard forte medical natural fast clear".split())

# Mis-spellings the edit-distance check cannot reach (3+ edits, glued or split words). wrong -> right.
# Chat shorthand (pls, thx, wanna ...) is handled in chat.js; this map is only product and health vocabulary.
SPELL = {
    "ruma": "rheuma", "rhuema": "rheuma", "rheumah": "rheuma", "reuma": "rheuma", "rhuma": "rheuma", "romah": "rheuma", "rheumar": "rheuma", "rheema": "rheuma", "rhuemah": "rheuma",
    "romasalve": "rheuma salve", "rumasalve": "rheuma salve", "rhuemasalve": "rheuma salve", "reumasalve": "rheuma salve", "rheumasave": "rheuma salve", "rheumasalf": "rheuma salve",
    "rheumasalve": "rheuma salve", "rheumasalva": "rheuma salve", "rheumasalv": "rheuma salve", "rheumasalvebalm": "rheuma salve balm", "rheumasalvecreme": "rheuma salve creme",
    "zoovite": "zoo vite", "zuvite": "zoo vite", "zoovit": "zoo vite", "zoovitamin": "zoo vite", "zoovitamins": "zoo vite", "zuvit": "zoo vite",
    "ivyleaf": "ivy leaf", "ivyleaves": "ivy leaf", "ivy leaves": "ivy leaf", "ivy leave": "ivy leaf", "ivy leafs": "ivy leaf",
    "melaton": "melatonin", "melatonine": "melatonin", "melatonim": "melatonin",
    "ginsen": "ginseng", "ginsing": "ginseng", "jinseng": "ginseng", "ginsang": "ginseng", "genseng": "ginseng", "ginseg": "ginseng",
    "cordiceps": "cordyceps", "cordycep": "cordyceps", "cordyseps": "cordyceps", "cordicep": "cordyceps",
    "lingzi": "lingzhi", "linzhi": "lingzhi",
    "squalane": "squalene", "squaline": "squalene",
    "flugard": "flu gard", "fluguard": "flu gard", "livergard": "liver gard", "urigard": "uri gard", "neurogard": "neuro gard", "arthrogard": "arthro gard",
    "maxical": "maxi cal", "boostimmune": "boost immune", "sinusclear": "sinus clear",
    "linctus": "lintus", "aliavaid": "alievaid", "alieveid": "alievaid", "aleivaid": "alievaid", "alivaid": "alievaid",
    "gaurd": "gard", "guard": "gard", "gaurds": "gard", "guards": "gard",
    "tummy": "stomach", "belly": "stomach", "migrane": "migraine", "migrain": "migraine", "throte": "throat", "thoat": "throat", "troat": "throat", "flue": "flu", "feaver": "fever",
    "plegm": "phlegm", "flem": "phlegm", "insomia": "insomnia", "insomnea": "insomnia", "cholestrol": "cholesterol", "colesterol": "cholesterol",
}

# ---------------------------------------------------------------- needs (symptom words -> the catalogue's own lines)
# (id, label, user phrases, shelves, ranked product slugs, catalogue words that pick the "why" line, optional note from the site's own copy)
PAIN_NOTE = "If pain persists beyond a week, see a doctor."
COLD_NOTE = "See a doctor if fever lasts more than three days or if you have difficulty breathing."
NEEDS_KB = [
    ("back-pain", "back pain", ["back pain", "backache", "back ache", "lower back", "lumbago", "sore back", "stiff back", "bad back", "back hurts", "aching back", "spine pain"],
     ["pain-relief"], ["rheuma-salve-pain-relief-patch-cool", "rheuma-salve-balm", "qian-li-zhui-feng-oil", "gold-lion-rheumatic-oil", "rheuma-salve-medi-stick"], ["back", "lumbago"], PAIN_NOTE),
    ("neck-shoulder", "neck and shoulder pain", ["neck pain", "stiff neck", "shoulder pain", "frozen shoulder", "tight shoulders", "sore neck", "neck and shoulder", "shoulder tension", "neck tension", "sore shoulder"],
     ["pain-relief"], ["rheuma-salve-pain-relief-patch-cool", "rheuma-salve-medi-stick", "safflower-red-flower-oil", "gold-lion-rheumatic-oil", "rheuma-salve-balm"], ["neck", "shoulder"], PAIN_NOTE),
    ("muscle", "muscle aches", ["muscle ache", "muscle aches", "sore muscles", "muscle pain", "muscle cramp", "muscle cramps", "cramps", "cramp", "tense muscles", "tight muscles", "body ache", "body aches", "body pain",
                                "aching muscles", "doms", "muscle soreness", "sore body", "tired muscles", "pulled muscle"],
     ["pain-relief"], ["rheuma-salve-creme", "rheuma-salve-balm", "rheuma-salve-pain-relief-patch-cool", "rheuma-salve-medi-stick", "gold-lion-rheumatic-oil"], ["muscle"], PAIN_NOTE),
    ("sports", "sports and exercise recovery", ["sports", "sport injury", "gym", "workout", "work out", "exercise", "running", "football", "badminton", "after training", "sports recovery", "marathon", "jogging", "yoga"],
     ["pain-relief"], ["rheuma-salve-creme", "rheuma-salve-pain-relief-patch-cool", "rheuma-salve-medi-stick", "rheuma-salve-balm", "gold-lion-rheumatic-oil"], ["sport", "recovery", "muscle"], PAIN_NOTE),
    ("sprain", "sprains and strains", ["sprain", "sprained", "strain", "strained", "twisted ankle", "twisted", "sprained ankle", "swollen ankle", "pulled", "bruise", "bruises", "bruised", "swelling"],
     ["pain-relief", "traditional-pain-relief"], ["rheuma-salve-balm", "rheuma-salve-medi-stick", "gold-lion-rheumatic-oil", "qian-li-zhui-feng-oil", "safflower-red-flower-oil"], ["sprain", "strain"], PAIN_NOTE),
    ("joint-pain", "joint pain", ["joint pain", "joints", "joint", "knee", "knees", "knee pain", "arthritis", "rheumatism", "rheumatic", "stiff joints", "swollen joints", "achy joints", "aching joints",
                                  "elbow", "wrist pain", "gout", "bad knees", "knee ache", "knee problem", "osteoarthritis", "stairs"],
     ["pain-relief", "traditional-pain-relief", "bones-joints"], ["rheuma-salve-balm", "gold-lion-rheumatic-oil", "qian-li-zhui-feng-oil", "arthro-gard", "curqmax"], ["joint", "rheumatic", "arthritis"], PAIN_NOTE),
    ("joint-supplement", "joint support supplements", ["joint supplement", "joint supplements", "cartilage", "glucosamine", "chondroitin", "joint health", "joint mobility", "flexibility", "mobility", "joint support", "joint vitamins", "collagen for joints"],
     ["bones-joints"], ["arthro-gard", "curqmax", "maxi-cal", "vitamin-d3-k2"], ["joint", "mobility", "flexib"], ""),
    ("headache", "headache", ["headache", "head ache", "headaches", "migraine", "head pain", "sore head", "head hurts", "splitting head", "sinus headache", "temple"],
     ["pain-relief", "cough-cold-flu"], ["rheuma-salve-liniment", "sinus-clear-2-in-1", "gold-lion-rheumatic-oil"], ["headache"], "If headaches are severe, sudden or keep coming back, please see a doctor."),
    ("giddy", "giddiness and motion sickness", ["giddy", "giddiness", "dizzy", "dizziness", "motion sickness", "car sick", "carsick", "sea sick", "seasick", "travel sick", "nausea", "vertigo", "light headed", "lightheaded"],
     ["pain-relief"], ["rheuma-salve-liniment", "korean-red-ginseng"], ["giddi", "motion"], "If dizziness is frequent or severe, please see a doctor."),
    ("sore-throat", "sore throat", ["sore throat", "throat pain", "scratchy throat", "itchy throat", "throat infection", "tonsils", "hoarse", "lose voice", "losing voice", "throat hurts", "painful throat", "dry throat", "irritated throat", "throat"],
     ["cough-cold-flu"], ["alievaid-herbal-drops", "ivy-leaf-drops", "cough-alievaid-herbal-lintus"], ["throat"], COLD_NOTE),
    ("dry-cough", "dry or irritating cough", ["dry cough", "irritating cough", "tickly cough", "tickle cough", "night cough", "cough at night", "persistent cough", "coughing", "cough", "cough a lot", "coughs", "keep coughing"],
     ["cough-cold-flu"], ["alievaid-herbal-drops", "ivy-leaf-cough-syrup", "ivy-leaf-drops", "cough-alievaid-herbal-lintus"], ["cough"], COLD_NOTE),
    ("phlegm", "cough with phlegm", ["phlegm", "chesty cough", "wet cough", "productive cough", "mucus", "cough with phlegm", "chest congestion", "phlegmy", "chesty", "plegm", "flem"],
     ["cough-cold-flu"], ["cough-alievaid-herbal-lintus", "ivy-leaf-cough-syrup", "ivy-leaf-drops", "flu-gard"], ["phlegm", "mucus", "chesty"], COLD_NOTE),
    ("cold-flu", "cold and flu", ["cold", "flu", "common cold", "flu symptoms", "cold symptoms", "influenza", "running nose", "runny nose", "sneeze", "sneezing", "fever", "feverish", "high temperature", "chills", "sick",
                                  "catching a cold", "down with flu", "got flu", "flu and cough", "cold and cough", "under the weather", "unwell"],
     ["cough-cold-flu"], ["flu-gard", "boost-immune", "c-rosehips", "cough-alievaid-herbal-lintus"], ["flu", "fever", "runny", "cold"], COLD_NOTE),
    ("blocked-nose", "blocked nose", ["blocked nose", "stuffy nose", "stuffed nose", "nose blocked", "congestion", "congested", "sinus", "sinusitis", "nasal congestion", "cant breathe through nose", "block nose", "bunged up", "stuffy"],
     ["cough-cold-flu"], ["sinus-clear-2-in-1", "rheuma-salve-liniment", "rheuma-salve-balm", "alievaid-herbal-drops"], ["nose", "nasal", "congestion", "blocked", "airway"], COLD_NOTE),
    ("bites", "insect bites", ["mosquito bite", "mosquito bites", "insect bite", "insect bites", "bug bite", "bug bites", "itchy bite", "bitten", "mozzie"],
     ["cough-cold-flu", "pain-relief"], ["sinus-clear-2-in-1", "rheuma-salve-liniment"], ["bite", "mosquito"], ""),
    ("immunity", "immunity", ["immunity", "immune", "immune system", "boost immunity", "strengthen immunity", "weak immune", "weak immunity", "catch cold easily", "fall sick often", "get sick often", "always sick", "defence", "defense",
                              "antioxidant", "antioxidants", "resistance"],
     ["immunity-allergy", "immunity-energy"], ["boost-immune", "c-rosehips", "synbioten", "cordyceps-cs-4", "korean-red-ginseng"], ["immun"], ""),
    ("vitamin-c", "vitamin C", ["vitamin c", "vit c", "ascorbic", "c vitamin", "high dose vitamin c"],
     ["immunity-allergy"], ["boost-immune", "c-rosehips", "therra-m"], ["immune", "vitamin c"], ""),
    ("energy", "energy and stamina", ["energy", "tired", "tiredness", "fatigue", "stamina", "lethargy", "lethargic", "low energy", "no energy", "exhausted", "weak body", "weakness", "run down", "drained", "burnout", "burn out",
                                      "endurance", "vitality", "tonic", "tonics", "recovery after illness", "convalescence", "sleepy all day", "always tired", "feel weak"],
     ["immunity-energy"], ["cordyceps-cs-4", "american-ginseng", "korean-red-ginseng", "deer-antler", "lingzhi-cracked-spores"], ["energy", "stamina", "fatigue", "vitality"], ""),
    ("sleep", "sleep", ["sleep", "insomnia", "cant sleep", "cannot sleep", "trouble sleeping", "sleepless", "sleep problem", "sleep problems", "poor sleep", "difficulty sleeping", "wake up at night", "waking up at night", "restless sleep",
                        "sleeping pill", "sleeping pills", "sleep aid", "help me sleep", "no sleep", "sleep better", "bedtime", "night sleep", "falling asleep", "fall asleep", "restful sleep"],
     ["stress-sleep"], ["melatonin-5mg", "sleep-aid-melatonin-10mg", "sleep-fast-melatonin-gummies", "magnesium-glycinate", "lingzhi-cracked-spores"], ["sleep", "insomnia"], "If sleeplessness continues for weeks, please see a doctor."),
    ("jet-lag", "jet lag and shift work", ["jet lag", "jetlag", "shift work", "night shift", "flight", "long flight", "time zone", "timezone", "body clock", "circadian", "shift worker"],
     ["stress-sleep"], ["sleep-aid-melatonin-10mg", "melatonin-5mg"], ["jet lag", "shift"], ""),
    ("stress", "stress and calm", ["stress", "stressed", "anxiety", "anxious", "relax", "relaxation", "calm", "nervous", "tension", "worried", "overwhelmed", "restless", "irritable", "cope with stress", "mental stress", "work stress", "unwind"],
     ["stress-sleep"], ["magnesium-glycinate", "american-ginseng", "pearl-powder", "lingzhi-cracked-spores", "melatonin-5mg"], ["stress", "calm", "nerve", "relax"], ""),
    ("kids", "kids' vitamins", ["kids vitamins", "kid vitamins", "children vitamins", "kids vitamin", "child vitamin", "kids supplements", "kids supplement", "vitamins for kids", "vitamins for children", "picky eater", "picky eaters", "fussy eater",
                                "growing child", "growth", "child", "children", "kids", "kid", "toddler", "toddlers", "school child", "my son", "my daughter", "gummies for kids", "baby vitamins", "teenager", "teen"],
     ["kids"], ["zoo-vite-multivitamin-gummies", "zoo-vite-elderberry-gummies", "zoo-vite-immune-jelly", "zoo-vite-dha-jelly", "zoo-vite-lutein-jelly"], ["growth", "immune"], ""),
    ("kids-immunity", "kids' immunity", ["kids immunity", "children immunity", "child immunity", "kids immune", "kids cold", "kids always sick", "kids fall sick", "child falls sick"],
     ["kids"], ["zoo-vite-immune-jelly", "zoo-vite-elderberry-gummies", "zoo-vite-multivitamin-gummies"], ["immun"], ""),
    ("kids-brain-eyes", "kids' eyes and brain", ["kids eyes", "kids vision", "child eyes", "kids brain", "kids focus", "kids memory", "child brain", "kids concentration", "kids learning", "kids dha", "children dha", "screen time kids", "kids study"],
     ["kids", "alertness-memory-vision"], ["zoo-vite-dha-jelly", "zoo-vite-lutein-jelly", "dha-600"], ["brain", "vision", "eye", "learning"], ""),
    ("eyes", "eye health", ["eyes", "eye", "eye strain", "tired eyes", "dry eyes", "vision", "blurry", "blurred vision", "screen time", "computer eyes", "sore eyes", "red eyes", "night vision", "eyesight", "eye fatigue", "eye health", "bad eyesight", "digital eye strain"],
     ["alertness-memory-vision"], ["clear-eyes-plus", "algaomega", "max-omega", "dha-600", "zoo-vite-lutein-jelly"], ["eye", "vision"], ""),
    ("memory", "memory and focus", ["memory", "forgetful", "forgetting", "brain", "brain health", "focus", "concentration", "concentrate", "alertness", "alert", "cognitive", "mental alertness", "brain fog", "exam", "clarity"],
     ["alertness-memory-vision"], ["neuro-gard", "algaomega", "dha-600", "max-omega", "american-ginseng"], ["memory", "alert", "cognitive", "brain"], ""),
    ("bones", "bones and calcium", ["bones", "bone", "calcium", "osteoporosis", "strong bones", "bone health", "teeth", "weak bones", "brittle bones", "bone density", "osteopenia", "vitamin d deficiency"],
     ["bones-joints"], ["maxi-cal", "vitamin-d3-k2", "deer-antler"], ["bone", "calcium"], ""),
    ("liver", "liver health", ["liver", "liver health", "detox", "detoxify", "detoxification", "cleanse", "liver detox", "fatty liver", "alcohol", "drinking", "hangover", "liver support", "liver care"],
     ["heart-liver-vitality"], ["liver-gard-forte", "deep-sea-squalene", "lingzhi-cracked-spores"], ["liver"], "For liver conditions, please see a doctor."),
    ("urinary", "urinary health", ["urinary", "bladder", "uti", "urine", "kidney", "kidneys", "frequent urination", "painful urination", "pee often", "peeing", "urinary tract", "urinary infection", "bladder control", "cystitis", "gout uric acid"],
     ["heart-liver-vitality"], ["uri-gard", "deep-sea-squalene"], ["urinary", "bladder", "kidney"], "For a suspected urinary infection, please see a doctor."),
    ("men", "men's health", ["men", "mens", "male", "men vitality", "mens vitality", "mens health", "libido", "prostate", "virility", "male vitality", "husband", "boyfriend", "sex drive", "stamina men", "testosterone"],
     ["heart-liver-vitality"], ["libi-max", "cordyceps-cs-4", "deer-antler"], ["prostate", "vitality", "stamina", "energy"], ""),
    ("women", "women's health", ["women", "womens", "female", "menopause", "menopausal", "menstrual", "period", "periods", "period cramps", "menstrual cramps", "pms", "hormonal", "hormones", "ladies", "wife", "girlfriend", "irregular period", "hot flashes",
                                 "women health", "womens health", "for women"],
     ["heart-liver-vitality"], ["womens-choice", "safflower-red-flower-oil"], ["menstrua", "hormon", "energy"], ""),
    ("hair", "hair", ["hair", "hair loss", "hair fall", "hair thinning", "thinning hair", "balding", "bald", "grey hair", "gray hair", "white hair", "hair growth", "hair care", "receding", "hair health", "falling hair", "dandruff"],
     ["beauty-wellness"], ["shou-wu-hair-plus"], ["hair"], ""),
    ("skin", "skin and beauty", ["skin", "complexion", "glowing skin", "dull skin", "fair skin", "whitening", "pigmentation", "dark spots", "wrinkles", "fine lines", "anti aging", "anti ageing", "ageing", "aging", "youthful", "beauty", "collagen",
                                 "radiant", "skincare", "skin care", "acne scars", "stretch marks", "scars", "uneven skin tone", "elasticity"],
     ["beauty-wellness"], ["pearl-powder", "age-defying-nmn", "crocodile-pure-skin-oil", "deep-sea-squalene", "c-rosehips"], ["skin", "complexion", "youthful", "elastic"], ""),
    ("skin-irritation", "dry, itchy or damaged skin", ["dry skin", "itchy skin", "eczema", "psoriasis", "rash", "sunburn", "sun burn", "cuts", "scald", "scalds", "chilblains", "athletes foot", "athlete's foot", "fungal", "cracked skin", "dry itchy", "skin allergy", "skin allergies"],
     ["beauty-wellness"], ["crocodile-pure-skin-oil", "deep-sea-squalene"], ["skin", "itchy", "allerg"], "For a skin condition that is spreading or not improving, please see a doctor."),
    ("heart", "heart, cholesterol and circulation", ["heart", "heart health", "cholesterol", "blood pressure", "circulation", "blood circulation", "triglycerides", "cardiovascular", "high cholesterol", "healthy heart", "poor circulation", "cold hands", "numbness"],
     ["alertness-memory-vision", "heart-liver-vitality", "beauty-wellness"], ["deep-sea-squalene", "algaomega", "max-omega", "fish-oil-minigels", "dha-600"], ["heart", "cholesterol", "blood", "triglycer"], "For high blood pressure or cholesterol, please follow your doctor's advice."),
    ("digestion", "digestion and gut health", ["digestion", "digestive", "bloating", "bloated", "constipation", "constipated", "gut", "gut health", "indigestion", "diarrhoea", "diarrhea", "loose stool", "stomach", "stomach ache", "stomachache", "stomach pain",
                                              "tummy ache", "gas", "flatulence", "upset stomach", "probiotics", "bowel", "irregular bowel"],
     ["immunity-allergy", "traditional-pain-relief"], ["synbioten", "qian-li-zhui-feng-oil", "safflower-red-flower-oil"], ["bloating", "stomach", "flatulence", "digest", "constipation"], "If stomach pain is severe or lasts more than a day or two, please see a doctor."),
    ("omega", "omega-3 and fish oil", ["omega 3", "omega3", "fish oil", "fish oils", "epa", "dha", "omega", "algae oil", "essential fatty acids"],
     ["alertness-memory-vision"], ["max-omega", "fish-oil-minigels", "algaomega", "dha-600"], ["omega", "dha", "epa"], ""),
    ("multivitamin", "daily multivitamins", ["multivitamin", "multivitamins", "multi vitamin", "daily vitamins", "daily vitamin", "general health", "all round", "overall health", "everyday health", "nutrition", "nutritional", "vitamins", "vitamin"],
     ["immunity-allergy"], ["therra-m", "boost-immune", "c-rosehips", "zoo-vite-multivitamin-gummies"], ["metabol", "nutrition", "daily"], ""),
    ("diabetic", "sugar-free options", ["diabetic", "diabetes", "sugar free", "sugarfree", "no sugar", "low sugar", "sugar-free", "for diabetics", "high blood sugar", "blood sugar"],
     ["immunity-allergy", "cough-cold-flu"], ["boost-immune", "c-rosehips", "cough-alievaid-herbal-lintus", "ivy-leaf-cough-syrup"], ["diabetic", "sugar"], "Please check with your doctor or pharmacist if you have diabetes."),
    ("travel", "travel", ["travel", "travelling", "traveling", "holiday", "trip", "airport", "overseas trip", "business trip", "pocket", "portable", "on the go", "compact", "carry on", "flight packing"],
     ["pain-relief", "cough-cold-flu"], ["rheuma-salve-balm", "rheuma-salve-medi-stick", "rheuma-salve-liniment", "ivy-leaf-cough-syrup", "sinus-clear-2-in-1"], ["travel", "pocket", "on-the-go", "compact"], ""),
    ("gift", "gifts", ["gift", "gifts", "present", "presents", "gift for parents", "for my parents", "for my mother", "for my father", "for elderly", "for grandparents", "birthday gift", "thoughtful gift", "gift idea", "gift ideas", "corporate gift", "cny"],
     ["traditional-pain-relief", "immunity-energy"], ["safflower-red-flower-oil", "qian-li-zhui-feng-oil", "korean-red-ginseng", "american-ginseng", "cordyceps-cs-4"], ["gift", "energy"], ""),
]

# Health words we recognise but the catalogue does not claim to treat: answer honestly instead of guessing.
UNCOVERED = ["toothache", "tooth ache", "dental", "cancer", "chemo", "covid", "diabetes", "hypertension", "depression", "asthma", "acne", "pimple", "pimples", "hay fever", "hayfever", "allergy", "allergies", "allergic",
             "weight loss", "lose weight", "diet", "slimming", "fat burner", "hangover", "ear ache", "earache", "eczema flare", "piles", "haemorrhoids", "hemorrhoids", "thyroid", "anaemia", "anemia", "ulcer", "acid reflux", "heartburn",
             "gastric", "cataract", "glaucoma", "tinnitus", "hearing", "arthritis medication", "antibiotic", "antibiotics", "steroid", "vaccine", "pregnancy test", "fertility", "ivf", "bp medicine", "insulin", "dialysis"]

# ---------------------------------------------------------------- area gazetteer (approximate centroids, used only to rank "closest listed store")
AREAS = {
    "ang mo kio": (1.3700, 103.8490), "amk": (1.3700, 103.8490), "bedok": (1.3236, 103.9273), "bishan": (1.3508, 103.8485), "boon lay": (1.3388, 103.7058), "bukit batok": (1.3590, 103.7637),
    "bukit merah": (1.2819, 103.8239), "bukit panjang": (1.3784, 103.7625), "bukit timah": (1.3294, 103.8021), "buona vista": (1.3073, 103.7900), "changi": (1.3640, 103.9915),
    "chinatown": (1.2842, 103.8441), "choa chu kang": (1.3854, 103.7443), "cck": (1.3854, 103.7443), "clementi": (1.3151, 103.7650), "dhoby ghaut": (1.2993, 103.8455), "eunos": (1.3198, 103.9034),
    "geylang": (1.3201, 103.8918), "harbourfront": (1.2653, 103.8220), "harbour front": (1.2653, 103.8220), "holland village": (1.3112, 103.7959), "hougang": (1.3712, 103.8924),
    "jurong east": (1.3330, 103.7422), "jurong west": (1.3404, 103.7090), "jurong": (1.3365, 103.7256), "kallang": (1.3115, 103.8714), "lavender": (1.3074, 103.8631), "little india": (1.3067, 103.8518),
    "marine parade": (1.3025, 103.9060), "marina bay": (1.2817, 103.8636), "marina": (1.2817, 103.8636), "novena": (1.3204, 103.8438), "orchard": (1.3040, 103.8318), "paya lebar": (1.3177, 103.8926),
    "pasir ris": (1.3731, 103.9494), "punggol": (1.4043, 103.9021), "queenstown": (1.2942, 103.8061), "raffles place": (1.2840, 103.8514), "redhill": (1.2897, 103.8168), "sembawang": (1.4491, 103.8185),
    "sengkang": (1.3917, 103.8954), "serangoon": (1.3500, 103.8730), "tampines": (1.3540, 103.9436), "tanjong pagar": (1.2764, 103.8458), "tiong bahru": (1.2860, 103.8270), "toa payoh": (1.3326, 103.8474),
    "woodlands": (1.4370, 103.7865), "yishun": (1.4294, 103.8350), "bugis": (1.3009, 103.8559), "somerset": (1.3006, 103.8390), "newton": (1.3127, 103.8383), "farrer park": (1.3123, 103.8545),
    "tai seng": (1.3359, 103.8878), "ubi": (1.3300, 103.8995), "macpherson": (1.3267, 103.8900), "kembangan": (1.3209, 103.9129), "simei": (1.3434, 103.9532), "bukit gombak": (1.3589, 103.7518),
    "pioneer": (1.3376, 103.6975), "tuas": (1.3294, 103.6494), "kranji": (1.4252, 103.7620), "admiralty": (1.4406, 103.8010), "canberra": (1.4430, 103.8297), "khatib": (1.4174, 103.8329),
    "yio chu kang": (1.3818, 103.8449), "braddell": (1.3405, 103.8468), "botanic gardens": (1.3224, 103.8154), "dover": (1.3114, 103.7786), "commonwealth": (1.3025, 103.7983), "tanah merah": (1.3274, 103.9464),
    "expo": (1.3350, 103.9615), "bayfront": (1.2815, 103.8590), "esplanade": (1.2935, 103.8555), "city hall": (1.2931, 103.8520), "outram": (1.2803, 103.8397), "clarke quay": (1.2886, 103.8465),
    "bras basah": (1.2970, 103.8505), "telok blangah": (1.2706, 103.8097), "sentosa": (1.2494, 103.8303), "kent ridge": (1.2935, 103.7845), "one north": (1.2993, 103.7872), "airport": (1.3590, 103.9890),
    "lakeside": (1.3445, 103.7208), "chinese garden": (1.3425, 103.7324), "bukit timah plaza": (1.3405, 103.7760),
    "thomson": (1.3260, 103.8310), "upper thomson": (1.3540, 103.8330), "mountbatten": (1.3062, 103.8825), "dakota": (1.3081, 103.8882), "aljunied": (1.3165, 103.8830), "potong pasir": (1.3312, 103.8689),
    "woodleigh": (1.3394, 103.8708), "boon keng": (1.3196, 103.8617), "jalan besar": (1.3054, 103.8555), "rochor": (1.3037, 103.8527), "katong": (1.3053, 103.9050), "east coast": (1.3045, 103.9300),
    "changi airport": (1.3590, 103.9890), "jewel": (1.3600, 103.9894), "city": (1.2930, 103.8520), "downtown": (1.2793, 103.8530), "central": (1.2930, 103.8520), "west": (1.3365, 103.7256),
    "north": (1.4294, 103.8350), "east": (1.3236, 103.9273), "south": (1.2653, 103.8220), "north east": (1.3712, 103.8924), "northeast": (1.3712, 103.8924), "north west": (1.4370, 103.7865), "northwest": (1.4370, 103.7865),
}
STORE_LL = {  # approximate mall / polyclinic locations
    "Changi Airport T1": (1.3598, 103.9890), "Changi Airport T2": (1.3542, 103.9886), "Changi Airport T3": (1.3571, 103.9886), "Jewel Changi Airport": (1.3600, 103.9894),
    "Causeway Point": (1.4361, 103.7862), "IMM": (1.3352, 103.7448), "ION Orchard": (1.3040, 103.8318), "Jurong Point": (1.3395, 103.7068), "Marina Bay Sands": (1.2834, 103.8607),
    "Takashimaya Shopping Centre": (1.3022, 103.8355), "Ngee Ann City": (1.3022, 103.8355), "Northpoint": (1.4295, 103.8359), "Paragon": (1.3036, 103.8356), "Parkway Parade": (1.3013, 103.9052),
    "NEX": (1.3508, 103.8725), "VivoCity": (1.2644, 103.8222), "Raffles City": (1.2936, 103.8530), "People's Park Centre": (1.2847, 103.8438),
    "Ang Mo Kio Polyclinic": (1.3700, 103.8490), "Hougang Polyclinic": (1.3727, 103.8923), "Kallang Polyclinic": (1.3125, 103.8655), "Sembawang Polyclinic": (1.4435, 103.8277),
    "Toa Payoh Polyclinic": (1.3374, 103.8545), "Woodlands Polyclinic": (1.4357, 103.7865), "Yishun Polyclinic": (1.4290, 103.8376),
}
CHAIN_WORDS = {  # words a shopper uses for each stockist
    "guardian": ["guardian", "guardians"], "watsons": ["watsons", "watson", "watsons pharmacy"], "nhgp": ["nhgp", "nhg", "polyclinic", "polyclinics", "nhg pharmacy", "nhgp pharmacies", "polyclinic pharmacy"],
    "essentials": ["essentials", "essentials pharmacy", "essential pharmacy", "peoples park"], "fairprice": ["fairprice", "fair price", "ntuc", "ntuc fairprice", "fairprice online"],
}

# ---------------------------------------------------------------- page text extraction (the built About / Brands / Trade / Contact / Privacy pages)
class _Text(HTMLParser):
    """Collects the readable paragraphs inside <main> (heading, text), skipping scripts, nav, forms, svg, hidden bits."""
    SKIP = {"script", "style", "svg", "nav", "button", "form", "select", "textarea", "noscript", "iframe", "figure", "template"}
    VOID = {"br", "img", "input", "hr", "meta", "link", "source", "wbr", "area", "col"}
    PARA = {"p", "li", "dd", "address", "blockquote", "summary", "h1", "h2", "h3", "dt"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.stack = []  # (tag, skips)
        self.head = ""
        self.buf = []
        self.hbuf = None
        self.items = []  # (heading, text)

    def _skipping(self):
        return any(sk for _t, sk in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.in_main = True
        if not self.in_main or tag in self.VOID:
            return
        cls = a.get("class") or ""
        sk = tag in self.SKIP or a.get("aria-hidden") == "true" or "sr-only" in cls or "hidden" in a
        self.stack.append((tag, sk))
        if sk:
            return
        if tag in self.PARA:
            self.flush()
        if tag in ("h1", "h2", "h3"):
            self.hbuf = []

    def handle_endtag(self, tag):
        if not self.in_main or tag in self.VOID:
            return
        while self.stack:
            t, _sk = self.stack.pop()
            if t == tag:
                break
        if tag in ("h1", "h2", "h3") and self.hbuf is not None:
            self.head = re.sub(r"\s+", " ", "".join(self.hbuf)).strip()
            self.hbuf = None
        elif tag in self.PARA:
            self.flush()
        if tag == "main":
            self.flush()
            self.in_main = False

    def handle_data(self, data):
        if not self.in_main or self._skipping():
            return
        if self.hbuf is not None:
            self.hbuf.append(data)
        else:
            self.buf.append(data)

    def flush(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if len(t) >= 24:
            self.items.append((self.head, t))


def page_chunks(path, title, url):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return []
    p = _Text()
    p.feed(src)
    out, cur_h, cur_t = [], None, ""
    for h, t in p.items:
        if t.lower().startswith(("prototype", "placeholder")) or "prototype:" in t.lower()[:24]:
            continue
        if h != cur_h or len(cur_t) + len(t) > 420:
            if cur_t:
                out.append({"t": title, "s": cur_h or "", "x": clip(cur_t, 460), "u": url})
            cur_h, cur_t = h, t
        else:
            cur_t += " " + t
    if cur_t:
        out.append({"t": title, "s": cur_h or "", "x": clip(cur_t, 460), "u": url})
    return out


# ---------------------------------------------------------------- the build
def _tidy_dash(s):
    return str(s).replace("—", " - ").replace("–", "-")


def _split_ben(prod):
    """Benefits and indications as the catalogue prints them: the sheet's list runs "benefit INDICATIONS indication ..."."""
    ben, ind, in_ind = [], [], False
    for b in prod.get("benefits") or []:
        b = b.strip()
        if b.endswith("INDICATIONS"):
            b = b[: -len("INDICATIONS")].strip()
            (ind if in_ind else ben).append(b)
            in_ind = True
            continue
        (ind if in_ind else ben).append(b)
    return [x for x in ben if x], [x for x in ind if x]


def _cap(s):
    s = s.strip().rstrip(".;,")
    return s[:1].upper() + s[1:]


def _why(prod, keys):
    """The catalogue's own words for why this product fits a need, never composed here: the 'For:' line or a short
    benefit/indication/usage/description clause that mentions one of the need's words (priority: the need's first
    word first), else the 'For:' line."""
    ben, ind = _split_ben(prod)
    sents = [x.strip() for x in re.split(r"(?<=[.;])\s+", prod.get("description") or "") if x.strip()]
    usage = [x.strip() for u in (prod.get("usage") or []) for x in re.split(r"(?<=[.])\s+", u) if x.strip()]
    labels = ["Pack sizes include the " + v["label"] for v in prod.get("variants") or []]
    clauses = [c.strip() for x in sents for c in re.split(r",\s+|;\s+|\s+and\s+(?=relie|reduc|eas|support)", x) if 8 < len(c.strip()) < 80]
    tag = prod.get("tagline") or ""
    tag = "" if (tag[:1].islower() or tag.lower().startswith(("from ", "and ", "for ", "with "))) else tag  # catalogue fragments such as "and Immunity"
    tiers = [[prod.get("for") or ""], [tag], ben, ind, labels, usage, sents, clauses]
    for ti, tier in enumerate(tiers):
        for k in keys:
            k = k.lower()
            for line in tier:
                line = re.sub(r"^(and|or)\s+", "", re.sub(r"^[A-Za-z ]{3,24}:\s+", "", line)).strip()
                if not line or line.endswith(":") or line.isupper() or k not in line.lower():
                    continue
                if len(line) > (150 if ti == 0 else 118):
                    continue
                return clip(_cap(line), 112)
    return clip(prod.get("for") or prod.get("tagline") or "", 112)


def _site_caution(cat):
    if cat in ("pain-relief", "traditional-pain-relief"):
        return "External use only. Not for broken skin; ask a pharmacist before use in pregnancy or for young children."
    return "A health supplement or herbal remedy, not a substitute for medical care. Ask a pharmacist if symptoms persist."


def _cautions(p):
    """Cautions as the catalogue words them: the site's shelf caution plus caution sentences found in the usage text."""
    out = [_site_caution(p["category"])]
    for u in p.get("usage") or []:
        for s in re.split(r"(?<=[.)])\s+(?=[A-Z])", u):
            s2 = re.sub(r"^(How To Use|Caution|Storage):\s*", "", s).strip()
            if re.search(r"caution|do not|not to be|avoid|consult|refrigerate|single person|pregnan|breast|under 2|below 4|children", s, re.I) and 8 < len(s2) < 240:
                if re.match(r"^(Adults?|Children|Above|Below|\d)", s2) and not re.search(r"caution|do not|not to be|avoid|consult|refrigerate|pregnan", s2, re.I):
                    continue
                if s2 not in out:
                    out.append(s2.rstrip(".") + ".")
    return out[:4]


def _diet(p):
    """Diet-relevant sentences exactly as the catalogue states them (vegan, vegetarian, gelatin, sugar-free ...)."""
    txt = " ".join([p.get("description") or ""] + list(p.get("benefits") or []) + list(p.get("usage") or []))
    out = []
    for s in re.split(r"(?<=[.])\s+", txt):
        if re.search(r"vegan|vegetarian|gelatin|gluten|sugar-free|sugar free|alcohol|halal|artificial", s, re.I) and 10 < len(s) < 330:
            out.append(clip(s.strip(), 230))
    return out[:2]


def _variant_row(v):
    return {"l": v["label"], "p": v["price"] if v["price"] else None, "c": v["code"] or ""}


def build(OUT, BASE, FLIPBOOK, PRODUCTS, CATS, CAT_ORDER, GUIDES, NEEDS, NEED_ICON_FOR, POSTS, ASSURE, ORG, TIMELINE, AWARD_TEXT, brand_label, money):
    flip_base = FLIPBOOK.split("#")[0]
    idx = json.load(open(os.path.join(HERE, "catalogue_index.json"), encoding="utf-8"))
    where = json.load(open(os.path.join(HERE, "where_data.json"), encoding="utf-8"))
    by_slug = {p["slug"]: p for p in PRODUCTS}

    # ---- products
    prods = []
    for p in PRODUCTS:
        s = p["slug"]
        pg = idx["pages"].get(s)
        short = SHORT.get(s) or re.sub(r"\s*\(.*?\)\s*", " ", re.sub(r"[“”\"]", "", fold_keep(p["name"]))).strip()
        halal = s == "alievaid-herbal-drops"  # the only certification the catalogue states (see the build's PDP "Halal (Malaysia)")
        diet = _diet(p)
        rec = {
            "id": s, "n": p["name"], "sn": short, "b": brand_label(p["brand"]), "c": p["category"], "sz": re.sub(r"\s*\(.*\)\s*$", "", p["size"]),
            "f": _tidy_dash(p["for"]).replace(":, ", ": "), "tg": ("" if (p["tagline"][:1].islower() or p["tagline"].lower().startswith(("from ", "and ", "for ", "with "))) else _tidy_dash(p["tagline"])), "d": clip(_tidy_dash(p["description"]), 420),
            "ben": [clip(_tidy_dash(b), 120) for b in _split_ben(p)[0][:6]], "ind": [clip(_tidy_dash(b), 80) for b in _split_ben(p)[1][:8]],
            "use": [clip(_tidy_dash(u), 260) for u in (p.get("usage") or [])[:3]],
            "ing": clip(" ".join(p.get("ingredients") or []), 420), "cau": _cautions(p), "o": p.get("country") or "", "halal": halal, "diet": diet,
            "img": "assets/img/products/%s-thumb.webp" % p["image"], "url": "products/%s/" % s, "pg": pg, "fm": FORMAT.get(s, ""),
            "need": NEEDS.get(s, ""), "v": [_variant_row(v) for v in p["variants"]],
        }
        prods.append(rec)

    # ---- aliases (curated + name n-grams), then drop anything too generic to point at a product
    owners = {}
    def add_alias(slug, phrase):
        k = " ".join(words(phrase))
        if len(k) < 2:
            return
        owners.setdefault(k, set()).add(slug)

    for p in PRODUCTS:
        s = p["slug"]
        toks = words(re.sub(r"\(.*?\)", " ", p["name"]))
        add_alias(s, " ".join(toks))
        for n in range(1, len(toks) + 1):
            for i in range(0, len(toks) - n + 1):
                g = toks[i:i + n]
                if all(t in GENERIC for t in g):
                    continue
                if n == 1:
                    t = g[0]
                    ok = t in SINGLE_OK or (len(t) >= 8 and t not in GENERIC and t not in NEED_ONLY) or (re.search(r"[a-z]", t) and re.search(r"\d", t) and len(t) >= 3 and not re.fullmatch(r"\d+(mg|g|ml|mcg|iu)", t))
                    if not ok:
                        continue
                else:
                    if len(" ".join(g)) < 5 or (g[0] in GENERIC and g[-1] in GENERIC):
                        continue
                add_alias(s, " ".join(g))
        for a in ALIASES.get(s, []):
            add_alias(s, a)
        add_alias(s, SHORT.get(s, p["name"]))
        if p["brand"] == "Heritage":
            add_alias(s, "heritage")
    alias_list = {}
    for k, o in owners.items():
        # a phrase that points at more than 7 products is not a product reference ("oil", "vitamin")
        if len(o) > 7 and k not in ("heritage",):
            continue
        alias_list[k] = sorted(o)
    # weights are computed in the browser from owner counts; ship phrase -> [slugs]

    # ---- needs
    needs = []
    for nid, label, phrases, cats, slugs, keys, note in NEEDS_KB:
        for sl in slugs:
            assert sl in by_slug, (nid, sl)
        needs.append({"id": nid, "l": label, "ph": phrases, "cats": cats, "p": [{"s": sl, "why": _why(by_slug[sl], keys)} for sl in slugs], "note": note})

    # ---- categories
    chap_order = ["pain-relief", "immunity-energy", "beauty-wellness", "traditional-pain-relief", "kids", "cough-cold-flu", "bones-joints", "alertness-memory-vision", "stress-sleep", "immunity-allergy", "heart-liver-vitality"]
    assert len(idx["chapters"]) == len(chap_order)
    chap_by_cat = {cid: ch for cid, ch in zip(chap_order, idx["chapters"])}
    CAT_ALIAS = {
        "pain-relief": ["pain relief", "premium pain relief", "pain", "rheuma salve range", "painkiller", "pain killer", "painkillers", "pain medicine"],
        "cough-cold-flu": ["cough cold flu", "cough and cold", "cold and flu", "cough cold", "cold flu", "flu cold cough", "cold remedies", "cough remedies", "cough range"],
        "traditional-pain-relief": ["traditional pain relief", "medicated oil", "medicated oils", "traditional oil", "traditional oils", "heritage oils", "rheumatic oils", "chinese oil", "oils"],
        "immunity-energy": ["immunity and energy", "immunity energy", "tonics", "tonic range", "herbal tonics", "energy tonics", "ginseng range", "heritage tonics"],
        "beauty-wellness": ["beauty and wellness", "beauty", "wellness", "beauty range", "beauty supplements", "beauty products", "skincare range"],
        "kids": ["kids supplements", "kids range", "kids", "children range", "zoo vite range", "kids products", "childrens vitamins"],
        "bones-joints": ["bones and joints", "bone and joint", "joint range", "bones range", "bone joint"],
        "alertness-memory-vision": ["alertness memory vision", "memory and vision", "brain and eyes", "omega range", "brain range", "eye range"],
        "stress-sleep": ["stress anxiety sleep", "stress and sleep", "sleep range", "sleep products", "sleep supplements", "relaxation range"],
        "immunity-allergy": ["immunity and allergy", "immunity allergy", "vitamin range", "vitamins range", "daily defence range"],
        "heart-liver-vitality": ["heart liver urinary vitality", "heart and liver", "vitality range", "mens and womens health", "organ health"],
    }
    cats = []
    for cid in CAT_ORDER:
        c = CATS[cid]
        ch = chap_by_cat[cid]
        cats.append({"id": cid, "n": c["name"], "b": c["blurb"].replace("�", ""), "url": "shop/%s/" % cid, "pg": ch["page"], "last": ch["last"], "no": ch["no"],
                     "al": CAT_ALIAS.get(cid, []) + [c["name"]], "slugs": [p["slug"] for p in PRODUCTS if p["category"] == cid]})

    # ---- FAQs (the shelf guides) and health notes
    faqs = []
    for cid, g in GUIDES.items():
        for q, a in g["faq"]:
            faqs.append({"q": q, "a": a, "cat": cid, "u": "shop/%s/" % cid})
    posts = []
    chunks = []
    for slug, title, date, summary, body in POSTS:
        posts.append({"slug": slug, "t": title, "x": summary, "u": "blog/%s/" % slug, "d": date})
        for m in re.finditer(r"<h2>(.*?)</h2>(.*?)(?=<h2>|<blockquote>|$)", body, re.S):
            chunks.append({"t": title, "s": plain(m.group(1)), "x": clip(plain(m.group(2)), 460), "u": "blog/%s/" % slug})
        intro = re.split(r"<h2>", body)[0]
        if plain(intro):
            chunks.append({"t": title, "s": "", "x": clip(plain(intro), 460), "u": "blog/%s/" % slug})

    # ---- pages
    pages = [
        {"id": "home", "t": "Home", "u": "", "al": ["home", "homepage", "home page", "front page", "main page", "start page"]},
        {"id": "shop", "t": "All products", "u": "shop/", "al": ["shop", "all products", "store", "products", "everything", "full range", "whole range", "shop page", "online store"]},
        {"id": "where", "t": "Where to buy", "u": "where-to-buy/", "al": ["where to buy", "stores page", "stockists", "store locator", "store finder"]},
        {"id": "resellers", "t": "Trade and resellers", "u": "resellers/", "al": ["trade", "trade page", "resellers", "reseller page", "distributor page", "trade enquiry"]},
        {"id": "about", "t": "About HST Medical", "u": "about/", "al": ["about", "about us", "about page", "our story", "company page"]},
        {"id": "brands", "t": "Our brands", "u": "brands/", "al": ["brands", "our brands", "brand page"]},
        {"id": "blog", "t": "Health notes", "u": "blog/", "al": ["health notes", "blog", "articles", "guides", "reading", "tips"]},
        {"id": "contact", "t": "Contact us", "u": "contact/", "al": ["contact", "contact page", "contact us", "contact form", "enquiry form", "send a message"]},
        {"id": "privacy", "t": "Privacy policy", "u": "privacy/", "al": ["privacy", "privacy policy", "pdpa", "personal data", "data protection", "terms"]},
        {"id": "cart", "t": "Your bag", "u": "cart/", "al": ["bag page", "cart page", "basket page", "my bag page", "bag"]},
        {"id": "checkout", "t": "Checkout", "u": "checkout/", "al": ["checkout page", "payment page"]},
    ]
    for pg in ("about", "brands", "resellers", "contact", "privacy"):
        chunks += page_chunks(os.path.join(OUT, pg, "index.html"), next(x["t"] for x in pages if x["id"] == pg), "%s/" % pg)
    for q in faqs:
        chunks.append({"t": q["q"], "s": "", "x": q["a"], "u": q["u"]})

    # ---- stores
    chains, stores = [], []
    for c in where["chains"]:
        chains.append({"id": c["id"], "n": c["name"], "note": c.get("note") or "", "online": c.get("online") or "", "hotline": c.get("hotline") or "", "hh": c.get("hotline_hours") or "",
                       "hours": c.get("hours") or "", "w": CHAIN_WORDS.get(c["id"], [c["name"].lower()]), "nst": len(c.get("stores") or [])})
        for s in c.get("stores") or []:
            key = re.sub(r"\s*\(.*\)\s*$", "", s["name"]).strip()
            ll = STORE_LL.get(key) or STORE_LL.get(s["name"])
            if not ll:
                key2 = next((k for k in STORE_LL if key.startswith(k) or k.startswith(key)), None)
                ll = STORE_LL.get(key2)
            assert ll, ("no coordinates for", s["name"])
            q = "%s %s, %s" % (c["name"], s["name"], s["address"])
            stores.append({"ch": c["id"], "cn": c["name"], "n": s["name"], "a": s["address"], "t": s.get("tel") or "", "ll": [ll[0], ll[1]], "q": q})
    areas = [{"n": k.strip(), "ll": [v[0], v[1]]} for k, v in AREAS.items() if k == k.strip()]

    # ---- facts: short, sourced, plain
    D = where["delivery"]
    contact = {"phone": where["hq"]["tel"], "ext": where["hq"]["ext"], "email": "contact@hstmedical.com", "order": "order@hstmedical.com", "trade": "resellercontact@hstmedical.com",
               "telegram": "https://t.me/hstmedical", "address": where["hq"]["address"], "uen": "199405743E", "name": "HST Medical Pte Ltd",
               "map": "https://www.google.com/maps/search/?api=1&query=HST+Medical+Pte+Ltd,+152+Paya+Lebar+Road,+Citipoint+Industrial+Complex,+Singapore+409020"}
    facts = {
        "free_above": D["free_above"], "fee": D["fee"], "gst": 9, "max_qty": 20,
        "delivery": "Delivery in Singapore is free on orders above S$30, and S$1.99 on orders of S$30 and below. Prices include 9% GST. The checkout page shows courier delivery in 2 to 3 working days. "
                    "We cannot deliver to P.O. boxes or restricted areas (for example Changi Airport, army camps, checkpoints, Jurong Island and the outlying islands).",
        "overseas": D["overseas"] + " Ask the order desk about your destination before you order.",
        "gst": "All prices are in Singapore dollars and include 9% GST.",
        "payment": "You pay on the secure checkout page, after entering your delivery details. The payment options shown there depend on the store's payment setup (this prototype lists card, PayNow, GrabPay, Apple Pay and Google Pay as examples). Please never type card details into this chat.",
        "order_status": "This prototype does not keep customer orders, so I cannot look up an order here. For an order you placed on hstmedical.com, email the order desk at %s with your order number, or call %s ext. %s." % (contact["order"], contact["phone"], contact["ext"]),
        "returns": "I do not have a returns or refund policy on file. For a damaged parcel, a wrong item or any order problem, email %s with your order number and the team will help." % contact["order"],
        "promo": "I do not have a current promotion on file, and this prototype's bag does not apply discounts. Offers are announced on the HST Medical Telegram channel (t.me/hstmedical); you can also ask the order desk at %s." % contact["order"],
        "genuine": where["fakes_more"],
        "about": "HST Medical Pte Ltd is a Singapore maker and supplier of health supplements and pain relief remedies. It grew from the Heng Say Tong medical hall (1930), was incorporated in 1994 (UEN %s), and has been part of Kowa Pharmaceutical Asia Pte. Ltd. since 29 May 2026. The brands are Rheuma-Salve, Heritage, HST Medical and Zoo-Vite. Higher, Stronger, Together." % contact["uen"],
        "quality": "HST Medical formulates with pharmacists and TCM physicians, manufactures under GMP, verifies the authenticity of ingredients and tests finished products. Alievaid Herbal Drops carry Halal (Malaysia) certification; for any other product, Halal status is not listed in the catalogue, so please check the pack or ask us.",
        "trade": "HST Medical supplies pharmacies, clinics, TCM halls, e-commerce sellers and overseas distributors directly. Email %s or use the trade enquiry form, and a territory manager will be in touch within two working days." % contact["trade"],
        "contact": "Customer service: %s. Orders and delivery: %s. Trade: %s. Phone %s ext. %s. We reply within two working days." % (contact["email"], contact["order"], contact["trade"], contact["phone"], contact["ext"]),
        "pharmacist": "I am an automated assistant, not a pharmacist. For personal advice, call %s ext. %s, email %s, or ask the pharmacist at any pharmacy that stocks HST Medical." % (contact["phone"], contact["ext"], contact["email"]),
        "bot": "I am Ask HST, an automated shop assistant. I am not a person and I am not a pharmacist. I answer only from this website's catalogue and pages, and I can add items to your bag.",
        "privacy": "Data is handled under Singapore's Personal Data Protection Act (PDPA). This chat stores your bag and a few preferences in your own browser only; nothing is sent anywhere. Use the menu to forget what it learned.",
        "awards": "; ".join(AWARD_TEXT.values()),
        "disclaimer": "Information here comes from the product label and catalogue. It is general guidance, not medical advice, and I cannot diagnose. Always read the label and follow the directions for use.",
        "tele": "Offers and news are posted on the HST Medical Telegram channel: t.me/hstmedical.",
        "catalogue": "The product catalogue is a flip-through book of every product sheet: benefits, how to use, ingredients, pack sizes and item codes.",
    }
    brands = [{"id": b[0], "n": b[1], "x": b[2], "u": b[4]} for b in page_about.BRANDS]
    about = {"timeline": [{"y": y, "t": t} for y, t in TIMELINE], "assure": [{"t": t, "x": x} for _k, t, x in ASSURE], "brands": brands}

    kb = {
        "v": 1, "base": BASE, "flipbook": flip_base, "flip_pages": idx["pageCount"],
        "site": {"free_above": D["free_above"], "fee": D["fee"], "gst": 9, "max_qty": 20},
        "facts": facts, "contact": contact, "cats": cats, "products": prods, "alias": alias_list, "spell": SPELL, "needs": needs, "uncovered": UNCOVERED, "faqs": faqs, "posts": posts,
        "pages": pages, "chunks": chunks, "chains": chains, "stores": stores, "areas": areas, "chapters": [{"no": c["no"], "t": c["title"], "pg": c["page"], "last": c["last"]} for c in idx["chapters"]],
        "about": about,
    }
    path = os.path.join(OUT, "assets", "data", "chat-kb.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = json.dumps(kb, ensure_ascii=False, separators=(",", ":"))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    return {"products": len(prods), "aliases": len(alias_list), "needs": len(needs), "stores": len(stores), "chunks": len(chunks), "bytes": len(data.encode("utf-8"))}


def fold_keep(s):
    """Name without the registered mark, keeping case and punctuation."""
    return str(s).replace("®", "").replace("™", "")
