__author__ = "Ferran Cantarino 173705, Marc Rabat 172808"

from collections import OrderedDict
from itertools import groupby
import operator
import random

def generate_model_from_training_set(path_to_training_set, output_filename):
	"""
	This method takes a training set (or the corpus) file in order to generate
	a model file which will contain the format "Word GramaticalCategory Frequency".
    
    Args:
        path_to_training_set (str): Path to training set file.
        output_filename (str): Name of the output file.

    Returns:
    	if the computation proceeds, it will return the written file as specified.    
    """
	with open(path_to_training_set, 'r') as training_set:	
		ocurrencies_dict = count_ocurrencies(training_set)
		with open(output_filename, 'w') as model:
			for key,value in ocurrencies_dict.items():
				format_to_print = str(key + " " + str(value) + "\n") 
				format_to_print.decode("UTF-8").encode('latin-1')
				model.write(format_to_print) 
		model.close()
	training_set.close()


def count_ocurrencies(training_set):
	"""
	This method takes a training set (or the corpus) opened form a file in order to count
	how many times a word with its associated gramatical category appears in the file.
    
    Args:
        training_set (opened_file): File descriptor to training set.

    Returns:
    	dictionary: key(word, gramatical category), value(frequency)
    """
	words_and_tags_dict = {}
	for line in training_set:
		aux = line.decode("latin-1").encode("UTF-8").split()
		aux[0] = aux[0].lower()
		string = str(aux[0] + " " + aux[1])
		if string not in words_and_tags_dict:
			words_and_tags_dict[string] = 1
		else:
			words_and_tags_dict[string] += 1
	return words_and_tags_dict


def load_evaluation_format(path):
	"""
	This method takes the path to a file to be evaluated and load it into memory
	in order to be operated. (Gold_Standard and Results)
    
    Args:
        path (str): Path to evaluation file.

    Returns:
    	orderedDictionary: key(word), value(gramatical_category)
    """
	with open(path, 'r') as eval:
		values = OrderedDict()
		for line in eval:
			aux = line.decode("latin-1").encode("UTF-8").split()
			values[aux[0].lower()] = aux[1]
		print values
		return values

def compute_accuracy(path_to_results, path_to_gold_standard):
	"""
	This method takes the path of the files to compare in order to compute
	the accuracy, which in fact is the relation between the #of coincidences / total.
	It loads the files to orderedDict structures in order to compare line by line if equal.
	Finally, it print the results of the computation.
    
    Args:
        path_to_results (str): Path to results generated file.
        path_to_results (str): Path to gold_standard file.

    Print:
    	Result to the problem purposed.
    	
    """
	results = load_evaluation_format(path_to_results)
	gold_standard = load_evaluation_format(path_to_gold_standard)
	count = 0.0
	for i in xrange(len(results)):
		if results.items()[i] == gold_standard.items()[i]:
			count += 1
		if False:
			print results.items()[i], "doesn't match", gold_standard.items()[i] #debug
	
	precision = (count / len(results)) * 100
	print "\n\n"
	print "ACCURACY: ", precision, "%"


def load_model(path_to_model):
	"""
	This method takes the path to the model file and loads it into a dictionary
	in order to deal better with it.
    
    Keyfacts: 
    	What is done, is doing a pair-valued key in order to uniquely identify each word
    	with its gramatical category. If we don't do this, probably we will have duplicate
    	keys and we will not preserve the data integrity.
    
    Args:
        path_to_model (str): Path to model file.

    Returns:
    	dictionary: key(word, gramatical_category), value(frequency)
    """
	with open(path_to_model, 'r') as model:
		loaded_model = {}
		for line in model:
			aux = line.decode("latin-1").encode("UTF-8").split()
			word = aux[0].lower()
			gramatical_category = aux[1]
			frequency = aux[2]
			tup_key = (word, gramatical_category);
			loaded_model[tup_key] = frequency
	model.close()
	return loaded_model

def tag_with_model(path_to_test, model, output_filename):
	"""
	This method takes the path to the main files that interact in this method in order
	to tag the test file with some precision. Defines a default gramatical categories when
	a word has not been matched in order to deal with the problem.
	Takes the prediction computed from the method and prints it as "Word PredictedTag"
    
    Args:
        path_to_test (str): Path to test file.
        model (dictionary): Model with the lexic.
        output_filename (str): Path to output_filename.

    Returns:
    	on succeed, prints the words with its tag into the file with output_filename specified.

    """
	with open(path_to_test, 'r') as test:
		with open(output_filename, 'w') as results:
			default_gcs = compute_common_gcs(model)
			for line in test:
				word = line.decode("latin-1").encode("UTF-8").split()
				word = word[0].lower()
				prediction = compute_prediction(word, model, default_gcs)

				format_to_print = str(word) + " " + str(prediction) + "\n"
				results.write(format_to_print.decode("UTF-8").encode("latin-1"))
				
		results.close()
	
	test.close()

def compute_prediction(word, model, default_gcs):
	"""
	This method takes the current word to have its tag predicted, the model and the default_gc
	if the word is not found in the model dictionary.
	First we create a list of matches which will contain the matches for a word before computing
	what's its best score in compute_best_gc method. If the word is not found, we take randmoly
	a gramatical category to be assigned.
    
    Args:
        word (str): Current word to be tagged.
        model (dictionary): Model with the lexic.
        default_gcs (list): List with default_gcs.

    Returns:
    	best_gc(str): If word is matched, return the gc with more frequency in the model.
    				  Otherwise, a random value for the most common gc's is picked up and returned.
    	
    """
	matches = []
	word = word.decode("latin-1").encode("UTF-8") #needed to deal with accent problems
	for key, value in model.items():
		if key[0] == word: 
			matches.append((key, value))
	best_gc = compute_best_gc(matches)

	if best_gc == "NONE":
		return random.choice(default_gcs)
	else:
		return best_gc
	
def compute_common_gcs(model):
	"""
	This method counts the times a gc is repeated and returns a list with the 5 most_common
	gc's.
    
    Args:
        model (dictionary): Model with the lexic.

    Returns:
    	common_dict.keys()(list): Returns the list with more common gcs.
    	
    """
	common_dict = {}
	for k, v in model.items():
	
		if k[1] not in common_dict.keys():
			common_dict[k[1]] = int(v)
		else:
			common_dict[k[1]] += int(v)

	common_dict = dict(sorted(common_dict.iteritems(), key=operator.itemgetter(1), reverse=True)[:5])
	return common_dict.keys()

def compute_best_gc(words_matched):
	"""
	This method computes the max_score and its tag associated and returns it.
    
    Args:
        words_matched (list): List of matches for a word.
   
    Returns:
    	best_gc(str): Return the gc with max frequency for the matched words-gc tuples. If the list is empty
    				  returns the indicator "NONE" to deal after.
    """
	best_score = 0
	best_gc = "NONE"
	for item in words_matched:
		if int(item[1]) > best_score:
			best_score = int(item[1])
			best_gc = item[0][1]
	return best_gc