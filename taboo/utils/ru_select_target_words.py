"""
    An adaptation of the original games/taboo/utils/select_taboo_words.py script for Russian data.
    --------------------------------------------------------------
    Script that generates target word lists for the TABOO game from a frequency dictionary (Russian).

    The frequency dictionary is a csv file that contains the following fields:
    СЛОВО = Word
    РАНГ = Rank
    ОНТНОСИТЕЛЬНАЯ ЧАСТОТА (на 1 млн.) = Frequency per Million
    ДОКУМЕНТНАЯ ЧАСТОТА = Document Frequency
    ЛЕММЫ (по OpenCorpora) = Lemma OpenCorpora (https://opencorpora.org/)

    We are parsing this csv file, extracting lemmas and POS-tags along with the frequency values,
    filter words with the specific POS tags, extract related words based on the Russian WordNet Thesaurus,
    filter out words which have less than 3 related words extracted
    and bin the filtered words into 3 lists based on the frequency values.

    POS to keep:
        ADJF = adjective (full form)
        NOUN = noun
        INFN = verb (base form)
        ADVB = adverb
        PRED = predicative (~a state of the subject)

    POS to remove:
        CONJ = conjugation
        PREP = preposition
        PRCL = particle
        GRND = transgressive verb/converb
        NPRO = pronoun
        INTJ = interjection
        NUMR = number
        ADJS = adjective (short form)
        COMP = comparative (adjective/adverb)
        PRTF = participle (full)
        PRTS = participle (short)
        VERB = conjugated verb (I-form)

    We additionally filter the words by spacy POS tags. Allowed tags: 'ADJ' (adjective), 'NOUN' (noun),
    'VERB' (verb), 'ADV' (adverb)

     Before running the script locally:
        1) download the frequency dictionary file and put it in the resources folder,
           link: https://drive.google.com/file/d/1XMcPzfDft2oOR0kzBD6KNP8qdGhLfIIN/view
        2) load the spacy model: python -m spacy download ru_core_news_sm
"""

import random
import pandas as pd
import spacy

from ru_append_related_words import extract_related_words


# Constants

RAW_DATA_FILENAME = "../resources/rus_freq_dictionary_1992-2019.csv"  # link in description above (file not in the repo!)

COLUMN_MAP = {'СЛОВО': "Word", "РАНГ": "Rank", "ОНТНОСИТЕЛЬНАЯ ЧАСТОТА (на 1 млн.)": "Frequency per Million",
              'ДОКУМЕНТНАЯ ЧАСТОТА': "Document Frequency", "ЛЕММЫ (по OpenCorpora)": "Lemma OpenCorpora"}

ALLOWED_OC_TAGS = ['ADJF', 'NOUN', 'INFN', 'ADVB', 'PRED']  # OpenCorpora tags
ALLOWED_SPACY_TAGS = ['ADJ', 'NOUN', 'VERB', 'ADV']  # spacy tags

FREQUENCY_CUTOFF_VALUE = 3  # arbitrary number

nlp = spacy.load("ru_core_news_sm")


def parse_lemma(raw_lemma: str) -> (str, str):
    """
    Parse lemma and OpenCorpora POS tag from raw data.
    :param raw_lemma: raw "Lemma OpenCorpora"/"ЛЕММЫ (по OpenCorpora)" value
    :return: tuple of lemma and POS tag
    """
    split = raw_lemma.split(',')[0].split()
    return pd.Series([split[1].strip(), split[2].strip('()')])


def tag_spacy_pos(lemma: str) -> str:
    """
    POS-tag a word with spacy.
    :param lemma: a word to tag
    :return: spacy POS tag
    """
    token = nlp(lemma)[0]
    return token.pos_


def parse_raw_data(filename: str) -> pd.DataFrame:
    """
    Read raw csv frequency dictionary, rename the columns and transform it into a pandas' dataframe.
    :param filename:
    :return: normalized raw data as pandas' dataframe
    """
    df = pd.read_csv(filename, sep='\t', usecols=range(5))  # the csv is uneven, dropping the row tails
    df.rename(columns=COLUMN_MAP, inplace=True)
    df = df.dropna()
    df[["Lemma", "POS tag"]] = df["Lemma OpenCorpora"].apply(parse_lemma)
    df.drop(columns=["Word", "Rank", "Document Frequency", "Lemma OpenCorpora"], inplace=True)
    return df


def filter_by_pos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the target word dataframe by allowed POS tags.
    :param df: dataframe to filter
    :return: filtered dataframe
    """
    # first filter: pick words with allowed OpenCorpora (oc) POS tags
    df["oc_allowed"] = df["POS tag"].map(lambda tag: tag in ALLOWED_OC_TAGS)
    df = df.where(df["oc_allowed"]).dropna()

    # the first filter is quite superficial, so here's the second filter - spacy POS tags
    df["spacy POS tag"] = df["Lemma"].apply(tag_spacy_pos)
    df["spacy_allowed"] = df["spacy POS tag"].map(lambda tag: tag in ALLOWED_SPACY_TAGS)
    df = df[df["spacy_allowed"]]
    return df


def extract_words_frequencies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract lemmas and word frequencies from the raw dataframe and group entries by lemma.
    :param df: raw dataframe
    :return: dataframe with 2 columns: Lemma and Document Frequency
    """
    # select words with allowed POS tags
    df_filtered = filter_by_pos(df)

    # group by lemma and aggregate frequencies of each entry
    df_grouped = df_filtered.groupby('Lemma')["Frequency per Million"].sum().reset_index()

    # save extracted words and frequencies as transitional state (due to time-consuming extraction)
    # df.to_json('df_taboo_full.json', orient='records', lines=True)

    return df_grouped


def export_target_words(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort and filter the target words based on frequency (>3 occurences per Million)
    and filter out words which have no related words in RuWordNet.
    :param df: dataframe with 2 columns: Lemma and Document Frequency
    :return: dataframe with target words and their frequencies
    """
    df["Frequency per Million"] = round(df["Frequency per Million"], 2)
    df = df.sort_values(by=["Frequency per Million"], ascending=False)

    df = df[df["Frequency per Million"] >= FREQUENCY_CUTOFF_VALUE]  # remove tail with least frequent words

    related_words = extract_related_words(df["Lemma"])
    filtered_df = df[df["Lemma"].isin(related_words.keys())]

    filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df


def write_stats(df: pd.DataFrame):
    """
    Write some word stats after binning into a txt file for future reference.
    """
    one_third = int(df.shape[0] / 3)
    two_thirds = df.shape[0] - one_third

    with open("../resources/data_stats.txt", "w") as o:
        o.write(f"Total words: {df.shape[0]}\n")
        o.write(f"High frequency: {df.loc[one_third, "Frequency per Million"]} occurrences per million and more, "
                f"{one_third} words\n")
        o.write(f"Medium frequency: from"
                f" {df.loc[one_third+1, "Frequency per Million"]} down to {df.loc[two_thirds, "Frequency per Million"]}"
                f" occurrences per million, {two_thirds-one_third} words.\n")
        o.write(f"Low frequency: "
                f"{df.loc[two_thirds+1, "Frequency per Million"]} down to {FREQUENCY_CUTOFF_VALUE}"
                f" occurrences per million, {df.shape[0] - two_thirds} words\n")


def create_word_lists(df: pd.DataFrame):
    """
    Bin target words into 3 equal groups, randomly choose 100 words out of each group
    and write them into files (high, medium and low frequency words).
    :param df: dataframe of target words with 2 columns: Lemma and Document Frequency
    """
    write_stats(df)

    one_third = int(df.shape[0] / 3)
    two_thirds = df.shape[0] - one_third

    # choose random 100 words from the index
    high_freq_100 = random.choices(df[:one_third].index, k=100)
    med_freq_100 = random.choices(df[one_third+1:two_thirds].index, k=100)
    low_freq_100 = random.choices(df[two_thirds+1:].index, k=100)

    with open("../resources/low_freq_100.txt", "w", encoding='utf-8') as o:
        for w in df.loc[low_freq_100, "Lemma"]:
            o.write(f"{w}\n")

    with open("../resources/medium_freq_100.txt", "w", encoding='utf-8') as o:
        for w in df.loc[med_freq_100, "Lemma"]:
            o.write(f"{w}\n")

    with open("../resources/high_freq_100.txt", "w", encoding='utf-8') as o:
        for w in list(df.loc[high_freq_100, "Lemma"]):
            o.write(f"{w}\n")


if __name__ == "__main__":
    # df_freq = parse_raw_data(RAW_DATA_FILENAME)
    # df_taboo = extract_words_frequencies(df_freq)
    df_taboo = pd.read_json('df_taboo_full.json', orient='records', lines=True)
    df_target_words = export_target_words(df_taboo)
    create_word_lists(df_target_words)
