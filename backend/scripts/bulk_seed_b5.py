"""Bulk seed batch 5: regret, relationships, restlessness, self_worth, success."""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── REGRET ───────────────────────────────────────────────────────────────────
{"themes":["regret"],"type":"self_awareness","depth":1,"emotions":["regret","guilt"],"concepts":["karma"],
"en":"What is the choice you keep returning to in your mind — the one you wish you had made differently?",
"hi":"वह निर्णय क्या है जिसके पास आपका मन बार-बार लौटता है — जिसे आप अलग तरह से लेना चाहते?",
"hinglish":"Woh nirnay kya hai jiske paas aapka mann baar-baar lauta hai — jise aap alag tarah se lena chahte?"},

{"themes":["regret"],"type":"self_awareness","depth":1,"emotions":["regret","sadness"],"concepts":["karma","impermanence"],
"en":"When you revisit this regret — what are you most trying to find that the revisiting could not possibly give you?",
"hi":"जब आप इस पछतावे पर वापस लौटते हैं — आप सबसे अधिक क्या खोजने की कोशिश कर रहे हैं जो यह वापसी आपको नहीं दे सकती?",
"hinglish":"Jab aap is pachtaave par wapas laute hain — aap sabse zyada kya khojne ki koshish kar rahe hain jo yeh wapsi aapko nahi de sakti?"},

{"themes":["regret"],"type":"self_awareness","depth":2,"emotions":["regret","shame","guilt"],"concepts":["karma","ego"],
"en":"What did you know then that you could not act on — and what has changed in you since that makes you wish you had?",
"hi":"तब आप क्या जानते थे जिस पर आप कार्य नहीं कर सके — और तब से आपमें क्या बदला है जो आपको चाहने पर मजबूर करता है कि आपने किया होता?",
"hinglish":"Tab aap kya jaante the jis par aap kaam nahi kar sake — aur tab se aap mein kya badla hai jo aapko chahne par majboor karta hai ki aapne kiya hota?"},

{"themes":["regret"],"type":"self_awareness","depth":2,"emotions":["regret","grief"],"concepts":["karma","ego","impermanence"],
"en":"What would you need to believe about the person you were then — the one who made that choice — to stop punishing them?",
"hi":"उस समय के उस व्यक्ति के बारे में — जिसने वह चुनाव किया — आपको क्या विश्वास करना होगा ताकि उसे दंड देना बंद हो सके?",
"hinglish":"Us samay ke us insaan ke baare mein — jisne woh chunaav kiya — aapko kya vishwas karna hoga taaki use dand dena band ho sake?"},

{"themes":["regret"],"type":"self_awareness","depth":3,"emotions":["regret","shame","existential"],"concepts":["karma","ego","witness-self"],
"en":"If you accepted that the path that brought you here — including the choices you regret — was the only path that could have brought you to this exact moment, what would shift?",
"hi":"यदि आप स्वीकार करें कि जो मार्ग आपको यहाँ तक लाया — जिन चुनावों पर आपको पछतावा है उन सहित — वह एकमात्र मार्ग था जो आपको इस सटीक क्षण तक ला सकता था, तो क्या बदलेगा?",
"hinglish":"Agar aap sweekar karein ki jo raasta aapko yahan tak laaya — jin chunaavon par aapko pachtaawa hai un sahit — woh ekmaatr raasta tha jo aapko is satik pal tak la sakta tha, toh kya badlega?"},

{"themes":["regret"],"type":"self_awareness","depth":3,"emotions":["regret","grief","existential"],"concepts":["karma","impermanence","witness-self"],
"en":"What is this regret teaching you about what you value — and is there a way to honor that value going forward that does not require rewriting the past?",
"hi":"यह पछतावा आपको उस बारे में क्या सिखा रहा है जो आप मूल्यवान समझते हैं — और क्या इस मूल्य को आगे सम्मान देने का कोई तरीका है जिसके लिए अतीत को फिर से लिखने की ज़रूरत नहीं?",
"hinglish":"Yeh pachtaawa aapko us baare mein kya sikha raha hai jo aap mulyavaan samajhte hain — aur kya is mulya ko aage samman dene ka koi tarika hai jiske liye ateet ko phir se likhne ki zaroorat nahi?"},

{"themes":["regret"],"type":"action_oriented","depth":1,"emotions":["regret","guilt"],"concepts":["karma"],
"en":"Is there something still undone — an apology unmade, a connection unmended — that remains within your power to act on now?",
"hi":"क्या कुछ अभी भी अधूरा है — कोई माफ़ी नहीं माँगी, कोई जुड़ाव नहीं जोड़ा — जो अभी भी आपकी शक्ति में है कार्य करने के लिए?",
"hinglish":"Kya kuch abhi bhi adhura hai — koi maafi nahi maangi, koi judav nahi joda — jo abhi bhi aapki shakti mein hai kaam karne ke liye?"},

{"themes":["regret"],"type":"action_oriented","depth":2,"emotions":["regret","resistance"],"concepts":["karma","dharma"],
"en":"What would it mean to make a different choice now — one that aligns with who you have become — even though you cannot go back?",
"hi":"अभी एक अलग चुनाव करने का क्या अर्थ होगा — एक जो आप जो बन गए हैं उसके अनुरूप हो — भले ही आप वापस नहीं जा सकते?",
"hinglish":"Abhi ek alag chunaav karne ka kya matlab hoga — ek jo aap jo ban gaye hain uske anuroop ho — chahe aap wapas nahi ja sakte?"},

{"themes":["regret"],"type":"action_oriented","depth":3,"emotions":["regret","grief","shame"],"concepts":["karma","dharma","detachment"],
"en":"If the regret could become fuel rather than weight — what would it drive you to do, to be, to offer?",
"hi":"यदि पछतावा बोझ के बजाय ईंधन बन जाए — यह आपको क्या करने, क्या बनने, क्या अर्पित करने के लिए प्रेरित करेगा?",
"hinglish":"Agar pachtaawa bojh ki bajaay indhan ban jaaye — yeh aapko kya karne, kya banne, kya arpit karne ke liye prerit karega?"},

{"themes":["regret"],"type":"spiritual","depth":1,"emotions":["regret","grief"],"concepts":["karma","impermanence"],
"en":"What if this regret is not a verdict on who you are — but a map showing you the direction you now want to grow?",
"hi":"क्या हो यदि यह पछतावा आप कौन हैं इसका फैसला नहीं है — बल्कि एक नक्शा है जो आपको वह दिशा दिखाता है जिसमें आप अब बढ़ना चाहते हैं?",
"hinglish":"Kya ho agar yeh pachtaawa aap kaun hain iska faisla nahi hai — balki ek naksha hai jo aapko woh disha dikhata hai jis mein aap ab badhna chahte hain?"},

{"themes":["regret"],"type":"spiritual","depth":2,"emotions":["regret","grief"],"concepts":["karma","impermanence","equanimity"],
"en":"The Gita asks you to act rightly now — not to undo what was, but to meet what is. What does that ask of you in this moment?",
"hi":"गीता अभी सही कार्य करने के लिए कहती है — जो था उसे पूर्ववत करने के लिए नहीं, बल्कि जो है उसका सामना करने के लिए। यह इस क्षण आपसे क्या माँगता है?",
"hinglish":"Gita abhi sahi kaam karne ke liye kehti hai — jo tha use purvaavat karne ke liye nahi, balki jo hai uska saamna karne ke liye. Yeh is pal aapse kya maangta hai?"},

{"themes":["regret"],"type":"spiritual","depth":3,"emotions":["regret","existential","grief"],"concepts":["karma","impermanence","witness-self","surrender"],
"en":"What if every choice — including the one you regret most — was part of the soul's curriculum, and this regret is simply where you are being taught?",
"hi":"क्या हो यदि हर चुनाव — जिसे आप सबसे अधिक पछताते हैं उसे भी शामिल करते हुए — आत्मा के पाठ्यक्रम का हिस्सा था, और यह पछतावा बस वह जगह है जहाँ आपको पढ़ाया जा रहा है?",
"hinglish":"Kya ho agar har chunaav — jise aap sabse zyada pachtaate hain use bhi shaamil karte hue — aatma ke pathyakram ka hissa tha, aur yeh pachtaawa bas woh jagah hai jahan aapko padhaaya ja raha hai?"},

# ── RELATIONSHIPS ────────────────────────────────────────────────────────────
{"themes":["relationships"],"type":"self_awareness","depth":1,"emotions":["longing","frustration"],"concepts":["ego","attachment"],
"en":"What do you most consistently bring to the relationships in your life — and what do you most consistently avoid?",
"hi":"आप अपने जीवन के संबंधों में सबसे अधिक निरंतर क्या लाते हैं — और सबसे अधिक निरंतर क्या टालते हैं?",
"hinglish":"Aap apne jeevan ke rishton mein sabse zyada lagaatar kya laate hain — aur sabse zyada lagaatar kya taalte hain?"},

{"themes":["relationships"],"type":"self_awareness","depth":1,"emotions":["longing","resentment"],"concepts":["ego","attachment"],
"en":"In this relationship, what are you asking for that you are not saying out loud — and what stops you from saying it?",
"hi":"इस संबंध में, आप क्या माँग रहे हैं जो आप ज़ोर से नहीं कह रहे — और उसे कहने से आपको क्या रोकता है?",
"hinglish":"Is rishte mein, aap kya maang rahe hain jo aap zor se nahi keh rahe — aur use kehne se aapko kya rokta hai?"},

{"themes":["relationships"],"type":"self_awareness","depth":2,"emotions":["longing","resentment","fear"],"concepts":["ego","attachment","karma"],
"en":"What pattern keeps showing up in your relationships — in how conflicts unfold, in what you need, in how you leave or stay?",
"hi":"आपके संबंधों में कौन-सा पैटर्न बार-बार दिखाई देता है — संघर्ष कैसे उभरते हैं, आपको क्या चाहिए, आप कैसे जाते या रहते हैं?",
"hinglish":"Aapke rishton mein kaun sa pattern baar-baar dikhai deta hai — sangharsh kaise ubharte hain, aapko kya chahiye, aap kaise jaate ya rehte hain?"},

{"themes":["relationships"],"type":"self_awareness","depth":2,"emotions":["resentment","longing"],"concepts":["ego","attachment","karma"],
"en":"Where in your relationships do you try to change the other person rather than adjusting your own response — and how well is that working?",
"hi":"अपने संबंधों में आप कहाँ दूसरे व्यक्ति को बदलने की कोशिश करते हैं बजाय अपनी प्रतिक्रिया को समायोजित करने के — और यह कितना अच्छा काम कर रहा है?",
"hinglish":"Apne rishton mein aap kahan doosre insaan ko badalne ki koshish karte hain bajaaye apni pratikriya ko samaayojit karne ke — aur yeh kitna achha kaam kar raha hai?"},

{"themes":["relationships"],"type":"self_awareness","depth":3,"emotions":["resentment","shame","grief"],"concepts":["ego","attachment","karma","forgiveness"],
"en":"What is the oldest wound you carry into new relationships — and how would another person know they had touched it?",
"hi":"सबसे पुराना ज़ख्म क्या है जो आप नए संबंधों में लेकर जाते हैं — और दूसरा व्यक्ति कैसे जानेगा कि उसने उसे छू लिया है?",
"hinglish":"Sabse purana zakham kya hai jo aap naye rishton mein lekar jaate hain — aur doosra insaan kaise janega ki usne use chhu liya hai?"},

{"themes":["relationships"],"type":"self_awareness","depth":3,"emotions":["shame","grief","existential"],"concepts":["ego","attachment","witness-self"],
"en":"If you were fully honest about what you are seeking in relationships — not what sounds noble, but what you are actually searching for — what would you say?",
"hi":"यदि आप इस बारे में पूरी तरह ईमानदार हों कि आप संबंधों में क्या खोज रहे हैं — जो महान लगता है वह नहीं, बल्कि जो आप वास्तव में ढूंढ रहे हैं — तो आप क्या कहेंगे?",
"hinglish":"Agar aap is baare mein poori tarah imaandaar hon ki aap rishton mein kya khoj rahe hain — jo maahan lagta hai woh nahi, balki jo aap asal mein dhundh rahe hain — toh aap kya kahenge?"},

{"themes":["relationships"],"type":"action_oriented","depth":1,"emotions":["longing","frustration"],"concepts":["karma","dharma"],
"en":"What is one thing you could offer in this relationship today — not out of obligation, but because you genuinely care?",
"hi":"इस संबंध में आज एक चीज़ जो आप दायित्व से नहीं, बल्कि इसलिए दे सकते हैं क्योंकि आप वास्तव में परवाह करते हैं — क्या है?",
"hinglish":"Is rishte mein aaj ek cheez jo aap dayitva se nahi, balki isliye de sakte hain kyunki aap asal mein parwaah karte hain — kya hai?"},

{"themes":["relationships"],"type":"action_oriented","depth":2,"emotions":["resentment","resistance"],"concepts":["karma","svadharma"],
"en":"What boundary have you failed to draw — with kindness — that has allowed this relationship to erode? What would drawing it actually look like?",
"hi":"कौन-सी सीमा जो आपने — दयालुता के साथ — नहीं खींची है जिसने इस संबंध को क्षय होने दिया? उसे खींचना वास्तव में कैसा दिखेगा?",
"hinglish":"Kaun si seema jo aapne — dayaluta ke saath — nahi kheenchi hai jisne is rishte ko ksay hone diya? Use kheenchna asal mein kaisa dikhega?"},

{"themes":["relationships"],"type":"action_oriented","depth":3,"emotions":["grief","resentment","longing"],"concepts":["karma","dharma","detachment"],
"en":"What would it look like to fully show up in this relationship — to stop managing it and start inhabiting it?",
"hi":"इस संबंध में पूरी तरह उपस्थित होना कैसा दिखेगा — इसे प्रबंधित करना बंद करना और इसमें वास्तव में रहना शुरू करना?",
"hinglish":"Is rishte mein poori tarah maujood hona kaisa dikhega — ise manage karna band karna aur ismein asal mein rehna shuru karna?"},

{"themes":["relationships"],"type":"spiritual","depth":1,"emotions":["longing","frustration"],"concepts":["karma","dharma","attachment"],
"en":"What if relationships are not primarily about receiving what you need — but about discovering what you are capable of giving?",
"hi":"क्या हो यदि संबंध मुख्यतः उसे प्राप्त करने के बारे में नहीं हैं जो आपको चाहिए — बल्कि यह खोजने के बारे में हैं कि आप क्या देने में सक्षम हैं?",
"hinglish":"Kya ho agar rishte mukhyatah us paane ke baare mein nahi hain jo aapko chahiye — balki yeh khojne ke baare mein hain ki aap kya dene mein saksham hain?"},

{"themes":["relationships"],"type":"spiritual","depth":2,"emotions":["resentment","longing"],"concepts":["karma","ego","attachment"],
"en":"What if the other person in this relationship is a mirror — showing you something about yourself you have not been willing to see?",
"hi":"क्या हो यदि इस संबंध का दूसरा व्यक्ति एक दर्पण है — आपको खुद के बारे में कुछ दिखाता है जिसे आप देखने को तैयार नहीं रहे हैं?",
"hinglish":"Kya ho agar is rishte ka doosra insaan ek darpan hai — aapko khud ke baare mein kuch dikhata hai jise aap dekhne ko taiyar nahi rahe hain?"},

{"themes":["relationships"],"type":"spiritual","depth":3,"emotions":["grief","longing","existential"],"concepts":["karma","attachment","ego","witness-self"],
"en":"What would love in this relationship look like if it did not ask for anything in return — and is there any part of you that has touched that quality of love?",
"hi":"इस संबंध में प्रेम कैसा दिखेगा यदि यह बदले में कुछ नहीं माँगता — और क्या आपमें कोई हिस्सा है जिसने प्रेम की उस गुणवत्ता को छुआ है?",
"hinglish":"Is rishte mein prem kaisa dikhega agar yeh badle mein kuch nahi maangta — aur kya aap mein koi hissa hai jisne prem ki us gunwatta ko chhua hai?"},

# ── RESTLESSNESS ─────────────────────────────────────────────────────────────
{"themes":["restlessness"],"type":"self_awareness","depth":1,"emotions":["restlessness","anxiety"],"concepts":["equanimity","ego"],
"en":"What are you looking for in all this movement and seeking — and have you ever found it, even briefly?",
"hi":"इस सारी गतिविधि और खोज में आप क्या ढूंढ रहे हैं — और क्या आपने कभी इसे पाया है, भले ही संक्षेप में?",
"hinglish":"Is saari gatividhi aur khoj mein aap kya dhundh rahe hain — aur kya aapne kabhi ise paya hai, chahe sankshep mein?"},

{"themes":["restlessness"],"type":"self_awareness","depth":1,"emotions":["restlessness","boredom"],"concepts":["equanimity"],
"en":"What are you running from when you fill every silence — and what might you hear if you stopped?",
"hi":"जब आप हर खामोशी को भरते हैं तो आप किससे भाग रहे हैं — और यदि आप रुक जाएं तो आप क्या सुन सकते हैं?",
"hinglish":"Jab aap har khamoshi ko bharte hain toh aap kisse bhaag rahe hain — aur agar aap ruk jaayein toh aap kya sun sakte hain?"},

{"themes":["restlessness"],"type":"self_awareness","depth":2,"emotions":["restlessness","anxiety","boredom"],"concepts":["equanimity","ego","attachment"],
"en":"What would happen if you stayed exactly where you are — in this life, this situation, this moment — without seeking to change it?",
"hi":"क्या होगा यदि आप ठीक वहाँ रहें जहाँ आप हैं — इस जीवन में, इस स्थिति में, इस क्षण में — इसे बदले बिना?",
"hinglish":"Kya hoga agar aap theek wahan rahein jahan aap hain — is jeevan mein, is situation mein, is pal mein — ise badle bina?"},

{"themes":["restlessness"],"type":"self_awareness","depth":2,"emotions":["restlessness","shame","emptiness"],"concepts":["ego","desire","equanimity"],
"en":"Is this restlessness about where you are — or about something in you that would follow you anywhere you went?",
"hi":"क्या यह बेचैनी इस बारे में है कि आप कहाँ हैं — या आपमें किसी ऐसी चीज़ के बारे में जो आप जहाँ भी जाएं आपके पीछे जाती?",
"hinglish":"Kya yeh bechaini is baare mein hai ki aap kahan hain — ya aap mein kisi aisi cheez ke baare mein jo aap jahan bhi jaayein aapke peechhe jaati?"},

{"themes":["restlessness"],"type":"self_awareness","depth":3,"emotions":["restlessness","existential","emptiness"],"concepts":["ego","desire","witness-self","equanimity"],
"en":"If the restlessness were pointing at something genuine — not something to acquire but something to return to — what might it be pointing at?",
"hi":"यदि बेचैनी किसी वास्तविक चीज़ की ओर इशारा कर रही है — कुछ प्राप्त करने की नहीं बल्कि वापस लौटने की — तो यह किस ओर इशारा कर रही है?",
"hinglish":"Agar bechaini kisi asli cheez ki taraf ishara kar rahi hai — kuch prapt karne ki nahi balki wapas lautne ki — toh yeh kis taraf ishara kar rahi hai?"},

{"themes":["restlessness"],"type":"self_awareness","depth":3,"emotions":["restlessness","existential","shame"],"concepts":["ego","witness-self","desire"],
"en":"Who are you when there is nothing to do, nothing to achieve, and no one watching — and are you comfortable with that person?",
"hi":"जब करने के लिए कुछ नहीं है, प्राप्त करने के लिए कुछ नहीं है, और कोई नहीं देख रहा — तब आप कौन हैं, और क्या आप उस व्यक्ति के साथ सहज हैं?",
"hinglish":"Jab karne ke liye kuch nahi hai, prapt karne ke liye kuch nahi hai, aur koi nahi dekh raha — tab aap kaun hain, aur kya aap us insaan ke saath sahaj hain?"},

{"themes":["restlessness"],"type":"action_oriented","depth":1,"emotions":["restlessness","boredom"],"concepts":["karma","discipline"],
"en":"What would it mean to be fully here — with this, as it is — for just the next five minutes?",
"hi":"बस अगले पाँच मिनट के लिए — यहाँ पूरी तरह उपस्थित होने का — इसके साथ, जैसा यह है — क्या अर्थ होगा?",
"hinglish":"Bas agle paanch minute ke liye — yahan poori tarah maujood hone ka — iske saath, jaisa yeh hai — kya matlab hoga?"},

{"themes":["restlessness"],"type":"action_oriented","depth":2,"emotions":["restlessness","avoidance"],"concepts":["karma","discipline","svadharma"],
"en":"What is the one thing you keep moving away from by staying busy — and what would it ask of you if you turned toward it?",
"hi":"व्यस्त रहकर आप किस एक चीज़ से दूर जाते रहते हैं — और यदि आप उसकी ओर मुड़ें तो यह आपसे क्या माँगेगी?",
"hinglish":"Vyast rehkar aap kis ek cheez se door jaate rehte hain — aur agar aap uski taraf mudein toh yeh aapse kya maangegi?"},

{"themes":["restlessness"],"type":"action_oriented","depth":3,"emotions":["restlessness","resistance","emptiness"],"concepts":["karma","discipline","dharma"],
"en":"What practice — repeated, unglamorous, returning even after you quit it — might give your restlessness somewhere to land?",
"hi":"कौन-सा अभ्यास — दोहराया गया, बिना चमक का, यहाँ तक कि छोड़ने के बाद भी लौटना — आपकी बेचैनी को कहीं रखने की जगह दे सकता है?",
"hinglish":"Kaun sa abhyas — dohraaya gaya, bina chamak ka, yahan tak ki chhodne ke baad bhi lautna — aapki bechaini ko kahi rakhne ki jagah de sakta hai?"},

{"themes":["restlessness"],"type":"spiritual","depth":1,"emotions":["restlessness","longing"],"concepts":["equanimity","desire","surrender"],
"en":"What if the restlessness is not a problem to fix — but a longing pointing toward something the world cannot satisfy?",
"hi":"क्या हो यदि बेचैनी ठीक करने की कोई समस्या नहीं है — बल्कि एक लालसा है जो किसी ऐसी चीज़ की ओर इशारा कर रही है जिसे दुनिया संतुष्ट नहीं कर सकती?",
"hinglish":"Kya ho agar bechaini theek karne ki koi samasya nahi hai — balki ek lalsa hai jo kisi aisi cheez ki taraf ishara kar rahi hai jise duniya santusht nahi kar sakti?"},

{"themes":["restlessness"],"type":"spiritual","depth":2,"emotions":["restlessness","longing","emptiness"],"concepts":["equanimity","desire","ego","surrender"],
"en":"The Gita speaks of the steady-minded one who is not disturbed by misery and not elated by happiness — what would your restlessness look like if you inhabited that steadiness even slightly?",
"hi":"गीता उस स्थिरचित्त की बात करती है जो दुख से विचलित नहीं होता और सुख से उत्साहित नहीं होता — यदि आप उस स्थिरता में थोड़ा भी रहें तो आपकी बेचैनी कैसी दिखेगी?",
"hinglish":"Gita us sthirchitt ki baat karti hai jo dukh se vichalit nahi hota aur sukh se utsahit nahi hota — agar aap us sthirata mein thoda bhi rahein toh aapki bechaini kaisi dikhegi?"},

{"themes":["restlessness"],"type":"spiritual","depth":3,"emotions":["restlessness","existential","emptiness"],"concepts":["equanimity","ego","witness-self","surrender"],
"en":"What if stillness is not the absence of movement but its ground — and the restlessness is simply the surface of something that is already quiet beneath?",
"hi":"क्या हो यदि शांति गतिविधि की अनुपस्थिति नहीं है बल्कि उसकी नींव है — और बेचैनी केवल उस सतह पर है जो नीचे पहले से शांत है?",
"hinglish":"Kya ho agar shanti gatividhi ki anupasthiti nahi hai balki uski neenv hai — aur bechaini sirf us satah par hai jo neeche pehle se shant hai?"},

# ── SELF_WORTH ───────────────────────────────────────────────────────────────
{"themes":["self_worth"],"type":"self_awareness","depth":1,"emotions":["inadequacy","shame"],"concepts":["ego","witness-self"],
"en":"What do you believe about yourself that you would not say out loud in front of someone you respect?",
"hi":"आप अपने बारे में क्या मानते हैं जो आप किसी ऐसे व्यक्ति के सामने ज़ोर से नहीं कहेंगे जिसका आप सम्मान करते हैं?",
"hinglish":"Aap apne baare mein kya maante hain jo aap kisi aise insaan ke saamne zor se nahi kahenge jiska aap samman karte hain?"},

{"themes":["self_worth"],"type":"self_awareness","depth":1,"emotions":["inadequacy","shame","guilt"],"concepts":["ego"],
"en":"What do you feel you have to do — or be — for you to deserve the good things in your life?",
"hi":"आपको क्या लगता है आपको करना होगा — या बनना होगा — ताकि आप अपने जीवन की अच्छी चीज़ों के हकदार हों?",
"hinglish":"Aapko kya lagta hai aapko karna hoga — ya banna hoga — taaki aap apne jeevan ki achchi cheezon ke hakdaar hon?"},

{"themes":["self_worth"],"type":"self_awareness","depth":2,"emotions":["inadequacy","shame","fear"],"concepts":["ego","witness-self"],
"en":"Whose opinion of you matters most to you — and is that person qualified to be the final word on your worth?",
"hi":"आपके बारे में किसकी राय आपके लिए सबसे अधिक मायने रखती है — और क्या वह व्यक्ति आपके मूल्य पर अंतिम शब्द कहने के योग्य है?",
"hinglish":"Aapke baare mein kiski raay aapke liye sabse zyada mayne rakhti hai — aur kya woh insaan aapke mulya par antim shabd kehne ke yogya hai?"},

{"themes":["self_worth"],"type":"self_awareness","depth":2,"emotions":["inadequacy","shame"],"concepts":["ego","comparison"],
"en":"What would you have to believe about yourself to act with confidence in this situation — and what stops you from believing it?",
"hi":"इस स्थिति में आत्मविश्वास से कार्य करने के लिए आपको अपने बारे में क्या विश्वास करना होगा — और क्या आपको उस पर विश्वास करने से रोकता है?",
"hinglish":"Is situation mein aatmavishwaas se kaam karne ke liye aapko apne baare mein kya vishwas karna hoga — aur kya aapko us par vishwas karne se rokta hai?"},

{"themes":["self_worth"],"type":"self_awareness","depth":3,"emotions":["shame","inadequacy","existential"],"concepts":["ego","witness-self"],
"en":"When did you first decide you were not enough — and what happened in that moment that made that feel true?",
"hi":"आपने पहली बार कब तय किया कि आप पर्याप्त नहीं हैं — और उस क्षण में क्या हुआ जिसने इसे सच लगने पर मजबूर किया?",
"hinglish":"Aapne pehli baar kab tay kiya ki aap paryaapt nahi hain — aur us pal mein kya hua jisne ise sach laagne par majboor kiya?"},

{"themes":["self_worth"],"type":"self_awareness","depth":3,"emotions":["shame","inadequacy","grief"],"concepts":["ego","witness-self","karma"],
"en":"What would change in how you move through the world if you knew — not just believed but knew — that you were inherently worthy of being here?",
"hi":"यदि आप जानते — केवल विश्वास नहीं बल्कि जानते — कि आप यहाँ होने के स्वाभाविक रूप से योग्य हैं, तो आप दुनिया में चलने के तरीके में क्या बदलेगा?",
"hinglish":"Agar aap jaante — sirf vishwas nahi balki jaante — ki aap yahan hone ke svabhaavic roop se yogya hain, toh aap duniya mein chalne ke tarike mein kya badlega?"},

{"themes":["self_worth"],"type":"action_oriented","depth":1,"emotions":["inadequacy","shame"],"concepts":["karma","svadharma"],
"en":"What would you do today if you believed you were worthy of doing it — without earning it first?",
"hi":"यदि आप मानते कि आप इसे करने के योग्य हैं — पहले इसे अर्जित किए बिना — तो आज आप क्या करेंगे?",
"hinglish":"Agar aap maante ki aap ise karne ke yogya hain — pehle ise arjit kiye bina — toh aaj aap kya karenge?"},

{"themes":["self_worth"],"type":"action_oriented","depth":2,"emotions":["inadequacy","shame","avoidance"],"concepts":["karma","svadharma"],
"en":"What have you been withholding from others — help, presence, your voice — because you did not feel you had the right to offer it?",
"hi":"आप दूसरों से क्या रोक रहे हैं — मदद, उपस्थिति, आपकी आवाज़ — क्योंकि आपको नहीं लगा कि आपको इसे देने का अधिकार है?",
"hinglish":"Aap doosron se kya rok rahe hain — madad, upasthiti, aapki aawaaz — kyunki aapko nahi laga ki aapko ise dene ka adhikaar hai?"},

{"themes":["self_worth"],"type":"action_oriented","depth":3,"emotions":["shame","inadequacy","resistance"],"concepts":["karma","dharma","witness-self"],
"en":"What would it look like to act as though you were already enough — not someday, not after you've fixed yourself, but now?",
"hi":"ऐसा कार्य करना कैसा दिखेगा जैसे आप पहले से पर्याप्त हैं — किसी दिन नहीं, खुद को ठीक करने के बाद नहीं, बल्कि अभी?",
"hinglish":"Aisa kaam karna kaisa dikhega jaise aap pehle se paryaapt hain — kisi din nahi, khud ko theek karne ke baad nahi, balki abhi?"},

{"themes":["self_worth"],"type":"spiritual","depth":1,"emotions":["inadequacy","shame"],"concepts":["ego","witness-self"],
"en":"What if your worth is not something you build through achievement — what if it is the ground you already stand on?",
"hi":"क्या हो यदि आपका मूल्य कोई ऐसी चीज़ नहीं है जिसे आप उपलब्धि से बनाते हैं — यदि यह वह ज़मीन है जिस पर आप पहले से खड़े हैं?",
"hinglish":"Kya ho agar aapka mulya koi aisi cheez nahi hai jise aap uplabdhi se banate hain — agar yeh woh zameen hai jis par aap pehle se khade hain?"},

{"themes":["self_worth"],"type":"spiritual","depth":2,"emotions":["inadequacy","shame"],"concepts":["ego","witness-self","surrender"],
"en":"The Gita speaks of the self as untouched by any circumstance — if that is true, what is the self-worth you are protecting, and what is the self that needs no protecting?",
"hi":"गीता स्वयं को किसी भी परिस्थिति से अछूता बताती है — यदि यह सच है, तो जो आत्म-मूल्य आप बचाने की कोशिश कर रहे हैं वह क्या है, और वह स्वयं क्या है जिसे किसी सुरक्षा की ज़रूरत नहीं?",
"hinglish":"Gita khud ko kisi bhi paristhiti se achhoot batati hai — agar yeh sach hai, toh jo aatma-mulya aap bachaane ki koshish kar rahe hain woh kya hai, aur woh khud kya hai jise kisi suraksha ki zaroorat nahi?"},

{"themes":["self_worth"],"type":"spiritual","depth":3,"emotions":["shame","inadequacy","existential"],"concepts":["ego","witness-self","surrender","detachment"],
"en":"What if the part of you that feels unworthy is exactly as temporary and constructed as the part that feels worthy — and beneath both is something that simply is?",
"hi":"क्या हो यदि आपका वह हिस्सा जो अयोग्य महसूस करता है ठीक उतना ही अस्थायी और निर्मित है जितना वह हिस्सा जो योग्य महसूस करता है — और दोनों के नीचे कुछ ऐसा है जो बस है?",
"hinglish":"Kya ho agar aapka woh hissa jo ayogya feel karta hai theek utna hi asthaayi aur nirmit hai jitna woh hissa jo yogya feel karta hai — aur dono ke neeche kuch aisa hai jo bas hai?"},

# ── SUCCESS ──────────────────────────────────────────────────────────────────
{"themes":["success"],"type":"self_awareness","depth":1,"emotions":["emptiness","pride"],"concepts":["desire","ego","detachment"],
"en":"You achieved something significant — and then what? What arrived after, and what did not?",
"hi":"आपने कुछ महत्वपूर्ण हासिल किया — और फिर क्या? बाद में क्या आया, और क्या नहीं आया?",
"hinglish":"Aapne kuch mahatvapurna haasil kiya — aur phir kya? Baad mein kya aaya, aur kya nahi aaya?"},

{"themes":["success"],"type":"self_awareness","depth":1,"emotions":["pride","anxiety"],"concepts":["ego","attachment"],
"en":"Whose definition of success have you been living by — and did you ever consciously choose it?",
"hi":"आप किसकी सफलता की परिभाषा के अनुसार जी रहे हैं — और क्या आपने इसे कभी सचेत रूप से चुना?",
"hinglish":"Aap kiski safalta ki paribhasha ke anusaar ji rahe hain — aur kya aapne ise kabhi sachet roop se chuna?"},

{"themes":["success"],"type":"self_awareness","depth":2,"emotions":["emptiness","pride","anxiety"],"concepts":["ego","desire","detachment"],
"en":"What have you sacrificed in the pursuit of this success — and was it worth it, looking back honestly?",
"hi":"इस सफलता की तलाश में आपने क्या बलिदान किया है — और ईमानदारी से पीछे देखने पर क्या यह इसके लायक था?",
"hinglish":"Is safalta ki talaash mein aapne kya balidaan kiya hai — aur imaandaari se peeche dekhne par kya yeh iski layak tha?"},

{"themes":["success"],"type":"self_awareness","depth":2,"emotions":["emptiness","shame"],"concepts":["ego","comparison","desire"],
"en":"After achieving this, do you feel secure — or have you simply moved the goalpost of what you need to feel secure?",
"hi":"यह हासिल करने के बाद क्या आप सुरक्षित महसूस करते हैं — या आपने बस सुरक्षित महसूस करने के लिए जो चाहिए उसका लक्ष्य बदल दिया है?",
"hinglish":"Yeh haasil karne ke baad kya aap surakshit feel karte hain — ya aapne bas surakshit feel karne ke liye jo chahiye uska lakshya badal diya hai?"},

{"themes":["success"],"type":"self_awareness","depth":3,"emotions":["emptiness","existential","pride"],"concepts":["ego","desire","witness-self","detachment"],
"en":"If all your external success disappeared tomorrow — every title, every achievement, every recognition — who would you be, and would you still be someone you could respect?",
"hi":"यदि आपकी सारी बाहरी सफलता कल गायब हो जाए — हर पदवी, हर उपलब्धि, हर मान्यता — आप कौन होंगे, और क्या आप अभी भी कोई ऐसे होंगे जिसका आप सम्मान कर सकें?",
"hinglish":"Agar aapki saari baahri safalta kal gayab ho jaaye — har padavi, har uplabdhi, har manyata — aap kaun honge, aur kya aap abhi bhi koi aise honge jiska aap samman kar sakein?"},

{"themes":["success"],"type":"self_awareness","depth":3,"emotions":["emptiness","shame","existential"],"concepts":["ego","desire","witness-self"],
"en":"What does the hunger for more success tell you about what you believe is still missing — and has achievement ever actually filled that gap?",
"hi":"अधिक सफलता की भूख आपको उस बारे में क्या बताती है जो आप मानते हैं अभी भी कमी है — और क्या उपलब्धि ने वास्तव में कभी उस कमी को भरा है?",
"hinglish":"Zyada safalta ki bhookh aapko us baare mein kya batati hai jo aap maante hain abhi bhi kami hai — aur kya uplabdhi ne asal mein kabhi us kami ko bhara hai?"},

{"themes":["success"],"type":"action_oriented","depth":1,"emotions":["emptiness","restlessness"],"concepts":["karma","svadharma"],
"en":"If you designed success from the inside out — from what gives you genuine meaning — what would it look like?",
"hi":"यदि आप सफलता को अंदर से बाहर की ओर डिज़ाइन करें — उससे जो आपको वास्तविक अर्थ देती है — तो यह कैसी दिखेगी?",
"hinglish":"Agar aap safalta ko andar se bahar ki taraf design karein — us se jo aapko asli arth deti hai — toh yeh kaisi dikhegi?"},

{"themes":["success"],"type":"action_oriented","depth":2,"emotions":["emptiness","anxiety","pride"],"concepts":["karma","detachment","svadharma"],
"en":"What would it look like to do your best work — and genuinely release whether it is recognized or rewarded?",
"hi":"अपना सर्वश्रेष्ठ काम करना कैसा दिखेगा — और वास्तव में यह छोड़ देना कि इसे मान्यता मिले या पुरस्कृत किया जाए?",
"hinglish":"Apna sarvashreshth kaam karna kaisa dikhega — aur asal mein yeh chhod dena ki ise manyata mile ya puraskrit kiya jaaye?"},

{"themes":["success"],"type":"action_oriented","depth":3,"emotions":["emptiness","existential","restlessness"],"concepts":["karma","dharma","detachment","svadharma"],
"en":"What would you build — or pursue, or become — if you were not trying to prove anything to anyone, including yourself?",
"hi":"आप क्या बनाएंगे — या क्या खोजेंगे, या क्या बनेंगे — यदि आप किसी को, खुद को भी, कुछ साबित करने की कोशिश नहीं कर रहे थे?",
"hinglish":"Aap kya banaenge — ya kya khojenge, ya kya banenge — agar aap kisi ko, khud ko bhi, kuch sabit karne ki koshish nahi kar rahe the?"},

{"themes":["success"],"type":"spiritual","depth":1,"emotions":["emptiness","pride"],"concepts":["desire","detachment","karma"],
"en":"What if the restlessness after achieving this is not ingratitude — but an invitation to look in a different direction?",
"hi":"क्या हो यदि यह हासिल करने के बाद की बेचैनी कृतघ्नता नहीं है — बल्कि एक अलग दिशा में देखने का निमंत्रण है?",
"hinglish":"Kya ho agar yeh haasil karne ke baad ki bechaini kritaghna nahi hai — balki ek alag disha mein dekhne ka nimantran hai?"},

{"themes":["success"],"type":"spiritual","depth":2,"emotions":["emptiness","pride"],"concepts":["desire","detachment","karma","ego"],
"en":"The Gita asks you to perform action as an offering, without attachment to the fruit — what would your work become if you actually lived that teaching?",
"hi":"गीता फल की आसक्ति के बिना कर्म को अर्पण के रूप में करने को कहती है — यदि आप सच में उस शिक्षा को जीते तो आपका काम क्या बन जाता?",
"hinglish":"Gita phal ki aasakti ke bina karm ko arpan ke roop mein karne ko kehti hai — agar aap sach mein us shiksha ko jeete toh aapka kaam kya ban jaata?"},

{"themes":["success"],"type":"spiritual","depth":3,"emotions":["emptiness","existential","pride"],"concepts":["desire","ego","witness-self","detachment"],
"en":"What if the deepest form of success is not something the world can see — but a quality of inner alignment, of being truly at home in your own life?",
"hi":"क्या हो यदि सफलता का सबसे गहरा रूप कुछ ऐसा नहीं है जिसे दुनिया देख सकती है — बल्कि आंतरिक संरेखण की एक गुणवत्ता है, अपने जीवन में सच में घर में होने की?",
"hinglish":"Kya ho agar safalta ka sabse gehra roop kuch aisa nahi hai jise duniya dekh sakti hai — balki aantarik sanrekhan ki ek gunwatta hai, apne jeevan mein sach mein ghar mein hone ki?"},
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
    print(f"Batch 5 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
