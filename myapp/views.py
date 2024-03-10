# impoting the required libraries

from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
import json
from joblib import load
from transformers import pipeline
from summarizer import Summarizer
import spacy
import cv2
import numpy as np
import pytesseract
from transformers import pipeline, BertTokenizerFast

 
spcnlp = spacy.load("en_core_web_sm")
model =load('./savedModels/model.joblib')

candidate_labels = ['business', 'tech', 'politics', 'sport', 'entertainment']

tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased", max_length=512)
nlp= pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

classifier = pipeline("zero-shot-classification", device="cpu")
sentiment_labels = ['positive','negative','neutral']



def print_high_score_labels(data):

    labels = data['labels']
    scores = data['scores']
    
    # Find the index of the highest score
    max_score_index = scores.index(max(scores))
    half_highest_score = scores[max_score_index] / 2
    
    # Filter labels based on the score threshold
    high_score_labels = [label for label, score in zip(labels, scores) if score >= half_highest_score]
    
    return high_score_labels




@csrf_exempt
def input_output(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('input', '')

            sent = classifier(user_input, sentiment_labels)
            # Find the index of the maximum score
            max_score_index = sent['scores'].index(max(sent['scores']))

            # Get the label with the highest score
            highest_score_label = sent['labels'][max_score_index]
            
            doc = spcnlp(user_input)
            entity_set = set()

            for ent in doc.ents:
                if ent.label_ in ['GPE', 'ORG', 'WORK_OF_ART', 'EVENT', 'LOC', 'NORP']:
                    entity_set.add(ent.text)



            multitag = classifier(user_input, candidate_labels,multi_label = True)
            final_tags = print_high_score_labels(multitag)

            react_dict={
                "main_tags":final_tags,
                "extra_tags":list(entity_set),
                "sentiment":highest_score_label
            }

            output = json.dumps(react_dict)           
            response_data = {"output": output}
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def summarizer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('input', '')
            
            bert_model = Summarizer()
            bert_summary = ''.join(bert_model(user_input, min_length=60))
            

            summary = f'{bert_summary}'
            response_data = {'summary': summary}
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def URL_summarizer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input_url = data.get('input', '')

            # Rename to user_input_url to avoid overwriting
            extracted_content = extract_and_print_paragraphs(user_input_url)
            
            bert_model = Summarizer()
            bert_summary = ''.join(bert_model(extracted_content, min_length=60))
            

            summary = f'{bert_summary}'
            response_data = {'summary': summary}
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def Image_summarizer(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['image']
            custom_config = r"--oem 3 --psm 11 -c tessedit_char_whitelist='1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz., ' -c preserve_interword_spaces=1"

            # Read the uploaded image data directly from the InMemoryUploadedFile
            image_data = uploaded_file.read()

            # Preprocess the image data
            preprocessed_image = preprocess_image(image_data)

            # Perform OCR on the preprocessed image
            extracted_text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

            
            bert_model = Summarizer()
            bert_summary = ''.join(bert_model(extracted_text, min_length=60))
            

            summary = f'{bert_summary}'
            response_data = {'summary': summary}
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def extract_and_print_paragraphs(url):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')

    result_string = ""
    for paragraph in paragraphs:
        result_string += paragraph.get_text() + "\n"

    return result_string

@csrf_exempt
def url_tagging(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input_url = data.get('input', '')  
            
            # Rename to user_input_url to avoid overwriting
            extracted_content = extract_and_print_paragraphs(user_input_url)

            # Process the extracted content as needed

            sent = classifier(extracted_content, sentiment_labels)
            max_score_index = sent['scores'].index(max(sent['scores']))
            highest_score_label = sent['labels'][max_score_index]

            doc = spcnlp(extracted_content)
            entity_set = set()

            for ent in doc.ents:
                if ent.label_ in ['GPE', 'ORG', 'WORK_OF_ART', 'EVENT', 'LOC', 'NORP']:
                    entity_set.add(ent.text)

            multitag = classifier(extracted_content, candidate_labels, multi_label=True)
            final_tags = print_high_score_labels(multitag)

            react_dict = {
                "main_tags": final_tags,
                "extra_tags": list(entity_set),
                "sentiment": highest_score_label,
                "text": extracted_content
            }
            output = json.dumps(react_dict) 
            response_data = {"output": output}
            # Return the JSON-formatted response
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image_data):
    # Decode the image data using OpenCV
    image_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Resize the image (optional, but can improve accuracy)
    image = cv2.resize(image, (800, 600))
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply binary thresholding
    _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Apply noise reduction using Gaussian blur
    blurred_image = cv2.GaussianBlur(binary_image, (3, 3), 0)
    
    # Enhance contrast using histogram equalization
    equalized_image = cv2.equalizeHist(blurred_image)
    return equalized_image

    
def extract_text(image_path, custom_config):
    preprocessed_image = preprocess_image(image_path)
    extracted_text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
    return extracted_text

@csrf_exempt
def extract_text_view(request):
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES['image']
            custom_config = r"--oem 3 --psm 11 -c tessedit_char_whitelist='1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz., ' -c preserve_interword_spaces=1"

            # Read the uploaded image data directly from the InMemoryUploadedFile
            image_data = uploaded_file.read()

            # Preprocess the image data
            preprocessed_image = preprocess_image(image_data)

            # Perform OCR on the preprocessed image
            extracted_text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

            sent = classifier(extracted_text, sentiment_labels)
            max_score_index = sent['scores'].index(max(sent['scores']))
            highest_score_label = sent['labels'][max_score_index]
            doc = spcnlp(extracted_text)
            entity_set = set()

            for ent in doc.ents:
                if ent.label_ in ['GPE', 'ORG', 'WORK_OF_ART', 'EVENT', 'LOC', 'NORP']:
                    entity_set.add(ent.text)

            multitag = classifier(extracted_text, candidate_labels, multi_label=True)
            final_tags = print_high_score_labels(multitag)
            react_dict = {
                "main_tags": final_tags,
                "extra_tags": list(entity_set),
                "sentiment": highest_score_label,
                "text": extracted_text
            }
            output = json.dumps(react_dict) 
            response_data = {"output": output}
            # Return the JSON-formatted response
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



        


        
        