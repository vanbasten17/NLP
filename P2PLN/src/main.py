__author__ = "Ferran Cantarino 173705, Marc Rabat 172808"

'''
This file contains the main for executing the program.
After the input of the desired parameters of execution is done,
it instantiates the classifier which do the following parts:
1. Extract the N most frequent words from the corpus
2. Computer the feature vector for each file
3. Generate the results in order to be evaluated with Weka
'''

from utils import Classifier


class Main:
    dataset_dir = "dataset/"  # path to corpus

    print("Enter the number of frequent words to use:")
    N = int(input())

    print("Remove stopwords? [y/n]")
    flag_stopwords = str(input())

    classifier = Classifier(dataset_dir, int(N), flag_stopwords)
    classifier.most_frequent_words()
    classifier.compute_features()
    classifier.generate_arff()