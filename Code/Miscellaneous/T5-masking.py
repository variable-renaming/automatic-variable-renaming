import re
import numpy as np
import codecs
import random
import glob
import os
import argparse
import torch

from transformers import T5Tokenizer
from typing import Dict, List, Tuple
from random import sample
from tqdm import tqdm


def writeTxt(filename, list_item):  # write txt file in Dataset folder
    file = codecs.open(filename, "w", "utf-8")

    for line in list_item:
        file.write(line + "\n")

    file.close()


def readTxt(filepath):  # read generic file

    try:
        f = open(filepath, 'r')
        content = f.readlines()
        c_ = list()

        for c in content:
            r = c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        settings.logger.error("Error ReadFile: " + str(e))
        c_ = []
    return c_


def saveFiles(file_path, save_folder, tokenizer):

    inputs_all = list()
    labels_all = list()

    with open(file_path, encoding="utf-8") as f:

        lines = [line.rstrip() for line in f if (
            len(line) > 0 and not line.isspace())]

        for l in tqdm(lines):
            inputs, labels = createIndexesLabels(l, tokenizer)
            # inputs, labels=createIndexesLabels(l)
            inputs_all.append(inputs)
            labels_all.append(labels)

    writeTxt("{}/{}_inputs.txt".format(save_folder, 'train'), inputs_all)
    writeTxt("{}/{}_labels.txt".format(save_folder, 'train'), labels_all)


def createIndexesLabels(line, tokenizer):

    input_text, label_text = add_noise(line, tokenizer)
    return tokenizer.decode(input_text, clean_up_tokenization_spaces=False), tokenizer.decode(
        label_text, clean_up_tokenization_spaces=False)


def set_seed(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)


def load_and_cache_examples(args, evaluate=False):
    prefix = "eval" if evaluate else "train"
    return LineByLineDatasetWithBPETokenizer(
        args.save_folder, args.tokenizer_name, prefix)


def read_dataset(tokenizer: T5Tokenizer, batch,
                 labels_to_process) -> Tuple[torch.Tensor, torch.Tensor]:
    # The inputs are already masked in the training file

    tmp_inputs = batch.clone()

    tmp_inputs_list = []
    for input in tmp_inputs:
        tmp_inputs_list.append(input)

    # Gets the maximum length of inputs and labels_lines (they may not be the same)
    # We then need to adapt one or the other to have the same length through
    # padding
    max_length_inputs = max([len(input) for input in tmp_inputs_list])
    max_length_labels_lines = max([len(label) for label in labels_to_process])

    # Create the labels tensor
    labels_to_convert_in_tensor = []

    i = 0
    while i < len(batch):
        l1_tmp = tokenizer.encode(labels_to_process[i])
        label_to_add = []
        for token in l1_tmp:
            if token != tokenizer.bos_token_id and token != tokenizer.eos_token_id:  # Remove special tokens
                label_to_add.append(token)

        j = len(label_to_add)
        while j < max_length_labels_lines:
            # we add -100 to preserve the same length
            label_to_add.append(-100)
            j += 1

        labels_to_convert_in_tensor.append(label_to_add)
        i += 1

    labels = torch.as_tensor(labels_to_convert_in_tensor)

    inputs_to_convert = []
    for input in tmp_inputs_list:
        tmp_input = []
        for token in input:
            tmp_input.append(token)

        i = len(tmp_input)
        while i < max_length_inputs:
            tmp_input.append(tokenizer.pad_token_id)
            i += 1
        inputs_to_convert.append(tmp_input)

    inputs = torch.as_tensor(inputs_to_convert)

    return inputs, labels


def racha_detection(lista):
    # It returns a list of lists where each sub-list contains the consecutive
    # tokens in the list
    rachas = []
    racha = []
    for i, element in enumerate(lista):
        if (i < len(lista) - 1) and (lista[i + 1] == element + 1):
            racha.append(element)
        else:
            if len(racha) > 0:
                rachas.append(racha + [element])
            else:  # (i!=len(lista)-1):
                rachas.append([element])
            racha = []
    return rachas


def masking(tokenized_sentence, rachas, tokenizer):
    # Function to mask a tokenized_sentence (token ids) following the rachas described in rachas
    # Only one sentinel_token per racha
    sent_token_id = 0
    enmascared = tokenized_sentence.copy()
    for racha in rachas:
        sent_token = f'<extra_id_{sent_token_id}>'
        sent_id = tokenizer.encode(sent_token)[0]
        for i, idx in enumerate(racha):
            if i == 0:
                enmascared[idx] = sent_id
            else:
                enmascared[idx] = -100
        sent_token_id += 1

    enmascared = [t for t in enmascared if t != -100]

    return enmascared


def add_noise(sentence, tokenizer, percent=0.15):
    # Function that takes a sentence, tokenizer and a noise percentage and returns
    # the masked input_ids and masked target_ids accordling with the T5 paper and HuggingFace docs
    # To see the process working uncomment all the prints ;)
    tokenized_sentence = tokenizer.encode(sentence)
    # print('PRE-MASKED:')
    # print('INPUT: {}'.format(tokenizer.convert_ids_to_tokens(tokenized_sentence)))
    # print('INPUT: {}'.format(tokenizer.convert_ids_to_tokens(tokenized_sentence)))

    idxs_2_mask = sorted(random.sample(range(1, len(tokenized_sentence) - 1),
                                       int(len(tokenized_sentence) * percent)))

    rachas = racha_detection(idxs_2_mask)
    enmascared_input = masking(tokenized_sentence, rachas, tokenizer)

    # print('RACHAS INPUT: {}'.format(rachas))
    idxs_2_mask = [idx for idx in range(len(tokenized_sentence)) if idx not in idxs_2_mask]
    rachas = racha_detection(idxs_2_mask)
    enmascared_target = masking(tokenized_sentence, rachas, tokenizer)
    # print('RACHAS TARGET: {}'.format(rachas))

    # print('POST-MASKED:')
    # print('INPUT: {}'.format(tokenizer.convert_ids_to_tokens(enmascared_input)))
    # print('TARGET: {} \n\n'.format(tokenizer.convert_ids_to_tokens(enmascared_target)))

    return enmascared_input[:-1], enmascared_target


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--train_data_file",
        required=True,
        type=str,
        help="Pre-training dataset in txt format where each sample must be on a single row"
        )
    
    parser.add_argument(
        "--tokenizer_name",
        required=True,
        type=str,
        help='.model file'
        )

    parser.add_argument(
        '--save_folder',
        required=True,
        type=str,
        help="Destination folder"
        )

    args = parser.parse_args()

    tokenizer = T5Tokenizer.from_pretrained(args.tokenizer_name)
    saveFiles(args.train_data_file, args.save_folder, tokenizer)


if __name__ == "__main__":
    main()

