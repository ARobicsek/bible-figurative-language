# Proverbs 3:11-18 Comparison: MEDIUM vs HIGH Reasoning

## Test Summary

| Metric | MEDIUM Reasoning | HIGH Reasoning |
|--------|------------------|----------------|
| Total Instances | 14 | 13 |
| Detection Rate | 1.75 per verse | 1.62 per verse |
| Total Cost | $1.24 | $2.15 |
| Cost per Verse | $0.15 | $0.27 |
| Total Time | 4.1 min | 6.5 min |
| Time per Verse | 30.6s | 48.4s |

## Verse-by-Verse Analysis

### Proverbs 3:11

**Text**: Do not reject the discipline of the LORD, my son; Do not abhor His rebuke.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 1 | $0.0269 | 24.1s | N/A | N/A |
| HIGH | 0 | $0.0453 | 39.4s | N/A | N/A |

#### MEDIUM Reasoning Detected (1 instances):

1. **my son** (Metaphor)
- Confidence: 0.85
- Explanation: The speaker addresses the generic disciple as 'my son', using familial language metaphorically to frame the teacher–student relationship as a parent–child relationship characterized by affection, authority, and obligation to heed instruction.

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- **מוּסַר יְהוָה ("the discipline of the LORD")**  
  - Considered whether "discipline" functions metaphorically for *suffering/hardship as a teacher* or as personified force.  
  - In Proverbs, *מוּסָר* is a standard abstract for corrective instruction (parental or divine). No concrete image (like path, tree, house) is invoked here, and the phrase can be read straightforwardly as God's corrective instruction through teaching and circumstances.  
  - Conclusion: treat as **conceptual/theological, not metaphorical** in this verse.

- **בְּנִי ("my son")**  
  - This is a key wisdom-literature formula. In context, the speaker is a sage/teacher addressing a generic disciple or student, not necessarily his literal biological son.  
  - The term "son" thus extends beyond literal genealogy to describe a **disciple as if he were a son**, implying filial loyalty, teachability, and familial affection.  
  - This is a conventional **kinship metaphor** (teacher as father, disciple as son), used to frame instruction.  
  - Conclusion: **figurative (metaphor)**; will be included in JSON.

- **אַל־תִּמְאָס ("do not despise/reject") & וְאַל־תָּקֹץ ("do not abhor/be weary of")**  
  - Both are normal emotional/volitional verbs applied to "discipline" and "rebuke." No non-literal vehicle image (e.g., weight, poison, etc.) is introduced.  
  - Conclusion: **literal emotional language**, no distinct metaphor/idiom here.

- **בְּתוֹכַחְתּוֹ ("in/with his rebuke")**  
  - Considered whether the preposition בְּ ("in/with") might create a metaphorical spatial image of being "inside" God's rebuke.  
  - In Biblical Hebrew this is a standard preposition marking association/instrument ("with/by means of his rebuke"). No clearly extended spatial or personifying imagery.  
  - *תּוֹכַחַת* itself is an abstract noun for verbal correction/reproof; in this context it can be taken straightforwardly.  
  - Conclusion: **no clear figurative usage** beyond normal abstract noun usage.

- **Divine action implied (God “disciplines” and “rebukes”)**  
  - Considered whether this should be treated as anthropomorphism or personification of divine activity.  
  - In ANE and biblical theology, God’s corrective actions are literally conceived; the text does not depict a body part or non-human agent functioning as a person.  
  - Conclusion: within the user’s guidelines, this is **not to be tagged as figurative**.

Only **"my son" / בְּנִי** is treated as figurative (kinship metaphor for disciple).

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "בְּנִ֣י",
    "english_text": "my son",
    "explanation": "The speaker addresses the generic disciple as 'my son', using familial language metaphorically to frame the teacher–student relationship as a parent–child relationship characterized by affection, authority, and obligation to heed instruction.",
    "target": [
      "disciple addressed as 'my son'",
      "student or moral learner",
      "human person"
    ],
    "vehicle": [
      "beloved son in a family",
      "offspring, child in a parent–child relationship",
      "human family member"
    ],
    "ground": [
      "filial relationship of dependence and obedience",
      "close, affectionate instructional bond",
      "social-moral relationship"
    ],
    "posture": [
      "affectionate exhortation",
      "parental instruction",
      "positive, caring stance"
    ],
    "confidence": 0.85,
    "speaker": "wise teacher/father-figure in Proverbs",
    "purpose": "To strengthen the authority and warmth of the exhortation by casting the addressee as a son under loving parental discipline."
  }
]
```
```

#### HIGH Reasoning Detected (0 instances):

*No instances detected*

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:

1. **מוּסַר יְהוָה – “the discipline of the LORD”**
   - Considered whether “discipline” (מוּסָר) here is:
     - a **metaphor** for general suffering or hardships;
     - a **metonymy** where “discipline” stands for concrete calamities God sends.
   - In Proverbs, מוּסָר regularly denotes **instruction/correction/chastening**, both parental and divine, as a real pedagogical process (e.g., 1:8; 4:1, 13).
   - Here, within the wisdom-education frame of chs. 1–9, “discipline of YHWH” is best taken as **literal divine correction/instruction**, whether via words or life events, not as an image borrowed from another domain.
   - So I did **not** mark this as metaphor or metonymy.

2. **בְּנִי – “my son”**
   - Considered whether this is:
     - a **metaphorical** kinship term for “disciple/student” rather than a literal son.
   - In wisdom literature, “my son” is a stereotyped form of **pedagogical address**. It can be broader than biological son, but it still uses the normal kinship term in line with the social reality that teachers often are fathers or father‑figures.
   - Instructions said to be **conservative with genealogical language**, so I treat “my son” as a conventional but **not figurative** address, not a deliberate metaphor to be tagged.

3. **אַל־תִּמְאָס – “do not despise / reject”**
   - Considered whether the strong verb “despise” is:
     - **hyperbolic** (exaggeration) for mild dislike;
     - an **idiom** meaning “do not ignore / do not neglect.”
   - The verb מָאַס regularly and literally means “reject, despise, treat as worthless” in Hebrew. Nothing in this context forces it into figurative exaggeration; it describes a real inner evaluative stance.
   - So I did **not** treat it as hyperbole or idiom.

4. **וְאַל־תָּקֹץ – “and do not abhor / be weary of”**
   - Considered:
     - Is קוּץ with בְּ + object an **idiom** or a **metaphor** (“be short / bristling” → “be disgusted”)?
   - In Biblical Hebrew, קוּץ with בְּ commonly means “to be disgusted with / loathe / be impatient of” (e.g., Lev 26:15), and that sense is lexically stable.
   - While historically it may derive from a physical image (“become short” etc.), at the level of usage in Proverbs 3:11 it functions as a **standard emotional verb**, not as a live figure.
   - I therefore did **not** mark this as figurative or idiomatic beyond normal lexical meaning.

5. **בְּתוֹכַחְתּוֹ – “at / because of His rebuke”**
   - Considered:
     - **Personification**: is “rebuke” pictured as some concrete entity?
     - **Metonymy**: “rebuke” as a label for the concrete consequences God sends.
   - תּוֹכַחַת is the regular term for **reproof, correction, argument**, whether human or divine. Here it is the counterpart to לֹא־תִמְאָס מוּסַר: the content or act of God’s corrective address.
   - The text depicts God truly rebuking; in ANE terms, that is a **literal divine action**, not personification of an object or process.
   - Any link to outward circumstances is part of the normal semantic range of “rebuke” in religious discourse, not a marked figure.
   - So I did **not** classify this as figurative.

6. **Poetic Parallelism in the verse**
   - Structure:
     - Colon A: “Do not despise the discipline of YHWH, my son”
     - Colon B: “and do not abhor His rebuke.”
   - Considered whether the parallelism itself entails a **metaphorical pairing** (e.g., discipline // rebuke as images).
   - The parallelism is **semantic reinforcement**: two near‑synonymous terms for divine correction, and two near‑synonymous verbs of rejection. This is standard Hebrew poetic parallelism, not figurative imagery.
   - Thus, I treated the verse as **poetic but not figurative** in the technical sense requested.

7. **Context with v. 12 (father–son simile)**
   - v. 12 explicitly introduces a simile: “For whom the LORD loves He reproves, **as a father** the son in whom he delights.”
   - Considered whether that father imagery retroactively makes “discipline of YHWH” in v. 11 part of a **God‑as‑father metaphor** in this verse.
   - However, v. 11 itself contains no explicit kinship or father term for God; it simply names “the discipline of YHWH” and “His rebuke.”
   - Following the instruction to analyze **only this verse**, I did not project the simile of v. 12 into the tagging of v. 11. The father imagery is textually signaled only in the next verse.

**Conclusion:**  
All examined elements in Proverbs 3:11 can be adequately explained as **literal moral-religious language in poetic parallelism**, without clear, marked metaphor, simile, personification, idiom, hyperbole, or metonymy that fits the tagging criteria.

Therefore, no figurative language is tagged for this verse.

```json
[]
```
```

---

### Proverbs 3:12

**Text**: For whom the LORD loves, He rebukes, As a father the son whom he favors.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 1 | $0.0552 | 15.1s | N/A | N/A |
| HIGH | 1 | $0.0890 | 23.2s | N/A | N/A |

#### MEDIUM Reasoning Detected (1 instances):

1. **As a father [reproves] the son whom he favors** (Simile)
- Confidence: 0.95
- Explanation: The verse compares the LORD’s loving reproof of those He loves to the way a human father deals with a son in whom he delights. This is an explicit simile, using the familiar parent-child relationship as the vehicle to explain the nature of divine discipline.

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
I examined each component of the verse:

Hebrew: כִּ֤י אֶ֥ת־אֲשֶׁ֣ר יֶאֱהַ֣ב יְהֹוָ֣ה יוֹכִ֑יחַ  
וּ֝כְאָ֗ב אֶת־בֵּ֥ן יִרְצֶֽה  

English: For whom the LORD loves, He rebukes,  
As a father the son whom he favors.

1. **"אֲשֶׁ֣ר יֶאֱהַ֣ב יְהוָ֣ה" / "whom the LORD loves"**  
   - Considered whether "love" here is figurative (e.g., covenantal favor as a metonymy for blessing) or anthropomorphic in a figurative way.  
   - In wisdom and covenant contexts, divine love is a standard way to describe God's genuine relational stance, not a conventional metaphor in itself. It is abstract but not figurative in the technical sense required here.  
   - Conclusion: treated as literal relational language, not metaphor/metonymy.

2. **"יוֹכִ֑יחַ" / "He rebukes"**  
   - Considered whether "rebuke" could be a *metaphor* for sending hardship or suffering. In Proverbs, "reproof" and "discipline" can cover verbal correction, consequences, and providential shaping, but the lexeme itself denotes correction/reproof straightforwardly.  
   - The possible extension to suffering is more theological inference than explicit figurative use here.  
   - Conclusion: no clear metaphor/idiom detected in the word itself.

3. **"וּכְאָב אֶת־בֵּן יִרְצֶה" / "As a father the son whom he favors"**  
   - The prefixed כ־ (“as/like”) introduces an explicit **simile**. I considered:
     - Is this merely illustrative or is it a genuine figurative mapping?  
     - It clearly draws a comparison between God’s action toward those he loves (target) and a human father’s treatment of a favored son (vehicle).  
   - The point (ground) is that **reproof arising from delight/love** is analogous in both relationships.  
   - This is not personification: God is not called “father” here; rather, a human father is the *vehicle* in a simile.  
   - Also weighed whether to treat this as a deeper **metaphor of God as father**; in this particular verse, the syntax keeps it at the level of simile (God acts *like* a father), so I marked simile "yes" and metaphor "no" for this phrase.  
   - Conclusion: this colon is clearly **figurative** as a simile.

4. **Any other idiomatic/hyperbolic elements?**  
   - “Son whom he favors/delights in” (בֵּן יִרְצֶה) could be idiomatic for “beloved/accepted son,” but it functions straightforwardly as “the son in whom he delights,” fitting the comparison. No obvious idiom beyond standard lexical meaning.  
   - No hyperbole, no nature/body/path metaphors in this verse.

Thus, the **only clear figurative element** is the simile in the second colon: **God’s disciplinary love likened to a father’s treatment of a delighted-in son.**

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "yes",
    "metaphor": "no",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "וּכְאָב אֶת־בֵּן יִרְצֶה",
    "english_text": "As a father [reproves] the son whom he favors",
    "explanation": "The verse compares the LORD’s loving reproof of those He loves to the way a human father deals with a son in whom he delights. This is an explicit simile, using the familiar parent-child relationship as the vehicle to explain the nature of divine discipline.",
    "target": [
      "YHWH’s corrective relationship with those He loves",
      "divine-human covenant relationship",
      "God’s relationship to people"
    ],
    "vehicle": [
      "a human father’s relationship to a favored son",
      "parent-child relationship",
      "human family relationship"
    ],
    "ground": [
      "loving discipline of one in whom one delights",
      "beneficial corrective love aimed at the child’s good",
      "moral and relational care"
    ],
    "posture": [
      "encouragement to accept loving discipline",
      "instruction and reassurance",
      "positive, pastoral stance"
    ],
    "confidence": 0.95,
    "speaker": "sage/teacher (Proverbs narrator addressing 'my son')",
    "purpose": "To persuade the hearer not to despise the LORD’s discipline by showing that it functions like a loving father’s corrective care for a favored son."
  }
]
```
```

#### HIGH Reasoning Detected (1 instances):

1. **As a father the son whom he favors.** (Simile)
- Confidence: 0.97
- Explanation: The verse explicitly compares YHWH’s corrective love to a human father’s treatment of a favored son, using a familiar family relationship as a simile to illuminate the nature of divine discipline.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- Phrase: **כִּ֤י אֶ֥ת־אֲשֶׁ֣ר יֶאֱהַ֣ב יְהֹוָ֣ה** (“for whom YHWH loves”)
  - Considered whether “love” for God is an anthropomorphism/anthropopathism functioning figuratively.
  - According to the provided guidelines, divine emotions and actions (e.g., “God was angry”) are to be treated as *literal* in the ANE context unless they involve God’s *body*. Here “love” is an emotional/relational verb, not a bodily term. I therefore treated this as straightforward, not as metaphor or personification.
- Phrase: **יוֹכִ֑יחַ** (“he rebukes / reproves”)
  - Considered whether this might be a metonymy for broader experiences of suffering or life’s hardships.
  - In the immediate context (vv. 11–12: מוּסַר יְהוָה … וְאַל־תָּקֹץ בְּתוֹכַחְתּוֹ), “rebuke/discipline” is a standard wisdom term for pedagogical correction. The verse states directly that YHWH corrects those he loves; no clear figurative transfer is required beyond normal theological language. I therefore did **not** mark this as metaphor, metonymy, or idiom.
- Phrase: **וּ֝כְאָ֗ב אֶת־בֵּ֥ן יִרְצֶֽה** (“as a father [does] the son whom he favors”)
  - The prefixed **כ־** (“like/as”) signals an explicit *comparison*, a prime marker of simile in biblical Hebrew poetry.
  - Here YHWH’s act of loving discipline (first colon) is **likened** to a human father’s treatment of a favored son (second colon). The human father–son relation is literal on the human side, but it functions as the *vehicle* for understanding God’s relation to those he loves.
  - Considered whether to treat this also as a metaphor (“God is father”), but the verse maintains the comparative form “like a father,” so I classify it primarily as **simile**, not as an independent nominal metaphor.
  - Considered whether “בֵּן יִרְצֶה” (“the son he delights in/favors”) might be an idiom for “legitimate heir” or “special-status child.” The phrase is fully compositional (son + delight/favor), so I did not mark it as idiomatic apart from its role within the simile.

Conclusion: One clear figurative element: the explicit **simile** “as a father [deals with] the son he favors,” used to explain YHWH’s loving rebuke.

```json
[
  {
    "figurative_language": "yes",
    "simile": "yes",
    "metaphor": "no",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "וּ֝כְאָ֗ב אֶת־בֵּ֥ן יִרְצֶֽה",
    "english_text": "As a father the son whom he favors.",
    "explanation": "The verse explicitly compares YHWH’s corrective love to a human father’s treatment of a favored son, using a familiar family relationship as a simile to illuminate the nature of divine discipline.",
    "target": [
      "YHWH's loving discipline of those he loves",
      "God's treatment of his faithful people",
      "divine behavior toward humans"
    ],
    "vehicle": [
      "a human father's treatment of a favored son",
      "parent–child relationship in an Israelite family",
      "human family relationships"
    ],
    "ground": [
      "discipline as an expression of favor and affection",
      "corrective care within close relationships",
      "moral formation motivated by love"
    ],
    "posture": [
      "reassuring encouragement to accept discipline",
      "instruction and pastoral reassurance",
      "positive pedagogical stance"
    ],
    "confidence": 0.97,
    "speaker": "Sapiential teacher addressing his son",
    "purpose": "To reinterpret divine rebuke as a loving, fatherly act, encouraging the listener to accept YHWH's discipline as a sign of favor."
  }
]
```
```

---

### Proverbs 3:13

**Text**: Happy is the man who finds wisdom, The man who attains understanding.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 2 | $0.0886 | 22.4s | N/A | N/A |
| HIGH | 2 | $0.1428 | 37.1s | N/A | N/A |

#### MEDIUM Reasoning Detected (2 instances):

1. **who finds wisdom** (Metaphor)
- Confidence: 0.86
- Explanation: The act of acquiring wisdom is portrayed with the verb 'find,' which in its concrete sense refers to locating or discovering a tangible object. This maps the abstract process of gaining wisdom onto the concrete experience of discovering a valuable thing, a standard metaphor in Proverbs where wisdom is treated like treasure or goods that one can find.

2. **who attains understanding** (Metaphor)
- Confidence: 0.84
- Explanation: The verb 'yafik' ('bring out, draw out, obtain') is concretely used for extracting or producing something (like resources or yield). Here it is applied to 'understanding,' an abstract quality, thus conceptualizing the gaining of understanding as drawing out or producing a valuable yield from some source (experience, teaching, reflection).

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- Phrase: **אַשְׁרֵי אָדָם / “Happy is the man”**  
  - Considered whether *אַשְׁרֵי* is an idiom or hyperbole. In Biblical Hebrew it is a conventional beatitude formula (“fortunate/blessed is…”). It expresses evaluation but does not obviously rely on imagery or non-literal wording. I treat it as conventional, not figurative for this tagging purpose.  
  - *אָדָם* here is a generic “person/man.” I considered whether this is metonymy (an individual standing for humanity), but in wisdom literature this generic masculine is the normal grammatical way to speak about “a person,” so I do **not** mark it as figurative.

- Phrase: **מָצָא חָכְמָה / “who finds wisdom”**  
  - I considered whether “find” could be taken literally (e.g., finding an already-existing entity in space). Here *חָכְמָה* is an abstract quality/skill, not a spatial object.  
  - The verb *מָצָא* (“find”) is extended from its concrete domain (locating a lost/hidden thing) to the abstract domain (acquiring wisdom). This is a standard conceptual metaphor: **ACQUIRING WISDOM IS FINDING A VALUABLE OBJECT/TREASURE.**  
  - In the immediate context (vv. 14–15) wisdom is also treated as valuable trade-goods and treasure, reinforcing the figurative acquisition imagery.  
  - I therefore mark this as **metaphor** (not simile, no explicit comparison marker).

- Phrase: **וְאָדָם יָפִיק תְּבוּנָה / “The man who attains understanding”**  
  - Verb *יָפִיק* (Hiphil of פוק) in its concrete sense is “bring out, draw out, cause to come forth” (as with something produced or extracted).  
  - Here the object is *תְּבוּנָה* (“understanding/insight”), again an abstract intellectual quality. The idea is not that understanding physically emerges, but that a person “draws out/obtains” it, likely from study, experience, or instruction.  
  - This again invokes a conceptual metaphor: **GAINING UNDERSTANDING IS EXTRACTING/PRODUCING A VALUABLE YIELD** (like drawing water from a well, ore from a mine, or produce from land).  
  - Because a concrete, productive/extractive process is mapped onto the cognitive-acquisitive realm, I mark this as **metaphor**.

- Possible personification of *חָכְמָה* / *תְּבוּנָה*:  
  - In the broader chapter, wisdom is personified (esp. vv. 15–18: “her ways,” “her paths,” “tree of life,” etc.).  
  - In v. 13 specifically, however, *חָכְמָה* and *תְּבוּנָה* are simply objects of human actions (“find,” “draw out/obtain”). They are not described as acting, speaking, or possessing bodily parts. Thus I **do not** mark personification in this verse itself.

- Whole-verse structure (beatitude):  
  - The verse as a whole is a wisdom beatitude praising the condition of the person who has attained wisdom and understanding. No additional distinct figurative structure (like path, tree, building imagery) appears in this line, so only the two acquisition verbs are tagged as figurative.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "מָצָא חׇכְמָה",
    "english_text": "who finds wisdom",
    "explanation": "The act of acquiring wisdom is portrayed with the verb 'find,' which in its concrete sense refers to locating or discovering a tangible object. This maps the abstract process of gaining wisdom onto the concrete experience of discovering a valuable thing, a standard metaphor in Proverbs where wisdom is treated like treasure or goods that one can find.",
    "target": [
      "acquisition of wisdom",
      "human learning and moral formation",
      "human cognition and character development"
    ],
    "vehicle": [
      "finding a valuable object or treasure",
      "search and discovery of concrete goods",
      "physical acquisition in the material world"
    ],
    "ground": [
      "successful discovery and secure possession after seeking",
      "effortful pursuit resulting in valuable gain",
      "beneficial outcome of a search or quest"
    ],
    "posture": [
      "commendation of those who acquire wisdom",
      "praise and encouragement of wise pursuit",
      "positive evaluative stance"
    ],
    "confidence": 0.86,
    "speaker": "sage/narrator of Proverbs",
    "purpose": "To motivate the pursuit of wisdom by picturing it as a valuable object that one can find, emphasizing its desirability and the blessed state of those who obtain it."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "יָפִיק תְּבוּנָה",
    "english_text": "who attains understanding",
    "explanation": "The verb 'yafik' ('bring out, draw out, obtain') is concretely used for extracting or producing something (like resources or yield). Here it is applied to 'understanding,' an abstract quality, thus conceptualizing the gaining of understanding as drawing out or producing a valuable yield from some source (experience, teaching, reflection).",
    "target": [
      "acquisition of understanding",
      "human learning and discernment",
      "human cognitive and evaluative processes"
    ],
    "vehicle": [
      "drawing out a resource or yield",
      "extraction or production of tangible benefit",
      "physical obtaining of material goods"
    ],
    "ground": [
      "deriving valuable results from a source through effort",
      "productive outcome that enriches the one who extracts it",
      "beneficial, fruitful gain from an underlying resource"
    ],
    "posture": [
      "approval of gaining understanding",
      "praise and encouragement of discernment",
      "positive evaluative stance"
    ],
    "confidence": 0.84,
    "speaker": "sage/narrator of Proverbs",
    "purpose": "To portray understanding as a valuable yield one can draw out, emphasizing both its worth and the active, productive effort involved in acquiring it."
  }
]
```
```

#### HIGH Reasoning Detected (2 instances):

1. **who finds wisdom** (Metaphor)
- Confidence: 0.88
- Explanation: The act of acquiring wisdom is portrayed using the verb 'find,' which in its concrete sense refers to discovering or obtaining a locatable object, often something valuable. In the context of Proverbs 3:13–15, where wisdom is compared to profitable trade and precious stones, this evokes a metaphor in which wisdom is like a valuable object or treasure that a person discovers and comes to possess.

2. **the man who attains (brings forth) understanding** (Metaphor)
- Confidence: 0.83
- Explanation: The verb 'yaphiq' (bring forth, draw out, produce) depicts understanding as something that can be brought out or caused to issue forth, like a product or yield drawn from a source. In the surrounding context, wisdom's 'trade' and 'yield' are better than silver and gold (vv. 14–15), reinforcing the metaphor of understanding as a valuable product or yield that a person produces or extracts, rather than a purely static mental state.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- **אַשְׁרֵי אָדָם / “Happy is the man”**  
  - Considered whether “אַשְׁרֵי” functions as:
    - Hyperbole (“supremely happy!”), or  
    - An idiomatic beatitude formula whose literal sense is weak or lost.  
  - In biblical Hebrew, אַשְׁרֵי regularly marks a *real* state of well-being/blessedness; it is evaluative but not necessarily exaggeration. It does not depict something *as* something else, nor does it rest on a transferred image.  
  - “אָדָם” is used here generically for “a human being,” not as “male” standing for all people; it is standard lexical usage (cf. Gen 1:27). This is not a rhetorical synecdoche but the normal generic sense, so I did **not** mark it as metonymy.  
  - Conclusion: **no figurative language** here beyond normal evaluative diction.

- **מָצָא חׇכְמָה / “who finds wisdom”**  
  - Considered whether “find” (מָצָא) is:
    - Just a conventional verb meaning “to obtain/come to possess” (literalized, dead metaphor), or  
    - Still an active conceptual metaphor portraying wisdom as something like a hidden object or treasure one “finds.”  
  - In BH, מָצָא commonly takes both concrete and abstract objects (find an object; “find favor,” “find grace,” etc.). Conceptually, it maps **acquiring an intangible quality** onto **discovering/obtaining a valuable, locatable object**.  
  - Given the immediate context (vv. 14–15 speak of trade, yield, precious stones), the verse very deliberately frames wisdom as something like valuable merchandise/treasure. That wider semantic field supports treating “find wisdom” as a **live metaphor**, not just bleached idiom.  
  - Conclusion: **Metaphor**: acquisition of wisdom is depicted in terms of finding a valuable object.

- **וְאָדָם יָפִיק תְּבוּנָה / “The man who attains (brings forth) understanding”**  
  - יָפִיק (Hiphil of הפיק) means “bring out, produce, draw out, obtain.” Considered:
    - Is this just a lexical synonym for “get/receive understanding” (literal), or  
    - Does it picture understanding as something *brought out/extracted*, like a product, yield, or resource?  
  - The verb’s core image is **bringing something out from a source**—whether a physical substance or, figuratively, a result or product. In wisdom literature this often shades into imagery of extracting something valuable from within (cf. other “drawing out” verbs used for counsel/wisdom).  
  - Coupled with v. 14’s language of “trade,” “yield” (תְּבוּאָתָהּ), and v. 15’s “precious” gem language, the clause naturally aligns with a **productive/extractive metaphor**: understanding is like a valuable yield that a person “brings out.”  
  - Borderline: one could argue that the verb has become a standard abstract-verb meaning “attain,” but the broader imagery of the passage keeps the productive metaphor alive.  
  - Conclusion: **Metaphor**: gaining/manifesting understanding is pictured as bringing out a valuable product/yield.

- **Parallelism of the two cola (“man who finds wisdom // man who brings forth understanding”)**  
  - The verse as a whole employs **synonymous parallelism**: “wisdom” ≈ “understanding,” “find” ≈ “bring forth/attain,” “man” // “man.” This is a structural poetic feature, not itself figurative language.  
  - The figurative aspect lies specifically in the verbs used for acquisition (find, bring forth), not in the parallelism per se.

- **No personification of Wisdom in v. 13 itself**  
  - Though vv. 14–18 begin to personify Wisdom as a “she,” v. 13 only mentions חָכְמָה and תְּבוּנָה as abstract qualities possessed/found/produced by a man. They are not acting as agents; thus, **no personification** yet in this verse.

Summary:  
- Marked **two** figurative expressions, both **metaphors** of acquisition:
  1. “מָצָא חׇכְמָה / finds wisdom” – wisdom as a valuable object/treasure discovered.  
  2. “יָפִיק תְּבוּנָה / brings forth (attains) understanding” – understanding as a valuable product/yield brought out.  
- No similes, personifications, idioms, hyperboles, or metonymies judged active in this verse.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "מָצָא חׇכְמָה",
    "english_text": "who finds wisdom",
    "explanation": "The act of acquiring wisdom is portrayed using the verb 'find,' which in its concrete sense refers to discovering or obtaining a locatable object, often something valuable. In the context of Proverbs 3:13–15, where wisdom is compared to profitable trade and precious stones, this evokes a metaphor in which wisdom is like a valuable object or treasure that a person discovers and comes to possess.",
    "target": [
      "acquiring wisdom (gaining wise character and insight)",
      "human pursuit of wisdom and instruction",
      "moral and spiritual life of a person"
    ],
    "vehicle": [
      "finding a valuable object or treasure",
      "acquiring precious goods or merchandise",
      "economic/physical possessions domain"
    ],
    "ground": [
      "discovering something highly valuable and desirable",
      "successful search and acquisition of a sought-after good",
      "beneficial gain leading to prosperity and well-being"
    ],
    "posture": [
      "blessing and commendation of those who seek and obtain wisdom",
      "praise of a wise, wisdom-seeking lifestyle",
      "positive evaluative stance toward the acquisition of wisdom"
    ],
    "confidence": 0.88,
    "speaker": "Parental sage/narrator addressing 'my son' in Proverbs 3",
    "purpose": "To motivate the hearer to seek wisdom by depicting it as a highly valuable treasure that can be found and possessed, thereby framing the pursuit of wisdom as a rewarding search."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "אָדָם יָפִיק תְּבוּנָה",
    "english_text": "the man who attains (brings forth) understanding",
    "explanation": "The verb 'yaphiq' (bring forth, draw out, produce) depicts understanding as something that can be brought out or caused to issue forth, like a product or yield drawn from a source. In the surrounding context, wisdom's 'trade' and 'yield' are better than silver and gold (vv. 14–15), reinforcing the metaphor of understanding as a valuable product or yield that a person produces or extracts, rather than a purely static mental state.",
    "target": [
      "manifesting and gaining understanding (discernment)",
      "human exercise and acquisition of insight",
      "inner intellectual and moral capacities"
    ],
    "vehicle": [
      "bringing out a physical substance or product",
      "producing or extracting valuable goods or yield",
      "economic/agricultural/productive activity domain"
    ],
    "ground": [
      "causing something latent to become actual and usable",
      "productive output resulting from effort and cultivation",
      "generating benefit or profit from an internal or given resource"
    ],
    "posture": [
      "blessing and approval of those who bring forth understanding",
      "commendation of a life that productively yields discernment",
      "positive evaluative stance toward the productive use of inner wisdom"
    ],
    "confidence": 0.83,
    "speaker": "Parental sage/narrator addressing 'my son' in Proverbs 3",
    "purpose": "To encourage the hearer not only to possess but to actively cultivate and 'bring out' understanding, portraying discernment as a valuable yield that results in blessedness and well-being."
  }
]
```
```

---

### Proverbs 3:14

**Text**: Her value in trade is better than silver, Her yield, greater than gold.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 2 | $0.1419 | 31.8s | N/A | N/A |
| HIGH | 2 | $0.2233 | 62.9s | N/A | N/A |

#### MEDIUM Reasoning Detected (2 instances):

1. **Her value in trade … her yield** (Metaphor)
- Confidence: 0.9
- Explanation: Wisdom’s benefits are depicted in terms of economic merchandise and agricultural yield, treating wisdom as an income-producing asset whose ‘profit’ and ‘produce’ can be compared to financial returns. This maps an abstract moral-spiritual quality (wisdom) onto the concrete domain of trade and harvest.

2. **than the trade of silver, and [better] than gold** (Metonymy)
- Confidence: 0.9
- Explanation: ‘Trade of silver’ uses the activity of trading as a stand-in for the profit gained from it, and ‘silver’ and ‘gold’ stand for material wealth and high economic value. They function as metonymic benchmarks for the best that material riches can offer, against which wisdom’s returns are measured.

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:

- כִּ֤י ט֣וֹב – “for [it is] better”: Simple evaluative comparison; no metaphor/idiom in the word itself.  
- סַ֭חְרָהּ “her trade / merchandise / profit”: Considered whether literal. Since the antecedent “her” is חָכְמָה (wisdom, v.13), an abstract quality, describing “her” as having *סחר* (merchandise/profit) maps wisdom’s benefits into the economic domain. This is not literal (you do not literally trade in “wisdom” as a commodity); it is a conceptual metaphor: wisdom’s gain is like commercial profit. Marked as metaphor.
- מִסְּחַר־כָּסֶף “than the trade of silver”:  
  - Considered if metaphor: the phrase itself stays within the economic domain; it’s a literal expression for profitable silver-trade.  
  - Considered if metonymy: “trade” (activity) standing for “profit from trade” (result) is a standard activity→result metonymy. Also “silver” here stands for the wealth obtainable from it, a common precious-metal→wealth metonymy. Marked as metonymy, not as metaphor.
- וּ֝מֵחָר֗וּץ “and [better] than gold”: חרוץ (a term for gold/fine gold) is used as a benchmark of highest material value. Considered hyperbole, but the verse is making a value judgment (wisdom truly is more beneficial than wealth), not an obvious exaggeration beyond plausibility. Primary figure is metonymy: gold → wealth/material riches.
- תְּבוּאָתָֽהּ “her yield / produce”: Again the suffix refers back to wisdom. תְּבוּאָה is literally agricultural produce/yield. Applying it to wisdom’s outcomes maps wisdom’s benefits into the domain of crop yield / economic return—another conceptual metaphor (wisdom as income‑producing asset/field). Marked as metaphor.
- Personification: While later verses strongly personify wisdom (vv.15–18: “in her right hand… her ways…”), here the feminine suffix “her” is grammatically normal for a feminine abstract noun. The *figurative* force lies in the economic/agricultural imagery (metaphor), not yet in distinctly human actions. I did **not** mark 3:14 itself as personification.
- Comparative structure (“better than silver … greater than gold”): Considered as possible hyperbolic praise. The line is evaluative but not clearly overstated beyond what the sage intends as literally true in a moral/theological sense, so I did not mark hyperbole.

Figurative elements included in JSON:
1) Metaphorical economic/agricultural language for wisdom’s benefits: סַ֭חְרָהּ … תְּבוּאָתָהּ (“her trade … her yield”).  
2) Metonymic use of “trade of silver” and “gold” for material wealth and financial return: מִסְּחַר־כָּסֶף … וּ֝מֵחָר֗וּץ.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "סַ֭חְרָהּ ... תְּבוּאָתָֽהּ",
    "english_text": "Her value in trade … her yield",
    "explanation": "Wisdom’s benefits are depicted in terms of economic merchandise and agricultural yield, treating wisdom as an income-producing asset whose ‘profit’ and ‘produce’ can be compared to financial returns. This maps an abstract moral-spiritual quality (wisdom) onto the concrete domain of trade and harvest.",
    "target": [
      "wisdom’s benefits and returns",
      "divine wisdom as a life-guiding virtue",
      "abstract moral-spiritual quality"
    ],
    "vehicle": [
      "profitable merchandise and abundant crop yield",
      "economic and agricultural gain",
      "material prosperity"
    ],
    "ground": [
      "superior profitability and lasting advantage",
      "value and benefit",
      "well-being and flourishing"
    ],
    "posture": [
      "commendation of wisdom’s profit",
      "praise and instruction",
      "positive stance"
    ],
    "confidence": 0.9,
    "speaker": "parental sage of Proverbs 3",
    "purpose": "To persuade the hearer that pursuing wisdom yields greater and more reliable benefits than any economic asset, by casting wisdom in the familiar imagery of profitable trade and produce."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "no",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "yes",
    "other": "no",
    "hebrew_text": "מִסְּחַר־כָּ֑סֶף וּ֝מֵחָר֗וּץ",
    "english_text": "than the trade of silver, and [better] than gold",
    "explanation": "‘Trade of silver’ uses the activity of trading as a stand-in for the profit gained from it, and ‘silver’ and ‘gold’ stand for material wealth and high economic value. They function as metonymic benchmarks for the best that material riches can offer, against which wisdom’s returns are measured.",
    "target": [
      "material riches (silver and gold)",
      "economic wealth",
      "material possessions"
    ],
    "vehicle": [
      "silver and gold as traded goods",
      "precious metals",
      "physical materials"
    ],
    "ground": [
      "high monetary value and profitability",
      "economic worth",
      "material aspect of life"
    ],
    "posture": [
      "relative devaluation compared with wisdom",
      "corrective moral instruction",
      "neutral-to-negative stance toward overvalued wealth"
    ],
    "confidence": 0.9,
    "speaker": "parental sage of Proverbs 3",
    "purpose": "To highlight the surpassing worth of wisdom by contrasting it with the most valued forms of material wealth, using silver and gold as shorthand for financial gain."
  }
]
```
```

#### HIGH Reasoning Detected (2 instances):

1. **For her merchandise is better than the merchandise of silver.** (Metaphor)
- Confidence: 0.92
- Explanation: Wisdom’s benefit is portrayed through a commercial metaphor: its gain is likened to merchandise or profit from trading silver, and declared to be superior in value.

2. **And her yield is greater than gold.** (Metaphor)
- Confidence: 0.9
- Explanation: The results of wisdom are described with harvest or return imagery: its outcomes are likened to a yield or produce whose value surpasses even fine gold.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
In this verse the poet evaluates wisdom (from v.13) by drawing on commercial and harvest imagery and by comparing it with precious metals. I examined each element as follows:

1. **“סַחְרָהּ / Her value in trade, her merchandise”**  
   - Considered whether this is literal or metaphorical. The feminine suffix (“her”) refers back to **חָכְמָה / wisdom** in v.13, which is an abstract quality, not an actual merchant or commodity.  
   - The noun **סַחַר** denotes “trade, merchandise, profit from trading.” Abstract wisdom cannot literally have merchandise or trade value in a marketplace.  
   - Conclusion: this is a **commercial metaphor**: the *benefit/profit* of possessing wisdom is being conceptualized as “her merchandise/merchandising.” Marked as **metaphor: yes**, not simile (no “like/as”).

2. **“מִסְּחַר־כָּסֶף / than the trade of silver”**  
   - This phrase extends the same commercial frame: “trade/merchandise of silver” is a literal kind of lucrative business in the ancient economy.  
   - I considered whether “silver” functions as **metonymy** for “wealth” in general. In biblical Hebrew, כֶסֶף can mean both “silver” and “money,” and silver and gold frequently represent wealth. However, here it is specifically “the trade of silver,” i.e., the profit one gains from dealing in a particularly valuable commodity. The metals themselves are the straightforward referent.  
   - The figurative force lies not so much in “silver” as in applying **“trade / merchandise”** language to wisdom. I therefore did **not** mark “silver” here as a distinct metonymy, but as part of the **vehicle** for the main metaphor.

3. **“תְּבוּאָתָהּ / Her yield, her produce”**  
   - **תְּבוּאָה** normally means agricultural “produce, harvest,” and by extension any “yield/return.”  
   - Again, abstract wisdom does not literally grow crops or yield a harvest. The poet speaks of the *results/outcomes* of wisdom as though they were a farmer’s or trader’s “yield.”  
   - This is another facet of the same conceptual mapping: **wisdom’s benefits** = **profitable yield**. Marked as **metaphor: yes**.

4. **“וּמֵחָרוּץ / than gold”**  
   - **חָרוּץ** is “fine gold.” As with “silver,” I considered whether this is metonymy for “material wealth.” It certainly functions as a benchmark of high value, but it still points directly to the precious metal itself as the clearest symbol of great worth.  
   - The figurative emphasis is not that “gold” stands for something else, but that the **yield of wisdom** is being valued **over** even the highest known material standards. I therefore did **not** mark “gold” itself as metonymy, but as part of the evaluative comparison in the larger metaphor.

5. **Comparative structure: “better than silver… greater than gold”**  
   - These are comparative assertions, not similes (no “like/as”). They intensify the commercial/harvest metaphor by setting up a graded parallelism:  
     - “Her trade” // “her yield”  
     - “trade of silver” // “gold”  
   - I asked whether this should be treated as **hyperbole**. The statement is strong but functions as a genuine value judgment in wisdom literature (cf. 8:10–11; 16:16); it is not presenting an obvious impossibility but a real theological evaluation (wisdom truly is more valuable than wealth). So I did **not** mark hyperbole.

6. **Pronoun “her” (סַחְרָהּ, תְּבוּאָתָהּ) and possible personification**  
   - The feminine suffix refers to חָכְמָה (wisdom, v.13), a grammatically feminine abstract noun. In the larger section (vv.13–18) wisdom is treated as a “she,” and elsewhere in Proverbs she is fully personified as a woman who calls and speaks (e.g., ch. 8).  
   - Here, however, the verse does not yet attribute personal actions to wisdom; it only attributes “merchandise” and “yield” to her. That is primarily a **commercial/harvest metaphor** about the *value* of an abstract quality, not an instance of vivid personification like “Wisdom cries out.”  
   - I therefore did **not** mark this verse specifically as **personification**, though it participates in the broader personified depiction of Wisdom in the surrounding context.

Overall, the verse uses **extended metaphor**: it maps the **benefit of wisdom** onto the domains of **trade/profit and harvest yield**, then evaluates that metaphorical “profit” as superior to the very best material gains symbolized by **silver and gold**.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "כִּ֤י ט֣וֹב סַ֭חְרָהּ מִסְּחַר־כָּ֑סֶף",
    "english_text": "For her merchandise is better than the merchandise of silver.",
    "explanation": "Wisdom’s benefit is portrayed through a commercial metaphor: its gain is likened to merchandise or profit from trading silver, and declared to be superior in value.",
    "target": [
      "benefit gained from possessing wisdom",
      "moral and practical insight given by God",
      "abstract spiritual and ethical quality"
    ],
    "vehicle": [
      "merchandise gained from trading silver",
      "profitable commercial activity and business gain",
      "economic and material prosperity domain"
    ],
    "ground": [
      "greater profitability and lasting value",
      "comparative advantage over material profit",
      "overall worth and benefit"
    ],
    "posture": [
      "commendation of wisdom's superior value",
      "instructional praise and exhortation",
      "positive evaluative stance"
    ],
    "confidence": 0.92,
    "speaker": "wise teacher/father in Proverbs",
    "purpose": "To persuade the hearer to value and pursue wisdom by depicting it as a more profitable investment than lucrative silver trade."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "וּ֝מֵחָר֗וּץ תְּבוּאָתָֽהּ",
    "english_text": "And her yield is greater than gold.",
    "explanation": "The results of wisdom are described with harvest or return imagery: its outcomes are likened to a yield or produce whose value surpasses even fine gold.",
    "target": [
      "results produced by living with wisdom",
      "outcomes of godly understanding in life",
      "abstract spiritual and ethical blessings"
    ],
    "vehicle": [
      "harvest yield or commercial return compared with fine gold",
      "abundant produce and high-value return",
      "agricultural and economic prosperity domain"
    ],
    "ground": [
      "surpassing yield and richness",
      "abundance and quality of outcomes",
      "overall benefit and reward"
    ],
    "posture": [
      "celebration of wisdom's rich rewards",
      "encouraging instruction",
      "positive evaluative stance"
    ],
    "confidence": 0.9,
    "speaker": "wise teacher/father in Proverbs",
    "purpose": "To strengthen the appeal for wisdom by depicting its outcomes as a yield more valuable than the highest standard of material wealth, fine gold."
  }
]
```
```

---

### Proverbs 3:15

**Text**: She is more precious than rubies; All of your goods cannot equal her.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 2 | $0.1744 | 18.9s | N/A | N/A |
| HIGH | 2 | $0.3123 | 71.6s | N/A | N/A |

#### MEDIUM Reasoning Detected (2 instances):

1. **She is more precious** (Metaphor, Personification)
- Confidence: 0.9
- Explanation: The pronoun 'she' refers to wisdom, an abstract quality, portrayed throughout the surrounding passage as a female figure ('Lady Wisdom'). This continues the personification of wisdom as a woman whose value and actions can be spoken of like a person’s, making the abstract virtue concrete and relational.

2. **She is more precious than rubies; all of your goods cannot equal her.** (Metaphor, Hyperbole)
- Confidence: 0.93
- Explanation: Wisdom, an abstract moral-spiritual quality, is evaluated as though it were a supreme luxury commodity whose worth exceeds rubies and the sum of all a person’s desirable possessions. This is a value metaphor (wisdom as incomparable treasure) expressed with commercial/comparative language. The sweeping claim that 'all your goods' cannot equal her is deliberate hyperbole to underscore her absolute superiority.

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- **הִיא “she” (implicit antecedent = חָכְמָה, “wisdom”)**  
  - Considered whether the feminine pronoun is merely grammatical (since חָכְמָה is grammatically feminine) or a genuine *personification*.  
  - In immediate context (vv. 13–18) wisdom is consistently treated with feminine pronominal suffixes and is portrayed as an agent who “has” hands (v. 16), “ways” and “paths” (v. 17), and can be “grasped” like a tree (v. 18). Across Proverbs (esp. 1; 8–9) this pattern clearly builds “Lady Wisdom” as a character.  
  - Therefore in this verse, the “she” is not just grammatical agreement but participates in that larger literary personification. I mark **personification = yes** for this element.

- **יְקָרָה הִיא מִפְּנִינִים “She is more precious than rubies/pearls”**  
  - Considered whether this is merely a literal axiological statement (wisdom’s value is greater than jewels) or figurative.  
  - Target domain: an abstract moral/intellectual quality (wisdom). Vehicle domain: concrete luxury stones used as wealth-storage. The comparison crosses domains (moral insight vs. luxury goods) and is cast in value language already developed in v. 14 (“her trading,” “her yield”). This builds a **conceptual metaphor: wisdom as a supremely valuable commodity/treasure**.  
  - No explicit כ־ “like/as” → grammatically a comparative, but conceptually it functions as a metaphorical valuation. I mark **metaphor = yes**, **simile = no**.

- **וְכׇל־חֲפָצֶיךָ לֹא יִשְׁווּ־בָהּ “and all your goods/desires do not equal her”**  
  - Considered whether חֲפָצֶיךָ is metonymic (e.g., “your desires” = “all you might value/own”) and whether the statement is hyperbolic.  
  - The phrase likely denotes “all that you desire / all your desirable things / all your possessions” in a broad sense. That breadth (“all”) combined with the absolute negation (“do not equal her”) functions as **hyperbolic** overstatement to stress her incomparable worth. In lived reality, one could exchange wisdom for goods, but the proverb absolutizes her superiority.  
  - The line also continues the same **economic-value metaphor**: wisdom as something whose worth exceeds any calculable sum of property or delights. I mark **metaphor = yes**, **hyperbole = yes**. I do **not** mark metonymy here, since the main force is not “X stands for Y” so much as “the totality of your valued things.”

- **Borderline / excluded elements**  
  - יְקָרָה “precious” by itself: evaluative but not figurative; it becomes figurative only in relation to the value-vehicle (“rubies,” “all your goods”).  
  - פְּנִינִים “rubies/pearls/corals”: literal luxury items used as the vehicle in the metaphor; not figurative in themselves.  
  - The verse contains no animal, path, house, or tree imagery; those appear in adjacent verses (vv. 17–18) but are not in v. 15, so they are not tagged here.


```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "יְקָרָה הִיא",
    "english_text": "She is more precious",
    "explanation": "The pronoun 'she' refers to wisdom, an abstract quality, portrayed throughout the surrounding passage as a female figure ('Lady Wisdom'). This continues the personification of wisdom as a woman whose value and actions can be spoken of like a person’s, making the abstract virtue concrete and relational.",
    "target": ["wisdom in Proverbs", "moral and practical discernment", "abstract virtue/concept"],
    "vehicle": ["female person 'she'", "woman, lady, daughter", "human person"],
    "ground": ["personal agency and relational presence", "human-like qualities and character", "personhood and social relation"],
    "posture": ["commendation of wisdom", "praise and exhortation", "positive stance"],
    "confidence": 0.9,
    "speaker": "sage/father addressing 'my son'",
    "purpose": "To make wisdom vivid and attractive by casting it as a personal, relational figure rather than an abstract idea."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "yes",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "יְקָרָה הִיא מִפְּנִינִים וְכׇל־חֲפָצֶיךָ לֹא יִשְׁווּ־בָהּ",
    "english_text": "She is more precious than rubies; all of your goods cannot equal her.",
    "explanation": "Wisdom, an abstract moral-spiritual quality, is evaluated as though it were a supreme luxury commodity whose worth exceeds rubies and the sum of all a person’s desirable possessions. This is a value metaphor (wisdom as incomparable treasure) expressed with commercial/comparative language. The sweeping claim that 'all your goods' cannot equal her is deliberate hyperbole to underscore her absolute superiority.",
    "target": ["wisdom in Proverbs", "moral and practical discernment", "abstract virtue/concept"],
    "vehicle": ["rubies/pearls and all your goods", "precious stones and material wealth", "economic value and possessions"],
    "ground": ["incomparable and unsurpassable worth", "superior value and desirability", "evaluation of worth/axiology"],
    "posture": ["exhortation to prize wisdom above wealth", "didactic praise and valuation", "positive stance"],
    "confidence": 0.93,
    "speaker": "sage/father addressing 'my son'",
    "purpose": "To persuade the hearer to prioritize the pursuit of wisdom over the pursuit of material wealth by depicting wisdom as a treasure whose value outstrips all tangible possessions."
  }
]
```
```

#### HIGH Reasoning Detected (2 instances):

1. **She is more precious than rubies** (Metaphor)
- Confidence: 0.93
- Explanation: An abstract quality (wisdom, referred to as "she") is evaluated using the concrete standard of highly valuable gemstones. Wisdom is not literally a gemstone; its worth is being mapped onto the economic domain of precious stones, creating a metaphorical comparison of value.

2. **All of your goods cannot equal her** (Metaphor, Hyperbole)
- Confidence: 0.95
- Explanation: The verse extends the economic-value metaphor by comparing wisdom to "all your goods" using the language of equality and comparison. The universal scope ("all your goods") and the absolute negation ("cannot equal her") form a sweeping, hyperbolic claim that nothing one possesses or desires can match wisdom's worth.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- **“הִיא / She”**
  - Considered whether this feminine pronoun, referring back to חָכְמָה (“wisdom,” v. 13), is itself personification.
  - In Proverbs, Wisdom is indeed personified as a woman in several contexts (esp. chs. 1, 8, 9). Here, however, the only marker inside this verse is the feminine pronoun, which can be explained by the grammatical gender of חָכְמָה.
  - Clear personification (Wisdom speaking, walking, building, etc.) appears more explicitly in nearby or later passages; in v. 15 alone we have value‑language, not actions or bodily features yet.
  - Conclusion: I note the broader personification background, but I do **not** mark v. 15’s “she” itself as a distinct case of personification for coding purposes.

- **“יְקָרָה / precious”**
  - Considered whether calling wisdom “precious” is metaphorical by extending concrete economic value language to an abstract quality.
  - The adjective יקר is widely used both for costly objects and for highly esteemed persons/qualities; the abstract sense is lexicalized.
  - By itself, “precious” here is not a clear, isolated metaphor; it becomes figurative when combined with a concrete standard of value (“rubies”).
  - Conclusion: by itself, not coded as a separate figurative unit; the figurative force lies in the whole comparative clause.

- **“מִפְּנִינִים / than rubies (pearls, corals)”**
  - Considered (a) simple concrete comparison, and (b) possible synecdoche/metonymy (rubies as a stand‑in for all luxury wealth).
  - In wisdom literature, פנינים functions as a standard of **highest material value** (cf. Prov 8:11; 31:10). The primary sense remains literal precious stones, but they also serve as a conventional “top of the scale” reference for material worth.
  - This functions as the **vehicle** in a value metaphor (wisdom is compared to the most valuable stones) rather than a true metonymic substitution.
  - Conclusion: treated as the **vehicle** within a metaphorical comparison (“more precious than rubies”), not as metonymy or a separate figure.

- **Clause: “יְקָרָה הִיא מִפְּנִינִים / She is more precious than rubies”**
  - Here an **abstract quality** (wisdom) is evaluated in terms taken from the domain of **luxury goods / precious stones**.
  - This is more than straightforward literal description: wisdom is not literally a gemstone; its worth is mapped against that concrete, economic domain.
  - This is a **comparative metaphor of value** (or comparison functioning like a metaphor). Syntax uses comparative מִן (“than”), not כ/“like,” so I treat it as a metaphorical comparison, not a classic “like/as” simile.
  - No hyperbole here in the strict sense; the statement expresses a strong but conceptually coherent value judgment rather than an impossible exaggeration.
  - Conclusion: Marked as **metaphor (value comparison)**; simile: no; hyperbole: no.

- **“וְכׇל־חֲפָצֶיךָ / all your goods, all your desires/things you delight in”**
  - Considered whether חֲפָצֶיךָ functions metonymically (e.g., “your goods” = your whole life, status, etc.).
  - The term can denote both “possessions/things” and “things one takes delight in,” but still stays within the semantic field of desirable objects/benefits.
  - There is no clear substitution of one domain for another; rather, this is a very **broad quantification** of material and experiential “goods.”
  - The breadth (“all”) contributes to **hyperbolic force** in the COLON as a whole but is not itself a separate metonymy.
  - Conclusion: not coded as metonymy; treated as part of a hyperbolic, metaphorical comparison when combined with “cannot equal her.”

- **“לֹא יִשְׁווּ־בָהּ / cannot equal her” (with “all your goods”)**
  - The verb שׁוה “to be equal, comparable” is standard lexical usage; not an idiom in itself.
  - However, the construction “all your goods cannot equal her” uses:
    - a **universal quantifier** (“all”), and
    - an **absolute negation** (“do not/cannot equal”)
    to say that **nothing at all**, taken together, reaches the worth of wisdom.
  - Conceptual structure: again, wisdom (abstract) is evaluated in **economic/comparative terms** against “all your goods” (concrete/material). This continues the **value metaphor** begun in v. 14–15a, mapping wisdom to the domain of wealth/commodities.
  - Because it claims that **everything** one could possess or desire fails to match wisdom, it has a strong **hyperbolic** flavor—sweeping, universal, and intensifying the earlier comparison with rubies.
  - Conclusion: the clause is both **metaphorical** (wisdom vs. goods in economic terms) and **hyperbolic** (“all your goods … not equal”).

- **Overall verse structure**
  - The two cola form a staircase:
    - v. 15a: wisdom > the **most valuable single material item** (rubies).
    - v. 15b: wisdom > **all** your accumulated goods.
  - Both cola belong to an extended **economic‑value metaphor** running through vv. 14–15 (merchandise, yield, precious, rubies, all goods).
  - For coding, I treat:
    - v. 15a as a **metaphorical comparison** (no hyperbole),
    - v. 15b as a **metaphorical comparison with hyperbolic scope**.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "יְקָרָה הִיא מִפְּנִינִים",
    "english_text": "She is more precious than rubies",
    "explanation": "An abstract quality (wisdom, referred to as \"she\") is evaluated using the concrete standard of highly valuable gemstones. Wisdom is not literally a gemstone; its worth is being mapped onto the economic domain of precious stones, creating a metaphorical comparison of value.",
    "target": [
      "wisdom as moral-spiritual insight",
      "virtue and inner character quality",
      "abstract quality"
    ],
    "vehicle": [
      "rubies as highly valuable gems",
      "precious stones and luxury wealth",
      "economic commodities and material wealth"
    ],
    "ground": [
      "surpassing preciousness and value",
      "economic worth and desirability",
      "overall value and importance"
    ],
    "posture": [
      "exaltation of wisdom's worth",
      "praise and commendation",
      "positive evaluative stance"
    ],
    "confidence": 0.93,
    "speaker": "Parental sage / narrator of Proverbs 3",
    "purpose": "To teach the listener to regard wisdom as surpassing even the highest imaginable material value."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "yes",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "וְכׇל־חֲפָצֶיךָ לֹא יִשְׁווּ־בָהּ",
    "english_text": "All of your goods cannot equal her",
    "explanation": "The verse extends the economic-value metaphor by comparing wisdom to \"all your goods\" using the language of equality and comparison. The universal scope (\"all your goods\") and the absolute negation (\"cannot equal her\") form a sweeping, hyperbolic claim that nothing one possesses or desires can match wisdom's worth.",
    "target": [
      "wisdom as moral-spiritual insight",
      "virtue and inner character quality",
      "abstract quality"
    ],
    "vehicle": [
      "all your goods and desirable possessions",
      "material wealth and benefits",
      "economic commodities and resources"
    ],
    "ground": [
      "incomparably greater value than any possessions",
      "superiority in worth over accumulated wealth",
      "ultimate value and priority"
    ],
    "posture": [
      "exaltation of wisdom's supremacy over wealth",
      "instructional praise and strong commendation",
      "positive evaluative stance"
    ],
    "confidence": 0.95,
    "speaker": "Parental sage / narrator of Proverbs 3",
    "purpose": "To urge the listener to prioritize wisdom above every possible possession or desired benefit by asserting, in hyperbolic fashion, that nothing they own or could desire can match it."
  }
]
```
```

---

### Proverbs 3:16

**Text**: In her right hand is length of days, In her left, riches and honor.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 2 | $0.2063 | 28.8s | N/A | N/A |
| HIGH | 2 | $0.3779 | 37.1s | N/A | N/A |

#### MEDIUM Reasoning Detected (2 instances):

1. **In her right hand is length of days, In her left, riches and honor.** (Metaphor, Personification)
- Confidence: 0.95
- Explanation: Wisdom, an abstract quality, is portrayed as a woman with a right and left hand that hold and dispense gifts. This personifies wisdom and metaphorically depicts her as a benefactress who offers long life and prosperity to those who embrace her.

2. **length of days** (Metaphor, Idiom)
- Confidence: 0.88
- Explanation: The expression 'length of days' is an idiomatic way of saying 'long life,' using spatial 'length' metaphorically for temporal duration (TIME/DURATION described as SPACE/LENGTH).

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- **“אֹ֣רֶךְ יָ֭מִים / length of days”**  
  - Considered whether this is literal or figurative. Literally it combines a spatial noun “length” with “days.” In Biblical Hebrew this is a conventional way to say “long life,” so it functions as an **idiomatic expression**.  
  - Conceptually, it rests on the metaphor **TIME IS SPACE / DURATION IS LENGTH** (temporal duration described in terms of spatial extension). Because the user’s brief wants figurative elements identified, I treat this as **both idiom and underlying metaphor**.  
  - Not hyperbole: it denotes genuine longevity, not necessarily “endless” life.

- **“בִּֽימִינָ֑הּ / in her right hand” and “בִּ֝שְׂמֹאולָ֗הּ / in her left [hand]”**  
  - First I considered whether “right hand / left hand” are just literal placements in the personified scene, or themselves figurative.  
  - Here, “her” refers back to **Wisdom** (חָכְמָה, vv. 13–15), which is an **abstract quality**. Giving wisdom a right and left hand is **personification**—attributing human bodily form and actions to an abstraction.  
  - In Hebrew culture, the “right hand” often connotes primacy, strength, or more honored gifts; the “left” the secondary gifts. So the distribution (“length of days” in the right; “riches and honor” in the left) adds a **metaphorical structure of Wisdom as a benefactress holding out gifts**.  
  - I therefore include this as **personification plus metaphor** (Wisdom conceptualized as a woman who can hold and dispense benefits).

- **Wisdom as “her” (implicit subject of the whole verse)**  
  - The verse itself does not name Wisdom explicitly but continues the feminine personification begun in vv. 13–15.  
  - This sustained depiction of wisdom as “she” who trades, holds, offers, walks, etc., is a classic **personification of an abstract quality**. Verse 16 is part of that extended figure, with special focus on her hands.  
  - I will capture this under the same personification/metaphor entry centered on “in her right hand… in her left…”

- **“עֹ֣שֶׁר וְכָבֽוֹד / riches and honor”**  
  - Considered whether these are metaphorical for spiritual blessings. In Proverbs they are often *concrete covenant blessings* (wealth; social esteem/standing), though these can include moral/spiritual dimensions.  
  - The text itself presents them straightforwardly as the kind of benefits wisdom yields; no clear metaphorical vehicle is invoked (no non‑wealth image used to stand for wealth).  
  - I therefore treat “riches and honor” here as **literal categories of blessing**, not primary metaphors or idioms.

No other clear figurative elements appear in this verse beyond the personification of Wisdom and the idiom/metaphor “length of days.”

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "אֹרֶךְ יָמִים בִּימִינָהּ בִּשְׂמֹאולָהּ עֹשֶׁר וְכָבוֹד",
    "english_text": "In her right hand is length of days, In her left, riches and honor.",
    "explanation": "Wisdom, an abstract quality, is portrayed as a woman with a right and left hand that hold and dispense gifts. This personifies wisdom and metaphorically depicts her as a benefactress who offers long life and prosperity to those who embrace her.",
    "target": [
      "wisdom (ḥokmāh) as a benefactress",
      "moral and practical wisdom",
      "abstract virtue / godly skill in living"
    ],
    "vehicle": [
      "a woman holding gifts in her right and left hands",
      "human female figure with hands",
      "human being / embodied person"
    ],
    "ground": [
      "ability to possess and distribute life and prosperity",
      "power to bestow benefits and security",
      "efficacy and generosity of wisdom"
    ],
    "posture": [
      "commendation of wisdom's benefits",
      "praise and encouragement",
      "positive, exhortational stance"
    ],
    "confidence": 0.95,
    "speaker": "Proverbs narrator/teacher",
    "purpose": "To make the advantages of wisdom vivid and attractive by picturing wisdom as a person who actively offers long life, wealth, and honor to those who take hold of her."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "yes",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "אֹרֶךְ יָמִים",
    "english_text": "length of days",
    "explanation": "The expression 'length of days' is an idiomatic way of saying 'long life,' using spatial 'length' metaphorically for temporal duration (TIME/DURATION described as SPACE/LENGTH).",
    "target": [
      "lifespan of the person who gains wisdom",
      "human life and its duration",
      "human temporal existence"
    ],
    "vehicle": [
      "length as a spatial dimension",
      "physical extension in space",
      "spatial measurement"
    ],
    "ground": [
      "extended duration of life",
      "longevity and continuance",
      "extent or fullness over time"
    ],
    "posture": [
      "promise of benefit for the wise",
      "instructional assurance",
      "positive, didactic stance"
    ],
    "confidence": 0.88,
    "speaker": "Proverbs narrator/teacher",
    "purpose": "To promise that embracing wisdom results in a long life, using a concise idiomatic and metaphorical expression familiar in Hebrew."
  }
]
```
```

#### HIGH Reasoning Detected (2 instances):

1. **In her right hand is length of days, In her left, riches and honor.** (Metaphor, Personification)
- Confidence: 0.95
- Explanation: Wisdom (ḥokmāh), an abstract quality, is depicted as a woman with right and left hands that hold and bestow long life, riches, and honor. This is personification of Wisdom as a benefactress whose hands carry gifts, and a metaphor that presents her benefits as concrete objects held out to the disciple.

2. **length of days** (Metaphor)
- Confidence: 0.85
- Explanation: The phrase uses the concrete notion of spatial length (אֹרֶךְ) to describe the temporal duration of life. It metaphorically conceptualizes a long lifespan as 'lengthened' days, mapping physical extension onto time.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
- **Phrase: “אֹ֣רֶךְ יָ֭מִים / length of days”**
  - Considered whether this is:
    - a **literal** description of time,
    - a **fixed idiom**, or  
    - a **metaphor** (spatial “length” applied to temporal “days”).
  - In Biblical Hebrew, אֹרֶךְ (“length”) is a spatial term; applied to “days,” it maps spatial extension onto temporal duration (long life). This is the common conceptual metaphor **TIME/LIFE IS LENGTH IN SPACE**.
  - Because the expression is still semantically transparent (not opaque like a true idiom), I treat it as **metaphor**, not as a separate idiom.
  - Marked as figurative (metaphor).

- **Phrase: “בִּֽימִינָ֑הּ ... בִּשְׂמֹאולָ֗הּ / in her right hand … in her left”**
  - The pronoun “her” refers back to **Wisdom (חָכְמָה)**, already personified as a woman in vv. 13–15, 17–18.
  - Considered whether this is:
    - merely pronominal reference,  
    - or a **continuation of personification** with concrete body imagery.
  - An abstract quality (“wisdom”) is given **hands** (right/left), in which she “has”/“holds” abstract goods (long life, riches, honor). This is a clear **personification** of Wisdom as a woman holding gifts.
  - The image also involves a further metaphor: **abstract benefits are concrete objects held in hands and bestowed**, but this is part of the same personified scene, so I include it under one figurative complex (metaphor + personification).
  - Right vs. left hand likely carries the cultural nuance of the **right hand as primary/preeminent**, but that symbolic asymmetry is secondary to the central personification.
  - Marked as figurative (metaphor + personification).

- **Phrase: “עֹ֣שֶׁר וְכָבֽוֹד / riches and honor”**
  - Considered whether this is:
    - purely **literal** (material wealth + social honor),
    - or **metonymy** for “all kinds of prosperity / blessing.”
  - In proverbial theology, “riches and honor” are standard, fairly concrete covenantal blessings. They can function as a shorthand for prosperity, but that is a normal semantic generalization rather than a clearly marked rhetorical figure.
  - I therefore treat them as **primarily literal promised outcomes**, not as a distinct, marked figure of speech.
  - Not marked as figurative.

- **Whole verse structure: “In her right hand is length of days, In her left, riches and honor”**
  - Considered whether to treat the entire bicola as a **single extended metaphor** (Wisdom as a benefactress holding out two classes of gifts).
  - This is essentially the same image as the personification noted above: Lady Wisdom stands before the disciple, holding life in one hand, prosperity and honor in the other.
  - To avoid redundancy, I encode this extended image via:
    - one entry for **Wisdom’s personification with right/left hands** (including the notion of gifts in hands), and
    - one entry for **“length of days”** as a spatial metaphor for long life.
  - The distributive structure (right-hand gift / left-hand gift) is figuratively vivid but does not introduce an additional distinct type of figure beyond those two.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "אֹ֣רֶךְ יָ֭מִים בִּֽימִינָ֑הּ בִּ֝שְׂמֹאולָ֗הּ עֹ֣שֶׁר וְכָבֽוֹד",
    "english_text": "In her right hand is length of days, In her left, riches and honor.",
    "explanation": "Wisdom (ḥokmāh), an abstract quality, is depicted as a woman with right and left hands that hold and bestow long life, riches, and honor. This is personification of Wisdom as a benefactress whose hands carry gifts, and a metaphor that presents her benefits as concrete objects held out to the disciple.",
    "target": [
      "Lady Wisdom (ḥokmāh) offering benefits",
      "personified wisdom figure in Proverbs",
      "abstract virtue or divine attribute"
    ],
    "vehicle": [
      "woman holding gifts in her right and left hands",
      "human benefactress or patron",
      "human being"
    ],
    "ground": [
      "ability to possess and bestow valuable benefits",
      "power to grant rewards and outcomes",
      "effective agency and generosity"
    ],
    "posture": [
      "commendation of wisdom's generosity and reward",
      "praise and exhortation to seek wisdom",
      "positive stance toward wisdom"
    ],
    "confidence": 0.95,
    "speaker": "Proverbs sage (father/teacher voice)",
    "purpose": "To make wisdom attractive by portraying her as a generous patroness who holds out both longevity and prosperity to those who embrace her."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "אֹ֣רֶךְ יָ֭מִים",
    "english_text": "length of days",
    "explanation": "The phrase uses the concrete notion of spatial length (אֹרֶךְ) to describe the temporal duration of life. It metaphorically conceptualizes a long lifespan as 'lengthened' days, mapping physical extension onto time.",
    "target": [
      "lifespan of the person who gains wisdom",
      "human lifespan and duration of life",
      "time experienced in human life"
    ],
    "vehicle": [
      "long physical length",
      "spatial extension in distance",
      "physical space"
    ],
    "ground": [
      "great extent or long duration",
      "prolongation and abundance in measure",
      "quantity or magnitude"
    ],
    "posture": [
      "promise of blessing through longevity",
      "encouragement and positive assurance",
      "positive stance"
    ],
    "confidence": 0.85,
    "speaker": "Proverbs sage (father/teacher voice)",
    "purpose": "To describe the benefit of wisdom—long life—in vivid, concrete terms that evoke extension and abundance."
  }
]
```
```

---

### Proverbs 3:17

**Text**: Her ways are pleasant ways, And all her paths, peaceful.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 2 | $0.2472 | 43.2s | N/A | N/A |
| HIGH | 2 | $0.4465 | 50.7s | N/A | N/A |

#### MEDIUM Reasoning Detected (2 instances):

1. **Her ways are pleasant ways** (Metaphor, Personification)
- Confidence: 0.96
- Explanation: The abstract quality of Wisdom is personified as a woman who has 'ways,' and these 'ways' metaphorically depict the lifestyle and conduct shaped by wisdom as a pleasant path or course of life.

2. **And all her paths, peaceful** (Metaphor, Personification)
- Confidence: 0.96
- Explanation: Wisdom continues to be personified as a woman whose 'paths' represent the various courses and decisions of a life shaped by wisdom. These paths are metaphorically characterized as 'peace,' indicating a life of safety, wholeness, and harmonious well-being.

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
I examined each potential figurative element in the verse:

1. **“דְּרָכֶ֥יהָ” / “Her ways”**
   - Considered whether “ways” (דְּרָכִים) is literal or metaphorical.
   - In biblical Hebrew, *derek* frequently functions as a conventional metaphor for conduct, lifestyle, or mode of behavior, not only a physical road.
   - Here the “her” is Wisdom (חָכְמָה) personified as a woman in vv. 13–18. So:
     - Wisdom itself is an abstraction treated as a person (“her”).
     - Her “ways” are the manners of life that follow from embracing wisdom.
   - Conclusion: This is part of the **LIFE/CONDUCT AS PATH** metaphor and sustains the **personification** of Wisdom. Marked as *metaphor* and *personification*.

2. **“דַרְכֵי־נֹ֑עַם” / “pleasant ways”**
   - Considered whether this is literal (a physically pleasant route) or figurative (pleasantness of life).
   - Since the “ways” belong to Wisdom (an abstract quality) and describe the experience of living by wisdom, “pleasant” refers to the *quality of life and its outcomes*, not to a literal road’s scenery or ease.
   - This continues the same underlying path metaphor rather than introducing a new figurative type.
   - Conclusion: Figurative as part of the **path metaphor** for life directed by wisdom. No additional idiom or hyperbole.

3. **“וְֽכׇל־נְתִ֖יבוֹתֶ֣יהָ” / “and all her paths”**
   - *Netivot* are literal tracks/paths, but again modified by “her” (Wisdom).
   - The verse parallels “ways” // “paths” (דְּרָכֶיהָ // נְתִיבוֹתֶיהָ), a standard Hebrew poetic parallelism, both referring to the life-course shaped by wisdom.
   - Considered whether “all” (כׇּל־) implies hyperbole. Determined it is a comprehensive generalization (“every aspect of life governed by wisdom”) rather than exaggerated overstatement.
   - Conclusion: **Metaphorical** (life-choices / life-course as “paths”), again joined with **personification** (Wisdom with “her paths”).

4. **“שָׁלוֹם” / “peace” in “וְֽכׇל־נְתִיבוֹתֶ֣יהָ שָׁלֽוֹם”**
   - Considered metonymy: in Hebrew, *shalom* can denote not only absence of conflict but wholeness, welfare, prosperity.
   - Here, however, that broad sense is simply the normal semantic range of *shalom*, not a distinct metonymic figure (e.g., “bread” for “food”).
   - The figurative element lies more in *paths = peace* (a way of life depicted as a peaceful path), not in *shalom* itself as a figure.
   - Conclusion: Treat *shalom* as literal within its extended semantic range, but part of the **metaphorical predication** that describes wisdom’s “paths” as “peace.”

5. **Overall personification of Wisdom (“her … her …”)**
   - The entire unit vv. 13–18 depicts Wisdom as a woman who has:
     - trade value (vv. 14–15),
     - hands (v. 16),
     - ways and paths (v. 17),
     - and is a tree of life (v. 18).
   - In v. 17 specifically, the feminine pronominal suffixes (“her ways,” “her paths”) presuppose this personification.
   - Conclusion: v. 17 participates clearly in **personification** of the abstract concept Wisdom as a female figure whose “ways” and “paths” one can follow.

6. **Idioms or other figures**
   - Checked if “ways of pleasantness” or “paths of peace” function as fixed idioms in biblical Hebrew.
   - They are poetically shaped but not recognizable as set idioms with non-compositional meanings.
   - No clear hyperbole beyond normal wisdom generalization; no independent metonymies beyond the basic metaphoric construal of “way/path” for “conduct.”

Based on this, I identify **two closely related metaphorical/personificational clauses** within the verse, corresponding to the two hemistichs.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "דְּרָכֶ֥יהָ דַרְכֵי־נֹ֑עַם",
    "english_text": "Her ways are pleasant ways",
    "explanation": "The abstract quality of Wisdom is personified as a woman who has 'ways,' and these 'ways' metaphorically depict the lifestyle and conduct shaped by wisdom as a pleasant path or course of life.",
    "target": [
      "the lifestyle shaped by wisdom",
      "wise conduct and character",
      "human moral and spiritual life"
    ],
    "vehicle": [
      "ways / roadways",
      "routes and paths",
      "spatial movement and travel"
    ],
    "ground": [
      "pleasantness and attractiveness",
      "beneficial and enjoyable quality",
      "overall well-being and positive experience"
    ],
    "posture": [
      "commendation of wisdom",
      "praise and approval",
      "positive stance"
    ],
    "confidence": 0.96,
    "speaker": "sage narrator of Proverbs",
    "purpose": "To depict a life guided by wisdom as an attractive, pleasant course, thereby motivating the listener to pursue and embrace wisdom."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "וְֽכׇל־נְתִיבוֹתֶ֣יהָ שָׁלֽוֹם",
    "english_text": "And all her paths, peaceful",
    "explanation": "Wisdom continues to be personified as a woman whose 'paths' represent the various courses and decisions of a life shaped by wisdom. These paths are metaphorically characterized as 'peace,' indicating a life of safety, wholeness, and harmonious well-being.",
    "target": [
      "the various courses of life under wisdom",
      "wise choices and life-paths",
      "human moral and spiritual journey"
    ],
    "vehicle": [
      "paths / tracks",
      "routes and ways",
      "spatial movement and travel"
    ],
    "ground": [
      "peace, safety, and wholeness",
      "secure and harmonious quality of life",
      "overall flourishing and stability"
    ],
    "posture": [
      "commendation of wisdom",
      "praise and approval",
      "positive stance"
    ],
    "confidence": 0.96,
    "speaker": "sage narrator of Proverbs",
    "purpose": "To portray every aspect of a wisdom-governed life as a peaceful, secure path, reinforcing the desirability and comprehensive benefit of embracing wisdom."
  }
]
```
```

#### HIGH Reasoning Detected (2 instances):

1. **Her ways are pleasant ways** (Metaphor, Personification)
- Confidence: 0.93
- Explanation: The 'ways' belonging to wisdom are not literal roads but a metaphor for the lifestyle and conduct shaped by wisdom, portrayed as experientially pleasant. This continues the personification of Wisdom as a woman whose 'ways' can be followed.

2. **And all her paths, peaceful.** (Metaphor, Personification)
- Confidence: 0.92
- Explanation: Wisdom's 'paths' are a metaphor for specific courses of action and decisions in a life guided by wisdom. Describing all these paths as 'peace' presents wise living as characterized by comprehensive well-being and security, within the larger personification of Wisdom as a woman whose paths can be walked.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:

1. **“דְּרָכֶ֥יהָ / Her ways”**  
   - Considered whether “ways” (דְּרָכִים) is literal (physical roads) or metaphorical.  
   - In context, the antecedent of “her” is **חָכְמָה / wisdom** (vv. 13–16, 18). Wisdom is an abstract quality, not a literal traveler with roads.  
   - In Proverbs, “way/path” language is a standard **conceptual metaphor** for one’s **manner of life, conduct, and life-course** (e.g., 3:6, 6:23, 12:28).  
   - Therefore **“her ways”** = the *lifestyle / conduct shaped by wisdom*, **not** literal roads → **metaphor** (life as a way).  
   - Because an abstract quality (“wisdom”) is spoken of as having “ways,” and in the immediate context as having “hands” (v. 16) and being a “tree of life” (v. 18), this verse participates in an **extended personification of Wisdom**. So I treat this as involving both **metaphor (paths)** and **personification (Wisdom as a lady whose ‘ways’ can be walked).**

2. **“דַרְכֵי־נֹ֑עַם / pleasant ways”**  
   - “Pleasantness” (נֹעַם) is a value judgment but belongs to the same domain as a person’s experience; it is not itself a metaphor.  
   - The **figurative element is still “ways”** being applied to a life-course; “pleasant” simply characterizes the metaphorical “ways.”  
   - No idiom or hyperbole here; it is straightforward evaluative description of the metaphorical “ways.”

3. **“וְֽכׇל־נְתִיבוֹתֶ֣יהָ / all her paths”**  
   - Again, considered whether “paths” (נְתִיבוֹת) might be literal tracks.  
   - Parallelism with “her ways” and the broader use of “path” imagery in Proverbs for **moral and existential courses** (e.g., 2:8–9, 4:11, 4:18–19) strongly indicates a **metaphor**: “paths” = individual decisions and courses of action formed by wisdom.  
   - The pronominal suffix “her” again ties this to personified Wisdom; the abstraction “wisdom” is pictured as having many walkable “paths.” This contributes to the **personification**.  
   - “All” (כָּל) is a generalization, but not strong enough to count as clear hyperbole; it is normal didactic totalizing language, so I did **not** mark it as hyperbole.

4. **“שָׁלוֹם / peace”** in “וְֽכׇל־נְתִיבוֹתֶ֣יהָ שָׁלֽוֹם / all her paths, peaceful.”  
   - Hebrew **שָׁלוֹם** already has a broad **literal** semantic range: wholeness, well-being, safety, not just absence of war.  
   - The construction is an **elliptical nominal clause** (“all her paths [are] peace”). One could ask whether “peace” stands metonymically for “a situation characterized by peace,” but that is very close to its normal sense.  
   - I considered marking a metonymy (result for path), but in light of how שָׁלוֹם regularly functions as a **state of life**, I judge this to be **primarily literal within the metaphorical ‘paths’ frame**. The only clear figurative structure remains the **path metaphor**; I do **not** mark “peace” itself as figurative.

5. **Personification of Wisdom (“her”) in this verse**  
   - While the noun “wisdom” (חָכְמָה) does not appear in v. 17, the feminine pronominal suffixes (“her ways,” “her paths”) rely on the antecedent from vv. 13–16. There Wisdom is clearly **personified** (she has hands, she is more precious than rubies, she is a tree of life, etc.).  
   - Verse 17 participates in this same extended portrait by treating Wisdom as a “she” whose “ways” and “paths” can be traversed.  
   - So in the JSON I mark **personification = “yes”** for these path-phrases, though the **primary local figure** is the **path metaphor**.

Summary:  
- **Figurative elements to encode:**  
  - “דְּרָכֶ֥יהָ דַרְכֵי־נֹ֑עַם / Her ways are pleasant ways” → metaphor (life as way), with personified Wisdom as possessor of “ways.”  
  - “וְֽכׇל־נְתִיבוֹתֶ֣יהָ שָׁלֽוֹם / And all her paths, peaceful” → metaphor (life choices as paths), again within Wisdom’s personified framework.  
- **Elements considered but not marked figurative:**  
  - “נֹעַם / pleasantness” – evaluative but not figurative.  
  - “שָׁלוֹם / peace” – broad but within its normal literal semantic range; no clear additional metaphor or metonymy beyond the path image.  
  - “כָּל / all” – totalizing but not strong hyperbole.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "דְּרָכֶ֥יהָ דַרְכֵי־נֹ֑עַם",
    "english_text": "Her ways are pleasant ways",
    "explanation": "The 'ways' belonging to wisdom are not literal roads but a metaphor for the lifestyle and conduct shaped by wisdom, portrayed as experientially pleasant. This continues the personification of Wisdom as a woman whose 'ways' can be followed.",
    "target": [
      "ways of living shaped by wisdom",
      "wise conduct and lifestyle",
      "human moral-existential life"
    ],
    "vehicle": [
      "pleasant ways or roads",
      "travel paths and routes",
      "journey and movement domain"
    ],
    "ground": [
      "pleasantness and attractiveness of wise living",
      "positive experience and benefit",
      "overall well-being and flourishing"
    ],
    "posture": [
      "commendation of wisdom's way of life",
      "exhortation and praise of wisdom",
      "positive stance"
    ],
    "confidence": 0.93,
    "speaker": "Proverbs sage/narrator",
    "purpose": "To depict the life shaped by wisdom as attractive and enjoyable, thereby motivating the audience to seek and follow wisdom."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "וְֽכׇל־נְתִיבוֹתֶ֣יהָ שָׁלֽוֹם",
    "english_text": "And all her paths, peaceful.",
    "explanation": "Wisdom's 'paths' are a metaphor for specific courses of action and decisions in a life guided by wisdom. Describing all these paths as 'peace' presents wise living as characterized by comprehensive well-being and security, within the larger personification of Wisdom as a woman whose paths can be walked.",
    "target": [
      "paths of life under wisdom",
      "wise conduct and decisions",
      "human moral-existential life"
    ],
    "vehicle": [
      "paths or tracks",
      "travel routes and roads",
      "journey and movement domain"
    ],
    "ground": [
      "peaceful and secure character of wise living",
      "safety, tranquility, and lack of harm",
      "overall well-being and flourishing"
    ],
    "posture": [
      "commendation of wisdom's way of life",
      "exhortation and praise of wisdom",
      "positive stance"
    ],
    "confidence": 0.92,
    "speaker": "Proverbs sage/narrator",
    "purpose": "To assure the audience that a life directed by wisdom leads to peace and safety, encouraging them to choose wisdom's paths over alternative ways."
  }
]
```
```

---

### Proverbs 3:18

**Text**: She is a tree of life to those who grasp her, And whoever holds on to her is happy.

| Model | Instances | Cost | Time | Input Tokens | Output Tokens |
|-------|-----------|------|------|--------------|---------------|
| MEDIUM | 2 | $0.2968 | 60.1s | N/A | N/A |
| HIGH | 2 | $0.5162 | 65.6s | N/A | N/A |

#### MEDIUM Reasoning Detected (2 instances):

1. **She is a tree of life** (Metaphor)
- Confidence: 0.96
- Explanation: The abstract, personified figure of Wisdom is directly identified with a 'tree of life', evoking the Edenic image of a life-giving tree. This metaphor portrays wisdom as the source of vitality, longevity, and flourishing for those who embrace her.

2. **to those who grasp her, and whoever holds on to her is happy** (Metaphor, Personification)
- Confidence: 0.88
- Explanation: Physical verbs of grasping and holding are used of an abstract, personified Wisdom, depicting devoted adherence and ongoing loyalty. Wisdom is treated as a figure one can seize and support, and those who maintain this firm attachment are declared blessed.

**MEDIUM Reasoning (complete)**:
```
FIGURATIVE_DETECTION:

1. **“עֵץ־חַיִּים הִיא / She is a tree of life”**  
   - Considered: whether this is a literal botanical reference, a set idiom, or a deliberate metaphor.  
   - Reasoning: The referent of “she” in the immediate context (vv. 13–17) is חָכְמָה / תְּבוּנָה (“wisdom / understanding”), an abstract quality personified as a woman. An abstract concept cannot literally be a “tree.” “Tree of life” alludes to Gen 2–3 and in Proverbs functions as a stock image for a life‑giving reality (cf. 11:30; 13:12; 15:4). No כְּ/“like” is present, so this is a **direct metaphor**, not a simile.  
   - Conclusion: **Metaphor, high confidence.** Target = wisdom; Vehicle = “tree of life”; Ground = wisdom as life‑giving, sustaining, protective.

2. **The feminine pronouns: “הִיא … בָּהּ / she … her”**  
   - Considered: whether the feminine pronominal forms themselves should be counted as personification in this verse.  
   - Reasoning: In Hebrew, חָכְמָה is grammatically feminine, so feminine agreement is formally required. However, in Prov 1–9 this grammatical femininity is **developed into a literary persona** (“Lady Wisdom”), spoken of as a woman who calls, has hands, a house, etc. In vv. 15–17, the same “she” has a right hand and left hand. Here, the same “she/her” is the one that can be “grasped” and “held,” which presupposes a quasi‑personal, embodied figure. So, in *this verse*, the personification remains in force as part of an ongoing portrayal.  
   - Conclusion: Personification is **present in the verse as part of the grasp/hold imagery**, not as an isolated pronoun. I will mark it together with the verbs of grasping/holding in a combined entry.

3. **“לַמַּחֲזִיקִים בָּהּ / to those who grasp her”**  
   - Considered: whether “grasp” is literal or figurative, and whether this is an idiom.  
   - Reasoning: The verb החזיק denotes physical taking hold or gripping. One cannot literally “grip” an abstract quality; the object here is wisdom. This is the common biblical pattern where physical actions of the hand/body are used figuratively for allegiance, adherence, or determination (e.g., “hold fast to the LORD”). It is not so frozen that the concrete image disappears; the physicality is still meaningful.  
   - Conclusion: **Metaphor, moderate–high confidence** (physical grasping → committed adherence to wisdom). Also participates in the personification, since wisdom is treated as something/someone you can hold.

4. **“וְתֹמְכֶיהָ מְאֻשָּׁר / and whoever holds on to her is happy”**  
   - Considered: whether “holds on to her” is literal, metaphorical, or idiomatic.  
   - Reasoning: תָּמַךְ is to support, hold, or sustain—again a physical verb. Applied to an abstract wisdom, it depicts supporters/holders of a personified wisdom figure. This mirrors the previous clause’s physical imagery and extends the same conceptual mapping: those who maintain their hold on wisdom are blessed.  
   - Conclusion: **Metaphor + personification, moderate–high confidence** (physical support → ongoing loyalty/support of wisdom; wisdom treated as someone that can be “supported” or “upheld”).

5. **“מְאֻשָּׁר / happy, blessed”**  
   - Considered: whether “happy/blessed” is figurative (hyperbole, idiom) or straightforward evaluation.  
   - Reasoning: מְאֻשָּׁר is a normal adjectival predicate for a fortunate, enviable state (cf. אַשְׁרֵי). It is evaluative but not obviously metaphorical; no underlying image domain is invoked beyond general well‑being.  
   - Conclusion: **Not figurative** in the technical sense; it is a literal statement of blessedness as the result of the (figuratively described) relationship to wisdom.

Overall:  
- Major figurative element: **“She is a tree of life”** (wisdom → tree of life metaphor).  
- Secondary figurative element: **physical “grasp/hold” imagery applied to wisdom**, which both extends the personification of Wisdom and uses bodily action as a metaphor for commitment/loyalty.

---

```json
[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "עֵץ־חַיִּים הִיא",
    "english_text": "She is a tree of life",
    "explanation": "The abstract, personified figure of Wisdom is directly identified with a 'tree of life', evoking the Edenic image of a life-giving tree. This metaphor portrays wisdom as the source of vitality, longevity, and flourishing for those who embrace her.",
    "target": [
      "personified Wisdom (חָכְמָה)",
      "divine wisdom and moral-spiritual insight",
      "abstract spiritual-moral quality"
    ],
    "vehicle": [
      "tree of life",
      "fruit-bearing, life-sustaining tree",
      "natural life-giving object"
    ],
    "ground": [
      "life-giving source of flourishing and safety",
      "provides vitality, longevity, well-being",
      "beneficial existential condition"
    ],
    "posture": [
      "commendation of wisdom as life-giving",
      "praise and exhortation to seek wisdom",
      "positive stance"
    ],
    "confidence": 0.96,
    "speaker": "Narrator / wisdom teacher",
    "purpose": "To motivate the audience to value and pursue wisdom by portraying it as the ultimate source of life and blessing, echoing and reorienting the Edenic 'tree of life' imagery."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "yes",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "לַמַּחֲזִיקִים בָּהּ וְתֹמְכֶיהָ מְאֻשָּׁר",
    "english_text": "to those who grasp her, and whoever holds on to her is happy",
    "explanation": "Physical verbs of grasping and holding are used of an abstract, personified Wisdom, depicting devoted adherence and ongoing loyalty. Wisdom is treated as a figure one can seize and support, and those who maintain this firm attachment are declared blessed.",
    "target": [
      "the relationship of a disciple to Wisdom",
      "devotion and loyalty to divine wisdom",
      "abstract spiritual-moral commitment"
    ],
    "vehicle": [
      "physically grasping and supporting a person or object",
      "bodily embrace and sustaining hold",
      "human physical action"
    ],
    "ground": [
      "firm attachment and persevering loyalty",
      "committed adherence, support, and steadfastness",
      "relational faithfulness"
    ],
    "posture": [
      "commendation of those attached to wisdom",
      "instructional praise and promise of blessing",
      "positive stance"
    ],
    "confidence": 0.88,
    "speaker": "Narrator / wisdom teacher",
    "purpose": "To depict adherence to wisdom in vivid, relational terms and to promise blessedness to those who tenaciously cling to and uphold wisdom, thereby urging sustained commitment."
  }
]
```
```

#### HIGH Reasoning Detected (2 instances):

1. **She is a tree of life to those who grasp her** (Metaphor)
- Confidence: 0.97
- Explanation: The abstract reality of wisdom is directly identified with a 'tree of life,' evoking the Edenic image of a life-giving, sustaining tree. This metaphor portrays wisdom as a source of true life, vitality, and flourishing for those who attach themselves to her.

2. **to those who grasp her, and whoever holds on to her is happy** (Metaphor)
- Confidence: 0.88
- Explanation: The verbs 'grasp' and 'hold on to' use bodily actions of taking hold with the hands to depict an inner, moral-intellectual stance toward wisdom—firm adherence, loyalty, and tenacious attachment. This is a conceptual metaphor mapping physical grip onto steadfast commitment, promising blessedness to those who maintain such a hold.

**HIGH Reasoning (complete)**:
```
FIGURATIVE_DETECTION:
1. עֵץ־חַיִּים הִיא (“She is a tree of life”):
   - Considered whether “tree of life” could be literal (e.g., an actual cosmic tree, as in Gen 2–3) or metaphorical.
   - Here the understood subject is חָכְמָה “wisdom” (vv. 13–17), an abstract quality, so identifying her as a “tree of life” cannot be literal.
   - It is a metaphor (not a simile; no כ / “like”) mapping an abstract, moral-spiritual reality (wisdom) onto a concrete, life-giving tree image, with clear Edenic resonance.
   - Marked as: metaphor = yes; not personification (non-human → non-human, not non-human → human).

2. לַמַּחֲזִיקִים בָּהּ (“to those who grasp her”):
   - Considered whether “grasp” is literal or figurative.
   - Since “her” = wisdom (an intangible), physical “grasping” is not literally possible; this uses bodily action language to describe an inner, cognitive/moral response (embracing, adhering to).
   - Thus, it is a conceptual metaphor: “adherence/loyalty to wisdom” is “physically taking hold of something.” Not an idiom in the strict sense; the imagery remains vivid and transparent.
   - Marked as: metaphor = yes; not personification (humans act; wisdom is direct object).

3. וְתֹמְכֶיהָ (“whoever holds on to her” / “her supporters, those who hold her fast”):
   - Considered similarly whether “support/hold” is literal.
   - Again, “her” = wisdom; “supporting/holding” wisdom is not literal manual holding but depicts steadfast loyalty and ongoing reliance, extending the same grasp/hold metaphor.
   - This is a continuation/intensification of the same conceptual metaphor as in “grasp her,” emphasizing firmness and persistence.
   - Marked as: metaphor = yes; not idiom (still imagistic), not personification.

4. מְאֻשָּׁר (“happy / blessed / fortunate”):
   - Considered whether this is hyperbolic or metaphorical (e.g., “happy” as a metaphor for “objectively blessed”).
   - In context it functions as a standard beatitude term describing the resultant state of those who adhere to wisdom; no obvious figurative transfer from a different semantic domain.
   - Treated as straightforward evaluative language rather than a distinct metaphor or hyperbole.
   - Marked as: not figurative for current purposes.

5. The feminine pronoun הִיא (“she”):
   - Considered whether to classify this as personification.
   - The personification of Wisdom as a woman is established in the broader unit (vv. 13–17), but the bare feminine pronoun here follows the grammatical gender of חָכְמָה and, by itself, does not introduce a new figure in this verse.
   - The verse’s main figurative force resides in the metaphor “tree of life” and the grasp/hold language, not in the pronoun.
   - Not separately tagged as personification in this verse.

Therefore, figurative elements to encode in JSON:
- Metaphor: “She is a tree of life to those who grasp her” (Wisdom = tree of life).
- Metaphor: “those who grasp her / whoever holds on to her” (adherence to wisdom = physical grasp/hold).

---

[
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "עֵץ־חַיִּים הִיא לַמַּחֲזִיקִים בָּהּ",
    "english_text": "She is a tree of life to those who grasp her",
    "explanation": "The abstract reality of wisdom is directly identified with a 'tree of life,' evoking the Edenic image of a life-giving, sustaining tree. This metaphor portrays wisdom as a source of true life, vitality, and flourishing for those who attach themselves to her.",
    "target": [
      "wisdom (חָכְמָה) in Proverbs 3",
      "personified wisdom and moral instruction",
      "abstract spiritual-moral quality"
    ],
    "vehicle": [
      "tree of life (עֵץ־חַיִּים)",
      "sacred life-giving tree",
      "natural object symbolizing vitality and blessing"
    ],
    "ground": [
      "life-giving effect on those connected to it",
      "source of vitality, protection, and flourishing",
      "well-being, life, and blessing"
    ],
    "posture": [
      "commendation of wisdom's life-giving nature",
      "praise and encouragement to value wisdom",
      "positive stance toward wisdom and its benefits"
    ],
    "confidence": 0.97,
    "speaker": "sage narrator of Proverbs 3 (father/teacher figure)",
    "purpose": "To present wisdom as the ultimate life-giving source, akin to the Edenic tree of life, thereby motivating the hearer to embrace and cling to wisdom."
  },
  {
    "figurative_language": "yes",
    "simile": "no",
    "metaphor": "yes",
    "personification": "no",
    "idiom": "no",
    "hyperbole": "no",
    "metonymy": "no",
    "other": "no",
    "hebrew_text": "לַמַּחֲזִיקִים בָּהּ וְתֹמְכֶיהָ מְאֻשָּׁר",
    "english_text": "to those who grasp her, and whoever holds on to her is happy",
    "explanation": "The verbs 'grasp' and 'hold on to' use bodily actions of taking hold with the hands to depict an inner, moral-intellectual stance toward wisdom—firm adherence, loyalty, and tenacious attachment. This is a conceptual metaphor mapping physical grip onto steadfast commitment, promising blessedness to those who maintain such a hold.",
    "target": [
      "faithful adherence to wisdom",
      "moral and intellectual devotion to instruction",
      "human moral-spiritual response"
    ],
    "vehicle": [
      "grasping and holding with the hands",
      "firm physical grip or support",
      "bodily action of holding onto an object"
    ],
    "ground": [
      "tenacity and closeness in relationship to wisdom",
      "steadfastness, not letting go, ongoing reliance",
      "firm commitment and persevering loyalty"
    ],
    "posture": [
      "commendation of those who cling to wisdom",
      "encouragement and promised blessing for adherence",
      "positive stance toward devoted pursuit of wisdom"
    ],
    "confidence": 0.88,
    "speaker": "sage narrator of Proverbs 3 (father/teacher figure)",
    "purpose": "To urge hearers to maintain a firm, unwavering commitment to wisdom by portraying such commitment as a strong physical grasp that leads to blessedness."
  }
]
```

---

