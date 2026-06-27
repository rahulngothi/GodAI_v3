"""Bulk seed batch 6: family (0 coverage) + uncertainty (0 coverage)."""
from __future__ import annotations
import datetime, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import get_db, REFLECTIVE_QUESTIONS, ensure_reflective_indexes

QUESTIONS = [
# ── FAMILY ───────────────────────────────────────────────────────────────────
{"themes":["family"],"type":"self_awareness","depth":1,"emotions":["guilt","longing"],"concepts":["dharma","relationships"],
"en":"What is the role you play in your family — and is it one you chose, or one that was assigned to you long ago?",
"hi":"परिवार में आपकी भूमिका क्या है — और क्या यह कुछ ऐसा है जो आपने चुना, या जो आपको बहुत पहले सौंपी गई थी?",
"hinglish":"Parivaar mein aapki bhumika kya hai — aur kya yeh kuch aisa hai jo aapne chuna, ya jo aapko bahut pehle saunpi gayi thi?"},

{"themes":["family"],"type":"self_awareness","depth":1,"emotions":["resentment","longing"],"concepts":["dharma","ego"],
"en":"Which family member do you find most difficult — and what does your reaction to them reveal about yourself?",
"hi":"परिवार का कौन-सा सदस्य आपको सबसे कठिन लगता है — और उनके प्रति आपकी प्रतिक्रिया आपके बारे में क्या प्रकट करती है?",
"hinglish":"Parivaar ka kaun sa sadasya aapko sabse mushkil lagta hai — aur unke prati aapki pratikriya aapke baare mein kya prakat karti hai?"},

{"themes":["family"],"type":"self_awareness","depth":2,"emotions":["guilt","resentment","grief"],"concepts":["dharma","ego","karma"],
"en":"What wound from your family of origin are you still carrying — and how is it showing up in your life today?",
"hi":"अपने मूल परिवार से कौन-सा ज़ख्म आप अभी भी लेकर चल रहे हैं — और यह आज आपके जीवन में कैसे प्रकट हो रहा है?",
"hinglish":"Apne mool parivaar se kaun sa zakham aap abhi bhi lekar chal rahe hain — aur yeh aaj aapke jeevan mein kaise prakat ho raha hai?"},

{"themes":["family"],"type":"self_awareness","depth":2,"emotions":["guilt","shame","longing"],"concepts":["dharma","ego","relationships"],
"en":"What have you inherited from your family — in patterns, beliefs, fears — that you have never consciously examined?",
"hi":"परिवार से आपको क्या विरासत में मिला है — पैटर्न में, मान्यताओं में, डरों में — जिसे आपने कभी सचेत रूप से जाँचा नहीं है?",
"hinglish":"Parivaar se aapko kya virasat mein mila hai — patterns mein, manyataon mein, daron mein — jise aapne kabhi sachet roop se jaancha nahi hai?"},

{"themes":["family"],"type":"self_awareness","depth":3,"emotions":["grief","resentment","existential"],"concepts":["dharma","ego","karma","forgiveness"],
"en":"What is the thing you most wish you could say to a family member — and what stops you from saying it?",
"hi":"परिवार के किसी सदस्य से सबसे अधिक क्या कहना चाहेंगे — और क्या आपको कहने से रोकता है?",
"hinglish":"Parivaar ke kisi sadasya se sabse zyada kya kehna chahenge — aur kya aapko kehne se rokta hai?"},

{"themes":["family"],"type":"self_awareness","depth":3,"emotions":["grief","shame","existential"],"concepts":["dharma","ego","witness-self","karma"],
"en":"Who in your family did you most want to see you — and did they? What did that experience make you believe about yourself?",
"hi":"परिवार में कौन आपको सबसे अधिक देखे यह आप चाहते थे — और क्या उन्होंने देखा? उस अनुभव ने आपको अपने बारे में क्या मानने पर मजबूर किया?",
"hinglish":"Parivaar mein kaun aapko sabse zyada dekhe yeh aap chahte the — aur kya unhone dekha? Us anubhav ne aapko apne baare mein kya maanne par majboor kiya?"},

{"themes":["family"],"type":"action_oriented","depth":1,"emotions":["guilt","longing"],"concepts":["karma","dharma"],
"en":"What is one genuine act of connection you could offer to your family this week — not out of obligation but out of care?",
"hi":"इस सप्ताह आप अपने परिवार को एक वास्तविक जुड़ाव का कार्य दे सकते हैं — दायित्व से नहीं बल्कि देखभाल से?",
"hinglish":"Is hafte aap apne parivaar ko ek asli judav ka kaam de sakte hain — dayitva se nahi balki dekhbhaal se?"},

{"themes":["family"],"type":"action_oriented","depth":1,"emotions":["resentment","avoidance"],"concepts":["karma","dharma"],
"en":"Which family relationship have you been avoiding — and what one small step could you take toward it?",
"hi":"कौन-सा पारिवारिक संबंध आप टाल रहे हैं — और इसकी ओर एक छोटा कदम क्या हो सकता है?",
"hinglish":"Kaun sa paarivaarik sambandh aap taal rahe hain — aur iski taraf ek chhota kadam kya ho sakta hai?"},

{"themes":["family"],"type":"action_oriented","depth":2,"emotions":["guilt","resentment","resistance"],"concepts":["karma","dharma","detachment"],
"en":"What pattern do you keep repeating in your family — and what would it look like to consciously break it, just once?",
"hi":"आप परिवार में कौन-सा पैटर्न दोहराते रहते हैं — और इसे सचेत रूप से तोड़ना, बस एक बार, कैसा दिखेगा?",
"hinglish":"Aap parivaar mein kaun sa pattern doharaate rehte hain — aur ise sachet roop se todna, bas ek baar, kaisa dikhega?"},

{"themes":["family"],"type":"action_oriented","depth":2,"emotions":["grief","longing"],"concepts":["karma","dharma","forgiveness"],
"en":"What conversation have you been putting off with a family member — and what would it take to have it with care?",
"hi":"किस पारिवारिक सदस्य के साथ कौन-सी बातचीत आप टाल रहे हैं — और उसे देखभाल से करने के लिए क्या चाहिए?",
"hinglish":"Kis paarivaarik sadasya ke saath kaun si baatcheet aap taal rahe hain — aur use dekhbhaal se karne ke liye kya chahiye?"},

{"themes":["family"],"type":"action_oriented","depth":3,"emotions":["grief","resentment","shame"],"concepts":["karma","dharma","forgiveness","detachment"],
"en":"What would it mean to love your family members as they actually are — not as you need them to be — and what would shift if you did?",
"hi":"अपने परिवार के सदस्यों को वैसे प्यार करने का क्या अर्थ होगा जैसे वे वास्तव में हैं — न कि जैसे आपको उन्हें होना चाहिए — और यदि आप ऐसा करें तो क्या बदलेगा?",
"hinglish":"Apne parivaar ke sadasyon ko waise pyar karne ka kya matlab hoga jaise woh asal mein hain — na ki jaise aapko unhe hona chahiye — aur agar aap aisa karein toh kya badlega?"},

{"themes":["family"],"type":"action_oriented","depth":3,"emotions":["grief","shame","existential"],"concepts":["karma","dharma","ego","surrender"],
"en":"What would it take to stop needing your family to validate who you have become — and what would that freedom feel like?",
"hi":"अपने परिवार को इस बात की पुष्टि करने की ज़रूरत बंद करने के लिए क्या चाहिए कि आप कौन बन गए हैं — और वह स्वतंत्रता कैसी लगेगी?",
"hinglish":"Apne parivaar ko is baat ki pushti karne ki zaroorat band karne ke liye kya chahiye ki aap kaun ban gaye hain — aur woh swatantrata kaisi lagegi?"},

{"themes":["family"],"type":"spiritual","depth":1,"emotions":["guilt","longing"],"concepts":["dharma","karma","relationships"],
"en":"What if your family — with all its difficulty — is exactly the teacher this life chose to assign to you?",
"hi":"क्या हो यदि आपका परिवार — अपनी सारी कठिनाइयों के साथ — ठीक वह गुरु है जिसे इस जीवन ने आपको सौंपना चुना?",
"hinglish":"Kya ho agar aapka parivaar — apni saari mushkilon ke saath — theek woh guru hai jise is jeevan ne aapko saunpna chuna?"},

{"themes":["family"],"type":"spiritual","depth":1,"emotions":["resentment","longing"],"concepts":["dharma","karma"],
"en":"What spiritual quality — patience, forgiveness, selflessness — is your family most directly inviting you to develop?",
"hi":"कौन-सी आध्यात्मिक गुणवत्ता — धैर्य, क्षमा, निःस्वार्थता — आपका परिवार सबसे सीधे आपको विकसित करने के लिए आमंत्रित कर रहा है?",
"hinglish":"Kaun si aadhyatmik gunwatta — dhairya, kshama, nihsvaarthat — aapka parivaar sabse seedhe aapko viksit karne ke liye aamantrit kar raha hai?"},

{"themes":["family"],"type":"spiritual","depth":2,"emotions":["grief","resentment"],"concepts":["dharma","karma","forgiveness","ego"],
"en":"What if you and each family member arrived into this constellation not by accident — and what would it ask of you to believe that?",
"hi":"क्या हो यदि आप और परिवार का प्रत्येक सदस्य इस नक्षत्र में संयोग से नहीं आए — और इस पर विश्वास करना आपसे क्या माँगेगा?",
"hinglish":"Kya ho agar aap aur parivaar ka har sadasya is nakshatra mein sanyog se nahi aaye — aur is par vishwas karna aapse kya maangega?"},

{"themes":["family"],"type":"spiritual","depth":2,"emotions":["guilt","shame"],"concepts":["dharma","karma","ego"],
"en":"The patterns that repeat across generations in your family — what are they carrying that has not yet been healed or understood?",
"hi":"आपके परिवार में पीढ़ियों में दोहराए जाने वाले पैटर्न — वे क्या लेकर चल रहे हैं जो अभी तक भरा या समझा नहीं गया है?",
"hinglish":"Aapke parivaar mein pidhiyon mein doharaaye jaane wale patterns — woh kya lekar chal rahe hain jo abhi tak bhara ya samjha nahi gaya hai?"},

{"themes":["family"],"type":"spiritual","depth":3,"emotions":["grief","existential","longing"],"concepts":["dharma","karma","ego","impermanence"],
"en":"If this family was the exact soil your soul needed to grow in — with all the rocks and shade and drought — what gifts are buried in what you have always called wounds?",
"hi":"यदि यह परिवार ठीक वह मिट्टी थी जिसमें आपकी आत्मा को उगना था — सभी पत्थरों, छाया और सूखे के साथ — तो जिसे आपने हमेशा ज़ख्म कहा उसमें कौन-से उपहार दबे हैं?",
"hinglish":"Agar yeh parivaar theek woh mitti thi jis mein aapki aatma ko ugna tha — sabhi pathron, chhaya aur sookhe ke saath — toh jise aapne hamesha zakham kaha us mein kaun se uphaar dabe hain?"},

{"themes":["family"],"type":"spiritual","depth":3,"emotions":["grief","shame","existential"],"concepts":["dharma","karma","surrender","witness-self"],
"en":"What would it mean to both belong to your family fully and remain your own soul — neither lost in the collective nor cut off from it?",
"hi":"अपने परिवार से पूरी तरह संबंधित होने और अपनी आत्मा बनी रहने का क्या अर्थ होगा — न सामूहिक में खो जाना, न उससे कट जाना?",
"hinglish":"Apne parivaar se poori tarah sambandhit hone aur apni aatma bani rehne ka kya matlab hoga — na saamoohik mein kho jaana, na usse kat jaana?"},

# ── UNCERTAINTY ───────────────────────────────────────────────────────────────
{"themes":["uncertainty"],"type":"self_awareness","depth":1,"emotions":["anxiety","confusion"],"concepts":["surrender","equanimity"],
"en":"What is it about not knowing that feels most unbearable — what does the uncertainty threaten to take from you?",
"hi":"न जानने में क्या है जो सबसे असहनीय लगता है — अनिश्चितता आपसे क्या छीनने की धमकी देती है?",
"hinglish":"Na jaanne mein kya hai jo sabse asahneeya lagta hai — anishchitata aapse kya chheenne ki dhamki deti hai?"},

{"themes":["uncertainty"],"type":"self_awareness","depth":1,"emotions":["anxiety","restlessness"],"concepts":["surrender","equanimity"],
"en":"In this uncertain situation — what do you actually know for sure, and what are you only assuming?",
"hi":"इस अनिश्चित स्थिति में — आप वास्तव में क्या निश्चित रूप से जानते हैं, और क्या आप केवल मान रहे हैं?",
"hinglish":"Is anishchit situation mein — aap asal mein kya nishchit roop se jaante hain, aur kya aap sirf maan rahe hain?"},

{"themes":["uncertainty"],"type":"self_awareness","depth":2,"emotions":["anxiety","dread","confusion"],"concepts":["surrender","ego","equanimity"],
"en":"What beliefs about how life is supposed to work are being challenged by this uncertainty — and where did those beliefs come from?",
"hi":"जीवन कैसे काम करना चाहिए इस बारे में कौन-सी मान्यताएँ इस अनिश्चितता से चुनौती दी जा रही हैं — और वे मान्यताएँ कहाँ से आईं?",
"hinglish":"Jeevan kaise kaam karna chahiye is baare mein kaun si manyataain is anishchitata se chunauti di ja rahi hain — aur woh manyataain kahan se aayin?"},

{"themes":["uncertainty"],"type":"self_awareness","depth":2,"emotions":["anxiety","shame","confusion"],"concepts":["ego","surrender","control"],
"en":"When you cannot control the outcome — what do you discover about who you are when the safety of certainty is removed?",
"hi":"जब आप परिणाम को नियंत्रित नहीं कर सकते — जब निश्चितता की सुरक्षा हट जाती है तो आप कौन हैं इसके बारे में आप क्या खोजते हैं?",
"hinglish":"Jab aap natija control nahi kar sakte — jab nishchitata ki suraksha hat jaati hai toh aap kaun hain is baare mein aap kya khojte hain?"},

{"themes":["uncertainty"],"type":"self_awareness","depth":3,"emotions":["existential","dread","anxiety"],"concepts":["ego","surrender","witness-self","impermanence"],
"en":"What if uncertainty is not a problem that good planning could solve — but the actual nature of existence, asking you to meet it differently?",
"hi":"क्या हो यदि अनिश्चितता कोई समस्या नहीं है जिसे अच्छी योजना से हल किया जा सके — बल्कि अस्तित्व की वास्तविक प्रकृति है, जो आपसे इसे अलग तरह से मिलने के लिए कह रही है?",
"hinglish":"Kya ho agar anishchitata koi samasya nahi hai jise achchi yojana se hal kiya ja sake — balki astitva ki asli prakriti hai, jo aapse ise alag tarah se milne ke liye keh rahi hai?"},

{"themes":["uncertainty"],"type":"self_awareness","depth":3,"emotions":["existential","dread"],"concepts":["ego","witness-self","surrender","impermanence"],
"en":"If you accepted that you will never fully know how this will turn out — what would become possible in how you live right now?",
"hi":"यदि आप स्वीकार करें कि आप कभी पूरी तरह नहीं जान सकते कि यह कैसे समाप्त होगा — तो अभी आप जिस तरह जीते हैं उसमें क्या संभव हो सकता है?",
"hinglish":"Agar aap sweekar karein ki aap kabhi poori tarah nahi jaan sakte ki yeh kaise khatam hoga — toh abhi aap jis tarah jeete hain us mein kya sambhav ho sakta hai?"},

{"themes":["uncertainty"],"type":"action_oriented","depth":1,"emotions":["anxiety","paralysis"],"concepts":["karma","surrender"],
"en":"Without waiting for certainty — what is one step you can take today based on what you know right now?",
"hi":"निश्चितता की प्रतीक्षा किए बिना — आज एक कदम जो आप अभी जो जानते हैं उसके आधार पर उठा सकते हैं?",
"hinglish":"Nishchitata ka intezaar kiye bina — aaj ek kadam jo aap abhi jo jaante hain uske aadhar par utha sakte hain?"},

{"themes":["uncertainty"],"type":"action_oriented","depth":1,"emotions":["anxiety","confusion"],"concepts":["karma","dharma"],
"en":"What would you do today if you treated this uncertainty as a temporary condition rather than a permanent one?",
"hi":"यदि आप इस अनिश्चितता को एक स्थायी स्थिति के बजाय अस्थायी मानें — तो आज आप क्या करेंगे?",
"hinglish":"Agar aap is anishchitata ko ek sthayi sthiti ki bajaay asthaayi maanein — toh aaj aap kya karenge?"},

{"themes":["uncertainty"],"type":"action_oriented","depth":2,"emotions":["anxiety","resistance"],"concepts":["karma","dharma","detachment"],
"en":"What is the most meaningful action available to you right now — regardless of whether you can guarantee how it will turn out?",
"hi":"अभी आपके लिए सबसे सार्थक क्रिया क्या है — चाहे आप इसके परिणाम की गारंटी दे सकें या नहीं?",
"hinglish":"Abhi aapke liye sabse saarthak kriya kya hai — chahe aap iske natije ki guarantee de sakein ya nahi?"},

{"themes":["uncertainty"],"type":"action_oriented","depth":2,"emotions":["anxiety","confusion","paralysis"],"concepts":["karma","svadharma","surrender"],
"en":"If you separated what is yours to do from what is not yours to control — what does your list of actions actually look like right now?",
"hi":"यदि आप जो करना आपका है और जो नियंत्रित करना आपका नहीं है उसे अलग करें — तो आपकी क्रियाओं की सूची अभी वास्तव में कैसी दिखती है?",
"hinglish":"Agar aap jo karna aapka hai aur jo control karna aapka nahi hai use alag karein — toh aapki kriyaon ki list abhi asal mein kaisi dikhti hai?"},

{"themes":["uncertainty"],"type":"action_oriented","depth":3,"emotions":["dread","resistance","existential"],"concepts":["karma","dharma","surrender","detachment"],
"en":"What would it look like to move forward — committed, full-hearted — while holding the outcome in an open hand?",
"hi":"आगे बढ़ना कैसा दिखेगा — प्रतिबद्ध, पूरे दिल से — लेकिन परिणाम को खुले हाथ में थामते हुए?",
"hinglish":"Aage badhna kaisa dikhega — pratibaddh, poore dil se — lekin natija ko khule haath mein thaamate hue?"},

{"themes":["uncertainty"],"type":"action_oriented","depth":3,"emotions":["existential","dread","anxiety"],"concepts":["karma","dharma","surrender"],
"en":"What values would guide you through this — even if you never know how it ends — and are you already living them?",
"hi":"कौन-से मूल्य आपको इसमें से गुज़रने में मार्गदर्शन करेंगे — भले ही आप कभी न जानें यह कैसे समाप्त होता है — और क्या आप पहले से उन्हें जी रहे हैं?",
"hinglish":"Kaun se mulya aapko ismein se guzarne mein maargdarshan karenge — chahe aap kabhi na jaanein yeh kaise khatam hota hai — aur kya aap pehle se unhe ji rahe hain?"},

{"themes":["uncertainty"],"type":"spiritual","depth":1,"emotions":["anxiety","confusion"],"concepts":["surrender","equanimity","karma"],
"en":"What would it feel like to be at peace — not because you know how this ends, but because you trust the ground beneath the uncertainty?",
"hi":"शांति में होना कैसा लगेगा — इसलिए नहीं कि आप जानते हैं यह कैसे समाप्त होगा, बल्कि इसलिए कि आप अनिश्चितता के नीचे की नींव पर भरोसा करते हैं?",
"hinglish":"Shanti mein hona kaisa lagega — isliye nahi ki aap jaante hain yeh kaise khatam hoga, balki isliye ki aap anishchitata ke neeche ki neenv par bharosa karte hain?"},

{"themes":["uncertainty"],"type":"spiritual","depth":1,"emotions":["anxiety","longing"],"concepts":["surrender","equanimity"],
"en":"What if uncertainty is not a gap to be filled with worry — but an open space where something new can enter?",
"hi":"क्या हो यदि अनिश्चितता चिंता से भरने की कोई खाई नहीं है — बल्कि एक खुली जगह है जहाँ कुछ नया प्रवेश कर सकता है?",
"hinglish":"Kya ho agar anishchitata chinta se bharne ki koi khaai nahi hai — balki ek khuli jagah hai jahan kuch naya pravesh kar sakta hai?"},

{"themes":["uncertainty"],"type":"spiritual","depth":2,"emotions":["anxiety","dread"],"concepts":["surrender","equanimity","karma"],
"en":"The Gita asks you to act fully and release the outcome entirely — what would that kind of courage look like, lived into this situation?",
"hi":"गीता पूरी तरह कार्य करने और परिणाम को पूरी तरह छोड़ने के लिए कहती है — उस प्रकार का साहस इस स्थिति में जीया जाए तो कैसा दिखेगा?",
"hinglish":"Gita poori tarah kaam karne aur natija ko poori tarah chhodne ke liye kehti hai — us prakar ka sahas is situation mein jiya jaaye toh kaisa dikhega?"},

{"themes":["uncertainty"],"type":"spiritual","depth":2,"emotions":["anxiety","confusion","longing"],"concepts":["surrender","equanimity","witness-self"],
"en":"What if the part of you that needs certainty is the same part that can never actually have it — and there is something deeper in you that was never disturbed by not knowing?",
"hi":"क्या हो यदि आपका वह हिस्सा जिसे निश्चितता चाहिए वही है जो इसे कभी वास्तव में नहीं पा सकता — और आपमें कुछ गहरा है जो न जानने से कभी परेशान नहीं हुआ?",
"hinglish":"Kya ho agar aapka woh hissa jise nishchitata chahiye wahi hai jo ise kabhi asal mein nahi pa sakta — aur aap mein kuch gehra hai jo na jaanne se kabhi pareshan nahi hua?"},

{"themes":["uncertainty"],"type":"spiritual","depth":3,"emotions":["existential","dread","anxiety"],"concepts":["surrender","witness-self","impermanence","equanimity"],
"en":"What if the deepest stability available to you is not found by resolving the uncertainty — but by discovering what in you remains unchanged through all of it?",
"hi":"क्या हो यदि आपके लिए उपलब्ध सबसे गहरी स्थिरता अनिश्चितता को हल करके नहीं मिलती — बल्कि यह खोजकर कि आपमें क्या है जो इन सब के दौरान अपरिवर्तित रहता है?",
"hinglish":"Kya ho agar aapke liye uplabdh sabse gehri sthirata anishchitata ko hal karke nahi milti — balki yeh khojakar ki aap mein kya hai jo in sab ke dauran aparivartit rehta hai?"},

{"themes":["uncertainty"],"type":"spiritual","depth":3,"emotions":["existential","longing","dread"],"concepts":["surrender","witness-self","ego","impermanence"],
"en":"If you knew with certainty that you would be held through whatever happens — not protected from it, but held — what would you do differently right now?",
"hi":"यदि आप निश्चित रूप से जानते कि जो भी हो उसके दौरान आप थामे जाएंगे — उससे बचाए नहीं, बल्कि थामे — तो अभी आप क्या अलग करेंगे?",
"hinglish":"Agar aap nishchit roop se jaante ki jo bhi ho uske dauran aap thame jaayenge — us se bachaye nahi, balki thame — toh abhi aap kya alag karenge?"},
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
    print(f"Batch 6 done: inserted={inserted} skipped={skipped}")

if __name__ == "__main__":
    main()
