"""Bulk seed batch 7: fill all cells that have exactly 1 question (need a second)."""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── EGO – action_oriented ────────────────────────────────────────────────────
{"themes":["ego"],"type":"action_oriented","depth":1,"emotions":["pride","stubbornness"],"concepts":["ego","karma"],
"en":"What would you say or do differently right now if protecting your image were simply not on the table?",
"hi":"यदि अपनी छवि बचाना बस विकल्प में न हो — तो आप अभी क्या अलग कहेंगे या करेंगे?",
"hinglish":"Agar apni chhavi bachana bas option mein na ho — toh aap abhi kya alag kahenge ya karenge?"},

{"themes":["ego"],"type":"action_oriented","depth":2,"emotions":["pride","defensiveness"],"concepts":["ego","karma"],
"en":"Where in your life are you performing rather than being — and what would it feel like to stop, just for today?",
"hi":"आपके जीवन में कहाँ आप होने की जगह प्रदर्शन कर रहे हैं — और आज के लिए बस रुकना कैसा लगेगा?",
"hinglish":"Aapke jeevan mein kahan aap hone ki jagah pradarshan kar rahe hain — aur aaj ke liye bas rukna kaisa lagega?"},

{"themes":["ego"],"type":"action_oriented","depth":3,"emotions":["pride","shame"],"concepts":["ego","karma","surrender"],
"en":"What would you have to stop needing — recognition, the last word, being right — to act from your deepest self today?",
"hi":"आज अपने गहरे स्वयं से कार्य करने के लिए — मान्यता, अंतिम शब्द, सही होना — आपको क्या चाहने से रोकना होगा?",
"hinglish":"Aaj apne gehre khud se kaam karne ke liye — manyata, antim shabd, sahi hona — aapko kya chahne se rokna hoga?"},

# ── EGO – spiritual ──────────────────────────────────────────────────────────
{"themes":["ego"],"type":"spiritual","depth":1,"emotions":["pride","restlessness"],"concepts":["ego","witness-self"],
"en":"What if the voice that insists on its importance most loudly is the one most in need of quiet?",
"hi":"क्या हो यदि जो आवाज़ सबसे ज़ोर से अपने महत्व पर जोर देती है — वही सबसे अधिक शांति की ज़रूरत में है?",
"hinglish":"Kya ho agar jo aawaaz sabse zor se apne mahatva par zor deti hai — wahi sabse zyada shanti ki zaroorat mein hai?"},

{"themes":["ego"],"type":"spiritual","depth":2,"emotions":["pride","shame"],"concepts":["ego","witness-self","detachment"],
"en":"What would your spiritual practice look like if you were not also hoping it would make you a better or more admirable person?",
"hi":"यदि आप यह भी आशा नहीं कर रहे थे कि यह आपको एक बेहतर या अधिक प्रशंसनीय व्यक्ति बनाएगा — तो आपका आध्यात्मिक अभ्यास कैसा दिखेगा?",
"hinglish":"Agar aap yeh bhi asha nahi kar rahe the ki yeh aapko ek behtar ya zyada prashansaneeya insaan banaayega — toh aapka aadhyatmik abhyas kaisa dikhega?"},

{"themes":["ego"],"type":"spiritual","depth":3,"emotions":["pride","existential","shame"],"concepts":["ego","witness-self","surrender"],
"en":"What if the ego is not something to destroy — but to see through: to recognise as a useful tool without mistaking it for the self?",
"hi":"क्या हो यदि अहंकार को नष्ट नहीं करना है — बल्कि इसे देखना है: एक उपयोगी उपकरण के रूप में पहचानना बिना इसे स्वयं समझने की गलती किए?",
"hinglish":"Kya ho agar ahankar ko nasht nahi karna hai — balki ise dekhna hai: ek upyogi upkarana ke roop mein pahchanana bina ise khud samajhne ki galti kiye?"},

# ── FEAR – action_oriented & spiritual ──────────────────────────────────────
{"themes":["fear"],"type":"action_oriented","depth":1,"emotions":["avoidance","dread"],"concepts":["karma","courage"],
"en":"What is the smallest version of the thing you fear that you could face today — not the whole thing, just the edge of it?",
"hi":"जिस चीज़ से आप डरते हैं उसका सबसे छोटा संस्करण क्या है जिसका आप आज सामना कर सकते हैं — पूरा नहीं, बस उसका किनारा?",
"hinglish":"Jis cheez se aap darte hain uska sabse chhota version kya hai jiska aap aaj saamna kar sakte hain — poora nahi, bas uska kinara?"},

{"themes":["fear"],"type":"action_oriented","depth":2,"emotions":["avoidance","dread"],"concepts":["karma","svadharma","courage"],
"en":"If fear were not the deciding factor today — what decision would you make that you have been putting off?",
"hi":"यदि आज डर निर्णायक कारक न हो — तो आप कौन-सा निर्णय लेंगे जिसे आप टालते रहे हैं?",
"hinglish":"Agar aaj dar nirnayak kaarak na ho — toh aap kaun sa nirnay lenge jise aap taalte rahe hain?"},

{"themes":["fear"],"type":"action_oriented","depth":3,"emotions":["dread","shame"],"concepts":["karma","dharma"],"en":"What would you owe to your future self if you acted with courage here, rather than waiting until you were no longer afraid?",
"hi":"यदि आप यहाँ साहस के साथ कार्य करें — डर के जाने का इंतज़ार किए बिना — तो आप अपने भविष्य के स्वयं को क्या देंगे?",
"hinglish":"Agar aap yahan sahas ke saath kaam karein — dar ke jaane ka intezaar kiye bina — toh aap apne bhavishy ke khud ko kya denge?"},

{"themes":["fear"],"type":"spiritual","depth":1,"emotions":["dread","longing"],"concepts":["surrender","equanimity"],
"en":"What if this fear is an initiation — not a stop sign but a threshold, asking whether you are ready to cross?",
"hi":"क्या हो यदि यह डर एक दीक्षा है — रुकने का संकेत नहीं बल्कि एक दहलीज़, पूछती हुई कि क्या आप पार करने के लिए तैयार हैं?",
"hinglish":"Kya ho agar yeh dar ek diksha hai — rukne ka sanket nahi balki ek dahliz, poochti hui ki kya aap paar karne ke liye taiyar hain?"},

{"themes":["fear"],"type":"spiritual","depth":3,"emotions":["existential","dread"],"concepts":["witness-self","surrender","impermanence"],
"en":"What remains in you when the fear moves through — and is that remainder available to you even while the fear is present?",
"hi":"जब डर से गुज़रता है — आपमें क्या बचता है, और क्या डर के उपस्थित रहते हुए भी वह शेष आपके लिए उपलब्ध है?",
"hinglish":"Jab dar se guzarta hai — aap mein kya bachta hai, aur kya dar ke maujood rehte hue bhi woh shesh aapke liye uplabdh hai?"},

# ── ATTACHMENT – action_oriented d1 ─────────────────────────────────────────
{"themes":["attachment"],"type":"action_oriented","depth":1,"emotions":["clinging","worry"],"concepts":["karma","detachment"],
"en":"What is one thing you are holding so tightly today that loosening your grip slightly might actually serve it better?",
"hi":"आज एक चीज़ जिसे आप इतनी कसकर थामे हैं कि पकड़ थोड़ी ढीली करना वास्तव में उसकी बेहतर सेवा कर सकता है?",
"hinglish":"Aaj ek cheez jise aap itni kaskar thame hain ki pakad thodi dhili karna asal mein uski behtar seva kar sakta hai?"},

# ── DESIRE – action_oriented & spiritual ─────────────────────────────────────
{"themes":["desire"],"type":"action_oriented","depth":1,"emotions":["longing","craving"],"concepts":["karma","svadharma"],
"en":"Instead of chasing what you want right now — what would it look like to cultivate the conditions in which it could naturally arise?",
"hi":"अभी जो आप चाहते हैं उसका पीछा करने की जगह — उन परिस्थितियों को विकसित करना कैसा दिखेगा जिनमें यह स्वाभाविक रूप से उत्पन्न हो सके?",
"hinglish":"Abhi jo aap chahte hain uska peechha karne ki jagah — un paristhitiyon ko viksit karna kaisa dikhega jinmein yeh svabhaavic roop se utpanna ho sake?"},

{"themes":["desire"],"type":"action_oriented","depth":2,"emotions":["craving","resistance"],"concepts":["karma","detachment"],
"en":"What would it look like to want this fully — giving it your honest effort — while treating the outcome as a gift rather than a due?",
"hi":"इसे पूरी तरह चाहना कैसा दिखेगा — इसके लिए अपना ईमानदार प्रयास देना — लेकिन परिणाम को अधिकार की जगह उपहार मानना?",
"hinglish":"Ise poori tarah chahna kaisa dikhega — iske liye apna imaandaar prayas dena — lekin natija ko adhikaar ki jagah uphaar maanna?"},

{"themes":["desire"],"type":"action_oriented","depth":3,"emotions":["longing","craving","grief"],"concepts":["karma","detachment","dharma"],
"en":"What desire — if you honoured it with discipline rather than chasing it with urgency — might actually take you somewhere worth going?",
"hi":"कौन-सी इच्छा — यदि आप इसे जल्दबाज़ी से नहीं बल्कि अनुशासन से सम्मान दें — वास्तव में आपको कहीं ऐसी जगह ले जा सकती है जो जाने योग्य हो?",
"hinglish":"Kaun si ichha — agar aap ise jaldi-baazi se nahi balki anushasan se samman dein — asal mein aapko kahi aisi jagah le ja sakti hai jo jaane yogya ho?"},

{"themes":["desire"],"type":"spiritual","depth":1,"emotions":["longing","craving"],"concepts":["desire","equanimity"],
"en":"What does this desire feel like in the body — before the mind names it and decides what to do with it?",
"hi":"यह इच्छा शरीर में कैसी महसूस होती है — इससे पहले कि मन इसे नाम दे और इसके साथ क्या करना है यह तय करे?",
"hinglish":"Yeh ichha sharir mein kaisi mahsoos hoti hai — isse pehle ki mann ise naam de aur iske saath kya karna hai yeh tay kare?"},

{"themes":["desire"],"type":"spiritual","depth":2,"emotions":["longing","restlessness"],"concepts":["desire","ego","surrender"],
"en":"What if every desire is pointing at a wholeness you already have — and the reaching outward is only the surface of a deeper inward return?",
"hi":"क्या हो यदि हर इच्छा एक ऐसी पूर्णता की ओर इशारा कर रही है जो आपके पास पहले से है — और बाहर पहुँचना केवल एक गहरी भीतरी वापसी का बाहरी रूप है?",
"hinglish":"Kya ho agar har ichha ek aisi purnata ki taraf ishara kar rahi hai jo aapke paas pehle se hai — aur bahar pahunchna sirf ek gehri bheeetri wapsi ka baahri roop hai?"},

{"themes":["desire"],"type":"spiritual","depth":3,"emotions":["longing","existential","craving"],"concepts":["desire","ego","witness-self"],
"en":"What would it mean to rest in the awareness that watches desire arise and pass — without being swept away by it, and without suppressing it?",
"hi":"उस चेतना में विश्राम करने का क्या अर्थ होगा जो इच्छा को उठते और जाते देखती है — उसमें बहे बिना, और उसे दबाए बिना?",
"hinglish":"Us chetna mein vishram karne ka kya matlab hoga jo ichha ko uthte aur jaate dekhti hai — us mein bahe bina, aur use dabaaye bina?"},

# ── JEALOUSY – action_oriented & spiritual ───────────────────────────────────
{"themes":["jealousy"],"type":"action_oriented","depth":1,"emotions":["envy","restlessness"],"concepts":["karma","svadharma"],
"en":"What is one thing you envy in someone else that you could begin developing in yourself — starting today?",
"hi":"किसी और में एक चीज़ जिससे आप ईर्ष्या करते हैं जिसे आप खुद में विकसित करना शुरू कर सकते हैं — आज से शुरू?",
"hinglish":"Kisi aur mein ek cheez jisse aap irshya karte hain jise aap khud mein viksit karna shuru kar sakte hain — aaj se shuru?"},

{"themes":["jealousy"],"type":"action_oriented","depth":2,"emotions":["envy","inadequacy"],"concepts":["karma","svadharma","dharma"],
"en":"What part of your own path have you been neglecting while you watched someone else's — and what would it look like to return to it?",
"hi":"किसी और के मार्ग को देखते हुए आपने अपने मार्ग के किस हिस्से की उपेक्षा की है — और उस पर वापस लौटना कैसा दिखेगा?",
"hinglish":"Kisi aur ke raaste ko dekhte hue aapne apne raaste ke kis hisse ki upeksha ki hai — aur us par wapas lautna kaisa dikhega?"},

{"themes":["jealousy"],"type":"action_oriented","depth":3,"emotions":["envy","shame","grief"],"concepts":["karma","svadharma","detachment"],
"en":"What would you pour your full energy into today if you genuinely no longer cared what anyone else had?",
"hi":"यदि आप वास्तव में अब किसी और के पास क्या है उसकी परवाह नहीं करते — तो आज आप अपनी पूरी ऊर्जा किसमें लगाएंगे?",
"hinglish":"Agar aap asal mein ab kisi aur ke paas kya hai uski parwaah nahi karte — toh aaj aap apni poori urja kismein lagaayenge?"},

{"themes":["jealousy"],"type":"spiritual","depth":1,"emotions":["envy","inadequacy"],"concepts":["svadharma","ego"],
"en":"What if what you see in others that you envy is actually showing you what is already latent in yourself?",
"hi":"क्या हो यदि दूसरों में जो आप देखते हैं जिससे ईर्ष्या करते हैं — वह वास्तव में दिखा रहा है कि आपमें क्या पहले से छुपा है?",
"hinglish":"Kya ho agar doosron mein jo aap dekhte hain jisse irshya karte hain — woh asal mein dikha raha hai ki aap mein kya pehle se chhupa hai?"},

{"themes":["jealousy"],"type":"spiritual","depth":2,"emotions":["envy","shame"],"concepts":["svadharma","ego","karma"],
"en":"What would it mean to bless what someone else has — genuinely, not as a performance — and what would that free in you?",
"hi":"किसी और के पास जो है उसे — वास्तव में, प्रदर्शन के रूप में नहीं — आशीर्वाद देने का क्या अर्थ होगा, और यह आपमें क्या मुक्त करेगा?",
"hinglish":"Kisi aur ke paas jo hai use — asal mein, pradarshan ke roop mein nahi — ashirwad dene ka kya matlab hoga, aur yeh aap mein kya mukt karega?"},

{"themes":["jealousy"],"type":"spiritual","depth":3,"emotions":["envy","existential","shame"],"concepts":["svadharma","ego","witness-self"],
"en":"What if envy arises because some part of you knows what it is capable of — but has not yet trusted itself enough to move toward it?",
"hi":"क्या हो यदि ईर्ष्या इसलिए उठती है क्योंकि आपका कोई हिस्सा जानता है कि वह क्या करने में सक्षम है — लेकिन अभी तक इसकी ओर बढ़ने के लिए खुद पर पर्याप्त भरोसा नहीं किया?",
"hinglish":"Kya ho agar irshya isliye uthti hai kyunki aapka koi hissa jaanta hai ki woh kya karne mein saksham hai — lekin abhi tak iski taraf badhne ke liye khud par paryaapt bharosa nahi kiya?"},

# ── GRIEF – action_oriented & spiritual ─────────────────────────────────────
{"themes":["grief"],"type":"action_oriented","depth":1,"emotions":["grief","exhaustion"],"concepts":["karma","impermanence"],
"en":"What would it mean to give yourself permission to grieve — not to wallow, but to actually feel what is here without rushing past it?",
"hi":"खुद को शोक मनाने की अनुमति देने का क्या अर्थ होगा — डूबने के लिए नहीं, बल्कि जो यहाँ है उसे बिना जल्दी आगे बढ़े महसूस करना?",
"hinglish":"Khud ko shok manaane ki anumati dene ka kya matlab hoga — doobne ke liye nahi, balki jo yahan hai use bina jaldi aage badhe mahsoos karna?"},

{"themes":["grief"],"type":"action_oriented","depth":2,"emotions":["grief","isolation"],"concepts":["karma","equanimity"],
"en":"Who could you let close enough to witness this grief — not to fix it, just to sit with it alongside you?",
"hi":"आप किसे इतना करीब आने दे सकते हैं कि वे इस दुख के साक्षी बन सकें — इसे ठीक करने के लिए नहीं, बस आपके साथ इसके साथ बैठने के लिए?",
"hinglish":"Aap kise itna kareeb aane de sakte hain ki woh is dard ke saakshi ban sakein — ise theek karne ke liye nahi, bas aapke saath iske saath baithne ke liye?"},

{"themes":["grief"],"type":"action_oriented","depth":3,"emotions":["grief","exhaustion","longing"],"concepts":["karma","dharma","impermanence"],
"en":"What small act today could honour what you have lost — not to move on from it, but to carry it forward with care?",
"hi":"आज एक छोटा कार्य जो आपने जो खोया उसका सम्मान कर सके — उससे आगे बढ़ने के लिए नहीं, बल्कि उसे देखभाल के साथ आगे ले जाने के लिए?",
"hinglish":"Aaj ek chhota kaam jo aapne jo khoya uska samman kar sake — us se aage badhne ke liye nahi, balki use dekhbhaal ke saath aage le jaane ke liye?"},

{"themes":["grief"],"type":"spiritual","depth":1,"emotions":["grief","longing"],"concepts":["impermanence","equanimity"],
"en":"What if grief is love that has nowhere left to go — and what would it mean to let that love continue, even without its object?",
"hi":"क्या हो यदि दुख वह प्रेम है जिसके जाने की अब कोई जगह नहीं है — और उस प्रेम को जारी रहने देने का क्या अर्थ होगा, भले ही उसकी वस्तु न हो?",
"hinglish":"Kya ho agar dard woh prem hai jiske jaane ki ab koi jagah nahi hai — aur us prem ko jaari rehne dene ka kya matlab hoga, chahe uski vastu na ho?"},

{"themes":["grief"],"type":"spiritual","depth":3,"emotions":["grief","existential","longing"],"concepts":["impermanence","witness-self","surrender"],
"en":"The self that grieves and the self that is grieved — are they both temporary, and what watches them both without grief?",
"hi":"जो स्वयं दुख उठाता है और जिस स्वयं का दुख उठाया जाता है — क्या वे दोनों अस्थायी हैं, और उन दोनों को बिना दुख के कौन देखता है?",
"hinglish":"Jo khud dukh uthata hai aur jis khud ka dukh uthaya jaata hai — kya woh dono asthaayi hain, aur unhe dono ko bina dukh ke kaun dekhta hai?"},

# ── FAILURE – action_oriented & spiritual ────────────────────────────────────
{"themes":["failure"],"type":"action_oriented","depth":1,"emotions":["shame","paralysis"],"concepts":["karma"],
"en":"What is one question this failure is answering for you — something you needed to know that you could only learn this way?",
"hi":"यह विफलता आपके लिए एक प्रश्न का उत्तर दे रही है — कुछ ऐसा जो आपको जानना था जो आप केवल इस तरह से सीख सकते थे?",
"hinglish":"Yeh vifalta aapke liye ek sawaal ka jawaab de rahi hai — kuch aisa jo aapko jaanna tha jo aap sirf is tarah se seekh sakte the?"},

{"themes":["failure"],"type":"action_oriented","depth":2,"emotions":["shame","resistance"],"concepts":["karma","detachment","svadharma"],
"en":"What piece of this failure is actually yours to own — not to punish yourself with, but to learn from cleanly?",
"hi":"इस विफलता का कौन-सा हिस्सा वास्तव में आपका है स्वीकार करने के लिए — खुद को दंड देने के लिए नहीं, बल्कि स्पष्टता से सीखने के लिए?",
"hinglish":"Is vifalta ka kaun sa hissa asal mein aapka hai sweekar karne ke liye — khud ko dand dene ke liye nahi, balki spashtata se seekhne ke liye?"},

{"themes":["failure"],"type":"action_oriented","depth":3,"emotions":["shame","grief","fear"],"concepts":["karma","detachment","dharma"],
"en":"What would you attempt next if you trusted that failure was a step in the process rather than a verdict on your worth?",
"hi":"आप आगे क्या करने की कोशिश करेंगे यदि आप विश्वास करते कि विफलता आपके मूल्य पर फैसला नहीं बल्कि प्रक्रिया का एक कदम है?",
"hinglish":"Aap aage kya karne ki koshish karenge agar aap vishwas karte ki vifalta aapke mulya par faisla nahi balki prakriya ka ek kadam hai?"},

{"themes":["failure"],"type":"spiritual","depth":1,"emotions":["shame","grief"],"concepts":["karma","equanimity"],
"en":"What if this failure was not a mistake to fix but a course correction — pointing you somewhere truer than where you were heading?",
"hi":"क्या हो यदि यह विफलता ठीक करने की गलती नहीं थी बल्कि एक दिशा-सुधार थी — आपको कहीं अधिक सच्चे स्थान की ओर इशारा कर रही थी?",
"hinglish":"Kya ho agar yeh vifalta theek karne ki galti nahi thi balki ek disha-sudhar thi — aapko kahi zyada sachche sthan ki taraf ishara kar rahi thi?"},

{"themes":["failure"],"type":"spiritual","depth":2,"emotions":["shame","grief","resistance"],"concepts":["karma","detachment","equanimity"],
"en":"What would equanimity in the face of this failure look like — not indifference, but steadiness that allows you to see it clearly?",
"hi":"इस विफलता के सामने समभाव कैसा दिखेगा — उदासीनता नहीं, बल्कि वह स्थिरता जो आपको इसे स्पष्ट रूप से देखने देती है?",
"hinglish":"Is vifalta ke saamne saambhaav kaisa dikhega — udaasinta nahi, balki woh sthirata jo aapko ise spashtata se dekhne deti hai?"},

{"themes":["failure"],"type":"spiritual","depth":3,"emotions":["shame","existential","grief"],"concepts":["karma","detachment","witness-self"],
"en":"If the soul is learning through this life and failure is part of how it learns — what specifically is yours being taught right now?",
"hi":"यदि आत्मा इस जीवन के माध्यम से सीख रही है और विफलता उसके सीखने के तरीके का हिस्सा है — तो आपकी आत्मा को अभी विशेष रूप से क्या सिखाया जा रहा है?",
"hinglish":"Agar aatma is jeevan ke zariye seekh rahi hai aur vifalta uske seekhne ke tarike ka hissa hai — toh aapki aatma ko abhi khaas taur par kya sikhaya ja raha hai?"},

# ── SUCCESS – action_oriented & spiritual ────────────────────────────────────
{"themes":["success"],"type":"action_oriented","depth":1,"emotions":["emptiness","restlessness"],"concepts":["karma","svadharma"],
"en":"What would you measure your day by — other than achievement — that would actually feel meaningful?",
"hi":"आप अपने दिन को — उपलब्धि के अलावा — किससे मापेंगे जो वास्तव में अर्थपूर्ण लगे?",
"hinglish":"Aap apne din ko — uplabdhi ke alaawa — kisse maapenge jo asal mein arthapoorn lage?"},

{"themes":["success"],"type":"action_oriented","depth":2,"emotions":["emptiness","anxiety","pride"],"concepts":["karma","detachment","svadharma"],
"en":"What would you do with your time and energy if you were not trying to become more successful — but simply to be fully present in what is already here?",
"hi":"यदि आप अधिक सफल बनने की कोशिश नहीं कर रहे थे — बल्कि केवल जो पहले से यहाँ है उसमें पूरी तरह उपस्थित रहने की — तो आप अपने समय और ऊर्जा के साथ क्या करेंगे?",
"hinglish":"Agar aap zyada safal banne ki koshish nahi kar rahe the — balki sirf jo pehle se yahan hai us mein poori tarah maujood rehne ki — toh aap apne samay aur urja ke saath kya karenge?"},

{"themes":["success"],"type":"action_oriented","depth":3,"emotions":["emptiness","existential","restlessness"],"concepts":["karma","dharma","detachment","svadharma"],
"en":"What contribution — to something beyond your own progress — is available to you right now, and are you offering it?",
"hi":"क्या योगदान — आपकी अपनी प्रगति से परे कुछ में — अभी आपके लिए उपलब्ध है, और क्या आप इसे दे रहे हैं?",
"hinglish":"Kya yogdaan — aapki apni pragati se pare kuch mein — abhi aapke liye uplabdh hai, aur kya aap ise de rahe hain?"},

{"themes":["success"],"type":"spiritual","depth":1,"emotions":["emptiness","pride"],"concepts":["desire","detachment","karma"],
"en":"What if the fullness you are searching for through success is not found at the end of the road — but available now, beneath the searching?",
"hi":"क्या हो यदि जो पूर्णता आप सफलता के माध्यम से ढूंढ रहे हैं वह रास्ते के अंत में नहीं मिलती — बल्कि अभी उपलब्ध है, खोज के नीचे?",
"hinglish":"Kya ho agar jo purnata aap safalta ke zariye dhundh rahe hain woh raaste ke ant mein nahi milti — balki abhi uplabdh hai, khoj ke neeche?"},

{"themes":["success"],"type":"spiritual","depth":2,"emotions":["emptiness","pride"],"concepts":["desire","detachment","karma","ego"],
"en":"What would you call success if the people who matter most to you — not to impress but to love — were the only judges?",
"hi":"यदि जो लोग आपके लिए सबसे अधिक मायने रखते हैं — प्रभावित करने के लिए नहीं बल्कि प्यार करने के लिए — एकमात्र न्यायाधीश हों, तो आप सफलता को क्या कहेंगे?",
"hinglish":"Agar jo log aapke liye sabse zyada mayne rakhte hain — prabhavit karne ke liye nahi balki pyar karne ke liye — ekmaatr nyayadhish hon, toh aap safalta ko kya kahenge?"},

{"themes":["success"],"type":"spiritual","depth":3,"emotions":["emptiness","existential","pride"],"concepts":["desire","ego","witness-self","detachment"],
"en":"If the witness in you watched your entire pursuit of success — what would it say about what you were really looking for?",
"hi":"यदि आपमें का साक्षी आपकी सफलता की पूरी खोज को देखे — तो वह क्या कहेगा कि आप वास्तव में क्या ढूंढ रहे थे?",
"hinglish":"Agar aap mein ka saakshi aapki safalta ki poori khoj ko dekhe — toh woh kya kahega ki aap asal mein kya dhundh rahe the?"},

# ── MONEY – action_oriented & spiritual ──────────────────────────────────────
{"themes":["money"],"type":"action_oriented","depth":1,"emotions":["anxiety","avoidance"],"concepts":["karma","dharma"],
"en":"What is one honest step you could take toward financial clarity today — not fixing everything, just opening one window?",
"hi":"वित्तीय स्पष्टता की ओर एक ईमानदार कदम जो आप आज उठा सकते हैं — सब कुछ ठीक करने के लिए नहीं, बस एक खिड़की खोलने के लिए?",
"hinglish":"Vitteey spashtata ki taraf ek imaandaar kadam jo aap aaj utha sakte hain — sab kuch theek karne ke liye nahi, bas ek khidki kholne ke liye?"},

{"themes":["money"],"type":"action_oriented","depth":2,"emotions":["anxiety","shame"],"concepts":["karma","dharma","discipline"],
"en":"What financial choice have you been avoiding because it would require you to admit something about your situation — and what would it mean to make it anyway?",
"hi":"कौन-सा वित्तीय निर्णय आप इसलिए टाल रहे हैं क्योंकि इसके लिए आपकी स्थिति के बारे में कुछ स्वीकार करना होगा — और फिर भी इसे करने का क्या अर्थ होगा?",
"hinglish":"Kaun sa vitteey nirnay aap isliye taal rahe hain kyunki iske liye aapki sthiti ke baare mein kuch sweekar karna hoga — aur phir bhi ise karne ka kya matlab hoga?"},

{"themes":["money"],"type":"action_oriented","depth":3,"emotions":["anxiety","shame","resentment"],"concepts":["karma","dharma","detachment"],
"en":"If money were a form of energy to be used wisely — not hoarded, not feared — what would it ask you to change about how you handle it?",
"hi":"यदि धन जमाखोरी नहीं, डरने की नहीं — बल्कि बुद्धिमानी से उपयोग की जाने वाली ऊर्जा हो — तो यह आपसे इसे संभालने के तरीके में क्या बदलने के लिए कहेगा?",
"hinglish":"Agar dhan jamaakhori nahi, darne ki nahi — balki samajhdaari se upyog ki jaane wali urja ho — toh yeh aapse ise sambhaalne ke tarike mein kya badalne ke liye kahega?"},

{"themes":["money"],"type":"spiritual","depth":1,"emotions":["anxiety","longing"],"concepts":["desire","attachment","karma"],
"en":"What does money represent to the deepest part of you — and is that thing actually available without it?",
"hi":"धन आपके सबसे गहरे हिस्से के लिए क्या दर्शाता है — और क्या वह चीज़ वास्तव में इसके बिना उपलब्ध है?",
"hinglish":"Dhan aapke sabse gehre hisse ke liye kya darshata hai — aur kya woh cheez asal mein iske bina uplabdh hai?"},

{"themes":["money"],"type":"spiritual","depth":2,"emotions":["anxiety","shame"],"concepts":["desire","attachment","detachment","karma"],
"en":"What would generosity look like in your relationship with money — not as sacrifice, but as an expression of trust that there is enough?",
"hi":"धन के साथ आपके संबंध में उदारता कैसी दिखेगी — बलिदान के रूप में नहीं, बल्कि इस विश्वास के प्रकटन के रूप में कि पर्याप्त है?",
"hinglish":"Dhan ke saath aapke rishte mein udaarta kaisi dikhegi — balidaan ke roop mein nahi, balki is vishwas ke prakat ke roop mein ki paryaapt hai?"},

{"themes":["money"],"type":"spiritual","depth":3,"emotions":["anxiety","existential","longing"],"concepts":["desire","ego","detachment","witness-self"],
"en":"What would your relationship with money look like if you truly believed that your security comes from within — not from a number in an account?",
"hi":"यदि आप सच में मानते कि आपकी सुरक्षा भीतर से आती है — किसी खाते की संख्या से नहीं — तो धन के साथ आपका संबंध कैसा दिखेगा?",
"hinglish":"Agar aap sach mein maante ki aapki suraksha andar se aati hai — kisi khaate ki sankhya se nahi — toh dhan ke saath aapka rishta kaisa dikhega?"},

# ── PURPOSE – action_oriented & spiritual ────────────────────────────────────
{"themes":["purpose"],"type":"action_oriented","depth":2,"emotions":["emptiness","confusion"],"concepts":["karma","svadharma","dharma"],
"en":"What skill or gift do you consistently undervalue in yourself — and how could you put it in service of something today?",
"hi":"कौन-सा कौशल या उपहार आप अपने आप में लगातार कम आँकते हैं — और आज आप इसे किसी चीज़ की सेवा में कैसे लगा सकते हैं?",
"hinglish":"Kaun sa kaushal ya uphaar aap apne aap mein lagaatar kam aankte hain — aur aaj aap ise kisi cheez ki seva mein kaise laga sakte hain?"},

{"themes":["purpose"],"type":"action_oriented","depth":3,"emotions":["emptiness","grief","restlessness"],"concepts":["karma","svadharma","dharma","detachment"],
"en":"What would your next year look like if it were organized around what feels most alive in you — rather than what looks most responsible to others?",
"hi":"यदि आपका अगला वर्ष उसके इर्द-गिर्द व्यवस्थित हो जो आपमें सबसे अधिक जीवंत महसूस होता है — दूसरों को जो सबसे अधिक ज़िम्मेदार लगता है उसके बजाय — तो यह कैसा दिखेगा?",
"hinglish":"Agar aapka agla saal us ke ird-gird vyavasthit ho jo aap mein sabse zyada jeevant mahsoos hota hai — doosron ko jo sabse zyada zimmedaar lagta hai uski bajaay — toh yeh kaisa dikhega?"},

{"themes":["purpose"],"type":"spiritual","depth":1,"emotions":["emptiness","longing"],"concepts":["svadharma","dharma","karma"],
"en":"What would it feel like to offer what you do today — your work, your presence, your attention — as an act of devotion rather than performance?",
"hi":"आज जो करते हैं — आपका काम, आपकी उपस्थिति, आपका ध्यान — उसे प्रदर्शन की बजाय भक्ति के कार्य के रूप में अर्पित करना कैसा लगेगा?",
"hinglish":"Aaj jo karte hain — aapka kaam, aapki upasthiti, aapka dhyan — use pradarshan ki bajaay bhakti ke kaam ke roop mein arpit karna kaisa lagega?"},

{"themes":["purpose"],"type":"spiritual","depth":2,"emotions":["emptiness","longing"],"concepts":["svadharma","dharma","surrender"],
"en":"What if your purpose is not a destination to reach but a quality of aliveness to inhabit — and it is available to you in this very moment?",
"hi":"क्या हो यदि आपका उद्देश्य पहुँचने का कोई गंतव्य नहीं है बल्कि जीवंतता की एक गुणवत्ता है जिसमें रहना है — और यह इसी क्षण आपके लिए उपलब्ध है?",
"hinglish":"Kya ho agar aapka uddeshya pahunchne ka koi gantavya nahi hai balki jeevanta ki ek gunwatta hai jis mein rehna hai — aur yeh isi pal aapke liye uplabdh hai?"},

{"themes":["purpose"],"type":"spiritual","depth":3,"emotions":["emptiness","existential","longing"],"concepts":["svadharma","dharma","ego","witness-self"],
"en":"What if you already are what you are seeking to become — and the work of purpose is not acquisition but recognition?",
"hi":"क्या हो यदि आप पहले से ही वही हैं जो आप बनना चाहते हैं — और उद्देश्य का काम अर्जन नहीं बल्कि पहचान है?",
"hinglish":"Kya ho agar aap pehle se hi wahi hain jo aap banna chahte hain — aur uddeshya ka kaam arjan nahi balki pahchan hai?"},

# ── DUTY – action_oriented & spiritual ───────────────────────────────────────
{"themes":["duty"],"type":"action_oriented","depth":1,"emotions":["reluctance","avoidance"],"concepts":["karma","dharma"],
"en":"What duty are you performing out of resentment rather than care — and what would shift if you chose to bring care to it anyway?",
"hi":"कौन-सा कर्तव्य आप देखभाल की जगह नाराज़गी से निभा रहे हैं — और यदि आप फिर भी उसमें देखभाल लाने का चुनाव करें तो क्या बदलेगा?",
"hinglish":"Kaun sa kartavya aap dekhbhaal ki jagah naraazgi se nibhaa rahe hain — aur agar aap phir bhi us mein dekhbhaal laane ka chunaav karein toh kya badlega?"},

{"themes":["duty"],"type":"action_oriented","depth":3,"emotions":["confusion","resentment"],"concepts":["karma","svadharma","detachment"],
"en":"What would it mean to fulfill this duty with your whole self — not to be consumed by it, but to bring genuine presence to it?",
"hi":"इस कर्तव्य को अपने पूरे स्वयं के साथ निभाने का क्या अर्थ होगा — इसमें खो जाने के लिए नहीं, बल्कि इसमें वास्तविक उपस्थिति लाने के लिए?",
"hinglish":"Is kartavya ko apne poore khud ke saath nibhaane ka kya matlab hoga — ismein kho jaane ke liye nahi, balki ismein asli upasthiti laane ke liye?"},

{"themes":["duty"],"type":"spiritual","depth":1,"emotions":["confusion","burden"],"concepts":["dharma","svadharma"],
"en":"What would it feel like to perform this duty as an offering — not because you have to, but because it is how you choose to meet this moment?",
"hi":"इस कर्तव्य को अर्पण के रूप में निभाना कैसा लगेगा — इसलिए नहीं कि आपको करना है, बल्कि इसलिए कि यह वह तरीका है जिससे आप इस क्षण का सामना करने का चुनाव करते हैं?",
"hinglish":"Is kartavya ko arpan ke roop mein nibhaana kaisa lagega — isliye nahi ki aapko karna hai, balki isliye ki yeh woh tarika hai jisse aap is pal ka saamna karne ka chunaav karte hain?"},

{"themes":["duty"],"type":"spiritual","depth":2,"emotions":["reluctance","resentment"],"concepts":["karma","dharma","detachment"],
"en":"What does your resistance to this duty teach you about what you are still attached to — and what would non-attachment actually look like here?",
"hi":"इस कर्तव्य के प्रति आपका प्रतिरोध आपको सिखाता है कि आप अभी भी किससे जुड़े हुए हैं — और यहाँ अनासक्ति वास्तव में कैसी दिखेगी?",
"hinglish":"Is kartavya ke prati aapka pratiroadh aapko sikhata hai ki aap abhi bhi kisse jude hue hain — aur yahan anaasakt hona asal mein kaisa dikhega?"},

{"themes":["duty"],"type":"spiritual","depth":3,"emotions":["confusion","existential"],"concepts":["svadharma","dharma","karma","surrender"],
"en":"If this duty asked you to become something — more patient, more present, more selfless — what would the doing of it make you into?",
"hi":"यदि यह कर्तव्य आपसे कुछ बनने के लिए कहे — अधिक धैर्यवान, अधिक उपस्थित, अधिक निःस्वार्थ — तो इसे करना आपको क्या बना देगा?",
"hinglish":"Agar yeh kartavya aapse kuch banne ke liye kahe — zyada dhairyavaan, zyada upasthit, zyada nihsvaarthi — toh ise karna aapko kya bana dega?"},

# ── DISCIPLINE – action_oriented & spiritual ─────────────────────────────────
{"themes":["discipline"],"type":"action_oriented","depth":1,"emotions":["inertia","avoidance"],"concepts":["karma"],
"en":"What is the one practice that, if you did it consistently for the next 30 days, would change something meaningful?",
"hi":"एक अभ्यास जो, यदि आप इसे अगले 30 दिनों तक लगातार करें, तो कुछ सार्थक बदल देगा?",
"hinglish":"Ek abhyas jo, agar aap ise agle 30 dinon tak lagaatar karein, toh kuch saarthak badal dega?"},

{"themes":["discipline"],"type":"action_oriented","depth":2,"emotions":["resistance","inertia"],"concepts":["karma","svadharma"],
"en":"What environment or condition makes your discipline most sustainable — and are you creating that condition for yourself?",
"hi":"कौन-सा परिवेश या स्थिति आपके अनुशासन को सबसे अधिक टिकाऊ बनाती है — और क्या आप अपने लिए वह स्थिति बना रहे हैं?",
"hinglish":"Kaun sa parivesh ya sthiti aapke anushasan ko sabse zyada tikaau banati hai — aur kya aap apne liye woh sthiti bana rahe hain?"},

{"themes":["discipline"],"type":"action_oriented","depth":3,"emotions":["resistance","shame"],"concepts":["karma","dharma","detachment"],
"en":"What would it mean to build your practice around identity — 'I am someone who does this' — rather than willpower?",
"hi":"अपने अभ्यास को पहचान के इर्द-गिर्द बनाने का क्या अर्थ होगा — 'मैं कोई ऐसा हूँ जो यह करता है' — इच्छाशक्ति की जगह?",
"hinglish":"Apne abhyas ko pahchan ke ird-gird banane ka kya matlab hoga — 'Main koi aisa hun jo yeh karta hai' — ichchhashakti ki jagah?"},

{"themes":["discipline"],"type":"spiritual","depth":1,"emotions":["inertia","guilt"],"concepts":["karma","tamas"],
"en":"What would it mean to begin your practice today not with effort but with willingness — to show up open rather than braced?",
"hi":"आज अपने अभ्यास को प्रयास से नहीं बल्कि तत्परता से शुरू करने का क्या अर्थ होगा — तैयार होकर नहीं, खुले दिल से आना?",
"hinglish":"Aaj apne abhyas ko prayas se nahi balki tatparta se shuru karne ka kya matlab hoga — taiyar hokar nahi, khule dil se aana?"},

{"themes":["discipline"],"type":"spiritual","depth":2,"emotions":["resistance","inertia"],"concepts":["karma","tamas","dharma"],
"en":"What would your practice become if you offered it — not as self-improvement, not as obligation, but as gratitude for the life you have been given?",
"hi":"यदि आप अपने अभ्यास को — स्व-सुधार के रूप में नहीं, दायित्व के रूप में नहीं, बल्कि आपको मिले जीवन के लिए कृतज्ञता के रूप में — अर्पित करें, तो यह क्या बन जाएगा?",
"hinglish":"Agar aap apne abhyas ko — swa-sudhar ke roop mein nahi, dayitva ke roop mein nahi, balki aapko mile jeevan ke liye kritagyata ke roop mein — arpit karein, toh yeh kya ban jaayega?"},

{"themes":["discipline"],"type":"spiritual","depth":3,"emotions":["inertia","shame","existential"],"concepts":["karma","dharma","witness-self"],
"en":"What would it mean to be the kind of person who shows up for what matters — not because it is easy, but because that is who you have decided to be?",
"hi":"उस व्यक्ति होने का क्या अर्थ होगा जो जो मायने रखता है उसके लिए उपस्थित होता है — इसलिए नहीं कि यह आसान है, बल्कि इसलिए कि आपने यही बनने का निर्णय लिया है?",
"hinglish":"Us insaan hone ka kya matlab hoga jo jo mayne rakhta hai uske liye maujood hota hai — isliye nahi ki yeh aasaan hai, balki isliye ki aapne yahi banne ka nirnay liya hai?"},

# ── LAZINESS – action_oriented & spiritual ───────────────────────────────────
{"themes":["laziness"],"type":"action_oriented","depth":1,"emotions":["guilt","inertia"],"concepts":["karma"],
"en":"What would happen if you began the thing you have been putting off — right now, for just two minutes?",
"hi":"क्या होगा यदि आप उस काम को शुरू करें जो टाल रहे हैं — अभी, बस दो मिनट के लिए?",
"hinglish":"Kya hoga agar aap us kaam ko shuru karein jo taal rahe hain — abhi, bas do minute ke liye?"},

{"themes":["laziness"],"type":"action_oriented","depth":2,"emotions":["inertia","resistance"],"concepts":["karma","discipline"],
"en":"What obstacle — internal or practical — most reliably stops you from beginning, and what would happen if you removed just that one thing?",
"hi":"कौन-सी बाधा — आंतरिक या व्यावहारिक — आपको शुरू करने से सबसे अधिक भरोसेमंद ढंग से रोकती है, और यदि आप केवल उस एक चीज़ को हटा दें तो क्या होगा?",
"hinglish":"Kaun si badha — aantarik ya vyavahaarik — aapko shuru karne se sabse zyada bharoseamanad dhang se rokti hai, aur agar aap sirf us ek cheez ko hataa dein toh kya hoga?"},

{"themes":["laziness"],"type":"action_oriented","depth":3,"emotions":["shame","guilt","inertia"],"concepts":["karma","dharma","discipline"],
"en":"What would it mean to commit — fully, without waiting to feel motivated — and what would be the first act of that commitment?",
"hi":"प्रेरित होने का इंतज़ार किए बिना — पूरी तरह — प्रतिबद्ध होने का क्या अर्थ होगा, और उस प्रतिबद्धता का पहला कार्य क्या होगा?",
"hinglish":"Prerit hone ka intezaar kiye bina — poori tarah — pratibaddh hone ka kya matlab hoga, aur us pratibaddhata ka pehla kaam kya hoga?"},

{"themes":["laziness"],"type":"spiritual","depth":1,"emotions":["guilt","inertia"],"concepts":["tamas","karma"],
"en":"What would it mean to meet this heaviness with kindness rather than judgment — and then, gently, to begin anyway?",
"hi":"इस भारीपन को निर्णय की जगह दयालुता से मिलने का क्या अर्थ होगा — और फिर, धीरे से, फिर भी शुरू करना?",
"hinglish":"Is bhaariapan ko nirnay ki jagah dayaluta se milne ka kya matlab hoga — aur phir, dheere se, phir bhi shuru karna?"},

{"themes":["laziness"],"type":"spiritual","depth":2,"emotions":["inertia","guilt"],"concepts":["tamas","karma","dharma"],
"en":"If you offered this day — your movement, your effort, your presence — as an act of honour for the consciousness you have been given, how would you spend it?",
"hi":"यदि आप इस दिन को — अपनी गति, अपने प्रयास, अपनी उपस्थिति को — उस चेतना के सम्मान के कार्य के रूप में अर्पित करें जो आपको दी गई है, तो आप इसे कैसे बिताएंगे?",
"hinglish":"Agar aap is din ko — apni gati, apne prayas, apni upasthiti ko — us chetna ke samman ke kaam ke roop mein arpit karein jo aapko di gayi hai, toh aap ise kaise bitaayenge?"},

{"themes":["laziness"],"type":"spiritual","depth":3,"emotions":["shame","inertia","existential"],"concepts":["tamas","karma","dharma","witness-self"],
"en":"What would the witness in you — the one that watches without judgment — say about the choices you are making with your time and energy right now?",
"hi":"आपमें का साक्षी — जो बिना निर्णय के देखता है — अभी आपके समय और ऊर्जा के साथ किए जाने वाले चुनावों के बारे में क्या कहेगा?",
"hinglish":"Aap mein ka saakshi — jo bina nirnay ke dekhta hai — abhi aapke samay aur urja ke saath kiye jaane wale chunaavon ke baare mein kya kahega?"},

# ── RELATIONSHIPS – action_oriented & spiritual ───────────────────────────────
{"themes":["relationships"],"type":"action_oriented","depth":1,"emotions":["longing","frustration"],"concepts":["karma","dharma"],
"en":"What is one thing you could do today to genuinely invest in a relationship that matters to you — without needing anything back?",
"hi":"आज एक चीज़ जो आप किसी महत्वपूर्ण संबंध में वास्तव में निवेश करने के लिए कर सकते हैं — बिना कुछ वापस माँगे?",
"hinglish":"Aaj ek cheez jo aap kisi mahatvapurna rishte mein asal mein nivesh karne ke liye kar sakte hain — bina kuch wapas maange?"},

{"themes":["relationships"],"type":"action_oriented","depth":2,"emotions":["resentment","resistance"],"concepts":["karma","svadharma"],
"en":"What have you been withholding in this relationship — your truth, your care, your full presence — and why?",
"hi":"इस संबंध में आप क्या रोक रहे हैं — आपकी सच्चाई, आपकी देखभाल, आपकी पूर्ण उपस्थिति — और क्यों?",
"hinglish":"Is rishte mein aap kya rok rahe hain — aapki sachchai, aapki dekhbhaal, aapki poori upasthiti — aur kyun?"},

{"themes":["relationships"],"type":"action_oriented","depth":3,"emotions":["grief","resentment","longing"],"concepts":["karma","dharma","detachment"],
"en":"What would it mean to show up fully for one important relationship this week — without agenda, without managing it, without needing it to be different?",
"hi":"इस सप्ताह एक महत्वपूर्ण संबंध के लिए पूरी तरह उपस्थित होने का क्या अर्थ होगा — बिना एजेंडे के, बिना इसे प्रबंधित किए, बिना इसे अलग होने की ज़रूरत के?",
"hinglish":"Is hafte ek mahatvapurna rishte ke liye poori tarah maujood hone ka kya matlab hoga — bina agenda ke, bina ise manage kiye, bina ise alag hone ki zaroorat ke?"},

{"themes":["relationships"],"type":"spiritual","depth":1,"emotions":["longing","frustration"],"concepts":["karma","dharma","attachment"],
"en":"What would it mean to see the other person in this relationship as a soul on their own journey — rather than as a character in yours?",
"hi":"इस संबंध में दूसरे व्यक्ति को अपनी यात्रा पर एक आत्मा के रूप में देखने का क्या अर्थ होगा — आपकी यात्रा के एक पात्र के रूप में नहीं?",
"hinglish":"Is rishte mein doosre insaan ko apni yatra par ek aatma ke roop mein dekhne ka kya matlab hoga — aapki yatra ke ek paatra ke roop mein nahi?"},

{"themes":["relationships"],"type":"spiritual","depth":2,"emotions":["resentment","longing"],"concepts":["karma","ego","attachment"],
"en":"What does this relationship ask of your spiritual practice — patience, humility, acceptance, honesty — and are you bringing it?",
"hi":"यह संबंध आपकी आध्यात्मिक साधना से क्या माँगता है — धैर्य, विनम्रता, स्वीकृति, ईमानदारी — और क्या आप इसे ला रहे हैं?",
"hinglish":"Yeh rishta aapki aadhyatmik sadhna se kya maangta hai — dhairya, vinamrata, sweekriti, imaandaari — aur kya aap ise la rahe hain?"},

{"themes":["relationships"],"type":"spiritual","depth":3,"emotions":["grief","longing","existential"],"concepts":["karma","attachment","ego","witness-self"],
"en":"If love is ultimately not about what you receive but about what you become through the giving — what are you becoming through this relationship?",
"hi":"यदि प्रेम अंततः आप जो पाते हैं उस बारे में नहीं है बल्कि आप देने के माध्यम से क्या बनते हैं उस बारे में है — तो आप इस संबंध के माध्यम से क्या बन रहे हैं?",
"hinglish":"Agar prem aakhirkar aap jo paate hain us baare mein nahi hai balki aap dene ke zariye kya bante hain us baare mein hai — toh aap is rishte ke zariye kya ban rahe hain?"},

# ── PARENTING – action_oriented & spiritual ───────────────────────────────────
{"themes":["parenting"],"type":"action_oriented","depth":1,"emotions":["guilt","anxiety"],"concepts":["karma","dharma"],
"en":"What would it look like to be fully present with your child today — just for 20 minutes, with no agenda and no phone?",
"hi":"आज अपने बच्चे के साथ पूरी तरह उपस्थित होना कैसा दिखेगा — बस 20 मिनट के लिए, बिना किसी एजेंडे और फ़ोन के?",
"hinglish":"Aaj apne bachche ke saath poori tarah maujood hona kaisa dikhega — bas 20 minute ke liye, bina kisi agenda aur phone ke?"},

{"themes":["parenting"],"type":"action_oriented","depth":2,"emotions":["guilt","anxiety","control"],"concepts":["karma","dharma","detachment"],
"en":"What conversation could you have with your child that would actually let them know you see them — not your hopes for them, but them?",
"hi":"अपने बच्चे के साथ कौन-सी बातचीत हो सकती है जो उन्हें वास्तव में बताएगी कि आप उन्हें देखते हैं — उनके लिए आपकी आशाएँ नहीं, बल्कि उन्हें?",
"hinglish":"Apne bachche ke saath kaun si baatcheet ho sakti hai jo unhe asal mein bataayegi ki aap unhe dekhte hain — unke liye aapki aahaein nahi, balki unhe?"},

{"themes":["parenting"],"type":"action_oriented","depth":3,"emotions":["grief","anxiety","guilt"],"concepts":["karma","dharma","detachment","surrender"],
"en":"What would it mean to apologize to your child — not to fix it, but to model that repair is possible?",
"hi":"अपने बच्चे से माफ़ी माँगने का क्या अर्थ होगा — इसे ठीक करने के लिए नहीं, बल्कि यह दिखाने के लिए कि मरम्मत संभव है?",
"hinglish":"Apne bachche se maafi maangne ka kya matlab hoga — ise theek karne ke liye nahi, balki yeh dikhane ke liye ki marammat sambhav hai?"},

{"themes":["parenting"],"type":"spiritual","depth":1,"emotions":["anxiety","longing"],"concepts":["dharma","karma","surrender"],
"en":"What would it mean to parent from a place of trust — that your child has their own wisdom and timing — rather than from fear?",
"hi":"विश्वास की जगह से पालन-पोषण करने का क्या अर्थ होगा — कि आपके बच्चे के पास अपनी बुद्धि और समय है — डर से नहीं?",
"hinglish":"Vishwas ki jagah se paalan-poshan karne ka kya matlab hoga — ki aapke bachche ke paas apni buddhi aur samay hai — dar se nahi?"},

{"themes":["parenting"],"type":"spiritual","depth":2,"emotions":["anxiety","grief"],"concepts":["dharma","karma","detachment","surrender"],
"en":"What would it mean to see your love for your child as a form of practice — of devotion, of service — rather than a source of anxiety?",
"hi":"अपने बच्चे के लिए अपने प्रेम को एक साधना के रूप में देखने का क्या अर्थ होगा — भक्ति का, सेवा का — चिंता के स्रोत की जगह?",
"hinglish":"Apne bachche ke liye apne prem ko ek sadhna ke roop mein dekhne ka kya matlab hoga — bhakti ka, seva ka — chinta ke srot ki jagah?"},

{"themes":["parenting"],"type":"spiritual","depth":3,"emotions":["grief","anxiety","existential"],"concepts":["dharma","karma","detachment","surrender","impermanence"],
"en":"What would it mean to release your child into their own life — not abandonment, but the profound act of trusting that they carry within them everything they need?",
"hi":"अपने बच्चे को उनके अपने जीवन में छोड़ने का क्या अर्थ होगा — त्याग नहीं, बल्कि यह विश्वास करने का गहरा कार्य कि वे अपने भीतर जो चाहिए वह सब लेकर चलते हैं?",
"hinglish":"Apne bachche ko unke apne jeevan mein chhodne ka kya matlab hoga — tyaag nahi, balki yeh vishwas karne ka gehra kaam ki woh apne andar jo chahiye woh sab lekar chalte hain?"},

# ── MARRIAGE – action_oriented & spiritual ────────────────────────────────────
{"themes":["marriage"],"type":"action_oriented","depth":1,"emotions":["frustration","longing"],"concepts":["karma","relationships"],
"en":"What is one kind thing you could say to your partner today — not because they deserve it, but because you choose to offer it?",
"hi":"आज अपने साथी से एक दयालु बात जो आप कह सकते हैं — इसलिए नहीं कि वे इसके पात्र हैं, बल्कि इसलिए कि आप इसे देना चुनते हैं?",
"hinglish":"Aaj apne saathi se ek dayaalu baat jo aap keh sakte hain — isliye nahi ki woh iske paatr hain, balki isliye ki aap ise dena chunte hain?"},

{"themes":["marriage"],"type":"action_oriented","depth":2,"emotions":["resentment","resistance"],"concepts":["karma","dharma","detachment"],
"en":"What are you consistently not saying in this marriage that is quietly creating distance — and what would it look like to say it with care?",
"hi":"इस विवाह में आप लगातार क्या नहीं कह रहे जो चुपचाप दूरी बना रहा है — और इसे देखभाल के साथ कहना कैसा दिखेगा?",
"hinglish":"Is vivah mein aap lagaatar kya nahi keh rahe jo chup-chaap doori bana raha hai — aur ise dekhbhaal ke saath kehna kaisa dikhega?"},

{"themes":["marriage"],"type":"action_oriented","depth":3,"emotions":["grief","resentment","longing"],"concepts":["karma","dharma","surrender","detachment"],
"en":"What would it look like to recommit to this marriage — not to the person you married, but to the person they actually are today?",
"hi":"इस विवाह के प्रति पुनः प्रतिबद्ध होना कैसा दिखेगा — उस व्यक्ति के लिए नहीं जिनसे आपने शादी की, बल्कि जो वे आज वास्तव में हैं?",
"hinglish":"Is vivah ke prati punah pratibaddh hona kaisa dikhega — us insaan ke liye nahi jinse aapne shaadi ki, balki jo woh aaj asal mein hain?"},

{"themes":["marriage"],"type":"spiritual","depth":1,"emotions":["frustration","longing"],"concepts":["dharma","relationships","karma"],
"en":"What if this marriage is a form of tapas — a burning that refines you — and what is it currently burning away?",
"hi":"क्या हो यदि यह विवाह तपस का एक रूप है — एक दहन जो आपको परिष्कृत करता है — और यह अभी क्या जला रहा है?",
"hinglish":"Kya ho agar yeh vivah tapas ka ek roop hai — ek dahan jo aapko parishkrit karta hai — aur yeh abhi kya jala raha hai?"},

{"themes":["marriage"],"type":"spiritual","depth":2,"emotions":["resentment","grief"],"concepts":["dharma","karma","ego"],
"en":"Where in this marriage are you still attached to being right — and what would love without that attachment actually look like?",
"hi":"इस विवाह में आप कहाँ अभी भी सही होने से जुड़े हैं — और उस आसक्ति के बिना प्रेम वास्तव में कैसा दिखेगा?",
"hinglish":"Is vivah mein aap kahan abhi bhi sahi hone se jude hain — aur us aasakti ke bina prem asal mein kaisa dikhega?"},

{"themes":["marriage"],"type":"spiritual","depth":3,"emotions":["grief","longing","existential"],"concepts":["dharma","ego","attachment","witness-self"],
"en":"What would marriage look like if it were a joint practice of waking up — using each other's presence as a mirror for what still needs attention in each of you?",
"hi":"विवाह कैसा दिखेगा यदि यह जागरण का एक संयुक्त अभ्यास हो — एक-दूसरे की उपस्थिति को दर्पण के रूप में उपयोग करना उसके लिए जिस पर आप दोनों में से प्रत्येक को अभी भी ध्यान देने की ज़रूरत है?",
"hinglish":"Vivah kaisa dikhega agar yeh jaagran ka ek sanyukt abhyas ho — ek-doosre ki upasthiti ko darpan ke roop mein upyog karna us ke liye jis par aap dono mein se har ek ko abhi bhi dhyan dene ki zaroorat hai?"},

# ── LONELINESS – action_oriented & spiritual ─────────────────────────────────
{"themes":["loneliness"],"type":"action_oriented","depth":1,"emotions":["loneliness","isolation"],"concepts":["karma"],
"en":"What is one way you could offer genuine care to someone today — not to receive connection, but to give it?",
"hi":"आज किसी को वास्तविक देखभाल देने का एक तरीका — जुड़ाव पाने के लिए नहीं, बल्कि देने के लिए?",
"hinglish":"Aaj kisi ko asli dekhbhaal dene ka ek tarika — judav paane ke liye nahi, balki dene ke liye?"},

{"themes":["loneliness"],"type":"action_oriented","depth":2,"emotions":["loneliness","resistance"],"concepts":["karma","svadharma"],
"en":"What makes you most difficult to be close to — and what would it look like to soften that, even slightly, today?",
"hi":"आपके करीब होना सबसे कठिन क्या बनाता है — और आज उसे थोड़ा भी नरम करना कैसा दिखेगा?",
"hinglish":"Aapke kareeb hona sabse mushkil kya banata hai — aur aaj use thoda bhi naram karna kaisa dikhega?"},

{"themes":["loneliness"],"type":"action_oriented","depth":3,"emotions":["loneliness","grief","shame"],"concepts":["karma","dharma","attachment"],
"en":"What would it mean to let someone know the truest version of what you are going through — not to burden them, but because real contact requires real honesty?",
"hi":"किसी को जो आप वास्तव में गुज़र रहे हैं उसका सबसे सच्चा संस्करण बताने का क्या अर्थ होगा — उन्हें बोझ देने के लिए नहीं, बल्कि इसलिए कि वास्तविक संपर्क के लिए वास्तविक ईमानदारी चाहिए?",
"hinglish":"Kisi ko jo aap asal mein guzar rahe hain uska sabse sachcha version batane ka kya matlab hoga — unhe bojh dene ke liye nahi, balki isliye ki asli sampark ke liye asli imaandaari chahiye?"},

{"themes":["loneliness"],"type":"spiritual","depth":2,"emotions":["loneliness","longing"],"concepts":["witness-self","ego","surrender"],
"en":"What if the antidote to loneliness is not more company but a deeper relationship with the awareness that is always here — the one that has never left?",
"hi":"क्या हो यदि एकाकीपन का उपाय अधिक साथ नहीं बल्कि उस चेतना के साथ गहरा संबंध है जो हमेशा यहाँ है — जो कभी नहीं गई?",
"hinglish":"Kya ho agar akalapan ka upaay zyada saath nahi balki us chetna ke saath gehra sambandh hai jo hamesha yahan hai — jo kabhi nahi gayi?"},

{"themes":["loneliness"],"type":"spiritual","depth":3,"emotions":["loneliness","existential","longing"],"concepts":["witness-self","ego","surrender","impermanence"],
"en":"What if the root of loneliness is the experience of being a separate self — and what practices, even briefly, let the edges of that separation soften?",
"hi":"क्या हो यदि एकाकीपन की जड़ एक अलग स्वयं होने का अनुभव है — और कौन-से अभ्यास, भले ही संक्षेप में, उस अलगाव के किनारों को नरम होने देते हैं?",
"hinglish":"Kya ho agar akalapan ki jadd ek alag khud hone ka anubhav hai — aur kaun se abhyas, chahe sankshep mein, us algaav ke kinaron ko naram hone dete hain?"},

# ── SELF_WORTH – action_oriented & spiritual ─────────────────────────────────
{"themes":["self_worth"],"type":"action_oriented","depth":1,"emotions":["inadequacy","shame"],"concepts":["karma","svadharma"],
"en":"What is something you genuinely value about yourself — not what you have achieved, but who you are — that you rarely let yourself hold?",
"hi":"कुछ ऐसा जो आप अपने बारे में वास्तव में मूल्यवान मानते हैं — वह नहीं जो आपने हासिल किया, बल्कि जो आप हैं — जिसे आप शायद ही कभी खुद को थामने देते हैं?",
"hinglish":"Kuch aisa jo aap apne baare mein asal mein mulyavaan maante hain — woh nahi jo aapne haasil kiya, balki jo aap hain — jise aap shaayad hi kabhi khud ko thaamne dete hain?"},

{"themes":["self_worth"],"type":"action_oriented","depth":2,"emotions":["inadequacy","shame","avoidance"],"concepts":["karma","svadharma"],
"en":"What would you do today if you treated yourself with the same patience and care you would offer to someone you love?",
"hi":"यदि आप खुद के साथ उसी धैर्य और देखभाल से व्यवहार करें जो आप किसी प्रिय व्यक्ति को देते हैं — तो आज आप क्या करेंगे?",
"hinglish":"Agar aap khud ke saath usi dhairya aur dekhbhaal se vyavahaar karein jo aap kisi pyare insaan ko dete hain — toh aaj aap kya karenge?"},

{"themes":["self_worth"],"type":"action_oriented","depth":3,"emotions":["shame","inadequacy","resistance"],"concepts":["karma","dharma","witness-self"],
"en":"What would you stop apologizing for — your presence, your needs, your voice — if you truly believed you belonged here?",
"hi":"यदि आप सच में मानते कि आप यहाँ के हैं — तो आप किसके लिए माफ़ी माँगना बंद करेंगे — अपनी उपस्थिति, अपनी ज़रूरतें, अपनी आवाज़?",
"hinglish":"Agar aap sach mein maante ki aap yahan ke hain — toh aap kiske liye maafi maangna band karenge — apni upasthiti, apni zaruraten, apni aawaaz?"},

{"themes":["self_worth"],"type":"spiritual","depth":1,"emotions":["inadequacy","shame"],"concepts":["ego","witness-self"],
"en":"What if your worth is not something you earn or lose — but something you simply are, as unchanging as consciousness itself?",
"hi":"क्या हो यदि आपका मूल्य कुछ ऐसा नहीं है जो आप अर्जित या खोते हैं — बल्कि कुछ ऐसा है जो आप बस हैं, चेतना की तरह ही अपरिवर्तनीय?",
"hinglish":"Kya ho agar aapka mulya kuch aisa nahi hai jo aap arjit ya khoye hain — balki kuch aisa hai jo aap bas hain, chetna ki tarah hi aparivartaniya?"},

{"themes":["self_worth"],"type":"spiritual","depth":2,"emotions":["inadequacy","shame"],"concepts":["ego","witness-self","surrender"],
"en":"What if the part of you that says you are not enough is simply one thought arising in awareness — and awareness itself is never diminished by any thought?",
"hi":"क्या हो यदि आपका वह हिस्सा जो कहता है आप पर्याप्त नहीं हैं — बस चेतना में उठने वाला एक विचार है — और चेतना स्वयं किसी भी विचार से कभी कम नहीं होती?",
"hinglish":"Kya ho agar aapka woh hissa jo kehta hai aap paryaapt nahi hain — bas chetna mein uthne wala ek vichaar hai — aur chetna khud kisi bhi vichaar se kabhi kam nahi hoti?"},

{"themes":["self_worth"],"type":"spiritual","depth":3,"emotions":["shame","inadequacy","existential"],"concepts":["ego","witness-self","surrender","detachment"],
"en":"What if the deepest answer to 'am I enough' is not a thought you can think — but a stillness you can rest in, that was never asking the question?",
"hi":"क्या हो यदि 'क्या मैं पर्याप्त हूँ' का सबसे गहरा उत्तर कोई विचार नहीं है जो आप सोच सकते हैं — बल्कि एक शांति है जिसमें आप विश्राम कर सकते हैं, जो कभी यह सवाल नहीं पूछ रही थी?",
"hinglish":"Kya ho agar 'kya main paryaapt hun' ka sabse gehra jawab koi vichaar nahi hai jo aap soch sakte hain — balki ek shanti hai jis mein aap vishram kar sakte hain, jo kabhi yeh sawaal nahi pooch rahi thi?"},

# ── CONTROL – remaining gaps ──────────────────────────────────────────────────
{"themes":["control"],"type":"action_oriented","depth":1,"emotions":["tension","anxiety"],"concepts":["karma","svadharma"],
"en":"In this situation, what is the single action most fully within your power — and have you taken it yet?",
"hi":"इस स्थिति में, एक कार्य जो सबसे पूरी तरह आपकी शक्ति में है — और क्या आपने इसे अभी तक किया है?",
"hinglish":"Is situation mein, ek kaam jo sabse poori tarah aapki shakti mein hai — aur kya aapne ise abhi tak kiya hai?"},

{"themes":["control"],"type":"action_oriented","depth":3,"emotions":["resistance","grief"],"concepts":["karma","surrender","detachment"],
"en":"What would it look like to fully invest your effort here — and then step back from needing the result to go a particular way?",
"hi":"यहाँ अपना पूरा प्रयास लगाना और फिर परिणाम के किसी विशेष तरीके से जाने की ज़रूरत से पीछे हटना कैसा दिखेगा?",
"hinglish":"Yahan apna poora prayas lagana aur phir natije ke kisi vishesh tarike se jaane ki zaroorat se peeche hatna kaisa dikhega?"},

{"themes":["control"],"type":"spiritual","depth":1,"emotions":["tension","worry"],"concepts":["surrender","karma"],
"en":"What if surrendering control here is not weakness — but a form of wisdom that allows something larger to move through?",
"hi":"क्या हो यदि यहाँ नियंत्रण छोड़ना कमज़ोरी नहीं है — बल्कि एक प्रकार की बुद्धिमत्ता है जो किसी बड़ी चीज़ को आगे बढ़ने देती है?",
"hinglish":"Kya ho agar yahan control chodna kamzori nahi hai — balki ek prakar ki buddhimatta hai jo kisi badi cheez ko aage badhne deti hai?"},

{"themes":["control"],"type":"spiritual","depth":3,"emotions":["existential fear","clinging"],"concepts":["surrender","witness-self","impermanence"],
"en":"What if the one who needs to control is itself the thing that most needs to be seen clearly — as constructed, temporary, and ultimately not in charge?",
"hi":"क्या हो यदि जो नियंत्रित करने की ज़रूरत है वही वह चीज़ है जिसे सबसे अधिक स्पष्ट रूप से देखे जाने की ज़रूरत है — निर्मित, अस्थायी, और अंततः नियंत्रण में नहीं?",
"hinglish":"Kya ho agar jo control karne ki zaroorat hai wahi woh cheez hai jise sabse zyada spashtata se dekhe jaane ki zaroorat hai — nirmit, asthaayi, aur aakhirkar control mein nahi?"},

# ── FORGIVENESS – action_oriented & spiritual ────────────────────────────────
{"themes":["forgiveness"],"type":"action_oriented","depth":1,"emotions":["resentment","hurt"],"concepts":["karma","forgiveness"],
"en":"What would it mean today to simply notice where you are carrying this grievance — in the body, in the mood — without needing to act on it or dismiss it?",
"hi":"आज इसका क्या अर्थ होगा कि बस ध्यान दें कि आप इस शिकायत को कहाँ ले जा रहे हैं — शरीर में, मन में — इस पर कार्य किए बिना या इसे खारिज किए बिना?",
"hinglish":"Aaj iska kya matlab hoga ki bas dhyan dein ki aap is shikaayat ko kahan le ja rahe hain — sharir mein, mann mein — is par kaam kiye bina ya ise khaarij kiye bina?"},

{"themes":["forgiveness"],"type":"action_oriented","depth":2,"emotions":["resentment","resistance"],"concepts":["karma","forgiveness","detachment"],
"en":"What is one thing you could genuinely wish for the person you have not yet forgiven — not as performance, but as a small act of loosening?",
"hi":"एक चीज़ जो आप उस व्यक्ति के लिए वास्तव में चाह सकते हैं जिसे आपने अभी तक माफ नहीं किया — प्रदर्शन के रूप में नहीं, बल्कि ढीला करने के एक छोटे से कार्य के रूप में?",
"hinglish":"Ek cheez jo aap us insaan ke liye asal mein chah sakte hain jise aapne abhi tak maaf nahi kiya — pradarshan ke roop mein nahi, balki dhila karne ke ek chhote se kaam ke roop mein?"},

{"themes":["forgiveness"],"type":"action_oriented","depth":3,"emotions":["resentment","grief","resistance"],"concepts":["karma","forgiveness","dharma"],
"en":"What would it mean to choose not to be defined by what was done to you — and what action today could come from that choice?",
"hi":"आपके साथ जो किया गया उससे परिभाषित न होने का चुनाव करने का क्या अर्थ होगा — और आज उस चुनाव से कौन-सा कार्य हो सकता है?",
"hinglish":"Aapke saath jo kiya gaya us se paribhashit na hone ka chunaav karne ka kya matlab hoga — aur aaj us chunaav se kaun sa kaam ho sakta hai?"},

{"themes":["forgiveness"],"type":"spiritual","depth":1,"emotions":["resentment","longing"],"concepts":["forgiveness","karma","surrender"],
"en":"What if holding this grievance is costing you more than it is costing them — and forgiveness is simply choosing to stop paying that price?",
"hi":"क्या हो यदि इस शिकायत को थामे रखना उन्हें जितनी कीमत चुका रहा है उससे अधिक आपको चुका रहा है — और क्षमा बस उस कीमत को चुकाना बंद करने का चुनाव है?",
"hinglish":"Kya ho agar is shikaayat ko thame rakhna unhe jitni keemat chuka raha hai usse zyada aapko chuka raha hai — aur kshama bas us keemat ko chukana band karne ka chunaav hai?"},

{"themes":["forgiveness"],"type":"spiritual","depth":2,"emotions":["resentment","grief"],"concepts":["forgiveness","karma","ego"],
"en":"What would it mean to see the person you have not forgiven as someone who was also, in their own way, lost or wounded — not to excuse them, but to humanize them?",
"hi":"जिसे आपने माफ नहीं किया उन्हें किसी ऐसे के रूप में देखने का क्या अर्थ होगा जो अपने तरीके से भी खोया हुआ या घायल था — उन्हें बहाना देने के लिए नहीं, बल्कि उन्हें इंसान बनाने के लिए?",
"hinglish":"Jise aapne maaf nahi kiya unhe kisi aise ke roop mein dekhne ka kya matlab hoga jo apne tarike se bhi khoya hua ya ghayal tha — unhe bahana dene ke liye nahi, balki unhe insaan banane ke liye?"},

{"themes":["forgiveness"],"type":"spiritual","depth":3,"emotions":["grief","resentment","existential"],"concepts":["forgiveness","karma","witness-self","surrender"],
"en":"What if forgiveness is ultimately an act of recognition — that the one who was wronged and the one who wronged are both caught in the same stream of cause and effect?",
"hi":"क्या हो यदि क्षमा अंततः पहचान का एक कार्य है — कि जिस पर गलत किया गया और जिसने गलत किया दोनों एक ही कारण और प्रभाव की धारा में फँसे हैं?",
"hinglish":"Kya ho agar kshama aakhirkar pahchan ka ek kaam hai — ki jis par galat kiya gaya aur jisne galat kiya dono ek hi kaaran aur prabhaav ki dhara mein phanse hain?"},

# ── FAITH_DOUBT – action_oriented & spiritual ────────────────────────────────
{"themes":["faith_doubt"],"type":"action_oriented","depth":1,"emotions":["confusion","doubt"],"concepts":["faith","karma"],
"en":"What one act today could you treat as a small prayer — an offering made without certainty but with sincerity?",
"hi":"आज एक कार्य जिसे आप एक छोटी प्रार्थना के रूप में मान सकते हैं — निश्चितता के बिना लेकिन ईमानदारी के साथ किया गया अर्पण?",
"hinglish":"Aaj ek kaam jise aap ek chhoti prarthna ke roop mein maan sakte hain — nishchitata ke bina lekin imaandaari ke saath kiya gaya arpan?"},

{"themes":["faith_doubt"],"type":"action_oriented","depth":2,"emotions":["doubt","resistance"],"concepts":["faith","karma","surrender"],
"en":"What would you do today if you treated your doubt as a companion rather than an obstacle — acknowledging it, and then acting anyway?",
"hi":"यदि आप अपने संदेह को बाधा की जगह साथी के रूप में मानें — इसे स्वीकार करते हुए, और फिर भी कार्य करते हुए — तो आज आप क्या करेंगे?",
"hinglish":"Agar aap apne sandeh ko badha ki jagah saathi ke roop mein maanein — ise sweekar karte hue, aur phir bhi kaam karte hue — toh aaj aap kya karenge?"},

{"themes":["faith_doubt"],"type":"action_oriented","depth":3,"emotions":["doubt","grief","longing"],"concepts":["faith","karma","dharma","surrender"],
"en":"What would your life look like — in practice, in daily choices — if you decided to live as though meaning existed, even while not knowing for certain?",
"hi":"यदि आप यह निर्णय लें कि अर्थ है ऐसे जिएं — व्यवहार में, दैनिक चुनावों में — निश्चित रूप से न जानते हुए भी — तो आपका जीवन कैसा दिखेगा?",
"hinglish":"Agar aap yeh nirnay lein ki arth hai aise jeeyein — vyavahaar mein, rozmarra chunaavon mein — nishchit roop se na jaante hue bhi — toh aapka jeevan kaisa dikhega?"},

{"themes":["faith_doubt"],"type":"spiritual","depth":1,"emotions":["doubt","longing"],"concepts":["faith","surrender"],
"en":"What if the courage required by faith is not the courage to believe — but the courage to keep showing up even when you don't?",
"hi":"क्या हो यदि आस्था के लिए आवश्यक साहस विश्वास करने का नहीं है — बल्कि तब भी उपस्थित रहने का है जब आप नहीं करते?",
"hinglish":"Kya ho agar aastha ke liye avashyak sahas vishwas karne ka nahi hai — balki tab bhi maujood rehne ka hai jab aap nahi karte?"},

{"themes":["faith_doubt"],"type":"spiritual","depth":2,"emotions":["doubt","grief","longing"],"concepts":["faith","surrender","equanimity"],
"en":"What remains when every concept of the divine is stripped away — is there something that still holds, even in the emptiness?",
"hi":"जब ईश्वर की हर अवधारणा हट जाती है — क्या कुछ ऐसा बचता है जो फिर भी थामे रहता है, खालीपन में भी?",
"hinglish":"Jab Ishwar ki har avdharena hat jaati hai — kya kuch aisa bachta hai jo phir bhi thame rehta hai, khalipan mein bhi?"},

{"themes":["faith_doubt"],"type":"spiritual","depth":3,"emotions":["existential","grief","longing"],"concepts":["faith","surrender","witness-self","equanimity"],
"en":"What if faith and doubt are not opposites — but two movements of the same seeking heart, and both are valid parts of the path?",
"hi":"क्या हो यदि आस्था और संदेह विपरीत नहीं हैं — बल्कि एक ही खोजने वाले हृदय की दो गतिविधियाँ हैं, और दोनों मार्ग के वैध हिस्से हैं?",
"hinglish":"Kya ho agar aastha aur sandeh vipreet nahi hain — balki ek hi khojne wale hridaya ki do gatividhiyan hain, aur dono raaste ke vaidh hisse hain?"},

# ── REGRET – action_oriented & spiritual ─────────────────────────────────────
{"themes":["regret"],"type":"action_oriented","depth":1,"emotions":["regret","guilt"],"concepts":["karma"],
"en":"What would it mean to use the energy of this regret as motivation — not to punish yourself, but to act differently today?",
"hi":"इस पछतावे की ऊर्जा को प्रेरणा के रूप में उपयोग करने का क्या अर्थ होगा — खुद को दंड देने के लिए नहीं, बल्कि आज अलग तरीके से कार्य करने के लिए?",
"hinglish":"Is pachtaave ki urja ko prerna ke roop mein upyog karne ka kya matlab hoga — khud ko dand dene ke liye nahi, balki aaj alag tarike se kaam karne ke liye?"},

{"themes":["regret"],"type":"action_oriented","depth":2,"emotions":["regret","resistance"],"concepts":["karma","dharma"],
"en":"What have you been postponing in your current life because you are still back in the past — and what would it look like to arrive here?",
"hi":"अपने वर्तमान जीवन में आप क्या टाल रहे हैं क्योंकि आप अभी भी अतीत में हैं — और यहाँ पहुँचना कैसा दिखेगा?",
"hinglish":"Apne vartamaan jeevan mein aap kya taal rahe hain kyunki aap abhi bhi ateet mein hain — aur yahan pahunchna kaisa dikhega?"},

{"themes":["regret"],"type":"action_oriented","depth":3,"emotions":["regret","grief","shame"],"concepts":["karma","dharma","detachment"],
"en":"If regret is pointing at a value you hold deeply — honesty, courage, loyalty, care — what would it mean to live that value more fully from now?",
"hi":"यदि पछतावा किसी मूल्य की ओर इशारा कर रहा है जिसे आप गहराई से मानते हैं — ईमानदारी, साहस, वफ़ादारी, देखभाल — तो अब से उस मूल्य को अधिक पूरी तरह जीने का क्या अर्थ होगा?",
"hinglish":"Agar pachtaawa kisi mulya ki taraf ishara kar raha hai jise aap gehraai se maante hain — imaandaari, sahas, vafaadaari, dekhbhaal — toh ab se us mulya ko zyada poori tarah jeene ka kya matlab hoga?"},

{"themes":["regret"],"type":"spiritual","depth":1,"emotions":["regret","grief"],"concepts":["karma","impermanence"],
"en":"What if this regret — painful as it is — is part of the curriculum the soul chose for this lifetime?",
"hi":"क्या हो यदि यह पछतावा — जितना दर्दनाक है — उस पाठ्यक्रम का हिस्सा है जो आत्मा ने इस जन्म के लिए चुना था?",
"hinglish":"Kya ho agar yeh pachtaawa — jitna dardnaak hai — us pathyakram ka hissa hai jo aatma ne is janam ke liye chuna tha?"},

{"themes":["regret"],"type":"spiritual","depth":2,"emotions":["regret","grief"],"concepts":["karma","impermanence","equanimity"],
"en":"What would equanimity in the face of this regret look like — not denial, not drama, but a steady willingness to be with what happened?",
"hi":"इस पछतावे के सामने समभाव कैसा दिखेगा — इनकार नहीं, नाटक नहीं, बल्कि जो हुआ उसके साथ रहने की स्थिर इच्छा?",
"hinglish":"Is pachtaave ke saamne saambhaav kaisa dikhega — inkaar nahi, naataka nahi, balki jo hua uske saath rehne ki sthir ichchha?"},

{"themes":["regret"],"type":"spiritual","depth":3,"emotions":["regret","existential","grief"],"concepts":["karma","impermanence","witness-self","surrender"],
"en":"What if the regret and the one who regrets are both part of the dream — and the witness that watches them has never made a mistake?",
"hi":"क्या हो यदि पछतावा और जो पछताता है दोनों स्वप्न का हिस्सा हैं — और जो साक्षी उन्हें देखता है उसने कभी कोई गलती नहीं की?",
"hinglish":"Kya ho agar pachtaawa aur jo pachtaata hai dono swapna ka hissa hain — aur jo saakshi unhe dekhta hai usne kabhi koi galti nahi ki?"},

# ── RESTLESSNESS – remaining gaps ────────────────────────────────────────────
{"themes":["restlessness"],"type":"action_oriented","depth":2,"emotions":["restlessness","avoidance"],"concepts":["karma","discipline","svadharma"],
"en":"What is the project or commitment you keep approaching but not starting — and what would happen if you began it right now, imperfectly?",
"hi":"वह परियोजना या प्रतिबद्धता क्या है जिसके पास आप जाते रहते हैं लेकिन शुरू नहीं करते — और यदि आप अभी इसे, अपूर्णता से, शुरू करें तो क्या होगा?",
"hinglish":"Woh pariyojana ya pratibaddhata kya hai jiske paas aap jaate rehte hain lekin shuru nahi karte — aur agar aap abhi ise, apurnata se, shuru karein toh kya hoga?"},

{"themes":["restlessness"],"type":"action_oriented","depth":3,"emotions":["restlessness","resistance","emptiness"],"concepts":["karma","discipline","dharma"],
"en":"What would it look like to choose depth over novelty — to go further into what you have started rather than pivoting to the next new thing?",
"hi":"नवीनता की जगह गहराई चुनना कैसा दिखेगा — जो आपने शुरू किया है उसमें आगे जाना न कि अगली नई चीज़ की ओर मुड़ना?",
"hinglish":"Navinta ki jagah gehraai chunna kaisa dikhega — jo aapne shuru kiya hai us mein aage jaana na ki agli nayi cheez ki taraf mudna?"},

{"themes":["restlessness"],"type":"spiritual","depth":2,"emotions":["restlessness","longing","emptiness"],"concepts":["equanimity","desire","ego","surrender"],
"en":"What if stillness is not something you achieve at the end of the seeking — but the very ground the seeking is happening on?",
"hi":"क्या हो यदि शांति कुछ ऐसा नहीं है जो आप खोज के अंत में पाते हैं — बल्कि वह नींव है जिस पर खोज हो रही है?",
"hinglish":"Kya ho agar shanti kuch aisa nahi hai jo aap khoj ke ant mein paate hain — balki woh neenv hai jis par khoj ho rahi hai?"},

{"themes":["restlessness"],"type":"spiritual","depth":3,"emotions":["restlessness","existential","emptiness"],"concepts":["equanimity","ego","witness-self","surrender"],
"en":"What if the restlessness, followed faithfully inward rather than outward, leads to the stillness it was always looking for?",
"hi":"क्या हो यदि बेचैनी, बाहर की जगह अंदर की ओर ईमानदारी से अनुसरण की जाए, उस शांति की ओर ले जाती है जिसे वह हमेशा खोज रही थी?",
"hinglish":"Kya ho agar bechaini, bahar ki jagah andar ki taraf imaandaari se anusaran ki jaaye, us shanti ki taraf le jaati hai jise woh hamesha khoj rahi thi?"},
]

INTENSITY_FLOORS = {1: "any", 2: "mild", 3: "moderate"}

def main():
    db = get_db()
    ensure_reflective_indexes()
    coll = db[REFLECTIVE_QUESTIONS]
    now = datetime.datetime.now(datetime.timezone.utc)
    inserted = skipped = 0
    for q in QUESTIONS:
        if coll.find_one({"text.en": q["en"]}):
            skipped += 1
            continue
        depth = q["depth"]
        doc = {
            "text": {"en": q["en"], "hi": q.get("hi"), "hinglish": q.get("hinglish")},
            "themes": q["themes"],
            "type": q["type"],
            "depth": depth,
            "intensity_safe_floor": INTENSITY_FLOORS[depth],
            "emotions": q.get("emotions", []),
            "concepts": q.get("concepts", []),
            "persona_fit": [],
            "related_verses": [],
            "status": "approved",
            "source": "human_written",
            "stats": {"shown_count":0,"answered_count":0,"engagement_rate":0.0,"last_shown_at":None},
            "active": True,
            "created_at": now, "updated_at": now, "version": 1,
        }
        coll.insert_one(doc)
        inserted += 1
    print(f"Batch 7 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
