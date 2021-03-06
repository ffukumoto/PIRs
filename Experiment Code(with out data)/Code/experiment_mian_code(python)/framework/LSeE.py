import torch
import numpy as np
import framework as fr
import time
import utils.file_tool as file_tool
import utils.parser_tool as parser_tool
import utils.general_tool as general_tool

import utils.data_tool as data_tool
from model import *


class LSeE(fr.Framework):
    name = "LSeE"
    result_path = file_tool.connect_path('result', name)

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
        self.name = LSeE.name
        self.result_path = LSeE.result_path

    @classmethod
    def framework_name(cls):
        return cls.name

    def create_arg_dict(self):
        arg_dict = {
            'semantic_compare_func': 'l2',
            'fully_scales': [768 * 2, 2],
            # 'fully_regular': 1e-4,
            # 'bert_regular': 1e-4,
            'bert_hidden_dim': 768,
            'pad_on_right': True,
            'sentence_max_len_for_bert': 128,
            'dtype': torch.float32,
        }
        return arg_dict

    def update_arg_dict(self, arg_dict):
        super().update_arg_dict(arg_dict)

        if self.arg_dict['repeat_train']:
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            model_dir = file_tool.connect_path(self.result_path, 'train',
                                               'bs:{}-lr:{}-com_fun:{}'.
                                               format(self.arg_dict['batch_size'], self.arg_dict['learn_rate'],
                                                      self.arg_dict['semantic_compare_func']), time_str)

        else:
            model_dir = file_tool.connect_path(self.result_path, 'test')

        file_tool.makedir(model_dir)
        if not file_tool.check_dir(model_dir):
            raise RuntimeError
        self.arg_dict['model_path'] = model_dir

    def create_models(self):
        self.bert = BertBase()
        config = self.bert.config
        self.dropout = torch.nn.Dropout(config.hidden_dropout_prob)
        self.semantic_layer = SemanticLayer(self.arg_dict)
        self.fully_connection = FullyConnection(self.arg_dict)

    def deal_with_example_batch(self, example_ids, example_dict):
        examples = [example_dict[str(e_id.item())] for e_id in example_ids]
        sentence_max_len = self.arg_dict['sentence_max_len_for_bert']
        pad_on_right = self.arg_dict['pad_on_right']
        pad_token = self.bert.tokenizer.convert_tokens_to_ids([self.bert.tokenizer.pad_token])[0]
        sep_token = self.bert.tokenizer.convert_tokens_to_ids([self.bert.tokenizer.sep_token])[0]
        mask_padding_with_zero = True
        pad_token_segment_id = 0

        sentence1s = [e.sentence1 for e in examples]
        sentence2s = [e.sentence2 for e in examples]

        labels = torch.tensor([e.label for e in examples], dtype=torch.long, device=self.device)

        input_ids_batch = []
        token_type_ids_batch = []
        attention_mask_batch = []
        sep_index_batch = []
        sent1_len_batch = []
        sent2_len_batch = []
        sent1_org_len_batch = []
        sent2_org_len_batch = []
        word_piece_flags_batch = []
        for s1, s2 in zip(sentence1s, sentence2s):
            inputs_ls_cased = self.bert.tokenizer.encode_plus(s1.sentence_with_root_head(), s2.sentence_with_root_head(),
                                                              add_special_tokens=True,
                                                              max_length=sentence_max_len, )
            input_ids, token_type_ids = inputs_ls_cased["input_ids"], inputs_ls_cased["token_type_ids"]

            word_piece_flags_batch.append(
                general_tool.word_piece_flag_list(self.bert.tokenizer.convert_ids_to_tokens(input_ids), '##'))

            attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

            padding_length = sentence_max_len - len(input_ids)
            if not pad_on_right:
                input_ids = ([pad_token] * padding_length) + input_ids
                attention_mask = ([0 if mask_padding_with_zero else 1] * padding_length) + attention_mask
                token_type_ids = ([pad_token_segment_id] * padding_length) + token_type_ids
            else:
                input_ids = input_ids + ([pad_token] * padding_length)
                attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
                token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)

            input_ids_batch.append(input_ids)
            token_type_ids_batch.append(token_type_ids)
            attention_mask_batch.append(attention_mask)

            sep_indexes = []

            for sep_index, id_ in enumerate(input_ids.copy()):
                if id_ == sep_token:
                    sep_indexes.append(sep_index)

            if len(sep_indexes) != 2:
                raise ValueError

            sep_index_batch.append(sep_indexes[0])
            sent1_len_batch.append(sep_indexes[0] - 1)
            sent2_len_batch.append(sep_indexes[1] - sep_indexes[0] - 1)

            sent1_org_len_batch.append(s1.len_of_tokens())
            sent2_org_len_batch.append(s2.len_of_tokens())


        input_ids_batch = torch.tensor(input_ids_batch, device=self.device)
        token_type_ids_batch = torch.tensor(token_type_ids_batch, device=self.device)
        attention_mask_batch = torch.tensor(attention_mask_batch, device=self.device)

        result = {
            'input_ids_batch': input_ids_batch,
            'token_type_ids_batch': token_type_ids_batch,
            'attention_mask_batch': attention_mask_batch,
            'sep_index_batch': sep_index_batch,
            'sent1_len_batch': sent1_len_batch,
            'sent1_org_len_batch': sent1_org_len_batch,
            'word_piece_flags_batch': word_piece_flags_batch,
            'sent2_len_batch': sent2_len_batch,
            'sent2_org_len_batch': sent2_org_len_batch,
            'labels': labels
        }
        return result

    def merge_reps_of_word_pieces(self, word_piece_flags, token_reps):
        result_reps = []
        word_piece_label = False
        word_piece_rep = 0
        word_piece_count = 0
        for i, flag in enumerate(word_piece_flags):
            if flag == 1:
                word_piece_rep += token_reps[i]
                word_piece_count += 1
                word_piece_label = True
            else:
                if word_piece_label:
                    if word_piece_count == 0:
                        raise ValueError
                    result_reps.append(word_piece_rep/word_piece_count)
                    word_piece_rep = 0
                    word_piece_count = 0
                result_reps.append(token_reps[i])
                word_piece_label = False

        if word_piece_label and (word_piece_count > 0):
            result_reps.append(word_piece_rep / word_piece_count)

        result_reps = torch.stack(result_reps, dim=0)
        return result_reps

    def forward(self, *input_data, **kwargs):
        if len(kwargs) > 0:  # common run or visualization
            data_batch = kwargs
            input_ids_batch = data_batch['input_ids_batch']
            token_type_ids_batch = data_batch['token_type_ids_batch']
            attention_mask_batch = data_batch['attention_mask_batch']
            sep_index_batch = data_batch['sep_index_batch']
            word_piece_flags_batch = data_batch['word_piece_flags_batch']
            sent1_len_batch = data_batch['sent1_len_batch']
            sent2_len_batch = data_batch['sent2_len_batch']
            labels = data_batch['labels']

            # sent1_org_len_batch = data_batch['sent1_org_len_batch']
            # sent2_org_len_batch = data_batch['sent2_org_len_batch']

        else:
            input_ids_batch, token_type_ids_batch, attention_mask_batch, sep_index_batch, sent1_len_batch, \
            sent2_len_batch, labels = input_data

        last_hidden_states_batch, pooled_output = self.bert(input_ids_batch, token_type_ids_batch, attention_mask_batch)
        pooled_output = self.dropout(pooled_output)

        sent1_states_batch = []
        sent2_states_batch = []
        for i, hidden_states in enumerate(last_hidden_states_batch):
            sent1_word_piece_flags = word_piece_flags_batch[i][1:sep_index_batch[i]]
            sent1_states = hidden_states[1:sep_index_batch[i]]

            sent2_word_piece_flags = word_piece_flags_batch[i][
                                     sep_index_batch[i] + 1: sep_index_batch[i] + 1 + sent2_len_batch[i]]
            sent2_states = hidden_states[sep_index_batch[i] + 1: sep_index_batch[i] + 1 + sent2_len_batch[i]]

            if len(sent1_states) != sent1_len_batch[i] or len(sent2_states) != sent2_len_batch[i]:
                raise ValueError

            if len(sent1_states) + len(sent2_states) + 3 != attention_mask_batch[i].sum():
                raise ValueError

            if len(word_piece_flags_batch[i]) != attention_mask_batch[i].sum():
                raise ValueError

            sent1_states = self.merge_reps_of_word_pieces(sent1_word_piece_flags, sent1_states)

            # if len(sent1_states) != sent1_org_len_batch[i]:
            #     raise ValueError

            sent1_states = data_tool.padding_tensor(sent1_states, self.arg_dict['max_sentence_length'],
                                                    align_dir='left', dim=0)

            sent2_states = self.merge_reps_of_word_pieces(sent2_word_piece_flags, sent2_states)

            # if len(sent2_states) != sent2_org_len_batch[i]:
            #     raise ValueError

            sent2_states = data_tool.padding_tensor(sent2_states, self.arg_dict['max_sentence_length'],
                                                    align_dir='left', dim=0)
            sent1_states_batch.append(sent1_states)
            sent2_states_batch.append(sent2_states)

        sent1_states_batch = torch.stack(sent1_states_batch, dim=0)
        sent2_states_batch = torch.stack(sent2_states_batch, dim=0)

        result = self.semantic_layer(sent1_states_batch, sent2_states_batch)
        result = torch.cat([pooled_output, result], dim=1)

        result = self.fully_connection(result)

        loss = torch.nn.CrossEntropyLoss()(result.view(-1, 2), labels.view(-1))
        predicts = np.array(result.detach().cpu().numpy()).argmax(axis=1)

        return loss, predicts

    def get_regular_parts(self):
        regular_part_list = ( self.fully_connection, self.bert)
        regular_factor_list = (self.arg_dict['fully_regular'], self.arg_dict['bert_regular'])
        return regular_part_list, regular_factor_list

    def get_input_of_visualize_model(self, example_ids, example_dict):
        data_batch = self.deal_with_example_batch(example_ids[0:1], example_dict)

        input_ids_batch = data_batch['input_ids_batch']
        token_type_ids_batch = data_batch['token_type_ids_batch']
        attention_mask_batch = data_batch['attention_mask_batch']
        sep_index_batch = torch.tensor(data_batch['sep_index_batch'], device=self.device)
        sent1_len_batch = torch.tensor(data_batch['sent1_len_batch'], device=self.device)
        sent2_len_batch = torch.tensor(data_batch['sent2_len_batch'], device=self.device)
        labels = data_batch['labels']

        input_data = input_ids_batch, token_type_ids_batch, attention_mask_batch, sep_index_batch, sent1_len_batch, \
            sent2_len_batch, labels

        return input_data

    def count_of_parameter(self):
        with torch.no_grad():
            self.cpu()
            model_list = [self, self.bert, self.fully_connection]
            parameter_counts = []
            weight_counts = []
            bias_counts = []
            parameter_list = []
            weights_list = []
            bias_list = []
            for model_ in model_list:
                parameters_temp = model_.named_parameters()
                weights_list.clear()
                parameter_list.clear()
                bias_list.clear()
                for name, p in parameters_temp:
                    # print(name)
                    parameter_list.append(p.reshape(-1))
                    if name.find('weight') != -1:
                        weights_list.append(p.reshape(-1))
                    if name.find('bias') != -1:
                        bias_list.append(p.reshape(-1))
                parameters = torch.cat(parameter_list, dim=0)
                weights = torch.cat(weights_list, dim=0)
                biases = torch.cat(bias_list, dim=0)
                parameter_counts.append(len(parameters))
                weight_counts.append(len(weights))
                bias_counts.append(len(biases))
            for p_count, w_count, b_count in zip(parameter_counts, weight_counts, bias_counts):
                if p_count != w_count + b_count:
                    raise ValueError

            for kind in (parameter_counts, weight_counts, bias_counts):
                total = kind[0]
                others = kind[1:]
                count_temp = 0
                for other in others:
                    count_temp += other
                if total != count_temp:
                    raise ValueError
            self.to(self.device)

            result = [
                {'name': 'entire', 'total': parameter_counts[0], 'weight': weight_counts[0], 'bias': bias_counts[0]},
                {'name': 'bert', 'total': parameter_counts[1], 'weight': weight_counts[1], 'bias': bias_counts[1]},
                {'name': 'fully', 'total': parameter_counts[2], 'weight': weight_counts[2], 'bias': bias_counts[2]},
            ]

            return result


