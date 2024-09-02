# From Wordle to Вордли: a step-by-step guide to porting Wordle into Russian (and hopefully other languages)

## Introduction
This guide provides a step-by-step process for adapting the Wordle game for [clembench](https://github.com/clp-research/clembench).
The goal of this guide is to help you replicate the process of selecting the correct data for a Russian version
of the game. Moreover, this guide attempts to provide some universal tips to port the game to the language of your choice.

## Understanding the original Wordle clemgame

### Game Overview

In clem-Wordle, a cLLM (Player A) attempts to guess a five-letter word in six attempts, guided by feedback on letter positions from a deterministic bot (Player B). 
The game evaluates three aspects of cLLM performance: rule comprehension (valid five-letter words), effective use of feedback, and speed in guessing the target word.

There are three game variations:

 - **Traditional Wordle:** cLLM serves as the Guesser (Player A), with feedback provided by a deterministic bot (Player B).

 - **Wordle with Semantic Clue:** Guesser receives a clue before guessing, such as "pack of lions" for the word "PRIDE" testing how well the cLLM uses this additional information.

 - **Wordle with Semantic Clue and Critic:** Guesser receives a clue before guessing AND after each guess, a "critic" evaluates the guess's correctness and provides feedback. The Guesser can adjust its guess based on the critic's input, exploring the influence of this additional feedback on guessing accuracy.

The game ends when the Guesser guesses correctly OR after six attempts.

For more details, go to the [original repo documentation](https://github.com/clp-research/clembench/blob/main/docs/wordle.md) and 
the [clembench-2023 paper](https://aclanthology.org/2023.emnlp-main.689.pdf) (Section 4.2 and Appendix D)

### Data Sources and Selection Process
- **Target words:** [a list of 2,309 possible target words](https://github.com/3b1b/videos/blob/master/_2022/wordle/data/possible_words.txt). After sorting these words by frequency,
 1 word without frequency data and 39 words without available semantic clues were excluded, leaving **2,269 target words**.
These were then divided into three equal groups based on descending frequency (frequency ↓ ⇒ difficulty ↑).
- **Allowed words:** [a list of 12,953 valid guess words](https://github.com/3b1b/videos/blob/master/_2022/wordle/data/allowed_words.txt)
- **Frequency dictionary:** [English Word Frequency Dictionary](https://www.kaggle.com/datasets/rtatman/english-word-frequency)
- **Semantic clues:** [New York Times Crossword Clues & Answers 1993-2021](https://www.kaggle.com/datasets/darinhawley/new-york-times-crossword-clues-answers-19932021)

## General approach to the game localization

- #### Step 0: Research the game
Wordle has become a pretty popular game and has been adapted for multiple languages and domains. 
[This resource](https://rwmpelstilzchen.gitlab.io/wordles/) provides a comprehensive overview on many different instances.

And of course, based on your target language, you should adapt the game premise. For example, Tamil script is syllabic,
compound symbols adds up to over 200 options, and players are confronted with far too many options to win in under six guesses ([source](https://restofworld.org/2022/wordle-viral-turkish-japanese-tamil-portuguese/)).


- #### Step 1: Find a data source for the target & allowed words
There is a good chance that the game is already implemented for your target language and you can use its source data (if it's available and permitted, of course). 
If it's not the case, you can build your own wordlists based on, for example, [Wiktionary's word frequency lists](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists) 
or search for a cheat sheet for five-letter [Scrabble](https://en.wikipedia.org/wiki/Scrabble) answers.

- #### Step 2: Find a data source for the semantic clues
In the original implementations, the authors used a dataset of crossword clues. This is quite specific data, 
there can be no such readily available data for your target language.
You can build you own clue dictionary based on specialized websites (see the example below in the Case Study section).
Alternatively, it can be worth using Wiktionary's word definitions as clues ([example](https://en.wiktionary.org/wiki/game#Noun)), 
because good descriptions rarely contain circular dependency and don't mention the word they describe or its parts.

- #### Step 3: Prepare target words
- **Accumulate**: compile a list of possible target words
- **Filter:** pick words which make sense for the game (for example, keep only those words that have frequency data and/or a connected sematic clue).
- **Categorize:** Sort and divide the word list into low, medium, and high-frequency groups.
- **Review:**: Manually review the sampled words to ensure they do not include inappropriate or culturally irrelevant terms.

- #### Step 4: Prepare allowed words

Compile a list of possible guess words, make sure that all target words are in the list.

- #### Step 5: Translate game prompts
Translate all game prompts you plan to use into the target language. The original game has 4 prompts: 
`guess_prompt.json`, `guess_prompt_with_clue.json`, `guess_prompt_with_critic.json`, `critic_prompt.json`

Google Translate does a pretty good job, if you don't speak the target language you can use it or ask for help from a (native) speaker.

- #### Step 6: Create game instances for clembench
TODO

Now, you can run the benchmark :)

### Common Challenges and How to Overcome Them

### Useful data resources
- [Wordles of the World: a comprehensive list of Wordle-like games and resources online](https://rwmpelstilzchen.gitlab.io/wordles/)
- [Wordle Global (64 languages)](https://wordle.global/)
- [Article: What it takes to bring the viral game into other languages](https://restofworld.org/2022/wordle-viral-turkish-japanese-tamil-portuguese/)

## Case Study: Russian

#### Step 0: Research the game
Wordle is a widely known game among the Russian speaking people and it received a bunch of adaptations form the enthusiasts.
It does make sense to continue using five-letter words as targets and limit the attempt number to 6,
in this regard Russian doesn't differ much from English.
(according to [this article](https://arxiv.org/pdf/1208.6109), average modern word length is 5.1 in English vs 5.28 in Russian).

There is an implemetation of an [optimal Wordle solver](https://github.com/Darxor/wordle-ru-algorithm?ysclid=m030rocj7851585255), the algorithm solves the game after 3.5 attempts on average.

#### Step 1: Find a data source for the target & allowed words
I have decided to go down the path of least resistance: I have combined all openly available data I have found
when I searched for the Russian Wordle implementations in the web.

Here are the sources I used:
- [Stategy optimization algorithm for the Russian Wordle](https://github.com/Darxor/wordle-ru-algorithm?ysclid=m030rocj7851585255):
this repo contains data from the [most popular Russian Wordle](https://wordle.belousov.one/), both target words and valid guesses.
- [Another implementation of Wordle](https://github.com/ronanru/wordle-ru): freely available data
- [Rudle](https://rudle.vercel.app/): the data is stored in the website's source code:
*Inspect Element* -> *Sources* ->`top/rudle.vercel.app/static/js/validGuesses.ts & wordlist.ts`
- [Словль/Slovl](https://timmarinin.net/slovl/): the data is stored in the website's source code:
*Inspect Element* -> *Sources* ->`top/timmarinin.net/slovl/src/guesswords.ts & answerwords.ts`

To divide the target words by difficulty, the original game depended on a word frequency dictionary. I have picked the biggest 
[Russian word frequency dictionary](http://dict.ruslang.ru/freq.php).

#### Step 2: Find a data source for the semantic clues
The original game relies on the dataset of [New York Times Crossword Clues & Answers 1993-2021](https://www.kaggle.com/datasets/darinhawley/new-york-times-crossword-clues-answers-19932021)
to extract semantic clues. 

I haven't managed to find any similar dataset for Russian, but what I did find is a [website](https://www.graycell.ru/) hosting a huge database
of crossword clues and answers. There is no API, so I have written a web scraper (TODO hyperlink).

I have extracted all five-letter words and their first definition/clue into a dictionary and saved it as a json file. 
The format is `{word1: clue1, word2: clue2, ...}`. This yielded **8268 entries**.

### Step 3: Prepare target words
- **Accumulate**: I have combined wordlists from all data sources (as a union of sets), it resulted in **4225 candidate words**.
- **Filter:** filter out words which don't have respective frequency values (leaving **2665 candidates**) and a semantic clue (leaving **2162 target words**)
- **Categorize:** Sort and equally divide the word list into low (720 words), medium (722 words), and high-frequency (720 words) groups .
- **Review:**: Manually review the sampled words to ensure they do not include inappropriate or culturally irrelevant terms.

### Step 4: Prepare allowed words

I have combined wordlists from all sources (as a union of sets), it resulted in **8390 words**.

The data preparation script can be found here: TODO

### Step 5: Translate game prompts

Location: TODO

### Step 6: Create game instances for clembench

TODO

## Summary
This guide provides a general approach for adapting the Wordle game from [clembench](https://github.com/clp-research/clembench) for other languages 
and applies it to Russian using freely available linguistic resources.

### Next steps
- verify this approach on another language (e.g. German)


