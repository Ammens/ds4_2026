""""Indexing module for the Book_indexing package."""
import argparse
import os
import math 
import itertools
from auxiliary_functions import load_book, clean_list_of_words, reduce_list_of_words, count_words, list_files_in_directory

def compute_tf(word_count, total_words):
    if total_words == 0:
        return {}
    dict_tf = {}
    for word, count in word_count.items():
        dict_tf[word] = count / total_words
    return dict_tf    

def main(args):
    book_path = args.book_path
    book_dictionary = {}
    if not os.path.isfile(book_path):
        print(f"Error: The file '{book_path}' does not exist.")
        return
    if os.path.isfile(book_path):
        book_dictionary[book_path] = load_book(book_path)
    elif os.path.isdir(book_path):
        files = list_files_in_directory(book_path)
        for file in files:
           if file.endswith('.txt'):
               book_dictionary[file] = load_book(os.path.join(book_path, file))
    else:
        print(f"Error: The path '{book_path}' is neither a file nor a directory.")
    print(book_dictionary.keys())
    for book_name, words in book_dictionary.items():
        cleaned_words = clean_list_of_words(words)
        word_count = count_words(cleaned_words)
        total_words = len(cleaned_words)
        tf_dict = compute_tf(word_count, total_words)
        print(f"Book: {book_name}")
        print(f"Total words: {total_words}")
        print(f"Unique words: {len(word_count)}")
        print(f"Term Frequencies:")
        for word, tf in tf_dict.items():
            if tf >= 0.0001:    
                print(f" {word}: {tf: .4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Index books")
    parser.add_argument("book_path", type=str, help="Path to the books text files.")
    args = parser.parse_args()
    main(args)
