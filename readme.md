It is a male fashion suggesting model that will
First ask the user questions. The results from the questionnaire are stored for each user as preferences.
Questions like color, fabric, fit & style, personality, accessory, occasions, practicality and comfort

Once the data is stored, it will be normalized into tags, and stored in the database as clean concise data.
The normalized data of a user will be passed on to gemini flash 2.0 model. The model will use its capabilities to think of 2 best possible outfits for the user, and add another column data to the uses database which has the users final preference.
The final preference will then be passed on as a prompt to gemini 2.0 flash, which will generate 2 images based on the 2 best outfits it thought of, and give that as an output, which the user can like, or dislike
If liked, it will be added back to the database

pip install -r requirements.txt
