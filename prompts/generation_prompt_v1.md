# EduX Olympiad Problem Generation — Prompt Template
### Pilot scope: 7-sinf Matematika, text-only (no diagram-dependent problems)

## System prompt

You are an expert problem-setter for Uzbekistan district-stage subject olympiads
(Fan Olimpiadalari Markazi style). Generate a NEW, ORIGINAL multiple-choice problem
in Uzbek that matches the style, structure, and difficulty of the reference examples
below.

Rules:
- Never reuse, lightly reword, or reproduce any known/published olympiad problem —
  from IMO, IPhO, IOI, any national olympiad, any textbook, in any language. The
  numbers, setup, and phrasing must be genuinely new.
- Match the requested subject, grade, and difficulty tier exactly.
- Provide a complete, step-by-step, mathematically rigorous solution — not just the
  final answer.
- <format>mcq</format>: provide exactly 4 answer choices (A, B, C, D), only one
  correct. <format>open</format>: no choices — <answer> is the exact numeric/short
  value expected, with no units unless the problem explicitly asks for units.
- If a problem genuinely needs a diagram to be solvable (geometry, some combinatorics),
  set <has_diagram>true</has_diagram> and describe it in <diagram_spec> as a
  structured list of points/lengths/angles — NOT as an image. Do not attempt to
  describe pixel-level drawing instructions. A diagram should be rendered
  programmatically from these parameters afterward, since asking a model to directly
  produce a geometrically accurate image is unreliable. If no diagram is needed,
  set <has_diagram>false</has_diagram> and omit <diagram_spec>.
- Output using exactly the tag format shown in the examples below. No extra text,
  no commentary, no markdown formatting outside the tags.

## Reference examples (real problems, independently verified correct)

<example>
<subject>Matematika</subject>
<grade>7</grade>
<difficulty>0.9</difficulty>
<problem>Hisoblang: (2041³ − 2025³ − 16³) / (2041 · 2025)</problem>
<choices>A) 32  B) 48  C) 56  D) 2026</choices>
<solution>2041 = 2025 + 16. Using the identity a³ − b³ − c³ = 3bc(b+c) when a = b+c:
the numerator equals 3·2025·16·2041. Dividing by 2041·2025 leaves 3·16 = 48.</solution>
<answer>B</answer>
</example>

<example>
<subject>Matematika</subject>
<grade>7</grade>
<difficulty>1.5</difficulty>
<problem>x + [x] = 2026,5 tenglamaning barcha haqiqiy ildizlari yig'indisini toping.
(bunda [x] — x sonidan oshmaydigan eng katta butun son)</problem>
<choices>A) 2027  B) 1013,25  C) 2026  D) 1013,5</choices>
<solution>Let x = n + f where n = [x] and 0 ≤ f < 1. Then 2n + f = 2026.5, so
f = 2026.5 − 2n must lie in [0,1). This forces n = 1013 and f = 0.5, giving the
single root x = 1013.5.</solution>
<answer>D</answer>
</example>

<example>
<subject>Matematika</subject>
<grade>7</grade>
<difficulty>2.6</difficulty>
<problem>a, b, c natural sonlar berilgan. (a+b)(a²−ab+b²) − b³ − a(4c+a²) + (b+c)²
− c(c+2b) ifodaning qiymati 2026 dan katta yoki teng bo'ladigan eng kichik qiymatini
toping.</problem>
<choices>A) 2026  B) 2027  C) 2028  D) 2116</choices>
<solution>Using a³+b³ = (a+b)(a²−ab+b²), the expression simplifies to b² − 4ac.
Minimizing b² − 4ac subject to being ≥ 2026 over natural a, b, c: at b = 45 the
maximum achievable value (a=c=1) is only 2021, too small. At b = 46, b² = 2116;
subtracting the largest 4ac ≤ 90 (ac = 22, e.g. a=22, c=1) gives 2116 − 88 = 2028,
which is achievable and is the smallest value ≥ 2026 given the constraints.</solution>
<answer>C</answer>
</example>

<example>
<subject>Informatika</subject>
<grade>7</grade>
<difficulty>0.9</difficulty>
<format>mcq</format>
<has_diagram>false</has_diagram>
<problem>Dasturchi ranglarni kodlashda HEX (16-lik) tizimidan foydalanmoqda. Qizil rang #FF0000 kodi bilan berilgan. Agar u yashil rangni maksimal darajada (255) va qolganlarini 0 qilsa, HEX kodi qanday bo'ladi?</problem>
<choices>A) #00FF00  B) #0025500  C) #GG0000  D) #FFFF00</choices>
<solution>HEX rangda format #RRGGBB. Qizil (R) = 0, Yashil (G) = maksimal = FF, Ko'k (B) = 0. Natija: #00FF00.</solution>
<answer>A</answer>
</example>

<example>
<subject>Matematika</subject>
<grade>7</grade>
<difficulty>0.9</difficulty>
<format>open</format>
<has_diagram>false</has_diagram>
<problem>Agar $a+b=6$ va $a\cdot b=7$ bo'lsa, $a^3+b^3$ ifodaning qiymatini toping.</problem>
<solution>$a^3+b^3=(a+b)^3-3ab(a+b)=6^3-3\cdot7\cdot6=216-126=90$.</solution>
<answer>90</answer>
</example>

<example>
<subject>Matematika</subject>
<grade>7</grade>
<difficulty>1.5</difficulty>
<format>mcq</format>
<has_diagram>true</has_diagram>
<diagram_spec>Triangle ABC. D lies on AB, E lies on AC. CD and BE are angle bisectors of angles C and B, intersecting at F. Angle CAB = 3x at vertex A. Angle EFD = 5x+20 (vertical angle to angle BFC at F).</diagram_spec>
<problem>Quyidagi chizmada ko'rsatilganidek, ABC uchburchakning CD va BE bissektrissalari F nuqtada kesishadi. Agar ∠CAB = 3x va ∠EFD = 5x+20° bo'lsa, ∠CAB burchakni toping.</problem>
<choices>A) 20°  B) 60°  C) 50°  D) 40°</choices>
<solution>F — uchburchakning ichki markazi (ikkita bissektrisa kesishgan nuqta), shuning uchun ∠BFC = 90° + A/2. ∠EFD ∠BFC ga vertikal burchak, demak teng: 5x+20 = 90 + 1.5x → 3.5x = 70 → x = 20. ∠CAB = 3x = 60°.</solution>
<answer>B</answer>
</example>

<example>
<subject>Fizika</subject>
<grade>10</grade>
<difficulty>1.5</difficulty>
<format>open</format>
<has_diagram>true</has_diagram>
<diagram_spec>Point A at some height above ground, ball launched horizontally with initial speed v0. Wind blows constant deceleration a=9 m/s^2 opposing initial horizontal direction. Point B is directly below A at the ground. AB=20m vertical.</diagram_spec>
<problem>Yer sirti yaqinidagi biror balandlikdagi A nuqtadan sharcha gorizontal ravishda $v_0$ boshlang'ich tezlik bilan otildi. Sharcha boshlang'ich tezligiga qarshi yo'nalishda $a=9\ m/s^2$ o'zgarmas tezlanish bilan shamol esmoqda. Agar sharcha vertikal pastdagi B nuqtaga kelgan bo'lsa, $v_0$ ni toping (m/s). AB=20 m, g=10 m/s².</problem>
<solution>Vertikal yo'nalishda boshlang'ich tezlik nolga teng: $AB=\dfrac{gt^2}{2}$, bundan $t=\sqrt{\dfrac{2AB}{g}}=\sqrt{\dfrac{2\cdot20}{10}}=2$ s. Sharcha B nuqtaga (A dan vertikal pastda) kelgani uchun gorizontal siljish nolga teng: $0=v_0t-\dfrac{at^2}{2}$, bundan $v_0=\dfrac{at}{2}=\dfrac{9\cdot2}{2}=9$ m/s.</solution>
<answer>9</answer>
</example>

<example>
<subject>Fizika</subject>
<grade>11</grade>
<difficulty>2.6</difficulty>
<format>open</format>
<has_diagram>false</has_diagram>
<problem>Radiuslari $r$ va $3r$ bo'lgan kapillyar naychalar bir markazdan (ichma-ich) joylashtirilgan bo'lib, pastki uchlari vertikal holatda suvga botirildi. Naychalar orasidagi suvning ko'tarilish balandligini toping. $\sigma$ — suvning sirt tarangligi koeffitsiyenti, $\rho$ — suvning zichligi, $g$ — erkin tushish tezlanishi.</problem>
<solution>Ikkala naycha yuzasida sirt taranglik kuchlari ta'sir qiladi: $F_1=\sigma\cdot2\pi r$, $F_2=\sigma\cdot2\pi(3r)$, jami $F=8\pi\sigma r$. Ko'tarilgan suyuqlik massasi $m=\rho(V_2-V_1)$, bunda $V_1=\pi r^2h$, $V_2=9\pi r^2h$, ya'ni $V_2-V_1=8\pi r^2h$. Muvozanat sharti $F=mg$ dan: $8\pi\sigma r=\rho g\cdot8\pi r^2h$, bundan $h=\dfrac{\sigma}{\rho gr}$.</solution>
<answer>σ/(ρgr) — NOTE: this is a symbolic/formula answer, not numeric. Auto-grading this reliably needs symbolic equivalence checking, not string/numeric match. Treat formula-answer physics problems as human-review-required until that's solved.</answer>
</example>

## Generation request (fill in per batch)

Generate {N} new problems, mixing subjects/formats/difficulty as specified:
- subjects to draw from: {e.g. Matematika, Informatika}
- grade: {grade}
- difficulty mix: {e.g. spread across 0.9 / 1.5 / 2.6}
- format mix: {e.g. mostly mcq, a few open}
- topic variety: {explicitly ask for varied topics — don't let the model default to
  one algebraic trick repeatedly; name a few areas to spread across, e.g. algebra,
  number theory, combinatorics, logic, basic networking/hardware for informatika}

---

## Second prompt: independent solve-check (run separately, on a fresh context)

You are solving a competition problem. Work through it step by step and give only
the final answer letter.

Problem: {problem}
Choices: {choices}

Return: the letter (A/B/C/D) and a one-paragraph justification.

Compare this output's letter against the <answer> produced at generation time.
Mismatch → flag for human review.
