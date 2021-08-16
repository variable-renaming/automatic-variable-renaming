"""
This script provides a full support for creating the "semi-final" dataset for the CugLM Model.
For further info, take a look at the original repo: https://github.com/LiuFang816/CugLM
"""

import json
import glob
import javalang
import os
import sys
import pandas as pd
import string, random
from tqdm import tqdm


def tokenize_java_line(code):
    token_gen = javalang.tokenizer.tokenize(code)
    tokens = []
    while (True):
        try:
            token = next(token_gen)
        except:
            break
        tokens.append(token)

    pure_tokens = [token.value for token in tokens]
    return pure_tokens


def tokenize_java(code, code_lines=None, need_index=False):
    token_gen = javalang.tokenizer.tokenize(code)
    tokens = []
    while (True):
        try:
            token = next(token_gen)
        except:
            break
        tokens.append(token)

    pure_tokens = [token.value for token in tokens]

    pos = [[token.position[0], token.position[1]] for token in tokens]
    lineno = [token.position[0] for token in tokens]

    indexes = []
    if need_index:
        for i in range(len(pure_tokens)):
            start_index = ''.join(code_lines[:(pos[i][0] - 1)])
            start_index = len(start_index) + pos[i][1] - 1
            end_index = start_index + len(pure_tokens[i])
            indexes.append([start_index, end_index])

    token_types = [str(type(token))[:-2].split(".")[-1] for token in tokens]
    return pure_tokens, token_types, pos, lineno, indexes


def sanityCheck(path_to_token, path_to_type, separator):
    with open(path_to_token, encoding="utf-8") as f:
        token_lines = f.readlines()

    with open(path_to_type, encoding="utf-8") as f:
        type_lines = f.readlines()
    

    for (token,type) in zip(token_lines, type_lines):
        per_line_tokens = token.split(separator)
        per_line_types = type.split(separator)
        if len(per_line_tokens) != len(per_line_types):
            return False

    return True

def main():

    separator = '\x1f'

    # target path should contain all the json files extracted with the resolver for that specific set (e.g, test, pre-training, fine-tuning)
    target_path = "All-Training-JSON"
    files = glob.glob(target_path + '/*.json', recursive=False)

    for file in tqdm(files):

        f = open(file, )

        data = json.load(f)

        token_final_list_refined = []
        sublist_types_list_refined = []
        if os.stat(file).st_size > 2:

            for item in data:

                class_item = item["classBody"]
                idLines = item["idLines"]
                resolved_ids = item["resolvedIdentifiers"]
                ids = item["identifiers"]
                from_where = item['extracted_from']

                pure_tokens, token_types, _, lineno, _ = tokenize_java(
                    class_item, code_lines=class_item.splitlines())

                index_pos_dict = dict()

                idSetList = [int(item) for item in list(set(idLines))]
                idSetList.sort()
                try:
                    starting_line = idSetList[0] - 1
                except IndexError:
                    continue

                for idx in idSetList:
                    index_pos_dict[int(idx)] = [i for i in range(len(idLines)) if int(idLines[i]) == idx]

                counter = 0
                token_final_list = []
                class_lines = class_item.splitlines()

                for line in class_lines:
                    item = (tokenize_java_line(line))
                    token_final_list.append(item)

                oldLNumber = starting_line
                type_token_string = ""
                final_type_token = []
                type_token_list = []

                for lnumber, token, ttoken in zip(lineno, pure_tokens, token_types):

                    if lineno >= lowerBoud and lineno <=upperBoud:

                        key_line = lnumber + starting_line

                        if key_line != oldLNumber:
                            type_token_string += "\n"
                            type_token_list.append("\n")

                        if ttoken == "Identifier" or (ttoken == "Keyword" and token=='this'):

                            solved = False
                            if key_line not in index_pos_dict.keys():
                                pass  # not resolved type

                            else:
                                for pos in index_pos_dict[key_line]:
                                    if ids[pos] == token:
                                        resolved_target = resolved_ids[pos]
                                        counter += 1
                                        solved = True
                                        break

                            if solved:
                                type_token_list.append(resolved_target)
                                type_token_string += '{}{}{}'.format(separator, resolved_target, separator)
                            else:
                                type_token_list.append("_")
                                type_token_string += '{}_{}'.format(separator, separator)

                        else:
                            type_token_list.append('_')
                            type_token_string += '{}_{}'.format(separator, separator)

                        oldLNumber = key_line

                    type_token_string += "\n"
                    type_token_list.append("\n")
                    type_token_list = type_token_list[1:]
                    final_type_token.append(type_token_list)

                    token_final_list_refined.extend(sublist for sublist in token_final_list if len(sublist) > 0)

                    sublist_types = []
                    old_idx = 0
                    for (idx, item) in enumerate(type_token_list):
                        if item == "\n":
                            sublist_types.append(type_token_list[old_idx:idx])
                            old_idx = idx + 1

                    sublist_types_list_refined.extend(sublist_types)

                    try:

                        for (idx, _) in enumerate(sublist_types_list_refined):

                            with open('token_java_tmp.txt', 'a+', encoding="utf-8") as f:
                                f.write('\x1f'.join(token_final_list_refined[idx]) + "\n")

                            with open('type_java_tmp.txt', 'a+', encoding="utf-8") as f:
                                f.write('\x1f'.join(sublist_types_list_refined[idx]) + "\n")


                        # Put line separator according to the author's suggestion
                        with open('token_java_tmp.txt', 'a+') as f:
                            f.write("\n")

                        with open('type_java_tmp.txt', 'a+') as f:
                            f.write("\n")


                        if not sanityCheck('token_java_tmp.txt', 'type_java_tmp.txt', separator):

                            with open('sanity.txt', 'a+') as fwrite:
                                fwrite.write('{}\n'.format(from_where))

                        else:

                            with open('token_java_tmp.txt') as f:
                                tokens_data = f.read()

                            with open('type_java_tmp.txt') as f:
                                types_data = f.read()

                            with open('token_java_pt.txt', 'a+') as fwrite:
                                fwrite.write(tokens_data)

                            with open('type_java_pt.txt', 'a+') as fwrite:
                                fwrite.write(types_data)

                        os.remove('token_java_tmp.txt')
                        os.remove('type_java_tmp.txt')

                    except Exception:
                       with open('to-discard.txt', 'a+') as fwrite:
                           fwrite.write('{}\n'.format(file))


            f.close()

if __name__ == "__main__":
    main()
