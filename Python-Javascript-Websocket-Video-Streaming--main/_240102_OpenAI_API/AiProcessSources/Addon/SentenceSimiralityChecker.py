
from sentence_transformers import SentenceTransformer
from math import sqrt, pow

model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')

def CheckSimilarity(str1, str2) : 
    sentences = [str1, str2]

    embeddings = model.encode(sentences, convert_to_tensor=True)


    comparison_value = sqrt(sum(pow(a-b,2) for a, b in zip(embeddings[0], embeddings[1])))

    print(rf"similarity with '{str1}' and '{str2}' : {comparison_value} (low means similar)")    

    return comparison_value


