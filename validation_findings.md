# LLM Errors in Figurative Language Detection

## Error Categories

### 1. Technical Cultic/Religious Terms Misidentified as Figurative

These are technical terms from ancient Israelite religious practice that have specific meanings, not figurative ones:

- **Leviticus 24:9** - "most holy things" (קֹדֶשׁ קׇדָשִׁים) - Technical cultic category, not metaphor
- **Leviticus 24:9** - "a due for all time" (חׇק־עוֹלָם) - Legal/cultic term for perpetual statute
- **Leviticus 6:18** - "most holy" (קֹדֶשׁ קׇדָשִׁים) - Technical cultic category
- **Leviticus 27:21** - "holy to YHWH" - Technical designation of consecration
- **Leviticus 20:14** - "depravity" (זִמָּה) - Technical moral/legal term
- **Numbers 15:3** - "odor pleasing to YHWH" - Technical cultic expression (though arguably anthropomorphic)
- **Leviticus 1:4** - "in expiation for you" - Technical sacrificial terminology

### 2. Formulaic Divine Speech Overcalled as Personification

The phrase "YHWH spoke" (וַיְדַבֵּר יְהוָה) is formulaic introduction to divine law:

- **Exodus 30:17** - "YHWH spoke"
- **Leviticus 15:1** - "YHWH spoke" 
- **Leviticus 6:17** - "YHWH spoke"
- **Leviticus 10:8** - "YHWH spoke"
- **Leviticus 19:3** - "I YHWH am your God" - Standard covenant formula
- **Numbers 15:1** - "YHWH spoke"

### 3. Literal Actions/Objects Misidentified as Metonymy

- **Leviticus 24:9** - "eat them" - Literal eating of showbread by priests
- **Leviticus 24:9** - "from YHWH's offerings by fire" - Literal sacrificial offerings
- **Leviticus 7:30** - "one's own hands" - Literal requirement for personal participation
- **Leviticus 7:30** - "the fat with the breast" - Literal parts of sacrifice
- **Leviticus 9:17** - "handful" - Literal measurement for grain offering
- **Leviticus 4:28** - "the sin of which one is guilty" - Literal description
- **Leviticus 1:4** - "head of the burnt offering" - Literal placement of hand on animal's head
- **Numbers 20:13** - "Waters of Meribah" - Place name, not metonymy

### 4. Misidentified or Questionable Metaphors

- **Leviticus 21:10** - "exalted above his fellows" - Literal hierarchical position of high priest
- **Leviticus 7:5** - "smoke" - Translation issue: Hebrew אִשֶּׁה means "fire offering"
- **Leviticus 20:14** - "put to the fire" - Possibly literal execution method
- **Exodus 25:20** - Cherubim descriptions - Literal artistic representations, not figurative

### 5. Ambiguous Cases Requiring Context

- **Numbers 13:23** - Large grape cluster - Could be literal description or hyperbole
- **Leviticus 24:4** - "He shall set up" - Misattributed to God when subject is likely the priest
- **Numbers 24:15** - "Word of Balaam" - Introduction formula, not metonymy
- **Leviticus 19:3** - "revere" - Literal command, not figurative

### 6. Correctly Identified Figurative Language

The LLM did correctly identify many genuine instances:
- **Leviticus 18:25** - "the land spewed out its inhabitants" (metaphor)
- **Leviticus 18:6** - "his own flesh" for family (metonymy)
- **Numbers 24:15** - "whose eye is true" (metaphor)
- **Exodus 5:13** - "as when you had straw" (simile with כַּאֲשֶׁר)

## Summary Statistics

- **Total verses analyzed**: ~40 verses
- **Total figurative instances claimed**: ~180
- **Estimated false positives**: ~60-70 (35-40%)
- **Most common error type**: Overcalling formulaic religious language as personification


Recommendations to Improve the LLM Output
Based on the error analysis, here are specific suggestions to modify your prompt to reduce false positives:
1. Add Explicit Exclusions for Technical Religious Language
Add to your prompt:
IMPORTANT EXCLUSIONS - DO NOT mark as figurative:
- Technical cultic terms: "most holy" (קֹדֶשׁ קׇדָשִׁים), "holy to YHWH", "perpetual statute" (חׇק־עוֹלָם), שֶׁקֶל הַקֹּדֶשׁ, טָה֑וֹר, קֹ֔דֶשׁ, לְכַפֵּ֥ר עָלָֽיו, תְּרוּמָ֖ה,קׇרְבָּנ֜וֹ שְׂעִירַ֤ת עִזִּים֙, שֶׁ֤מֶן הַמִּשְׁחָה֙,blood in the context of literal sacrifice
- Standard sacrificial terminology: "expiation", "sin offering", "guilt offering", "wave offering", עֹרֹתָ֥ם וְאֶת־בְּשָׂרָ֖ם וְאֶת־פִּרְשָֽׁם
- Formulaic introductions: "YHWH spoke to Moses saying", "Thus says YHWH"
- Covenant formulas: "I am YHWH your God"
- Legal/moral categories: zimmah (depravity), toevah (abomination)
- Literal ritual actions: eating sacred offerings, laying hands on sacrifices, measuring offerings
- Technical religious/legal terms should default to literal unless clearly used metaphorically
- actions that occur literally, locations that are actual, etc. in the context of the text should not be considered metaphorical (e.g. וַיִּרְגְּמ֥וּ אֹת֖וֹ אָ֑בֶן, מִחוּץ ,,,אֲשֶׁ֣ר עָבַ֔ר בֵּ֖ין הַגְּזָרִ֥ים הָאֵֽלֶּה,בַּקֹּ֔דֶשׁ,אֶת־דֶּ֖רֶךְ עֵ֥ץ הַֽחַיִּֽים,לַמַּחֲנֶה)
2. Refine the Personification Guidelines
Replace the current personification guidance with:
-personification: Human characteristics given to non-human entities (e.g. וְאֶת־מַלְכֵ֨י מִדְיָ֜ן הָרְג֣וּ עַל־חַלְלֵיהֶ֗ם אֶת־אֱוִ֤י וְאֶת־רֶ֙קֶם֙ וְאֶת־צ֤וּר וְאֶת־חוּר֙ וְאֶת־רֶ֔בַע חֲמֵ֖שֶׁת מַלְכֵ֣י מִדְיָ֑ן וְאֵת֙ בִּלְעָ֣ם בֶּן־בְּע֔וֹר הָרְג֖וּ בֶּחָֽרֶב - 'they slew' is a literal thing that the Israelits did)
-in this case, there is a non-human entity, but it's not DOING anything; it's just being slaughtered, so no personification; this is all literal: דַּבֵּ֤ר אֶֽל־אַהֲרֹן֙ וְאֶל־בָּנָ֣יו לֵאמֹ֔ר זֹ֥את תּוֹרַ֖ת הַֽחַטָּ֑את בִּמְק֡וֹם אֲשֶׁר֩ תִּשָּׁחֵ֨ט הָעֹלָ֜ה תִּשָּׁחֵ֤ט הַֽחַטָּאת֙ לִפְנֵ֣י יְהֹוָ֔ה קֹ֥דֶשׁ קׇֽדָשִׁ֖ים הִֽוא
IMPORTANT: 
- "YHWH spoke/said" in formulaic contexts (וַיְדַבֵּר יְהוָה) is NOT personification - it's standard biblical narrative
- Only mark divine speech as personification when it includes emotional or physical human actions beyond speaking (e.g., "YHWH repented", "YHWH's nostrils flared")
3. Clarify Metonymy vs. Literal Usage
Add:
metonymy: Substituting name with something closely associated
IMPORTANT DISTINCTION:
- If a body part/object is performing its literal function, it's NOT metonymy
- "Hands" bringing offering = literal if referring to physical act
- "Heart" = metonymy only if representing emotions/will, not the physical organ
- Place names (Waters of Meribah) = NOT metonymy, they're proper nouns
- this is not metonymy - Joseph is literally brought to this place: וְיוֹסֵ֖ף הוּרַ֣ד מִצְרָ֑יְמָה וַיִּקְנֵ֡הוּ פּוֹטִיפַר֩ סְרִ֨יס פַּרְעֹ֜ה שַׂ֤ר הַטַּבָּחִים֙ אִ֣ישׁ מִצְרִ֔י מִיַּד֙ הַיִּשְׁמְעֵאלִ֔ים אֲשֶׁ֥ר הוֹרִדֻ֖הוּ שָֽׁמָּה
- in this verse the blasphemer is just that - an actual person, not a stand-in for anything else. וַיְדַבֵּ֣ר מֹשֶׁה֮ אֶל־בְּנֵ֣י יִשְׂרָאֵל֒ וַיּוֹצִ֣יאוּ אֶת־הַֽמְקַלֵּ֗ל אֶל־מִחוּץ֙ לַֽמַּחֲנֶ֔ה 
- in this verse the children are just that - children, not a stand-in for anything else. וַיֹּ֨אמֶר יְהוּדָ֜ה אֶל־יִשְׂרָאֵ֣ל אָבִ֗יו שִׁלְחָ֥ה הַנַּ֛עַר אִתִּ֖י וְנָק֣וּמָה וְנֵלֵ֑כָה וְנִֽחְיֶה֙ וְלֹ֣א נָמ֔וּת גַּם־אֲנַ֥חְנוּ גַם־אַתָּ֖ה גַּם־טַפֵּֽנוּ
-in this verse the share does not stand in for anything - it's just the literal share: כֵּ֗ן בְּנ֣וֹת צְלׇפְחָד֮ דֹּבְרֹת֒ נָתֹ֨ן תִּתֵּ֤ן לָהֶם֙ אֲחֻזַּ֣ת נַחֲלָ֔ה בְּת֖וֹךְ אֲחֵ֣י אֲבִיהֶ֑ם וְהַֽעֲבַרְתָּ֛ אֶת־נַחֲלַ֥ת אֲבִיהֶ֖ן לָהֶֽן
4. Provide More Context About Biblical Hebrew
BIBLICAL HEBREW CONTEXT:
- Ancient Near Eastern religious texts often use technical vocabulary that seems metaphorical to modern readers but was understood literally or technically
- Distinguish between:
  * Phenomenological language (describing appearances)
  * Technical cultic language (ritual/legal terms)
  * Genuine figurative language (poetic comparisons)
5. Hyperbole is overcalled. (e.g. מֵרָחֹֽק, לְמָתַ֣י) are meant literally
5. Add a "Check Yourself" Section
BEFORE MARKING AS FIGURATIVE, ASK:
1. Is this a technical religious/legal term?
2. Is this a formulaic expression common in biblical narrative?
3. Could this be understood literally in its ancient context (an ACTUAL action, place thing, etc such as in נָקוּמָה וְנֵלֵכָה וְנִֽחְיֶה וְלֹ֣א נָמ֔וּת)?
4. Is this describing actual ritual practice or law?
If YES to any → likely NOT figurative, substantially reduce confidence.
5. If confidence is less than 0.7, do not label as figurative language.

The core issue is that the LLM is applying modern literary analysis to ancient technical religious texts without sufficient awareness of genre conventions and technical vocabulary. These modifications should significantly reduce false positives while maintaining sensitivity to genuine figurative language.