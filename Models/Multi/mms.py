import os
from transformers import AutoProcessor, Wav2Vec2ForCTC

# for language identification
from transformers import Wav2Vec2ForSequenceClassification, AutoFeatureExtractor

from pathlib import Path
import torch
import gc
from Models.TextCorrection import T5

from Models.Singleton import SingletonMeta

model_cache_path = Path(".cache/mms-cache")

LANGUAGES = {
    "abi": "Abidji",
    "abp": "Ayta, Abellen",
    "aca": "Achagua",
    "acd": "Gikyode",
    "ace": "Aceh",
    "acf": "Lesser Antillean French Creole",
    "ach": "Acholi",
    "acn": "Achang",
    "acr": "Achi",
    "acu": "Achuar-Shiwiar",
    "ade": "Adele",
    "adh": "Jopadhola",
    "adj": "Adioukrou",
    "adx": "Tibetan, Amdo",
    "aeu": "Akeu",
    "agd": "Agarabi",
    "agg": "Angor",
    "agn": "Agutaynen",
    "agr": "Awajún",
    "agu": "Awakateko",
    "agx": "Aghul",
    "aha": "Ahanta",
    "ahk": "Akha",
    "aia": "Arosi",
    "aka": "Akan",
    "akb": "Batak Angkola",
    "ake": "Akawaio",
    "akp": "Siwu",
    "alj": "Alangan",
    "alp": "Alune",
    "alt": "Altai, Southern",
    "alz": "Alur",
    "ame": "Yanesha’",
    "amf": "Hamer-Banna",
    "amh": "Amharic",
    "ami": "Amis",
    "amk": "Ambai",
    "ann": "Obolo",
    "any": "Anyin",
    "aoz": "Uab Meto",
    "apb": "Sa’a",
    "apr": "Arop-Lokep",
    "ara": "Arabic",
    "arl": "Arabela",
    "asa": "Asu",
    "asg": "Cishingini",
    "asm": "Assamese",
    "ata": "Pele-Ata",
    "atb": "Zaiwa",
    "atg": "Ivbie North-Okpela-Arhe",
    "ati": "Attié",
    "atq": "Aralle-Tabulahan",
    "ava": "Avar",
    "avn": "Avatime",
    "avu": "Avokaya",
    "awa": "Awadhi",
    "awb": "Awa",
    "ayo": "Ayoreo",
    "ayr": "Aymara, Central",
    "ayz": "Mai Brat",
    "azb": "Azerbaijani, South",
    "azg": "Amuzgo, San Pedro Amuzgos",
    "azj": "Azerbaijani, North",
    "azz": "Nahuatl, Highland Puebla",
    "bak": "Bashkort",
    "bam": "Bamanankan",
    "ban": "Bali",
    "bao": "Waimaha",
    "bav": "Vengo",
    "bba": "Baatonum",
    "bbb": "Barai",
    "bbc": "Batak Toba",
    "bbo": "Konabéré",
    "bcc": "Balochi, Southern",
    "bcl": "Bikol, Central",
    "bcw": "Bana",
    "bdg": "Bonggi",
    "bdh": "Baka",
    "bdq": "Bahnar",
    "bdu": "Oroko",
    "bdv": "Bodo Parja",
    "beh": "Biali",
    "bem": "Bemba",
    "ben": "Bengali",
    "bep": "Behoa",
    "bex": "Jur Modo",
    "bfa": "Bari",
    "bfo": "Birifor, Malba",
    "bfy": "Bagheli",
    "bfz": "Pahari, Mahasu",
    "bgc": "Haryanvi",
    "bgq": "Bagri",
    "bgr": "Chin, Bawm",
    "bgt": "Bughotu",
    "bgw": "Bhatri",
    "bha": "Bharia",
    "bht": "Bhattiyali",
    "bhz": "Bada",
    "bib": "Bisa",
    "bim": "Bimoba",
    "bis": "Bislama",
    "biv": "Birifor, Southern",
    "bjr": "Binumarien",
    "bjv": "Bedjond",
    "bjw": "Bakwé",
    "bjz": "Baruga",
    "bkd": "Binukid",
    "bkv": "Bekwarra",
    "blh": "Kuwaa",
    "blt": "Tai Dam",
    "blx": "Ayta, Mag-Indi",
    "blz": "Balantak",
    "bmq": "Bomu",
    "bmr": "Muinane",
    "bmu": "Somba-Siawari",
    "bmv": "Bum",
    "bng": "Benga",
    "bno": "Bantoanon",
    "bnp": "Bola",
    "boa": "Bora",
    "bod": "Tibetan, Central",
    "boj": "Anjam",
    "bom": "Berom",
    "bor": "Borôro",
    "bov": "Tuwuli",
    "box": "Buamu",
    "bpr": "Blaan, Koronadal",
    "bps": "Blaan, Sarangani",
    "bqc": "Boko",
    "bqi": "Bakhtiâri",
    "bqj": "Bandial",
    "bqp": "Bisã",
    "bru": "Bru, Eastern",
    "bsc": "Oniyan",
    "bsq": "Bassa",
    "bss": "Akoose",
    "btd": "Batak Dairi",
    "bts": "Batak Simalungun",
    "btt": "Bete-Bendi",
    "btx": "Batak Karo",
    "bud": "Ntcham",
    "bul": "Bulgarian",
    "bus": "Bokobaru",
    "bvc": "Baelelea",
    "bvz": "Bauzi",
    "bwq": "Bobo Madaré, Southern",
    "bwu": "Buli",
    "byr": "Yipma",
    "bzh": "Buang, Mapos",
    "bzi": "Bisu",
    "bzj": "Belize English Creole",
    "caa": "Ch’orti’",
    "cab": "Garifuna",
    "cac": "Chuj",
    "cak": "Kaqchikel",
    "cap": "Chipaya",
    "car": "Carib",
    "cas": "Tsimané",
    "cat": "Catalan",
    "cax": "Chiquitano",
    "cbc": "Carapana",
    "cbi": "Chachi",
    "cbr": "Kakataibo-Kashibo",
    "cbs": "Kashinawa",
    "cbt": "Shawi",
    "cbu": "Kandozi-Chapra",
    "cbv": "Cacua",
    "cce": "Chopi",
    "cco": "Chinantec, Comaltepec",
    "cdj": "Churahi",
    "ceb": "Cebuano",
    "ceg": "Chamacoco",
    "cek": "Chin, Eastern Khumi",
    "cfm": "Chin, Falam",
    "cgc": "Kagayanen",
    "che": "Chechen",
    "chf": "Chontal, Tabasco",
    "chv": "Chuvash",
    "chz": "Chinantec, Ozumacín",
    "cjo": "Ashéninka, Pajonal",
    "cjp": "Cabécar",
    "cjs": "Shor",
    "cko": "Anufo",
    "ckt": "Chukchi",
    "cla": "Ron",
    "cle": "Chinantec, Lealao",
    "cly": "Chatino, Eastern Highland",
    "cme": "Cerma",
    "cmo": "Mnong, Central",
    "cmr": "Mro-Khimi",
    "cnh": "Chin, Hakha",
    "cni": "Asháninka",
    "cnl": "Chinantec, Lalana",
    "cnt": "Chinantec, Tepetotutla",
    "coe": "Koreguaje",
    "cof": "Tsafiki",
    "cok": "Cora, Santa Teresa",
    "con": "Cofán",
    "cot": "Caquinte",
    "cou": "Wamey",
    "cpa": "Chinantec, Palantla",
    "cpb": "Ashéninka, Ucayali-Yurúa",
    "cpu": "Ashéninka, Pichis",
    "crh": "Crimean Tatar",
    "crk": "Cree, Plains",
    "crn": "Cora, El Nayar",
    "crq": "Chorote, Iyo’wujwa",
    "crs": "Seychelles French Creole",
    "crt": "Chorote, Iyojwa’ja",
    "csk": "Jola-Kasa",
    "cso": "Chinantec, Sochiapam",
    "ctd": "Chin, Tedim",
    "ctg": "Chittagonian",
    "cto": "Embera Catío",
    "ctu": "Chol",
    "cuc": "Chinantec, Usila",
    "cui": "Cuiba",
    "cuk": "Kuna, San Blas",
    "cul": "Kulina",
    "cwa": "Kabwa",
    "cwe": "Kwere",
    "cwt": "Kuwaataay",
    "cya": "Chatino, Nopala",
    "cym": "Welsh",
    "daa": "Dangaléat",
    "dah": "Gwahatike",
    "dar": "Dargwa",
    "dbj": "Ida’an",
    "dbq": "Daba",
    "ddn": "Dendi",
    "ded": "Dedua",
    "des": "Desano",
    "deu": "German, Standard",
    "dga": "Dagaare, Southern",
    "dgi": "Dagara, Northern",
    "dgk": "Dagba",
    "dgo": "Dogri",
    "dgr": "Tlicho",
    "dhi": "Dhimal",
    "did": "Didinga",
    "dig": "Chidigo",
    "dik": "Dinka, Southwestern",
    "dip": "Dinka, Northeastern",
    "div": "Maldivian",
    "djk": "Aukan",
    "dnj": "Dan",
    "dnt": "Dani, Mid Grand Valley",
    "dnw": "Dani, Western",
    "dop": "Lukpa",
    "dos": "Dogosé",
    "dsh": "Daasanach",
    "dso": "Desiya",
    "dtp": "Kadazan Dusun",
    "dts": "Dogon, Toro So",
    "dug": "Chiduruma",
    "dwr": "Dawro",
    "dyi": "Sénoufo, Djimini",
    "dyo": "Jola-Fonyi",
    "dyu": "Jula",
    "dzo": "Dzongkha",
    "eip": "Lik",
    "eka": "Ekajuk",
    "ell": "Greek",
    "emp": "Emberá, Northern",
    "enb": "Markweeta",
    "eng": "English",
    "enx": "Enxet",
    "ese": "Ese Ejja",
    "ess": "Yupik, Saint Lawrence Island",
    "eus": "Basque",
    "evn": "Evenki",
    "ewe": "Éwé",
    "eza": "Ezaa",
    "fal": "Fali, South",
    "fao": "Faroese",
    "far": "Fataleka",
    "fas": "Persian",
    "fij": "Fijian",
    "fin": "Finnish",
    "flr": "Fuliiru",
    "fmu": "Muria, Far Western",
    "fon": "Fon",
    "fra": "French",
    "frd": "Fordata",
    "ful": "Fulah",
    "gag": "Gagauz",
    "gai": "Mbore",
    "gam": "Kandawo",
    "gau": "Gadaba, Mudhili",
    "gbi": "Galela",
    "gbk": "Gaddi",
    "gbm": "Garhwali",
    "gbo": "Grebo, Northern",
    "gde": "Gude",
    "geb": "Kire",
    "gej": "Gen",
    "gil": "Kiribati",
    "gjn": "Gonja",
    "gkn": "Gokana",
    "gld": "Nanai",
    "glk": "Gilaki",
    "gmv": "Gamo",
    "gna": "Kaansa",
    "gnd": "Zulgo-Gemzek",
    "gng": "Ngangam",
    "gof": "Gofa",
    "gog": "Gogo",
    "gor": "Gorontalo",
    "gqr": "Gor",
    "grc": "Greek, Ancient",
    "gri": "Ghari",
    "grn": "Guarani",
    "grt": "Garo",
    "gso": "Gbaya, Southwest",
    "gub": "Guajajára",
    "guc": "Wayuu",
    "gud": "Dida, Yocoboué",
    "guh": "Guahibo",
    "guj": "Gujarati",
    "guk": "Gumuz",
    "gum": "Misak",
    "guo": "Guayabero",
    "guq": "Aché",
    "guu": "Yanomamö",
    "gux": "Gourmanchéma",
    "gvc": "Wanano",
    "gvl": "Gulay",
    "gwi": "Gwich’in",
    "gwr": "Gwere",
    "gym": "Ngäbere",
    "gyr": "Guarayu",
    "had": "Hatam",
    "hag": "Hanga",
    "hak": "Chinese, Hakka",
    "hap": "Hupla",
    "hat": "Haitian Creole",
    "hau": "Hausa",
    "hay": "Haya",
    "heb": "Hebrew",
    "heh": "Hehe",
    "hif": "Hindi, Fiji",
    "hig": "Kamwe",
    "hil": "Hiligaynon",
    "hin": "Hindi",
    "hlb": "Halbi",
    "hlt": "Chin, Matu",
    "hne": "Chhattisgarhi",
    "hnn": "Hanunoo",
    "hns": "Hindustani, Sarnami",
    "hoc": "Ho",
    "hoy": "Holiya",
    "hto": "Witoto, Minika",
    "hub": "Wampís",
    "hui": "Huli",
    "hun": "Hungarian",
    "hus": "Huastec",
    "huu": "Witoto, Murui",
    "huv": "Huave, San Mateo del Mar",
    "hvn": "Hawu",
    "hwc": "Hawaii Pidgin",
    "hyw": "Armenian, Western",
    "iba": "Iban",
    "icr": "Islander English Creole",
    "idd": "Ede Idaca",
    "ifa": "Ifugao, Amganad",
    "ifb": "Ifugao, Batad",
    "ife": "Ifè",
    "ifk": "Ifugao, Tuwali",
    "ifu": "Ifugao, Mayoyao",
    "ify": "Kallahan, Keley-i",
    "ign": "Ignaciano",
    "ikk": "Ika",
    "ilb": "Ila",
    "ilo": "Ilocano",
    "imo": "Imbongu",
    "inb": "Inga",
    "ind": "Indonesian",
    "iou": "Tuma-Irumu",
    "ipi": "Ipili",
    "iqw": "Ikwo",
    "iri": "Rigwe",
    "irk": "Iraqw",
    "isl": "Icelandic",
    "itl": "Itelmen",
    "itv": "Itawit",
    "ixl": "Ixil",
    "izr": "Izere",
    "izz": "Izii",
    "jac": "Jakalteko",
    "jam": "Jamaican English Creole",
    "jav": "Javanese",
    "jbu": "Jukun Takum",
    "jen": "Dza",
    "jic": "Tol",
    "jiv": "Shuar",
    "jmc": "Machame",
    "jmd": "Yamdena",
    "jun": "Juang",
    "juy": "Juray",
    "jvn": "Javanese, Suriname",
    "kaa": "Karakalpak",
    "kab": "Amazigh",
    "kac": "Jingpho",
    "kak": "Kalanguya",
    "kan": "Kannada",
    "kao": "Xaasongaxango",
    "kaq": "Capanahua",
    "kay": "Kamayurá",
    "kaz": "Kazakh",
    "kbo": "Keliko",
    "kbp": "Kabiyè",
    "kbq": "Kamano",
    "kbr": "Kafa",
    "kby": "Kanuri, Manga",
    "kca": "Khanty",
    "kcg": "Tyap",
    "kdc": "Kutu",
    "kde": "Makonde",
    "kdh": "Tem",
    "kdi": "Kumam",
    "kdj": "Ng’akarimojong",
    "kdl": "Tsikimba",
    "kdn": "Kunda",
    "kdt": "Kuay",
    "kek": "Q’eqchi’",
    "ken": "Kenyang",
    "keo": "Kakwa",
    "ker": "Kera",
    "key": "Kupia",
    "kez": "Kukele",
    "kfb": "Kolami, Northwestern",
    "kff": "Koya",
    "kfw": "Naga, Kharam",
    "kfx": "Pahari, Kullu",
    "khg": "Tibetan, Khams",
    "khm": "Khmer",
    "khq": "Songhay, Koyra Chiini",
    "kia": "Kim",
    "kij": "Kilivila",
    "kik": "Gikuyu",
    "kin": "Kinyarwanda",
    "kir": "Kyrgyz",
    "kjb": "Q’anjob’al",
    "kje": "Kisar",
    "kjg": "Khmu",
    "kjh": "Khakas",
    "kki": "Kagulu",
    "kkj": "Kako",
    "kle": "Kulung",
    "klu": "Klao",
    "klv": "Maskelynes",
    "klw": "Tado",
    "kma": "Konni",
    "kmd": "Kalinga, Majukayang",
    "kml": "Kalinga, Tanudan",
    "kmr": "Kurdish, Northern",
    "kmu": "Kanite",
    "knb": "Kalinga, Lubuagan",
    "kne": "Kankanaey",
    "knf": "Mankanya",
    "knj": "Akateko",
    "knk": "Kuranko",
    "kno": "Kono",
    "kog": "Kogi",
    "kor": "Korean",
    "kpq": "Korupun-Sela",
    "kps": "Tehit",
    "kpv": "Komi-Zyrian",
    "kpy": "Koryak",
    "kpz": "Kupsapiiny",
    "kqe": "Kalagan",
    "kqp": "Kimré",
    "kqr": "Kimaragang",
    "kqy": "Koorete",
    "krc": "Karachay-Balkar",
    "kri": "Krio",
    "krj": "Kinaray-a",
    "krl": "Karelian",
    "krr": "Krung",
    "krs": "Gbaya",
    "kru": "Kurux",
    "ksb": "Shambala",
    "ksr": "Borong",
    "kss": "Kisi, Southern",
    "ktb": "Kambaata",
    "ktj": "Krumen, Plapo",
    "kub": "Kutep",
    "kue": "Kuman",
    "kum": "Kumyk",
    "kus": "Kusaal",
    "kvn": "Kuna, Border",
    "kvw": "Wersing",
    "kwd": "Kwaio",
    "kwf": "Kwara’ae",
    "kwi": "Awa-Cuaiquer",
    "kxc": "Konso",
    "kxf": "Kawyaw",
    "kxm": "Khmer, Northern",
    "kxv": "Kuvi",
    "kyb": "Kalinga, Butbut",
    "kyc": "Kyaka",
    "kyf": "Kouya",
    "kyg": "Keyagana",
    "kyo": "Klon",
    "kyq": "Kenga",
    "kyu": "Kayah, Western",
    "kyz": "Kayabí",
    "kzf": "Kaili, Da’a",
    "lac": "Lacandon",
    "laj": "Lango",
    "lam": "Lamba",
    "lao": "Lao",
    "las": "Lama",
    "lat": "Latin",
    "lav": "Latvian",
    "law": "Lauje",
    "lbj": "Ladakhi",
    "lbw": "Tolaki",
    "lcp": "Lawa, Western",
    "lee": "Lyélé",
    "lef": "Lelemi",
    "lem": "Nomaande",
    "lew": "Kaili, Ledo",
    "lex": "Luang",
    "lgg": "Lugbara",
    "lgl": "Wala",
    "lhu": "Lahu",
    "lia": "Limba, West-Central",
    "lid": "Nyindrou",
    "lif": "Limbu",
    "lip": "Sekpele",
    "lis": "Lisu",
    "lje": "Rampi",
    "ljp": "Lampung Api",
    "llg": "Lole",
    "lln": "Lele",
    "lme": "Pévé",
    "lnd": "Lundayeh",
    "lns": "Lamnso’",
    "lob": "Lobi",
    "lok": "Loko",
    "lom": "Loma",
    "lon": "Lomwe, Malawi",
    "loq": "Lobala",
    "lsi": "Lacid",
    "lsm": "Saamya-Gwe",
    "luc": "Aringa",
    "lug": "Ganda",
    "lwo": "Luwo",
    "lww": "Lewo",
    "lzz": "Laz",
    "maa": "Mazatec, San Jerónimo Tecóatl",
    "mad": "Madura",
    "mag": "Magahi",
    "mah": "Marshallese",
    "mai": "Maithili",
    "maj": "Mazatec, Jalapa de Díaz",
    "mak": "Makasar",
    "mal": "Malayalam",
    "mam": "Mam",
    "maq": "Mazatec, Chiquihuitlán",
    "mar": "Marathi",
    "maw": "Mampruli",
    "maz": "Mazahua, Central",
    "mbb": "Manobo, Western Bukidnon",
    "mbc": "Macushi",
    "mbh": "Mangseng",
    "mbj": "Nadëb",
    "mbt": "Manobo, Matigsalug",
    "mbu": "Mbula-Bwazza",
    "mbz": "Mixtec, Amoltepec",
    "mca": "Maka",
    "mcb": "Matsigenka",
    "mcd": "Sharanahua",
    "mco": "Mixe, Coatlán",
    "mcp": "Makaa",
    "mcq": "Ese",
    "mcu": "Mambila, Cameroon",
    "mda": "Mada",
    "mdv": "Mixtec, Santa Lucía Monteverde",
    "mdy": "Male",
    "med": "Melpa",
    "mee": "Mengen",
    "mej": "Meyah",
    "men": "Mende",
    "meq": "Merey",
    "met": "Mato",
    "mev": "Maan",
    "mfe": "Morisyen",
    "mfh": "Matal",
    "mfi": "Wandala",
    "mfk": "Mofu, North",
    "mfq": "Moba",
    "mfy": "Mayo",
    "mfz": "Mabaan",
    "mgd": "Moru",
    "mge": "Mango",
    "mgh": "Makhuwa-Meetto",
    "mgo": "Meta’",
    "mhi": "Ma’di",
    "mhr": "Mari, Meadow",
    "mhu": "Digaro-Mishmi",
    "mhx": "Lhao Vo",
    "mhy": "Ma’anyan",
    "mib": "Mixtec, Atatlahuca",
    "mie": "Mixtec, Ocotepec",
    "mif": "Mofu-Gudur",
    "mih": "Mixtec, Chayuco",
    "mil": "Mixtec, Peñoles",
    "mim": "Mixtec, Alacatlatzala",
    "min": "Minangkabau",
    "mio": "Mixtec, Pinotepa Nacional",
    "mip": "Mixtec, Apasco-Apoala",
    "miq": "Mískito",
    "mit": "Mixtec, Southern Puebla",
    "miy": "Mixtec, Ayutla",
    "miz": "Mixtec, Coatzospan",
    "mjl": "Mandeali",
    "mjv": "Mannan",
    "mkl": "Mokole",
    "mkn": "Malay, Kupang",
    "mlg": "Malagasy",
    "mmg": "Ambrym, North",
    "mnb": "Muna",
    "mnf": "Mundani",
    "mnk": "Mandinka",
    "mnw": "Mon",
    "mnx": "Sougb",
    "moa": "Mwan",
    "mog": "Mongondow",
    "mon": "Mongolian",
    "mop": "Maya, Mopán",
    "mor": "Moro",
    "mos": "Mòoré",
    "mox": "Molima",
    "moz": "Mukulu",
    "mpg": "Marba",
    "mpm": "Mixtec, Yosondúa",
    "mpp": "Migabac",
    "mpx": "Misima-Panaeati",
    "mqb": "Mbuko",
    "mqf": "Momuna",
    "mqj": "Mamasa",
    "mqn": "Moronene",
    "mrw": "Maranao",
    "msy": "Aruamu",
    "mtd": "Mualang",
    "mtj": "Moskona",
    "mto": "Mixe, Totontepec",
    "muh": "Mündü",
    "mup": "Malvi",
    "mur": "Murle",
    "muv": "Muthuvan",
    "muy": "Muyang",
    "mvp": "Duri",
    "mwq": "Chin, Müün",
    "mwv": "Mentawai",
    "mxb": "Mixtec, Tezoatlán",
    "mxq": "Mixe, Juquila",
    "mxt": "Mixtec, Jamiltepec",
    "mxv": "Mixtec, Metlatónoc",
    "mya": "Burmese",
    "myb": "Mbay",
    "myk": "Sénoufo, Mamara",
    "myl": "Moma",
    "myv": "Erzya",
    "myx": "Masaaba",
    "myy": "Macuna",
    "mza": "Mixtec, Santa María Zacatepec",
    "mzi": "Mazatec, Ixcatlán",
    "mzj": "Manya",
    "mzk": "Mambila, Nigeria",
    "mzm": "Mumuye",
    "mzw": "Deg",
    "nab": "Nambikuára, Southern",
    "nag": "Nagamese",
    "nan": "Chinese, Min Nan",
    "nas": "Naasioi",
    "naw": "Nawuri",
    "nca": "Iyo",
    "nch": "Nahuatl, Central Huasteca",
    "ncj": "Nahuatl, Northern Puebla",
    "ncl": "Nahuatl, Michoacán",
    "ncu": "Chumburung",
    "ndj": "Ndamba",
    "ndp": "Kebu",
    "ndv": "Ndut",
    "ndy": "Lutos",
    "ndz": "Ndogo",
    "neb": "Toura",
    "new": "Newar",
    "nfa": "Dhao",
    "nfr": "Nafaanra",
    "nga": "Ngbaka",
    "ngl": "Lomwe",
    "ngp": "Ngulu",
    "ngu": "Nahuatl, Guerrero",
    "nhe": "Nahuatl, Eastern Huasteca",
    "nhi": "Nahuatl, Zacatlán-Ahuacatlán-Tepetzintla",
    "nhu": "Noone",
    "nhw": "Nahuatl, Western Huasteca",
    "nhx": "Nahuatl, Isthmus-Mecayapan",
    "nhy": "Nahuatl, Northern Oaxaca",
    "nia": "Nias",
    "nij": "Ngaju",
    "nim": "Nilamba",
    "nin": "Ninzo",
    "nko": "Nkonya",
    "nlc": "Nalca",
    "nld": "Dutch",
    "nlg": "Gela",
    "nlk": "Yali, Ninia",
    "nmz": "Nawdm",
    "nnb": "Nande",
    "nnq": "Ngindo",
    "nnw": "Nuni, Southern",
    "noa": "Woun Meu",
    "nod": "Thai, Northern",
    "nog": "Nogai",
    "not": "Nomatsigenga",
    "npl": "Nahuatl, Southeastern Puebla",
    "npy": "Napu",
    "nst": "Naga, Tangshang",
    "nsu": "Nahuatl, Sierra Negra",
    "ntm": "Nateni",
    "ntr": "Delo",
    "nuj": "Nyole",
    "nus": "Nuer",
    "nuz": "Nahuatl, Tlamacazapa",
    "nwb": "Nyabwa",
    "nxq": "Naxi",
    "nya": "Chichewa",
    "nyf": "Kigiryama",
    "nyn": "Nyankore",
    "nyo": "Nyoro",
    "nyy": "Nyakyusa-Ngonde",
    "nzi": "Nzema",
    "obo": "Manobo, Obo",
    "ojb": "Ojibwa, Northwestern",
    "oku": "Oku",
    "old": "Mochi",
    "omw": "Tairora, South",
    "onb": "Lingao",
    "ood": "Tohono O’odham",
    "orm": "Oromo",
    "ory": "Odia",
    "oss": "Ossetic",
    "ote": "Otomi, Mezquital",
    "otq": "Otomi, Querétaro",
    "ozm": "Koonzime",
    "pab": "Parecís",
    "pad": "Paumarí",
    "pag": "Pangasinan",
    "pam": "Kapampangan",
    "pan": "Punjabi, Eastern",
    "pao": "Paiute, Northern",
    "pap": "Papiamentu",
    "pau": "Palauan",
    "pbb": "Nasa",
    "pbc": "Patamona",
    "pbi": "Parkwa",
    "pce": "Palaung, Ruching",
    "pcm": "Pidgin, Nigerian",
    "peg": "Pengo",
    "pez": "Penan, Eastern",
    "pib": "Yine",
    "pil": "Yom",
    "pir": "Piratapuyo",
    "pis": "Pijin",
    "pjt": "Pitjantjatjara",
    "pkb": "Kipfokomo",
    "pls": "Popoloca, San Marcos Tlacoyalco",
    "plw": "Palawano, Brooke’s Point",
    "pmf": "Pamona",
    "pny": "Pinyin",
    "poh": "Poqomchi’",
    "poi": "Popoluca, Highland",
    "pol": "Polish",
    "por": "Portuguese",
    "poy": "Pogolo",
    "ppk": "Uma",
    "pps": "Popoloca, San Luís Temalacayuca",
    "prf": "Paranan",
    "prk": "Wa, Parauk",
    "prt": "Prai",
    "pse": "Malay, Central",
    "pss": "Kaulong",
    "ptu": "Bambam",
    "pui": "Puinave",
    "pwg": "Gapapaiwa",
    "pww": "Karen, Pwo Northern",
    "pxm": "Mixe, Quetzaltepec",
    "qub": "Quechua, Huallaga",
    "quc": "K’iche’",
    "quf": "Quechua, Lambayeque",
    "quh": "Quechua, South Bolivian",
    "qul": "Quechua, North Bolivian",
    "quw": "Quichua, Tena Lowland",
    "quy": "Quechua, Ayacucho",
    "quz": "Quechua, Cusco",
    "qvc": "Quechua, Cajamarca",
    "qve": "Quechua, Eastern Apurímac",
    "qvh": "Quechua, Huamalíes-Dos de Mayo Huánuco",
    "qvm": "Quechua, Margos-Yarowilca-Lauricocha",
    "qvn": "Quechua, North Junín",
    "qvo": "Quichua, Napo",
    "qvs": "Quechua, San Martín",
    "qvw": "Quechua, Huaylla Wanca",
    "qvz": "Quichua, Northern Pastaza",
    "qwh": "Quechua, Huaylas Ancash",
    "qxh": "Quechua, Panao",
    "qxl": "Quichua, Salasaca Highland",
    "qxn": "Quechua, Northern Conchucos Ancash",
    "qxo": "Quechua, Southern Conchucos",
    "qxr": "Quichua, Cañar Highland",
    "rah": "Rabha",
    "rai": "Ramoaaina",
    "rap": "Rapa Nui",
    "rav": "Sampang",
    "raw": "Rawang",
    "rej": "Rejang",
    "rel": "Rendille",
    "rgu": "Rikou",
    "rhg": "Rohingya",
    "rif": "Tarifit",
    "ril": "Riang Lang",
    "rim": "Nyaturu",
    "rjs": "Rajbanshi",
    "rkt": "Rangpuri",
    "rmc": "Romani, Carpathian",
    "rmo": "Romani, Sinte",
    "rmy": "Romani, Vlax",
    "rng": "Ronga",
    "rnl": "Ranglong",
    "rol": "Romblomanon",
    "ron": "Romanian",
    "rop": "Kriol",
    "rro": "Waima",
    "rub": "Gungu",
    "ruf": "Luguru",
    "rug": "Roviana",
    "run": "Rundi",
    "rus": "Russian",
    "sab": "Buglere",
    "sag": "Sango",
    "sah": "Yakut",
    "saj": "Sahu",
    "saq": "Samburu",
    "sas": "Sasak",
    "sba": "Ngambay",
    "sbd": "Samo, Southern",
    "sbl": "Sambal, Botolan",
    "sbp": "Sangu",
    "sch": "Sakachep",
    "sck": "Sadri",
    "sda": "Toraja-Sa’dan",
    "sea": "Semai",
    "seh": "Sena",
    "ses": "Songhay, Koyraboro Senni",
    "sey": "Paicoca",
    "sgb": "Ayta, Mag-antsi",
    "sgj": "Surgujia",
    "sgw": "Sebat Bet Gurage",
    "shi": "Tachelhit",
    "shk": "Shilluk",
    "shn": "Shan",
    "sho": "Shanga",
    "shp": "Shipibo-Conibo",
    "sid": "Sidamo",
    "sig": "Paasaal",
    "sil": "Sisaala, Tumulung",
    "sja": "Epena",
    "sjm": "Mapun",
    "sld": "Sissala",
    "slu": "Selaru",
    "sml": "Sama, Central",
    "smo": "Samoan",
    "sna": "Shona",
    "sne": "Bidayuh, Bau",
    "snn": "Siona",
    "snp": "Siane",
    "snw": "Selee",
    "som": "Somali",
    "soy": "Miyobe",
    "spa": "Spanish",
    "spp": "Sénoufo, Supyire",
    "spy": "Sabaot",
    "sqi": "Albanian",
    "sri": "Siriano",
    "srm": "Saramaccan",
    "srn": "Sranan Tongo",
    "srx": "Sirmauri",
    "stn": "Owa",
    "stp": "Tepehuan, Southeastern",
    "suc": "Subanon, Western",
    "suk": "Sukuma",
    "sun": "Sunda",
    "sur": "Mwaghavul",
    "sus": "Susu",
    "suv": "Puroik",
    "suz": "Sunwar",
    "swe": "Swedish",
    "swh": "Swahili",
    "sxb": "Suba",
    "sxn": "Sangir",
    "sya": "Siang",
    "syl": "Sylheti",
    "sza": "Semelai",
    "tac": "Tarahumara, Western",
    "taj": "Tamang, Eastern",
    "tam": "Tamil",
    "tao": "Yami",
    "tap": "Taabwa",
    "taq": "Tamasheq",
    "tat": "Tatar",
    "tav": "Tatuyo",
    "tbc": "Takia",
    "tbg": "Tairora, North",
    "tbk": "Tagbanwa, Calamian",
    "tbl": "Tboli",
    "tby": "Tabaru",
    "tbz": "Ditammari",
    "tca": "Ticuna",
    "tcc": "Datooga",
    "tcs": "Torres Strait Creole",
    "tcz": "Chin, Thado",
    "tdj": "Tajio",
    "ted": "Krumen, Tepo",
    "tee": "Tepehua, Huehuetla",
    "tel": "Telugu",
    "tem": "Themne",
    "teo": "Ateso",
    "ter": "Terêna",
    "tes": "Tengger",
    "tew": "Tewa",
    "tex": "Tennet",
    "tfr": "Teribe",
    "tgj": "Tagin",
    "tgk": "Tajik",
    "tgl": "Tagalog",
    "tgo": "Sudest",
    "tgp": "Tangoa",
    "tha": "Thai",
    "thk": "Kitharaka",
    "thl": "Tharu, Dangaura",
    "tih": "Murut, Timugon",
    "tik": "Tikar",
    "tir": "Tigrigna",
    "tkr": "Tsakhur",
    "tlb": "Tobelo",
    "tlj": "Talinga-Bwisi",
    "tly": "Talysh",
    "tmc": "Tumak",
    "tmf": "Toba-Maskoy",
    "tna": "Tacana",
    "tng": "Tobanga",
    "tnk": "Kwamera",
    "tnn": "Tanna, North",
    "tnp": "Whitesands",
    "tnr": "Ménik",
    "tnt": "Tontemboan",
    "tob": "Toba",
    "toc": "Totonac, Coyutla",
    "toh": "Tonga",
    "tom": "Tombulu",
    "tos": "Totonac, Highland",
    "tpi": "Tok Pisin",
    "tpm": "Tampulma",
    "tpp": "Tepehua, Pisaflores",
    "tpt": "Tepehua, Tlachichilco",
    "trc": "Triqui, Copala",
    "tri": "Trió",
    "trn": "Trinitario",
    "trs": "Triqui, Chicahuaxtla",
    "tso": "Tsonga",
    "tsz": "Purepecha",
    "ttc": "Tektiteko",
    "tte": "Bwanabwana",
    "ttq": "Tamajaq, Tawallammat",
    "tue": "Tuyuca",
    "tuf": "Tunebo, Central",
    "tuk": "Turkmen",
    "tuo": "Tucano",
    "tur": "Turkish",
    "tvw": "Sedoa",
    "twb": "Tawbuid",
    "twe": "Teiwa",
    "twu": "Termanu",
    "txa": "Tombonuo",
    "txq": "Tii",
    "txu": "Kayapó",
    "tye": "Kyanga",
    "tzh": "Tzeltal",
    "tzj": "Tz’utujil",
    "tzo": "Tzotzil",
    "ubl": "Bikol, Buhi’non",
    "ubu": "Umbu-Ungu",
    "udm": "Udmurt",
    "udu": "Uduk",
    "uig": "Uyghur",
    "ukr": "Ukrainian",
    "unr": "Mundari",
    "upv": "Uripiv-Wala-Rano-Atchin",
    "ura": "Urarina",
    "urb": "Kaapor",
    "urd": "Urdu",
    "urk": "Urak Lawoi’",
    "urt": "Urat",
    "ury": "Orya",
    "usp": "Uspanteko",
    "uzb": "Uzbek",
    "vag": "Vagla",
    "vid": "Vidunda",
    "vie": "Vietnamese",
    "vif": "Vili",
    "vmw": "Makhuwa",
    "vmy": "Mazatec, Ayautla",
    "vun": "Vunjo",
    "vut": "Vute",
    "wal": "Wolaytta",
    "wap": "Wapishana",
    "war": "Waray-Waray",
    "waw": "Waiwai",
    "way": "Wayana",
    "wba": "Warao",
    "wlo": "Wolio",
    "wlx": "Wali",
    "wmw": "Mwani",
    "wob": "Wè Northern",
    "wsg": "Gondi, Adilabad",
    "wwa": "Waama",
    "xal": "Kalmyk-Oirat",
    "xdy": "Malayic Dayak",
    "xed": "Hdi",
    "xer": "Xerénte",
    "xmm": "Malay, Manado",
    "xnj": "Chingoni",
    "xnr": "Kangri",
    "xog": "Soga",
    "xon": "Konkomba",
    "xrb": "Karaboro, Eastern",
    "xsb": "Sambal",
    "xsm": "Kasem",
    "xsr": "Sherpa",
    "xsu": "Sanumá",
    "xta": "Mixtec, Alcozauca",
    "xtd": "Mixtec, Diuxi-Tilantongo",
    "xte": "Ketengban",
    "xtm": "Mixtec, Magdalena Peñasco",
    "xtn": "Mixtec, Northern Tlaxiaco",
    "xua": "Kurumba, Alu",
    "xuo": "Kuo",
    "yaa": "Yaminahua",
    "yad": "Yagua",
    "yal": "Yalunka",
    "yam": "Yamba",
    "yao": "Yao",
    "yas": "Nugunu",
    "yat": "Yambeta",
    "yaz": "Lokaa",
    "yba": "Yala",
    "ybb": "Yemba",
    "ycl": "Lolopo",
    "ycn": "Yucuna",
    "yea": "Ravula",
    "yka": "Yakan",
    "yli": "Yali, Angguruk",
    "yor": "Yoruba",
    "yre": "Yaouré",
    "yua": "Maya, Yucatec",
    "yuz": "Yuracare",
    "yva": "Yawa",
    "zaa": "Zapotec, Sierra de Juárez",
    "zab": "Zapotec, Western Tlacolula Valley",
    "zac": "Zapotec, Ocotlán",
    "zad": "Zapotec, Cajonos",
    "zae": "Zapotec, Yareni",
    "zai": "Zapotec, Isthmus",
    "zam": "Zapotec, Miahuatlán",
    "zao": "Zapotec, Ozolotepec",
    "zaq": "Zapotec, Aloápam",
    "zar": "Zapotec, Rincón",
    "zas": "Zapotec, Santo Domingo Albarradas",
    "zav": "Zapotec, Yatzachi",
    "zaw": "Zapotec, Mitla",
    "zca": "Zapotec, Coatecas Altas",
    "zga": "Kinga",
    "zim": "Mesme",
    "ziw": "Zigula",
    "zlm": "Malay",
    "zmz": "Mbandja",
    "zne": "Zande",
    "zos": "Zoque, Francisco León",
    "zpc": "Zapotec, Choapan",
    "zpg": "Zapotec, Guevea de Humboldt",
    "zpi": "Zapotec, Santa María Quiegolani",
    "zpl": "Zapotec, Lachixío",
    "zpm": "Zapotec, Mixtepec",
    "zpo": "Zapotec, Amatlán",
    "zpt": "Zapotec, San Vicente Coatlán",
    "zpu": "Zapotec, Yalálag",
    "zpz": "Zapotec, Texmelucan",
    "ztq": "Zapotec, Quioquitani-Quierí",
    "zty": "Zapotec, Yatee",
    "zyb": "Zhuang, Yongbei",
    "zyp": "Chin, Zyphe",
    "zza": "Zaza"
}

language_to_txt_correction_mapping = {
    "eng": "english",
    "deu": "german",
}

class Mms(metaclass=SingletonMeta):
    model = None
    processor = None

    device = None
    compute_type = "float32"
    compute_device = "cpu"
    compute_device_str = "cpu"
    precision = None
    load_in_8bit = False

    used_language = "eng"
    previous_model = ""

    text_correction_model = None

    language_identification = None

    def __init__(self, model='mms-1b-fl102', compute_type="float32", device="cpu"):
        self.load_model(model_size=model, compute_type=compute_type, device=device)

    @staticmethod
    def get_languages():
        return tuple([{"code": code, "name": language} for code, language in LANGUAGES.items()])

    def _str_to_dtype_dict(self, dtype_str):
        if dtype_str == "float16":
            return {'dtype': torch.float16, '4bit': False, '8bit': False}
        elif dtype_str == "float32":
            return {'dtype': torch.float32, '4bit': False, '8bit': False}
        elif dtype_str == "4bit":
            return {'dtype': torch.float32, '4bit': True, '8bit': False}
        elif dtype_str == "8bit":
            return {'dtype': torch.float32, '4bit': False, '8bit': True}
        else:
            return {'dtype': torch.float32, '4bit': False, '8bit': False}

    def set_device(self, device: str | None):
        self.compute_device_str = device
        if device is None or device == "cuda" or device == "auto" or device == "":
            self.compute_device_str = "cuda" if torch.cuda.is_available() else "cpu"
            device = torch.device(self.compute_device_str)
        elif device == "cpu":
            device = torch.device("cpu")
        elif device.startswith("direct-ml"):
            device_id = 0
            device_id_split = device.split(":")
            if len(device_id_split) > 1:
                device_id = int(device_id_split[1])
            import torch_directml
            device = torch_directml.device(device_id)
        self.compute_device = device

    def load_model(self, model_size='mms-1b-fl102', compute_type="float32", device="cpu"):
        model_path = Path(model_cache_path / model_size)

        if self.previous_model is None or model_size != self.previous_model:
            compute_dtype = self._str_to_dtype_dict(compute_type).get('dtype', torch.float32)
            compute_4bit = self._str_to_dtype_dict(self.compute_type).get('4bit', False)
            compute_8bit = self._str_to_dtype_dict(self.compute_type).get('8bit', False)
            self.compute_type = compute_type
            self.set_device(device)

            if self.model is None or model_size != self.previous_model:
                if self.model is not None:
                    self.release_model()

                # self.download_model(model_size)

                print(f"MMS {model_size} is Loading to {device} using {compute_type} precision...")

                self.processor = AutoProcessor.from_pretrained(str(model_path.resolve()),
                                                               torch_dtype=compute_dtype)

                self.model = Wav2Vec2ForCTC.from_pretrained(str(model_path.resolve()),
                                                            torch_dtype=compute_dtype,
                                                            ignore_mismatched_sizes=True,
                                                            load_in_8bit=compute_8bit,
                                                            load_in_4bit=compute_4bit,
                                                            )

                self.model.to(self.compute_device).to(compute_dtype)

                # load text correction model
                self.text_correction_model = T5.TextCorrectionT5(self.compute_type, self.compute_device)

    def release_model(self):
        if self.model is not None:
            print("Releasing mms model...")
            if hasattr(self.model, 'model'):
                del self.model.model
            if hasattr(self.model, 'feature_extractor'):
                del self.model.feature_extractor
            if hasattr(self.model, 'hf_tokenizer'):
                del self.model.hf_tokenizer
            del self.model
            self.previous_model = ""
        if self.processor is not None:
            del self.processor
            self.used_language = ""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def transcribe(self, audio_sample, source_lang=None) -> dict:
        if source_lang is not None and (source_lang == '' or source_lang.lower() == 'auto'):
            source_lang = None

        if source_lang is None:
            if self.language_identification is None:
                self.language_identification = MmsLid(model="4017", compute_type=self.compute_type, device=self.compute_device)

            if self.language_identification is not None:
                source_lang = self.language_identification.classify(audio_sample)

        compute_dtype = self._str_to_dtype_dict(self.compute_type).get('dtype', torch.float32)
        compute_4bit = self._str_to_dtype_dict(self.compute_type).get('4bit', False)
        compute_8bit = self._str_to_dtype_dict(self.compute_type).get('8bit', False)

        if self.used_language != source_lang:
            print("switching adapter to: " + source_lang)
            self.used_language = source_lang
            self.processor.tokenizer.set_target_lang(source_lang)
            self.model.load_adapter(source_lang,
                                    torch_dtype=compute_dtype,
                                    ignore_mismatched_sizes=True,
                                    load_in_8bit=compute_8bit,
                                    load_in_4bit=compute_4bit,
                                    )
            self.model.to(self.compute_device).to(compute_dtype)

        inputs = self.processor(audio=audio_sample, sampling_rate=16_000, return_tensors="pt")
        inputs = inputs.to(self.compute_device).to(compute_dtype)

        with torch.no_grad():
            output_tokens = self.model(**inputs).logits

        ids = torch.argmax(output_tokens, dim=-1)[0]
        transcription = self.processor.decode(ids)

        if self.text_correction_model is not None and transcription != "" and source_lang in language_to_txt_correction_mapping:
            transcription = self.text_correction_model.translate(transcription, language_to_txt_correction_mapping[source_lang])

        result = {
            'text': transcription,
            'type': "transcribe",
            'language': source_lang,
            'target_lang': source_lang
        }

        return result


class MmsLid(metaclass=SingletonMeta):
    model = None
    processor = None

    device = None
    precision = None
    load_in_8bit = False

    previous_model = ""

    def __init__(self, model='4017', compute_type="float32", device="cpu"):
        self.compute_type = compute_type
        self.compute_device = device

        self.load_model(model_size=model, compute_type=compute_type, device=device)

    def _str_to_dtype_dict(self, dtype_str):
        if dtype_str == "float16":
            return {'dtype': torch.float16, '4bit': False, '8bit': False}
        elif dtype_str == "float32":
            return {'dtype': torch.float32, '4bit': False, '8bit': False}
        elif dtype_str == "4bit":
            return {'dtype': torch.float32, '4bit': True, '8bit': False}
        elif dtype_str == "8bit":
            return {'dtype': torch.float32, '4bit': False, '8bit': True}
        else:
            return {'dtype': torch.float32, '4bit': False, '8bit': False}

    def load_model(self, model_size='4017', compute_type="float32", device="cpu"):
        model_path = Path(model_cache_path / ("lid-" + model_size))

        if self.previous_model is None or model_size != self.previous_model:
            compute_dtype = self._str_to_dtype_dict(compute_type).get('dtype', torch.float32)
            compute_4bit = self._str_to_dtype_dict(self.compute_type).get('4bit', False)
            compute_8bit = self._str_to_dtype_dict(self.compute_type).get('8bit', False)
            self.compute_type = compute_type
            self.compute_device = device

            if self.model is None or model_size != self.previous_model:
                if self.model is not None:
                    self.release_model()

                # self.download_model(model_size)

                print(f"MMS LID {model_size} is Loading to {device} using {compute_type} precision...")

                self.processor = AutoFeatureExtractor.from_pretrained(str(model_path.resolve()),
                                                               torch_dtype=compute_dtype)

                self.model = Wav2Vec2ForSequenceClassification.from_pretrained(str(model_path.resolve()),
                                                            torch_dtype=compute_dtype,
                                                            ignore_mismatched_sizes=True,
                                                            load_in_8bit=compute_8bit,
                                                            load_in_4bit=compute_4bit,
                                                            )
                self.model.to(self.compute_device).to(compute_dtype)

    def release_model(self):
        if self.model is not None:
            print("Releasing mms model...")
            if hasattr(self.model, 'model'):
                del self.model.model
            if hasattr(self.model, 'feature_extractor'):
                del self.model.feature_extractor
            if hasattr(self.model, 'hf_tokenizer'):
                del self.model.hf_tokenizer
            del self.model
            self.previous_model = ""
        if self.processor is not None:
            del self.processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    def classify(self, audio) -> str:
        print("classifying")
        if audio is None:
            return ""

        compute_dtype = self._str_to_dtype_dict(self.compute_type).get('dtype', torch.float32)

        inputs = self.processor(audio, sampling_rate=16_000, return_tensors="pt")
        inputs = inputs.to(self.compute_device).to(compute_dtype)

        with torch.no_grad():
            outputs = self.model(**inputs).logits

        lang_id = torch.argmax(outputs, dim=-1)[0].item()

        print(self.model.config.id2label[lang_id])

        return self.model.config.id2label[lang_id]
