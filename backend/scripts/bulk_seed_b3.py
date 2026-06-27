"""Bulk seed batch 3: fear, forgiveness, grief, jealousy, laziness."""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── FEAR ────────────────────────────────────────────────────────────────────
{"themes":["fear"],"type":"self_awareness","depth":1,"emotions":["dread","avoidance"],"concepts":["equanimity"],
"en":"When you name what you are most afraid of right now — what does the naming itself feel like?",
"hi":"जब आप इस समय जिससे सबसे अधिक डरते हैं उसे नाम दें — तो वह नामकरण स्वयं कैसा लगता है?",
"hinglish":"Jab aap is waqt jisse sabse zyada darte hain use naam dein — toh woh naama karna khud kaisa lagta hai?"},

{"themes":["fear"],"type":"self_awareness","depth":1,"emotions":["anxiety","avoidance"],"concepts":["equanimity","surrender"],
"en":"What are you doing — or not doing — to keep this fear from being triggered?",
"hi":"आप इस डर को भड़कने से रोकने के लिए क्या कर रहे हैं — या क्या नहीं कर रहे?",
"hinglish":"Aap is dar ko bhadkne se rokne ke liye kya kar rahe hain — ya kya nahi kar rahe?"},

{"themes":["fear"],"type":"self_awareness","depth":2,"emotions":["dread","shame"],"concepts":["ego","fear"],
"en":"Beneath this fear, what is the deeper fear — the one the first fear is trying to cover?",
"hi":"इस डर के नीचे, गहरा डर क्या है — वह जिसे पहला डर ढकने की कोशिश कर रहा है?",
"hinglish":"Is dar ke neeche, gehra dar kya hai — woh jise pehla dar dhakne ki koshish kar raha hai?"},

{"themes":["fear"],"type":"self_awareness","depth":2,"emotions":["dread","clinging"],"concepts":["ego","impermanence"],
"en":"When this fear visits — what does it believe would happen to you if the thing you dread actually came true?",
"hi":"जब यह डर आता है — तो वह क्या मानता है कि यदि जिस बात का आप अंदेशा करते हैं वह सच हो जाए तो आपके साथ क्या होगा?",
"hinglish":"Jab yeh dar aata hai — toh woh kya maanta hai ki agar jis baat ka aap andesha karte hain woh sach ho jaaye toh aapke saath kya hoga?"},

{"themes":["fear"],"type":"self_awareness","depth":3,"emotions":["dread","existential","shame"],"concepts":["ego","witness-self","impermanence"],
"en":"What would you be free to do — or become — if this fear were not part of the equation?",
"hi":"यदि यह डर समीकरण का हिस्सा न हो — तो आप क्या करने या क्या बनने के लिए स्वतंत्र होंगे?",
"hinglish":"Agar yeh dar equation ka hissa na ho — toh aap kya karne ya kya banne ke liye swatantra honge?"},

{"themes":["fear"],"type":"self_awareness","depth":3,"emotions":["existential","dread"],"concepts":["witness-self","ego","impermanence"],
"en":"Who is the part of you that is afraid — and is there something in you that watches even the fear without being moved by it?",
"hi":"आपका कौन-सा हिस्सा डरा हुआ है — और क्या आप में कुछ ऐसा है जो डर को भी देखता है बिना उससे प्रभावित हुए?",
"hinglish":"Aapka kaun sa hissa dara hua hai — aur kya aap mein kuch aisa hai jo dar ko bhi dekhta hai bina us se prabhavit hue?"},

{"themes":["fear"],"type":"action_oriented","depth":1,"emotions":["avoidance","dread"],"concepts":["karma","courage"],
"en":"What is the one step toward the thing you are avoiding that you could take today — even if it is a very small one?",
"hi":"जिस चीज़ से आप बच रहे हैं उसकी ओर एक कदम जो आप आज उठा सकते हैं — भले ही वह बहुत छोटा हो — क्या है?",
"hinglish":"Jis cheez se aap bach rahe hain uski taraf ek kadam jo aap aaj utha sakte hain — chahe woh bahut chhota ho — kya hai?"},

{"themes":["fear"],"type":"action_oriented","depth":2,"emotions":["avoidance","dread"],"concepts":["karma","svadharma"],
"en":"What would the braver version of you do with this situation — and what would you need to believe to do that?",
"hi":"आपका अधिक साहसी संस्करण इस स्थिति के साथ क्या करता — और उसे करने के लिए आपको क्या विश्वास करना होगा?",
"hinglish":"Aapka zyada saahasik version is situation ke saath kya karta — aur use karne ke liye aapko kya vishwas karna hoga?"},

{"themes":["fear"],"type":"action_oriented","depth":3,"emotions":["dread","shame"],"concepts":["karma","dharma","courage"],
"en":"If you acted from your values rather than from this fear — what would you do that you are currently not doing?",
"hi":"यदि आप इस डर से नहीं बल्कि अपने मूल्यों से कार्य करें — तो आप क्या करेंगे जो अभी नहीं कर रहे?",
"hinglish":"Agar aap is dar se nahi balki apne mulyon se kaam karein — toh aap kya karenge jo abhi nahi kar rahe?"},

{"themes":["fear"],"type":"spiritual","depth":1,"emotions":["dread","longing"],"concepts":["surrender","equanimity"],
"en":"What if this fear is a messenger rather than a verdict — what might it be asking you to pay attention to?",
"hi":"क्या हो यदि यह डर एक फैसला नहीं बल्कि एक दूत है — यह आपको किस पर ध्यान देने के लिए कह रहा है?",
"hinglish":"Kya ho agar yeh dar ek faisla nahi balki ek doot hai — yeh aapko kis par dhyan dene ke liye keh raha hai?"},

{"themes":["fear"],"type":"spiritual","depth":2,"emotions":["dread","resistance"],"concepts":["surrender","equanimity","karma"],
"en":"The Gita asks you to act fully and release the outcome — what would it mean to enter this fear and act anyway?",
"hi":"गीता पूरी तरह कार्य करने और परिणाम छोड़ने को कहती है — इस डर में प्रवेश करके फिर भी कार्य करने का क्या अर्थ होगा?",
"hinglish":"Gita poori tarah kaam karne aur natija chhodne ko kehti hai — is dar mein pravesh karke phir bhi kaam karne ka kya matlab hoga?"},

{"themes":["fear"],"type":"spiritual","depth":3,"emotions":["existential","dread"],"concepts":["witness-self","surrender","impermanence"],
"en":"What if the deepest refuge from fear is not the removal of what threatens you — but recognition of what in you cannot be threatened?",
"hi":"क्या हो यदि डर से सबसे गहरी शरण वह नहीं है जो आपको खतरा देती है उसे हटाना — बल्कि यह पहचानना कि आपमें क्या है जिसे खतरा नहीं हो सकता?",
"hinglish":"Kya ho agar dar se sabse gehri sharan woh nahi hai jo aapko khatra deti hai use hatana — balki yeh pahchanana ki aap mein kya hai jise khatra nahi ho sakta?"},

# ── FORGIVENESS ──────────────────────────────────────────────────────────────
{"themes":["forgiveness"],"type":"self_awareness","depth":1,"emotions":["resentment","grief"],"concepts":["karma","forgiveness"],
"en":"What would it feel like to set down the weight of this resentment — just for this moment?",
"hi":"इस नाराज़गी के बोझ को — बस इस क्षण के लिए — रख देना कैसा लगेगा?",
"hinglish":"Is naraazgi ke bojh ko — bas is pal ke liye — rakh dena kaisa lagega?"},

{"themes":["forgiveness"],"type":"self_awareness","depth":1,"emotions":["resentment","hurt"],"concepts":["karma","forgiveness"],
"en":"What is the story you have been carrying about what happened — and how long have you been its keeper?",
"hi":"जो हुआ उसके बारे में आप जो कहानी लेकर चल रहे हैं — और आप कब से उसके रखवाले हैं?",
"hinglish":"Jo hua us ke baare mein aap jo kahani lekar chal rahe hain — aur aap kab se uske rakhwaale hain?"},

{"themes":["forgiveness"],"type":"self_awareness","depth":2,"emotions":["resentment","grief","shame"],"concepts":["forgiveness","ego","karma"],
"en":"What does holding on to this anger give you — what does it protect, or prove, or prevent?",
"hi":"इस क्रोध को थामे रहना आपको क्या देता है — यह क्या बचाता है, या सिद्ध करता है, या रोकता है?",
"hinglish":"Is krodh ko thame rehna aapko kya deta hai — yeh kya bachata hai, ya sabit karta hai, ya rokta hai?"},

{"themes":["forgiveness"],"type":"self_awareness","depth":2,"emotions":["hurt","resentment"],"concepts":["forgiveness","ego"],
"en":"If forgiving this person means nothing about what they did — what would forgiveness actually be for?",
"hi":"यदि इस व्यक्ति को क्षमा करना उन्होंने जो किया उसके बारे में कुछ नहीं कहता — तो क्षमा वास्तव में किसके लिए होगी?",
"hinglish":"Agar is insaan ko maaf karna unhone jo kiya us ke baare mein kuch nahi kehta — toh maafi asal mein kiske liye hogi?"},

{"themes":["forgiveness"],"type":"self_awareness","depth":3,"emotions":["resentment","shame","grief"],"concepts":["ego","forgiveness","karma"],
"en":"What does holding this grievance say about what you believe you are owed — and where did that belief come from?",
"hi":"इस शिकायत को थामे रहना यह क्या कहता है कि आप क्या मानते हैं आपका हक है — और वह विश्वास कहाँ से आया?",
"hinglish":"Is shikaayat ko thame rehna yeh kya kehta hai ki aap kya maante hain aapka haq hai — aur woh vishwas kahan se aaya?"},

{"themes":["forgiveness"],"type":"self_awareness","depth":3,"emotions":["resentment","existential"],"concepts":["forgiveness","ego","witness-self"],
"en":"Is there someone you need to forgive who is yourself — and what would you have to believe about yourself to do that?",
"hi":"क्या कोई है जिसे आपको क्षमा करने की ज़रूरत है और वह आप खुद हैं — और ऐसा करने के लिए आपको अपने बारे में क्या विश्वास करना होगा?",
"hinglish":"Kya koi hai jise aapko maaf karne ki zaroorat hai aur woh aap khud hain — aur aisa karne ke liye aapko apne baare mein kya vishwas karna hoga?"},

{"themes":["forgiveness"],"type":"action_oriented","depth":1,"emotions":["resentment","hurt"],"concepts":["karma","forgiveness"],
"en":"What would be the smallest act of releasing this — not full forgiveness yet, but loosening the grip slightly?",
"hi":"इसे छोड़ने का सबसे छोटा कार्य क्या होगा — पूरी क्षमा अभी नहीं, बस पकड़ को थोड़ा ढीला करना?",
"hinglish":"Ise chhodne ka sabse chhota kaam kya hoga — poori maafi abhi nahi, bas pakad ko thoda dhila karna?"},

{"themes":["forgiveness"],"type":"action_oriented","depth":2,"emotions":["resentment","resistance"],"concepts":["karma","forgiveness","detachment"],
"en":"What would it mean to stop rehearsing this injury — not to excuse what happened, but to free your attention for something else?",
"hi":"इस चोट को दोहराना बंद करने का क्या अर्थ होगा — जो हुआ उसे माफ़ करना नहीं, बल्कि अपना ध्यान किसी और चीज़ के लिए मुक्त करना?",
"hinglish":"Is chot ko dohrona band karne ka kya matlab hoga — jo hua use maaf karna nahi, balki apna dhyan kisi aur cheez ke liye mukt karna?"},

{"themes":["forgiveness"],"type":"action_oriented","depth":3,"emotions":["resentment","grief","resistance"],"concepts":["karma","forgiveness","dharma"],
"en":"If you knew that forgiveness was entirely for your own sake — not for them — what would you choose to do?",
"hi":"यदि आप जानते कि क्षमा पूरी तरह आपके अपने लिए है — उनके लिए नहीं — तो आप क्या चुनते?",
"hinglish":"Agar aap jaante ki maafi poori tarah aapke apne liye hai — unke liye nahi — toh aap kya chunte?"},

{"themes":["forgiveness"],"type":"spiritual","depth":1,"emotions":["resentment","longing"],"concepts":["forgiveness","karma","surrender"],
"en":"What if forgiveness is not something you grant to another — but a softening within yourself that lets the past be the past?",
"hi":"क्या हो यदि क्षमा कुछ ऐसा नहीं है जो आप किसी और को देते हैं — बल्कि अपने भीतर एक नरमाई है जो अतीत को अतीत रहने देती है?",
"hinglish":"Kya ho agar maafi kuch aisa nahi hai jo aap kisi aur ko dete hain — balki apne andar ek narmai hai jo ateet ko ateet rehne deti hai?"},

{"themes":["forgiveness"],"type":"spiritual","depth":2,"emotions":["resentment","grief"],"concepts":["forgiveness","karma","ego"],
"en":"The Gita speaks of acting without being bound by past actions — what would it mean to let this person's past action be complete rather than ongoing?",
"hi":"गीता पिछले कार्यों से बंधे बिना कार्य करने की बात करती है — इस व्यक्ति के पिछले कार्य को चालू रहने की बजाय पूर्ण मानने का क्या अर्थ होगा?",
"hinglish":"Gita pichle karmon se bandhe bina kaam karne ki baat karti hai — is insaan ke pichle kaam ko jari rehne ki bajaay poora maanne ka kya matlab hoga?"},

{"themes":["forgiveness"],"type":"spiritual","depth":3,"emotions":["grief","resentment","existential"],"concepts":["forgiveness","karma","witness-self","surrender"],
"en":"What if the deepest act of forgiveness is releasing your story about what should have happened — not for their sake but because you no longer wish to live inside that story?",
"hi":"क्या हो यदि क्षमा का सबसे गहरा कार्य आपकी उस कहानी को छोड़ना है कि क्या होना चाहिए था — उनके लिए नहीं, बल्कि इसलिए कि आप अब उस कहानी के भीतर नहीं जीना चाहते?",
"hinglish":"Kya ho agar maafi ka sabse gehra kaam aapki us kahani ko chhodna hai ki kya hona chahiye tha — unke liye nahi, balki isliye ki aap ab us kahani ke andar nahi jeena chahte?"},

# ── GRIEF ────────────────────────────────────────────────────────────────────
{"themes":["grief"],"type":"self_awareness","depth":1,"emotions":["grief","sadness"],"concepts":["impermanence","equanimity"],
"en":"What is the loss beneath the loss — not just the person or thing gone, but what their absence has taken with them?",
"hi":"खोने के नीचे खोना क्या है — केवल वह व्यक्ति या चीज़ नहीं जो चली गई, बल्कि उनकी अनुपस्थिति अपने साथ क्या ले गई?",
"hinglish":"Khoye ke neeche khona kya hai — sirf woh insaan ya cheez nahi jo chali gayi, balki unki anupasthiti apne saath kya le gayi?"},

{"themes":["grief"],"type":"self_awareness","depth":1,"emotions":["grief","longing"],"concepts":["impermanence"],
"en":"When this grief moves through you — what does it feel like in the body, and where does it live?",
"hi":"जब यह दुख आपसे होकर गुज़रता है — शरीर में यह कैसा महसूस होता है, और यह कहाँ रहता है?",
"hinglish":"Jab yeh dard aapse hokar guzarta hai — sharir mein yeh kaisa feel hota hai, aur yeh kahan rehta hai?"},

{"themes":["grief"],"type":"self_awareness","depth":2,"emotions":["grief","longing","sadness"],"concepts":["impermanence","ego"],
"en":"What is the shape of what you are grieving — not the story of the loss, but the actual quality of what is now absent?",
"hi":"जिसका आप शोक मना रहे हैं उसका आकार क्या है — खोने की कहानी नहीं, बल्कि जो अब अनुपस्थित है उसकी वास्तविक गुणवत्ता?",
"hinglish":"Jiska aap shok mana rahe hain uska aakar kya hai — khoye ki kahani nahi, balki jo ab anupasthit hai uski asli gunwatta?"},

{"themes":["grief"],"type":"self_awareness","depth":2,"emotions":["grief","resistance","anger"],"concepts":["impermanence","ego"],
"en":"Is there a part of you that refuses to let this go — and if so, what does that part believe holding on is doing for you?",
"hi":"क्या आपका कोई हिस्सा इसे जाने देने से इनकार करता है — और यदि हाँ, तो वह हिस्सा क्या मानता है कि थामे रखना आपके लिए क्या कर रहा है?",
"hinglish":"Kya aapka koi hissa ise jaane dene se inkar karta hai — aur agar haan, toh woh hissa kya maanta hai ki thame rakhna aapke liye kya kar raha hai?"},

{"themes":["grief"],"type":"self_awareness","depth":3,"emotions":["grief","existential","longing"],"concepts":["impermanence","ego","witness-self"],
"en":"What does this grief reveal about what you love — and what would it mean to let that love remain even after the loss?",
"hi":"यह दुख उस बारे में क्या प्रकट करता है जो आप प्यार करते हैं — और उस प्रेम को खोने के बाद भी बने रहने देने का क्या अर्थ होगा?",
"hinglish":"Yeh dard us baare mein kya prakat karta hai jo aap pyar karte hain — aur us prem ko khoye ke baad bhi bane rehne dene ka kya matlab hoga?"},

{"themes":["grief"],"type":"self_awareness","depth":3,"emotions":["grief","shame","existential"],"concepts":["impermanence","witness-self"],
"en":"Who are you becoming through this grief — not who you were before it, but who this loss is carving you into?",
"hi":"आप इस दुख के माध्यम से कौन बन रहे हैं — वह नहीं जो आप इससे पहले थे, बल्कि यह खोना आपको किसमें तराश रहा है?",
"hinglish":"Aap is dard ke zariye kaun ban rahe hain — woh nahi jo aap isse pehle the, balki yeh khona aapko kis mein tarash raha hai?"},

{"themes":["grief"],"type":"action_oriented","depth":1,"emotions":["grief","exhaustion"],"concepts":["karma","impermanence"],
"en":"What does grief ask of you right now — not what you think you should do, but what this feeling itself seems to need?",
"hi":"दुख अभी आपसे क्या माँगता है — वह नहीं जो आपको लगता है आपको करना चाहिए, बल्कि यह भावना स्वयं क्या चाहती लगती है?",
"hinglish":"Dard abhi aapse kya maangta hai — woh nahi jo aapko lagta hai aapko karna chahiye, balki yeh bhaawna khud kya chahti lagti hai?"},

{"themes":["grief"],"type":"action_oriented","depth":2,"emotions":["grief","isolation"],"concepts":["karma","equanimity"],
"en":"What would it look like to move through this grief — not around it, not through gritted teeth, but to actually let it move through you?",
"hi":"इस दुख से गुज़रना कैसा दिखेगा — इसके इर्द-गिर्द नहीं, दाँत भींचकर नहीं, बल्कि वास्तव में इसे अपने से होकर गुज़रने देना?",
"hinglish":"Is dard se guzarna kaisa dikhega — iske ird-gird nahi, daant bheenchkar nahi, balki asal mein ise apne se hokar guzarne dena?"},

{"themes":["grief"],"type":"action_oriented","depth":3,"emotions":["grief","exhaustion","longing"],"concepts":["karma","dharma","impermanence"],
"en":"What would it mean to carry this grief and still continue — not to have healed, but to have made room for both the loss and the living?",
"hi":"इस दुख को साथ लेकर चलते रहने का क्या अर्थ होगा — ठीक नहीं हुए, बल्कि खोने और जीने दोनों के लिए जगह बना ली?",
"hinglish":"Is dard ko saath lekar chalte rehne ka kya matlab hoga — theek nahi hue, balki khoye aur jeene dono ke liye jagah bana li?"},

{"themes":["grief"],"type":"spiritual","depth":1,"emotions":["grief","longing"],"concepts":["impermanence","equanimity"],
"en":"What if grief is not something to overcome but something to honor — a measure of what mattered?",
"hi":"क्या हो यदि दुख कुछ ऐसा नहीं है जिसे जीतना हो बल्कि कुछ ऐसा है जिसे सम्मान देना हो — जो मायने रखता था उसका एक माप?",
"hinglish":"Kya ho agar dard kuch aisa nahi hai jise jeetna ho balki kuch aisa hai jise samman dena ho — jo mayne rakhta tha uska ek maap?"},

{"themes":["grief"],"type":"spiritual","depth":2,"emotions":["grief","longing","sadness"],"concepts":["impermanence","equanimity","surrender"],
"en":"The Gita speaks of the soul as untouched by what the world takes — what part of what you grieve remains, even now, beyond the reach of loss?",
"hi":"गीता आत्मा को उस चीज़ से अछूती बताती है जो दुनिया लेती है — जिसका आप शोक करते हैं उसमें से कौन-सा हिस्सा अब भी, खोने की पहुँच से परे, बचा है?",
"hinglish":"Gita aatma ko us cheez se achhoot batati hai jo duniya leti hai — jiska aap shok karte hain us mein se kaun sa hissa ab bhi, khoye ki pahunch se pare, bacha hai?"},

{"themes":["grief"],"type":"spiritual","depth":3,"emotions":["grief","existential","longing"],"concepts":["impermanence","witness-self","surrender"],
"en":"What if this grief is not just yours — what if it is the weight all beings carry in a world of impermanence, and in feeling it you are not alone?",
"hi":"क्या हो यदि यह दुख केवल आपका नहीं है — यदि यह वह बोझ है जो सभी प्राणी अनित्यता की दुनिया में उठाते हैं, और इसे महसूस करने में आप अकेले नहीं हैं?",
"hinglish":"Kya ho agar yeh dard sirf aapka nahi hai — agar yeh woh bojh hai jo sabhi prani anitya ki duniya mein uthate hain, aur ise mahsoos karne mein aap akele nahi hain?"},

# ── JEALOUSY ────────────────────────────────────────────────────────────────
{"themes":["jealousy"],"type":"self_awareness","depth":1,"emotions":["envy","inadequacy"],"concepts":["ego","svadharma"],
"en":"When jealousy rises — what specifically does the other person seem to have that you feel you lack?",
"hi":"जब ईर्ष्या उठती है — दूसरे व्यक्ति के पास विशेष रूप से क्या लगता है जो आपको लगता है आपके पास नहीं?",
"hinglish":"Jab irshya uthti hai — doosre insaan ke paas khaas taur par kya lagta hai jo aapko lagta hai aapke paas nahi?"},

{"themes":["jealousy"],"type":"self_awareness","depth":1,"emotions":["envy","shame"],"concepts":["ego"],
"en":"What is it like to admit this jealousy honestly — to say: I want what they have?",
"hi":"इस ईर्ष्या को ईमानदारी से स्वीकार करना — यह कहना कि मुझे वह चाहिए जो उनके पास है — कैसा लगता है?",
"hinglish":"Is irshya ko imaandaari se sweekar karna — yeh kehna ki mujhe woh chahiye jo unke paas hai — kaisa lagta hai?"},

{"themes":["jealousy"],"type":"self_awareness","depth":2,"emotions":["envy","shame","inadequacy"],"concepts":["ego","svadharma","comparison"],
"en":"What does this jealousy tell you about what you actually want for your own life — stripped of comparison?",
"hi":"यह ईर्ष्या आपको आपके अपने जीवन के लिए आप वास्तव में क्या चाहते हैं — तुलना से अलग करके — इस बारे में क्या बताती है?",
"hinglish":"Yeh irshya aapko aapke apne jeevan ke liye aap asal mein kya chahte hain — tulna se alag karke — is baare mein kya batati hai?"},

{"themes":["jealousy"],"type":"self_awareness","depth":2,"emotions":["envy","resentment"],"concepts":["ego","karma"],
"en":"What would have to be true about your own path for their success to feel like good news rather than a threat?",
"hi":"आपके अपने मार्ग के बारे में क्या सच होना होगा ताकि उनकी सफलता खतरे की जगह अच्छी खबर लगे?",
"hinglish":"Aapke apne raaste ke baare mein kya sach hona hoga taaki unki safalta khatre ki jagah achchi khabar lage?"},

{"themes":["jealousy"],"type":"self_awareness","depth":3,"emotions":["envy","shame","existential"],"concepts":["ego","svadharma","witness-self"],
"en":"What does the strength of this jealousy reveal about what you believe is possible for you — and is that belief accurate?",
"hi":"इस ईर्ष्या की तीव्रता आपके लिए क्या संभव है इस विश्वास के बारे में क्या प्रकट करती है — और क्या वह विश्वास सटीक है?",
"hinglish":"Is irshya ki tivrata aapke liye kya sambhav hai is vishwas ke baare mein kya prakat karti hai — aur kya woh vishwas sateek hai?"},

{"themes":["jealousy"],"type":"self_awareness","depth":3,"emotions":["envy","shame","resentment"],"concepts":["ego","witness-self","karma"],
"en":"If you were fully living your own path with full conviction — what would this person's life mean to you?",
"hi":"यदि आप पूरी तरह अपने मार्ग पर पूर्ण विश्वास के साथ जी रहे हों — तो इस व्यक्ति का जीवन आपके लिए क्या अर्थ रखता?",
"hinglish":"Agar aap poori tarah apne raaste par poorn vishwas ke saath ji rahe hon — toh is insaan ka jeevan aapke liye kya arth rakhta?"},

{"themes":["jealousy"],"type":"action_oriented","depth":1,"emotions":["envy","restlessness"],"concepts":["karma","svadharma"],
"en":"What energy that goes into this jealousy could be redirected — and toward what?",
"hi":"इस ईर्ष्या में जो ऊर्जा जाती है उसे पुनर्निर्देशित किया जा सकता है — और किस ओर?",
"hinglish":"Is irshya mein jo urja jaati hai use punarnirdeshit kiya ja sakta hai — aur kis taraf?"},

{"themes":["jealousy"],"type":"action_oriented","depth":2,"emotions":["envy","inadequacy"],"concepts":["karma","svadharma","dharma"],
"en":"What would you need to start doing — genuinely and consistently — for the jealousy to slowly lose its grip?",
"hi":"जलन की पकड़ धीरे-धीरे ढीली हो जाए इसके लिए आपको क्या शुरू करने की ज़रूरत होगी — वास्तव में और लगातार?",
"hinglish":"Jalan ki pakad dheere-dheere dhili ho jaaye iske liye aapko kya shuru karne ki zaroorat hogi — asal mein aur lagaatar?"},

{"themes":["jealousy"],"type":"action_oriented","depth":3,"emotions":["envy","shame","grief"],"concepts":["karma","svadharma","detachment"],
"en":"What would it look like to genuinely want what is good for this person — not because you have no wants of your own, but because you have found something steadier?",
"hi":"इस व्यक्ति के लिए जो अच्छा हो वह वास्तव में चाहना कैसा दिखेगा — इसलिए नहीं कि आपकी अपनी कोई इच्छा नहीं है, बल्कि इसलिए कि आपने कुछ अधिक स्थिर पाया है?",
"hinglish":"Is insaan ke liye jo achha ho woh asal mein chahna kaisa dikhega — isliye nahi ki aapki apni koi ichha nahi hai, balki isliye ki aapne kuch zyada sthir paya hai?"},

{"themes":["jealousy"],"type":"spiritual","depth":1,"emotions":["envy","inadequacy"],"concepts":["svadharma","ego"],
"en":"What if the longing inside this jealousy is pointing at something real that belongs to your own path — not theirs?",
"hi":"क्या हो यदि इस ईर्ष्या के भीतर की लालसा किसी वास्तविक चीज़ की ओर इशारा कर रही है जो आपके अपने मार्ग की है — उनके नहीं?",
"hinglish":"Kya ho agar is irshya ke andar ki lalsa kisi asli cheez ki taraf ishara kar rahi hai jo aapke apne raaste ki hai — unke nahi?"},

{"themes":["jealousy"],"type":"spiritual","depth":2,"emotions":["envy","shame"],"concepts":["svadharma","ego","karma"],
"en":"What would change in how you see their blessing if you trusted that it does not diminish yours — that abundance does not work that way?",
"hi":"यदि आप विश्वास करें कि उनका आशीर्वाद आपका कम नहीं करता — कि प्रचुरता इस तरह काम नहीं करती — तो उनकी खुशहाली को देखने का आपका तरीका कैसे बदलेगा?",
"hinglish":"Agar aap trust karein ki unka ashirwad aapka kam nahi karta — ki prachurta is tarah kaam nahi karti — toh unki khushhaali ko dekhne ka aapka tarika kaise badlega?"},

{"themes":["jealousy"],"type":"spiritual","depth":3,"emotions":["envy","existential","shame"],"concepts":["svadharma","ego","witness-self"],
"en":"If there is a witness in you that watches even jealousy without being consumed by it — what does that witness see that the jealous self cannot?",
"hi":"यदि आप में कोई साक्षी है जो ईर्ष्या को भी उससे ग्रसित हुए बिना देखता है — वह साक्षी क्या देखता है जो ईर्ष्यालु स्वयं नहीं देख सकता?",
"hinglish":"Agar aap mein koi saakshi hai jo irshya ko bhi us se grast hue bina dekhta hai — woh saakshi kya dekhta hai jo irshyaalu khud nahi dekh sakta?"},

# ── LAZINESS ────────────────────────────────────────────────────────────────
{"themes":["laziness"],"type":"self_awareness","depth":1,"emotions":["guilt","inertia"],"concepts":["tamas","karma"],
"en":"When you call yourself lazy — what is actually happening beneath that word?",
"hi":"जब आप खुद को आलसी कहते हैं — उस शब्द के नीचे वास्तव में क्या हो रहा है?",
"hinglish":"Jab aap khud ko aalsi kehte hain — us shabd ke neeche asal mein kya ho raha hai?"},

{"themes":["laziness"],"type":"self_awareness","depth":1,"emotions":["guilt","avoidance"],"concepts":["tamas","karma"],
"en":"What is the thing you are not starting — and what would have to happen for you to begin?",
"hi":"वह काम जो आप शुरू नहीं कर रहे — और शुरू करने के लिए क्या होना होगा?",
"hinglish":"Woh kaam jo aap shuru nahi kar rahe — aur shuru karne ke liye kya hona hoga?"},

{"themes":["laziness"],"type":"self_awareness","depth":2,"emotions":["guilt","shame","avoidance"],"concepts":["tamas","ego","karma"],
"en":"Is this inertia protecting you from something — from failure, from judgment, from discovering something you don't want to know?",
"hi":"क्या यह जड़ता आपको किसी चीज़ से बचा रही है — विफलता से, आलोचना से, कुछ ऐसा खोजने से जो आप नहीं जानना चाहते?",
"hinglish":"Kya yeh jadta aapko kisi cheez se bacha rahi hai — vifalta se, aalochana se, kuch aisa khojne se jo aap nahi jaanna chahte?"},

{"themes":["laziness"],"type":"self_awareness","depth":2,"emotions":["guilt","inertia"],"concepts":["tamas","ego"],
"en":"What is the difference between rest you have earned and avoidance disguised as rest — and which is this?",
"hi":"जो विश्राम आपने अर्जित किया है और परिहार जो विश्राम के रूप में छुपा है — उनके बीच क्या अंतर है, और यह कौन-सा है?",
"hinglish":"Jo vishram aapne arjit kiya hai aur parihar jo vishram ke roop mein chhuupa hai — unke beech kya antar hai, aur yeh kaun sa hai?"},

{"themes":["laziness"],"type":"self_awareness","depth":3,"emotions":["shame","guilt","inertia"],"concepts":["tamas","ego","karma"],
"en":"If you look honestly at the pattern of avoidance — what have you been putting off not for days but for years, and what does that cost you?",
"hi":"यदि आप परिहार के पैटर्न को ईमानदारी से देखें — आप क्या दिनों से नहीं बल्कि सालों से टाल रहे हैं, और इसकी कीमत क्या है?",
"hinglish":"Agar aap parihar ke pattern ko imaandaari se dekhein — aap kya dinon se nahi balki salon se taal rahe hain, aur iski keemat kya hai?"},

{"themes":["laziness"],"type":"self_awareness","depth":3,"emotions":["shame","inertia","existential"],"concepts":["tamas","ego","dharma"],
"en":"What would the version of you who did not have this pattern be doing with the time and energy you are spending on not-doing?",
"hi":"आपका वह संस्करण जिसके पास यह पैटर्न नहीं होता — न करने में जो समय और ऊर्जा आप खर्च कर रहे हैं उससे क्या करता?",
"hinglish":"Aapka woh version jiske paas yeh pattern nahi hota — na karne mein jo samay aur urja aap kharch kar rahe hain us se kya karta?"},

{"themes":["laziness"],"type":"action_oriented","depth":1,"emotions":["guilt","inertia"],"concepts":["karma"],
"en":"What is the smallest possible beginning you could make right now — not the whole thing, just one minute of starting?",
"hi":"अभी आप जो सबसे छोटी शुरुआत कर सकते हैं — पूरा नहीं, बस एक मिनट शुरू करना — वह क्या है?",
"hinglish":"Abhi aap jo sabse choti shuruaat kar sakte hain — poora nahi, bas ek minute shuru karna — woh kya hai?"},

{"themes":["laziness"],"type":"action_oriented","depth":2,"emotions":["inertia","resistance"],"concepts":["karma","discipline"],
"en":"What time or environment makes it easiest for you to begin — and are you protecting that condition for yourself?",
"hi":"कौन-सा समय या परिवेश आपके लिए शुरू करना सबसे आसान बनाता है — और क्या आप अपने लिए उस स्थिति की रक्षा कर रहे हैं?",
"hinglish":"Kaun sa samay ya parivesh aapke liye shuru karna sabse aasaan banata hai — aur kya aap apne liye us sthiti ki suraksha kar rahe hain?"},

{"themes":["laziness"],"type":"action_oriented","depth":3,"emotions":["shame","guilt","inertia"],"concepts":["karma","dharma","discipline"],
"en":"What would it mean to show up for your own life — not when you feel like it, not when conditions are perfect, but as a practice of commitment?",
"hi":"अपने ही जीवन के लिए उपस्थित होने का क्या अर्थ होगा — जब मन हो तब नहीं, जब परिस्थितियाँ सही हों तब नहीं, बल्कि प्रतिबद्धता के अभ्यास के रूप में?",
"hinglish":"Apne hi jeevan ke liye maujood hone ka kya matlab hoga — jab mann ho tab nahi, jab paristhitiyan sahi hon tab nahi, balki pratibaddhata ke abhyas ke roop mein?"},

{"themes":["laziness"],"type":"spiritual","depth":1,"emotions":["guilt","inertia"],"concepts":["tamas","karma"],
"en":"What if this heaviness is not a character flaw but energy that has not yet found its right direction — where might that direction be?",
"hi":"क्या हो यदि यह भारीपन कोई चारित्रिक दोष नहीं है बल्कि वह ऊर्जा है जिसे अभी सही दिशा नहीं मिली — वह दिशा कहाँ हो सकती है?",
"hinglish":"Kya ho agar yeh bhaariapan koi charitrik dosh nahi hai balki woh urja hai jise abhi sahi disha nahi mili — woh disha kahan ho sakti hai?"},

{"themes":["laziness"],"type":"spiritual","depth":2,"emotions":["inertia","guilt"],"concepts":["tamas","karma","dharma"],
"en":"The Gita speaks of tamas as the guna of heaviness and sleep — what would it mean to choose rajas or sattva right now, even slightly?",
"hi":"गीता तमस को भारीपन और नींद के गुण के रूप में बताती है — अभी, थोड़ा भी, रजस या सत्व चुनने का क्या अर्थ होगा?",
"hinglish":"Gita tamas ko bhaariapan aur neend ke gun ke roop mein batati hai — abhi, thoda bhi, rajas ya sattva chunne ka kya matlab hoga?"},

{"themes":["laziness"],"type":"spiritual","depth":3,"emotions":["shame","inertia","existential"],"concepts":["tamas","karma","dharma","witness-self"],
"en":"What would it mean to offer your effort — not for the result, not to escape the shame, but simply as an act of honoring the life you were given?",
"hi":"अपना प्रयास अर्पित करने का क्या अर्थ होगा — परिणाम के लिए नहीं, शर्म से बचने के लिए नहीं, बल्कि केवल जो जीवन आपको मिला है उसे सम्मान देने के कार्य के रूप में?",
"hinglish":"Apna prayas arpit karne ka kya matlab hoga — natije ke liye nahi, sharm se bachne ke liye nahi, balki sirf jo jeevan aapko mila hai use samman dene ke kaam ke roop mein?"},
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
    print(f"Batch 3 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
