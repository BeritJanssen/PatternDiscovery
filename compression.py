import csv
import numpy as np

def dict_to_tuple(dict_list):
    """ Take a list of {'onset', 'pitch'} dictionaries,
    return a list of tuples
    """
    tuple_list = [(note['onset'], note['pitch']) for note in dict_list]
    return tuple_list


def get_all_notes_in_patterns(pattern_list):
    """
    From a list of pattern dictionaries as parsed from a file of pattern discovery results,
    return all notes which are part of patterns and their occurrences.
    """
    list_of_notes = []
    for p in pattern_list:
        for oc in p:
            list_of_notes.extend(dict_to_tuple(oc))
    return list_of_notes


def parse_musical_pieces(file_path) :
    """
    Take a csv file and return a list with
    [onset, pitch] lists, rounded to the third decimal
    """
    piece_list = []
    with open(file_path) as f:
        doc = csv.reader(f, delimiter=",")
        for row in doc :
            piece_list.append({
                'onset':round(float(row[0]), 3),
                'pitch': int(float(row[1]))
            })
    return piece_list


def parse_pattern_output(file_path):
    """ given a file path with pattern discovery results,
    return a list of dictionaries pattern_list,
    which is a json-compatible hierarchical format:
    [ # pattern 1
        [ # occurrence 1
            {'onset': 0.0, 'pitch': 62},
            {'onset': 1.0, 'pitch': 64},
            {'onset': 1.5, 'pitch': 63},
            ....
        ], 
        [ # occurrence 2
            {'onset': 20.0, 'pitch': 62},
            {'onset': 21.0, 'pitch': 64},
            {'onset': 21.5, 'pitch': 63},
            ...
        ],
        ...
    , # pattern 2
        [ # occurrence 1
            {}, {}, {}, ..
        ],
        [ # occurrence 2
            {}, {}, {}, ...
        ],
        ...
    ]
    the index of each pattern / occurrence in the list is its id
    """
    pattern_list = []
    occurrence_list = []
    note_list = []
    with open(file_path) as f:
        for line in f:
            if line.startswith('pattern'):
                if note_list:
                    occurrence_list.append(note_list)
                    pattern_list.append(occurrence_list)
                occurrence_list = []
                note_list = []                
            elif line.startswith('occurrence'):
                if note_list:
                    occurrence_list.append(note_list)
                note_list = []
            else:
                onset, pitch = line.split(", ")
                note_list.append({
                    'onset': round(float(onset), 3), 
                    'pitch': int(float(pitch[:-1]))
                })
    occurrence_list.append(note_list)
    pattern_list.append(occurrence_list)
    return pattern_list


def coverage(pattern_list, piece):
    """ given a pattern_list as parsed with parse_pattern_output,
    compare to notes of the piece,
    and return the intersection of the set of notes defined by pattern,
    divided by the length of piece
    """
    notes_in_patterns = get_all_notes_in_patterns(pattern_list)
    notes_in_piece = dict_to_tuple(piece)
    covered_notes = set.intersection(set(notes_in_patterns), set(notes_in_piece))
    coverage = len(list(covered_notes)) / len(piece)
    return coverage


def count_uncovered_notes(pattern_list, piece):
    """ given a pattern_list as parsed with parse_pattern_output,
    compare to notes of the piece,
    return the number of notes not covered by patterns
    """
    notes_in_patterns = get_all_notes_in_patterns(pattern_list)
    notes_in_piece = dict_to_tuple(piece)
    uncovered_notes = set(notes_in_piece).difference(set(notes_in_patterns))
    return len(list(uncovered_notes))


def lossless_compression(pattern_list, piece):
    """ given a pattern_list and piece (see coverage),
    return the length of the lists within pattern_dict,
    divided by the length of the piece
    """
    space_required = 0
    for pat in pattern_list:
        begin_notes = dict_to_tuple([oc[0] for oc in pat])
        tecs = np.subtract(begin_notes[1:], begin_notes[0])
        first_oc = dict_to_tuple(pat[0])
        space_required += len(first_oc) + len(tecs)
    uncovered_notes = count_uncovered_notes(pattern_list, piece)
    space_required += uncovered_notes
    lossless_compression = len(piece) / space_required
    return lossless_compression

