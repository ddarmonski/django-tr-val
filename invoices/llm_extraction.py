#Backend definition of the LLM functions to extract invoice content:
import openai
import base64
import pandas as pd
from pdf2image import convert_from_path
import re
import json
import fitz  # PyMuPDF
import io
from PIL import Image
import os

AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')


dict_cols = {
    "tour_id": {
      "description": "Round or tour (tournée in French) performed. IMPORTANT: it is a 4-digit code or an alphanumeric short key of more than 3 characters.",
      "french": "'Tournée'",
      "type": "string"
    },
    "Description": {
      "description": "Description of the service provided, usually a delivery round or tour (tournée in French).",
      "french": "'Description'",
      "type": "string"
    },
    "tour_qty": {
      "description": "Number of days or times the round or tour was performed.",
      "french": "Quantité, Nombre Jours, nb or similar",
      "columns": ["jours", "nb", "nombre", "nombre total de jours", "qte", "qte :", "204 qte", "nb jour", "nb jours", "quantite", "quantite"],
      "type": "integer"
    },
    "unit_type": {
      "description": "Quantity to which the column 'tour_qty' refers, sometimes referred as tariff type. It can be number of days (or times) the round or tour was performed, number of hours or number of kms, and the corresponding admissible values are 'day', 'hour' or 'km'.",
      "french": "'Type d'unité' or 'Tarif type'",
      "type": "string",
      "enum": ["day", "hour", "km"]
    },
    "number_kms": {
      "description": "Length of the round. IMPORTANT: Do not consider this field unless kms are explicitly mentioned on the column name or on the entries.",
      "french": "'Nombre Kms'",
      "type": "integer"
    },
    "number_hours": {
      "description": "Duration of the round. IMPORTANT: Do not consider this field unless hours or minutes are explicitly mentioned on the column name or on the entries.",
      "french": "'Nombre Heures'",
      "columns": ["nb heures", "heure", "nbre d'heures"],
      "type": "integer"
    },
    "price_per_unit": {
      "description": "Price excluding VAT per round performed.",
      "french": "'Prix unitaire' or 'p.u.'",
      "columns": ["unite", "prix unitaire", ".p.u. ht", "p.u", "forfait unite", "prix", "p.u.h.t", "p.u.h.t / kms", "prix unit. ht", "p.u. ht", "pu ht", "pu ht €", "prix u", "tarif journalier ht", "pu vente", "p.u. h.t.", "p.u. ht net", "prix unitaire ht", "prix unite", "p.u.h.t / jour"],
      "type": "number"
    },
    "total_cost_tour": {
      "description": "Total price excluding VAT for this row.",
      "french": "'Prix total' or 'montant total'",
      "columns": ["total", "montant", "€ ht", "total ht net", "sous total ht", "total ht €", "total prix ht", "total h.t.", "montant ht", "total ht", "transport ht", "total ht tva ( 20 % )", "prix total"],
      "type": "number"
    },
    "toll_total": {
      "description": "Total toll paid during the total amount of rounds performed.",
      "french": "'Péage total'",
      "columns": ["montant peage"],
      "type": "number"
    },
    "toll_unit_qty": {
      "description": "Number of rounds performed for which a toll needed to be paid.",
      "french": "'Quantité de péage'",
      "columns": [],
      "type": "integer"
    },
    "toll_price_per_unit": {
      "description": "Amount paid for tolls during one occurrence of the round performed.",
      "french": "'Prix unitaire péage'",
      "columns": ["prix unit. peage"],
      "type": "number"
    },
    "required": ["tour_id", "Description", "tour_qty", "unit_type", "price_per_unit", "total_cost_tour"]
  }




def pdf_to_base64_images(pdf_bytes):
    # Open the PDF file from bytes
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Initialize a list to hold base64 encoded images
    base64_images = []
    
    # Iterate through each page in the PDF
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_num)
        
        # Convert the page to a pixmap (image)
        pix = page.get_pixmap()
        
        # Convert the pixmap to a PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save the PIL Image to a bytes buffer
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        
        # Encode the image to base64
        img_str = base64.b64encode(buffered.getvalue())
        base64_images.append(img_str.decode('utf-8'))
    
    return base64_images

def call_openai_api(base64_image):
    client = openai.AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        azure_deployment="gpt4o",
        api_version="2024-02-15-preview",
        azure_endpoint=f"https://aaaigpt4o.openai.azure.com/"
    )

    response = client.chat.completions.create(
        model="gpt4o",
       
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "You are AI assistant that have excellent undrestanding on invoices. Your task is to extract table from an image of invoice and match it with a schema. You should return JSON only"}, 
                    #{"type": "text", "text": "You are AI assistant that helps people find answers."}, 

                ]
            },
            {
                "role": "user",
                "content": [
                   {"type": "text", "text": f"Extract the table from this invoice and match it with the following schema: {dict_cols}." },
                    #{"type": "text", "text": f"tell me what is on the image." },

                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    }
                ],
            }
        ],
        max_tokens=2500,
        temperature = 0.1 #Very important to avoid hallucinations!!!
    )

    responce_str = response.choices[0].message.content
    print(responce_str)
    # Extract JSON response containing the table data
    json_output = extract_json_from_string(responce_str)

    # Convert the JSON to a dataframe
    df = pd.DataFrame(json_output)

    return df


def extract_json_from_string(input_string):
    # Use regex to find the JSON object in the string
    # The improved regex pattern ensures matching of nested objects inside the array
        json_string_match = re.search(r'\[\s*{.*?}\s*](?![^\[]*\])', input_string, re.DOTALL)
    
        if json_string_match:
            json_string = json_string_match.group(0)
            #print(json_string)
            try:
                # Parse the JSON string
                json_object = json.loads(json_string)
                return json_object
            except json.JSONDecodeError as e:
                print("Error decoding JSON: ", e.msg)
                return None
        else:
            print("No JSON found")
            return None