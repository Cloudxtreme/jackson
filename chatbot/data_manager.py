from information_retrieval.phrase_extractor import PhraseExtractor
from information_retrieval.summarizer import Summarizer
from preprocess.lemmatizer import Lemmatizer

summarizer = Summarizer(Lemmatizer())

class DataManager():
    ANSWER_FULL_FORMAT = '{subject} {verb} {related_nodes}.'
    ANSWER_NO_RELATIONS_FORMAT = 'I know {subject}, but I don\'t know what {subject} {verb}.'
    TITLES_PER_PHRASE = 2

    def __init__(self, text_processor, db_service, wiki_service, search_service, parser, svo_extractor):
        self.text_processor = text_processor
        self.db_service = db_service
        self.wiki_service = wiki_service
        self.search_service = search_service
        self.parser = parser
        self.svo_extractor = svo_extractor

    def try_remember(self, tokenized_sentence):
        print(tokenized_sentence)
        tree = self.parser.parse(tokenized_sentence)
        svos = self.svo_extractor.get_svos(tree)

        remembered = False

        for svo in svos:
            print(svo)
            if self.svo_extractor.is_full_svo(svo):
                relation = self.text_processor.lemmatize(svo['verb'], 'v')

                subject = self.db_service.add(
                    name=svo['subject'].lower(),
                    original_name=svo['subject'])

                object = self.db_service.add(
                    name=svo['object'].lower(),
                    original_name=svo['object'])

                self.db_service.add_relation(subject, object, relation.lower())

                remembered = True

        return remembered

    def try_answer(self, tokenized_sentence):
        tree = self.parser.parse(tokenized_sentence)
        svos = self.svo_extractor.get_svos(tree)
        answer = None
        for svo in svos:
            print(svo)
            if self.svo_extractor.is_full_sv(svo):
                self.text_processor.get_lemmas(svo['verb'], 'VERB')
                node = self.db_service.get(svo['subject'].lower())
                if node:
                    related_nodes = self.db_service.get_relations(node, svo['verb'].lower())
                    if related_nodes:
                        answer = self.ANSWER_FULL_FORMAT.format(
                            subject = svo['subject'],
                            verb = svo['verb'].lower(),
                            related_nodes = ', '.join(related_nodes)
                        )
                    else:
                        answer = self.ANSWER_NO_RELATIONS_FORMAT.format(
                            subject = svo['subject'],
                            verb = svo['verb']
                        )

        print('ANSWER: ', answer, '-'*30)

        return answer

    def get_search_phrases(self, tokenized_sentence):
        tree = self.parser.parse(tokenized_sentence)
        nj_phrases = self.svo_extractor.get_nj_phrases(tree)
        search_phrases = self.svo_extractor.get_search_phrases(nj_phrases)

        return search_phrases, nj_phrases

    def get_text_from_wiki(self, search_phrases, only_intro = False, pages_for_phrase = 1):
        print('ONLY INTRO: ', only_intro)
        page_titles = []
        for search_phrase in search_phrases:
            titles = self.wiki_service.search(search_phrase)[:pages_for_phrase]
            page_titles.extend(titles)

        print(page_titles)

        full_text = ''
        for title in page_titles:
            print('GETTING PAGE FOR TITLE: ', title)
            full_text += self.wiki_service.get(title, only_intro)
            print('GET FINISHED: ', title)

        return full_text

    def summarize_with_phrases(self, full_text, nj_phrases):
        sentences = summarizer.summarize_by_input_frequency(3, full_text, nj_phrases)
        print(sentences)

        return ' '.join(sentences)

    def answer_from_wiki(self, phrases, topic):
        sentences = []
        if topic in ['HUM', 'ABBR']:
            full_text = self.get_text_from_wiki(phrases, True)
            sentences = summarizer.summarize(3, full_text)
        else:
            search_phrases, nj_phrases = phrases
            full_text = self.get_text_from_wiki(search_phrases, False, DataManager.TITLES_PER_PHRASE)
            sentences = summarizer.summarize_by_input_frequency(3, full_text, nj_phrases)

        print(sentences)

        summary = ' '.join(sentences)

        return summary


