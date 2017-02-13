from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus.reader.wordnet import WordNetError

class Lemmatizer():
    ERROR_FORMAT = 'ERROR in Lemmatizer: {error}, returning {value}'
    LEMMA_KEY_FORMAT = '{word}.{part_of_speech}'
    SYNSET_KEY_FORMAT = '{lemma}.{part_of_speech}.01'

    def __init__(self):
        #Ensuring that the wordnet corpus is loaded, so we can support multithreading
        wn.ensure_loaded()

        self.lemmatizer = WordNetLemmatizer()
        self.lemmas_dict = {}
        self.synsets_dict = {}

    def get_lemmas(self, word, part_of_speech):
        try:
            part_of_speech = self._translate_part_of_speech(part_of_speech)
            synset = wn.synset(word+ '.' + part_of_speech + '.01')

            if not synset:
                return []

            return synset.lemmas()
        except WordNetError:
            return [word]

    def lemmatize(self, word, part_of_speech):
        try:
            part_of_speech = self._translate_part_of_speech(part_of_speech)
            lemmas = self.lemmatizer.lemmatize(word, part_of_speech)
            return lemmas
        except WordNetError:
            return word

    def get_synonyms(self, word, part_of_speech, threshold):
        try:
            lemma = self.lemmatizer.lemmatize(word, part_of_speech)
            default_synset = wn.synset(lemma + '.' + part_of_speech + '.01')
            synsets = wn.synsets(lemma)
            synonyms = []
            for synset in synsets:

                path_similarity = synset.path_similarity(default_synset)
                if path_similarity\
                        and path_similarity >= threshold\
                        and synset.pos() == part_of_speech:
                    synset_name = synset.name().split('.')[0]
                    synonyms.append(synset_name)

            return synonyms

        except WordNetError:
            return []

    def get_similarity(self, first_word, second_word, part_of_speech):
        first_word_synset = self._get_synset(first_word, part_of_speech)
        second_word_synset = self._get_synset(second_word, part_of_speech)

        if not first_word_synset or not second_word_synset:
            return 0

        return first_word_synset.path_similarity(second_word_synset) or 0

    def _get_synset(self, word, part_of_speech):
        try:
            lemma = self._get_lemma(word, part_of_speech)
            synset_key = Lemmatizer.SYNSET_KEY_FORMAT.format(
                lemma=lemma,
                part_of_speech=part_of_speech
            )

            if synset_key not in self.synsets_dict.keys():
                self.synsets_dict[synset_key] = wn.synset(synset_key)

        except WordNetError:
            self.synsets_dict[synset_key] = None

        return self.synsets_dict[synset_key]

    def _get_lemma(self, word, part_of_speech):
        key = Lemmatizer.LEMMA_KEY_FORMAT.format(
            word=word,
            part_of_speech=part_of_speech
        )

        if key not in self.lemmas_dict.keys():
            try:
                self.lemmas_dict[key] = self.lemmatizer.lemmatize(word, part_of_speech)
            except WordNetError:
                self.lemmas_dict[key] = word

        return self.lemmas_dict[key]

    def _translate_part_of_speech(self, part_of_speech):
        parts_of_speech = {
            'verb': 'v',
            'v': 'v',
            'noun': 'n',
            'n': 'n',
            'adj': 'a',
            'a': 'a',
            'adjective': 'a'
        }

        if part_of_speech.lower() not in list(parts_of_speech.keys()):
            raise ValueError('part_of_speech must be in ', list(parts_of_speech.keys()))

        return parts_of_speech.get(part_of_speech.lower())