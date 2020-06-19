import corpus
import framework as fr
import argparse
import utils.general_tool as general_tool


#initial global argument
def create_arg_dict():
    arg_dict = {
        'batch_size': 8,
        'learn_rate': 2e-5,
        'optimizer': 'adam',
        'k_fold': 10,
        'epoch': 3,
        'warmup_steps': 0,
        'max_steps': -1,
        'gcn_layer': 2,
        'position_encoding': False,
        'dropout': 1,
        'regular_flag': False,
        'ues_gpu': -1,
        'repeat_train': True,
        'corpus': corpus.mrpc.get_mrpc_obj,
        'framework_name': "LSSE",
        'task_type': 'classification',
        'seed': 1234
    }
    general_tool.setup_seed(arg_dict['seed'])

    parser = argparse.ArgumentParser(description='PIRs')

    parser.add_argument('-gpu', dest="ues_gpu", default='0', type=int,
                        help='GPU order, if value is -1, it use cpu. default 0')

    parser.add_argument('--framework', '-f', dest="framework_name", default='LSSE', type=str,
                        choices=['LSSE', 'LSyE', 'LSeE', 'LE', 'SeE'],
                        help='Choose the framework, default "LSSE"')

    parser.add_argument('-wope', dest="position_encoding", action='store_false',
                        help='whether without position encoding, default false')

    parser.add_argument('--corpus', '-c', dest="corpus_name", default='mrpc', type=str, choices=['mrpc', 'qqp'],
                        help='Choose the corpus, default "mrpc"')

    parser.add_argument('--batch_size', '-bz', dest="batch_size", default=8, type=int,
                        help='The batch size of training and testing')

    parser.add_argument('--learn_rate', '-lr', dest="learn_rate", default=2e-5, type=float,
                        help='The learn rate of training, default 2e-5 ')

    parser.add_argument('--epoch', '-e', dest='epoch', default=3, type=int,
                        help='The epoch of training, default 3')

    parser.add_argument('--gcn_layer', '-gl', dest='gcn_layer', default=2, type=int,
                        help='The hidden layer of GCN, default 2')

    args = parser.parse_args()
    args = vars(args)
    if 'corpus_name' in args:
        if args['corpus_name'] == 'mrpc':
            args['corpus'] = corpus.mrpc.get_mrpc_obj
        elif args['corpus_name'] == 'qqp':
            print("Haven't submit the qqp data, now use mrpc")
            args['corpus'] = corpus.mrpc.get_mrpc_obj
            args['corpus_name'] = 'mrpc'
        else:
            raise ValueError

    arg_dict.update(args)

    return arg_dict

# train and test our method
def run_framework():
    arg_dict = create_arg_dict()
    framework_manager = fr.FrameworkManager(arg_dict)
    # train model use training date
    framework_manager.train_final_model()
    # evaluate model use test date
    framework_manager.test_model()


def main():
    run_framework()

if __name__ == '__main__':
    main()
    pass
