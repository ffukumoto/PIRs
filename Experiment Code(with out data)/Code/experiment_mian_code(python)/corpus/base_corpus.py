from abc import abstractmethod


class Example:
    def __init__(self, id_, sentence1, sentence2, label):
        self.id = id_
        self.sentence1 = sentence1
        self.sentence2 = sentence2
        self.label = label


class Sentence:
    def __init__(self, id_, original_sentence):
        self.id = id_
        self.original = original_sentence
        self.parse_info = None
        self.syntax_info = None

    def len_of_tokens(self):
        return len(self.parse_info['words'].copy())

    def word_tokens(self):
        return self.parse_info['words'].copy()

    def word_tokens_uncased(self):
        result = self.parse_info['words'].copy()
        for i, _ in enumerate(result):
            result[i] = result[i].lower()
        return result

    def original_sentence(self):
        return self.original

    def sentence_with_root_head(self):
        return 'root ' + self.original

    def original_sentence_uncased(self):
        return self.original.lower()

    def numeral_dependencies(self):
        return self.syntax_info['dependencies'].copy()


class Corpus:
    def __init__(self):
        super().__init__()
        self.train_example_dict = None
        self.train_example_list = None

        self.test_example_dict = None
        self.test_example_list = None

        self.sentence_dict = None
        self.sentence_list = None
        self.parse_info = None

        self.create_data()

    def create_data(self):
        self.create_sentences()
        self.parse_sentences()
        self.create_examples()

    @abstractmethod
    def create_examples(self):
        raise RuntimeError("have not implemented this abstract method")

    @abstractmethod
    def create_sentences(self):
        raise RuntimeError("have not implemented this abstract method")

    @abstractmethod
    def parse_sentences(self):
        raise RuntimeError("have not implemented this abstract method")

    def get_max_sent_len(self):
        return self.parse_info.max_sent_len

    def get_dep_type_count(self):
        return self.parse_info.dependency_count

    def get_sentence_by_id(self, s_id):
        sentence = self.sentence_dict[str(s_id)]
        return sentence.original

    def get_sentence_pair_by_id(self, sentence_ids):
        return self.get_sentence_by_id(sentence_ids[0]), self.get_sentence_by_id(sentence_ids[1])



