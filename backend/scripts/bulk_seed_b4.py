"""Bulk seed batch 4: loneliness, marriage, money, parenting, purpose."""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── LONELINESS ───────────────────────────────────────────────────────────────
{"themes":["loneliness"],"type":"self_awareness","depth":1,"emotions":["loneliness","longing"],"concepts":["ego","surrender"],
"en":"When you feel most alone — what is it you are most longing for in that moment?",
"hi":"जब आप सबसे अधिक अकेला महसूस करते हैं — उस क्षण में आप सबसे अधिक किसके लिए तरस रहे होते हैं?",
"hinglish":"Jab aap sabse zyada akela mahsoos karte hain — us pal mein aap sabse zyada kiske liye taras rahe hote hain?"},

{"themes":["loneliness"],"type":"self_awareness","depth":1,"emotions":["loneliness","sadness"],"concepts":["witness-self"],
"en":"Is the loneliness about the absence of people — or about something more interior that their presence could not fill?",
"hi":"क्या यह एकाकीपन लोगों की अनुपस्थिति के बारे में है — या कुछ अधिक आंतरिक है जिसे उनकी उपस्थिति भी नहीं भर सकती?",
"hinglish":"Kya yeh akalapan logon ki anupasthiti ke baare mein hai — ya kuch zyada aantarik hai jise unki upasthiti bhi nahi bhar sakti?"},

{"themes":["loneliness"],"type":"self_awareness","depth":2,"emotions":["loneliness","shame"],"concepts":["ego","witness-self"],
"en":"What part of yourself do you hide from others that contributes to feeling unseen — and why do you keep it hidden?",
"hi":"अपने किस हिस्से को आप दूसरों से छुपाते हैं जो न देखे जाने की भावना में योगदान करता है — और आप उसे क्यों छुपाए रखते हैं?",
"hinglish":"Apne kis hisse ko aap doosron se chupaate hain jo na dekhe jaane ki bhaawna mein yogdaan karta hai — aur aap use kyun chhupaaye rakhte hain?"},

{"themes":["loneliness"],"type":"self_awareness","depth":2,"emotions":["loneliness","longing"],"concepts":["ego","attachment"],
"en":"What kind of connection are you actually hungry for — and is that the kind you have been reaching for?",
"hi":"आप वास्तव में किस प्रकार के जुड़ाव के लिए भूखे हैं — और क्या वह वही है जिसके लिए आप पहुँचते रहे हैं?",
"hinglish":"Aap asal mein kis prakar ke judav ke liye bhookhe hain — aur kya woh wahi hai jiske liye aap pahunchte rahe hain?"},

{"themes":["loneliness"],"type":"self_awareness","depth":3,"emotions":["loneliness","existential","shame"],"concepts":["ego","witness-self"],
"en":"What if the deepest loneliness is not the absence of others but estrangement from yourself — from the part of you you have not yet befriended?",
"hi":"क्या हो यदि सबसे गहरा एकाकीपन दूसरों की अनुपस्थिति नहीं है बल्कि खुद से — अपने उस हिस्से से — अलगाव है जिससे आप अभी तक दोस्ती नहीं कर पाए?",
"hinglish":"Kya ho agar sabse gehra akalapan doosron ki anupasthiti nahi hai balki khud se — apne us hisse se — algaav hai jisse aap abhi tak dosti nahi kar paaye?"},

{"themes":["loneliness"],"type":"self_awareness","depth":3,"emotions":["loneliness","grief","existential"],"concepts":["ego","witness-self","attachment"],
"en":"If you sat with this loneliness rather than escaping it — fully present to it — what might it be trying to show you?",
"hi":"यदि आप इस एकाकीपन के साथ बैठें बजाय इससे भागने के — इसमें पूरी तरह उपस्थित रहकर — यह आपको क्या दिखाने की कोशिश कर रहा है?",
"hinglish":"Agar aap is akalapan ke saath baithen is se bhaagne ki jagah — ismein poori tarah maujood rehkar — yeh aapko kya dikhane ki koshish kar raha hai?"},

{"themes":["loneliness"],"type":"action_oriented","depth":1,"emotions":["loneliness","isolation"],"concepts":["karma"],
"en":"What is one genuine gesture of reaching out — to another person, or to this moment itself — that you could make today?",
"hi":"एक वास्तविक हाथ बढ़ाने का इशारा — किसी अन्य व्यक्ति की ओर, या इस क्षण की ओर — जो आप आज कर सकते हैं, क्या है?",
"hinglish":"Ek asli haath badhaane ka ishara — kisi aur insaan ki taraf, ya is pal ki taraf — jo aap aaj kar sakte hain, kya hai?"},

{"themes":["loneliness"],"type":"action_oriented","depth":2,"emotions":["loneliness","resistance"],"concepts":["karma","svadharma"],
"en":"What barrier — internal or external — most prevents you from creating the kind of connection you long for?",
"hi":"कौन-सी बाधा — आंतरिक या बाह्य — आपको सबसे अधिक उस जुड़ाव को बनाने से रोकती है जिसके लिए आप तरसते हैं?",
"hinglish":"Kaun si badha — aantarik ya baahri — aapko sabse zyada us judav ko banane se rokti hai jiske liye aap taraste hain?"},

{"themes":["loneliness"],"type":"action_oriented","depth":3,"emotions":["loneliness","grief","shame"],"concepts":["karma","dharma","attachment"],
"en":"What would it mean to risk being truly seen by someone — to let them encounter the parts of you that feel most alone?",
"hi":"किसी के द्वारा सच में देखे जाने का जोखिम उठाने का क्या अर्थ होगा — उन्हें अपने उन हिस्सों से मिलने देना जो सबसे अधिक अकेले महसूस करते हैं?",
"hinglish":"Kisi ke dwara sach mein dekhe jaane ka jokhim uthane ka kya matlab hoga — unhe apne un hisson se milne dena jo sabse zyada akele feel karte hain?"},

{"themes":["loneliness"],"type":"spiritual","depth":1,"emotions":["loneliness","longing"],"concepts":["witness-self","surrender"],
"en":"What if you were never truly alone — what if there is something in you that is always present, always aware, always whole?",
"hi":"क्या हो यदि आप कभी सच में अकेले नहीं हैं — यदि आपमें कुछ ऐसा है जो हमेशा उपस्थित है, हमेशा सजग है, हमेशा पूर्ण है?",
"hinglish":"Kya ho agar aap kabhi sach mein akele nahi hain — agar aap mein kuch aisa hai jo hamesha maujood hai, hamesha sajag hai, hamesha poorn hai?"},

{"themes":["loneliness"],"type":"spiritual","depth":2,"emotions":["loneliness","longing"],"concepts":["witness-self","ego","surrender"],
"en":"The sages speak of a stillness beneath all experience that is never lonely because it is never separate — have you ever touched that in yourself?",
"hi":"ऋषि सभी अनुभवों के नीचे एक ऐसी शांति की बात करते हैं जो कभी अकेली नहीं है क्योंकि वह कभी अलग नहीं है — क्या आपने कभी अपने भीतर उसे छुआ है?",
"hinglish":"Rishi sabhi anubhavon ke neeche ek aisi shanti ki baat karte hain jo kabhi akeli nahi hai kyunki woh kabhi alag nahi hai — kya aapne kabhi apne andar use chhua hai?"},

{"themes":["loneliness"],"type":"spiritual","depth":3,"emotions":["loneliness","existential","longing"],"concepts":["witness-self","ego","surrender","impermanence"],
"en":"What if loneliness itself is pointing — not at what is absent from your life, but at the yearning of the individual self to return to something it came from?",
"hi":"क्या हो यदि एकाकीपन इशारा कर रहा है — आपके जीवन में जो अनुपस्थित है उसकी ओर नहीं, बल्कि व्यक्तिगत स्वयं की उस लालसा की ओर जो उस चीज़ में वापस लौटना चाहता है जिससे वह आया था?",
"hinglish":"Kya ho agar akalapan ishara kar raha hai — aapke jeevan mein jo anupasthit hai uski taraf nahi, balki vyaktigat khud ki us lalsa ki taraf jo us cheez mein wapas lautna chahta hai jisse woh aaya tha?"},

# ── MARRIAGE ────────────────────────────────────────────────────────────────
{"themes":["marriage"],"type":"self_awareness","depth":1,"emotions":["frustration","longing"],"concepts":["relationships","dharma"],
"en":"What do you most wish your partner understood about you — and have you truly tried to show them?",
"hi":"आप सबसे अधिक क्या चाहते हैं कि आपका साथी आपके बारे में समझे — और क्या आपने उन्हें दिखाने की वास्तव में कोशिश की है?",
"hinglish":"Aap sabse zyada kya chahte hain ki aapka saathi aapke baare mein samjhe — aur kya aapne unhe dikhane ki asal mein koshish ki hai?"},

{"themes":["marriage"],"type":"self_awareness","depth":1,"emotions":["frustration","resentment"],"concepts":["relationships","ego"],
"en":"In this relationship, where do you demand what you are not willing to give — and are you aware of doing it?",
"hi":"इस संबंध में, आप कहाँ वह माँगते हैं जो आप देने को तैयार नहीं हैं — और क्या आप ऐसा करते हुए जानते हैं?",
"hinglish":"Is rishte mein, aap kahan woh maangते hain jo aap dene ko taiyar nahi hain — aur kya aap aisa karte hue jaante hain?"},

{"themes":["marriage"],"type":"self_awareness","depth":2,"emotions":["resentment","longing","grief"],"concepts":["relationships","ego","karma"],
"en":"What are you carrying into this marriage from before it — and how much of your frustration belongs to this relationship versus that earlier story?",
"hi":"आप इस विवाह में उससे पहले से क्या लेकर आ रहे हैं — और आपकी कितनी निराशा इस संबंध की है बनाम उस पहले की कहानी की?",
"hinglish":"Aap is vivah mein us se pehle se kya lekar aa rahe hain — aur aapki kitni nirasha is rishte ki hai vs us pehle ki kahani ki?"},

{"themes":["marriage"],"type":"self_awareness","depth":2,"emotions":["longing","frustration"],"concepts":["relationships","attachment","ego"],
"en":"What would you need to see change in this relationship for it to feel alive again — and is any of that within your own power to offer first?",
"hi":"इस संबंध में क्या बदलता देखना होगा ताकि यह फिर से जीवंत लगे — और क्या उसमें से कुछ पहले खुद देने की आपकी अपनी शक्ति में है?",
"hinglish":"Is rishte mein kya badalte dekhna hoga taaki yeh phir se jeevant lage — aur kya us mein se kuch pehle khud dene ki aapki apni shakti mein hai?"},

{"themes":["marriage"],"type":"self_awareness","depth":3,"emotions":["grief","resentment","longing"],"concepts":["relationships","ego","attachment","karma"],
"en":"What version of your partner do you still hold them against — the one they were, the one you imagined, or the one you needed them to be?",
"hi":"अपने साथी के किस संस्करण से आप अभी भी उन्हें तुलना करते हैं — जो वे थे, जिसकी आपने कल्पना की थी, या जिसकी आपको ज़रूरत थी?",
"hinglish":"Apne saathi ke kis version se aap abhi bhi unhe tulna karte hain — jo woh the, jiski aapne kalpana ki thi, ya jiski aapko zaroorat thi?"},

{"themes":["marriage"],"type":"self_awareness","depth":3,"emotions":["grief","existential","longing"],"concepts":["ego","attachment","relationships","dharma"],
"en":"If you were fully honest — what is it you have outgrown together, and what is it you are afraid to name?",
"hi":"यदि आप पूरी तरह ईमानदार हों — क्या है जिसे आप दोनों साथ मिलकर पार कर गए हैं, और क्या है जिसे नाम देने से आप डरते हैं?",
"hinglish":"Agar aap poori tarah imaandaar hon — kya hai jise aap dono saath milkar paar kar gaye hain, aur kya hai jise naam dene se aap darte hain?"},

{"themes":["marriage"],"type":"action_oriented","depth":1,"emotions":["frustration","longing"],"concepts":["karma","relationships"],
"en":"What is one thing you could do today — without waiting for them to go first — that would move toward the relationship you want?",
"hi":"एक चीज़ जो आप आज कर सकते हैं — उनके पहले जाने का इंतज़ार किए बिना — जो उस संबंध की ओर बढ़ेगी जो आप चाहते हैं?",
"hinglish":"Ek cheez jo aap aaj kar sakte hain — unke pehle jaane ka intezaar kiye bina — jo us rishte ki taraf badhegi jo aap chahte hain?"},

{"themes":["marriage"],"type":"action_oriented","depth":2,"emotions":["resentment","resistance"],"concepts":["karma","dharma","detachment"],
"en":"What conversation have you been avoiding in this marriage — and what are you afraid would happen if you had it?",
"hi":"इस विवाह में आप किस बातचीत से बच रहे हैं — और यदि आप वह करें तो आपको क्या होने का डर है?",
"hinglish":"Is vivah mein aap kis baatcheet se bach rahe hain — aur agar aap woh karein toh aapko kya hone ka dar hai?"},

{"themes":["marriage"],"type":"action_oriented","depth":3,"emotions":["grief","resentment","longing"],"concepts":["karma","dharma","surrender","detachment"],
"en":"What would it look like to bring your full self into this relationship — not your defended self, not the self that is managing them, but the one that is genuinely present?",
"hi":"अपने पूरे स्वयं को इस संबंध में लाना कैसा दिखेगा — वह नहीं जो बचाव में है, वह नहीं जो उन्हें संभाल रहा है, बल्कि वह जो वास्तव में उपस्थित है?",
"hinglish":"Apne poore khud ko is rishte mein laana kaisa dikhega — woh nahi jo bachav mein hai, woh nahi jo unhe sambhaal raha hai, balki woh jo asal mein maujood hai?"},

{"themes":["marriage"],"type":"spiritual","depth":1,"emotions":["frustration","longing"],"concepts":["dharma","relationships","karma"],
"en":"What if this relationship is also a practice — a form of yoga — and what is it currently teaching you?",
"hi":"क्या हो यदि यह संबंध भी एक अभ्यास है — योग का एक रूप — और यह अभी आपको क्या सिखा रहा है?",
"hinglish":"Kya ho agar yeh rishta bhi ek abhyas hai — yoga ka ek roop — aur yeh abhi aapko kya sikha raha hai?"},

{"themes":["marriage"],"type":"spiritual","depth":2,"emotions":["resentment","grief"],"concepts":["dharma","karma","ego"],
"en":"What if your partner — in all their difficulty — is offering you the exact friction your growth requires?",
"hi":"क्या हो यदि आपका साथी — अपनी सारी कठिनाइयों के साथ — आपको वह घर्षण दे रहा है जो आपकी वृद्धि को चाहिए?",
"hinglish":"Kya ho agar aapka saathi — apni saari mushkilon ke saath — aapko woh gharshan de raha hai jo aapki wridhi ko chahiye?"},

{"themes":["marriage"],"type":"spiritual","depth":3,"emotions":["grief","longing","existential"],"concepts":["dharma","ego","attachment","witness-self"],
"en":"What would love look like in this relationship if it were not about what you receive — but about what you are willing to consistently offer?",
"hi":"इस संबंध में प्रेम कैसा दिखेगा यदि यह इस बारे में न हो कि आप क्या प्राप्त करते हैं — बल्कि इस बारे में हो कि आप लगातार क्या देने को तैयार हैं?",
"hinglish":"Is rishte mein prem kaisa dikhega agar yeh is baare mein na ho ki aap kya prapt karte hain — balki is baare mein ho ki aap lagaatar kya dene ko taiyar hain?"},

# ── MONEY ────────────────────────────────────────────────────────────────────
{"themes":["money"],"type":"self_awareness","depth":1,"emotions":["anxiety","shame"],"concepts":["desire","attachment"],
"en":"What does money represent to you beyond its practical use — what feeling does more of it promise to give you?",
"hi":"धन आपके लिए उसके व्यावहारिक उपयोग से परे क्या दर्शाता है — इसका अधिक होना आपको कौन-सी भावना देने का वादा करता है?",
"hinglish":"Dhan aapke liye uske vyavahaarik upyog se pare kya darshata hai — iska zyada hona aapko kaun si bhaawna dene ka wada karta hai?"},

{"themes":["money"],"type":"self_awareness","depth":1,"emotions":["anxiety","shame"],"concepts":["desire","fear"],
"en":"What is your earliest memory connected to money — and how does that memory still shape the way you relate to it?",
"hi":"धन से जुड़ी आपकी सबसे पुरानी याद क्या है — और वह याद अभी भी इससे आपके संबंध को कैसे आकार देती है?",
"hinglish":"Dhan se judi aapki sabse purani yaad kya hai — aur woh yaad abhi bhi isse aapke rishte ko kaise aakar deti hai?"},

{"themes":["money"],"type":"self_awareness","depth":2,"emotions":["anxiety","shame","guilt"],"concepts":["desire","ego","attachment"],
"en":"Where in your relationship with money do you act from fear rather than from choice — and what is that fear actually about?",
"hi":"धन के साथ अपने संबंध में आप कहाँ चुनाव की जगह डर से कार्य करते हैं — और वह डर वास्तव में किस बारे में है?",
"hinglish":"Dhan ke saath apne rishte mein aap kahan chunaav ki jagah dar se kaam karte hain — aur woh dar asal mein kis baare mein hai?"},

{"themes":["money"],"type":"self_awareness","depth":2,"emotions":["anxiety","shame","comparison"],"concepts":["desire","ego","comparison"],
"en":"What does how much money you have say about you — in your own mind — and where did you learn to read it that way?",
"hi":"आपके पास कितना धन है यह आपके बारे में क्या कहता है — आपके अपने मन में — और आपने इसे इस तरह पढ़ना कहाँ से सीखा?",
"hinglish":"Aapke paas kitna dhan hai yeh aapke baare mein kya kehta hai — aapke apne mann mein — aur aapne ise is tarah padhna kahan se seekha?"},

{"themes":["money"],"type":"self_awareness","depth":3,"emotions":["anxiety","shame","existential"],"concepts":["desire","ego","attachment"],
"en":"If your financial situation did not change at all — what would have to shift in you for you to feel secure?",
"hi":"यदि आपकी वित्तीय स्थिति बिल्कुल भी न बदले — सुरक्षित महसूस करने के लिए आपके भीतर क्या बदलना होगा?",
"hinglish":"Agar aapki vitteey sthiti bilkul bhi na badle — surakshit feel karne ke liye aapke andar kya badalna hoga?"},

{"themes":["money"],"type":"self_awareness","depth":3,"emotions":["shame","existential","anxiety"],"concepts":["desire","ego","detachment"],
"en":"What are you actually trading — time, attention, integrity, relationships — for the money you pursue, and is that trade worth examining?",
"hi":"आप वास्तव में क्या व्यापार कर रहे हैं — समय, ध्यान, ईमानदारी, संबंध — उस धन के लिए जो आप पाना चाहते हैं, और क्या वह व्यापार जाँचने योग्य है?",
"hinglish":"Aap asal mein kya vyapaar kar rahe hain — samay, dhyan, imaandaari, rishte — us dhan ke liye jo aap paana chahte hain, aur kya woh vyapaar jaanchne yogya hai?"},

{"themes":["money"],"type":"action_oriented","depth":1,"emotions":["anxiety","avoidance"],"concepts":["karma","dharma"],
"en":"What is one money-related decision you have been avoiding — and what would it take to face it today?",
"hi":"धन से संबंधित एक निर्णय जिससे आप बच रहे हैं — और आज उसका सामना करने के लिए क्या चाहिए?",
"hinglish":"Dhan se sambandhit ek nirnay jisse aap bach rahe hain — aur aaj uska saamna karne ke liye kya chahiye?"},

{"themes":["money"],"type":"action_oriented","depth":2,"emotions":["anxiety","shame"],"concepts":["karma","dharma","discipline"],
"en":"If you aligned your spending with your values — what would you stop spending on, and what would you spend more on?",
"hi":"यदि आप अपना खर्च अपने मूल्यों के अनुरूप करें — किस पर खर्च करना बंद करेंगे, और किस पर अधिक?",
"hinglish":"Agar aap apna kharch apne mulyon ke anuroop karein — kis par kharch karna band karenge, aur kis par zyada?"},

{"themes":["money"],"type":"action_oriented","depth":3,"emotions":["anxiety","shame","resentment"],"concepts":["karma","dharma","detachment"],
"en":"What would your relationship to money look like if you worked for what you need and gave freely from what remains — without hoarding and without scarcity thinking?",
"hi":"यदि आप जो चाहिए उसके लिए काम करें और जो शेष बचे उससे स्वतंत्र रूप से दें — जमाखोरी और कमी की सोच के बिना — तो धन के साथ आपका संबंध कैसा दिखेगा?",
"hinglish":"Agar aap jo chahiye uske liye kaam karein aur jo shesh bache us se swatantra roop se dein — jamaakhori aur kami ki soch ke bina — toh dhan ke saath aapka rishta kaisa dikhega?"},

{"themes":["money"],"type":"spiritual","depth":1,"emotions":["anxiety","longing"],"concepts":["desire","attachment","karma"],
"en":"What would it feel like to have enough — not more, just enough — and do you believe that feeling is available to you?",
"hi":"पर्याप्त होना कैसा लगेगा — अधिक नहीं, बस पर्याप्त — और क्या आप मानते हैं कि वह भावना आपके लिए उपलब्ध है?",
"hinglish":"Paryaapt hona kaisa lagega — zyada nahi, bas paryaapt — aur kya aap maante hain ki woh bhaawna aapke liye uplabdh hai?"},

{"themes":["money"],"type":"spiritual","depth":2,"emotions":["anxiety","shame"],"concepts":["desire","attachment","detachment","karma"],
"en":"The Gita speaks of using the world without being used by it — what would that look like in your relationship with money?",
"hi":"गीता दुनिया का उपयोग करने की बात करती है — उसके द्वारा उपयोग किए बिना — धन के साथ आपके संबंध में यह कैसा दिखेगा?",
"hinglish":"Gita duniya ka upyog karne ki baat karti hai — uske dwara upyog kiye bina — dhan ke saath aapke rishte mein yeh kaisa dikhega?"},

{"themes":["money"],"type":"spiritual","depth":3,"emotions":["anxiety","existential","longing"],"concepts":["desire","ego","detachment","witness-self"],
"en":"If wealth were a form of energy rather than a measure of worth — how would that change what you seek and what you share?",
"hi":"यदि धन एक प्रकार की ऊर्जा हो न कि मूल्य का माप — तो यह आप क्या खोजते हैं और क्या बाँटते हैं उसे कैसे बदल देगा?",
"hinglish":"Agar dhan ek prakar ki urja ho na ki mulya ka maap — toh yeh aap kya dhundhte hain aur kya baantate hain use kaise badal dega?"},

# ── PARENTING ────────────────────────────────────────────────────────────────
{"themes":["parenting"],"type":"self_awareness","depth":1,"emotions":["anxiety","guilt"],"concepts":["dharma","relationships"],
"en":"When you worry about your child — what specific fear sits at the center of that worry?",
"hi":"जब आप अपने बच्चे के बारे में चिंता करते हैं — उस चिंता के केंद्र में कौन-सा विशिष्ट डर है?",
"hinglish":"Jab aap apne bachche ke baare mein chinta karte hain — us chinta ke kendra mein kaun sa vishisht dar hai?"},

{"themes":["parenting"],"type":"self_awareness","depth":1,"emotions":["guilt","shame"],"concepts":["dharma","ego"],
"en":"What kind of parent are you most afraid of becoming — and which of your parents does that remind you of?",
"hi":"आप किस प्रकार के माता-पिता बनने से सबसे अधिक डरते हैं — और यह आपके कौन से माता-पिता की याद दिलाता है?",
"hinglish":"Aap kis prakar ke mata-pita banne se sabse zyada darte hain — aur yeh aapke kaun se mata-pita ki yaad dilata hai?"},

{"themes":["parenting"],"type":"self_awareness","depth":2,"emotions":["guilt","anxiety","control"],"concepts":["ego","dharma","attachment"],
"en":"Where in your parenting do you act from your own unhealed wounds rather than from what your child actually needs?",
"hi":"अपने पालन-पोषण में आप कहाँ अपने न भरे जख्मों से कार्य करते हैं बजाय उसके जो आपके बच्चे को वास्तव में चाहिए?",
"hinglish":"Apne paalan-poshan mein aap kahan apne na bhare zakhmoon se kaam karte hain bajaaye us ke jo aapke bachche ko asal mein chahiye?"},

{"themes":["parenting"],"type":"self_awareness","depth":2,"emotions":["guilt","longing"],"concepts":["dharma","ego","attachment"],
"en":"What do you most want to give your child that you did not receive — and is that gift truly for them or also for the child you once were?",
"hi":"आप अपने बच्चे को सबसे अधिक क्या देना चाहते हैं जो आपको नहीं मिला — और क्या वह उपहार सच में उनके लिए है या उस बच्चे के लिए भी जो आप कभी थे?",
"hinglish":"Aap apne bachche ko sabse zyada kya dena chahte hain jo aapko nahi mila — aur kya woh uphaar sach mein unke liye hai ya us bachche ke liye bhi jo aap kabhi the?"},

{"themes":["parenting"],"type":"self_awareness","depth":3,"emotions":["anxiety","grief","guilt"],"concepts":["ego","dharma","attachment","detachment"],
"en":"Who are you as a parent when no one is watching and there is no performance — and is that person someone you are at peace with?",
"hi":"जब कोई नहीं देख रहा और कोई प्रदर्शन नहीं है — तब माता-पिता के रूप में आप कौन हैं, और क्या वह व्यक्ति कोई है जिसके साथ आप शांति में हैं?",
"hinglish":"Jab koi nahi dekh raha aur koi pradarshan nahi hai — tab mata-pita ke roop mein aap kaun hain, aur kya woh insaan koi hai jiske saath aap shanti mein hain?"},

{"themes":["parenting"],"type":"self_awareness","depth":3,"emotions":["grief","anxiety","existential"],"concepts":["ego","dharma","detachment","impermanence"],
"en":"What is the grief hidden inside your love for your child — the one about their growing up and away, about not being able to protect them from everything?",
"hi":"अपने बच्चे के प्रति आपके प्रेम के भीतर छुपा दुख क्या है — उनके बड़े होने और दूर जाने के बारे में, उन्हें सब कुछ से न बचा पाने के बारे में?",
"hinglish":"Apne bachche ke prati aapke prem ke andar chhuupa dard kya hai — unke bade hone aur door jaane ke baare mein, unhe sab kuch se na bacha paane ke baare mein?"},

{"themes":["parenting"],"type":"action_oriented","depth":1,"emotions":["guilt","anxiety"],"concepts":["karma","dharma"],
"en":"What is the one thing your child most needs from you right now — not what you think they should need, but what they seem to be asking for?",
"hi":"अभी आपके बच्चे को आपसे सबसे अधिक क्या चाहिए — वह नहीं जो आपको लगता है उन्हें चाहिए, बल्कि जो वे माँगते प्रतीत होते हैं?",
"hinglish":"Abhi aapke bachche ko aapse sabse zyada kya chahiye — woh nahi jo aapko lagta hai unhe chahiye, balki jo woh maangte prateet hote hain?"},

{"themes":["parenting"],"type":"action_oriented","depth":2,"emotions":["guilt","anxiety","control"],"concepts":["karma","dharma","detachment"],
"en":"What would it look like to trust your child more — not to remove all protection, but to make room for them to encounter and navigate difficulty?",
"hi":"अपने बच्चे पर अधिक विश्वास करना कैसा दिखेगा — सारी सुरक्षा हटाना नहीं, बल्कि उन्हें कठिनाइयों का सामना करने और उनसे निपटने के लिए जगह देना?",
"hinglish":"Apne bachche par zyada vishwas karna kaisa dikhega — saari suraksha hatana nahi, balki unhe mushkilon ka saamna karne aur unse niptne ke liye jagah dena?"},

{"themes":["parenting"],"type":"action_oriented","depth":3,"emotions":["grief","anxiety","guilt"],"concepts":["karma","dharma","detachment","surrender"],
"en":"What would it mean to parent from a place of love that is not conditional on their choices — loving them through the choices you would not make for them?",
"hi":"उनके चुनावों पर निर्भर न होने वाले प्रेम से पालन-पोषण करने का क्या अर्थ होगा — उन्हें उन चुनावों के दौरान प्रेम करना जो आप उनके लिए न करते?",
"hinglish":"Unke chunaavon par nirbhar na hone wale prem se paalan-poshan karne ka kya matlab hoga — unhe un chunaavon ke dauran prem karna jo aap unke liye na karte?"},

{"themes":["parenting"],"type":"spiritual","depth":1,"emotions":["anxiety","longing"],"concepts":["dharma","karma","surrender"],
"en":"What would it mean to trust that your child has their own path — and that your role is to accompany rather than to direct?",
"hi":"यह विश्वास करने का क्या अर्थ होगा कि आपके बच्चे का अपना मार्ग है — और आपकी भूमिका निर्देशित करने की नहीं बल्कि साथ देने की है?",
"hinglish":"Yeh vishwas karne ka kya matlab hoga ki aapke bachche ka apna raasta hai — aur aapki bhumika nirdeshit karne ki nahi balki saath dene ki hai?"},

{"themes":["parenting"],"type":"spiritual","depth":2,"emotions":["anxiety","grief"],"concepts":["dharma","karma","detachment","surrender"],
"en":"What would it mean to love your child with open hands — fully present, fully caring, without needing them to be a particular way for you to feel at peace?",
"hi":"अपने बच्चे को खुले हाथों से प्रेम करने का क्या अर्थ होगा — पूरी तरह उपस्थित, पूरी तरह परवाह करते हुए, बिना उनसे किसी विशेष तरीके से होने की ज़रूरत के ताकि आप शांति में हों?",
"hinglish":"Apne bachche ko khule haathon se prem karne ka kya matlab hoga — poori tarah maujood, poori tarah parwaah karte hue, bina unse kisi vishesh tarike se hone ki zaroorat ke taaki aap shanti mein hon?"},

{"themes":["parenting"],"type":"spiritual","depth":3,"emotions":["grief","anxiety","existential"],"concepts":["dharma","karma","detachment","surrender","impermanence"],
"en":"What if your child is a soul passing through your life — related but distinct — and your task is not to shape them but to witness them becoming themselves?",
"hi":"क्या हो यदि आपका बच्चा आपके जीवन से गुज़रने वाली एक आत्मा है — संबंधित लेकिन अलग — और आपका काम उन्हें आकार देना नहीं बल्कि उन्हें खुद बनते देखना है?",
"hinglish":"Kya ho agar aapka bachcha aapke jeevan se guzarne wali ek aatma hai — sambandhit lekin alag — aur aapka kaam unhe aakar dena nahi balki unhe khud bante dekhna hai?"},

# ── PURPOSE ─────────────────────────────────────────────────────────────────
{"themes":["purpose"],"type":"self_awareness","depth":1,"emotions":["emptiness","restlessness"],"concepts":["svadharma","dharma"],
"en":"When your life feels most meaningful — even in a small moment — what is happening?",
"hi":"जब आपका जीवन सबसे अधिक अर्थपूर्ण लगता है — एक छोटे से पल में भी — क्या हो रहा होता है?",
"hinglish":"Jab aapka jeevan sabse zyada arthapoorn lagta hai — ek chhote se pal mein bhi — kya ho raha hota hai?"},

{"themes":["purpose"],"type":"self_awareness","depth":1,"emotions":["emptiness","confusion"],"concepts":["svadharma"],
"en":"If no one were watching and there were no reward — what would you still do just because it mattered?",
"hi":"यदि कोई नहीं देख रहा और कोई पुरस्कार नहीं है — तो आप क्या फिर भी करते क्योंकि यह मायने रखता?",
"hinglish":"Agar koi nahi dekh raha aur koi puraskaar nahi hai — toh aap kya phir bhi karte kyunki yeh mayne rakhta?"},

{"themes":["purpose"],"type":"self_awareness","depth":2,"emotions":["emptiness","confusion","restlessness"],"concepts":["svadharma","ego"],
"en":"What is the difference between the purpose you have been given and the purpose you are discovering — are they the same?",
"hi":"जो उद्देश्य आपको दिया गया है और जो उद्देश्य आप खोज रहे हैं — उनके बीच क्या अंतर है, क्या वे एक ही हैं?",
"hinglish":"Jo uddeshya aapko diya gaya hai aur jo uddeshya aap khoj rahe hain — unke beech kya antar hai, kya woh ek hi hain?"},

{"themes":["purpose"],"type":"self_awareness","depth":2,"emotions":["emptiness","restlessness","shame"],"concepts":["svadharma","ego","comparison"],
"en":"What would you pursue if you were not trying to build a life that looks purposeful to others — if only you knew what it was for?",
"hi":"यदि आप दूसरों को उद्देश्यपूर्ण दिखने वाला जीवन बनाने की कोशिश नहीं कर रहे थे — तो आप क्या खोजते, यदि केवल आप जानते कि यह किसके लिए है?",
"hinglish":"Agar aap doosron ko uddeshyapoorn dikhne wala jeevan banane ki koshish nahi kar rahe the — toh aap kya khojte, agar sirf aap jaante ki yeh kiske liye hai?"},

{"themes":["purpose"],"type":"self_awareness","depth":3,"emotions":["emptiness","existential","grief"],"concepts":["svadharma","ego","dharma"],
"en":"What would you have to let go of — in terms of what you thought your life would be — to see what it actually is calling you toward?",
"hi":"जो आपने सोचा था आपका जीवन क्या होगा उसे छोड़ने के लिए क्या छोड़ना होगा — यह देखने के लिए कि यह आपको वास्तव में किस ओर बुला रहा है?",
"hinglish":"Jo aapne socha tha aapka jeevan kya hoga use chhodne ke liye kya chhodni hogi — yeh dekhne ke liye ki yeh aapko asal mein kis taraf bula raha hai?"},

{"themes":["purpose"],"type":"self_awareness","depth":3,"emotions":["emptiness","grief","existential"],"concepts":["svadharma","ego","witness-self"],
"en":"What if the sense of purposelessness you feel is not evidence that you lack a purpose — but a signal that you are not yet living in alignment with one you already sense?",
"hi":"क्या हो यदि उद्देश्यहीनता का जो एहसास आप महसूस करते हैं वह इस बात का प्रमाण नहीं है कि आपके पास कोई उद्देश्य नहीं है — बल्कि एक संकेत है कि आप अभी तक उस उद्देश्य के अनुरूप नहीं जी रहे जिसे आप पहले से महसूस करते हैं?",
"hinglish":"Kya ho agar uddeshyahinta ka jo ahsas aap mahsoos karte hain woh is baat ka praman nahi hai ki aapke paas koi uddeshya nahi hai — balki ek sanket hai ki aap abhi tak us uddeshya ke anuroop nahi ji rahe jise aap pehle se mahsoos karte hain?"},

{"themes":["purpose"],"type":"action_oriented","depth":1,"emotions":["emptiness","restlessness"],"concepts":["karma","svadharma"],
"en":"What is one small experiment you could run this week toward something that genuinely interests you — regardless of whether it leads anywhere?",
"hi":"इस सप्ताह एक छोटा प्रयोग जो आप किसी ऐसी चीज़ की ओर कर सकते हैं जो आपको वास्तव में रुचिकर लगती है — चाहे यह कहीं ले जाए या नहीं?",
"hinglish":"Is hafte ek chhota prayog jo aap kisi aisi cheez ki taraf kar sakte hain jo aapko asal mein ruchikr lagti hai — chahe yeh kahi le jaaye ya nahi?"},

{"themes":["purpose"],"type":"action_oriented","depth":2,"emotions":["emptiness","confusion"],"concepts":["karma","svadharma","dharma"],
"en":"What would you need to stop doing to make room for what you are being called toward — and what makes that hard to stop?",
"hi":"जो आपको बुलाया जा रहा है उसके लिए जगह बनाने के लिए आपको क्या करना बंद करना होगा — और उसे बंद करना क्या कठिन बनाता है?",
"hinglish":"Jo aapko bulaya ja raha hai uske liye jagah banane ke liye aapko kya karna band karna hoga — aur use band karna kya mushkil banata hai?"},

{"themes":["purpose"],"type":"action_oriented","depth":3,"emotions":["emptiness","grief","restlessness"],"concepts":["karma","svadharma","dharma","detachment"],
"en":"What would it look like to move toward your purpose — not with grand declarations, but with small, consistent acts that are available to you today?",
"hi":"अपने उद्देश्य की ओर बढ़ना कैसा दिखेगा — बड़ी घोषणाओं से नहीं, बल्कि छोटे, सुसंगत कार्यों से जो आज आपके लिए उपलब्ध हैं?",
"hinglish":"Apne uddeshya ki taraf badhna kaisa dikhega — badi ghoshnaon se nahi, balki chhote, susangat karmon se jo aaj aapke liye uplabdh hain?"},

{"themes":["purpose"],"type":"spiritual","depth":1,"emotions":["emptiness","longing"],"concepts":["svadharma","dharma","karma"],
"en":"What if your purpose is not something to find but something to listen for — and what has it been saying that you have not been hearing?",
"hi":"क्या हो यदि आपका उद्देश्य कुछ खोजने की चीज़ नहीं है बल्कि सुनने की — और यह क्या कह रहा है जो आप सुन नहीं रहे?",
"hinglish":"Kya ho agar aapka uddeshya kuch khojne ki cheez nahi hai balki sunne ki — aur yeh kya keh raha hai jo aap sun nahi rahe?"},

{"themes":["purpose"],"type":"spiritual","depth":2,"emotions":["emptiness","longing"],"concepts":["svadharma","dharma","surrender"],
"en":"The Gita speaks of svadharma — the particular duty of this particular life — what is yours, as best you can hear it right now?",
"hi":"गीता स्वधर्म की बात करती है — इस विशेष जीवन का विशेष कर्तव्य — जितना आप अभी सुन सकते हैं, आपका क्या है?",
"hinglish":"Gita svadharma ki baat karti hai — is vishesh jeevan ka vishesh kartavya — jitna aap abhi sun sakte hain, aapka kya hai?"},

{"themes":["purpose"],"type":"spiritual","depth":3,"emotions":["emptiness","existential","longing"],"concepts":["svadharma","dharma","ego","witness-self"],
"en":"What if purpose is not a destination but the quality of attention you bring to whatever is in front of you — and what would it mean to live that way?",
"hi":"क्या हो यदि उद्देश्य कोई गंतव्य नहीं है बल्कि ध्यान की वह गुणवत्ता है जो आप जो भी आपके सामने है उसमें लाते हैं — और इस तरह जीने का क्या अर्थ होगा?",
"hinglish":"Kya ho agar uddeshya koi gantavya nahi hai balki dhyan ki woh gunwatta hai jo aap jo bhi aapke saamne hai us mein laate hain — aur is tarah jeene ka kya matlab hoga?"},
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
    print(f"Batch 4 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
