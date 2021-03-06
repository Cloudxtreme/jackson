import nltk
from nltk.corpus import brown

class PhraseExtractor:
    def extract(self, tree):
        nouns = self.extract_nouns(tree)
        adjectives = self.extract_adjectives(tree)

        return {
            'nouns': set(nouns[0]),
            'noun_phrases': nouns[1],
            'adjectives': adjectives[0],
            'adjective_phrases': adjectives[1]
        }

    def _is_used_as_noun(self, text):
        if len(text) == 1:
            if text[-3:] == 'est':
                most_common_usage = self._get_most_common_usage(text)

                return 'NN' in most_common_usage[0]
        else:
            if text[-3:] == 'est':
                return False

        return True

    def extract_nouns(self, tree):
        nouns = set()
        noun_phrases = set()
        for node in tree:
            if hasattr(node, 'label'):
                node_text = ' '.join(node.leaves())
                node_label = node.label()

                if 'NN' in node_label\
                        and self._is_used_as_noun(node_text):
                    nouns.add(node_text)
                if node_label == 'NP'\
                        and self._is_used_as_noun(node_text):
                    noun_phrases.add(node_text)

                nouns_and_phrases = self.extract_nouns(node)
                nouns.update(nouns_and_phrases[0])
                noun_phrases.update(nouns_and_phrases[1])

        return nouns, noun_phrases

    def extract_adjectives(self, tree):
        adjectives = set()
        adjective_phrases = set()
        for node in tree:
            if hasattr(node, 'label'):
                node_label = node.label()
                node_text = ' '.join(node.leaves())

                if node_label == 'ADJP':
                    adjective_phrases.add(node_text)
                if 'JJ' in node_label:
                    adjectives.add(node_text)

                adjectives_and_phrases = self.extract_adjectives(node)
                adjectives.update(adjectives_and_phrases[0])
                adjective_phrases.update(adjectives_and_phrases[1])

        return adjectives, adjective_phrases

    def _get_most_common_usage(self, word):
        return nltk.FreqDist(
                word_type for word, word_type in brown.tagged_words()
                if word.lower() == word)\
            .most_common(1)