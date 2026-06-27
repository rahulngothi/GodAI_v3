"""Bulk seed batch 1: anxiety, attachment, comparison, control, desire.
Run: python3 -m scripts.bulk_seed_b1
"""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── ANXIETY ─────────────────────────────────────────────────────────────────
{"themes":["anxiety"],"type":"self_awareness","depth":1,"emotions":["worry","restlessness"],"concepts":["equanimity"],
"en":"When the mind races ahead to what might go wrong, what is it really trying to protect?",
"hi":"जब मन आगे दौड़कर सोचने लगता है कि क्या गलत हो सकता है — वह असल में क्या बचाने की कोशिश कर रहा है?",
"hinglish":"Jab mann aage daudta hai ki kya galat ho sakta hai — woh asal mein kya bachane ki koshish kar raha hai?"},

{"themes":["anxiety"],"type":"self_awareness","depth":1,"emotions":["tension","dread"],"concepts":["surrender"],
"en":"What is the worst that could happen here — and how much of your energy is already living in that imagined place?",
"hi":"यहाँ सबसे बुरा क्या हो सकता है — और आपकी कितनी ऊर्जा पहले से उस कल्पित जगह में रह रही है?",
"hinglish":"Yahan sabse bura kya ho sakta hai — aur aapki kitni urja pehle se us kalpita jagah mein reh rahi hai?"},

{"themes":["anxiety"],"type":"self_awareness","depth":1,"emotions":["unease","anticipation"],"concepts":["present moment"],
"en":"Right now, in this breath, is there actually a problem — or only the thought of one?",
"hi":"अभी, इस साँस में — क्या सच में कोई समस्या है, या केवल उसका विचार?",
"hinglish":"Abhi, is saans mein — kya sach mein koi samasya hai, ya sirf uska khayal?"},

{"themes":["anxiety"],"type":"self_awareness","depth":1,"emotions":["nervousness","insecurity"],"concepts":["equanimity"],
"en":"What would you do differently today if you trusted that things would find their own resolution?",
"hi":"यदि आप विश्वास करते कि चीज़ें अपनी राह खुद खोज लेंगी — तो आज आप क्या अलग करते?",
"hinglish":"Agar aap trust karte ki cheezein apna rasta khud dhundh lengi — toh aaj aap kya alag karte?"},

{"themes":["anxiety"],"type":"self_awareness","depth":2,"emotions":["fear","clinging"],"concepts":["detachment","karma"],
"en":"This worry keeps returning — what does its persistence tell you about what you are unwilling to release?",
"hi":"यह चिंता बार-बार लौटती है — इसकी वापसी आपको क्या बताती है कि आप क्या छोड़ने को तैयार नहीं हैं?",
"hinglish":"Yeh chinta baar-baar lautti hai — iski wapsi aapko kya batati hai ki aap kya chhodne ko taiyar nahi hain?"},

{"themes":["anxiety"],"type":"self_awareness","depth":2,"emotions":["overwhelm","anticipation"],"concepts":["equanimity","detachment"],
"en":"If this fear came true, what is the deepest thing you are afraid of losing — and is that thing truly yours to keep?",
"hi":"यदि यह भय सच हो जाए — तो सबसे गहरी चीज़ जिसे खोने से आप डरते हैं वह क्या है, और क्या वह वास्तव में आपकी है?",
"hinglish":"Agar yeh dar sach ho jaaye — toh sabse gehri cheez jo aap khoye se darte hain woh kya hai, aur kya woh sach mein aapki hai?"},

{"themes":["anxiety"],"type":"self_awareness","depth":2,"emotions":["tension","resistance"],"concepts":["surrender"],
"en":"What part of you refuses to let this worry go, and what does it believe would happen if you did?",
"hi":"आपका कौन-सा हिस्सा इस चिंता को जाने देने से इनकार करता है — और वह क्या मानता है कि छोड़ने पर क्या होगा?",
"hinglish":"Aapka kaun sa hissa is chinta ko jaane dene se inkar karta hai — aur woh kya maanta hai ki chodne par kya hoga?"},

{"themes":["anxiety"],"type":"self_awareness","depth":2,"emotions":["dread","shame"],"concepts":["ego","witness-self"],
"en":"When this anxious voice speaks, whose voice does it most remind you of?",
"hi":"जब यह चिंतित आवाज़ बोलती है — तो यह किसकी आवाज़ की सबसे अधिक याद दिलाती है?",
"hinglish":"Jab yeh chintit aawaaz bolta hai — toh yeh kisi ki aawaaz ki sabse zyada yaad dilata hai?"},

{"themes":["anxiety"],"type":"self_awareness","depth":3,"emotions":["dread","clinging"],"concepts":["ego","detachment"],
"en":"If you could not control how this turns out — not even a little — what would be left of who you think you are?",
"hi":"यदि इसका परिणाम आपके नियंत्रण में बिल्कुल न हो — तब आप जो सोचते हैं कि आप हैं, उसमें से क्या शेष बचेगा?",
"hinglish":"Agar is ka natija bilkul aapke control mein na ho — toh jo aap sochte hain ki aap hain, us mein se kya bacha rahega?"},

{"themes":["anxiety"],"type":"self_awareness","depth":3,"emotions":["existential fear","emptiness"],"concepts":["witness-self","surrender"],
"en":"Beneath this anxiety, what is the belief about yourself that you are most afraid to examine?",
"hi":"इस चिंता के नीचे — अपने बारे में वह कौन-सी धारणा है जिसे आप सबसे अधिक जाँचने से डरते हैं?",
"hinglish":"Is chinta ke neeche — apne baare mein woh kaun si dharna hai jise aap sabse zyada jaanchne se darte hain?"},

{"themes":["anxiety"],"type":"self_awareness","depth":3,"emotions":["fear","shame"],"concepts":["ego","karma"],
"en":"What would it mean about you if the thing you are dreading actually happened — and where did that meaning come from?",
"hi":"यदि जिस बात से आप डरते हैं वह हो जाए — तो इसका आपके बारे में क्या अर्थ होगा, और यह अर्थ कहाँ से आया?",
"hinglish":"Agar jo aap se darte hain woh ho jaaye — toh aapke baare mein iska kya matlab hoga, aur yeh matlab kahan se aaya?"},

{"themes":["anxiety"],"type":"action_oriented","depth":1,"emotions":["nervousness","hesitation"],"concepts":["karma","dharma"],
"en":"What one small thing could you do right now that would make this feel slightly less enormous?",
"hi":"अभी एक छोटी चीज़ क्या है जो आप कर सकते हैं जिससे यह थोड़ा कम विशाल लगे?",
"hinglish":"Abhi ek choti cheez kya hai jo aap kar sakte hain jisse yeh thoda kam bada lage?"},

{"themes":["anxiety"],"type":"action_oriented","depth":1,"emotions":["paralysis","worry"],"concepts":["karma"],
"en":"If you acted on what you know rather than waiting for certainty, what would you do first?",
"hi":"यदि आप निश्चितता की प्रतीक्षा किए बिना जो जानते हैं उस पर कार्य करें — तो सबसे पहले क्या करेंगे?",
"hinglish":"Agar aap nischitata ka wait kiye bina jo jaante hain us par kaam karein — toh sabse pehle kya karenge?"},

{"themes":["anxiety"],"type":"action_oriented","depth":2,"emotions":["fear","indecision"],"concepts":["karma","detachment"],
"en":"What action have you been postponing because you cannot guarantee how it will land — and what would it cost you to take it anyway?",
"hi":"कौन-सा कार्य आप इसलिए टाल रहे हैं क्योंकि आप उसके परिणाम की गारंटी नहीं दे सकते — और उसे फिर भी करने की कीमत क्या होगी?",
"hinglish":"Kaun sa kaam aap isliye taal rahe hain kyunki aap uske natije ki guarantee nahi de sakte — aur use phir bhi karne ki keemat kya hogi?"},

{"themes":["anxiety"],"type":"action_oriented","depth":2,"emotions":["overwhelm","resistance"],"concepts":["karma","svadharma"],
"en":"If you separated what is yours to do from what is not yours to control — what does your list of duties actually look like?",
"hi":"यदि आप अपना कर्तव्य और अपने नियंत्रण से परे की बात अलग करें — तो आपके कर्तव्यों की सूची कैसी दिखती है?",
"hinglish":"Agar aap apna kartavya aur apne control se pare ki baat alag karein — toh aapke kartavyon ki list kaisi dikhti hai?"},

{"themes":["anxiety"],"type":"action_oriented","depth":3,"emotions":["dread","clinging"],"concepts":["karma","surrender","detachment"],
"en":"If you knew the outcome was already decided — not by you — what would you still choose to do, and why?",
"hi":"यदि आप जानते कि परिणाम पहले से तय है — आपके द्वारा नहीं — तो फिर भी आप क्या करना चुनते, और क्यों?",
"hinglish":"Agar aap jaante ki natija pehle se tay hai — aapke dwara nahi — toh phir bhi aap kya karna chunte, aur kyun?"},

{"themes":["anxiety"],"type":"spiritual","depth":1,"emotions":["worry","restlessness"],"concepts":["equanimity","surrender"],
"en":"What would it feel like to hand this worry to something larger than yourself, just for this moment?",
"hi":"इस चिंता को किसी अपने से बड़ी शक्ति को — बस इस क्षण के लिए — सौंपना कैसा लगेगा?",
"hinglish":"Is chinta ko kisi apne se badi shakti ko — bas is pal ke liye — saunpna kaisa lagega?"},

{"themes":["anxiety"],"type":"spiritual","depth":2,"emotions":["fear","resistance"],"concepts":["surrender","equanimity"],
"en":"What would it mean to trust — not that things will go well, but that you will be held regardless?",
"hi":"इसका क्या अर्थ होगा कि आप विश्वास करें — यह नहीं कि सब ठीक होगा, बल्कि यह कि आप चाहे कुछ भी हो, थामे जाएंगे?",
"hinglish":"Iska kya matlab hoga ki aap trust karein — yeh nahi ki sab theek hoga, balki yeh ki aap chahe kuch bhi ho, thame jaoge?"},

{"themes":["anxiety"],"type":"spiritual","depth":3,"emotions":["existential fear","dread"],"concepts":["surrender","witness-self","impermanence"],
"en":"If this anxiety is pointing at something true about the nature of things — impermanence, uncertainty, the limits of control — what would it ask you to accept?",
"hi":"यदि यह चिंता चीज़ों की वास्तविक प्रकृति — अनित्यता, अनिश्चितता, नियंत्रण की सीमाएँ — की ओर इशारा कर रही है, तो यह आपसे क्या स्वीकार करवाना चाहती है?",
"hinglish":"Agar yeh chinta cheezein ki sacchi prakriti — anitya, anishchitata, control ki seemain — ki taraf ishara kar rahi hai, toh yeh aapse kya swikaar karwana chahti hai?"},

# ── ATTACHMENT ──────────────────────────────────────────────────────────────
{"themes":["attachment"],"type":"self_awareness","depth":1,"emotions":["clinging","longing"],"concepts":["detachment"],
"en":"What are you most afraid of losing right now — and how much of your day is organized around keeping it?",
"hi":"अभी आप किसे खोने से सबसे अधिक डरते हैं — और आपका दिन उसे बनाए रखने के इर्द-गिर्द कितना व्यवस्थित है?",
"hinglish":"Abhi aap kise khoye se sabse zyada darte hain — aur aapka din use banaye rakhne ke ird-gird kitna set hai?"},

{"themes":["attachment"],"type":"self_awareness","depth":1,"emotions":["worry","possessiveness"],"concepts":["detachment"],
"en":"What would it feel like to hold this thing you love more lightly — not to lose it, but simply to grip less tightly?",
"hi":"जिसे आप प्यार करते हैं उसे थोड़ा हल्के से थामना कैसा लगेगा — उसे खोने के लिए नहीं, बस कम कसकर पकड़ने के लिए?",
"hinglish":"Jise aap pyar karte hain use thoda halke se thamna kaisa lagega — use khoye ke liye nahi, bas kam kaskar pakadne ke liye?"},

{"themes":["attachment"],"type":"self_awareness","depth":2,"emotions":["clinging","fear of loss"],"concepts":["detachment","impermanence"],
"en":"When you imagine this thing being taken away — what story about yourself goes with it?",
"hi":"जब आप कल्पना करते हैं कि यह चीज़ छिन जाए — तो उसके साथ अपने बारे में कौन-सी कहानी भी जाती है?",
"hinglish":"Jab aap kalpana karte hain ki yeh cheez chhin jaaye — toh us ke saath apne baare mein kaun si kahani bhi jaati hai?"},

{"themes":["attachment"],"type":"self_awareness","depth":2,"emotions":["possessiveness","desire"],"concepts":["ego","detachment"],
"en":"What do you believe this person or thing gives you that you cannot find within yourself?",
"hi":"आप क्या मानते हैं कि यह व्यक्ति या चीज़ आपको वह देती है जो आप खुद के भीतर नहीं पा सकते?",
"hinglish":"Aap kya maante hain ki yeh insaan ya cheez aapko woh deti hai jo aap khud ke andar nahi pa sakte?"},

{"themes":["attachment"],"type":"self_awareness","depth":3,"emotions":["clinging","grief","fear"],"concepts":["detachment","witness-self","ego"],
"en":"If this attachment were to dissolve — not violently, but gently — what would you discover about who you are without it?",
"hi":"यदि यह आसक्ति धीरे-धीरे — हिंसा नहीं, बल्कि कोमलता से — विलीन हो जाए, तो आप इसके बिना अपने बारे में क्या खोजेंगे?",
"hinglish":"Agar yeh attachment dheere-dheere — hinsa nahi, balki komalata se — vilin ho jaaye, toh aap iske bina apne baare mein kya khojenge?"},

{"themes":["attachment"],"type":"self_awareness","depth":3,"emotions":["clinging","shame"],"concepts":["ego","detachment","karma"],
"en":"What part of you insists that your happiness depends on this — and when did that part make that decision?",
"hi":"आपका कौन-सा हिस्सा जोर देता है कि आपकी खुशी इस पर निर्भर करती है — और उस हिस्से ने यह निर्णय कब लिया था?",
"hinglish":"Aapka kaun sa hissa zor deta hai ki aapki khushi is par nirbhar karti hai — aur us hisse ne yeh faisla kab liya tha?"},

{"themes":["attachment"],"type":"action_oriented","depth":1,"emotions":["clinging","worry"],"concepts":["karma","detachment"],
"en":"What is one thing you could do today that comes from love rather than from fear of losing?",
"hi":"आज एक चीज़ क्या है जो आप खोने के डर से नहीं, बल्कि प्रेम से कर सकते हैं?",
"hinglish":"Aaj ek cheez kya hai jo aap khoye ke dar se nahi, balki prem se kar sakte hain?"},

{"themes":["attachment"],"type":"action_oriented","depth":2,"emotions":["clinging","resistance"],"concepts":["karma","detachment","svadharma"],
"en":"If you acted on this situation from a place of giving rather than of holding — what would change in how you act?",
"hi":"यदि आप इस स्थिति में थामने की जगह देने की भावना से कार्य करें — तो आपके कार्य करने के तरीके में क्या बदलेगा?",
"hinglish":"Agar aap is situation mein thamne ki jagah dene ki bhaawna se kaam karein — toh aapke kaam karne ke tarike mein kya badlega?"},

{"themes":["attachment"],"type":"action_oriented","depth":3,"emotions":["grief","resistance"],"concepts":["karma","surrender","detachment"],
"en":"What would it look like to fully commit to this — pouring yourself into it — while holding the outcome in an open hand?",
"hi":"यह कैसा दिखेगा जब आप इसमें पूरी तरह समर्पित हों — खुद को इसमें उँडेल दें — लेकिन परिणाम को खुले हाथ में थामें?",
"hinglish":"Yeh kaisa dikhega jab aap ismein poori tarah sarmpit hon — khud ko ismein undel dein — lekin natija ko khule haath mein thamein?"},

{"themes":["attachment"],"type":"spiritual","depth":1,"emotions":["longing","clinging"],"concepts":["detachment","impermanence"],
"en":"What if this thing you are holding so tightly was always only passing through you — never truly yours to keep?",
"hi":"क्या हो यदि जिसे आप इतनी कसकर थामे हैं वह हमेशा केवल आपसे होकर गुज़र रहा था — कभी सच में आपका नहीं था?",
"hinglish":"Kya ho agar jise aap itni kaskar thame hain woh hamesha sirf aapse hokar guzar raha tha — kabhi sach mein aapka nahi tha?"},

{"themes":["attachment"],"type":"spiritual","depth":2,"emotions":["clinging","grief"],"concepts":["detachment","impermanence","equanimity"],
"en":"The Gita speaks of acting without clinging to the fruit — what would your relationship to this look like if you truly lived that teaching?",
"hi":"गीता फल की आसक्ति के बिना कर्म करने की बात करती है — यदि आप सच में इस शिक्षा को जीते, तो इससे आपका संबंध कैसा दिखता?",
"hinglish":"Gita phal ki aasakti ke bina karm karne ki baat karti hai — agar aap sach mein is shiksha ko jeete, toh isse aapka sambandh kaisa dikhta?"},

{"themes":["attachment"],"type":"spiritual","depth":3,"emotions":["fear","existential clinging"],"concepts":["detachment","ego","witness-self"],
"en":"If the self that is clinging were also impermanent — as temporary as the thing it clings to — what would remain that could not be lost?",
"hi":"यदि जो स्वयं आसक्त है वह भी अनित्य हो — जिससे वह चिपका है उतना ही क्षणिक — तो क्या शेष बचेगा जिसे खोया नहीं जा सकता?",
"hinglish":"Agar jo khud aasakt hai woh bhi anitya ho — jisse woh chipka hai utna hi kshanik — toh kya shesh bachega jise khoya nahi ja sakta?"},

# ── COMPARISON ──────────────────────────────────────────────────────────────
{"themes":["comparison"],"type":"self_awareness","depth":1,"emotions":["inadequacy","envy"],"concepts":["svadharma"],
"en":"When you compare yourself to someone and feel smaller — what exactly are you measuring, and did you choose that measure?",
"hi":"जब आप खुद की किसी से तुलना करते हैं और छोटा महसूस करते हैं — आप ठीक क्या माप रहे हैं, और क्या आपने यह पैमाना चुना था?",
"hinglish":"Jab aap khud ki kisi se tulna karte hain aur chhota feel karte hain — aap theek kya maap rahe hain, aur kya aapne yeh scale chuna tha?"},

{"themes":["comparison"],"type":"self_awareness","depth":1,"emotions":["inadequacy","restlessness"],"concepts":["svadharma"],
"en":"Who is it that you most compare yourself to — and what is it you secretly believe they have that you do not?",
"hi":"आप खुद की तुलना सबसे अधिक किससे करते हैं — और आप मन में क्या मानते हैं कि उनके पास है जो आपके पास नहीं?",
"hinglish":"Aap khud ki tulna sabse zyada kisse karte hain — aur aap man mein kya maante hain ki unke paas hai jo aapke paas nahi?"},

{"themes":["comparison"],"type":"self_awareness","depth":2,"emotions":["inadequacy","shame","envy"],"concepts":["svadharma","ego"],
"en":"What does it say about your own path that you so often evaluate it by someone else's distance traveled?",
"hi":"आपके अपने मार्ग के बारे में यह क्या कहता है कि आप उसे इतनी बार किसी और की तय की हुई दूरी से आँकते हैं?",
"hinglish":"Aapke apne raaste ke baare mein yeh kya kehta hai ki aap use itni baar kisi aur ki tay ki hui doori se aankate hain?"},

{"themes":["comparison"],"type":"self_awareness","depth":2,"emotions":["inadequacy","resentment"],"concepts":["ego","svadharma"],
"en":"When the comparing mind quiets — even for a moment — what do you notice about yourself that it usually drowns out?",
"hi":"जब तुलना करने वाला मन — एक पल के लिए भी — शांत होता है, तो आप अपने बारे में क्या नोटिस करते हैं जिसे वह आमतौर पर दबा देता है?",
"hinglish":"Jab tulna karne wala mann — ek pal ke liye bhi — shant hota hai, toh aap apne baare mein kya notice karte hain jise woh aam taur par daba deta hai?"},

{"themes":["comparison"],"type":"self_awareness","depth":3,"emotions":["shame","inadequacy","envy"],"concepts":["ego","witness-self","svadharma"],
"en":"If the person you envy were to disappear from your awareness entirely — what would be left for you to want, and what would be left of who you think you are?",
"hi":"यदि जिस व्यक्ति से आप ईर्ष्या करते हैं वह आपकी जागरूकता से पूरी तरह गायब हो जाए — तो आपके चाहने के लिए क्या बचेगा, और आप जो सोचते हैं कि आप हैं उसमें से क्या शेष रहेगा?",
"hinglish":"Agar jis insaan se aap irshya karte hain woh aapki awareness se poori tarah gayab ho jaaye — toh aapke chahne ke liye kya bachega, aur aap jo sochte hain ki aap hain us mein se kya reh jaayega?"},

{"themes":["comparison"],"type":"self_awareness","depth":3,"emotions":["inadequacy","ego","shame"],"concepts":["ego","svadharma","witness-self"],
"en":"What would you have to believe about your own path to make the comparison irrelevant — and why is that belief so difficult to hold?",
"hi":"आपको अपने मार्ग के बारे में क्या विश्वास करना होगा ताकि तुलना अप्रासंगिक हो जाए — और वह विश्वास रखना इतना कठिन क्यों है?",
"hinglish":"Aapko apne raaste ke baare mein kya vishwas karna hoga taaki tulna irrelevant ho jaaye — aur woh vishwas rakhna itna mushkil kyun hai?"},

{"themes":["comparison"],"type":"action_oriented","depth":1,"emotions":["inadequacy","restlessness"],"concepts":["svadharma","karma"],
"en":"If you could not see what anyone else was doing today — what would you choose to do with your energy?",
"hi":"यदि आज आप किसी और को क्या कर रहा है देख नहीं सकते — तो आप अपनी ऊर्जा के साथ क्या करना चुनते?",
"hinglish":"Agar aaj aap kisi aur ko kya kar raha hai dekh nahi sakte — toh aap apni urja ke saath kya karna chunte?"},

{"themes":["comparison"],"type":"action_oriented","depth":2,"emotions":["inadequacy","restlessness"],"concepts":["svadharma","karma"],
"en":"What is one thing only you can do — shaped by your exact life and nature — that no one else could do in quite the same way?",
"hi":"एक ऐसी चीज़ क्या है जो केवल आप कर सकते हैं — आपके अपने जीवन और स्वभाव से ढली — जो कोई और बिल्कुल उसी तरह नहीं कर सकता?",
"hinglish":"Ek aisi cheez kya hai jo sirf aap kar sakte hain — aapke apne jeevan aur swabhaav se dhali — jo koi aur bilkul usi tarah nahi kar sakta?"},

{"themes":["comparison"],"type":"action_oriented","depth":3,"emotions":["inadequacy","envy","shame"],"concepts":["svadharma","karma","dharma"],
"en":"If you committed fully to your own path — not the path that looks impressive, but the one that is truly yours — what would you have to stop doing?",
"hi":"यदि आप अपने मार्ग पर पूरी तरह समर्पित हों — वह नहीं जो प्रभावशाली दिखता है, बल्कि वह जो सच में आपका है — तो आपको क्या करना बंद करना होगा?",
"hinglish":"Agar aap apne raaste par poori tarah sarmpit hon — woh nahi jo impressive dikhta hai, balki woh jo sach mein aapka hai — toh aapko kya karna band karna hoga?"},

{"themes":["comparison"],"type":"spiritual","depth":1,"emotions":["inadequacy","restlessness"],"concepts":["svadharma"],
"en":"The Gita says it is better to walk your own path imperfectly than another's perfectly — what does that leave you with today?",
"hi":"गीता कहती है कि अपने मार्ग पर अपूर्णता से चलना किसी और के मार्ग पर पूर्णता से चलने से बेहतर है — आज यह आपके पास क्या छोड़ता है?",
"hinglish":"Gita kehti hai ki apne raaste par apurnata se chalna kisi aur ke raaste par purnata se chalne se behtar hai — aaj yeh aapke paas kya chhodta hai?"},

{"themes":["comparison"],"type":"spiritual","depth":2,"emotions":["envy","inadequacy"],"concepts":["svadharma","ego"],
"en":"What if every soul were given exactly the terrain it needs — and what you see in others is not evidence of your lack, but of their particular lesson?",
"hi":"क्या हो यदि हर आत्मा को ठीक वही भूमि दी गई हो जो उसे चाहिए — और दूसरों में जो आप देखते हैं वह आपकी कमी का प्रमाण नहीं, बल्कि उनके विशेष पाठ का?",
"hinglish":"Kya ho agar har aatma ko theek wahi zameen mili ho jo use chahiye — aur doosron mein jo aap dekhte hain woh aapki kami ka praman nahi, balki unke vishesh paath ka?"},

{"themes":["comparison"],"type":"spiritual","depth":3,"emotions":["shame","inadequacy","existential"],"concepts":["svadharma","ego","witness-self"],
"en":"If there were no other person to measure yourself against — if comparison itself dissolved — what would you discover about what you actually long for?",
"hi":"यदि खुद को मापने के लिए कोई और न हो — यदि तुलना स्वयं विलीन हो जाए — तो आप क्या खोजेंगे कि आप वास्तव में किसकी लालसा रखते हैं?",
"hinglish":"Agar khud ko maapne ke liye koi aur na ho — agar tulna khud vilin ho jaaye — toh aap kya khojenge ki aap asal mein kiska lalsa rakhte hain?"},

# ── CONTROL ─────────────────────────────────────────────────────────────────
{"themes":["control"],"type":"self_awareness","depth":1,"emotions":["tension","anxiety"],"concepts":["surrender","karma"],
"en":"What in this situation are you actually able to influence — and what are you spending most of your energy on?",
"hi":"इस स्थिति में आप वास्तव में क्या प्रभावित कर सकते हैं — और अपनी अधिकांश ऊर्जा किस पर खर्च कर रहे हैं?",
"hinglish":"Is situation mein aap asal mein kya influence kar sakte hain — aur apni zyaadatar urja kis par kharch kar rahe hain?"},

{"themes":["control"],"type":"self_awareness","depth":1,"emotions":["frustration","anxiety"],"concepts":["surrender"],
"en":"When things slip beyond your control, what is the first thing that happens inside you?",
"hi":"जब चीज़ें आपके नियंत्रण से बाहर जाने लगती हैं — तो आपके भीतर सबसे पहले क्या होता है?",
"hinglish":"Jab cheezein aapke control se bahar jaane lagti hain — toh aapke andar sabse pehle kya hota hai?"},

{"themes":["control"],"type":"self_awareness","depth":2,"emotions":["anxiety","resistance"],"concepts":["surrender","ego"],
"en":"What does the need to control this situation protect you from feeling?",
"hi":"इस स्थिति को नियंत्रित करने की ज़रूरत आपको क्या महसूस करने से बचाती है?",
"hinglish":"Is situation ko control karne ki zaroorat aapko kya feel karne se bachati hai?"},

{"themes":["control"],"type":"self_awareness","depth":2,"emotions":["fear","tension"],"concepts":["ego","surrender"],
"en":"What would it mean about you if this did not go the way you planned — and whose judgment are you most afraid of?",
"hi":"यदि यह आपकी योजना के अनुसार न हो — तो इसका आपके बारे में क्या अर्थ होगा, और आप किसके निर्णय से सबसे अधिक डरते हैं?",
"hinglish":"Agar yeh aapki plan ke hisaab se na ho — toh iska aapke baare mein kya matlab hoga, aur aap kiske faisle se sabse zyada darte hain?"},

{"themes":["control"],"type":"self_awareness","depth":3,"emotions":["fear","shame","existential"],"concepts":["ego","surrender","witness-self"],
"en":"Underneath the need to control, what is the deeper belief — about the world, or about what happens to you when things fall apart?",
"hi":"नियंत्रण की ज़रूरत के नीचे — गहरी मान्यता क्या है — दुनिया के बारे में, या इस बारे में कि जब चीज़ें बिखर जाती हैं तो आपके साथ क्या होता है?",
"hinglish":"Control ki zaroorat ke neeche — gehri manyata kya hai — duniya ke baare mein, ya is baare mein ki jab cheezein bikhar jaati hain toh aapke saath kya hota hai?"},

{"themes":["control"],"type":"self_awareness","depth":3,"emotions":["existential fear","clinging"],"concepts":["ego","witness-self","impermanence"],
"en":"If you truly accepted that you cannot control this — not as defeat, but as reality — what might become possible that isn't right now?",
"hi":"यदि आप सच में स्वीकार कर लें कि आप इसे नियंत्रित नहीं कर सकते — हार के रूप में नहीं, बल्कि वास्तविकता के रूप में — तो क्या संभव हो सकता है जो अभी नहीं है?",
"hinglish":"Agar aap sach mein sweekar kar lein ki aap ise control nahi kar sakte — haar ke roop mein nahi, balki haqeeqat ke roop mein — toh kya sambhav ho sakta hai jo abhi nahi hai?"},

{"themes":["control"],"type":"action_oriented","depth":1,"emotions":["tension","anxiety"],"concepts":["karma","svadharma"],
"en":"In this situation, what is the one thing that is entirely yours to do — and have you done it?",
"hi":"इस स्थिति में, एक चीज़ जो पूरी तरह आपकी है करने के लिए — क्या आपने वह की है?",
"hinglish":"Is situation mein, ek cheez jo poori tarah aapki hai karne ke liye — kya aapne woh ki hai?"},

{"themes":["control"],"type":"action_oriented","depth":2,"emotions":["resistance","frustration"],"concepts":["karma","detachment"],
"en":"What would it look like to put your full energy into what you can do — and genuinely release what you cannot?",
"hi":"यह कैसा दिखेगा जब आप जो कर सकते हैं उसमें अपनी पूरी ऊर्जा लगाएं — और जो नहीं कर सकते उसे सच में छोड़ दें?",
"hinglish":"Yeh kaisa dikhega jab aap jo kar sakte hain us mein apni poori urja lagaein — aur jo nahi kar sakte use sach mein chhod dein?"},

{"themes":["control"],"type":"action_oriented","depth":3,"emotions":["resistance","grief"],"concepts":["karma","surrender","detachment"],
"en":"If you acted from your deepest values — not from the need to guarantee the outcome — what would you do that you are not doing?",
"hi":"यदि आप अपने गहरे मूल्यों से कार्य करें — परिणाम की गारंटी की ज़रूरत से नहीं — तो आप क्या करेंगे जो अभी नहीं कर रहे?",
"hinglish":"Agar aap apne gehre mulyon se kaam karein — natija guarantee karne ki zaroorat se nahi — toh aap kya karenge jo abhi nahi kar rahe?"},

{"themes":["control"],"type":"spiritual","depth":1,"emotions":["tension","worry"],"concepts":["surrender","karma"],
"en":"What might open up if you treated this situation as something to move through rather than something to master?",
"hi":"यदि आप इस स्थिति को महारत हासिल करने की चीज़ के बजाय — इससे गुज़रने की चीज़ के रूप में देखें — तो क्या खुल सकता है?",
"hinglish":"Agar aap is situation ko maharat haasil karne ki cheez ke bajaaye — isse guzarne ki cheez ke roop mein dekhein — toh kya khul sakta hai?"},

{"themes":["control"],"type":"spiritual","depth":2,"emotions":["resistance","fear"],"concepts":["surrender","equanimity"],
"en":"The Gita points toward acting fully and releasing the fruit entirely — what would it ask of you to live that way in this situation?",
"hi":"गीता पूरी तरह कार्य करने और फल को पूरी तरह छोड़ने की ओर इशारा करती है — इस स्थिति में उस तरह जीना आपसे क्या माँगेगा?",
"hinglish":"Gita poori tarah kaam karne aur phal ko poori tarah chhodne ki taraf ishara karti hai — is situation mein us tarah jeena aapse kya maangega?"},

{"themes":["control"],"type":"spiritual","depth":3,"emotions":["existential fear","clinging"],"concepts":["surrender","witness-self","impermanence"],
"en":"What would it mean to trust — not that things will go right, but that the deeper self watching all of this is not in danger?",
"hi":"इसका क्या अर्थ होगा कि विश्वास करें — यह नहीं कि सब ठीक होगा, बल्कि यह कि यह सब देखने वाला गहरा स्वयं खतरे में नहीं है?",
"hinglish":"Iska kya matlab hoga ki trust karein — yeh nahi ki sab theek hoga, balki yeh ki yeh sab dekhne wala gehra khud khatre mein nahi hai?"},

# ── DESIRE ──────────────────────────────────────────────────────────────────
{"themes":["desire"],"type":"self_awareness","depth":1,"emotions":["longing","craving"],"concepts":["detachment"],
"en":"What is it you are truly hungry for — and is what you are chasing the thing itself, or what you believe it will make you feel?",
"hi":"आप सच में किसके लिए भूखे हैं — और जो आप पाने की कोशिश कर रहे हैं वह चीज़ खुद है, या जो आप मानते हैं वह आपको कैसा महसूस कराएगी?",
"hinglish":"Aap sach mein kiske liye bhookhe hain — aur jo aap paane ki koshish kar rahe hain woh cheez khud hai, ya jo aap maante hain woh aapko kaisa feel karaayegi?"},

{"themes":["desire"],"type":"self_awareness","depth":1,"emotions":["craving","restlessness"],"concepts":["desire","equanimity"],
"en":"When this desire is satisfied, how long before the next one arises — and what does that pattern tell you?",
"hi":"जब यह इच्छा पूरी होती है — कितने समय बाद अगली उठती है, और यह पैटर्न आपको क्या बताता है?",
"hinglish":"Jab yeh ichha poori hoti hai — kitne samay baad agli uthti hai, aur yeh pattern aapko kya batata hai?"},

{"themes":["desire"],"type":"self_awareness","depth":2,"emotions":["longing","shame"],"concepts":["desire","ego","detachment"],
"en":"What does this particular desire say about what you believe you are missing — and when did you decide you were missing it?",
"hi":"यह विशेष इच्छा उस कमी के बारे में क्या कहती है जो आप मानते हैं आपमें है — और आपने कब तय किया कि वह कमी है?",
"hinglish":"Yeh vishesh ichha us kami ke baare mein kya kehti hai jo aap maante hain aap mein hai — aur aapne kab tay kiya ki woh kami hai?"},

{"themes":["desire"],"type":"self_awareness","depth":2,"emotions":["craving","shame"],"concepts":["desire","ego"],
"en":"Is this something you genuinely want — or something you want because you have watched others want it?",
"hi":"क्या यह कुछ ऐसा है जो आप सच में चाहते हैं — या कुछ ऐसा जो आप इसलिए चाहते हैं क्योंकि आपने दूसरों को इसे चाहते देखा है?",
"hinglish":"Kya yeh kuch aisa hai jo aap sach mein chahte hain — ya kuch aisa jo aap isliye chahte hain kyunki aapne doosron ko ise chahte dekha hai?"},

{"themes":["desire"],"type":"self_awareness","depth":3,"emotions":["longing","existential"],"concepts":["desire","ego","witness-self"],
"en":"What is the oldest want you carry — the one beneath all the others — and what would it mean to finally turn toward it honestly?",
"hi":"आप जो सबसे पुरानी चाहत लेकर चलते हैं — बाकी सब के नीचे वाली — उसका क्या अर्थ होगा यदि आप अंततः उसकी ओर ईमानदारी से मुड़ें?",
"hinglish":"Aap jo sabse purani chaahat lekar chalte hain — baaki sab ke neeche wali — uska kya matlab hoga agar aap aakhirkar uski taraf imaandaari se mudein?"},

{"themes":["desire"],"type":"self_awareness","depth":3,"emotions":["craving","shame","existential"],"concepts":["desire","ego","detachment"],
"en":"If you got everything you currently desire — completely and immediately — what would be the first new thing you would want, and what does that tell you?",
"hi":"यदि आप जो अभी चाहते हैं वह सब मिल जाए — पूरी तरह और तुरंत — तो पहली नई चीज़ क्या होगी जो आप चाहेंगे, और यह आपको क्या बताती है?",
"hinglish":"Agar aap jo abhi chahte hain woh sab mil jaaye — poori tarah aur turant — toh pehli nayi cheez kya hogi jo aap chahenge, aur yeh aapko kya batati hai?"},

{"themes":["desire"],"type":"action_oriented","depth":1,"emotions":["longing","craving"],"concepts":["karma","svadharma"],
"en":"What would you pursue today if you were guided by what truly nourishes you rather than what merely excites you?",
"hi":"यदि आज आप उससे निर्देशित हों जो आपको सच में पोषण देता है न कि जो केवल उत्साहित करता है — तो आप क्या करते?",
"hinglish":"Agar aaj aap us se nirdeshit hon jo aapko sach mein poshan deta hai na ki jo sirf utsahit karta hai — toh aap kya karte?"},

{"themes":["desire"],"type":"action_oriented","depth":2,"emotions":["craving","resistance"],"concepts":["karma","detachment"],
"en":"What would it look like to move toward what you want without making your peace contingent on getting it?",
"hi":"यह कैसा दिखेगा कि आप जो चाहते हैं उसकी ओर बढ़ें — लेकिन अपनी शांति को उसे पाने पर निर्भर न करें?",
"hinglish":"Yeh kaisa dikhega ki aap jo chahte hain uski taraf badein — lekin apni shanti ko use paane par nirbhar na karein?"},

{"themes":["desire"],"type":"action_oriented","depth":3,"emotions":["longing","craving","grief"],"concepts":["karma","detachment","dharma"],
"en":"What if you channeled the energy of this desire into your duty — not to suppress the want, but to let it fuel the work?",
"hi":"क्या हो यदि आप इस इच्छा की ऊर्जा को अपने कर्तव्य में लगाएं — चाहत को दबाने के लिए नहीं, बल्कि उसे काम का ईंधन बनाने के लिए?",
"hinglish":"Kya ho agar aap is ichha ki urja ko apne kartavya mein lagaein — chaahat ko dabane ke liye nahi, balki use kaam ka indhan banane ke liye?"},

{"themes":["desire"],"type":"spiritual","depth":1,"emotions":["longing","craving"],"concepts":["desire","equanimity"],
"en":"What is beneath this wanting — the deeper thirst that this desire is pointing toward but can never quite satisfy?",
"hi":"इस चाहत के नीचे क्या है — वह गहरी प्यास जिसकी ओर यह इच्छा इशारा करती है लेकिन जिसे कभी पूरी तरह बुझा नहीं सकती?",
"hinglish":"Is chaahat ke neeche kya hai — woh gehri pyas jiski taraf yeh ichha ishara karti hai lekin jise kabhi poori tarah bujha nahi sakti?"},

{"themes":["desire"],"type":"spiritual","depth":2,"emotions":["longing","restlessness"],"concepts":["desire","ego","surrender"],
"en":"What if this restless longing is not a problem to be solved but a sign pointing toward something the world cannot give?",
"hi":"क्या हो यदि यह बेचैन लालसा कोई समस्या नहीं है जिसे सुलझाया जाए — बल्कि एक संकेत है जो उस ओर इशारा करता है जो दुनिया नहीं दे सकती?",
"hinglish":"Kya ho agar yeh bechaini wali lalsa koi samasya nahi hai jise suljhaya jaaye — balki ek sanket hai jo us taraf ishara karta hai jo duniya nahi de sakti?"},

{"themes":["desire"],"type":"spiritual","depth":3,"emotions":["longing","existential","craving"],"concepts":["desire","ego","witness-self"],
"en":"If the one who desires were also seen through — if the self that wants were as empty as what it reaches for — what would remain?",
"hi":"यदि जो इच्छा करता है उसे भी देखा जाए — यदि जो चाहता है वह स्वयं भी उतना ही रिक्त हो जितना जिसके लिए वह पहुँचता है — तो क्या शेष बचेगा?",
"hinglish":"Agar jo ichha karta hai use bhi dekha jaaye — agar jo chahta hai woh khud bhi utna hi rikt ho jitna jiske liye woh pahunchta hai — toh kya shesh bachega?"},
]

INTENSITY_FLOORS = {1: "any", 2: "mild", 3: "moderate"}

def main():
    import sys
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
    print(f"Batch 1 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
