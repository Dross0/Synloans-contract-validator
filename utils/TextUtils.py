def find_distance(nlp, sentence, anchor_word, token):
    token_start_index = sentence.text.lower().find(token.lower())
    token_end_index = token_start_index + len(token)
    return find_distance_index(nlp, sentence, anchor_word, token_start_index, token_end_index)


def find_distance_index(nlp, sentence, anchor_word, token_start, token_end):
    anchor_lemma = nlp(anchor_word)[0].lemma_

    anchor_indexes = []

    for word in sentence:
        if word.lemma_ == anchor_lemma:
            word_start_index = word.idx
            word_end_index = word_start_index + len(word.text)
            anchor_indexes.append((word_start_index, word_end_index))

    if not anchor_indexes:
        return -1

    min_distance = len(sentence.text)
    for (start, end) in anchor_indexes:
        if end <= token_start:
            min_distance = min(min_distance, token_start - end)
        else:
            min_distance = min(min_distance, start - token_end)

    return min_distance
