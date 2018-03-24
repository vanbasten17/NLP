__author__ = "Ferran Cantarino 173705, Marc Rabat 172808"
'''
This file contains the necessary classes to deal with the purposed problem.
It contains two classes:
- Classifier: Abstract the operations for each file in the corpus
- FileInstance: Do the operations within each file
'''

import os
from collections import Counter
from collections import OrderedDict
import re


class Classifier:
    '''
    This class is initialized with the following values:
        dataset_dir: which is the name of the dataset folder
        N: the value of most frequent words to extract
        flag_stopwords: if True (removes stopwords), o.w. work with the normal corpus
    There are also declarations for:
        files: which will contain the FileInstances
        most_frequent: a list containg the most frequent words
    It calls on initialization the methods:
        initialize_files: fill the list of files with FileInstance
        parse_files: for each file get its text and parse it in order to deal propperly with it
    '''

    def __init__(self, dataset_dir, N, flag_stopwords):
        self.dataset_dir = dataset_dir
        self.files = []
        self.N = N
        self.most_frequent = []
        self.remove_stopwords = True
        if flag_stopwords is 'n':
            self.remove_stopwords = False
        self.initialize_files()
        self.parse_files()

    def initialize_files(self):
        """
        	This method initialize the list of FileInstance of the classifier.

            Args:
                self.

            Returns:
            	each file is appended to the files list
        """
        for file_name in os.listdir(self.dataset_dir):
            self.files.append(FileInstance(self.dataset_dir, file_name, self.N))

    def parse_files(self):
        """
            This method calls the propper methods in order to parse correctly the file.
            If the user input is according to remove the stopwords, the remove_stopwords method
            is called.
            Args:
                self.

            Returns:
                each file with its text parsed
        """
        for file in self.files:
            file.parse()
            if self.remove_stopwords:
                file.remove_stopwords()

    def most_frequent_words(self):
        """
        This method extract the words more repeated in the corpus.
            Args:
                self.
           Returns:
                fill the most_frequent list with the most frequent words
                in the corpus
        """
        for file in self.files:
            for word in file.parsed_vocabulary:
                self.most_frequent.append(word)
        # the class Counter will do the trick in order to extract most frequent_words
        self.most_frequent = Counter(self.most_frequent).most_common(self.N)
        aux = []
        for item in self.most_frequent:
            aux.append(item[0].lower())
        self.most_frequent = aux
        print(self.most_frequent)

    def compute_features(self):
        """
        	This methods call the method compute_vector for each file in the corpus

            Args:
                self

            Returns:
            	it modifies within each file its features vector
        """
        for file in self.files:
            file.compute_vector(self.most_frequent)

    def generate_arff(self):
        """
        	Generate the results file formatted with the data of the execution.

            Args:
                self.

            Returns:
            	generate the file with the results in the same directory
        """
        file_name = str(self.N) + "-results_StopwordsRemoved-" + str(self.remove_stopwords) + ".arff"
        with open(file_name, "w") as results:
            results.write("%1. Title: Results of Features")
            results.write("\n%2. Sources:")
            results.write("\n%\tAuthors: Ferran Cantarino i Marc Rabat")
            results.write("\n@RELATION " + str(self.N) + "_Features")
            for item in self.most_frequent:
                aux = item
                if "\'" in item:
                    aux = item.replace("\'", ".")
                results.write("\n@ATTRIBUTE " + str(aux) + " NUMERIC")
            results.write("\n@ATTRIBUTE class {male, female}")
            results.write("\n@DATA\n")
            for file in self.files:
                for k, v in file.features.items():
                    results.write(str(str(v) + ","))
                results.write(file.gender)
                results.write("\n")

        results.close()


class FileInstance:
    '''
      This class is initialized with the following values:
          dataset_dir: which is the name of the dataset path
          N: the value of most frequent words to extract
          file_name: the name of the file
          gender: the label corresponding with the gender of the author of the file
      There are also declarations for:
          shared variables among all the instances:
            punctuation: this are the punctuation symbols we want to extract from the word of the file
            stopwords: a list containing stopwords, them are extracted from the resulting list of the parsed words of the file
          instance variables (relevant info for the class):
            file_descriptor: the path to the file in order to read it from
            vocabulary: the words extracted in the first time the file is read
            parsed_vocabulary: the words parsed that we have considered to be 'legal'
            vocabulary_length: the length of the 'legal' vocabulary
            features: it will contain the features vector
      On initialization:
          the file is read line by line with the method read
      '''

    # shared variables among all the file instances
    punctuation = str("!#$%&()*+\"/:;<=>?[\].,^_—`{|}~")

    with open("stopwords.txt", "r") as sw:
        stopwords = sw.read().splitlines()
    sw.close()

    # instance variables
    def __init__(self, dataset_dir, file_name, N):
        # File Information
        self.file_name = file_name
        self.gender = re.sub('^[^A-Za-z]*', '', self.file_name)
        self.file_descriptor = dataset_dir + file_name
        # File data
        with open(self.file_descriptor) as fd:
            self.vocabulary = fd.read().lower().split()
        fd.close()

        self.N = N
        self.vocabulary_length = 0
        self.parsed_vocabulary = []
        self.features = OrderedDict()

    def parse(self):
        """
            Deal with the logic of parsing. First of all a first pass is done to erase the punctuation symbols.
            The second pass assures that the words are correctly separated to save them in a list.
            Finally, updates the count of legal words that the file have
            Args:
                self.

            Returns:
            	modify the vocabulary of a file
        """
        self.first_pass()
        self.second_pass()
        self.vocabulary_length = len(self.parsed_vocabulary)

    def first_pass(self):
        #remove the punctuation symbols that we have considered not useful for our model
        for word in self.vocabulary:
            if word is not '-':
                new_word = re.sub('[' + self.punctuation + ']', '\n', word)
                self.parsed_vocabulary.append(new_word)

    def second_pass(self):
        #prettify the list of words to save it to the vocabulary
        aux_parsed = []
        for word in self.parsed_vocabulary:
            aux = word.split("\n")
            for item in aux:
                if item is not "":
                    aux_parsed.append(item)
        self.parsed_vocabulary = aux_parsed

    def remove_stopwords(self):
        """
        	This method removes the stopwords from the vocabulary of each file.

            Args:
                self.

            Returns:
            	update the vocabulary without the stopwords
        """
        newlist = []
        for word in self.parsed_vocabulary:
            if word not in self.stopwords:
                newlist.append(word)
        self.parsed_vocabulary = newlist

    def compute_vector(self, most_frequent):
        """
        	Computes the vector in the following way:
        	    1.Initialize the vector of features to zero
        	    2.For each word in the vocabulary of the file look for match with the most_common words in the corpus
        	    3.Compute the results

            Args:
                self, most_frequent(list)

            Returns:
            	fill the vector of features with the propper data
        """
        for item in most_frequent:
            self.features[item] = 0

        for word in self.parsed_vocabulary:
            for item in most_frequent:
                count = 0
                if word == item:
                    count += 1
                    self.features[item] = count

        for k, v in self.features.items():
            self.features[k] = (v / self.vocabulary_length)

