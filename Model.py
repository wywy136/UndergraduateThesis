# coding: UTF-8
from transformers import BertTokenizer, BertModel, BertConfig
import torch.nn as nn
import torch


class BERTModel(nn.Module):
    def __init__(self, args):
        hidden_size = args.hidden_size

        super(BERTModel, self).__init__()

        # BERT模型
        if args.bert_model_type == 'bert-base-uncased' or args.bert_model_type == 'bert-large-uncased':
            self._bert = BertModel.from_pretrained(args.bert_model_type)
            self._tokenizer = BertTokenizer.from_pretrained(args.bert_model_type)
            print(f'{args.bert_model_type} model loaded')

        else:
            raise KeyError('Config.args.bert_model_type should be bert-base/large-uncased. ')

        self.classifier_start = nn.Linear(hidden_size, 2)

        self.classifier_end = nn.Linear(hidden_size, 2)

        self._classifier_sentiment = nn.Linear(hidden_size, 3)

        self.AA = nn.Linear(hidden_size, hidden_size)
        self.AO = nn.Linear(hidden_size, hidden_size)
        self.OO = nn.Linear(hidden_size, hidden_size)
        self.OA = nn.Linear(hidden_size, hidden_size)

    def forward(self, query_tensor, query_mask, query_seg, step, stage):

        hidden_states = self._bert(
            input_ids=query_tensor.to(torch.int64),
            attention_mask=query_mask,
            token_type_ids=query_seg.to(torch.int64))[0]
        if step == 0:  # predict entity
            if stage == 'AA':
                hidden_states = self.AA(hidden_states)
            elif stage == 'AO':
                hidden_states = hidden_states + self.OO(hidden_states)
            elif stage == 'OO':
                hidden_states = self.OO(hidden_states)
            else:
                hidden_states = hidden_states + self.AA(hidden_states)
            out_scores_start = self.classifier_start(hidden_states)
            out_scores_end = self.classifier_end(hidden_states)
            return out_scores_start, out_scores_end
        else:  # predict sentiment
            cls_hidden_states = hidden_states[:, 0, :]
            cls_hidden_scores = self._classifier_sentiment(cls_hidden_states)
            return cls_hidden_scores
