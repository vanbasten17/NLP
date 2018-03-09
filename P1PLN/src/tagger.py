__author__ = "Ferran Cantarino 173705, Marc Rabat 172808"

import time
from nlp_methods import *
'''
Summary of the file tagger.py:
	Here we call the main functions imported from nlp_methods.py
	in order to reflect the tagging process in three encapsulated parts,
	which are mentioned in the below code.
	After entering the number of the tests, test_1 or test_2, the project
	is setted up make the propper calls.
'''
def main():
	#Program flow time and input 
	start_time = time.time()
	print "Enter the # of test you want to prove:"
	num = raw_input()
	test = "test_" + str(num) + ".txt"
	gold_standard = "gold_standard_" + str(num) + ".txt"
	results = "results_" + str(num) + ".txt"

	#PART 1: Generation of the model
	print "\nGenerating model from training_set..."
	generate_model_from_training_set('corpus.txt', 'lexic.txt')
	
	#PART 2: Tag using the model
	print "\nLoading model from training_set..."
	model = load_model('lexic.txt')
	print "\nTagging", test ,"..."
	tag_with_model(test, model, results)
	
	#PART 3: Evaluation of the results
	print "\nComputing results of ", results , " vs. ", gold_standard, "..."
	compute_accuracy(results, gold_standard)
	
	print "--- %s seconds ---" % (time.time() - start_time)

##############################END##############################

main()
