import torch
import numpy as np
import framework as fr
import time
import utils.file_tool as file_tool
import utils.parser_tool as parser_tool
import utils.general_tool as general_tool

import utils.data_tool as data_tool
from model import *


class LSyE(fr.LSSE):
    name = "LSyE"
    result_path = file_tool.connect_path('result', name)

    def __init__(self, arg_dict):
        super().__init__(arg_dict)
        self.name = LSyE.name
        self.result_path = LSyE.result_path

    @classmethod
    def framework_name(cls):
        return cls.name

    def create_arg_dict(self):
        arg_dict = {
            # 'sgd_momentum': 0.4,
            'semantic_compare_func': 'l2',
            'concatenate_input_for_gcn_hidden': True,
            'fully_scales': [768, 2],
            'position_encoding': True,
            # 'fully_regular': 1e-4,
            # 'gcn_regular': 1e-4,
            # 'bert_regular': 1e-4,
            'gcn_layer': 2,
            'group_layer_limit_flag': False,
            # 'group_layer_limit_list': [2, 3, 4, 5, 6],
            'gcn_gate_flag': True,
            'gcn_norm_item': 0.5,
            'gcn_self_loop_flag': True,
            'gcn_hidden_dim': 768,
            'bert_hidden_dim': 768,
            'pad_on_right': True,
            'sentence_max_len_for_bert': 128,
            'dtype': torch.float32,
        }
        return arg_dict

    def create_models(self):
        self.bert = BertBase()
        self.gcn = GCN(self.arg_dict)
        self.semantic_layer = SemanticLayer(self.arg_dict)
        self.fully_connection = FullyConnection(self.arg_dict)
        self.gcn.apply(self.init_weights)
        self.fully_connection.apply(self.init_weights)

    def forward(self, *input_data, **kwargs):
        if len(kwargs) > 0:  # common run or visualization
            data_batch = kwargs
            input_ids_batch = data_batch['input_ids_batch']
            token_type_ids_batch = data_batch['token_type_ids_batch']
            attention_mask_batch = data_batch['attention_mask_batch']
            sep_index_batch = data_batch['sep_index_batch']
            word_piece_flags_batch = data_batch['word_piece_flags_batch']
            sent1_len_batch = data_batch['sent1_len_batch']
            adj_matrix1_batch = data_batch['adj_matrix1_batch']

            sent2_len_batch = data_batch['sent2_len_batch']
            adj_matrix2_batch = data_batch['adj_matrix2_batch']
            labels = data_batch['labels']

            sent1_org_len_batch = data_batch['sent1_org_len_batch']
            sent2_org_len_batch = data_batch['sent2_org_len_batch']

        else:
            input_ids_batch, token_type_ids_batch, attention_mask_batch, sep_index_batch, sent1_len_batch, \
            adj_matrix1_batch, sent2_len_batch, adj_matrix2_batch, labels = input_data

        last_hidden_states_batch, pooled_output = self.bert(input_ids_batch, token_type_ids_batch, attention_mask_batch)

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

            if len(sent1_states) != sent1_org_len_batch[i]:
                raise ValueError

            sent1_states = data_tool.padding_tensor(sent1_states, self.arg_dict['max_sentence_length'],
                                                    align_dir='left', dim=0)

            sent2_states = self.merge_reps_of_word_pieces(sent2_word_piece_flags, sent2_states)

            if len(sent2_states) != sent2_org_len_batch[i]:
                raise ValueError

            sent2_states = data_tool.padding_tensor(sent2_states, self.arg_dict['max_sentence_length'],
                                                    align_dir='left', dim=0)
            sent1_states_batch.append(sent1_states)
            sent2_states_batch.append(sent2_states)

        sent1_states_batch = torch.stack(sent1_states_batch, dim=0)
        sent2_states_batch = torch.stack(sent2_states_batch, dim=0)

        def get_position_es(shape):
            position_encodings = general_tool.get_global_position_encodings(length=self.arg_dict['max_sentence_length'],
                                                                            dimension=self.arg_dict['bert_hidden_dim'])
            position_encodings = position_encodings[:shape[1]]
            position_encodings = torch.tensor(position_encodings, dtype=self.data_type,
                                              device=self.device).expand([shape[0], -1, -1])
            return position_encodings

        if self.arg_dict['position_encoding']:
            shape1 = sent1_states_batch.size()
            position_es1 = get_position_es(shape1)
            shape2 = sent2_states_batch.size()
            position_es2 = get_position_es(shape2)
            sent1_states_batch += position_es1
            sent2_states_batch += position_es2

        # star_time = time.time()
        gcn_out1 = self.gcn(sent1_states_batch, adj_matrix1_batch)
        gcn_out2 = self.gcn(sent2_states_batch, adj_matrix2_batch)
        if self.arg_dict['concatenate_input_for_gcn_hidden']:
            gcn_out1 = torch.cat([gcn_out1, sent1_states_batch], dim=2)
            gcn_out2 = torch.cat([gcn_out2, sent2_states_batch], dim=2)
        result = self.semantic_layer(gcn_out1, gcn_out2)

        result = self.fully_connection(result)

        loss = torch.nn.CrossEntropyLoss()(result.view(-1, 2), labels.view(-1))
        predicts = np.array(result.detach().cpu().numpy()).argmax(axis=1)

        return loss, predicts



