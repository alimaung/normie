import os
import re
from rapidfuzz import process, fuzz

def split_filename(filename):
    """
    Extract meaningful parts from the filename.
    Example: "039-2024_01043399_rejected.pdf" → ['039', '2024', '01043399', 'rejected']
    """
    filename = os.path.splitext(filename)[0]  # Remove extension
    parts = re.split(r'[-_.]', filename)  # Split by -, _, or .
    return parts

def weighted_similarity(target, candidate, weights):
    """
    Compute a weighted similarity score between two filenames.
    - `weights` is a list defining the importance of each part.
    """
    target_parts = split_filename(target)
    candidate_parts = split_filename(candidate)

    # Ensure both filenames have the same number of parts
    max_length = max(len(target_parts), len(candidate_parts))
    target_parts += [""] * (max_length - len(target_parts))
    candidate_parts += [""] * (max_length - len(candidate_parts))

    # Apply fuzzy matching to each part and weight them
    total_score = 0
    for i in range(max_length):
        part_score = fuzz.ratio(target_parts[i], candidate_parts[i])  # Fuzzy match
        weight = weights[i] if i < len(weights) else 1  # Use weight if available, otherwise 1
        total_score += part_score * weight

    return total_score / sum(weights[:max_length])  # Normalize by total weight

def fuzzy_search_file(filename, folder_path, weights, threshold=70, recursive=True):
    """
    Searches for filenames similar to `filename` in the given folder, applying custom weights.

    :param filename: The target filename.
    :param folder_path: The directory to search in.
    :param weights: A list of weights for different filename parts.
    :param threshold: Minimum similarity score to consider a match.
    :param recursive: Whether to search in subdirectories.
    :return: List of matching file paths with weighted similarity scores.
    """

    # Get all files in the directory
    file_list = []
    for root, _, files in os.walk(folder_path) if recursive else [(folder_path, [], os.listdir(folder_path))]:
        for file in files:
            file_list.append(os.path.join(root, file))

    # Extract just the filenames
    filenames_only = [os.path.basename(file) for file in file_list]

    # Compute similarity scores
    matches = [
        (file_list[i], weighted_similarity(filename, filenames_only[i], weights))
        for i in range(len(filenames_only))
    ]

    # Filter and sort matches
    matches = [(path, score) for path, score in matches if score >= threshold]
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches


# Example usage
folder = r"\\Dehesdna-a009a\projekte\k-z\ofs\Dokumentenservice\TeileundStoffe\Antrag"  # Change this to your directory
search_filename = "039-2004_10003399_Freigabe_zurückgezogen.PDF"

# Define importance (weights) for filename parts: [ID, Year, Unique Number, Status]
weights = [2, 3, 4, 1]  # Higher weight means more importance

matches = fuzzy_search_file(search_filename, folder, weights)

if matches:
    print("\nBest Matches:")
    for path, score in matches:
        print(f"{path} (Score: {score:.2f})")
else:
    print("No matching files found.")