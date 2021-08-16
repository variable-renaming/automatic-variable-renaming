{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Lade nötiges Paket: exactci\n",
      "Lade nötiges Paket: ssanv\n",
      "  Dataset McNemar.p McNemar.OR\n",
      "1 javadoc         0  17.564404\n",
      "2  inside         0   8.039298\n",
      "3 overall         0  16.791317\n"
     ]
    }
   ],
   "source": [
    "!/Library/Frameworks/R.framework/Versions/4.0/Resources/bin/Rscript /Users/antonio/Desktop/statistical_test.r"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "import pickle\n",
    "\n",
    "# javadoc_train = '/Users/antonio/Desktop/ICPC_PROJECT/Replication/Data/datasets/NGrams/javadoc_train_4_Ngram.pickle'\n",
    "# inside_train = '/Users/antonio/Desktop/ICPC_PROJECT/Replication/Data/datasets/NGrams/inside_train_4_Ngram.pickle'\n",
    "\n",
    "inside_train = '/Users/antonio/Desktop/auto_cm_completion/preprocessing/code/core/single_comment_train_instances.pickle'\n",
    "javadoc_train = '/Users/antonio/Desktop/auto_cm_completion/preprocessing/code/core/javadoc_train_instances.pickle'\n",
    "\n",
    "with open(javadoc_train, 'rb') as newObj:\n",
    "    items = pickle.load(newObj)\n",
    "    javadoc_list = [item.strip() for item in items]\n",
    "\n",
    "with open(inside_train, 'rb') as newObj:\n",
    "    items = pickle.load(newObj)\n",
    "    inside_list = [item.strip() for item in items]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [],
   "source": [
    "stop_word_java_tag = [#'@author',\n",
    "                      '@param',\n",
    "                      '@deprecated',\n",
    "                      '@return',\n",
    "                      #'@see',\n",
    "                      '{@link}',\n",
    "                      #'@since',\n",
    "                      '@throws',\n",
    "                      '@Override',\n",
    "                      '{@docRoot}',\n",
    "                      '@exception',\n",
    "                      '{@inheritDoc}',\n",
    "                      '{@linkplain}',\n",
    "                      '{@literal}',\n",
    "                      '@serial',\n",
    "                      '@serialData',\n",
    "                      #'@version',\n",
    "                      '@{value}',\n",
    "                      '@argfiles'\n",
    "                ]\n",
    "\n",
    "def flatten(string):\n",
    "    string = string.strip()\n",
    "    string = string.replace('\\n',' ')\n",
    "    string = re.sub('\\s+',' ',string)\n",
    "    return string"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "59950"
      ]
     },
     "execution_count": 23,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "len(inside_list)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [],
   "source": [
    "import re\n",
    "\n",
    "inside_final_list = []\n",
    "javadoc_final_list = []\n",
    "\n",
    "flag = True\n",
    "\n",
    "for item in inside_list:\n",
    "    \n",
    "    flattened = flatten(item)\n",
    "    comments = re.findall(\"<sep>([\\s\\S]*?)<sep>\", flattened)\n",
    "    \n",
    "    for comment in comments:\n",
    "        \n",
    "        for stop in stop_word_java_tag:\n",
    "            \n",
    "            flag = True\n",
    "            if stop in comment:\n",
    "#                 print('Discarded: ',comment)\n",
    "                flag=False\n",
    "                break\n",
    "                \n",
    "        if flag:\n",
    "            inside_final_list.append(comment.strip())\n",
    "        \n",
    "       \n",
    "        \n",
    "for item in javadoc_list:\n",
    "    \n",
    "    flattened = flatten(item)\n",
    "    comments = re.findall(\"<sep>([\\s\\S]*?)<sep>\", flattened)\n",
    "    comment = comments[-1]\n",
    "    \n",
    "    javadoc_final_list.append(comment.strip())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(59941, 105749)"
      ]
     },
     "execution_count": 34,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "len(inside_final_list), len(javadoc_final_list)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'Return true if the given service is ready to be used, means initialized and running. @param serviceClass @return isReady'"
      ]
     },
     "execution_count": 35,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "javadoc_final_list[4]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "\"public java.util.List<? extends com.google.cloud.talent.v4beta1.SkillOrBuilder>\\n      getSkillsOrBuilderList() {\\n    return skills_;\\n  }\\n\\n<sep> Optional. The skill set of the candidate. It's highly recommended to provide as much information as possible to help improve the search quality. repeated .google.cloud.talent.v4beta1.Skill skills = 19; <sep>\""
      ]
     },
     "execution_count": 27,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "javadoc_list[0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [],
   "source": [
    "with open('javadoc_train_4_Ngram.txt','a+') as fwrite:\n",
    "    for line in javadoc_final_list:\n",
    "        fwrite.write(line+'\\n')\n",
    "        \n",
    "with open('inside_train_4_Ngram.txt','a+') as fwrite:\n",
    "    for line in inside_final_list:\n",
    "        fwrite.write(line+'\\n')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
