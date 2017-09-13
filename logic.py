import nltk
import random
import pickle
from nltk.stem.snowball import RussianStemmer
from nltk.tokenize.toktok import ToktokTokenizer

stemmer = RussianStemmer()
toktok = ToktokTokenizer()

DUMP_FILE_NAME = "./dump/dump.bin"
SENTENCES_CHUNK_SIZE = 1
sentences = {}
amount_of_sentences_in_dump = 0

def dump_sentences():
	with open(DUMP_FILE_NAME, 'wb') as dump_file:
	    pickle.dump(sentences, dump_file)

def dump_chunked_sentences():
	if len(sentences) > amount_of_sentences_in_dump + SENTENCES_CHUNK_SIZE:
		dump_sentences()

def load_sentences():
	global sentences
	with open(DUMP_FILE_NAME, 'rb') as dump_file:
		try:
			sentences = pickle.load(dump_file)
		except Exception as e:
			print("Failed to load sentences: {0}".format(e))

def normalize_sentence(sentence_text):
	words = toktok.tokenize(sentence_text.lower())
	stems = []
	for word in words:
		stems.append(stemmer.stem(word.lower()))
	return frozenset(stems)

def calculate_set_similarity(set1, set2):
	intersection = set1.intersection(set2)
	mean_length = (len(set1) + len(set2)) // 2
	if mean_length == 0:
		return 1
	return len(intersection) / mean_length

def calculate_sentence_similarity(sentence1_text, sentence2_text):
	n_sentence1 = normalize_sentence(sentence1_text)
	n_sentence2 = normalize_sentence(sentence2_text)
	return calculate_set_similarity(n_sentence1, n_sentence2)

def add_sentence(sentence_text):
	n_sentence = normalize_sentence(sentence_text)
	if n_sentence not in sentences:
		sentences[n_sentence] = {}
		sentences[n_sentence]["full_text"] = sentence_text
		sentences[n_sentence]["normalized_answers"] = set()
		dump_chunked_sentences()

def add_answer(sentence_text, answer_text):
	n_sentence = normalize_sentence(sentence_text)
	n_answer = normalize_sentence(answer_text)
	add_sentence(sentence_text)
	add_sentence(answer_text)
	sentences[n_sentence]["full_text"] = sentence_text
	sentences[n_sentence]["normalized_answers"].add(n_answer)

def get_most_similar_normalized_sentence(sentence_text):
	n_sentence = normalize_sentence(sentence_text)

	if n_sentence in sentences and len(sentences[n_sentence]["normalized_answers"]) > 0:
		# print("Sentence found: {0}".format(sentence_text))
		return n_sentence

	max_similarity = 0.5
	similar_normalized_sentence = n_sentence
	for n_sentence_item in sentences:
		if len(sentences[n_sentence_item]["normalized_answers"]) == 0:
			continue
		similarity = calculate_set_similarity(n_sentence_item, n_sentence)
		if similarity >= max_similarity:
			max_similarity = similarity
			similar_normalized_sentence = n_sentence_item
			# print("For {0} -> similar is {1} -> similarity: {2}".format(sentence_text, similar_normalized_sentence, similarity))
	return similar_normalized_sentence

def get_most_similar_normalized_answers(sentence_text):
	n_similar_sentence = get_most_similar_normalized_sentence(sentence_text)
	return sentences[n_similar_sentence]["normalized_answers"]

def get_random_normalized_answer(sentence_text):
	n_answers = get_most_similar_normalized_answers(sentence_text)
	# print("Answers for {0} -----> {1}".format(sentence_text, n_answers))
	if len(n_answers) == 0:
		return False
	return random.sample(n_answers, 1)[0]

def get_random_answer(sentence_text):
	n_answer = get_random_normalized_answer(sentence_text)
	if not n_answer:
		# n_random_sentence = random.sample(list(sentences), 1)[0]
		# return sentences[n_random_sentence]["full_text"]
		return False
	return sentences[n_answer]["full_text"]