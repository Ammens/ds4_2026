""" Indexing functions for the book database. """
import argparse
import os
import math
import itertools

from auxiliary_functions import list_directory_files, load_book, clean_list_of_words, reduce_list_of_words, count_words   

def compute_tf(word_count, total_words):
    """ Compute the term frequency (TF) for a word in a document. """
    if total_words == 0:
        return {}
    dict_tf = {}
    for word, count in word_count.items():
        dict_tf[word] = count / total_words
    return dict_tf

def compute_idf(documents):
    '''
        Compute the Inverse Document Frequency (IDF) for each word in the documents.
        usage: idf = compute_idf(list_of_dictionaries)
    '''
    N = len(documents)
    dictionary_list = [list(dictionary.keys()) for dictionary in documents]
    key_list = list(itertools.chain(*dictionary_list))
    idf_dictionary = dict.fromkeys(key_list, 0)
    
    for dictionary in documents:
        for word, valor in dictionary.items():
            if valor > 0:
                if word in idf_dictionary:
                    idf_dictionary[word] += 1
                else:
                    idf_dictionary[word] = 1
    for word, valor in idf_dictionary.items():
        idf_dictionary[word] = math.log(N / float(valor))
    return idf_dictionary

def compute_tf_idf(tf: dict, idfs: dict) -> dict:
    '''
        Computes Term-Frequency-Inverse Document Frequency (TF-IDF) for all documents.
        usage: tfidf_book = compute_tf_idf(book_tf, idfs)
    '''
    tfidf = dict()
    for word, value in tf.items():
        tfidf[word] = value * idfs[word]
    return tfidf

def book_indexing(dictionary_of_books: dict) -> dict:
    """ Indexes the books and computes TF, IDF, and TF-IDF. """
    tf_dict = {}
    for book_name, words in dictionary_of_books.items():
        cleaned_words = clean_list_of_words(words)
        word_count = count_words(cleaned_words)
        total_words = len(cleaned_words)
        tf_dict[book_name] = compute_tf(word_count, total_words)

    idf_dict = compute_idf(list(tf_dict.values()))

    tfidf_dict = {}
    for book_name, tf in tf_dict.items():
        tfidf_dict[book_name] = compute_tf_idf(tf, idf_dict)

    return tfidf_dict

def top_tf_per_book(book_dictionary: dict, top_n: int = 10) -> dict:
    """ 
    Retorna el top N de palabras con mayor Term Frequency (TF) 
    para cada libro individualmente. 
    """
    book_top_tf = {}
    for book_name, words in book_dictionary.items():
        cleaned_words = clean_list_of_words(words)
        word_count = count_words(cleaned_words)
        total_words = len(cleaned_words)
        
        tf_dict = compute_tf(word_count, total_words)
        sorted_tf = sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)
        book_top_tf[book_name] = dict(sorted_tf[:top_n])
        
    return book_top_tf

def search_word(book_dictionary: dict, word: str) -> list:
    """ Search for a word in the book dictionary and return a list of books containing the word """
    tfidf_dict = book_indexing(book_dictionary)
    result_dict = {}
    for book_name, tfidf in tfidf_dict.items():
        if word in tfidf:
            result_dict[book_name] = tfidf[word]
    sorted_results = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_results

def main(args):
    """ Main function to index books. """
    book_path = args.book_path
    book_dictionary = {}
    
    if not os.path.exists(book_path):
        print(f"Error: The path '{book_path}' does not exist.")
        return
        
    if os.path.isfile(book_path):
        book_dictionary[book_path] = load_book(book_path)
    elif os.path.isdir(book_path):
        files = list_directory_files(book_path)
        for file in files:
            if file.endswith('.txt'):
                book_dictionary[file] = load_book(os.path.join(book_path, file))
    else:
        print(f"Error: The path '{book_path}' is neither a file nor a directory.")
        return

    print(f"\n=== Top {args.top_n} Term Frequency (TF) por Libro ===")
    top_tf_results = top_tf_per_book(book_dictionary, top_n=args.top_n)
    for book, tf_dict in top_tf_results.items():
        print(f"\nLibro: {book}")
        for word, tf_val in tf_dict.items():
            print(f"   - {word}: {tf_val:.6f}")

    print(f"\n=== Búsqueda de la palabra '{args.word_to_check}' (TF-IDF) ===")
    word_to_check = args.word_to_check
    result_list = search_word(book_dictionary, word_to_check)
    if result_list:
        for book, tfidf in result_list:
            print(f"   - Libro: {book}, TF-IDF: {tfidf:.6f}")
    else:
        print(f"   - La palabra '{word_to_check}' no se encontró en ningún libro.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index books.")
    parser.add_argument("book_path", type=str, help="Path to the books text files.")
    parser.add_argument("word_to_check", type=str, help="Word to check TF-IDF for.")
    parser.add_argument("--top_n", type=int, help="Number of top term frequencies to display per book.", default=10)
    args = parser.parse_args()
    main(args)