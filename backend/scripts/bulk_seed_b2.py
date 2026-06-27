"""Bulk seed batch 2: discipline, duty, ego, failure, faith_doubt."""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── DISCIPLINE ───────────────────────────────────────────────────────────────
{"themes":["discipline"],"type":"self_awareness","depth":1,"emotions":["guilt","inertia"],"concepts":["karma","dharma"],
"en":"What is the gap between what you intend to do and what you actually do — and what lives in that gap?",
"hi":"जो आप करना चाहते हैं और जो आप वास्तव में करते हैं — उनके बीच की खाई में क्या रहता है?",
"hinglish":"Jo aap karna chahte hain aur jo aap asal mein karte hain — unke beech ki khaai mein kya rehta hai?"},

{"themes":["discipline"],"type":"self_awareness","depth":1,"emotions":["restlessness","avoidance"],"concepts":["karma"],
"en":"When you avoid the practice you know serves you — what are you choosing instead, and does that choice satisfy you?",
"hi":"जब आप उस अभ्यास से बचते हैं जो आप जानते हैं आपकी सेवा करता है — उसकी जगह आप क्या चुनते हैं, और क्या वह चुनाव आपको संतुष्ट करता है?",
"hinglish":"Jab aap us abhyas se bachte hain jo aap jaante hain aapki seva karta hai — uski jagah aap kya chunte hain, aur kya woh chunaav aapko santusht karta hai?"},

{"themes":["discipline"],"type":"self_awareness","depth":2,"emotions":["guilt","shame"],"concepts":["karma","ego"],
"en":"What story do you tell yourself about why you cannot maintain this — and how long have you been telling it?",
"hi":"आप खुद को क्या कहानी सुनाते हैं कि यह क्यों बनाए नहीं रख सकते — और आप यह कब से सुना रहे हैं?",
"hinglish":"Aap khud ko kya kahani sunate hain ki yeh kyun banaye nahi rakh sakte — aur aap yeh kab se suna rahe hain?"},

{"themes":["discipline"],"type":"self_awareness","depth":2,"emotions":["inertia","resistance"],"concepts":["karma","laziness"],
"en":"What are you protecting yourself from by staying comfortable — and is that protection actually serving you?",
"hi":"आरामदायक रहकर आप किससे खुद को बचा रहे हैं — और क्या वह सुरक्षा सच में आपकी सेवा कर रही है?",
"hinglish":"Aaramdayak rehkar aap kisse khud ko bacha rahe hain — aur kya woh suraksha sach mein aapki seva kar rahi hai?"},

{"themes":["discipline"],"type":"self_awareness","depth":3,"emotions":["shame","resistance","fear"],"concepts":["ego","karma","witness-self"],
"en":"If you look honestly at the habits that shape your days — are they the choices of the person you want to be, or of someone else?",
"hi":"यदि आप उन आदतों को ईमानदारी से देखें जो आपके दिनों को आकार देती हैं — क्या वे उस व्यक्ति के चुनाव हैं जो आप बनना चाहते हैं, या किसी और के?",
"hinglish":"Agar aap un aadaton ko imaandaari se dekhein jo aapke dinon ko aakar deti hain — kya woh us insaan ke chunaav hain jo aap banna chahte hain, ya kisi aur ke?"},

{"themes":["discipline"],"type":"self_awareness","depth":3,"emotions":["shame","inertia"],"concepts":["karma","ego","dharma"],
"en":"What would the most disciplined version of you have to believe about themselves that you currently don't?",
"hi":"आपके सबसे अनुशासित संस्करण को अपने बारे में क्या विश्वास करना होगा जो आप अभी नहीं करते?",
"hinglish":"Aapke sabse anushasit version ko apne baare mein kya vishwas karna hoga jo aap abhi nahi karte?"},

{"themes":["discipline"],"type":"action_oriented","depth":1,"emotions":["inertia","avoidance"],"concepts":["karma"],
"en":"What is the smallest possible action you could take right now in the direction you know you need to move?",
"hi":"अभी सबसे छोटी संभव क्रिया क्या है जो आप उस दिशा में कर सकते हैं जहाँ आप जानते हैं आपको जाना है?",
"hinglish":"Abhi sabse choti sambhav kriya kya hai jo aap us disha mein kar sakte hain jahan aap jaante hain aapko jaana hai?"},

{"themes":["discipline"],"type":"action_oriented","depth":2,"emotions":["resistance","inertia"],"concepts":["karma","svadharma"],
"en":"What system or structure could you build around this practice so that it requires less willpower each time?",
"hi":"इस अभ्यास के चारों ओर आप क्या प्रणाली या संरचना बना सकते हैं ताकि हर बार कम इच्छाशक्ति चाहिए?",
"hinglish":"Is abhyas ke chaaron taraf aap kya pranali ya sanrachna bana sakte hain taaki har baar kam ichchhashakti chahiye?"},

{"themes":["discipline"],"type":"action_oriented","depth":3,"emotions":["resistance","shame"],"concepts":["karma","dharma","detachment"],
"en":"What would it look like to show up for this practice when you don't feel like it — and still do it without punishing yourself for having resisted?",
"hi":"यह कैसा दिखेगा जब आप इस अभ्यास के लिए तब उपस्थित हों जब मन न हो — और फिर भी इसे करें बिना प्रतिरोध के लिए खुद को दंड दिए?",
"hinglish":"Yeh kaisa dikhega jab aap is abhyas ke liye tab maujood hon jab mann na ho — aur phir bhi ise karein bina pratiroadh ke liye khud ko dand diye?"},

{"themes":["discipline"],"type":"spiritual","depth":1,"emotions":["inertia","guilt"],"concepts":["karma","tamas"],
"en":"What would change in your daily life if you thought of your practice not as something you owe yourself but as an offering?",
"hi":"यदि आप अपने अभ्यास को उस चीज़ के रूप में सोचें जो आप खुद पर नहीं, बल्कि एक अर्पण के रूप में — तो आपके दैनिक जीवन में क्या बदलेगा?",
"hinglish":"Agar aap apne abhyas ko us cheez ke roop mein sochein jo aap khud par nahi, balki ek arpan ke roop mein — toh aapke rozmarra ke jeevan mein kya badlega?"},

{"themes":["discipline"],"type":"spiritual","depth":2,"emotions":["resistance","inertia"],"concepts":["karma","tamas","dharma"],
"en":"The Gita speaks of tamas — the inertia that keeps us still when we should move — where do you feel its weight most in your life?",
"hi":"गीता तमस की बात करती है — वह जड़ता जो हमें तब स्थिर रखती है जब हमें चलना चाहिए — आप अपने जीवन में इसका भार कहाँ सबसे अधिक महसूस करते हैं?",
"hinglish":"Gita tamas ki baat karti hai — woh jadta jo hame tab sthir rakhti hai jab hame chalna chahiye — aap apne jeevan mein iski bhaari kahan sabse zyada mahsoos karte hain?"},

{"themes":["discipline"],"type":"spiritual","depth":3,"emotions":["inertia","shame","existential"],"concepts":["karma","dharma","witness-self"],
"en":"If discipline is a form of respect for the self that exists in future time — what does your relationship with your future self actually look like?",
"hi":"यदि अनुशासन भविष्य के स्वयं के लिए सम्मान का एक रूप है — तो आपके भविष्य के स्वयं के साथ आपका संबंध वास्तव में कैसा दिखता है?",
"hinglish":"Agar anushasan bhavishy ke khud ke liye samman ka ek roop hai — toh aapke bhavishy ke khud ke saath aapka sambandh asal mein kaisa dikhta hai?"},

# ── DUTY ────────────────────────────────────────────────────────────────────
{"themes":["duty"],"type":"self_awareness","depth":1,"emotions":["confusion","reluctance"],"concepts":["svadharma","dharma"],
"en":"When you think about what you are supposed to do here — whose voice is telling you that?",
"hi":"जब आप सोचते हैं कि यहाँ आपको क्या करना चाहिए — वह आवाज़ किसकी है?",
"hinglish":"Jab aap sochte hain ki yahan aapko kya karna chahiye — woh aawaaz kiski hai?"},

{"themes":["duty"],"type":"self_awareness","depth":1,"emotions":["burden","reluctance"],"concepts":["dharma","karma"],
"en":"Where does this duty feel like a weight you carry — and where does it feel like a natural expression of who you are?",
"hi":"यह कर्तव्य कहाँ एक बोझ की तरह लगता है जो आप उठाते हैं — और कहाँ यह स्वाभाविक रूप से आप जो हैं उसकी अभिव्यक्ति की तरह?",
"hinglish":"Yeh kartavya kahan ek bojh ki tarah lagta hai jo aap uthate hain — aur kahan yeh swabhaavic roop se aap jo hain uski abhivyakti ki tarah?"},

{"themes":["duty"],"type":"self_awareness","depth":2,"emotions":["resentment","burden"],"concepts":["svadharma","dharma","karma"],
"en":"What is the difference between the duty you have chosen and the duty that has been chosen for you — and do you know which this is?",
"hi":"जो कर्तव्य आपने चुना है और जो आपके लिए चुना गया है — उनके बीच क्या अंतर है, और क्या आप जानते हैं यह कौन-सा है?",
"hinglish":"Jo kartavya aapne chuna hai aur jo aapke liye chuna gaya hai — unke beech kya antar hai, aur kya aap jaante hain yeh kaun sa hai?"},

{"themes":["duty"],"type":"self_awareness","depth":2,"emotions":["guilt","confusion"],"concepts":["svadharma","ego"],
"en":"When you fulfill this duty, does it leave you feeling larger or smaller — and what does that tell you about whether it truly belongs to you?",
"hi":"जब आप यह कर्तव्य निभाते हैं — क्या यह आपको बड़ा या छोटा महसूस कराता है, और यह आपको क्या बताता है कि क्या यह सच में आपका है?",
"hinglish":"Jab aap yeh kartavya nibhate hain — kya yeh aapko bada ya chhota feel karata hai, aur yeh aapko kya batata hai ki kya yeh sach mein aapka hai?"},

{"themes":["duty"],"type":"self_awareness","depth":3,"emotions":["resentment","existential"],"concepts":["svadharma","dharma","ego"],
"en":"If you stripped away what others expect of you, what remains of your sense of duty — and is that remainder the truest version of it?",
"hi":"यदि आप दूसरों की अपेक्षाएँ हटा दें — तो आपके कर्तव्य-बोध में से क्या बचता है, और क्या वह शेष उसका सबसे सच्चा रूप है?",
"hinglish":"Agar aap doosron ki apekshaein hataa dein — toh aapke kartavya-bodh mein se kya bachta hai, aur kya woh shesh uska sabse sachcha roop hai?"},

{"themes":["duty"],"type":"self_awareness","depth":3,"emotions":["confusion","burden"],"concepts":["svadharma","dharma","witness-self"],
"en":"What would happen to your sense of who you are if you were released from this duty entirely — and does that answer reveal something?",
"hi":"यदि आपको इस कर्तव्य से पूरी तरह मुक्त कर दिया जाए — तो आपकी पहचान के बोध का क्या होगा, और क्या वह उत्तर कुछ प्रकट करता है?",
"hinglish":"Agar aapko is kartavya se poori tarah mukta kar diya jaaye — toh aapki pehchaan ke bodh ka kya hoga, aur kya woh jawab kuch prakat karta hai?"},

{"themes":["duty"],"type":"action_oriented","depth":1,"emotions":["reluctance","avoidance"],"concepts":["karma","dharma"],
"en":"What is the one action you keep putting off that you already know belongs to you — what is in the way?",
"hi":"एक कार्य जो आप टालते रहते हैं और जो आप पहले से जानते हैं आपका है — उसके रास्ते में क्या है?",
"hinglish":"Ek kaam jo aap taalte rehte hain aur jo aap pehle se jaante hain aapka hai — uske raaste mein kya hai?"},

{"themes":["duty"],"type":"action_oriented","depth":2,"emotions":["burden","resentment"],"concepts":["karma","detachment","dharma"],
"en":"What would it mean to do this duty fully — not grudgingly, not perfectly, but with all that you have — and then let go of how it is received?",
"hi":"इस कर्तव्य को पूरी तरह निभाने का क्या अर्थ होगा — अनिच्छा से नहीं, पूर्णता से नहीं, बल्कि जो है उसके साथ — और फिर यह कैसे स्वीकार होता है उसे छोड़ देना?",
"hinglish":"Is kartavya ko poori tarah nibhaane ka kya matlab hoga — anicchha se nahi, purnata se nahi, balki jo hai us ke saath — aur phir yeh kaise sweekar hota hai use chhod dena?"},

{"themes":["duty"],"type":"action_oriented","depth":3,"emotions":["confusion","resentment"],"concepts":["karma","svadharma","detachment"],
"en":"If you acted from your deepest understanding of what this moment asks of you — not from obligation, not from fear of judgement — what would you do?",
"hi":"यदि आप इस क्षण जो आपसे माँगता है उसकी गहरी समझ से कार्य करें — दायित्व से नहीं, निर्णय के डर से नहीं — तो आप क्या करेंगे?",
"hinglish":"Agar aap is pal jo aapse maangta hai uski gehri samajh se kaam karein — dayitva se nahi, niraday ke dar se nahi — toh aap kya karenge?"},

{"themes":["duty"],"type":"spiritual","depth":1,"emotions":["confusion","burden"],"concepts":["dharma","svadharma"],
"en":"What would it feel like to do this not because you must, but because it is the truest expression of who you are in this moment?",
"hi":"यह कैसा लगेगा यदि आप यह इसलिए नहीं करें कि करना है, बल्कि इसलिए कि यह इस क्षण में आप जो हैं उसकी सबसे सच्ची अभिव्यक्ति है?",
"hinglish":"Yeh kaisa lagega agar aap yeh isliye nahi karein ki karna hai, balki isliye ki yeh is pal mein aap jo hain uski sabse sachchi abhivyakti hai?"},

{"themes":["duty"],"type":"spiritual","depth":2,"emotions":["reluctance","resentment"],"concepts":["karma","dharma","detachment"],
"en":"The Gita does not say do what is easy — it says do what is yours. How do you know what is truly yours to do here?",
"hi":"गीता यह नहीं कहती कि जो आसान हो वह करो — वह कहती है जो तुम्हारा हो वह करो। आप यहाँ कैसे जानते हैं कि सच में क्या आपका है करने के लिए?",
"hinglish":"Gita yeh nahi kehti ki jo aasaan ho woh karo — woh kehti hai jo tumhara ho woh karo. Aap yahan kaise jaante hain ki sach mein kya aapka hai karne ke liye?"},

{"themes":["duty"],"type":"spiritual","depth":3,"emotions":["confusion","existential"],"concepts":["svadharma","dharma","karma","surrender"],
"en":"What if your deepest duty in this moment is not the one the world can see — but something interior, a turning inward that only you would know?",
"hi":"क्या हो यदि इस क्षण आपका सबसे गहरा कर्तव्य वह नहीं है जो दुनिया देख सकती है — बल्कि कुछ आंतरिक, एक भीतर की ओर मुड़ना जो केवल आप जानेंगे?",
"hinglish":"Kya ho agar is pal aapka sabse gehra kartavya woh nahi hai jo duniya dekh sakti hai — balki kuch aantarik, ek andar ki taraf mudna jo sirf aap jaanenge?"},

# ── EGO ─────────────────────────────────────────────────────────────────────
{"themes":["ego"],"type":"self_awareness","depth":1,"emotions":["pride","defensiveness"],"concepts":["ego"],
"en":"When you felt the need to defend yourself just now — what were you afraid would be lost if you didn't?",
"hi":"जब आपको अभी खुद का बचाव करने की ज़रूरत महसूस हुई — अगर आप न करते, तो आपको डर था क्या खो जाएगा?",
"hinglish":"Jab aapko abhi khud ka bachav karne ki zaroorat mahsoos hui — agar aap na karte, toh aapko dar tha kya kho jaayega?"},

{"themes":["ego"],"type":"self_awareness","depth":1,"emotions":["pride","shame"],"concepts":["ego","witness-self"],
"en":"What opinion of yourself are you most careful to protect — and where does that opinion come from?",
"hi":"अपने बारे में कौन-सी राय आप सबसे अधिक सावधानी से बचाते हैं — और वह राय कहाँ से आती है?",
"hinglish":"Apne baare mein kaun si raay aap sabse zyada saavdhaani se bachate hain — aur woh raay kahan se aati hai?"},

{"themes":["ego"],"type":"self_awareness","depth":2,"emotions":["pride","shame","defensiveness"],"concepts":["ego","witness-self"],
"en":"What are you most afraid others will discover about you — and how much of your energy goes toward preventing that discovery?",
"hi":"आप डरते हैं कि दूसरे आपके बारे में क्या खोजेंगे — और उस खोज को रोकने में आपकी कितनी ऊर्जा जाती है?",
"hinglish":"Aap darte hain ki doosre aapke baare mein kya khojenge — aur us khoj ko rokne mein aapki kitni urja jaati hai?"},

{"themes":["ego"],"type":"self_awareness","depth":2,"emotions":["pride","inadequacy"],"concepts":["ego","comparison"],
"en":"When someone else succeeds at something you want — what is the first reaction beneath the surface, and what does it reveal?",
"hi":"जब कोई और उस काम में सफल होता है जो आप चाहते हैं — सतह के नीचे पहली प्रतिक्रिया क्या है, और वह क्या प्रकट करती है?",
"hinglish":"Jab koi aur us kaam mein safal hota hai jo aap chahte hain — upar ki satah ke neeche pehli pratikriya kya hai, aur woh kya prakat karti hai?"},

{"themes":["ego"],"type":"self_awareness","depth":3,"emotions":["shame","pride","existential"],"concepts":["ego","witness-self","detachment"],
"en":"Who would you be if every role, achievement, and reputation were taken away — and is that person someone you have ever met?",
"hi":"यदि हर भूमिका, उपलब्धि, और प्रतिष्ठा छिन जाए — तो आप कौन होंगे, और क्या वह व्यक्ति आपने कभी मिला है?",
"hinglish":"Agar har bhumika, uplabdhi, aur pratishtha chhin jaaye — toh aap kaun honge, aur kya woh insaan aapne kabhi mila hai?"},

{"themes":["ego"],"type":"self_awareness","depth":3,"emotions":["pride","fear","existential"],"concepts":["ego","witness-self"],
"en":"What would remain of your sense of self if you were no longer needed, recognized, or right about something — and is that remainder enough?",
"hi":"यदि आप अब आवश्यक, मान्यता प्राप्त, या किसी बात में सही न रहें — तो आपके स्व-बोध में से क्या शेष बचेगा, और क्या वह शेष पर्याप्त है?",
"hinglish":"Agar aap ab avashyak, manyata prapt, ya kisi baat mein sahi na rahein — toh aapke swabodh mein se kya shesh bachega, aur kya woh shesh kaafi hai?"},

{"themes":["ego"],"type":"action_oriented","depth":1,"emotions":["pride","stubbornness"],"concepts":["ego","karma"],
"en":"What would you do differently in this situation if you were not concerned with how it makes you look?",
"hi":"यदि आप इस बात से चिंतित न हों कि यह आपको कैसा दिखाता है — तो इस स्थिति में आप क्या अलग करते?",
"hinglish":"Agar aap is baat se chintit na hon ki yeh aapko kaisa dikhata hai — toh is situation mein aap kya alag karte?"},

{"themes":["ego"],"type":"action_oriented","depth":2,"emotions":["pride","defensiveness"],"concepts":["ego","karma","svadharma"],
"en":"What would you be free to do — or say, or admit — if protecting your image were not part of the equation?",
"hi":"यदि अपनी छवि बचाना समीकरण का हिस्सा न हो — तो आप क्या करने, कहने या स्वीकार करने के लिए स्वतंत्र होंगे?",
"hinglish":"Agar apni chhavi bachana equation ka hissa na ho — toh aap kya karne, kehne ya sweekar karne ke liye swatantra honge?"},

{"themes":["ego"],"type":"action_oriented","depth":3,"emotions":["pride","shame"],"concepts":["ego","karma","surrender"],
"en":"What is the action you have been avoiding because it would require you to be wrong, small, or uncertain in front of someone?",
"hi":"वह कार्य क्या है जिससे आप इसलिए बच रहे हैं क्योंकि इसके लिए किसी के सामने गलत, छोटे, या अनिश्चित होना पड़ेगा?",
"hinglish":"Woh kaam kya hai jisse aap isliye bach rahe hain kyunki iske liye kisi ke saamne galat, chhote, ya anishchit hona padega?"},

{"themes":["ego"],"type":"spiritual","depth":1,"emotions":["pride","restlessness"],"concepts":["ego","witness-self"],
"en":"What if the voice that most insists it is right is the one most in need of being gently questioned?",
"hi":"क्या हो यदि जो आवाज़ सबसे अधिक जोर देती है कि वह सही है — वही सबसे अधिक धीरे से सवाल किए जाने की ज़रूरत में है?",
"hinglish":"Kya ho agar jo aawaaz sabse zyada zor deti hai ki woh sahi hai — wahi sabse zyada dheere se sawaal kiye jaane ki zaroorat mein hai?"},

{"themes":["ego"],"type":"spiritual","depth":2,"emotions":["pride","shame"],"concepts":["ego","witness-self","detachment"],
"en":"The Gita asks: who is the one watching the mind create all this drama — and have you ever rested in that watcher?",
"hi":"गीता पूछती है: जो मन को यह सारा नाटक रचते देख रहा है — वह कौन है, और क्या आप कभी उस साक्षी में विश्राम किए हैं?",
"hinglish":"Gita poochti hai: jo mann ko yeh saara naataka rachte dekh raha hai — woh kaun hai, aur kya aap kabhi us saakshi mein vishram kiye hain?"},

{"themes":["ego"],"type":"spiritual","depth":3,"emotions":["pride","existential","shame"],"concepts":["ego","witness-self","detachment","surrender"],
"en":"If the ego that suffers and seeks and defends is itself a construction — built piece by piece — what is it built on, and could it be built differently?",
"hi":"यदि जो अहंकार दुख उठाता, खोजता, और बचाव करता है वह स्वयं एक निर्माण है — टुकड़े-टुकड़े बना — तो यह किस पर बना है, और क्या इसे अलग तरह से बनाया जा सकता है?",
"hinglish":"Agar jo ahankar dukh uthata, dhundhta, aur bachav karta hai woh khud ek nirman hai — tukde-tukde bana — toh yeh kis par bana hai, aur kya ise alag tarah se banaya ja sakta hai?"},

# ── FAILURE ─────────────────────────────────────────────────────────────────
{"themes":["failure"],"type":"self_awareness","depth":1,"emotions":["shame","disappointment"],"concepts":["karma","ego"],
"en":"What is the harshest thing you have said to yourself about this — and would you say that to someone you love?",
"hi":"इस बारे में आपने खुद से जो सबसे कठोर बात कही है — क्या आप वह किसी प्रिय व्यक्ति से कहेंगे?",
"hinglish":"Is baare mein aapne khud se jo sabse kathor baat kahi hai — kya aap woh kisi pyare insaan se kahenge?"},

{"themes":["failure"],"type":"self_awareness","depth":1,"emotions":["shame","disappointment"],"concepts":["karma"],
"en":"What did you learn from this that you could not have learned any other way?",
"hi":"इससे आपने क्या सीखा जो आप किसी और तरीके से नहीं सीख सकते थे?",
"hinglish":"Isse aapne kya seekha jo aap kisi aur tarike se nahi seekh sakte the?"},

{"themes":["failure"],"type":"self_awareness","depth":2,"emotions":["shame","inadequacy","resentment"],"concepts":["ego","karma"],
"en":"What does calling this a failure reveal about what you believed was supposed to happen — and who decided that?",
"hi":"इसे विफलता कहना उस बारे में क्या प्रकट करता है जो आपने सोचा था होना चाहिए था — और यह किसने तय किया था?",
"hinglish":"Ise vifalta kehna us baare mein kya prakat karta hai jo aapne socha tha hona chahiye tha — aur yeh kisne tay kiya tha?"},

{"themes":["failure"],"type":"self_awareness","depth":2,"emotions":["shame","self-criticism"],"concepts":["ego","witness-self"],
"en":"If this had happened to someone else — someone you cared for — would you call it a failure, or would you see it differently?",
"hi":"यदि यह किसी और के साथ हुआ होता — किसी ऐसे के साथ जिसकी आप परवाह करते हैं — क्या आप इसे विफलता कहते, या इसे अलग तरह से देखते?",
"hinglish":"Agar yeh kisi aur ke saath hua hota — kisi aise ke saath jis ki aap parwaah karte hain — kya aap ise vifalta kehte, ya ise alag tarah se dekhte?"},

{"themes":["failure"],"type":"self_awareness","depth":3,"emotions":["shame","existential","inadequacy"],"concepts":["ego","witness-self","karma"],
"en":"What is the story about who you are that this failure seems to confirm — and when did that story first take root?",
"hi":"यह विफलता आपके बारे में कौन-सी कहानी की पुष्टि करती लगती है — और वह कहानी पहली बार कब उगी थी?",
"hinglish":"Yeh vifalta aapke baare mein kaun si kahani ki pushti karti lagti hai — aur woh kahani pehli baar kab ugi thi?"},

{"themes":["failure"],"type":"self_awareness","depth":3,"emotions":["shame","grief","existential"],"concepts":["ego","witness-self","karma"],
"en":"What if this ending is not evidence of your inadequacy but a door that the old version of you could not have walked through?",
"hi":"क्या हो यदि यह अंत आपकी अपर्याप्तता का प्रमाण नहीं है — बल्कि एक दरवाज़ा है जिसमें से आपका पुराना संस्करण नहीं जा सकता था?",
"hinglish":"Kya ho agar yeh ant aapki aparyaptata ka praman nahi hai — balki ek darwaza hai jis se aapka purana version nahi ja sakta tha?"},

{"themes":["failure"],"type":"action_oriented","depth":1,"emotions":["shame","paralysis"],"concepts":["karma"],
"en":"What is the next smallest move available to you from here — not to fix everything, but just to take one step?",
"hi":"यहाँ से आपके लिए अगला सबसे छोटा कदम क्या उपलब्ध है — सब कुछ ठीक करने के लिए नहीं, बस एक कदम उठाने के लिए?",
"hinglish":"Yahan se aapke liye agla sabse chhota kadam kya uplabdh hai — sab kuch theek karne ke liye nahi, bas ek kadam uthane ke liye?"},

{"themes":["failure"],"type":"action_oriented","depth":2,"emotions":["shame","resistance"],"concepts":["karma","detachment","svadharma"],
"en":"What would it look like to try again — not to erase this failure, but to carry it lightly and keep going anyway?",
"hi":"फिर से प्रयास करना कैसा दिखेगा — इस विफलता को मिटाने के लिए नहीं, बल्कि इसे हल्के से लेकर फिर भी आगे बढ़ने के लिए?",
"hinglish":"Phir se prayas karna kaisa dikhega — is vifalta ko mitane ke liye nahi, balki ise halke se lekar phir bhi aage badhne ke liye?"},

{"themes":["failure"],"type":"action_oriented","depth":3,"emotions":["shame","grief","fear"],"concepts":["karma","detachment","dharma"],
"en":"If this outcome does not define you — if you acted rightly and it still did not go well — what would acting rightly next time look like, regardless of outcome?",
"hi":"यदि यह परिणाम आपको परिभाषित नहीं करता — यदि आपने सही किया और फिर भी यह ठीक नहीं हुआ — तो अगली बार सही करना कैसा दिखेगा, परिणाम की परवाह किए बिना?",
"hinglish":"Agar yeh natija aapko define nahi karta — agar aapne sahi kiya aur phir bhi yeh theek nahi hua — toh agla baar sahi karna kaisa dikhega, natije ki parwaah kiye bina?"},

{"themes":["failure"],"type":"spiritual","depth":1,"emotions":["shame","grief"],"concepts":["karma","equanimity"],
"en":"What if this is not the end of something — but the ground being cleared for something that could not have grown before?",
"hi":"क्या हो यदि यह किसी चीज़ का अंत नहीं है — बल्कि ज़मीन साफ हो रही है उस चीज़ के लिए जो पहले उग नहीं सकती थी?",
"hinglish":"Kya ho agar yeh kisi cheez ka ant nahi hai — balki zameen saaf ho rahi hai us cheez ke liye jo pehle ug nahi sakti thi?"},

{"themes":["failure"],"type":"spiritual","depth":2,"emotions":["shame","grief","resistance"],"concepts":["karma","detachment","equanimity"],
"en":"The Gita speaks of acting without being shaken by loss or gain — what would it mean to meet this outcome from that steadiness?",
"hi":"गीता हानि या लाभ से विचलित हुए बिना कार्य करने की बात करती है — इस परिणाम का सामना उस स्थिरता से करने का क्या अर्थ होगा?",
"hinglish":"Gita haani ya laabh se vichalit hue bina kaam karne ki baat karti hai — is natije ka saamna us sthirata se karne ka kya matlab hoga?"},

{"themes":["failure"],"type":"spiritual","depth":3,"emotions":["shame","existential","grief"],"concepts":["karma","detachment","witness-self"],
"en":"If the self that failed were itself only a temporary formation — a role the deeper witness watched — what would remain of the shame?",
"hi":"यदि जो स्वयं विफल हुआ वह भी केवल एक अस्थायी संरचना हो — एक भूमिका जिसे गहरे साक्षी ने देखा — तो उस शर्म में से क्या शेष बचेगा?",
"hinglish":"Agar jo khud vifal hua woh bhi sirf ek asthaayi sanrachna ho — ek bhumika jise gehre saakshi ne dekha — toh us sharm mein se kya shesh bachega?"},

# ── FAITH_DOUBT ──────────────────────────────────────────────────────────────
{"themes":["faith_doubt"],"type":"self_awareness","depth":1,"emotions":["confusion","longing"],"concepts":["faith","surrender"],
"en":"What is the thing you have always hoped was true — even when you could not prove it?",
"hi":"वह चीज़ क्या है जिसके बारे में आपने हमेशा आशा की कि यह सच है — भले ही आप इसे साबित नहीं कर सके?",
"hinglish":"Woh cheez kya hai jiske baare mein aapne hamesha asha ki ki yeh sach hai — chahe aap ise sabit nahi kar sake?"},

{"themes":["faith_doubt"],"type":"self_awareness","depth":1,"emotions":["doubt","restlessness"],"concepts":["faith","witness-self"],
"en":"What is the doubt that keeps returning — and what would it ask you to do if you took it seriously?",
"hi":"वह संदेह क्या है जो बार-बार लौटता है — और यदि आप इसे गंभीरता से लें तो यह आपसे क्या करवाएगा?",
"hinglish":"Woh sandeh kya hai jo baar-baar lauta hai — aur agar aap ise gambhirta se lein toh yeh aapse kya karwaaega?"},

{"themes":["faith_doubt"],"type":"self_awareness","depth":2,"emotions":["doubt","grief","longing"],"concepts":["faith","surrender"],
"en":"When your faith wavered — what exactly shook it, and what does that reveal about what your faith was resting on?",
"hi":"जब आपकी आस्था डगमगाई — ठीक क्या हिला, और यह क्या प्रकट करता है कि आपकी आस्था किस पर टिकी थी?",
"hinglish":"Jab aapki aastha dagmagayi — theek kya hila, aur yeh kya prakat karta hai ki aapki aastha kis par tiki thi?"},

{"themes":["faith_doubt"],"type":"self_awareness","depth":2,"emotions":["confusion","longing"],"concepts":["faith","ego","surrender"],
"en":"What is the difference between your doubt of God and your doubt of yourself — are they the same doubt wearing different faces?",
"hi":"ईश्वर पर आपके संदेह और खुद पर आपके संदेह में क्या अंतर है — क्या वे अलग-अलग चेहरे पहने एक ही संदेह हैं?",
"hinglish":"Ishwar par aapke sandeh aur khud par aapke sandeh mein kya antar hai — kya woh alag-alag chehre pahne ek hi sandeh hain?"},

{"themes":["faith_doubt"],"type":"self_awareness","depth":3,"emotions":["grief","existential","longing"],"concepts":["faith","witness-self","surrender"],
"en":"What would you have to let go of — in your picture of how things should work — to allow a different kind of faith to take root?",
"hi":"आपकी इस तस्वीर में क्या छोड़ना होगा — कि चीज़ें कैसे काम करनी चाहिए — ताकि एक अलग प्रकार की आस्था जड़ें पकड़ सके?",
"hinglish":"Aapki is tasweer mein kya chhodni hogi — ki cheezein kaise kaam karni chahiye — taaki ek alag prakar ki aastha jadein pakad sake?"},

{"themes":["faith_doubt"],"type":"self_awareness","depth":3,"emotions":["existential","grief","longing"],"concepts":["faith","ego","witness-self"],
"en":"If you dropped every inherited belief and every acquired doubt — what is left that you actually know from the inside?",
"hi":"यदि आप हर विरासत में मिली मान्यता और हर अर्जित संदेह को छोड़ दें — तो क्या शेष है जो आप वास्तव में भीतर से जानते हैं?",
"hinglish":"Agar aap har virasat mein mili manyata aur har arjit sandeh ko chhod dein — toh kya shesh hai jo aap asal mein andar se jaante hain?"},

{"themes":["faith_doubt"],"type":"action_oriented","depth":1,"emotions":["confusion","doubt"],"concepts":["faith","karma"],
"en":"What is one thing you could do today that would require you to trust — even without certainty?",
"hi":"आज एक चीज़ क्या है जो करने के लिए आपको विश्वास करना पड़ेगा — बिना निश्चितता के भी?",
"hinglish":"Aaj ek cheez kya hai jo karne ke liye aapko vishwas karna padega — bina nishchitata ke bhi?"},

{"themes":["faith_doubt"],"type":"action_oriented","depth":2,"emotions":["doubt","resistance"],"concepts":["faith","karma","surrender"],
"en":"What would you do differently if you acted as though there were something larger than you holding this — not as a belief, but as an experiment?",
"hi":"यदि आप ऐसे कार्य करें जैसे आपसे बड़ी कोई शक्ति इसे थामे हुए हो — मान्यता के रूप में नहीं, बल्कि एक प्रयोग के रूप में — तो क्या अलग करेंगे?",
"hinglish":"Agar aap aise kaam karein jaise aapse badi koi shakti ise thame hue ho — manyata ke roop mein nahi, balki ek prayog ke roop mein — toh kya alag karenge?"},

{"themes":["faith_doubt"],"type":"action_oriented","depth":3,"emotions":["doubt","grief","longing"],"concepts":["faith","karma","dharma","surrender"],
"en":"What would living from your deepest values look like — even in a universe that offers you no guarantees and no explanations?",
"hi":"अपने गहरे मूल्यों से जीना कैसा दिखेगा — एक ऐसे ब्रह्मांड में भी जो आपको कोई गारंटी और कोई स्पष्टीकरण नहीं देता?",
"hinglish":"Apne gehre mulyon se jeena kaisa dikhega — ek aise brahmand mein bhi jo aapko koi guarantee aur koi spashtikarana nahi deta?"},

{"themes":["faith_doubt"],"type":"spiritual","depth":1,"emotions":["doubt","longing"],"concepts":["faith","surrender"],
"en":"What if faith is not the absence of doubt but the willingness to act in the presence of it?",
"hi":"क्या हो यदि आस्था संदेह की अनुपस्थिति नहीं है — बल्कि उसकी उपस्थिति में कार्य करने की इच्छा है?",
"hinglish":"Kya ho agar aastha sandeh ki anupasthiti nahi hai — balki uski upasthiti mein kaam karne ki ichchha hai?"},

{"themes":["faith_doubt"],"type":"spiritual","depth":2,"emotions":["doubt","grief","longing"],"concepts":["faith","surrender","equanimity"],
"en":"What is the version of the divine — or of meaning, or of order — that your doubt cannot quite destroy, however hard it tries?",
"hi":"ईश्वर का — या अर्थ का, या व्यवस्था का — वह स्वरूप कौन-सा है जिसे आपका संदेह, चाहे कितना भी कोशिश करे, पूरी तरह नष्ट नहीं कर सकता?",
"hinglish":"Ishwar ka — ya arth ka, ya vyavastha ka — woh swaroop kaun sa hai jise aapka sandeh, chahe kitna bhi koshish kare, poori tarah nasht nahi kar sakta?"},

{"themes":["faith_doubt"],"type":"spiritual","depth":3,"emotions":["existential","grief","longing"],"concepts":["faith","surrender","witness-self","equanimity"],
"en":"What if the deepest kind of faith is not belief in a particular story but trust in the awareness that is present through all stories — even this one?",
"hi":"क्या हो यदि सबसे गहरी आस्था किसी विशेष कहानी में विश्वास नहीं है — बल्कि उस चेतना पर विश्वास है जो सभी कहानियों में उपस्थित है — इस कहानी में भी?",
"hinglish":"Kya ho agar sabse gehri aastha kisi vishesh kahani mein vishwas nahi hai — balki us chetna par vishwas hai jo sabhi kahanion mein maujood hai — is kahani mein bhi?"},
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
            "related_verses": q.get("related_verses", []),
            "status": "approved",
            "source": "human_written",
            "stats": {"shown_count":0,"answered_count":0,"engagement_rate":0.0,"last_shown_at":None},
            "active": True,
            "created_at": now, "updated_at": now, "version": 1,
        }
        coll.insert_one(doc)
        inserted += 1
    print(f"Batch 2 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
