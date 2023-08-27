import boto3
from flask import Flask, request

app = Flask(__name__)

# Konfigurujte Boto3 na použitie svojich prístupových údajov S3
s3 = boto3.client('s3',
                  aws_access_key_id='AKIA2E7FAZMVEOBLDJVG',
                  aws_secret_access_key='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')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Získať obrázok z POST požiadavky
    uploaded_file = request.files['file']

    if uploaded_file:
        # Nahrať obrázok do S3
        s3.upload_fileobj(uploaded_file, 'your-s3-bucket-name', uploaded_file.filename)
        return 'Obrázok bol úspešne nahraný do S3'

    return 'Obrázok sa nepodarilo nahrať'

if __name__ == '__main__':
    app.run()