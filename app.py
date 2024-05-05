
import streamlit as st
import boto3
import io
from PIL import Image
import docx
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read AWS credentials from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

title = '<p style="font-size: 40px;font-weight: 550;"> Textract - Extract Text via Images & PDFs </p>'
st.markdown(title, unsafe_allow_html=True)

st.image("./assets/example.jpeg")

# Provide AWS credentials directly
aws_management_console = boto3.session.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name  # Replace with your desired region
)

client = aws_management_console.client(service_name='textract', region_name='ap-south-1')

# Create S3 client
s3_client = aws_management_console.client('s3')


# Define a function to extract text from an image
def extract_text_from_image(image):
    response = client.detect_document_text(Document={"Bytes": image})

    # Extract the text from the response
    text = ""

    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text += item["Text"] + "\n"

    # Display the extracted text
    st.subheader("Extracted Text")
    st.write(text)
    download_text(text)


def download_text(text):
    doc = docx.Document()
    doc.add_paragraph(text)

    output_file = io.BytesIO()
    doc.save(output_file)
    output_file.seek(0)
    st.download_button(
        label="Download Doc File",
        data=output_file,
        file_name="extracted_text.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def extract_text_from_pdf(pdf_bytes, pdf_filename):
    
    # Create a file-like object from the bytes
    pdf_fileobj = io.BytesIO(pdf_bytes)

    # Upload PDF file to S3 bucket
    bucket_name = 'pdf-stuff'  # Replace with your S3 bucket name
    s3_key = 'uploads/' + pdf_filename
    s3_client.upload_fileobj(pdf_fileobj, bucket_name, s3_key)

    # Start text detection job with S3 object
    response = client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': s3_key
            }
        }
    )

    # Wait for the job to complete
    job_id = response['JobId']
    st.write("Text extraction job started. Job ID:", job_id)
    st.write("Waiting for the job to complete... (This might take a while)")

    # Poll until the job is complete
    while True:
        job_status = client.get_document_text_detection(JobId=job_id)
        if job_status['JobStatus'] in ['SUCCEEDED', 'FAILED']:
            break
        time.sleep(5)  # Wait for 5 seconds before checking again

    if job_status['JobStatus'] == 'SUCCEEDED':
        text_blocks = [item['Text'] for item in job_status['Blocks'] if item['BlockType'] == "LINE"]
        if len(text_blocks) > 0:
            text = "\n".join(text_blocks)
            st.success("Text extracted from PDF:")
            st.write(text)
            download_text(text)
        else:
            st.warning("No text found in the PDF.")
    else:
        st.error("Text extraction failed. Please try again later.")


# Define the main function that will be called when the "Extract Text" button is clicked
def extract_text(file, file_type):
    if file_type == "Image":
        extracted_text = extract_text_from_image(file.read())
        img = Image.open(file)
        st.image(img, caption="Uploaded Image")
    elif file_type == "PDF":
        extracted_text = extract_text_from_pdf(file.read(), file.name)
        st.write(extracted_text)


# Create an option menu for selecting the file type
file_type = st.selectbox("Select file type", options=["Image", "PDF"])

# Create a file uploader
file = st.file_uploader("Upload file", type=["jpg", "jpeg", "png", "pdf"])

# Create a button to extract text from the uploaded file
if st.button("Extract Text"):
    if file is not None:
        extract_text(file, file_type)
    else:
        st.write("Please upload a file.")
