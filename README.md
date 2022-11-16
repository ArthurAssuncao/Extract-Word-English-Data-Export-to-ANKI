# Extract Word English Data, like phonetics, audio and examples and Export to ANKI

This project extract word data from Dictionaryapi.dev and Dictionary.cambridge.org and generate anki export file in csv.

## Screenshots

<p align="center">
    <img src="https://raw.githubusercontent.com/ArthurAssuncao/extract-english-phonetics-audio-export-anki/main/screenshots/screenshot-1.jpeg" width="300px" />

  <img src="https://raw.githubusercontent.com/ArthurAssuncao/extract-english-phonetics-audio-export-anki/main/screenshots/screenshot-2.jpeg" width="300px" />
</p>

## How to Use

1. Create account in AnkiWeb and download Anki desktop.
2. Install AnkiDroid in your phone.
3. Create a word list file, like Word List example below.
4. Execute crawler-words.py
5. Export word-list.csv to Anki.
6. Customize your anki with `anki-style.css`, `anki-html-front.html` and `anki-html-back.html` files.

### Word List example
```csv
Thought;Pensamento / Ideia
Though;Mas / Embora / Entretando
Tough;"Forte / Determinado / Resistente / Duro / Severo / Difícil"
Through;Através
Thorough;Detalhado / Minucioso
Throughout;Inteiramente / Por toda a parte / Durante a duração de um tempo determinado
Although;Apesar
```

### Anki export file example
```csv
# separator:Semicolon
# html:false
# tags:th-palavras-similares
# columns:Front Back Phonetic GrammaticalClasses Synonyms Antonyms Meanings
# deck:english-th-palavras-similares
Thought [sound:thought-us.mp3];Pensamento, Ideia;/θɔt/, /θɔːt/;verb, noun;guess;;<p class='example'>verb: I tend to think of her as rather ugly.</p><p class='example'>verb: Idly, the detective <span class='word-in-example'>thought</span> what his next move should be.</p><p class='example'>noun: Traditional eastern <span class='word-in-example'>thought</span> differs markedly from that of the west.</p><p class='example'>noun: The greatest weapon against stress is our ability to choose one <span class='word-in-example'>thought</span> over another.</p><p class='example'>verb: I <span class='word-in-example'>thought</span> for three hours about the problem and still couldn’t find the solution.</p><p class='example'>verb: At the time i <span class='word-in-example'>thought</span> his adamant refusal to give in right.</p><p class='example'>verb: I think she’ll pass the examination.</p><p class='example'>noun: Without freedom of <span class='word-in-example'>thought</span> there can be no such thing as wisdom, and no such thing as public liberty without freedom of speech.</p>
Though [sound:though-us.mp3];Mas, Embora, Entretando;/ðəʊ/, /ðoʊ/;adverb, conjunction;yet, all the same, even though, still, even so, although, anyway, in any case, nevertheless, anyhow, nonetheless;;"<p class='example'>adverb: ""man, it's hot in here."" — ""isn't it, <span class='word-in-example'>though</span>?""</p><p class='example'>conjunction: We shall be not sorry <span class='word-in-example'>though</span> the man die tonight.</p><p class='example'>conjunction: <span class='word-in-example'>though</span> it’s risky, it’s worth taking the chance.</p><p class='example'>adverb: I will do it, <span class='word-in-example'>though</span>.</p>"
Tough [sound:tough-us.mp3];Forte, Determinado, Resistente, Duro, Severo, Difícil;/tʌf/;verb, interjection, noun, adjective;;;<p class='example'>interjection: If you don't like it, <span class='word-in-example'>tough</span>!</p><p class='example'>noun: They were doing fine until they encountered a bunch of <span class='word-in-example'>tough</span>s from the opposition.</p><p class='example'>adjective: He had a reputation as a <span class='word-in-example'>tough</span> negotiator.</p><p class='example'>adjective: The tent, made of <span class='word-in-example'>tough</span> canvas, held up to many abuses.</p><p class='example'>adjective: This is a <span class='word-in-example'>tough</span> crowd.</p><p class='example'>adjective: To soften a <span class='word-in-example'>tough</span> cut of meat, the recipe suggested simmering it for hours.</p><p class='example'>adjective: Only a <span class='word-in-example'>tough</span> species will survive in the desert.</p><p class='example'>adjective: A bunch of the <span class='word-in-example'>tough</span> boys from the wrong side of the tracks threatened him.</p>
Through [sound:through-1-us.mp3];Através;/θɹu/, /θɹuː/;adverb, noun, preposition, adjective;;;<p class='example'>adverb: The american army broke <span class='word-in-example'>through</span> at st. lo.</p><p class='example'>adverb: The arrow went straight <span class='word-in-example'>through</span>.</p><p class='example'>adverb: He said he would see it <span class='word-in-example'>through</span>.</p><p class='example'>adjective: The <span class='word-in-example'>through</span> flight <span class='word-in-example'>through</span> memphis was the fastest.</p><p class='example'>preposition: I went <span class='word-in-example'>through</span> the window.</p><p class='example'>adverb: Leave the yarn in the dye overnight so the color soaks <span class='word-in-example'>through</span>.</p><p class='example'>adjective: After being implicated in the scandal, he was <span class='word-in-example'>through</span> as an executive in financial services.</p><p class='example'>adjective: She was <span class='word-in-example'>through</span> with him.</p><p class='example'>adjective: They were <span class='word-in-example'>through</span> with laying the subroof by noon.</p><p class='example'>adverb: Others slept / he worked straight <span class='word-in-example'>through</span>.</p><p class='example'>preposition: This team believes in winning <span class='word-in-example'>through</span> intimidation.</p><p class='example'>preposition: From 1945 <span class='word-in-example'>through</span> 1991 / the numbers 1 <span class='word-in-example'>through</span> 9 / your membership is active <span class='word-in-example'>through</span> march 15, 2013</p><p class='example'>adjective: Interstate highways form a nationwide system of <span class='word-in-example'>through</span> roads.</p><p class='example'>preposition: I drove <span class='word-in-example'>through</span> the town at top speed without looking left or right.</p><p class='example'>preposition: We slogged <span class='word-in-example'>through</span> the mud for hours before turning back and giving up.</p>
Thorough [sound:thorough-us.mp3];Detalhado, Minucioso;/ˈθɜɹoʊ/, /ˈθʌɹə/;noun, preposition, adjective;rigorous, downright, scrupulous, comprehensive, unmitigated, outright;;adjective: He is the most <span class='word-in-example'>thorough</span> worker i have ever seen.
Throughout [sound:throughout-us.mp3];Inteiramente, Por toda a parte, Durante a duração de um tempo determinado;[θɹuːˈʷaʊt], /θɹuˈʌʊt/;adverb, preposition;amidst, across, during;;<p class='example'></p>
Although [sound:although-us.mp3];Apesar;/ɔːlˈðəʊ/, /ɑlˈðoʊ/;conjunction;even if, even though, albeit, notwithstanding;;<p class='example'>conjunction: It was difficult, <span class='word-in-example'>although</span> not as difficult as we had expected.</p><p class='example'>conjunction: <span class='word-in-example'>although</span> it was very muddy, the football game went on.</p>

```

### Using convert-csv-to-anki-csv.py

If you want use my template with another propose, try this utilitary, because it converts a CSV data to my model ANKI CSV data.

#### Example

Imagine you have a directory `in-on-at` with a csv file like below. You want to transfort this csv in anki csv using my model. My model uses seven columns, how as follows:
1. Word + sound
2. Translation
3. Pronunciation
4. Grammatical class
5. Synonyms
6. Antonyms
7. Example Phrases

For this, use the `convert-csv-to-anki-csv.py` utilitary adding a json config file in words dir.


##### CSV example
```csv
Com a palavra night, midnight and noon;<p><strong>Com a palavra night, midnight and noon</strong></p><p style='font-size:12px'>Alex was on the window seat when she returned, gazing out __ the night.</p>;at;Alex was on the window seat when she returned, gazing out at the night.;Alex was on the window seat when she returned, gazing out __ the night.;Alex was on the window seat when she returned, gazing out <span class='word-in-example'>at</span> the night.;preposition;IN, ON or AT
Com a palavra table;<p><strong>Com a palavra table</strong></p><p style='font-size:12px'>As soon as they were settled __ a table, Felipa lay out her plan.</p>;at;As soon as they were settled at a table, Felipa lay out her plan.;As soon as they were settled __ a table, Felipa lay out her plan.;As soon as they were settled <span class='word-in-example'>at</span> a table, Felipa lay out her plan.;preposition;IN, ON or AT
```

##### JSON example
```json
{
    "word_sound": 1,
    "translation_pt": 2,
    "pronunciation": 7,
    "class": 6,
    "synonyms": null,
    "antonyms": null,
    "phrases": 5
}
```

##### ANKI CSV Result
```csv
# separator:Semicolon
# html:true
# tags:in-on-at
# columns:Front Back Phonetic GrammaticalClasses Synonyms Antonyms Meanings
# deck:english-in-on-at
<p><strong>Com a palavra night, midnight and noon</strong></p><p style='font-size:12px'>Alex was on the window seat when she returned, gazing out __ the night.</p>;at;IN, ON or AT;preposition;;;Alex was on the window seat when she returned, gazing out <span class='word-in-example'>at</span> the night.
<p><strong>Com a palavra table</strong></p><p style='font-size:12px'>As soon as they were settled __ a table, Felipa lay out her plan.</p>;at;IN, ON or AT;preposition;;;As soon as they were settled <span class='word-in-example'>at</span> a table, Felipa lay out her plan.
```

