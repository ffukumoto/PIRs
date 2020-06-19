import torch


class FullyConnection(torch.nn.Module):
    def __init__(self, arg_dict):
        super().__init__()
        layer_list = []
        active_list = []
        scales = arg_dict['fully_scales']
        for i in range(1, len(scales)):
            layer_list.append(torch.nn.Linear(scales[i - 1], scales[i], bias=True))
            active_list.append(torch.nn.Tanh())
        del active_list[-1]
        self.layer_list = torch.nn.ModuleList(layer_list)
        self.active_list = torch.nn.ModuleList(active_list)
        gpu_id = arg_dict['ues_gpu']
        if gpu_id == -1:
            self.device = torch.device('cpu')
        else:
            self.device = torch.device('cuda', gpu_id)

    def forward(self, input_data):
        # input_data = input_data.permute(1, 0, 2)
        result = input_data
        if torch.isnan(result).sum() > 0:
            print(torch.isnan(result))
            raise ValueError
        layer_num = len(self.layer_list)
        for i, linear, in enumerate(self.layer_list):
            result = linear(result)
            if i < layer_num - 1:
                result = self.active_list[i](result)

        return result


class BertFineTuneConnection(torch.nn.Module):
    def __init__(self, arg_dict):
        super().__init__()
        bert_hidden_dim = arg_dict['bert_hidden_dim']
        self.linear = torch.nn.Linear(bert_hidden_dim, 2, bias=True)

    def forward(self, input_data):
        # input_data = input_data.permute(1, 0, 2)
        result = input_data
        if torch.isnan(result).sum() > 0:
            print(torch.isnan(result))
            raise ValueError
        result = self.linear(result)
        result = self.activity(result)
        result = result[:, 0]
        result = result.reshape(-1)
        return result