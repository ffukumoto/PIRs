import utils.file_tool as file_tool
import corpus.base_corpus as base_corpus
import utils.parser_tool as parser_tool
import utils.general_tool as general_tool
import random
import time
import matplotlib.pyplot as plt
import numpy as np


single_mrpc_obj = None


class Qqp(base_corpus.Corpus):
    def __init__(self):
        self.max_sent_len = 0
        super().__init__()


    data_path = 'corpus/qqp'

    def __extra_examples_from_org_file__(self, org_file, des_filename):
        if file_tool.check_file(des_filename):
            examples_dicts = file_tool.load_data_pickle(des_filename)
            return examples_dicts
        example_dicts = []
        rows = file_tool.read_tsv(org_file)
        for i, row in enumerate(rows):
            if i == 0:
                continue
            if i == 0:
                continue

            if len(row) != 6:
                raise RuntimeError

            example_temp = {
                'qes_id1': int(row[1]),
                'qes1': str(row[3]).strip(),
                'qes_id2': int(row[2]),
                'qes2': str(row[4]).strip(),
                'label': int(row[5]),
                'id': int(row[0]),
            }
            example_dicts.append(example_temp)

        file_tool.save_data_pickle(example_dicts, des_filename)
        return example_dicts

    def __divide_example_dicts_to_train_and_test__(self, example_dicts):
        positive_exa_dicts = []
        negative_exa_dicts = []
        test_example_dicts = []
        train_id_set = set()
        test_id_set = set()
        sample_count = 5000
        for e in example_dicts:
            label = int(e['label'])
            if label == 0:
                negative_exa_dicts.append(e)
            elif label == 1:
                positive_exa_dicts.append(e)
            else:
                raise ValueError("error label")
        # pos_sample_indexes = random.sample([i for i in range(len(positive_exa_dicts))], sample_count)
        # neg_sample_indexes = random.sample([i for i in range(len(negative_exa_dicts))], sample_count)

        for i in range(sample_count):
            pos_index = random.randint(0, len(positive_exa_dicts)-1)
            test_example_dicts.append(positive_exa_dicts.pop(pos_index))

            neg_index = random.randint(0, len(negative_exa_dicts)-1)
            test_example_dicts.append(negative_exa_dicts.pop(neg_index))

        train_example_dicts = positive_exa_dicts.copy()
        train_example_dicts.extend(negative_exa_dicts)

        for e in test_example_dicts:
            test_id_set.add(e['id'])

        for e in train_example_dicts:
            train_id_set.add(e['id'])

        for test_id in test_id_set:
            if test_id in train_id_set:
                raise ValueError

        if (len(train_id_set) != len(train_example_dicts)) or (len(test_id_set) != len(test_example_dicts)):
            raise ValueError

        if len(test_example_dicts) != 2*sample_count:
            raise ValueError

        if len(train_example_dicts) + len(test_example_dicts) != len(example_dicts):
            raise ValueError

        negative_count = 0
        positive_count = 0
        for e in test_example_dicts:
            if int(e['label']) == 0:
                negative_count += 1
            else:
                positive_count += 1
        if (negative_count != positive_count) or (negative_count != sample_count):
            raise ValueError

        return train_example_dicts, test_example_dicts

    def create_examples(self):
        def create_examples_by_dicts(examples):
            example_obj_list = []
            example_obj_dict = {}
            repeat_qes_exam_list = []
            for e in examples:
                id_ = str(e['id'])
                label = int(e['label'])
                qes1_id = str(e['qes_id1'])
                qes2_id = str(e['qes_id2'])

                if (qes1_id not in self.sentence_dict) or (qes2_id not in self.sentence_dict):
                    print('example id {} q1 id {} q2 id {} is invalid'.format(id_, qes1_id, qes2_id))
                    continue

                sent_obj1 = self.sentence_dict[qes1_id]
                sent_obj2 = self.sentence_dict[qes2_id]

                if (e['qes1'] != sent_obj1.original_sentence()) or (e['qes2'] != sent_obj2.original_sentence()):
                    raise ValueError("sentence load error")

                example_obj = base_corpus.Example(id_, sentence1=sent_obj1, sentence2=sent_obj2, label=label)

                if id_ in example_obj_dict:
                    raise ValueError("example in corpus is repeated")

                if example_obj.sentence1 == example_obj.sentence2:
                    raise ValueError("example in corpus is repeated")

                if example_obj.sentence1.id == example_obj.sentence2.id:
                    raise ValueError("example in corpus is repeated")

                if example_obj.sentence1.original == example_obj.sentence2.original:
                    # raise ValueError("example in corpus is repeated")
                    repeat_qes_exam_list.append(example_obj)

                example_obj_list.append(example_obj)
                example_obj_dict[id_] = example_obj

            if len(example_obj_list) != len(example_obj_dict):
                raise ValueError("example in corpus is repeated")

            print("repeat question example count:{}".format(len(repeat_qes_exam_list)))
            return example_obj_list, example_obj_dict

        example_dicts = self.__extra_examples_from_org_file__(
                                file_tool.connect_path(self.data_path, 'data.tsv'),
                                file_tool.connect_path(self.data_path, 'example_dicts.pkl'))

        train_dicts, test_dicts = self.__divide_example_dicts_to_train_and_test__(example_dicts)

        self.train_example_list, self.train_example_dict = create_examples_by_dicts(train_dicts)

        self.test_example_list, self.test_example_dict = create_examples_by_dicts(test_dicts)

        for e_id in self.test_example_dict.keys():
            if e_id in self.train_example_dict:
                raise ValueError("example {} in both test and train".format(e_id))

        pass

    def __extra_sentences_from_org_file__(self, org_file, des_filename):
        if file_tool.check_file(des_filename):
            sentence_dict = file_tool.load_data_pickle(des_filename)
            return sentence_dict
        sentence_dict = {}
        rows = file_tool.load_data(org_file, mode='r')
        for i, row in enumerate(rows):
            result = row.split("\t")
            if i == 0:
                continue
            if len(result) != 6:
                raise RuntimeError

            if not general_tool.is_number(result[1]):
                raise RuntimeError

            if not general_tool.is_number(result[2]):
                raise RuntimeError

            if str(result[3]).strip() == '':
                print('empty sentence id:{}'.format(str(result[1]).strip()))
            else:
                sentence_dict[str(result[1]).strip()] = str(result[3]).strip()

            if str(result[4]).strip() == '':
                print('empty sentence id:{}'.format(str(result[2]).strip()))
                continue
            else:
                sentence_dict[str(result[2]).strip()] = str(result[4]).strip()

        file_tool.save_data_pickle(sentence_dict, des_filename)
        return sentence_dict

    def create_sentences(self):
        original_sentence_dict = self.__extra_sentences_from_org_file__(
                                file_tool.connect_path(self.data_path, 'data.tsv'),
                                file_tool.connect_path(self.data_path, 'original_sentence_dict.pkl'))
        self.sentence_list = []
        self.sentence_dict = {}
        for sent_id, o_sent in original_sentence_dict.items():
            sent_id = int(sent_id)
            sent_obj = base_corpus.Sentence(id_=sent_id, original_sentence=o_sent)
            self.sentence_list.append(sent_obj)
            if str(sent_id) in self.sentence_dict:
                raise ValueError("sentence in corpus is repeated")
            self.sentence_dict[str(sent_id)] = sent_obj
        if len(self.sentence_dict) != len(self.sentence_list):
            raise ValueError("sentence in corpus is repeated")

        pass

    def parse_sentences(self):
        parsed_sentence_org_file = file_tool.connect_path(self.data_path, 'parsed_sentences.txt')
        parsed_sentence_dict_file = file_tool.connect_path(self.data_path, 'parsed_sentence_dict.pkl')
        if file_tool.check_file(parsed_sentence_dict_file):
            parsed_sentence_dict = file_tool.load_data_pickle(parsed_sentence_dict_file)
        else:
            parsed_sentence_dict = parser_tool.extra_parsed_sentence_dict_from_org_file(parsed_sentence_org_file)
            file_tool.save_data_pickle(parsed_sentence_dict, parsed_sentence_dict_file)

        if len(parsed_sentence_dict) != len(self.sentence_dict):
            raise ValueError("parsed_sentence_dict not march sentence_dict")

        if not general_tool.compare_two_dict_keys(self.sentence_dict.copy(), parsed_sentence_dict.copy()):
            raise ValueError("parsed_sentence_dict not march sentence_dict")

        for sent_id, info in parsed_sentence_dict.items():
            if info['original'] != self.sentence_dict[sent_id].original:
                raise ValueError("parsed_sentence_dict not march sentence_dict")

        for sent_id, parse_info in parsed_sentence_dict.items():
            sent_id = str(sent_id)
            self.sentence_dict[sent_id].parse_info = parse_info

        self.parse_info = parser_tool.process_parsing_sentence_dict(parsed_sentence_dict, modify_dep_name=True)
        numeral_sentence_dict = self.parse_info.numeral_sentence_dict
        self.max_sent_len = self.parse_info.max_sent_len

        if not general_tool.compare_two_dict_keys(self.sentence_dict.copy(), numeral_sentence_dict.copy()):
            raise ValueError("numeral_sentence_dict not march sentence_dict")

        for sent_id in self.sentence_dict.keys():
            self.sentence_dict[sent_id].syntax_info = numeral_sentence_dict[sent_id]
        pass

    def __create_new_data_set__(self, example_list, filename):
        save_data = [['id', 'qid1', 'qid2', 'question1', 'question2', 'is_duplicate']]
        for e in example_list:
            save_data.append([e.id, str(e.sentence1.id), str(e.sentence2.id), str(e.sentence1.original), str(e.sentence2.original), str(e.label)])
        file_tool.write_lines_to_tsv(save_data, filename)

    def create_data(self):
        self.create_sentences()
        self.create_examples()
        self.parse_sentences()

        print('{}'.format('*' * 80))
        print('finished load orig data and create objects')
        print('sentence count:{}'.format(len(self.sentence_dict)))
        print('train example count:{}'.format(len(self.train_example_dict.keys())))
        print('test example count:{}'.format(len(self.test_example_dict.keys())))
        print('{}'.format('*' * 80), end='\n\n')

        self.modify_data()
        self.save_data()

    def modify_data(self):
        while(True):
            print("Whether deleted examples with too long sentence, y/n?")
            delete_flag = input()
            if delete_flag == 'y':
                self.__delete_examples_by_sent_len_threshold__(60)
            elif delete_flag == 'n':
                break

    def save_data(self):
        test_file = file_tool.connect_path(self.data_path, 'test.tsv')
        train_file = file_tool.connect_path(self.data_path, 'train.tsv')
        self.__create_new_data_set__(self.train_example_list, train_file)
        self.__create_new_data_set__(self.test_example_list, test_file)

    def __delete_examples_by_sent_len_threshold__(self, threshold):
        def delete_examples_from_dict(example_dict, example_ids):
            deleted_es = []
            for e_id in example_ids:
                deleted_es.append(example_dict.pop(str(e_id)))
            print("deleted {} examples".format(len(deleted_es)))
            return example_dict

        self.sent_distribute_count()

        print("length threshold is {}".format(threshold))

        train_old_count = len(self.train_example_dict)
        test_old_count = len(self.test_example_dict)

        train_delete_examples = self.__collect_examples_over_threshold__(self.train_example_list, threshold)
        test_delete_examples = self.__collect_examples_over_threshold__(self.test_example_list, threshold)

        delete_examples_from_dict(self.train_example_dict, [e.id for e in train_delete_examples])
        delete_examples_from_dict(self.test_example_dict, [e.id for e in test_delete_examples])

        self.train_example_list = list(self.train_example_dict.values())
        self.test_example_list = list(self.test_example_dict.values())

        train_count = len(self.train_example_dict)
        test_count = len(self.test_example_dict)

        if train_count + len(train_delete_examples) != train_old_count:
            raise ValueError("deleted train data error")

        if test_count + len(test_delete_examples) != test_old_count:
            raise ValueError("deleted test data error")

        for e_id in self.test_example_dict.keys():
            if e_id in self.train_example_dict:
                raise ValueError("example {} in both test and train".format(e_id))

        print('deleted {} train examples'.format(len(train_delete_examples)))
        print('deleted {} test examples'.format(len(test_delete_examples)))

        self.max_sent_len = threshold
        self.sent_distribute_count()

    def get_max_sent_len(self):
        return self.max_sent_len

    def show_pared_info(self):
        print('the count of dep type:{}'.format(self.parse_info.dependency_count))
        print('the max len of sentence_tokens:{}, correspond sent id:{}'.format(self.parse_info.max_sent_len,
                                                                                self.parse_info.max_sent_id))
        print('the average len of sentence_tokens:{}'.format(self.parse_info.avg_sent_len))
        sent_len_table = self.parse_info.sent_len_table
        file_tool.save_data_pickle(sent_len_table, file_tool.connect_path(self.data_path, "sent_len_table.pkl"))
        plt.bar(range(1, len(sent_len_table) + 1), sent_len_table)
        plt.title("sentence tokens length distribution")
        plt.show()

    def __collect_examples_over_threshold__(self, examples, threshold):
        result_examples = []
        for e in examples:
            if (e.sentence1.len_of_tokens() > threshold) or (e.sentence2.len_of_tokens() > threshold):
                result_examples.append(e)
        return result_examples

    def sent_distribute_count(self):
        sent_len_table = np.zeros(500, dtype=np.int)
        for s in self.sentence_list:
            sent_len_table[s.len_of_tokens()] += 1

        sent_count = sent_len_table.sum()
        train_count = len(self.train_example_list)
        test_count = len(self.test_example_list)
        print('count of sentence:{}'.format(sent_count))
        print('count of example:{}'.format(train_count + test_count))
        while(True):
            print('please input length threshold, "e" donate exit')
            length_threshold = input()
            if length_threshold == "e":
                break
            if not general_tool.is_number(length_threshold):
                continue

            length_threshold = int(length_threshold)
            sent_temp = sent_len_table[:length_threshold + 1].sum()
            print('sentence: {}/{}, rate:{}'.format(sent_temp, sent_count-sent_temp, round(sent_temp/sent_count, 6)))

            train_out_count = len(self.__collect_examples_over_threshold__(self.train_example_list, length_threshold))

            test_out_count = len(self.__collect_examples_over_threshold__(self.test_example_list, length_threshold))

            print('train data: {}/{}, rate:{}'.format(train_count, train_out_count,
                                                      round((train_count-train_out_count)/train_count, 6)))

            print('test data: {}/{}, rate:{}'.format(test_count, test_out_count,
                                                     round((test_count-test_out_count)/test_count, 6)))

    def sentence_dict_from_examples(self):
        sentence_dict = {}
        for e in self.train_example_dict.values():
            sentence_dict[e.sentence1.id] = e.sentence1
            sentence_dict[e.sentence2.id] = e.sentence2

        for e in self.test_example_dict.values():
            sentence_dict[e.sentence1.id] = e.sentence1
            sentence_dict[e.sentence2.id] = e.sentence2

        return sentence_dict


single_qqp_obj = None


def get_qqp_obj(force=False):

    global single_qqp_obj
    if force or (single_qqp_obj is None):
        single_qqp_obj_file = file_tool.connect_path("corpus/qqp", 'qqp_obj.pkl')
        if file_tool.check_file(single_qqp_obj_file):
            single_qqp_obj = file_tool.load_data_pickle(single_qqp_obj_file)
        else:
            single_qqp_obj = Qqp()
            file_tool.save_data_pickle(single_qqp_obj, single_qqp_obj_file)

    return single_qqp_obj


def show_sent_len_distribute():
    sent_len_table = file_tool.load_data_pickle(file_tool.connect_path(Qqp.data_path, 'sent_len_table.pkl'))
    plt.bar(range(1, len(sent_len_table) + 1), sent_len_table)
    plt.title("")
    plt.xlabel('sentence length')
    plt.ylabel('count')
    plt.xlim(0, 80)
    plt.show()

def test():
    # start = time.time()
    # qqp = get_qqp_obj()
    # Qqp.show_pared_info(qqp)
    # qqp.sent_distribute_count()
    # end = time.time()
    # print(end-start)
    # qqp = get_qqp_obj()
    # qqp = get_qqp_obj()
    show_sent_len_distribute()

if __name__ == '__main__':
    test()