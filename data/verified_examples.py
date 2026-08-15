"""
Every problem+solution pair verified so far in the pilot: independently solved
and checked against a real answer key (Matematika), verified by direct reasoning
(Informatika), or verified against a licensed source with our own re-derivation
(Fizika). This is the single source of truth for fine-tuning data -- add new
verified items here as the pipeline produces more.

Fields:
  subject, grade, difficulty (0.9/1.5/2.6 tier), format (mcq/open),
  problem, choices (mcq only), correct_index (mcq only, 0-based),
  answer (open only), solution, topic (free text, used to build the
  synthetic training prompt), has_diagram (bool), diagram_note (optional)
"""

VERIFIED_EXAMPLES = [
    # ---- Matematika, real exam problems (verified against answer key) ----
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "algebra",
        "problem": "a\\cdot x+5=a-2x tenglama yechimga ega bo'lmasligi uchun a ning qiymatini toping.",
        "choices": ["-2", "2", "5", "0"], "correct_index": 0,
        "solution": "ax+2x=a-5 \\Rightarrow x(a+2)=a-5. Tenglama yechimga ega bo'lmasligi uchun a+2=0 va a-5\\neq0. Demak a=-2.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "percentages",
        "problem": "Birinchi kitob ikkinchisidan 75% arzon. Ikkinchi kitob birinchisidan necha foiz qimmat?",
        "choices": ["75%", "150%", "300%", "25%"], "correct_index": 2,
        "solution": "1-kitob = 0.25 x 2-kitob. Farq: (2-kitob-1-kitob)/1-kitob x 100 = 0.75/0.25 x 100 = 300%.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "open",
        "topic": "word problem, rate",
        "problem": "Birinchi idishda 30 L, ikkinchisida 40 L sut bor edi. Ikkinchi idishdan birinchisiga qaraganda 2 marta ko'p sut olingach, birinchi idishda ikkinchisiga qaraganda 5 L ko'p sut qoldi. Birinchi idishdan necha litr sut olingan?",
        "answer": "15",
        "solution": "x - 1-idishdan olingan miqdor. (30-x)-(40-2x)=5 => x-10=5 => x=15.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "algebra simplification",
        "problem": "Soddalashtiring: a-(a-2b+c)+2c-(b-a)",
        "choices": ["a-b+c", "2a+b+c", "a+b+c", "b+c"], "correct_index": 2,
        "solution": "a-(a-2b+c)+2c-(b-a) = a-a+2b-c+2c-b+a = a+b+c.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "number theory, divisors",
        "problem": "500 dan kichik, aynan 15 ta natural bo'luvchiga ega bo'lgan natural sonlar sonini toping.",
        "choices": ["3", "2", "4", "5"], "correct_index": 0,
        "solution": "15=3x5 bo'lganda n=p^2 q^4 yoki p^4 q^2 ko'rinishida. 500 dan kichik bo'lganlar: 144=2^4*3^2, 400=2^4*5^2, 324=3^4*2^2. Jami 3 ta.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "algebraic identity, exponents",
        "problem": "Hisoblang: (2041^3 - 2025^3 - 16^3) / (2041 . 2025)",
        "choices": ["32", "48", "56", "2026"], "correct_index": 1,
        "solution": "2041=2025+16. a^3-b^3-c^3=3bc(b+c) qachonki a=b+c. Surat=3*2025*16*2041. 2041*2025 ga bo'lsak: 3*16=48.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "algebraic identity",
        "problem": "Hisoblang: 2023 . 2025 - 2021 . 2027",
        "choices": ["4", "6", "8", "12"], "correct_index": 2,
        "solution": "a=2024. 2023*2025=a^2-1. 2021*2027=a^2-9. Ayirma: (a^2-1)-(a^2-9)=8.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "open",
        "topic": "system of equations",
        "problem": "Agar x va y sonlari x+2y=10 va 2x-y=5 tenglamalar sistemasining yechimi bo'lsa, x^2-y^2 ifodaning qiymatini toping.",
        "answer": "7",
        "solution": "4x-2y=10 ni 1-tenglamaga qo'shsak 5x=20 => x=4, y=3. x^2-y^2=16-9=7.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "algebraic identity, substitution",
        "problem": "x=12 bo'lganda, (x-2)(x^2+2x+4)-x(x-3)(x+3) ifodaning qiymatini hisoblang.",
        "choices": ["-16", "100", "108", "116"], "correct_index": 1,
        "solution": "(x-2)(x^2+2x+4)=x^3-8. x(x-3)(x+3)=x^3-9x. Ayirma: 9x-8. x=12: 108-8=100.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "mcq",
        "topic": "geometry, clock angles",
        "problem": "Soat 20:26 bo'lganda, soat mili va minut mili orasidagi kichik burchakni toping.",
        "choices": ["97°", "87°", "103°", "113°"], "correct_index": 0,
        "solution": "Minut mili: 26*6=156°. Soat mili: 8*30+(26/60)*30=253°. Farq: |253-156|=97°.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "mcq",
        "topic": "floor function equation",
        "problem": "x + [x] = 2026,5 tenglamaning barcha haqiqiy ildizlari yig'indisini toping. ([x] - x sonidan oshmaydigan eng katta butun son)",
        "choices": ["1013,5", "2027", "2026", "1013,25"], "correct_index": 0,
        "solution": "x=n+f, 2n+f=2026.5 => n=1013, f=0.5 => x=1013.5 (yagona ildiz).",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "open",
        "topic": "digit sum, large numbers",
        "problem": "(10^20-20).26 sonining raqamlari yig'indisini toping.",
        "answer": "172",
        "solution": "(10^20-20)*26 = 2599999999999999999480 (17 ta 9, boshida 25, oxirida 480). Raqamlar yig'indisi: 2+5+17*9+4+8+0=172.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "mcq",
        "topic": "word problem, rates",
        "problem": "Ikki qishloq orasidagi masofa 9 km. Yo'lning bir qismi qiyalik, bir qismi tekislik. Piyoda qiyalikdan yuqoriga 4 km/soat, tekislikda 5 km/soat, qiyalikdan pastga 6 km/soat tezlikda yuradi. Borish-kelishga 3 soat 41 minut sarflagan bo'lsa, tekislik qismi necha km?",
        "choices": ["4", "3", "5", "6"], "correct_index": 0,
        "solution": "s(qiyalik)+f(tekislik)=9. Vaqt: s(1/4+1/6)+f(2/5)=221/60. s=9-f qo'yib yechsak f=4 km.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "mcq",
        "topic": "geometry, angle bisectors",
        "problem": "Quyidagi chizmada ko'rsatilganidek, ABC uchburchakning CD va BE bissektrissalari F nuqtada kesishadi. Agar CAB burchak=3x va EFD burchak=5x+20° bo'lsa, CAB burchakni toping.",
        "choices": ["20°", "60°", "50°", "40°"], "correct_index": 1,
        "solution": "F - ichki markaz, BFC=90+A/2. EFD BFC ga vertikal: 5x+20=90+1.5x => x=20 => CAB=60°.",
        "has_diagram": True,
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "2.6", "format": "mcq",
        "topic": "number theory, digit counting",
        "problem": "a.b + b.c + c.a = 24 shartni qanoatlantiradigan barcha uch xonali (abc) sonlar sonini toping.",
        "choices": ["14", "20", "10", "18"], "correct_index": 0,
        "solution": "a=1..9, b,c=0..9 bo'yicha sanab chiqilganda 14 ta yechim topiladi.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "2.6", "format": "mcq",
        "topic": "algebra, optimization",
        "problem": "a,b,c natural sonlar. (a+b)(a^2-ab+b^2)-b^3-a(4c+a^2)+(b+c)^2-c(c+2b) ifodaning qiymati 2026 dan katta yoki teng bo'ladigan eng kichik qiymatini toping.",
        "choices": ["2028", "2026", "2027", "2116"], "correct_index": 0,
        "solution": "Ifoda b^2-4ac ga soddalashadi. b=45 da maksimal qiymat 2021 (yetarli emas). b=46: 2116-4ac, ac<=22 bo'lganda eng kichik qiymat 2116-88=2028.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "2.6", "format": "mcq",
        "topic": "number theory, divisibility",
        "problem": "(k^2+3k+6)^2/(k+1) ifoda butun son bo'ladigan barcha butun k larning yig'indisini toping.",
        "choices": ["-10", "0", "10", "-16"], "correct_index": 0,
        "solution": "n=k+1 almashtirsak, ifoda butun bo'lishi uchun n 16 ning bo'luvchisi bo'lishi kerak. k=n-1 larning yig'indisi: -10.",
    },
    # ---- Matematika, AI-generated & independently solve-checked ----
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "algebraic identity, exponents",
        "problem": "Hisoblang: (5^2024 - 5^2022) / (5^2023 + 5^2022)",
        "choices": ["4", "5", "20", "24"], "correct_index": 0,
        "solution": "Suratda: 5^2024-5^2022=5^2022(5^2-1)=5^2022*24. Maxrajda: 5^2023+5^2022=5^2022*6. Natija: 24/6=4.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "open",
        "topic": "algebraic identity, cubes",
        "problem": "Agar a+b=6 va a.b=7 bo'lsa, a^3+b^3 ifodaning qiymatini toping.",
        "answer": "90",
        "solution": "a^3+b^3=(a+b)^3-3ab(a+b)=6^3-3*7*6=216-126=90.",
    },
    {
        "subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "open",
        "topic": "geometry, angle bisectors (synthetic diagram)",
        "problem": "Xuddi shunday uchburchakda (CD va BE bissektrissalari F nuqtada kesishadi), agar CAB burchak=4x va EFD burchak=5x+30° bo'lsa, CAB burchakni toping.",
        "answer": "80",
        "solution": "EFD=BFC=90+A/2. 5x+30=90+2x => 3x=60 => x=20 => CAB=4x=80°.",
        "has_diagram": True,
    },
    # ---- Informatika, verified by direct reasoning ----
    {
        "subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "color encoding",
        "problem": "Dasturchi ranglarni kodlashda HEX (16-lik) tizimidan foydalanmoqda. Qizil rang #FF0000 kodi bilan berilgan. Agar u yashil rangni maksimal darajada (255) va qolganlarini 0 qilsa, HEX kodi qanday bo'ladi?",
        "choices": ["#00FF00", "#0025500", "#GG0000", "#FFFF00"], "correct_index": 0,
        "solution": "HEX format #RRGGBB. R=0, G=FF (maksimal), B=0. Natija: #00FF00.",
    },
    {
        "subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "logic gates",
        "problem": "Sxemada ikkita kirish bor: A va B. Chiroq yonishi uchun A ham, B ham tok o'tkazishi kerak. Bu qaysi mantiqiy element?",
        "choices": ["OR", "NOT", "XOR", "AND"], "correct_index": 3,
        "solution": "Ikkala kirish ham TRUE bo'lgandagina natija TRUE bo'ladi - bu AND elementi.",
    },
    {
        "subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "mcq",
        "topic": "pseudocode, loops",
        "problem": "Scratch dasturlash tili:\n\nJON = 10\nrepeat until <JON = 0>\n  say [Salom]\nend\n\nBu dastur necha marta \"Salom\" deydi?",
        "choices": ["10 marta", "1 marta", "0 marta", "Cheksiz (Infinite loop)"], "correct_index": 3,
        "solution": "Tsikl ichida JON hech qachon o'zgartirilmaydi, shuning uchun u hech qachon 0 ga teng bo'lmaydi - cheksiz tsikl.",
    },
    # ---- Fizika, from licensed source, independently re-derived ----
    {
        "subject": "Fizika", "grade": 10, "difficulty": "1.5", "format": "open",
        "topic": "kinematics, projectile with drag",
        "problem": "Yer sirti yaqinidagi biror balandlikdagi A nuqtadan sharcha gorizontal ravishda v0 boshlang'ich tezlik bilan otildi. Sharcha boshlang'ich tezligiga qarshi yo'nalishda a=9 m/s^2 o'zgarmas tezlanish bilan shamol esmoqda. Agar sharcha vertikal pastdagi B nuqtaga kelgan bo'lsa, v0 ni toping (m/s). AB=20 m, g=10 m/s^2.",
        "answer": "9",
        "solution": "Vertikal: AB=g t^2/2, t=sqrt(2*20/10)=2s. Gorizontal siljish nolga teng (B, A dan vertikal pastda): 0=v0*t-a*t^2/2 => v0=a*t/2=9*2/2=9 m/s.",
        "has_diagram": True,
    },
    {
        "subject": "Fizika", "grade": 11, "difficulty": "2.6", "format": "open",
        "topic": "surface tension, capillary action",
        "problem": "Radiuslari r va 3r bo'lgan kapillyar naychalar bir markazdan (ichma-ich) joylashtirilgan bo'lib, pastki uchlari vertikal holatda suvga botirildi. Naychalar orasidagi suvning ko'tarilish balandligini toping. sigma - suvning sirt tarangligi koeffitsiyenti, rho - suvning zichligi, g - erkin tushish tezlanishi.",
        "answer": "h = sigma / (rho * g * r)  [SYMBOLIC ANSWER -- flag for human review, not auto-gradable with numeric/string match]",
        "solution": "Ikkala naycha yuzasida sirt taranglik kuchlari ta'sir qiladi: F1=sigma*2*pi*r, F2=sigma*2*pi*3r, jami F=8*pi*sigma*r. Ko'tarilgan suyuqlik massasi m=rho*(V2-V1), V1=pi*r^2*h, V2=9*pi*r^2*h, V2-V1=8*pi*r^2*h. F=mg dan: h=sigma/(rho*g*r).",
    },
]
